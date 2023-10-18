from datetime import datetime

from PyQt6.QtWidgets import QDialogButtonBox, QVBoxLayout, QMessageBox, QDialog, QLineEdit, QTableWidgetItem


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

    def update_project(self, id_, eigen_ref: str, bestek: str, subset: str, table, dlg):
        changed_on = datetime.now()
        try:
            # Updates the project in the database
            self.db.update_project(id_, eigen_ref, bestek, subset, changed_on)
            # Updates the items in the table with the new data
            table.setItem(table.currentRow(), 0, QTableWidgetItem(eigen_ref))
            table.setItem(table.currentRow(), 1, QTableWidgetItem(bestek))
            table.setItem(table.currentRow(), 2, QTableWidgetItem(subset))
            table.setItem(table.currentRow(), 3, QTableWidgetItem(changed_on.strftime("%d-%m-%Y")))
            # Closes the dialog window
            dlg.close()
        except Exception as e:
            print(e)

    def add_project(self, eigen_ref: str, bestek: str, subset: str, table, dlg, home_screen):
        added_on = datetime.now()

        id_ = self.db.add_project(eigen_ref, bestek, subset, added_on)
        home_screen.projects = self.db.get_all_projects()
        table.insertRow(table.rowCount())
        table.setItem(table.rowCount() - 1, 0, QTableWidgetItem(eigen_ref))
        table.setItem(table.rowCount() - 1, 1, QTableWidgetItem(bestek))
        table.setItem(table.rowCount() - 1, 2, QTableWidgetItem(subset))
        table.setItem(table.rowCount() - 1, 3, QTableWidgetItem(added_on.strftime("%d-%m-%Y")))
        home_screen.add_update_and_delete_button(count= table.rowCount() - 1, id_=id_, table=table)
        dlg.close()



