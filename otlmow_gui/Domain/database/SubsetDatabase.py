import sqlite3
from pathlib import Path
from sqlite3 import Connection

from otlmow_gui.Domain.logger.OTLLogger import OTLLogger
from otlmow_gui.Exceptions.NotASqlliteFileError import NotASqlliteFileError


class SubsetDatabase:

    def __init__(self, db_path: Path):
        self.db_path: Path = db_path
        self.connection: Connection
        self.create_connection(self.db_path)

    def create_connection(self, db_path: Path) -> None:
        if db_path.exists():
            try:
                self.connection = sqlite3.connect(db_path)
            except sqlite3.OperationalError as e:
                OTLLogger.logger.error(e)
                raise NotASqlliteFileError(e)
        else:
            raise FileNotFoundError(f'{db_path} is not a valid path. File does not exist.')

    def get_general_info_project(self) -> list:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM GeneralInfo")
        info = cursor.fetchall()
        cursor.close()
        return info

    def is_valid_subset_database(self) -> bool:
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM OSLOClass")
            cursor.fetchall()
            cursor.close()
            return True
        except sqlite3.OperationalError:
            return False

    def close_connection(self) -> None:
        OTLLogger.logger.debug("Closing connection to subset database")
        self.connection.close()
