import logging
from pathlib import Path


class OTLLogger:

    @classmethod
    def init(cls,logging_file: Path):
        file_handler = logging.FileHandler(logging_file)
        file_handler.setLevel(logging.DEBUG)
        logger = logging.getLogger()
        logger.addHandler(file_handler)
        logger.setLevel(logging.DEBUG)
        logger.handlers[0].setFormatter(logging.Formatter(fmt='%(asctime)s ln %(lineno)-4d:%(filename)-25s %(levelname)-8s %(message)s',
             datefmt='%Y-%m-%d %H:%M:%S'))
