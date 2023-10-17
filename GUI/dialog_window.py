from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QDialogButtonBox
from Domain.home_domain import HomeDomain


class DialogWindow:
    home_domain = None

    def __init__(self, database):
        self.home_domain = HomeDomain(database)

    def update_project(self, id_, eigen_ref: str = None, bestek: str = None, subset: str = None, table=None):
        dlg = QDialog()
        if eigen_ref is None:
            dlg.setWindowTitle("Project bewerken")
        else:
            dlg.setWindowTitle("Nieuw project")
        layout = QVBoxLayout()
        input_eigen_ref = QLineEdit()
        input_bestek = QLineEdit()
        input_subset = QLineEdit()
        input_eigen_ref.setPlaceholderText("Eigen referentie")
        input_subset.setPlaceholderText("Bestek")
        input_bestek.setPlaceholderText("Subset")
        if table is not None:
            input_eigen_ref.setText(eigen_ref)
            input_subset.setText(bestek)
            input_bestek.setText(subset)
        layout.addWidget(input_eigen_ref)
        layout.addWidget(input_bestek)
        layout.addWidget(input_subset)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(
            lambda: self.home_domain.update_project(id_, input_eigen_ref.text(), input_bestek.text(),
                                               input_subset.text(), table))
        layout.addWidget(button_box)
        dlg.setLayout(layout)
        dlg.show()
        dlg.exec()
