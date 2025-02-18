import random
import string
from typing import Optional, Any

from otlmow_model.OtlmowModel.BaseClasses.StringField import StringField
import re


class URIField(StringField):
    """Een tekstwaarde die een verwijzing naar meer informatie van het element bevat
    volgens http://www.w3.org/2001/XMLSchema#anyURI ."""
    naam = 'AnyURI'
    objectUri = 'http://www.w3.org/2001/XMLSchema#anyURI'
    definition = ('Een tekstwaarde die een verwijzing naar meer informatie van het element bevat '
                  'volgens http://www.w3.org/2001/XMLSchema#anyURI.')
    label = 'URI'
    usagenote = 'https://www.w3.org/TR/xmlschema-2/#anyURI'

    @classmethod
    def convert_to_correct_type(cls, value: str, log_warnings=True) -> Optional[str]:
        value = StringField.convert_to_correct_type(value, log_warnings=log_warnings)
        if value is not None and value.startswith('/eminfra'):
            return f'https://apps.mow.vlaanderen.be{value}'
        return value

    @classmethod
    def validate(cls, value: Any, attribuut) -> bool:
        if not StringField.validate(value, attribuut):
            return False

        regex = re.compile(
            r'^(?:http|ftp)s?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  
            r'(?::\d+)?' 
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)  # django url validation regex
        return re.match(regex, value) is not None

    def __str__(self) -> str:
        return StringField.__str__(self)

    @classmethod
    def create_dummy_data(cls) -> str:
        return 'http://' + ''.join(random.choice(string.ascii_letters)
                                   for _ in range(random.randint(5, 15))) + '.dummy'
