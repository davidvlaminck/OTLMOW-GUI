from pathlib import Path

import pytest

from Domain.language_settings import return_language
from Domain.home_domain import HomeDomain
from Exceptions.EmptyFieldError import EmptyFieldError

ROOT_DIR = Path(__file__).parent

LOCALE_DIR = ROOT_DIR.parent.parent / 'locale/'


@pytest.fixture
def home_domain():
    return HomeDomain(return_language(LOCALE_DIR))


def test_validate_with_good_values(home_domain):
    assert home_domain.validate('test', 'test') is True


def test_validate_with_empty_eigen_ref(home_domain):
    with pytest.raises(EmptyFieldError):
        home_domain.validate('', 'test')


def test_validate_with_empty_bestek(home_domain):
    with pytest.raises(EmptyFieldError):
        home_domain.validate('test', '')
