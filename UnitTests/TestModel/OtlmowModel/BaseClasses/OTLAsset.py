from abc import abstractmethod

from .OTLObject import OTLObject


class OTLAsset(OTLObject):
    @abstractmethod
    def __init__(self):
        super().__init__()
