import logging

class LoggerSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._configure_logger()
        return cls._instance

    def _configure_logger(self):
        # Create a logger instance
        self.logger = logging.getLogger("Logger")
        self.logger.setLevel(logging.DEBUG)

        # Create a console handler for CLI logs
        # console_handler = logging.StreamHandler()
        # console_handler.setLevel(logging.INFO)
        # console_formatter = logging.Formatter("%(levelname)s - %(message)s")
        # console_handler.setFormatter(console_formatter)

        # Create a file handler for file logs
        file_handler = logging.FileHandler("logs.log")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)

        error_handler = logging.StreamHandler()
        error_handler.setLevel(logging.ERROR)
        # error_handler.setFormatter(console_formatter)

        # Add handlers to the logger
        # self.logger.addHandler(console_handlxer)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)

    def log_info(self, message):
        self.logger.info(message)

    def log_debug(self, message):
        self.logger.debug(message)
    
    def log_error(self, message):
        self.logger.error(message)

# Usage:
logger = LoggerSingleton()
# logger.log_info("This is an info log message")
# logger.log_debug("This is a debug log message")

