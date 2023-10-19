from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QDialogButtonBox, QLabel, QHBoxLayout
from Domain.home_domain import HomeDomain


class DialogWindow:
    home_domain = None
    error_label = None

    def __init__(self, database):
        self.home_domain = HomeDomain(database)
        self.error_label = QLabel()

    def update_project(self, home_screen, id_=None, table=None):
        is_project = id_ is not None
        # TODO: velden trimmen
        # Resets the error label to empty when reopening the dialog
        self.error_label.setText("")
        dialog_window = QDialog()
        # Makes the dialog the primary screen, disabling the screen behind it
        dialog_window.setModal(True)
        if is_project:
            project = home_screen.home_func.db.get_project(id_)
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
        container_eigen_ref.addWidget(label_eigen_ref, alignment=Qt.AlignmentFlag.AlignLeft)
        label_bestek = QLabel("Bestek:")
        container_bestek.addWidget(label_bestek, alignment=Qt.AlignmentFlag.AlignLeft)
        label_subset = QLabel("Subset:")
        container_subset.addWidget(label_subset, alignment=Qt.AlignmentFlag.AlignLeft)
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
        if is_project:
            input_eigen_ref.setText(project[1])
            input_subset.setText(project[2])
            input_bestek.setText(project[3])
        # Adds the input fields to the layout
        layout.addLayout(container_eigen_ref)
        layout.addLayout(container_bestek)
        layout.addLayout(container_subset)

        # Changes the color of the error label to red
        self.error_label.setStyleSheet("color: red")

        # Creates the button box
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.setProperty("class", "button-box")
        # sends the values off to validate once submitted
        button_box.accepted.connect(
            lambda: self.validate(input_eigen_ref.text(), input_bestek.text(),
                                  input_subset.text(), table, dialog_window, home_screen, id_))
        button_box.rejected.connect(dialog_window.reject)
        # Adds the two buttons to the layout
        layout.addWidget(button_box)
        button_box.button(QDialogButtonBox.StandardButton.Ok).setProperty("class", "primary-button")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setProperty("class", "secondary-button")
        layout.addWidget(self.error_label)
        # Fills the dialog with the created layout
        dialog_window.setLayout(layout)
        # Shows the dialog
        dialog_window.show()
        dialog_window.exec()
        # Updates the projects behind the table
        home_screen.projects = self.home_domain.get_all_projects()

    def validate(self, input_eigen_ref: str, input_bestek: str, input_subset: str, table, dialog_window, home_screen, id_: int = None):
        is_project = id_ is not None
        if input_eigen_ref.strip() == "" or input_subset.strip() == "":
            self.error_label.setText("Vul alle velden in")
            return
        self.error_label.setText("")
        properties = [input_eigen_ref, input_bestek, input_subset]
        self.home_domain.alter_table(properties, table, dialog_window, home_screen, id_)
