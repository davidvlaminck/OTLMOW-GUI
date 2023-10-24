from Domain.language_settings import return_language
from Domain.home_domain import HomeDomain
from Domain.database import Database


def test_get_amount_of_rows():
    db = Database()
    _ = return_language('../../locale/')
    db.create_connection(":memory:")
    home_domain = HomeDomain(db, _)
    assert home_domain.get_amount_of_rows() == 0
    db.close_connection()
