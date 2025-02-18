import logging


class IncorrectTypeWarning(Warning):
    def __init__(self, msg):
        logging.warning(msg)
