import logging
from pathlib import Path


class OTLLogger:

    @classmethod
    def init(cls,logging_file: Path):
        logging.basicConfig(
            format='%(asctime)s %(levelname)-8s %(message)s',
            level=logging.DEBUG,
            datefmt='%Y-%m-%d %H:%M:%S')

        file_handler = logging.FileHandler(logging_file)
        file_handler.setLevel(logging.DEBUG)
        logging.getLogger().addHandler(file_handler)
