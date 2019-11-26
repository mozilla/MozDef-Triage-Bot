import logging
import traceback

from .config import CONFIG
from .utils import (
    foo
)

logger = logging.getLogger()
logging.getLogger().setLevel(CONFIG.log_level)
logging.getLogger('boto3').propagate = False
logging.getLogger('botocore').propagate = False
logging.getLogger('urllib3').propagate = False


def send_message_to_slack() -> str:
    result = foo()
    return result


def lambda_handler(event: dict, context: dict) -> dict:
    """Handler for all API Gateway requests

    :param event: AWS API Gateway input fields for AWS Lambda
    :param context: Lambda context about the invocation and environment
    :return: An AWS API Gateway output dictionary for proxy mode
    """
    logger.debug('event is {}'.format(event))
    try:
        if event.get('resource') == '/{proxy+}':
            # this invocation comes from API Gateway
            if event.get('path') == '/error':
                return {
                    'headers': {'Content-Type': 'text/html'},
                    'statusCode': 400,
                    'body': "Since you requested the /error API endpoint I'll go ahead and serve back a 400"}
            elif event.get('path') == '/test':
                return {
                    'headers': {'Content-Type': 'text/html'},
                    'statusCode': 200,
                    'body': 'API request received'}
            else:
                return {
                    'headers': {'Content-Type': 'text/html'},
                    'statusCode': 404,
                    'body': "That path wasn't found"}
        else:
            # Not an API Gateway invocation, we'll assume a direct Lambda invocation
            return {'result': send_message_to_slack()}
    except Exception as e:
        logger.error(str(e))
        logger.error(traceback.format_exc())
        return {
            'headers': {'Content-Type': 'text/html'},
            'statusCode': 500,
            'body': 'Error'}
