import datetime
import logging
import sqlite3


class Database:
    cursor = None
    connection = None

    # Creates connection to database file, if file does not exist it will be created
    def create_connection(self, path: str) -> None:
        self.connection = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self.create_project_table()

    # Creates project table where all the data of projects can be stored if it does not exist
    def create_project_table(self) -> None:
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS projects(Id INTEGER PRIMARY KEY AUTOINCREMENT, Eigen_referentie TEXT, Bestek TEXT, Subset TEXT, Laatst_bewerkt TIMESTAMP)''')
        self.cursor.close()

    # Adds a project to the project table taking the parameters as values
    def add_project(self, eigen_referentie: str, bestek: str, subset: str, laatst_bewerkt: datetime.datetime) -> int:
        self.cursor = self.connection.cursor()
        if not isinstance(eigen_referentie, str) or not isinstance(bestek, str) or not isinstance(subset, str):
            raise TypeError("Invalid type")
        else:
            self.cursor.execute(
                '''INSERT INTO projects(Eigen_referentie, Bestek, Subset, Laatst_bewerkt) VALUES(?,?,?,?)''',
                (eigen_referentie, bestek, subset, laatst_bewerkt))
            id_ = self.cursor.lastrowid
            self.cursor.close()
            return id_

    # Returns all projects in the project table
    def get_all_projects(self) -> list:
        self.cursor = self.connection.cursor()
        self.cursor.execute('''SELECT * FROM projects''')
        projects = self.cursor.fetchall()
        self.cursor.close()
        return projects

    # Removes a project from the project table based on id
    def remove_project(self, id_: int) -> None:
        self.cursor = self.connection.cursor()
        self.cursor.execute('''DELETE FROM projects WHERE Id = ?''', (id_,))
        self.cursor.close()

    # Get a certain project based on id
    def get_project(self, id_: int):
        self.cursor = self.connection.cursor()
        self.cursor.execute('''SELECT * FROM projects WHERE Id = ?''', (id_,))
        project = self.cursor.fetchone()
        self.cursor.close()
        return project

    def update_project(self, id_: int, eigen_referentie: str, bestek: str, subset: str, laatst_bewerkt) -> int:
        self.cursor = self.connection.cursor()
        if not isinstance(eigen_referentie, str) or not isinstance(bestek, str) or not isinstance(subset, str):
            raise TypeError("Invalid Type")
        else:
            self.cursor.execute(
                '''UPDATE projects SET Eigen_referentie = ?, Bestek = ?, Subset = ?, Laatst_bewerkt = ? WHERE Id = ?''',
                (eigen_referentie, bestek, subset, laatst_bewerkt, id_))
        amount_of_rows = self.cursor.rowcount
        self.cursor.close()
        return amount_of_rows

    # Returns amount of projects in database
    def count_projects(self) -> int:
        self.cursor = self.connection.cursor()
        self.cursor.execute('''SELECT COUNT(*) FROM projects''')
        result = self.cursor.fetchone()
        self.cursor.close()
        return result[0]

    # Closes the connection to the database
    def close_connection(self) -> None:
        logging.debug("Closing connection")
        self.connection.close()
