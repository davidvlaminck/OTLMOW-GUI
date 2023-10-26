import sys

import pytest
from PyQt6.QtWidgets import QApplication

from Domain.database import Database
from GUI.home_screen import HomeScreen


@pytest.fixture
def db():
    db = Database()
    db.create_connection(":memory:")
    db.add_project('testen', 'test', 'test', None)
    db.add_project('test2', 'test2', 'test2', None)
    db.add_project('test3', 'test3', 'test3', None)
    return db


def test_right_amount_of_projects_loaded_in(db):
    app = QApplication(sys.argv)
    window = HomeScreen(db)
    assert len(window.projects) == 3
    app.quit()


def test_filter_function_with_nothing_returns_all_projects(db):
    app = QApplication(sys.argv)
    window = HomeScreen(db)
    window.filter_projects()
    assert len(window.projects) == 3
    app.quit()


def test_filter_function_with_search_returns_correct_projects(db):
    app = QApplication(sys.argv)
    window = HomeScreen(db)
    window.filter_projects("testen")
    assert len(window.projects) == 1
    app.quit()
