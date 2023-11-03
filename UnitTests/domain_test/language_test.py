from pathlib import Path

from Domain.language_settings import return_language

from Domain.enums import Language

ROOT_DIR = Path(__file__).parent

LOCALE_DIR = ROOT_DIR.parent.parent / 'locale/'


def test_english_on_default():
    _ = return_language(LOCALE_DIR)
    assert _('own_reference') == 'Own reference'


def test_change_to_dutch_works():
    _ = return_language(LOCALE_DIR, Language.DUTCH)
    assert _('own_reference') == 'Eigen referentie'
