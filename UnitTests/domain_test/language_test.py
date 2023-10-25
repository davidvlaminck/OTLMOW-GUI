import os
from pathlib import Path

import pytest

from Domain.language_settings import return_language

ROOT_DIR = Path(__file__).parent

LOCALE_DIR = ROOT_DIR.parent.parent / 'locale/'


# Runt enkel samen met alle andere tests anders moet ../locale/ aangepast worden naar ../../locale/
def test_english_on_default():
    _ = return_language(LOCALE_DIR)
    assert _('own_reference') == 'Own reference'


def test_change_to_dutch_works():
    _ = return_language(LOCALE_DIR, 'nl_BE')
    assert _('own_reference') == 'Eigen referentie'


@pytest.mark.filterwarnings('ignore::UserWarning')
def test_other_languages_are_not_supported():
    _ = return_language(LOCALE_DIR, 'fr')
    assert _('own_reference') == 'Own reference'
