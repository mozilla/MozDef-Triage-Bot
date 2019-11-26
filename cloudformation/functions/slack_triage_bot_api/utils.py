import logging

from .config import CONFIG

logger = logging.getLogger(__name__)
logger.setLevel(CONFIG.log_level)


def foo() -> str:
    return 'bar'
