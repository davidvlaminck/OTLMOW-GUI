import decimal
import random
import warnings
from typing import Optional, Any

from otlmow_model.OtlmowModel.BaseClasses.OTLField import OTLField
from otlmow_model.OtlmowModel.Exceptions.CouldNotConvertToCorrectTypeError import CouldNotConvertToCorrectTypeError
from otlmow_model.OtlmowModel.warnings.IncorrectTypeWarning import IncorrectTypeWarning


class FloatOrDecimalField(OTLField):
    """Beschrijft een decimaal getal volgens http://www.w3.org/2001/XMLSchema#decimal."""
    naam = 'Decimal'
    objectUri = 'http://www.w3.org/2001/XMLSchema#decimal'
    definition = 'Beschrijft een decimaal getal volgens http://www.w3.org/2001/XMLSchema#decimal.'
    label = 'Decimaal getal'
    usagenote = 'https://www.w3.org/TR/xmlschema-2/#decimal'
    clearing_value = 88888888.0

    @classmethod
    def convert_to_correct_type(cls, value: Any, log_warnings: bool = True) -> Optional[float]:
        if value is None:
            return None
        if isinstance(value, bool):
            if log_warnings:
                warnings.warn(category=IncorrectTypeWarning,
                              message='Assigned a boolean to a decimal datatype. '
                                      'Automatically converted to the correct type. Please change the type')
            return value
        if isinstance(value, float):
            return value
        if isinstance(value, (int, decimal.Decimal)):
            return float(value)
        try:
            float_value = float(value)
            if log_warnings:
                warnings.warn(category=IncorrectTypeWarning,
                              message='Assigned a string to a decimal datatype. '
                                      'Automatically converted to the correct type. Please change the type')
            return float_value
        except (ValueError, TypeError) as e:
            raise CouldNotConvertToCorrectTypeError(
                f'"{value}" could not be converted to correct type (implied by {cls.__name__})'
            ) from e

    @classmethod
    def validate(cls, value: Any, attribuut) -> bool:
        if value is not None:
            if isinstance(value, (bool, float)):
                return True
            raise TypeError(f'expecting a number (int, float or Decimal) in {attribuut.naam}')
        return True

    @classmethod
    def create_dummy_data(cls) -> float:
        return round(random.random() * 100, 2)

    def __str__(self) -> str:
        return OTLField.__str__(self)
