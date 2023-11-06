import gettext
from enum import Enum
from pathlib import Path

from Domain.enums import Language


# Switchen kan door in language en of nl_BE in te geven
def return_language(locale_dir: Path, language: Enum = None):
    if language is None:
        language = Language.ENGLISH
    translator = gettext.translation('messages', localedir=locale_dir, languages=[language.value])
    translator.install()
    return translator.gettext



