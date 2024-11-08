import logging


class ClassDeprecationWarning(DeprecationWarning):
    def __init__(self, msg):
        logging.warning(msg)
