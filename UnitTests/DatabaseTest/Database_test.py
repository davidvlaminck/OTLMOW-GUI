import pytest

from domain.database import Database


@pytest.fixture
def db():
    db = Database()
    db.create_test_connection()
    return db


def test_create_connection(db):
    assert db.connection is not 0
    db.close_connection()


def test_new_database_is_empty(db):
    assert db.get_all_projects() == []
    db.close_connection()


def test_add_project(db):
    db.add_project('test', 'test', 'test', None)
    assert db.get_all_projects() == [(1, 'test', 'test', 'test', None)]
    db.close_connection()


def test_remove_project(db):
    db.add_project('test', 'test', 'test', None)
    db.remove_project(1)
    assert db.get_all_projects() == []
    db.close_connection()


def test_get_project_returns_project(db):
    db.add_project('test', 'test', 'test', None)
    assert db.get_project(1) == (1, 'test', 'test', 'test', None)
    db.close_connection()


def test_get_project_returns_none_if_no_project(db):
    assert db.get_project(1) is None
    db.close_connection()


def test_update_project(db):
    db.add_project('test', 'test', 'test', None)
    assert db.update_project(1, 'test2', 'test2', 'test2', None) == 1
    assert db.get_project(1) == (1, 'test2', 'test2', 'test2', None)
    db.close_connection()


def test_update_returns_zero_if_no_rows_affected(db):
    assert db.update_project(1, 'test2', 'test2', 'test2', None) == 0
    db.close_connection()
