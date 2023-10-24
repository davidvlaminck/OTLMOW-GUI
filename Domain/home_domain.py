from datetime import datetime
from PyQt6.QtWidgets import QMessageBox


class HomeDomain:
    db = None
    HomeScreen = None

    def __init__(self, database, language_settings):
        self.db = database
        self.lang_settings = language_settings
        self._ = self.lang_settings.return_language()

    def get_amount_of_rows(self) -> int:
        return self.db.count_projects()

    def get_all_projects(self) -> list:
        return self.db.get_all_projects()

    # TODO: remove project opsplitsen in functie voor aanmaken scherm en functie voor verwijderen
    def remove_project(self, id_, table):
        dlg = QMessageBox()
        dlg.setWindowTitle(self._("delete"))
        dlg.setText(self._("project_deletion_question"))
        dlg.setIcon(QMessageBox.Icon.Warning)
        dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        button = dlg.exec()
        if button == QMessageBox.StandardButton.Yes:
            try:
                self.db.remove_project(id_)
                table.removeRow(table.currentRow())
            except Exception as e:
                print(e)

    def alter_table(self, properties, table, dlg, home_screen, id_=None):
        time_of_alter = datetime.now()
        properties += [time_of_alter]
        project_exists = id_ is not None
        if project_exists:
            self.db.draw_upsert_project(id_, properties[0], properties[1], properties[2], time_of_alter)
        else:
            id_ = self.db.add_project(properties[0], properties[1], properties[2], time_of_alter)
        home_screen.draw_table()
        dlg.close()
