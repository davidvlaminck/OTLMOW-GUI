import datetime
import sqlite3


class Database:
    cursor = None
    connection = None

    # Creates connection to database file, if file does not exist it will be created
    def create_connection(self, path: str):
        self.connection = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self.cursor = self.connection.cursor()
        self.create_project_table()

    # Creates project table where all the data of projects can be stored if it does not exist
    def create_project_table(self):
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS projects(Id INTEGER PRIMARY KEY AUTOINCREMENT, Eigen_referentie TEXT, Bestek TEXT, Subset TEXT, Laatst_bewerkt TIMESTAMP)''')

    # Adds a project to the project table taking the parameters as values
    def add_project(self, eigen_referentie: str, bestek: str, subset: str, laatst_bewerkt: datetime.datetime):
        if not isinstance(eigen_referentie, str) or not isinstance(bestek, str) or not isinstance(subset, str):
            raise TypeError("Invalid type")
        else:
            self.cursor.execute(
                '''INSERT INTO projects(Eigen_referentie, Bestek, Subset, Laatst_bewerkt) VALUES(?,?,?,?)''',
                (eigen_referentie, bestek, subset, laatst_bewerkt))

    # Returns all projects in the project table
    def get_all_projects(self) -> list:
        self.cursor.execute('''SELECT * FROM projects''')
        return self.cursor.fetchall()

    # Removes a project from the project table based on id
    def remove_project(self, id_: int):
        self.cursor.execute('''DELETE FROM projects WHERE Id = ?''', (id_,))

    # Get a certain project based on id
    def get_project(self, id_: int):
        self.cursor.execute('''SELECT * FROM projects WHERE Id = ?''', (id_,))
        return self.cursor.fetchone()

    def update_project(self, id_: int, eigen_referentie: str, bestek: str, subset: str, laatst_bewerkt) -> int:
        if not isinstance(eigen_referentie, str) or not isinstance(bestek, str) or not isinstance(subset, str):
            raise TypeError("Invalid Type")
        else:
            self.cursor.execute(
                '''UPDATE projects SET Eigen_referentie = ?, Bestek = ?, Subset = ?, Laatst_bewerkt = ? WHERE Id = ?''',
                (eigen_referentie, bestek, subset, laatst_bewerkt, id_))
            return self.cursor.rowcount

    # Returns amount of projects in database
    def count_projects(self) -> int:
        self.cursor.execute('''SELECT COUNT(*) FROM projects''')
        result = self.cursor.fetchone()
        return result[0]

    # Closes the connection to the database
    def close_connection(self):
        self.cursor.close()
        self.connection.close()
