import pytest

from Domain.language_settings import return_language


def test_english_on_default():
    _ = return_language('../../locale/')
    assert _('own_reference') == 'Own reference'


def test_change_to_dutch_works():
    _ = return_language('../../locale/', 'nl_BE')
    assert _('own_reference') == 'Eigen referentie'


@pytest.mark.filterwarnings('ignore::UserWarning')
def test_other_languages_are_not_supported():
    _ = return_language('../../locale/', 'fr')
    assert _('own_reference') == 'Own reference'
