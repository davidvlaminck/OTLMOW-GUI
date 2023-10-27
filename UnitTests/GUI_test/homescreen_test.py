import sys
from pathlib import Path

import pytest
from PyQt6.QtWidgets import QApplication, QTableWidget

from Domain.database import Database
from Domain.home_domain import HomeDomain
from Domain.language_settings import return_language
from GUI.home_screen import HomeScreen

ROOT_DIR = Path(__file__).parent

LOCALE_DIR = ROOT_DIR.parent.parent / 'locale/'


@pytest.fixture
def db():
    db = Database()
    db.create_connection(":memory:")
    db.add_project('testen', 'test', 'test', None)
    db.add_project('test2', 'test2', 'test2', None)
    db.add_project('test3', 'test3', 'test3', None)
    return db


@pytest.fixture
def home_domain():
    db = Database()
    db.create_connection(":memory:")
    db.add_project('testen', 'test', 'test', None)
    db.add_project('test2', 'test2', 'test2', None)
    db.add_project('test3', 'test3', 'test3', None)
    home_domain = HomeDomain(db, return_language(LOCALE_DIR))
    return home_domain


@pytest.fixture
def locale():
    return return_language(LOCALE_DIR)


def test_filter_function_with_nothing_returns_all_projects(home_domain, locale, db):
    assert len(HomeScreen.filter_projects(locale, home_domain)) == 3


def test_filter_function_with_search_returns_correct_projects(home_domain, locale):
    assert HomeScreen.filter_projects(locale, home_domain, 'testen') == [(1, 'testen', 'test', 'test', None)]


def test_filter_function_with_search_not_in_set_returns_exception(home_domain, locale):
    with pytest.raises(Exception):
        HomeScreen.filter_projects(locale, home_domain, 'banaan')


def test_filter_function_returns_multiple_projects(home_domain, locale):
    assert HomeScreen.filter_projects(locale, home_domain, 'test') == [(1, 'testen', 'test', 'test', None),
                                                                       (2, 'test2', 'test2', 'test2', None),
                                                                       (3, 'test3', 'test3', 'test3', None)]
