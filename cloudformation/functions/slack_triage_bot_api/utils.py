import logging
import json
from typing import Optional
import boto3
import requests

from .config import CONFIG

logger = logging.getLogger(__name__)
logger.setLevel(CONFIG.log_level)


class SlackException(Exception):
    pass


def store_oauth_token(client_id: str, access_token: str) -> dict:
    """Store an OAuth 2 access token in SSM parameter store

    :param client_id: OAuth 2 client_id issued by Slack
    :param access_token: OAuth 2 access token
    :return: dictionary containing the "Version" and "Tier" of the stored
             parameter
    """
    client = boto3.client('ssm')
    return client.put_parameter(
        Name='{}-{}'.format(
            CONFIG.slack_token_parameter_store_name, client_id),
        Description='The Slack OAuth access token for the MozDef Slack Triage '
                    'Bot API',
        Value=access_token,
        Type='SecureString',
        Overwrite=True,
        Tags=[
            {
                'Key': 'Application',
                'Value': 'MozDef Slack Triage Bot API'
            },
        ]
    )


def get_access_token(client_id: str) -> dict:
    """Fetch the OAuth 2 access token for a given client_id from cache or SSM
    parameter store

    :param client_id: The OAuth 2 client_id to fetch the associated access
                      token from
    :return: string of the access token
    """
    global access_token
    if 'access_token' not in globals():
        access_token = {}
    if client_id not in access_token:
        client = boto3.client('ssm')
        response = client.get_parameter(
            Name='{}-{}'.format(
                CONFIG.slack_token_parameter_store_name, client_id),
            WithDecryption=True
        )
        access_token[client_id] = response['Parameter']['Value']
    return access_token


def emit_to_mozdef(
        identifier: str,
        email: str,
        slack_user_id: str,
        identity_confidence: str,
        response: str) -> str:
    """Send a message with the user's response to SQS for pickup by MozDef

    :param identifier: The unique identifier sent by MozDef originally
    :param email: The user's email address
    :param slack_user_id: The user's slack ID
    :param identity_confidence: The identityConfidence sent by MozDef
                                originally
    :param response: The user's response
    :return: The message ID returned from SQS after sending the message
    """
    data = {
        "identifier": identifier,
        "user": {
            "email": email,
            "slack": slack_user_id
        },
        "identityConfidence": identity_confidence,
        "response": response
    }
    client = boto3.client('sqs')
    response = client.send_message(
        QueueUrl=CONFIG.queue_url,
        MessageBody=json.dumps(data)
    )
    return response['MessageId']


def call_slack(
        url: str,
        data: dict,
        key_to_return: str,
        post_as_json: Optional[bool] = False) -> dict:
    """POST to a slack URL and return the result

    :param url: The Slack URL to POST to
    :param data: The payload to pass in the POST body
    :param key_to_return: The key in the dictionary that is returned by Slack
                          to return to the caller of the call_slack method
    :param post_as_json: A boolean of whether or not to POST a JSON payload
                         or a URL encoded payload
    :return: The response from Slack based on the key_to_return
    """
    access_token = get_access_token(CONFIG.slack_client_id)
    headers = {
        'Authorization': 'Bearer {}'.format(
            access_token[CONFIG.slack_client_id])}
    try:
        if post_as_json:
            response = requests.post(url, json=data, headers=headers)
        else:
            response = requests.post(url, data=data, headers=headers)
        response.raise_for_status()
        if not response.json().get('ok'):
            raise SlackException(response.json().get('error'))
    except requests.exceptions.RequestException as e:
        logger.error(
            'POST of response to {} failed {} : {} : {} : {}'.format(
                url,
                data,
                e,
                getattr(e.response, 'status_code', None),
                getattr(e.response, 'text', None)
            ))
        raise
    logger.debug('Called slack with {} and received response of {}'.format(
        data,
        response.json()
    ))
    return response.json().get(key_to_return)


def provision_token(query_string_parameters: dict) -> dict:
    """Given an OAuth 2 code, obtain a Slack access token and store it

    :param query_string_parameters: A dictionary of the URL query parameters
    :return: A dictionary of an API Gateway HTTP response
    """
    if query_string_parameters.get('error'):
        logger.error('redirect_uri error : {}'.format(
            query_string_parameters.get('error')
        ))
        return {
            'headers': {'Content-Type': 'text/html'},
            'statusCode': 400,
            'body': "Unable to provision and store an OAuth access token"}
    data = {
        'code': query_string_parameters.get('code'),
        'client_id': CONFIG.slack_client_id,
        'client_secret': CONFIG.slack_client_secret
    }
    url = 'https://slack.com/api/oauth.v2.access'
    try:
        response = requests.post(
            url=url,
            data=data
        )
        response.raise_for_status()
        if not response.json().get('ok'):
            raise SlackException(response.json().get('error'))
    except (requests.exceptions.RequestException, SlackException) as e:
        logger.error(
            'Failed to provision and store OAuth access token with url {} '
            'and data {} : {} : {} : {}'.format(
                url,
                data,
                e,
                getattr(e.response, 'status_code', None),
                getattr(e.response, 'text', None)
            ))
        return {
            'headers': {'Content-Type': 'text/html'},
            'statusCode': 400,
            'body': "Unable to provision and store an OAuth access token"}

    access_token = response.json().get('access_token')
    if access_token is not None:
        store_oauth_token(CONFIG.slack_client_id, access_token)
        return {
            'headers': {'Content-Type': 'text/html'},
            'statusCode': 200,
            'body': 'Success : OAuth access token has been '
                    'provisioned and stored'}


def redirect_to_slack_authorize() -> dict:
    """Build a Slack OAuth 2 authorization URL and redirect the user to it

    :return: A dictionary of an API Gateway HTTP response
    """
    redirect_uri = 'https://{}/redirect_uri'.format(
        CONFIG.domain_name)
    # TODO : Do we want to pass a "state" argument here? If so we'll need
    # to store it in the client's cookies or somewhere

    # users:read scope must be requested at the same time as
    # users:read.email or the error "Invalid permissions requested" is
    # returned
    scopes = [
        'chat:write',
        'users:read',
        'users:read.email',
        'im:write'
    ]
    url = (
        'https://slack.com/oauth/v2/authorize?'
        'redirect_uri={redirect_uri}&'
        'client_id={client_id}&'
        'scope={scopes}'.format(
            redirect_uri=redirect_uri,
            client_id=CONFIG.slack_client_id,
            scopes=' '.join(scopes)
        ))
    return {
        'statusCode': 302,
        'headers': {
            'Location': url,
            'Cache-Control': 'max-age=0',
            'Content-Type': 'text/html'
        },
        'body': 'Redirecting to identity provider'
    }
