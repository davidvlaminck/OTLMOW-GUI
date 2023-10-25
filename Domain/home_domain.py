from datetime import datetime
from PyQt6.QtWidgets import QMessageBox, QTableWidget, QWidget, QPushButton


class HomeDomain:

    def __init__(self, database, language_settings):
        self.db = database
        self._ = language_settings

    def get_amount_of_rows(self) -> int:
        return self.db.count_projects()

    def get_all_projects(self) -> list:
        return self.db.get_all_projects()

    def remove_project(self, id_: int, table: QTableWidget) -> None:
        self.db.remove_project(id_)
        table.removeRow(table.currentRow())

    def alter_table(self, properties: list, dlg, home_screen: QWidget, id_=None):
        time_of_alter = datetime.now()
        properties += [time_of_alter]
        project_exists = id_ is not None
        if project_exists:
            self.db.update_project(id_, properties[0], properties[1], properties[2], time_of_alter)
        else:
            id_ = self.db.add_project(properties[0], properties[1], properties[2], time_of_alter)
        home_screen.draw_table()
        dlg.close()

    def validate(self, input_eigen_ref, input_bestek):
        if input_eigen_ref.strip() == "":
            raise TypeError(self._('own_reference_empty_error'))
        elif input_bestek.strip() == "":
            raise TypeError(self._('bestek_empty_error'))
        else:
            return True
