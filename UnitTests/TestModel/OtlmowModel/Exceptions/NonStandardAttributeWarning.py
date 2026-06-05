import logging


class NonStandardAttributeWarning(Warning):
    def __init__(self, msg=None):
        super().__init__(msg)
        logging.warning(msg)
