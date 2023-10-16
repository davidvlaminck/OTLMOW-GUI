import sys
from PyQt6.QtWidgets import QApplication
from GUI.home_screen import HomeScreen
from Domain.database import Database


def test_init_home_screen():
    # launch an instance of HomeScreen and assert that it is not None
    app = QApplication(sys.argv)
    db = Database()
    db.create_connection(":memory:")
    window = HomeScreen(db)
    assert window is not None
    window.close()
    db.close_connection()
    app.quit()

# if needed, alternative solution (2nd!):
# https://stackoverflow.com/questions/70267550/testing-pyqt-application-with-pytest