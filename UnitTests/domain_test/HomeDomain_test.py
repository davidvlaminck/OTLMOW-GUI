from pathlib import Path
from unittest.mock import Mock

import pytest

from Domain.Settings import Settings
from Domain.step_domain.HomeDomain import HomeDomain
from Exceptions.EmptyFieldError import EmptyFieldError
from Exceptions.WrongDatabaseError import WrongDatabaseError

ROOT_DIR = Path(__file__).parent

LOCALE_DIR = ROOT_DIR.parent.parent / 'locale/'


@pytest.fixture
def home_domain() -> HomeDomain:
    HomeDomain.init_static(home_screen=Mock())


def test_validate_with_good_values():
    db_path = str(Path(
        __file__).parent.parent / 'project_files_test' / 'OTLWizardProjects' / 'Projects' / 'project_1' / 'OTL_AllCasesTestClass_no_double_kard.db')
    assert HomeDomain.validate('test', 'test', db_path) is True


def test_validate_with_empty_eigen_ref():
    db_path = str(Path(
        __file__).parent.parent / 'project_files_test' / 'OTLWizardProjects' / 'Projects' / 'project_1' / 'OTL_AllCasesTestClass_no_double_kard.db')
    with pytest.raises(EmptyFieldError):
        HomeDomain.validate('', 'test', db_path)


def test_validate_with_empty_bestek():
    db_path = str(Path(
        __file__).parent.parent / 'project_files_test' / 'OTLWizardProjects' / 'Projects' / 'project_1' / 'OTL_AllCasesTestClass_no_double_kard.db')
    with pytest.raises(EmptyFieldError):
        HomeDomain.validate('test', '', db_path)


def test_validate_with_bad_db():
    db_path = str(Path(
        __file__).parent.parent / 'project_files_test' / 'OTLWizardProjects' / 'Projects' / 'bad_files' / 'bad.db')
    with pytest.raises(WrongDatabaseError):
        HomeDomain.validate('test', 'test', db_path)

def test_validate_with_empty_db():

    with pytest.raises(EmptyFieldError):
        HomeDomain.validate('test', 'test', "")