from enum import Enum


class Language(Enum):
    ENGLISH = 'en'
    DUTCH = 'nl_BE'


class FileState(Enum):
    ERROR = 'error'
    WARNING = 'warning'
    OK = 'ok'


class ReportAction(Enum):
    ATA = 'attribute added'
    ATR = 'attribute removed'
    ATC = 'attribute changed'
    ASS = 'asset added'
    REL = 'relation added'
