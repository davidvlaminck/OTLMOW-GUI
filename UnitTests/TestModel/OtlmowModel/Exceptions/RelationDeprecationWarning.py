import logging


class RelationDeprecationWarning(DeprecationWarning):
    def __init__(self, msg):
        super().__init__(msg)
        logging.warning(msg)
