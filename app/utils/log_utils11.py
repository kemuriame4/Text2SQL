import sys

from loguru import logger

def write_log():
    logger.remove()
    logger.add()