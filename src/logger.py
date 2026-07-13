import logging.handlers
import os
import sys

from .constant import DEBUG

__all__ = ['logger']
logger = logging.getLogger("Random Student Number Generator")
logger.setLevel(logging.DEBUG)

# Make Logger Formatter
fmt = '\n'.join((
    "[%(asctime)s] %(name)s's %(levelname)s Log",
    "On %(pathname)s, %(lineno)s, %(funcName)s; thread: %(threadName)s",
    "%(message)s",
    "", ""))
formatter = logging.Formatter(fmt=fmt, datefmt='%Y-%m-%d %H:%M:%S')

# Make Logger Handler
if DEBUG:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
os.makedirs('logging', exist_ok=True)
file_handler = logging.handlers.TimedRotatingFileHandler('logging/RSG.log', when='midnight', interval=1, backupCount=7)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)