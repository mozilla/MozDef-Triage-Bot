import json
import logging
import traceback
import urllib.parse
import requests

from .config import CONFIG

from .utils import (
    call_slack,
    emit_to_mozdef,
    provision_token,
    redirect_to_slack_authorize,
    SlackException
)

logger = logging.getLogger()
logging.getLogger().setLevel(CONFIG.log_level)
logging.getLogger('boto3').propagate = False
logging.getLogger('botocore').propagate = False
logging.getLogger('urllib3').propagate = False


def get_user_from_email(email: str) -> dict:
    """Fetch a slack user dictionary for an email address

    Required slack scopes
    * bot - users:read.email : https://api.slack.com/methods/users.lookupByEmail
    * bot - users:read : This scope must be requested if users:read.email is
                         requested
    :param email: email address of the slack user
    :return: dictionary of user information
    """
    data = {'email': email}
    url = 'https://slack.com/api/users.lookupByEmail'
    return call_slack(url, data, 'user')


def create_slack_channel(user: str) -> dict:
    """Create an IM channel with a user

    Required slack scopes
    * bot - im:write : https://api.slack.com/methods/conversations.open

    :param user: The Slack user ID of the user to create an IM channel with
    :return: dictionary of channel information
    """
    data = {'users': user}
    url = 'https://slack.com/api/conversations.open'
    return call_slack(url, data, 'channel', True)


def compose_message(
        identifier: str,
        alert: str,
        summary: str,
        email: str,
        user: dict,
        identity_confidence: str) -> dict:
    """Create a Slack message object

    :param identifier: The unique identifier for this message
    :param alert: The name of the MozDef alert
    :param summary: The summary text of the alert
    :param email: The email address of the user
    :param user: The slack user dictionary
    :param identity_confidence: The identity confidence sent from MozDef
    :return: A Slack message dictionary
    """

    default_response = {
        'identifier': identifier,
        'email': email,
        'slack_name': user['name'],
        'alert': alert,
        'identity_confidence': identity_confidence
    }

    # TODO : Add something that if the identity_confidence is high don't offer
    # the wronguser option
    blocks = [
        {
            "block_id": "mozdef-triage-bot-api-question",
            "text": {
                "text": "{}\nWas this action taken by you ({})?".format(
                    summary, email),
                "type": "mrkdwn",
            },
            "type": "section"
        },
        {
            "block_id": "mozdef-triage-bot-api-answer",
            "type": "actions",
            "elements": [
                {
                    "action_id": "mozdef-triage-bot-api-yes",
                    "style": "primary",
                    "text": {
                        "emoji": False,
                        "text": "Yes, I did that",
                        "type": "plain_text"
                    },
                    "type": "button",
                    "value": json.dumps(
                        {**default_response, "response": "yes"})
                },
                {
                    "action_id": "mozdef-triage-bot-api-no",
                    "style": "danger",
                    "text": {
                        "emoji": False,
                        "text": "No, I didn't do that!",
                        "type": "plain_text",
                    },
                    "type": "button",
                    "confirm": {
                        "confirm": {
                            "text": "Ya, I didn't take that action",
                            "type": "plain_text"
                        },
                        "deny": {
                            "text": "Oh, nevermind, I did do that",
                            "type": "plain_text"
                        },
                        "text": {
                            "text": "Are you sure that you didn't take that "
                                    "action? If you're sure then someone in "
                                    "the security team will contact you to "
                                    "follow up.".format(email),
                            "type": "mrkdwn"
                        },
                        "title": {
                            "text": "Are you sure?", "type": "plain_text"}
                    },

                    "value": json.dumps({**default_response, "response": "no"})
                }
            ]
        }
    ]
    if identity_confidence in ['moderate', 'low', 'lowest']:
        blocks[1]['elements'].append(
            {
                "action_id": "mozdef-triage-bot-api-wronguser",
                "text": {
                    "text": "You've got the wrong person",
                    "type": "plain_text"
                },
                "confirm": {
                    "confirm": {
                        "text": "Ya, that's not me",
                        "type": "plain_text"
                    },
                    "deny": {
                        "text": "Oh, actually that is me",
                        "type": "plain_text"
                    },
                    "text": {
                        "text": (
                            "Are you sure that {} isn't you and we've sent "
                            "this alert to the wrong user?".format(email)),
                        "type": "mrkdwn"
                    },
                    "title": {"text": "Are you sure?", "type": "plain_text"}
                },
                "type": "button",
                "value": json.dumps(
                    {**default_response, "response": "wronguser"})
            }
        )
    blocks[1]['elements'].append(
        {
            "action_id": "mozdef-triage-bot-api-notsure",
            "text": {
                "text": "Hmm... I'm not sure",
                "type": "plain_text"
            },
            "type": "button",
            "value": json.dumps({**default_response, "response": "notsure"})
        }
    )
    blocks_json = json.dumps(blocks)

    # We can't pass "as_user": False here as doing so causes the Slack API to
    # return an error that the chat:write:bot scope is missing
    # Slack support reports this is a known bug
    # https://mozilla-sandbox-scim.slack.com/help/requests/2564183
    message = {
        'blocks': blocks_json,
        'text': summary
    }
    return message


def post_message(channel: str, message: dict) -> dict:
    """Post a message to a slack channel

    Required slack scopes
    * bot - chat:write : https://api.slack.com/methods/chat.postMessage

    :param channel: The Slack channel ID to post the message to
    :param message: The message to post
    :return: A slack message dictionary
    """
    data = message
    data['channel'] = channel
    url = 'https://slack.com/api/chat.postMessage'
    return call_slack(url, data, 'message', True)


def send_message_to_slack(
        identifier: str,
        alert: str,
        summary: str,
        email_address: str,
        identity_confidence: str) -> dict:
    """Send a message to a user via IM or Slack App conversation

    :param identifier: The unique identifier sent by MozDef originally
    :param alert: The name of the MozDef alert
    :param summary: The summary text of the alert
    :param email_address: The user's email address
    :param identity_confidence: The identityConfidence sent by MozDef
                                originally
    :return: A slack message dictionary
    """
    send_to_im = False
    user = get_user_from_email(email_address)
    message = compose_message(
        identifier, alert, summary, email_address, user, identity_confidence)
    if send_to_im:
        channel = create_slack_channel(user['id'])
        post_result = post_message(channel['id'], message)
    else:
        post_result = post_message(user['id'], message)
    return post_result


def send_slack_message_response(
        response_url: str,
        message: dict,
        user_response: str) -> bool:
    """Respond to a user's selection by updating the Slack message with a reply

    :param response_url: The Slack URL to send message responses to
    :param message: The original message that the user made a selection from
    :param user_response: The user's selection
    :return: Whether or not the response to the user succeeded
    """
    if user_response == 'yes':
        bot_response = (
            ':heavy_check_mark: Understood, thanks for letting us know.')
    elif user_response == 'no':
        bot_response = (
            ':open_mouth: Got it, thank you. Someone from the security team '
            'will contact you to follow up on this.')
    elif user_response == 'wronguser':
        bot_response = (
            ":flushed: Oh, sorry about that. Someone from the security team "
            "will look into this and contact the right user. Sorry to bother "
            "you.")
    elif user_response == 'notsure':
        bot_response = (
            ":ok_hand: No problem. Someone from the security team will "
            "contact you to follow up on this.")
    else:
        bot_response = (
            ":heavy_multiplication_x: Hmm, I had some kind of internal error. "
            "Would you contact the security team to let them know that I'm "
            "unwell?")

    if 'mozdef-triage-bot-api-response' in [x.get('block_id') for x
                                            in message.get('blocks', [])]:
        bot_response = "You've changed your mind, no problem. " + bot_response
    response_block = {
        'block_id': 'mozdef-triage-bot-api-response',
        'text': {
            'text': bot_response,
            'type': "mrkdwn"
        },
        "type": "section"
    }
    if 'blocks' in message:
        for i in range(0, len(message['blocks'])):
            if message['blocks'][i].get('block_id') == 'mozdef-triage-bot-api-response':
                message['blocks'][i] = response_block
                break
        else:
            message['blocks'].append(response_block)

    message['replace_original'] = True
    try:
        response = requests.post(
            url=response_url,
            json=message
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(
            'POST of response to {} failed {} : {} : {} : {}'.format(
                response_url,
                message,
                e,
                getattr(e.response, 'status_code', None),
                getattr(e.response, 'text', None)
            ))
        return False
    return True


def handle_message_interaction(payload: dict) -> bool:
    """Process a user's interaction with a Slack message

    payload['type'] :
        'block_actions' : Parse the value that the user chose, send it to
                          MozDef and send a response to the user
    :param payload: A dictionary of data sent from Slack about a user's
                    interaction
    :return: Whether or not the response to the user succeeded
    """
    # The right way to do this is
    # 1. Drop a message in a message queue (e.g. SQS) with the message to
    #    send back to the user
    # 2. Return 200
    # 3. Pull that message off the queue
    # 4. POST to the response_url with the response message
    # Until that's added we'll just
    # 1. POST to the response_url with the response message
    # 2. Hope that the POST completes in under 3 seconds and return 200
    if payload.get('type') == 'block_actions':
        # User clicked a Block Kit interactive component
        for action in payload.get('actions', []):
            if 'value' not in action:
                raise SlackException(
                    'Action encountered with no value : {}'.format(action))
            try:
                value = json.loads(action['value'])
            except json.decoder.JSONDecodeError as e:
                logger.error('Failed to parse button value "{}" : {}'.format(
                    action['value'],
                    e
                ))
                raise
            message_id = emit_to_mozdef(
                value.get('identifier'),
                value.get('email'),
                payload.get('user', {}).get('id'),
                value.get('slack_name'),
                value['identity_confidence'],
                value.get('response')
            )
            allowed_keys = [
                'text', 'blocks', 'attachments', 'thread_ts', 'mrkdwn']
            original_message = {
                k: v for k, v in
                payload.get('message', {}).items()
                if k in allowed_keys}
            return send_slack_message_response(
                payload.get('response_url'),
                original_message,
                value.get('response'))
    else:
        # https://api.slack.com/interactivity/handling#payloads
        logger.error(
            "Encountered a message interaction payload type that hasn't yet "
            "been developed : {}".format(payload))
        return False


def process_api_call(
        event: dict,
        query_string_parameters: dict,
        body: dict) -> dict:
    """Process an API Gateway call depending on the URL path called

    :param event: The API Gateway request event
    :param query_string_parameters: A dictionary of query string parameters
    :param body: The parsed body that was POSTed to the API Gateway
    :return: A dictionary of an API Gateway HTTP response
    """
    if event.get('path') == '/error':
        return {
            'headers': {'Content-Type': 'text/html'},
            'statusCode': 400,
            'body': "Since you requested the /error API endpoint I'll go "
                    "ahead and serve back a 400"}
    elif event.get('path') == '/test':
        return {
            'headers': {'Content-Type': 'text/html'},
            'statusCode': 200,
            'body': 'API request received'}
    elif event.get('path') == '/redirect_uri':
        return provision_token(query_string_parameters)
    elif event.get('path') == '/authorize':
        return redirect_to_slack_authorize()
    elif event.get('path') == '/slack/interactive-endpoint':
        for payload_raw in body.get('payload', []):
            payload = json.loads(payload_raw)
            logger.debug('payload is {}'.format(payload))
            result = handle_message_interaction(payload)
        return {
            'headers': {'Content-Type': 'text/html'},
            'statusCode': 200,
            'body': 'Acknowledged'}
    elif event.get('path') == '/slack/options-load-endpoint':
        # https://api.slack.com/reference/block-kit/block-elements#external_select
        return {
            'headers': {'Content-Type': 'text/html'},
            'statusCode': 200,
            'body': 'Acknowledged'}
    else:
        return {
            'headers': {'Content-Type': 'text/html'},
            'statusCode': 404,
            'body': "That path wasn't found"}


def lambda_handler(event: dict, context: dict) -> dict:
    """Handler for all API Gateway requests

    :param event: AWS API Gateway input fields for AWS Lambda
    :param context: Lambda context about the invocation and environment
    :return: An AWS API Gateway output dictionary for proxy mode
    """
    logger.debug('event is {}'.format(event))
    if event.get('resource') == '/{proxy+}':
        try:
            headers = event['headers'] if event['headers'] is not None else {}
            cookie_header = headers.get('Cookie', '')
            referer = headers.get('Referer', '')
            query_string_parameters = (
                event['queryStringParameters']
                if event['queryStringParameters'] is not None else {})

            parser = None
            if headers.get('Content-Type') == 'application/x-www-form-urlencoded':
                parser = urllib.parse.parse_qs
            elif headers.get('Content-Type') == 'application/json':
                parser = json.loads
            if parser is not None and event.get('body') is not None:
                body = parser(event['body'])
            else:
                body = {}
            return process_api_call(event, query_string_parameters, body)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return {
                'headers': {'Content-Type': 'text/html'},
                'statusCode': 500,
                'body': 'Error'}
    else:
        # Not an API Gateway invocation, we'll assume a direct Lambda invocation
        try:
            if event.get('action') == 'discover-sqs-queue-url':
                result = CONFIG.queue_url
            else:
                try:
                    result = send_message_to_slack(
                        event.get('identifier'),
                        event.get('alert'),
                        event.get('summary'),
                        event.get('user'),
                        event.get('identityConfidence')
                    )
                except SlackException as e:
                    result = e
        except Exception as e:
            result = str(e)
        return result