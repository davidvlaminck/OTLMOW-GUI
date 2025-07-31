import warnings


class WrongGeometryWarning(Warning):
    def __init__(self, message: str = ''):
        self.message = message
        warnings.warn('WrongGeometryWarning is now deprecated and replaced by an error', DeprecationWarning)
