import logging
from logging.handlers import TimedRotatingFileHandler

import os
import getpass
import datetime
from rich import print

# Create a logs directory if it doesn't exist
if not os.path.exists('log'):
    os.makedirs('log')

# Fetch the username of the device
username = getpass.getuser()

# Configure logging




def setup_logging(level=logging.INFO, username='user'):
    # Create a custom logger
    log_file = datetime.datetime.now().strftime('log/%y-%m-%d.log')
    logger = logging.getLogger(__name__)
    logger.setLevel(level)

    # Create a TimedRotatingFileHandler
    file_handler = TimedRotatingFileHandler(
        log_file, when='midnight', interval=1, backupCount=7)
    file_handler.setLevel(level)

    # Create a formatter that includes the username
    formatter = logging.Formatter(
        f'%(asctime)s [from {username}] %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    # Create a StreamHandler for terminal output
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    stream_handler.setFormatter(formatter)

    # Add the stream handler to the logger (prints logs to the console)
    logger.addHandler(stream_handler)

    return logger


def info(msg):

    date = datetime.datetime.now().strftime('%H:%M:%S')
    print(f'[black]({date})[/black] - [bold]{msg}')

def error(msg):
    date = datetime.datetime.now().strftime('%H:%M:%S')
    print(f'[black]({date})[/black] - [bold red]{msg}')

