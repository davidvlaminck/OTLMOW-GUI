from Domain.language_settings import LanguageSettings
from datetime import datetime
from PyQt6.QtWidgets import QMessageBox

lang_settings = LanguageSettings()
_ = lang_settings.return_language()


class HomeDomain:
    db = None
    HomeScreen = None

    def __init__(self, database):
        self.db = database

    def get_amount_of_rows(self) -> int:
        rowcount = self.db.count_projects()
        return rowcount

    def get_all_projects(self) -> list:
        projects = self.db.get_all_projects()
        return projects

    def remove_project(self, id_, table):
        dlg = QMessageBox()
        dlg.setWindowTitle(_("delete"))
        dlg.setText(_("project_deletion_question"))
        dlg.setIcon(QMessageBox.Icon.Warning)
        dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        button = dlg.exec()
        if button == QMessageBox.StandardButton.Yes:
            try:
                self.db.remove_project(id_)
                table.removeRow(table.currentRow())
            except Exception as e:
                print(e)

    def alter_table(self, properties,table, dlg, home_screen, id_=None):
        time_of_alter = datetime.now()
        properties += [time_of_alter]
        project_exists = id_ is not None
        if project_exists:
            row = table.currentRow()
            self.db.update_project(id_, properties[0], properties[1], properties[2], time_of_alter)
        else:
            home_screen.projects = self.db.get_all_projects()
            table.insertRow(table.rowCount())
            row = table.rowCount() - 1
            id_ = self.db.add_project(properties[0], properties[1], properties[2], time_of_alter)
        #for count, element in enumerate(properties):
            # home_screen.add_cell_to_table(table, row, count, element)
        if not project_exists:
            home_screen.add_update_and_delete_button(count=row, id_=id_, table=table)
        dlg.close()



