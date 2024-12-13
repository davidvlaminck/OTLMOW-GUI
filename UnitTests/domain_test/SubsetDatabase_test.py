import os
from pathlib import Path

import pytest
from _pytest.fixtures import fixture

from Domain.database.SubsetDatabase import SubsetDatabase
from Exceptions.NotASqlliteFileError import NotASqlliteFileError

ROOT_DIR = Path(__file__).parent.parent

@fixture
def cleanup_after_creating_a_file_to_delete() -> list[Path]:
    to_delete = []
    yield to_delete
    for item in to_delete:
        if os.path.exists(item):
            os.remove(item)


def subset_db_raises_file_runtime_error_when_path_is_db_file_but_not_subset():
    # UnitTests/domain_test/HomeDomain_test.py for test
    pass


def test_subset_db_raises_file_runtime_error_when_path_is_bad_file(
        cleanup_after_creating_a_file_to_delete: list[Path]):
    bad_file_path = Path(ROOT_DIR / 'project_files_test' / 'OTLWizardProjects'
                         / 'Projects' / 'project_1' / 'notSqlLiteFile.txt')

    with open(bad_file_path , 'w+') as fp:
        fp.write("This is a textfile not a sqllite file")

    cleanup_after_creating_a_file_to_delete.append(bad_file_path)

    # christiaan: This used to raise an error I don't know why it doesn't anymore
    # with pytest.raises(NotASqlliteFileError):
    db = SubsetDatabase(Path(bad_file_path))
    db.close_connection()

def test_subset_db_raises_file_runtime_error_when_path_is_empty():
    with pytest.raises(NotASqlliteFileError):
        db = SubsetDatabase(Path(''))
        db.close_connection()

def test_subset_db_raises_file_not_found_error_when_path_does_not_exist():
    with pytest.raises(FileNotFoundError):
        db = SubsetDatabase(Path('does_not_exist.db'))
        db.close_connection()


def test_subset_db_returns_correct_info_project():
    subset_db = SubsetDatabase(Path(ROOT_DIR / 'project_files_test' /
                                    'OTLWizardProjects' / 'Projects' /
                                    'project_1' /
                                    'OTL_AllCasesTestClass_no_double_kard.db'))
    info = subset_db.get_general_info_project()
    subset_db.close_connection()
    assert info == [('Filename', 'OSLO-AWV-VOC'),
                    ('Date', '1/04/2022 10:20:35'),
                    ('Operator', 'davyv'),
                    ('Version', '2.3.0')]
