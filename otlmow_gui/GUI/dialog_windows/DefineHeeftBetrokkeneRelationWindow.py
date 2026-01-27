from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QDialogButtonBox, \
    QComboBox
from otlmow_model.OtlmowModel.Datatypes.KlBetrokkenheidRol import KlBetrokkenheidRol

from otlmow_gui.Domain.step_domain.RelationChangeDomain import RelationChangeDomain


class DefineHeeftBetrokkeneRelationWindow:
    options_to_data_dict = {}


    def __init__(self, language_settings,data_list_and_relation_objects):
        self.error_label = QLabel()
        self._ = language_settings

        self.input_asset_id_or_name: QLineEdit = QLineEdit()
        self.combobox_asset_type: QComboBox = QComboBox()

        self.data_list_and_relation_objects = data_list_and_relation_objects

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
        only_heeft_betrokkene_relation_objects =  [data for data in self.data_list_and_relation_objects
         if  data[2].typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#HeeftBetrokkene']

        if(len(only_heeft_betrokkene_relation_objects) == 1):
            label_asset_id_or_name = QLabel( self._("define_attribute_to_add_heeft_betrokkene_relation").format(only_heeft_betrokkene_relation_objects[0][2].doelAssetId.identificator,only_heeft_betrokkene_relation_objects[0][2].bronAssetId.identificator))
            container_eigen_ref.addWidget(label_asset_id_or_name)
        else:
            label_asset_id_or_name = QLabel(
                self._("define_attribute_to_add_heeft_betrokkene_relations").format(
                    only_heeft_betrokkene_relation_objects[0][2].doelAssetId.identificator))
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

        RelationChangeDomain.last_added_to_existing.clear()
        for data in self.data_list_and_relation_objects:
            relation_object = data[2]

            if relation_object.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#HeeftBetrokkene':
                relation_object.rol = optie.invulwaarde

            RelationChangeDomain.add_relation_object_to_existing_relations(relation_object)
            RelationChangeDomain.last_added_to_existing.append(relation_object)

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
