from typing import Any

from otlmow_model.OtlmowModel.BaseClasses.OTLField import OTLField
from otlmow_model.OtlmowModel.Exceptions.UnionTypeError import UnionTypeError


class UnionTypeField(OTLField):
    waarde_shortcut_applicable = False

    def __str__(self):
        return OTLField.__str__(self)

    @classmethod
    def validate(cls, value: Any, attribuut) -> bool:
        if value is None:
            return True
        if isinstance(value, attribuut.field.waardeObject):
            return True
        value_dict = vars(attribuut.field.waardeObject())
        for val_in_dict in value_dict.values():
            if val_in_dict is None:
                continue
            try:
                validate_result = val_in_dict.field.validate(value, val_in_dict)
                if validate_result:
                    return True
            except:
                raise UnionTypeError(f'Invalid value for {attribuut.naam}, '
                                     f'check attr_type_info to see what kind of values are valid.')
        raise UnionTypeError(f'Invalid value for {attribuut.naam}, '
                             f'check attr_type_info to see what kind of values are valid.')
