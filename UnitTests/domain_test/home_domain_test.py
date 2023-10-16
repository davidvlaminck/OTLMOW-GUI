import sys

from PyQt6.QtWidgets import QApplication

from Domain.home_domain import HomeDomain
from Domain.database import Database

def test_get_amount_of_rows():
    db = Database()
    db.create_connection(":memory:")
    home_domain = HomeDomain(db)
    assert home_domain.get_amount_of_rows() == 0
    db.close_connection()