import os
from pathlib import Path

import pytest

from Domain.subset_db import SubsetDatabase
from Exceptions.NotASqlliteFileError import NotASqlliteFileError
from Exceptions.WrongDatabaseError import WrongDatabaseError

ROOT_DIR = Path(__file__).parent.parent


def test_subset_db_raises_file_runtime_error_when_path_is_empty():
    with pytest.raises(NotASqlliteFileError):
        SubsetDatabase(Path(''))

def test_subset_db_raises_file_not_found_error_when_path_does_not_exist():
    with pytest.raises(FileNotFoundError):
        SubsetDatabase(Path('does_not_exist.db'))


def test_subset_db_returns_correct_info_project():
    subset_db = SubsetDatabase(Path(ROOT_DIR / 'project_files_test' / 'OTLWizardProjects' / 'Projects' / 'project_1' / 'OTL_AllCasesTestClass_no_double_kard.db'))
    info = subset_db.get_general_info_project()
    assert info == [('Filename', 'OSLO-AWV-VOC'), ('Date', '1/04/2022 10:20:35'), ('Operator', 'davyv'), ('Version', '2.3.0')]
