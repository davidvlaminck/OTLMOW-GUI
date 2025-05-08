from abc import abstractmethod

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QComboBox, QCheckBox, QRadioButton

from otlmow_gui.Domain.logger.OTLLogger import OTLLogger


class Screen(QWidget):

    # list containing all fields of a screen that need to be reset on calling reset_ui
    # these need to be added manually everytime a developer creates a new field of the following types:
    # QComboBox (dropdownlist)
    # QCheckBox (checkbox)
    resetable_fields_list = []



    def add_resetable_field(self,field ,default_value=None):



        if isinstance(field,QComboBox) and (not default_value or isinstance(default_value,int)):
            if not default_value:
                default_value = 0
        elif isinstance(field, QCheckBox) and (
                        not default_value or isinstance(default_value, bool)):
            if not default_value:
                default_value = False

        elif isinstance(field, QRadioButton) and (
                        not default_value or isinstance(default_value, bool)):
            if not default_value:
                default_value = False
        else:
            field_type= type(field)
            OTLLogger.logger.error(f"Cannot add field type {field_type} to Screen.resetable_fields_list")
            return

        self.resetable_fields_list.append([field, default_value])


    @abstractmethod
    def reset_ui(self, _):
        for field_and_default_value in self.resetable_fields_list:
            field =  field_and_default_value[0]
            default_value =  field_and_default_value[1]

            if isinstance(field, QComboBox) and field.count():
                field.setCurrentIndex(default_value)
            elif isinstance(field, QCheckBox):
                if field.checkState() == Qt.CheckState.Checked:
                    field.setChecked(False)

                if default_value:
                    field.setChecked(True)
            elif isinstance(field, QRadioButton):
                if field.isChecked():
                    field.setChecked(False)

                if default_value:
                    field.setChecked(True)

    def opened(self):
        pass