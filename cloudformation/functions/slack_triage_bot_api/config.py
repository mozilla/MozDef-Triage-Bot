import os


class Config:
    def __init__(self):
        self.domain_name = os.getenv('DOMAIN_NAME')
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')


CONFIG = Config()
