import datetime
import logging
import warnings
from datetime import timedelta
from random import randrange
from typing import Optional, Any

from otlmow_model.OtlmowModel.Exceptions.CouldNotConvertToCorrectTypeError import CouldNotConvertToCorrectTypeError
from otlmow_model.OtlmowModel.BaseClasses.OTLField import OTLField
from otlmow_model.OtlmowModel.warnings.IncorrectTypeWarning import IncorrectTypeWarning


class DateTimeField(OTLField):
    """Beschrijft een datum volgens http://www.w3.org/2001/XMLSchema#dateTime."""
    naam = 'DateTime'
    objectUri = 'http://www.w3.org/2001/XMLSchema#dateTime'
    definition = 'Beschrijft een datum volgens http://www.w3.org/2001/XMLSchema#dateTime.'
    label = 'Datumtijd'
    usagenote = 'https://www.w3.org/TR/xmlschema-2/#dateTime'
    clearing_value = '88888888'

    @classmethod
    def validate(cls, value: Any, attribuut) -> bool:
        if value is not None and not isinstance(value, datetime.datetime):
            raise TypeError(f'expecting datetime in {attribuut.naam}')
        return True

    @classmethod
    def convert_to_correct_type(cls, value: Any, log_warnings: bool = True) -> Optional[datetime.datetime]:
        if value is None:
            return None
        if isinstance(value, bool):
            raise CouldNotConvertToCorrectTypeError(
                f'{value} could not be converted to correct type (implied by {cls.__name__})')
        if isinstance(value, datetime.datetime):
            return value
        if isinstance(value, datetime.date):
            if log_warnings:
                warnings.warn(category=IncorrectTypeWarning,
                              message='Assigned a date to a datetime datatype. '
                                      'Automatically converted to the correct type. Please change the type')
            return datetime.datetime(year=value.year, month=value.month, day=value.day)
        if isinstance(value, int):
            if log_warnings:
                warnings.warn(category=IncorrectTypeWarning,
                              message='Assigned a int to a datetime datatype. '
                                      'Automatically converted to the correct type. Please change the type')
            timestamp = datetime.datetime.fromtimestamp(value, datetime.timezone.utc)
            return datetime.datetime(timestamp.year, timestamp.month, timestamp.day, timestamp.hour, timestamp.minute,
                                     timestamp.second)
        if isinstance(value, str):
            try:
                if 'T' in value:
                    dt = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
                else:
                    dt = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                if log_warnings:
                    warnings.warn(category=IncorrectTypeWarning,
                                  message='Assigned a string to a datetime datatype. '
                                          'Automatically converted to the correct type. Please change the type')
                return dt
            except ValueError:
                try:
                    if 'T' in value:
                        dt = datetime.datetime.strptime(value, "%d/%m/%YT%H:%M:%S")
                    else:
                        dt = datetime.datetime.strptime(value, "%d/%m/%Y %H:%M:%S")
                    if log_warnings:
                        warnings.warn(category=IncorrectTypeWarning,
                                      message='Assigned a string to a datetime datatype. '
                                              'Automatically converted to the correct type. Please change the type')
                    return dt
                except Exception as e:
                    raise CouldNotConvertToCorrectTypeError(
                        f'{value} could not be converted to correct type (implied by {cls.__name__})'
                    ) from e
        try:
            return datetime.datetime(value)
        except Exception as exc:
            raise CouldNotConvertToCorrectTypeError(
                f'{value} could not be converted to correct type (implied by {cls.__name__})'
            ) from exc

    @classmethod
    def value_default(cls, value: datetime.datetime) -> str:
        return value.strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self) -> str:
        return OTLField.__str__(self)

    @staticmethod
    def random_date(start: datetime.datetime, end: datetime.datetime) -> datetime.datetime:
        delta = end - start
        int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
        random_second = randrange(int_delta)
        return start + timedelta(seconds=random_second)

    @classmethod
    def create_dummy_data(cls) -> datetime.datetime:
        return DateTimeField.random_date(start=datetime.datetime(2000, 1, 1),
                                         end=datetime.datetime(2020, 1, 1))
