from rich.logging import RichHandler
from rich.console import Console
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


class CallbackHandler(logging.Handler):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def emit(self, record):
        log_entry = self.format(record)
        self.callback(log_entry)


def setup_logging(level=logging.INFO,  print_callback=None):
    # Create a custom logger
    log_file = datetime.datetime.now().strftime('log/%y-%m-%d.log')
    logger = logging.getLogger(__name__)
    logger.setLevel(level)

    # Create a TimedRotatingFileHandler
    file_handler = TimedRotatingFileHandler(
        log_file, when='midnight', interval=1, backupCount=7)
    file_handler.setLevel(level)

    # Create a formatter that includes the username for the file
    file_formatter = logging.Formatter(
        f'%(asctime)s %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    # Register the CallbackHandler if a print callback is provided
    if print_callback:
        callback_handler = CallbackHandler(print_callback)
        # Using RichHandler for enhanced terminal output
        rich_handler = RichHandler()
        logger.addHandler(rich_handler)

    return logger

# Custom print function using Rich


def custom_print_format(log_entry):
    console = Console()
    console.log(log_entry)  # Using rich to print the log entry
