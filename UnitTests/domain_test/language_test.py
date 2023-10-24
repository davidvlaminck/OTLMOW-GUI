import pytest

from Domain.language_settings import LanguageSettings


def test_english_on_default():
    language_settings = LanguageSettings()
    assert language_settings.language == 'en'


def test_change_to_dutch_works():
    language_settings = LanguageSettings()
    language_settings.set_language('nl_BE')
    assert language_settings.language == 'nl_BE'


@pytest.mark.filterwarnings('ignore::UserWarning')
def test_other_languages_are_not_supported():
    language_settings = LanguageSettings()
    language_settings.set_language('fr')
    assert language_settings.language == 'en'
