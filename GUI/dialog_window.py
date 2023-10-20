from Domain.language_settings import LanguageSettings
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QDialogButtonBox, QLabel, QHBoxLayout, QPushButton
from Domain.home_domain import HomeDomain

lang_settings = LanguageSettings()
_ = lang_settings.return_language()


class DialogWindow:
    home_domain = None
    error_label = None


    def __init__(self, database):
        self.home_domain = HomeDomain(database)
        self.error_label = QLabel()

    def update_project(self, home_screen, id_=None, table=None):
        is_project = id_ is not None
        # Resets the error label to empty when reopening the dialog
        self.error_label.setText("")
        dialog_window = QDialog()
        # Makes the dialog the primary screen, disabling the screen behind it
        dialog_window.setModal(True)
        if is_project:
            project = home_screen.home_func.db.get_project(id_)
            dialog_window.setWindowTitle(_("alter_project_title"))
        else:
            dialog_window.setWindowTitle(_("new_project_title"))
        # Creates the vertical stack layout
        layout = QVBoxLayout()
        # Creates 3 horizontal layouts for each input field with its label
        container_eigen_ref = QHBoxLayout()
        container_bestek = QHBoxLayout()
        container_subset = QHBoxLayout()
        # Creates labels for the input fields and adds them to the horizontal layouts
        label_eigen_ref = QLabel(_("own_reference") + ":")
        container_eigen_ref.addWidget(label_eigen_ref, alignment=Qt.AlignmentFlag.AlignLeft)
        label_bestek = QLabel(_("service_order") + ":")
        container_bestek.addWidget(label_bestek, alignment=Qt.AlignmentFlag.AlignLeft)
        label_subset = QLabel(_("subset") + ":")
        container_subset.addWidget(label_subset, alignment=Qt.AlignmentFlag.AlignLeft)
        # Creates the input fields
        input_eigen_ref = QLineEdit()
        container_eigen_ref.addWidget(input_eigen_ref)
        input_bestek = QLineEdit()
        container_bestek.addWidget(input_bestek)
        input_subset = QLineEdit()
        container_subset.addWidget(input_subset)
        input_eigen_ref.setPlaceholderText(_("own_reference"))
        input_bestek.setPlaceholderText(_("service_order"))
        input_subset.setPlaceholderText(_("subset"))
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
        home_screen.reset_ui()

    def validate(self, input_eigen_ref: str, input_bestek: str, input_subset: str, table, dialog_window, home_screen,
                 id_: int = None):
        is_project = id_ is not None
        if input_eigen_ref.strip() == "" or input_subset.strip() == "":
            self.error_label.setText(_("empty_fields_error"))
            return
        self.error_label.setText("")
        properties = [input_eigen_ref, input_bestek, input_subset]
        self.home_domain.alter_table(properties, table, dialog_window, home_screen, id_)

    def language_window(self, home_screen):
        dialog = QDialog()
        dialog.setModal(True)
        dialog.setWindowTitle(_("change_language_title"))
        layout = QHBoxLayout()
        button_ned = QPushButton(_("language_option_dutch"))
        button_eng = QPushButton(_("language_option_english"))
        button_ned.clicked.connect(lambda: self.change_language("nl_BE", dialog, home_screen))
        button_eng.clicked.connect(lambda: self.change_language("en", dialog, home_screen))
        layout.addWidget(button_ned)
        layout.addWidget(button_eng)
        dialog.setLayout(layout)
        dialog.show()
        dialog.exec()

    def change_language(self, lang : str, dialog, home_screen):
        try:
            lang_settings.setLanguage(lang)
            home_screen.reset_ui()
            dialog.close()
        except Exception as e:
            print(e)
