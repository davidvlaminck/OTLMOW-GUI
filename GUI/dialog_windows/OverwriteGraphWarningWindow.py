import asyncio

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox

from Domain import global_vars
from Domain.step_domain.InsertDataDomain import InsertDataDomain
from exception_handler.ExceptionHandlers import create_task_reraise_exception


class OverwriteGraphWarningWindow:

    def __init__(self, screen, language_settings):
        self.screen =screen
        self._ = language_settings
        self.init_ui()

    def init_ui(self):
        dialog = QDialog()
        dialog.setModal(True)
        dialog.setWindowTitle(self._("overwrite_graph_warning_title"))
        layout = QVBoxLayout()
        question_label = QLabel()
        question_label.setText(self._("overwrite_graph_warning_text"))
        layout.addWidget(question_label)
        button_box = self.create_button_box()
        button_box.accepted.connect(lambda:self.accept_action(dialog) )
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        dialog.setLayout(layout)
        dialog.show()
        dialog.exec()

    def accept_action(self,dialog:QDialog):
        visuals_screen = global_vars.otl_wizard.main_window.step3_visuals
        current_visuals_html_path = global_vars.current_project.get_current_visuals_html_path()
        visuals_screen.recreate_html(current_visuals_html_path)
        dialog.close()

    def create_button_box(self):
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.setProperty("class", "button-box")
        button_box.button(QDialogButtonBox.StandardButton.Ok).setProperty("class", "primary-button")
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText(self._('continue'))
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setProperty("class", "secondary-button")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(self._("cancel"))
        return button_box

    def validate_documents_again(self, dialog):
        missing_project_files = InsertDataDomain.check_current_project_project_files_existence()
        if len(missing_project_files):
            self.screen.show_missing_project_files_notification_window(missing_project_files)
        else:
            create_task_reraise_exception(self.screen.validate_documents())
        dialog.close()

