import os


class Config:
    def __init__(self):
        self.parameter_store_prefix = '/SlackTriageBot'
        self.slack_token_parameter_store_name = '{}/SlackOAuthToken'.format(
            self.parameter_store_prefix)
        self.domain_name = os.getenv('DOMAIN_NAME')
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.slack_client_id = os.getenv('SLACK_CLIENT_ID')
        self.slack_client_secret = os.getenv('SLACK_CLIENT_SECRET')
        self.queue_url = os.getenv('QUEUE_URL')


CONFIG = Config()
