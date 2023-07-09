import logging

class LoggingSingleton:
    __instance = None

    @staticmethod
    def get_instance():
        """Static access method to get the singleton instance."""
        if LoggingSingleton.__instance is None:
            LoggingSingleton()
        return LoggingSingleton.__instance

    def __init__(self):
        """Private constructor that initializes the logger."""
        if LoggingSingleton.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            LoggingSingleton.__instance = self
            logging.basicConfig(level=logging.DEBUG)  # Set desired logging level here
            self.logger = logging.getLogger()

    def log(self, message):
        """Logs the given message using the logger."""
        self.logger.debug(message)
        # You can use other logging methods like .info(), .warning(), etc.

# Usage example:
# logger = LoggingSingleton.get_instance()

