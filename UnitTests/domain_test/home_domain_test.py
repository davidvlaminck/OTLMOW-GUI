from Domain.language_settings import LanguageSettings
from Domain.home_domain import HomeDomain
from Domain.database import Database


def test_get_amount_of_rows():
    db = Database()
    language_settings = LanguageSettings()
    db.create_connection(":memory:")
    home_domain = HomeDomain(db, language_settings)
    assert home_domain.get_amount_of_rows() == 0
    db.close_connection()
