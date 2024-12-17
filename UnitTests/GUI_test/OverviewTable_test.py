from pathlib import Path

import pytest

from Domain import global_vars
from Domain.project.Project import Project

from Domain.language_settings import return_language
from Exceptions.EmptySearchWarning import EmptySearchWarning
from GUI.screens.Home_elements.OverviewTable import OverviewTable

ROOT_DIR = Path(__file__).parent

LOCALE_DIR = ROOT_DIR.parent.parent / 'locale/'

TEST_DIR = ROOT_DIR / 'project_files_test/'


@pytest.fixture
def projects():
    global_vars.projects = [Project(project_path=None, subset_path=None, saved_documents_overview_path=None,
                                    eigen_referentie="testen", bestek="test", laatst_bewerkt=None),
                            Project(project_path=None, subset_path=None, saved_documents_overview_path=None,
                                    eigen_referentie="test2", bestek="test2", laatst_bewerkt=None),
                            Project(project_path=None, subset_path=None, saved_documents_overview_path=None,
                                    eigen_referentie="test3", bestek="test3", laatst_bewerkt=None)]


@pytest.fixture
def locale():
    return return_language(LOCALE_DIR)


def test_filter_function_with_nothing_returns_all_projects(locale, projects):
    assert len(OverviewTable.filter_projects(locale)) == 3
    global_vars.projects = []


def test_filter_function_with_search_returns_correct_projects(locale, projects):
    filter_result = OverviewTable.filter_projects(locale, 'testen')
    assert len(filter_result) == 1
    assert filter_result[0].bestek == 'test'
    global_vars.projects = []


def test_filter_function_with_search_not_in_set_returns_exception(projects, locale):
    with pytest.raises(EmptySearchWarning):
        OverviewTable.filter_projects(locale, 'banaan')
    global_vars.projects = []


def test_filter_function_returns_multiple_projects(projects, locale):
    filter_result = OverviewTable.filter_projects(locale, 'test')
    assert len(filter_result) == 3
    assert filter_result[0].bestek == 'test'
    assert filter_result[1].bestek == 'test2'
    global_vars.projects = []
