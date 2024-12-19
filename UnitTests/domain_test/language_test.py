from pathlib import Path

from Domain.Settings import Settings

from Domain.enums import Language

ROOT_DIR = Path(__file__).parent

LOCALE_DIR = ROOT_DIR.parent.parent / 'locale/'


def test_dutch_on_default():
    _ = Settings.return_language(LOCALE_DIR)
    assert _('own_reference') == 'Eigen referentie'


def test_change_to_dutch_works():
    _ = Settings.return_language(LOCALE_DIR, Language.DUTCH)
    assert _('own_reference') == 'Eigen referentie'
