from PyQt6.QtWidgets import QDialogButtonBox, QVBoxLayout, QMessageBox


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
        try:
            dlg = QMessageBox()
            dlg.setWindowTitle("Verwijderen")
            dlg.setText("Weet u zeker dat u dit project wilt verwijderen?")
            dlg.setIcon(QMessageBox.Icon.Warning)
            dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            button = dlg.exec()
        except Exception as e:
            print(e)
        if button == QMessageBox.StandardButton.Yes:
            try:
                self.db.remove_project(id_)
                table.removeRow(table.currentRow())
            except Exception as e:
                print(e)
        else:
            dlg.close()

