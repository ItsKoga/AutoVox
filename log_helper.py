import logging
from logging.handlers import RotatingFileHandler

import datetime
import os

class LogColors:
    """Colors"""
    CRITICAL = '\033[0;31m'  # Red
    SUCCESS = '\033[0;32m'   # Green
    ERROR = '\033[0;33m'     # Yellow
    SYSTEM = '\033[0;34m'    # Blue
    INFO = '\033[0;35m'      # Purple
    USER_ACTION = '\033[0;36m' # Cyan
    NORMAL = '\033[0;37m'    # White


class LogTypes:
    """Log levels"""
    CRITICAL = "CRITICAL" # used for critical errors
    SUCCESS = "SUCCESS" # used for successful actions
    ERROR = "ERROR" # used for errors
    SYSTEM = "SYSTEM" # used for system messages
    INFO = "INFO" # used for information, like events
    USER_ACTION = "USER_ACTION" # used for user actions 
    NORMAL = "NORMAL" # used for normal messages

class Logger:
    """Logger class"""
    def __init__(self, type):
        self.type = type
        self.logger = logging.getLogger(type)
        self.logger.setLevel(logging.DEBUG)

    def create_logger(self, type):
        """Create a logger with the given type"""
        logger = logging.getLogger(type)
        logger.setLevel(logging.DEBUG)

        return logger

    def log(self, message, type:LogTypes=LogTypes.NORMAL):
        """Log a message with the given level"""
        color = {
            "CRITICAL": LogColors.CRITICAL,
            "SUCCESS": LogColors.SUCCESS,
            "ERROR": LogColors.ERROR,
            "SYSTEM": LogColors.SYSTEM,
            "INFO": LogColors.INFO,
            "USER_ACTION": LogColors.USER_ACTION,
            "NORMAL": LogColors.NORMAL
        }.get(type, LogColors.NORMAL)

        # clear the handler list
        self.logger.handlers.clear()

        #get date in format DD-MM-YYYY
        date = datetime.datetime.now().strftime("%d-%m-%Y")
        log_file_path = f"logs/{date}.log"

        # File and console handler
        try:
            file_handler = RotatingFileHandler(log_file_path, maxBytes=5000000, backupCount=2)
        except FileNotFoundError:
            os.makedirs("logs")
            file_handler = RotatingFileHandler(log_file_path, maxBytes=5000000, backupCount=2)
        console_handler = logging.StreamHandler()
        if type == LogTypes.NORMAL:
            file_handler.setFormatter(logging.Formatter(f"[%(asctime)s] [{self.type}] %(message)s", datefmt='%H:%M:%S'))
            console_handler.setFormatter(logging.Formatter(f"{color}[%(asctime)s] [{self.type}] %(message)s", datefmt='%H:%M:%S'))
        else:
            file_handler.setFormatter(logging.Formatter(f"[%(asctime)s] [{self.type}/{type}] %(message)s", datefmt='%H:%M:%S'))
            console_handler.setFormatter(logging.Formatter(f"{color}[%(asctime)s] [{self.type}/{type}] %(message)s", datefmt='%H:%M:%S'))
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # Log the message
        getattr(self.logger, type.lower(), self.logger.info)(message)

