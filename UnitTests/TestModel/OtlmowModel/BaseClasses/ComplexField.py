from abc import ABC
from otlmow_model.OtlmowModel.BaseClasses.OTLField import OTLField


class ComplexField(OTLField, ABC):
    def __str__(self) -> str:
        return OTLField.__str__(self)

    waarde_shortcut_applicable = False
