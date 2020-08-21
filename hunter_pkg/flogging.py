import logging
from os.path import basename
import sys


DEBUG = "DEBUG"
INFO = "INFO"
WARNING = "WARNING"
ERROR = "ERROR"
CRITICAL = "CRITICAL"

class Flogging():
    @classmethod
    def get(cls, name, log_level):
        converted_log_level = cls.convert_log_level(log_level)
        logger = logging.getLogger(basename(name))
        logger.handlers = []
        out_hdlr = logging.StreamHandler(sys.stdout)
        out_hdlr.setFormatter(logging.Formatter('|%(name)s|%(levelname)s|: %(message)s'))
        out_hdlr.setLevel(converted_log_level)
        logger.addHandler(out_hdlr)
        logger.setLevel(converted_log_level)

        return logger

    @classmethod
    def convert_log_level(cls, log_level):
        if log_level == DEBUG:
            return logging.DEBUG
        elif log_level == INFO:
            return logging.INFO
        elif log_level == WARNING:
            return logging.WARNING
        elif log_level == ERROR:
            return logging.ERROR
        else:
            raise Exception("Unrecognized log level")