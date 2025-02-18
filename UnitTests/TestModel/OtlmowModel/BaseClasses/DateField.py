import warnings
from datetime import date, datetime, timedelta, timezone
from random import randrange
from typing import Optional, Any

from otlmow_model.OtlmowModel.BaseClasses.OTLField import OTLField
from otlmow_model.OtlmowModel.Exceptions.CouldNotConvertToCorrectTypeError import CouldNotConvertToCorrectTypeError
from otlmow_model.OtlmowModel.warnings.IncorrectTypeWarning import IncorrectTypeWarning


class DateField(OTLField):
    """Beschrijft een datum volgens http://www.w3.org/2001/XMLSchema#date."""
    naam = 'Date'
    objectUri = 'http://www.w3.org/2001/XMLSchema#date'
    definition = 'Beschrijft een datum volgens http://www.w3.org/2001/XMLSchema#date.'
    label = 'Datum'
    usagenote = 'https://www.w3.org/TR/xmlschema-2/#date'
    clearing_value = '88888888'

    @classmethod
    def convert_to_correct_type(cls, value: Any, log_warnings: bool = True) -> Optional[date]:
        if value is None:
            return None
        if isinstance(value, bool):
            raise CouldNotConvertToCorrectTypeError(
                f'{value} could not be converted to correct type (implied by {cls.__name__})')
        if isinstance(value, datetime):
            if log_warnings:
                warnings.warn(category=IncorrectTypeWarning,
                              message='Assigned a datetime to a date datatype. '
                                      'Automatically converted to the correct type. Please change the type')
            return date(value.year, value.month, value.day)
        if isinstance(value, date):
            return value
        if isinstance(value, int):
            if log_warnings:
                warnings.warn(category=IncorrectTypeWarning,
                              message='Assigned a int to a date datatype. '
                                      'Automatically converted to the correct type. Please change the type')
            timestamp = datetime.fromtimestamp(value, timezone.utc)

            return date(timestamp.year, timestamp.month, timestamp.day)

        if isinstance(value, str):
            try:
                dt = datetime.strptime(value, "%Y-%m-%d")
                if log_warnings:
                    warnings.warn(category=IncorrectTypeWarning,
                                  message='Assigned a string to a date datatype. '
                                          'Automatically converted to the correct type. Please change the type')
                return date(dt.year, dt.month, dt.day)
            except ValueError:
                try:
                    dt = datetime.strptime(value, "%d/%m/%Y")
                    if log_warnings:
                        warnings.warn(category=IncorrectTypeWarning,
                                      message='Assigned a string to a date datatype. '
                                              'Automatically converted to the correct type. Please change the type')
                    return date(dt.year, dt.month, dt.day)
                except ValueError as e:
                    raise CouldNotConvertToCorrectTypeError(
                        f'{value} could not be converted to correct type (implied by {cls.__name__})'
                    ) from e
        raise CouldNotConvertToCorrectTypeError(
            f'{value} could not be converted to correct type (implied by {cls.__name__})')

    @classmethod
    def validate(cls, value: Any, attribuut) -> bool:
        if value is not None and not isinstance(value, date):
            raise TypeError(f'expecting date in {attribuut.naam}')
        return True

    @classmethod
    def value_default(cls, value: date) -> str:
        return value.strftime("%Y-%m-%d")

    def __str__(self) -> str:
        return OTLField.__str__(self)

    @classmethod
    def random_date(cls, start: date, end: date) -> date:
        delta = end - start
        int_delta = delta.days
        random_days = randrange(int_delta)
        return start + timedelta(days=random_days)

    @classmethod
    def create_dummy_data(cls) -> date:
        return DateField.random_date(start=date(2000, 1, 1),
                                     end=date(2020, 1, 1))
