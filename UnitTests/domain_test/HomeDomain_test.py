import shutil

from otlmow_gui.Domain import Project
from otlmow_gui.Domain.step_domain.HomeDomain import HomeDomain
from otlmow_gui.Exceptions.EmptyFieldError import EmptyFieldError
from otlmow_gui.Exceptions.WrongDatabaseError import WrongDatabaseError

from UnitTests.general_fixtures.GUIFixtures import *

ROOT_DIR = Path(__file__).parent

LOCALE_DIR = ROOT_DIR.parent.parent / 'locale/'

PARENT_OF_THIS_FILE = Path(__file__).parent.parent

@pytest.fixture
def home_domain() -> HomeDomain:
    HomeDomain.init_static(home_screen=Mock())

@fixture
def create_mock_project_project_1():
    project_path = Path(PARENT_OF_THIS_FILE / 'project_files_test' / 'OTLWizardProjects' / 'Projects' / 'project_1')
    project_backup_path = Path(PARENT_OF_THIS_FILE / 'project_files_test' / 'OTLWizardProjects' / 'Projects_backup' / project_path.name)
    # project = Project(
    #     project_path=project_path,
    #     subset_path=Path(
    #         PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1' /
    #         'OTL_AllCasesTestClass_no_double_kard.db'),
    #     assets_path=Path(
    #         PARENT_OF_THIS_FILE / 'OTLWizardProjects' / 'Projects' / 'project_1' / 'saved_documents.json'),
    #     eigen_referentie="project_1",
    #     bestek="bestek",
    #     laatst_bewerkt=datetime.datetime(2023, 11, 1))
    # project.save_project_to_dir()

    if project_path.exists():
        shutil.rmtree(project_path)
    shutil.copytree(project_backup_path,project_path)

    project = Project.load_project(project_path)

    yield project

    if project_path.exists():
        shutil.rmtree(project_path)

    shutil.copytree(project_backup_path,project_path)

def test_validate_with_good_values(create_mock_project_project_1,create_translations):
    db_path =  str(PARENT_OF_THIS_FILE / 'project_files_test' / 'OTLWizardProjects' / 'Projects' / 'project_1' / 'OTL_AllCasesTestClass_no_double_kard.db')
    assert HomeDomain.validate('test', 'test', db_path) is True


def test_validate_with_empty_eigen_ref(create_mock_project_project_1,create_translations):
    db_path = str(PARENT_OF_THIS_FILE / 'project_files_test' / 'OTLWizardProjects' / 'Projects' / 'project_1' / 'OTL_AllCasesTestClass_no_double_kard.db')
    with pytest.raises(EmptyFieldError):
        HomeDomain.validate('', 'test', db_path)


def test_validate_with_empty_bestek(create_mock_project_project_1,create_translations):
    db_path = str(PARENT_OF_THIS_FILE / 'project_files_test' / 'OTLWizardProjects' / 'Projects' / 'project_1' / 'OTL_AllCasesTestClass_no_double_kard.db')
    with pytest.raises(EmptyFieldError):
        HomeDomain.validate('test', '', db_path)


def test_validate_with_bad_db(create_translations):
    db_path = str(PARENT_OF_THIS_FILE / 'project_files_test' / 'OTLWizardProjects' / 'Projects' / 'bad_files' / 'bad.db')
    with pytest.raises(WrongDatabaseError):
        HomeDomain.validate('test', 'test', db_path)

def test_validate_with_empty_db(create_translations):

    with pytest.raises(EmptyFieldError):
        HomeDomain.validate('test', 'test', "")