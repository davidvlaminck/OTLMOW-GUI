from enum import Enum
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, \
    QDialogButtonBox, \
    QFileDialog, QFrame, QComboBox
from otlmow_model.OtlmowModel.Classes.Onderdeel.HeeftBetrokkene import HeeftBetrokkene
from otlmow_model.OtlmowModel.Datatypes.KlBetrokkenheidRol import KlBetrokkenheidRol

from Domain.Project import Project
from Domain.HomeDomain import HomeDomain

import qtawesome as qta

from Domain.RelationChangeDomain import RelationChangeDomain
from Exceptions.EmptyFieldError import EmptyFieldError
from Exceptions.WrongDatabaseError import WrongDatabaseError


class DefineHeeftBetrokkeneRelationWindow:
    options_to_data_dict = {}
    def __init__(self, language_settings, bron_asset_id, target_asset_id, relation_object: HeeftBetrokkene):
        self.home_domain = HomeDomain(language_settings)
        self.error_label = QLabel()
        self._ = language_settings

        self.input_asset_id_or_name: QLineEdit = QLineEdit()
        self.combobox_asset_type: QComboBox = QComboBox()

        self.relation_object: HeeftBetrokkene = relation_object
        self.bron_asset_id =  bron_asset_id
        self.target_asset_id = target_asset_id

    def draw_define_heeft_betrokkene_rol_window(self):

        self.error_label.setText("")
        dialog_window = QDialog()
        dialog_window.setMinimumWidth(450)
        # Makes the dialog the primary screen, disabling the screen behind it
        dialog_window.setModal(True)
        dialog_window.setWindowTitle(self._("needs_attribute"))
        # Creates the vertical stack layout
        layout = QVBoxLayout()

        # Creates 3 horizontal layouts for each input field with its label
        container_eigen_ref = QHBoxLayout()

        label_asset_id_or_name = QLabel( self._("define_attribute_to_add_heeft_betrokkene_relation").format(self.bron_asset_id,self.target_asset_id))
        container_eigen_ref.addWidget(label_asset_id_or_name)


        container_subset = QHBoxLayout()
        label_asset_type = QLabel(self._("asset_type") + ":")

        self.combobox_asset_type = self.create_combobox(KlBetrokkenheidRol.options)
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
        button_box.rejected.connect(lambda: self.reject_action(dialog_window))
        # Adds the two buttons to the layout
        layout.addWidget(button_box)
        layout.addWidget(self.error_label)
        # Fills the dialog with the created layout
        dialog_window.setLayout(layout)
        # Shows the dialog
        dialog_window.show()
        dialog_window.exec()

    def add_asset(self, dialog_window):

        combobox_choice = self.combobox_asset_type.currentText()

        optie = KlBetrokkenheidRol.options[combobox_choice]

        self.relation_object.rol = optie.invulwaarde

        RelationChangeDomain.add_relation_object_to_existing_relations(relation_object=self.relation_object)
        RelationChangeDomain.update_frontend()
        dialog_window.close()

    def reject_action(self, dialog_window):

        RelationChangeDomain.update_frontend()
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
        options = [key for key,option in options_to_data_dict.items() if option.status == "ingebruik" ]

        comboBox.addItems(options)
        # comboBox.currentTextChanged.connect(self.)

        return comboBox
