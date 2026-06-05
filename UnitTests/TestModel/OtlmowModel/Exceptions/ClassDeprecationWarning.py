import logging


class ClassDeprecationWarning(DeprecationWarning):
    def __init__(self, msg):
        super().__init__(msg)
        logging.warning(msg)
