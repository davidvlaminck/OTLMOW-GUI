
class HomeDomain:
    db = None

    def __init__(self, database):
        self.db = database

    def get_amount_of_rows(self) -> int:
        rowcount = self.db.count_projects()
        return rowcount

    def get_all_projects(self) -> list:
        projects = self.db.get_all_projects()
        return projects

    def remove_project(self, id_, table):
        table.removeRow(table.currentRow())
        try:
            self.db.remove_project(id_)
        except Exception as e:
            print(e)