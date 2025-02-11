import logging
from pathlib import Path
import qtawesome as qta
from PyQt6.QtCore import QSize

from PyQt6.QtWidgets import QVBoxLayout, QFrame, QHBoxLayout, QLabel, QPushButton, QWidget, QTableWidget, \
    QHeaderView, QTreeWidget, QFileDialog, QTreeWidgetItem, QTableView

from Domain import global_vars
from Domain.logger.OTLLogger import OTLLogger
from Domain.step_domain.AssetChangeDomain import AssetChangeDomain
from GUI.screens.general_elements.ButtonWidget import ButtonWidget
from GUI.dialog_windows.ChooseFileNameWindow import ChooseFileNameWindow
from GUI.screens.Screen import Screen
from GUI.screens.AssetDataChange_elements.TableModel import TableModel


class AssetDataChangeScreen(Screen):
    def __init__(self, language_settings=None):
        super().__init__()
        self._ = language_settings
        self.container_insert_data_screen = QVBoxLayout()
        self.main_window = None
        self.original_file_label = QLabel()
        self.new_file_label = QLabel()
        self.control_button = ButtonWidget()
        self.refresh_button = QPushButton()
        self.export_button = ButtonWidget()
        self.input_file_field = QTreeWidget()
        self.input_file_button = QPushButton()
        self.table = QTableView()
        self.message_icon = QLabel()
        self.message = QLabel()
        self.feedback_message_box = QFrame()
        self.model = None
        self.init_ui()

    def init_ui(self):
        self.container_insert_data_screen.addSpacing(10)
        self.container_insert_data_screen.addWidget(self.create_menu())
        self.container_insert_data_screen.addStretch()
        self.container_insert_data_screen.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.container_insert_data_screen)

    def create_menu(self):
        window = QWidget()
        window.setProperty('class', 'background-box')
        window_layout = QVBoxLayout()
        window_layout.addWidget(self.upper_side())
        window_layout.addWidget(self.lower_side())
        # window_layout.addWidget(QLabel("Under Construction"))
        window.setLayout(window_layout)
        return window

    def upper_side(self):
        frame = QFrame()
        frame_layout = QVBoxLayout()
        frame_layout.addWidget(self.input_original_file_field())
        frame_layout.addWidget(self.button_group())
        frame_layout.addStretch()
        frame.setLayout(frame_layout)
        return frame

    def lower_side(self):
        frame = QFrame()
        frame_layout = QVBoxLayout()
        self.change_table()
        frame_layout.addWidget(self.table)
        self.construct_feedback_message()
        frame_layout.addWidget(self.feedback_message_box)
        frame.setLayout(frame_layout)
        return frame



    def button_group(self):
        frame = QFrame()
        frame_layout = QHBoxLayout()
        self.input_file_button.setText(self._('choose_file'))
        self.input_file_button.setProperty('class', 'primary-button')
        self.input_file_button.clicked.connect(lambda: self.open_file_picker())
        self.control_button.setText(self._('show differences'))
        self.control_button.setProperty('class', 'primary-button')
        self.control_button.setDisabled(True)
        self.control_button.clicked.connect(lambda: self.navigate_to_diff_report(self.table))

        self.export_button.setText(self._('apply differences'))
        self.export_button.setDisabled(True)
        self.export_button.setProperty('class', 'primary-button')
        self.export_button.clicked.connect(lambda: self.replace_file_with_diff_report())

        self.refresh_button.setText(self._('empty fields'))
        self.refresh_button.setProperty('class', 'secondary-button')
        self.refresh_button.clicked.connect(lambda: self.clear_user_fields())
        frame_layout.addWidget(self.input_file_button)
        frame_layout.addStretch()
        frame_layout.addWidget(self.control_button)
        frame_layout.addWidget(self.export_button)
        frame_layout.addWidget(self.refresh_button)

        frame.setLayout(frame_layout)
        return frame



    def reset_ui(self, _):
        self._ = _
        self.clear_user_fields()
        self.original_file_label.setText(self._('original_file_load'))
        self.new_file_label.setText(self._('new_file_load'))
        self.control_button.setText(self._('show differences'))
        self.export_button.setText(self._('apply differences'))
        self.input_file_button.setText(self._('choose_file'))
        self.refresh_button.setText(self._('empty fields'))

    def open_file_picker(self):
        file_path = str(Path.home())
        file_picker = QFileDialog()
        file_picker.setWindowTitle(self._('choose_file'))
        file_picker.setDirectory(file_path)
        file_picker.setFileMode(QFileDialog.FileMode.ExistingFiles)
        filters = ""
        for i, item in enumerate(global_vars.supported_file_formats.items()):
            keys = item[0]
            value = item[1]

            filters += f"{keys} files (*.{value})"
            if i < len(global_vars.supported_file_formats) - 1:
                filters += ";;"  # the last value cannot have ;; behind it
        file_picker.setNameFilter(filters)

        if file_picker.exec():
            OTLLogger.logger.debug("file picker executed")
            self.add_file_to_list(file_picker.selectedFiles())

    def add_file_to_list(self, files):
        self.control_button.setDisabled(False)
        files_str = str(files)
        OTLLogger.logger.debug(f"adding file to list {files_str}")
        for file in files:
            list_item = QTreeWidgetItem()
            doc_name = Path(file).name
            list_item.setText(0, doc_name)
            list_item.setData(0, 1, file)
            self.input_file_field.addTopLevelItem(list_item)
            button = ButtonWidget()
            button.clicked.connect(lambda: self.delete_file_from_list())
            button.setIcon(qta.icon('mdi.close'))
            self.input_file_field.setItemWidget(list_item, 1, button)

    def delete_file_from_list(self):
        items = self.input_file_field.selectedItems()
        self.input_file_field.removeItemWidget(items[0], 1)
        self.input_file_field.takeTopLevelItem(self.input_file_field.indexOfTopLevelItem(items[0]))
        if self.input_file_field.topLevelItemCount() == 0:
            self.control_button.setDisabled(True)



    def fill_up_change_table(self, report, table):
        data = [
            [
                str(rep.id),
                str(rep.actie.value),
                str(rep.attribute),
                str(rep.original_value),
                str(rep.new_value),
            ]
            for rep in report
        ]
        self.model = TableModel(data, self._)
        table.setModel(self.model)

    def replace_file_with_diff_report(self):
        original_documents = [self.input_file_field.topLevelItem(i).data(0, 1) for i in
                              range(self.input_file_field.topLevelItemCount())]
        OTLLogger.logger.debug(f"original documents {original_documents}")
        project = global_vars.current_project
        dialog_window = ChooseFileNameWindow(self._, project, original_documents)
        try:
            dialog_window.warning_overwrite_screen()
            self.main_window.widget(2).tab1.load_saved_documents_in_project()
            self.positive_feedback_message()
        except Exception as e:
            OTLLogger.logger.debug(e)
            self.negative_feedback_message()


