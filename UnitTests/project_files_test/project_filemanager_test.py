import datetime
from pathlib import Path

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
