
from pathlib import Path
from typing import Callable

import pytest

from Domain import global_vars
from Domain.project.Project import Project

from Domain.Settings import Settings
from Domain.step_domain.HomeDomain import HomeDomain
from Exceptions.EmptySearchWarning import EmptySearchWarning
from GUI.screens.HomeScreen import HomeScreen
from GUI.screens.Home_elements.OverviewTable import OverviewTable

ROOT_DIR = Path(__file__).parent

LOCALE_DIR = ROOT_DIR.parent.parent / 'locale/'

TEST_DIR = ROOT_DIR / 'project_files_test/'
@pytest.fixture
def locale() -> Callable:
    return Settings.return_language(LOCALE_DIR)


@pytest.fixture
def projects(locale) -> HomeScreen:
    home_screen  = HomeScreen(locale)
    original_home_ref = global_vars.otl_wizard.main_window.home_screen
    global_vars.otl_wizard.main_window.home_screen = home_screen

    HomeDomain.init(home_screen)
    HomeDomain.projects = [Project(eigen_referentie="testen", project_path=None, subset_path=None,
                                   saved_documents_overview_path=None, bestek="test",
                                   laatst_bewerkt=None),
                           Project(eigen_referentie="test2", project_path=None, subset_path=None,
                                   saved_documents_overview_path=None, bestek="test2",
                                   laatst_bewerkt=None),
                           Project(eigen_referentie="test3", project_path=None, subset_path=None,
                                   saved_documents_overview_path=None, bestek="test3",
                                   laatst_bewerkt=None)]

    yield home_screen

    HomeDomain.projects.clear()
    global_vars.otl_wizard.main_window.home_screen = original_home_ref

@pytest.mark.skip
def test_filter_function_with_nothing_returns_all_projects(projects):

    home_screen = projects
    home_screen.table.filter("")
    assert len(home_screen.table) == 3
    HomeDomain.projects = []

@pytest.mark.skip
def test_filter_function_with_search_returns_correct_projects(locale, projects):
    filter_result = OverviewTable.filter('testen')
    assert len(filter_result) == 1
    assert filter_result[0].bestek == 'test'
    HomeDomain.projects = []

@pytest.mark.skip
def test_filter_function_with_search_not_in_set_returns_exception(projects, locale):
    with pytest.raises(EmptySearchWarning):
        OverviewTable.filter_projects(locale, 'banaan')
    HomeDomain.projects = []

@pytest.mark.skip
def test_filter_function_returns_multiple_projects(projects, locale):
    filter_result = OverviewTable.filter_projects(locale, 'test')
    assert len(filter_result) == 3
    assert filter_result[0].bestek == 'test'
    assert filter_result[1].bestek == 'test2'
    HomeDomain.projects = []
