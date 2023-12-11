import logging
from pathlib import Path
import qtawesome as qta
from PyQt6.QtCore import QSize

from PyQt6.QtWidgets import QVBoxLayout, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QWidget, QTableWidget, \
    QHeaderView, QTreeWidget, QFileDialog, QTreeWidgetItem, QTableWidgetItem, QTableView

from Domain import global_vars
from Domain.asset_change_domain import AssetChangeDomain
from GUI.ButtonWidget import ButtonWidget
from GUI.DialogWindows.choose_file_name_window import ChooseFileNameWindow
from GUI.Screens.screen import Screen
from GUI.TableModel import TableModel


class AssetDataChangeScreen(Screen):
    def __init__(self, language_settings=None):
        super().__init__()
        self._ = language_settings
        self.container_insert_data_screen = QVBoxLayout()
        self.stacked_widget = None
        self.original_file_label = QLabel()
        self.new_file_label = QLabel()
        self.control_button = ButtonWidget()
        self.export_button = ButtonWidget()
        self.input_file_field = QTreeWidget()
        self.table = QTableView()
        self.message_icon = QLabel()
        self.message = QLabel()
        self.feedback_message_box = QFrame()
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

    def input_original_file_field(self):
        input_file = QFrame()
        input_file_layout = QHBoxLayout()
        self.original_file_label.setText(self._('original_file_load'))

        self.input_file_field.setHeaderHidden(True)
        self.input_file_field.setColumnCount(2)
        self.input_file_field.header().setStretchLastSection(False)
        self.input_file_field.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        input_file_button = QPushButton()
        input_file_button.setIcon(qta.icon('mdi.folder-open-outline'))
        input_file_button.clicked.connect(lambda: self.open_file_picker())
        input_file_layout.addWidget(self.original_file_label)
        input_file_layout.addWidget(self.input_file_field)
        input_file_layout.addWidget(input_file_button)
        input_file.setLayout(input_file_layout)
        return input_file

    def button_group(self):
        frame = QFrame()
        frame_layout = QHBoxLayout()
        self.control_button.setText(self._('show differences'))
        self.control_button.setProperty('class', 'primary-button')
        self.control_button.setDisabled(True)
        self.control_button.clicked.connect(lambda: self.navigate_to_diff_report(self.table))

        self.export_button.setText(self._('apply differences'))
        self.export_button.setDisabled(True)
        self.export_button.setProperty('class', 'primary-button')
        self.export_button.clicked.connect(lambda: self.replace_file_with_diff_report(self.table))

        refresh_button = QPushButton()
        refresh_button.setText(self._('empty fields'))
        refresh_button.setProperty('class', 'secondary-button')
        refresh_button.clicked.connect(lambda: self.clear_input_field())

        frame_layout.addWidget(self.control_button)
        frame_layout.addWidget(self.export_button)
        frame_layout.addWidget(refresh_button)
        frame_layout.addStretch()

        frame.setLayout(frame_layout)
        return frame

    def change_table(self):
        self.table.setEnabled(True)
        self.table.verticalHeader().setHidden(True)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def reset_ui(self, _):
        self._ = _
        self.original_file_label.setText(self._('original_file_load'))
        self.new_file_label.setText(self._('new_file_load'))
        self.control_button.setText(self._('show differences'))
        self.export_button.setText(self._('apply differences'))

    def open_file_picker(self):
        file_path = str(Path.home())
        file_picker = QFileDialog()
        file_picker.setWindowTitle(self._('choose_file'))
        file_picker.setDirectory(file_path)
        file_picker.setFileMode(QFileDialog.FileMode.ExistingFiles)
        if file_picker.exec():
            logging.debug("file picker executed")
            self.add_file_to_list(file_picker.selectedFiles())

    def add_file_to_list(self, files):
        self.control_button.setDisabled(False)
        logging.debug("adding file to list" + str(files))
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

    def clear_input_field(self):
        self.input_file_field.clear()
        self.control_button.setDisabled(True)
        self.export_button.setDisabled(True)

    def navigate_to_diff_report(self, table):
        original_documents = [self.input_file_field.topLevelItem(i).data(0, 1) for i in
                              range(self.input_file_field.topLevelItemCount())]
        report = AssetChangeDomain().get_diff_report(original_documents=original_documents)
        self.fill_up_change_table(report, table)
        self.export_button.setDisabled(False)

    def fill_up_change_table(self, report, table):
        data = []
        for rep in report:
            data.append([str(rep.id), str(rep.actie.value), str(rep.attribute), str(rep.original_value), str(rep.new_value)])
        model = TableModel(data, self._)
        table.setModel(model)

    def replace_file_with_diff_report(self, table):
        original_documents = [self.input_file_field.topLevelItem(i).data(0, 1) for i in
                              range(self.input_file_field.topLevelItemCount())]
        logging.debug("original documents" + str(original_documents))
        project = global_vars.single_project
        dialog_window = ChooseFileNameWindow(self._, project, original_documents)
        try:
            dialog_window.warning_overwrite_screen()
            self.positive_feedback_message()
        except Exception as e:
            logging.debug(e)
            self.negative_feedback_message()

    def construct_feedback_message(self):
        logging.debug("constructing feedback message")
        frame_layout = QHBoxLayout()
        frame_layout.addWidget(self.message_icon)
        self.message.setProperty('class', 'feedback-message')
        frame_layout.addWidget(self.message)
        frame_layout.addStretch()
        self.feedback_message_box.setLayout(frame_layout)

    def positive_feedback_message(self):
        self.message_icon.setPixmap(qta.icon('mdi.check', color="white").pixmap(QSize(48, 48)))
        self.message.setText(self._('the changes were correctly written to a new file'))
        self.feedback_message_box.setStyleSheet('background-color: #1DCA94; border-radius: 10px;')

    def clear_feedback_message(self):
        self.message.setText('')
        self.feedback_message_box.setStyleSheet('')

    def negative_feedback_message(self):
        self.message_icon.setPixmap(qta.icon('mdi.alert-circle-outline', color="white").pixmap(QSize(48, 48)))
        self.message.setText(self._('error'))
        self.feedback_message_box.setStyleSheet('background-color: #CC3300; border-radius: 10px;')
