import datetime
import os
from pathlib import Path

from Domain.Project import Project
from Domain.ProjectFileManager import ProjectFileManager

ROOT_DIR = Path(__file__).parent


def test_load_project_details_given_project_dir_location():
    project_dir_path = ROOT_DIR / 'sample_project_dir' / 'project_1'

    project = ProjectFileManager.get_project_from_dir(project_dir_path)

    assert project.project_path == Path(ROOT_DIR / 'sample_project_dir' / 'project_1')
    assert project.subset_path == Path(ROOT_DIR / 'sample_project_dir' / 'project_1' / 'OTL_AllCasesTestClass.db')
    assert project.assets_path == Path(ROOT_DIR / 'sample_project_dir' / 'project_1' / 'assets.json')
    assert project.eigen_referentie == "eigen referentie"
    assert project.bestek == "bestek"
    assert project.laatst_bewerkt == datetime.datetime(2023, 11, 1)


def test_save_project_given_details():
    project = Project()

    project.project_path = Path(ROOT_DIR / 'sample_project_dir' / 'project_2')
    project.subset_path = Path(ROOT_DIR / 'sample_project_dir' / 'project_2' / 'OTL_AllCasesTestClass.db')
    project.assets_path = Path(ROOT_DIR / 'sample_project_dir' / 'project_2' / 'assets.json')
    project.eigen_referentie = "eigen referentie"
    project.bestek = "bestek"
    project.laatst_bewerkt = datetime.datetime(2023, 11, 1)

    ProjectFileManager.get_otl_wizard_projects_dir = lambda: Path(ROOT_DIR / 'sample_project_dir')
    ProjectFileManager.save_project_to_dir(project)

    project_dir_path = ROOT_DIR / 'sample_project_dir' / 'project_2'
    assert project_dir_path.exists()
    assert (project_dir_path / 'project_details.json').exists()
    assert (project_dir_path / 'OTL_AllCasesTestClass.db').exists()
    assert (project_dir_path / 'assets.json').exists()

    generated_project = ProjectFileManager.get_project_from_dir(project_dir_path)
    assert generated_project.eigen_referentie == "eigen referentie"
    assert generated_project.bestek == "bestek"
    assert generated_project.laatst_bewerkt == datetime.datetime(2023, 11, 1)

    os.unlink(project_dir_path)
