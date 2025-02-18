import logging


class RelationDeprecationWarning(DeprecationWarning):
    def __init__(self, msg):
        logging.warning(msg)
