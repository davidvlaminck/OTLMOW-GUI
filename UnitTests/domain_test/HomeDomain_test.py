from pathlib import Path

import pytest

from Domain.Settings import Settings
from Domain.step_domain.HomeDomain import HomeDomain
from Exceptions.EmptyFieldError import EmptyFieldError
from Exceptions.WrongDatabaseError import WrongDatabaseError

ROOT_DIR = Path(__file__).parent

LOCALE_DIR = ROOT_DIR.parent.parent / 'locale/'


@pytest.fixture
def home_domain() -> HomeDomain:
    return HomeDomain(Settings.return_language(LOCALE_DIR))


def test_validate_with_good_values(home_domain: HomeDomain):
    db_path = str(Path(
        __file__).parent.parent / 'project_files_test' / 'OTLWizardProjects' / 'Projects' / 'project_1' / 'OTL_AllCasesTestClass_no_double_kard.db')
    assert home_domain.validate('test', 'test', db_path) is True


def test_validate_with_empty_eigen_ref(home_domain: HomeDomain):
    db_path = str(Path(
        __file__).parent.parent / 'project_files_test' / 'OTLWizardProjects' / 'Projects' / 'project_1' / 'OTL_AllCasesTestClass_no_double_kard.db')
    with pytest.raises(EmptyFieldError):
        home_domain.validate('', 'test', db_path)


def test_validate_with_empty_bestek(home_domain: HomeDomain):
    db_path = str(Path(
        __file__).parent.parent / 'project_files_test' / 'OTLWizardProjects' / 'Projects' / 'project_1' / 'OTL_AllCasesTestClass_no_double_kard.db')
    with pytest.raises(EmptyFieldError):
        home_domain.validate('test', '', db_path)


def test_validate_with_bad_db(home_domain: HomeDomain):
    db_path = str(Path(
        __file__).parent.parent / 'project_files_test' / 'OTLWizardProjects' / 'Projects' / 'bad_files' / 'bad.db')
    with pytest.raises(WrongDatabaseError):
        home_domain.validate('test', 'test', db_path)

def test_validate_with_empty_db(home_domain: HomeDomain):

    with pytest.raises(EmptyFieldError):
        home_domain.validate('test', 'test', "")