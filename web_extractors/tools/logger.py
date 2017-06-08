import logging
import os
from logging.handlers import RotatingFileHandler


class Logger:
    def __init__(self, name):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        path_to_logs = './logs/'
        try:
            os.mkdir(path_to_logs, 755)
        except Exception as e:
            pass

        file_handler = RotatingFileHandler(path_to_logs + name + '.log',
                                           'a', 1000000, 1)

        formatter = logging.Formatter(name + ' :: %(asctime)s :: %(levelname)s :: %(message)s')

        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)


if __name__ == "__main__":
    log = Logger("Logger")
    log.logger.debug("Test")
