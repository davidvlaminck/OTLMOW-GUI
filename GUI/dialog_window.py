from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QDialogButtonBox, QLabel, QHBoxLayout, QPushButton
from Domain.home_domain import HomeDomain
from Domain.language_settings import return_language


class DialogWindow:

    def __init__(self, database, language_settings):
        self.home_domain = HomeDomain(database, language_settings)
        self.error_label = QLabel()
        self._ = language_settings

    def draw_upsert_project(self, home_screen, id_=None):
        is_project = id_ is not None
        # Resets the error label to empty when reopening the dialog
        self.error_label.setText("")
        dialog_window = QDialog()
        # Makes the dialog the primary screen, disabling the screen behind it
        dialog_window.setModal(True)
        if is_project:
            project = home_screen.home_domain.db.get_project(id_)
            dialog_window.setWindowTitle(self._("alter_project_title"))
        else:
            dialog_window.setWindowTitle(self._("new_project_title"))
        # Creates the vertical stack layout
        layout = QVBoxLayout()
        # Creates 3 horizontal layouts for each input field with its label
        container_eigen_ref = QHBoxLayout()
        container_bestek = QHBoxLayout()
        container_subset = QHBoxLayout()
        # Creates labels for the input fields and adds them to the horizontal layouts
        label_eigen_ref = QLabel(self._("own_reference") + ":")
        container_eigen_ref.addWidget(label_eigen_ref, alignment=Qt.AlignmentFlag.AlignLeft)
        label_bestek = QLabel(self._("service_order") + ":")
        container_bestek.addWidget(label_bestek, alignment=Qt.AlignmentFlag.AlignLeft)
        label_subset = QLabel(self._("subset") + ":")
        container_subset.addWidget(label_subset, alignment=Qt.AlignmentFlag.AlignLeft)
        # Creates the input fields
        input_eigen_ref = QLineEdit()
        container_eigen_ref.addWidget(input_eigen_ref)
        input_bestek = QLineEdit()
        container_bestek.addWidget(input_bestek)
        input_subset = QLineEdit()
        container_subset.addWidget(input_subset)
        input_eigen_ref.setPlaceholderText(self._("own_reference"))
        input_bestek.setPlaceholderText(self._("service_order"))
        input_subset.setPlaceholderText(self._("subset"))
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
                                  input_subset.text(), dialog_window, home_screen, id_))
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

    def validate(self, input_eigen_ref: str, input_bestek: str, input_subset: str, dialog_window, home_screen,
                 id_: int = None) -> None:
        if input_eigen_ref.strip() == "" or input_subset.strip() == "":
            self.error_label.setText(self._("empty_fields_error"))
            return
        self.error_label.setText("")
        properties = [input_eigen_ref, input_bestek, input_subset]
        self.home_domain.alter_table(properties, dialog_window, home_screen, id_)

    def language_window(self, home_screen) -> None:
        dialog = QDialog()
        dialog.setModal(True)
        dialog.setWindowTitle(self._("change_language_title"))
        layout = QHBoxLayout()
        button_ned = QPushButton(self._("language_option_dutch"))
        button_eng = QPushButton(self._("language_option_english"))
        button_ned.clicked.connect(lambda: self.change_language("nl_BE", dialog, home_screen))
        button_eng.clicked.connect(lambda: self.change_language("en", dialog, home_screen))
        layout.addWidget(button_ned)
        layout.addWidget(button_eng)
        dialog.setLayout(layout)
        dialog.show()
        dialog.exec()

    def change_language(self, lang: str, dialog: QDialog, home_screen) -> None:
        self._ = return_language('../locale/', lang)
        home_screen.reset_ui(self._)
        dialog.close()
