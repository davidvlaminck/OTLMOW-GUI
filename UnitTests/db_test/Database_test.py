import datetime

import pytest

from Domain.database.Database import Database


@pytest.fixture
def db():
    db = Database()
    db.create_connection(":memory:")
    return db


def test_create_connection(db):
    assert db.connection != 0
    db.close_connection()


def test_new_database_is_empty(db):
    assert db.get_all_projects() == []
    db.close_connection()


def test_add_project(db):
    test_date = datetime.datetime.now()
    project_id = db.add_project('test', 'test', 'test', test_date)
    assert project_id == 1
    db.close_connection()


@pytest.mark.parametrize('eigen_ref, bestek, subset', [(1, 1, 1), (None, None, None)])
def test_add_project_with_non_string_values_returns_error(db, eigen_ref, bestek, subset):
    with pytest.raises(TypeError):
        db.add_project(eigen_ref, bestek, subset, None)
    db.close_connection()


def test_remove_project(db):
    db.add_project('test', 'test', 'test', None)
    db.remove_project(1)
    assert db.get_all_projects() == []
    db.close_connection()


def test_remove_project_that_does_not_exist(db):
    db.remove_project(1)
    assert db.get_all_projects() == []
    db.close_connection()


def test_remove_project_with_non_int_value(db):
    db.remove_project('test')
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


@pytest.mark.parametrize('eigen_ref, bestek, subset', [(1, 1, 1), (None, None, None)])
def test_update_project_with_non_string_values_returns_error(db, eigen_ref, bestek, subset):
    db.add_project('test', 'test', 'test', None)
    with pytest.raises(TypeError):
        db.update_project(1, eigen_ref, bestek, subset, None)
    db.close_connection()


def test_update_returns_zero_if_no_rows_affected(db):
    assert db.update_project(1, 'test2', 'test2', 'test2', None) == 0
    db.close_connection()


def test_count_projects(db):
    db.add_project('test', 'test', 'test', None)
    assert db.count_projects() == 1
    db.close_connection()


def test_count_projects_empty(db):
    assert db.count_projects() == 0
    db.close_connection()
