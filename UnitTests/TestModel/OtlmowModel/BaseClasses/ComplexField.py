from abc import ABC
from .OTLField import OTLField


class ComplexField(OTLField, ABC):
    def __str__(self) -> str:
        return OTLField.__str__(self)

    waarde_shortcut_applicable = False
    native_type = dict
