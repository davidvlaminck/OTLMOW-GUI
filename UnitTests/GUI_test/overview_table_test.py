import logging
from pathlib import Path

import pytest

from Domain.Project import Project
from Domain.ProjectFileManager import ProjectFileManager
from Domain.database import Database
from Domain.home_domain import HomeDomain
from Domain.language_settings import return_language
from Exceptions.EmptySearchWarning import EmptySearchWarning
from GUI.overviewtable import OverviewTable

ROOT_DIR = Path(__file__).parent

LOCALE_DIR = ROOT_DIR.parent.parent / 'locale/'

TEST_DIR = ROOT_DIR / 'project_files_test/'


@pytest.fixture
def db():
    db = Database()
    db.create_connection(":memory:")
    db.add_project('testen', 'test', 'test', None)
    db.add_project('test2', 'test2', 'test2', None)
    db.add_project('test3', 'test3', 'test3', None)
    return db


@pytest.fixture
def mock_homedomain():
    # This fixture will mock homedomain function to return a directory in the UnitTests directory
    # and defaults to 'mock_otlwizard_project_dir'
    orig_home_domain_func = HomeDomain.get_all_projects
    HomeDomain.get_all_projects = lambda: [Project(project_path=None, subset_path=None, assets_path=None,
                                                   eigen_referentie="testen", bestek="test", laatst_bewerkt=None),
                                           Project(project_path=None, subset_path=None, assets_path=None,
                                                   eigen_referentie="test2", bestek="test2", laatst_bewerkt=None),
                                           Project(project_path=None, subset_path=None, assets_path=None,
                                                   eigen_referentie="test3", bestek="test3", laatst_bewerkt=None)]
    yield
    HomeDomain.get_all_projects = orig_home_domain_func


@pytest.fixture
def locale():
    return return_language(LOCALE_DIR)


def test_filter_function_with_nothing_returns_all_projects(locale, db, mock_homedomain):
    assert len(OverviewTable.filter_projects(locale)) == 3


def test_filter_function_with_search_returns_correct_projects(locale, mock_homedomain):
    filter_result = OverviewTable.filter_projects(locale, 'testen')
    assert len(filter_result) == 1
    assert filter_result[0].bestek == 'test'


def test_filter_function_with_search_not_in_set_returns_exception(mock_homedomain, locale):
    with pytest.raises(EmptySearchWarning):
        OverviewTable.filter_projects(locale, 'banaan')


def test_filter_function_returns_multiple_projects(mock_homedomain, locale):
    filter_result = OverviewTable.filter_projects(locale, 'test')
    assert len(filter_result) == 3
    assert filter_result[0].bestek == 'test'
    assert filter_result[1].bestek == 'test2'
