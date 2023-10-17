from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QDialogButtonBox, QLabel, QHBoxLayout
from Domain.home_domain import HomeDomain


class DialogWindow:
    home_domain = None
    error_label = None

    def __init__(self, database):
        self.home_domain = HomeDomain(database)
        self.error_label = QLabel()

    def update_project(self, id_, eigen_ref: str = None, bestek: str = None, subset: str = None, table=None,
                       home_screen=None):
        # Resets the error label to empty when reopening the dialog
        self.error_label.setText("")
        dialog_window = QDialog()
        # Makes the dialog the primary screen, disabling the screen behind it
        dialog_window.setModal(True)
        if eigen_ref is None:
            dialog_window.setWindowTitle("Project bewerken")
        else:
            dialog_window.setWindowTitle("Nieuw project")
        # Creates the vertical stack layout
        layout = QVBoxLayout()
        # Creates 3 horizontal layouts for each input field with its label
        container_eigen_ref = QHBoxLayout()
        container_bestek = QHBoxLayout()
        container_subset = QHBoxLayout()
        # Creates labels for the input fields and adds them to the horizontal layouts
        label_eigen_ref = QLabel("Eigen referentie:")
        container_eigen_ref.addWidget(label_eigen_ref, alignment= Qt.AlignmentFlag.AlignLeft)
        label_bestek = QLabel("Bestek:")
        container_bestek.addWidget(label_bestek, alignment= Qt.AlignmentFlag.AlignLeft)
        label_subset = QLabel("Subset:")
        container_subset.addWidget(label_subset, alignment= Qt.AlignmentFlag.AlignLeft)
        # Adds the labels to the layout
        # Creates the input fields
        input_eigen_ref = QLineEdit()
        container_eigen_ref.addWidget(input_eigen_ref)
        input_bestek = QLineEdit()
        container_bestek.addWidget(input_bestek)
        input_subset = QLineEdit()
        container_subset.addWidget(input_subset)
        input_eigen_ref.setPlaceholderText("Eigen referentie:")
        input_bestek.setPlaceholderText("Bestek")
        input_subset.setPlaceholderText("Subset")
        if table is not None:
            input_eigen_ref.setText(eigen_ref)
            input_subset.setText(subset)
            input_bestek.setText(bestek)
        # Adds the input fields to the layout
        layout.addLayout(container_eigen_ref)
        layout.addLayout(container_bestek)
        layout.addLayout(container_subset)

        #Changes the color of the error label to red
        self.error_label.setStyleSheet("color: red")


        # Creates the button box
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        # sends the values off to validate once submitted
        button_box.accepted.connect(
            lambda: self.validate(id_, input_eigen_ref.text(), input_bestek.text(),
                                  input_subset.text(), table, dialog_window))
        button_box.rejected.connect(dialog_window.reject)
        # Adds the two buttons to the layout
        layout.addWidget(button_box)
        layout.addWidget(self.error_label)
        # Fills the dialog with the created layout
        dialog_window.setLayout(layout)
        # Shows the dialog
        dialog_window.show()
        dialog_window.exec()
        # Updates the projects behind the table
        home_screen.projects = self.home_domain.get_all_projects()

    def validate(self, id_: int, input_eigen_ref: str, input_bestek: str, input_subset: str, table, dialog_window):

        if input_eigen_ref == "" or input_subset == "" or input_subset.isspace() or input_eigen_ref.isspace():
            self.error_label.setText("Vul alle velden in")
            return
        self.error_label.setText("")
        self.home_domain.update_project(id_, input_eigen_ref, input_bestek,
                                        input_subset, table, dialog_window)
