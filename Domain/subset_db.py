import logging
import os
import sqlite3


class SubsetDatabase:

    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None

        self.create_connection(self.db_path)

    def create_connection(self, db_path):
        if os.path.exists(db_path):
            self.connection = sqlite3.connect(db_path)
        else:
            raise FileNotFoundError(f'{db_path} is not a valid path. File does not exist.')

    def get_general_info_project(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM GeneralInfo")
        info = cursor.fetchall()
        cursor.close()
        self.close_connection()
        return info

    def close_connection(self):
        logging.debug("Closing connection to subset database")
        self.connection.close()