import logging
from logging.handlers import TimedRotatingFileHandler
import os
import getpass
import datetime
# Create a logs directory if it doesn't exist
if not os.path.exists('log'):
    os.makedirs('log')

# Fetch the username of the device
username = getpass.getuser()

# Configure logging


def setup_logging(level=logging.INFO):
    # Create a custom logger
    log_file = datetime.datetime.now().strftime('log/%y-%m-%d.log')
    logger = logging.getLogger(__name__)
    logger.setLevel(level)

    # Create a TimedRotatingFileHandler
    handler = TimedRotatingFileHandler(
        log_file, when='midnight', interval=1, backupCount=7)
    handler.setLevel(level)

    # Create a formatter that includes the username
    formatter = logging.Formatter(
        f'%(asctime)s [from {username}] %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    return logger


# Example usage
if __name__ == '__main__':
    logger = setup_logging()

    logger.debug('This is a debug message')
    logger.info('This is an info message')
    logger.warning('This is a warning message')
    logger.error('This is an error message')
    logger.critical('This is a critical message')
