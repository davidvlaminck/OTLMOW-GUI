from enum import Enum


class Language(Enum):
    ENGLISH = 'en'
    DUTCH = 'nl_BE'


class FileState(Enum):
    ERROR = 'error'
    WARNING = 'warning'
    OK = 'ok'

