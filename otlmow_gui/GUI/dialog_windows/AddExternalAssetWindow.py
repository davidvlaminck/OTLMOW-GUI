from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QDialogButtonBox, \
    QComboBox

from otlmow_gui.Domain.util.Helpers import Helpers

from otlmow_gui.Domain.step_domain.RelationChangeDomain import RelationChangeDomain
from otlmow_gui.exception_handler.ExceptionHandlers import create_task_reraise_exception


class AddExternalAssetWindow:


    def __init__(self, language_settings):
        self.error_label = QLabel()
        self._ = language_settings

        self.input_asset_id_or_name: QLineEdit = QLineEdit()
        self.combobox_asset_type: QComboBox = QComboBox()



    def draw_add_external_asset_window(self):

        self.error_label.setText("")
        dialog_window = QDialog()
        dialog_window.setMinimumWidth(450)
        # Makes the dialog the primary screen, disabling the screen behind it
        dialog_window.setModal(True)
        dialog_window.setWindowTitle(self._("add_external_asset_title"))
        # Creates the vertical stack layout
        layout = QVBoxLayout()

        # Creates 3 horizontal layouts for each input field with its label
        container_eigen_ref = QHBoxLayout()
        label_asset_id_or_name = QLabel( self._("asset_id_or_name")+ ":")
        self.input_asset_id_or_name = QLineEdit()
        self.input_asset_id_or_name.setPlaceholderText(self._("asset_id_dummy"))
        container_eigen_ref.addWidget(label_asset_id_or_name, alignment=Qt.AlignmentFlag.AlignLeft)
        container_eigen_ref.addWidget(self.input_asset_id_or_name)

        container_subset = QHBoxLayout()
        label_asset_type = QLabel(self._("asset_type") + ":")

        self.combobox_asset_type = self.create_combobox(Helpers.all_OTL_asset_types_dict)
        self.combobox_asset_type.setPlaceholderText(self._("asset_type_dummy"))
        container_subset.addWidget(label_asset_type, alignment=Qt.AlignmentFlag.AlignLeft)
        container_subset.addWidget(self.combobox_asset_type)

        # Adds the input fields to the layout
        layout.addLayout(container_eigen_ref)
        layout.addLayout(container_subset)

        # Changes the color of the error label to red
        self.error_label.setStyleSheet("color: red")

        # Creates the button box
        button_box:QDialogButtonBox = self.create_button_box()
        # sends the values off to validate once submitted
        button_box.accepted.connect(lambda: self.add_asset(dialog_window))
        button_box.rejected.connect(dialog_window.reject)
        # Adds the two buttons to the layout
        layout.addWidget(button_box)
        layout.addWidget(self.error_label)
        # Fills the dialog with the created layout
        dialog_window.setLayout(layout)
        # Shows the dialog
        dialog_window.show()
        dialog_window.exec()

    def add_asset(self, dialog_window):
        id_or_name = self.input_asset_id_or_name.text().strip()
        if not id_or_name:
            error_text = self._("asset_id_or_name") + self._(" is leeg")
            self.error_label.setText(str(error_text))
            return

        if RelationChangeDomain.get_object(id_or_name):
            error_text = self._('OTL-asset with {0} "{1}" already exists'.format(self._("asset_id_or_name"),id_or_name ))
            self.error_label.setText(str(error_text))
            return

        combobox_choice = self.combobox_asset_type.currentText()

        type_uri = Helpers.all_OTL_asset_types_dict[combobox_choice]

        # Replaced by an async call
        # RelationChangeDomain.create_and_add_new_external_asset(id_or_name=id_or_name, type_uri=type_uri)
        # global_vars.current_project.visualisation_uptodate.set_clear_all(True)
        # RelationChangeDomain.update_frontend()

        #async version that also saves the assets after executing
        create_task_reraise_exception(RelationChangeDomain.user_input_to_create_and_add_new_external_asset(id_or_name=id_or_name, type_uri=type_uri))

        dialog_window.close()

    def create_button_box(self):
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.setProperty("class", "button-box")
        button_box.button(QDialogButtonBox.StandardButton.Ok).setProperty("class", "primary-button")
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText(self._("submit"))
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setProperty("class", "secondary-button")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(self._("cancel"))
        return button_box

    def create_combobox(self, options_to_data_dict):
        comboBox = QComboBox()
        comboBox.addItems(list(options_to_data_dict.keys()))
        # comboBox.currentTextChanged.connect(self.)

        comboBox.setEditable(True)
        comboBox.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        return comboBox
