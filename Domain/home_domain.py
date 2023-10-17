from PyQt6.QtWidgets import QDialogButtonBox, QVBoxLayout, QMessageBox, QDialog, QLineEdit


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
        dlg = QMessageBox()
        dlg.setWindowTitle("Verwijderen")
        dlg.setText("Weet u zeker dat u dit project wilt verwijderen?")
        dlg.setIcon(QMessageBox.Icon.Warning)
        dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        button = dlg.exec()
        if button == QMessageBox.StandardButton.Yes:
            try:
                self.db.remove_project(id_)
                table.removeRow(table.currentRow())
            except Exception as e:
                print(e)

    def update_project(self, id_, table, eigen_ref, bestek, subset):
        try:
            self.db.update_project(id_, eigen_ref, bestek, subset, None)
            table.setItem(table.currentRow(), 1, eigen_ref)
            table.setItem(table.currentRow(), 2, bestek)
            table.setItem(table.currentRow(), 3, subset)
        except Exception as e:
            print(e)
