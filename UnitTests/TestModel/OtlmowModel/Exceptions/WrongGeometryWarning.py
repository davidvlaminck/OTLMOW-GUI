import warnings


class WrongGeometryWarning(Warning):
    def __init__(self, msg: str = ''):
        super().__init__(msg)
        self.msg = msg
        warnings.warn('WrongGeometryWarning is now deprecated and replaced by an error', DeprecationWarning)
