import logging


class AttributeDeprecationWarning(DeprecationWarning):
    def __init__(self, msg):
        logging.warning(msg)