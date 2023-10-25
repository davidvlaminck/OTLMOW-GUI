import gettext
import warnings
from enum import Enum


# Switchen kan door in language en of nl_BE in te geven
# TODO: localedir omzetten naar locale_dir
# TODO: language inladen als enum
def return_language(localedir: str, language: str = None):
    if language is None:
        language = Language.ENGLISH.value
    elif language not in [lang.value for lang in Language]:
        warnings.warn("Language not supported. Defaulting to English")
        language = Language.ENGLISH.value
    translator = gettext.translation('messages', localedir=localedir, languages=[language])
    translator.install()
    return translator.gettext


# TODO: get you out of here in aparte file steken
class Language(Enum):
    ENGLISH = 'en'
    DUTCH = 'nl_BE'
