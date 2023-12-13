import logging
from pathlib import Path
from typing import List

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QLabel, QPushButton, QFrame, QHBoxLayout, QListWidget, \
    QFileDialog, QListWidgetItem, QTreeWidget, QTreeWidgetItem, QHeaderView
from otlmow_converter.Exceptions.ExceptionsGroup import ExceptionsGroup
from otlmow_converter.Exceptions.FailedToImportFileError import FailedToImportFileError
from otlmow_converter.Exceptions.InvalidColumnNamesInExcelTabError import InvalidColumnNamesInExcelTabError
from otlmow_converter.Exceptions.NoTypeUriInExcelTabError import NoTypeUriInExcelTabError
from otlmow_converter.Exceptions.TypeUriNotInFirstRowError import TypeUriNotInFirstRowError
from otlmow_model.OtlmowModel.Helpers.OTLObjectHelper import count_assets_by_type

from Domain import global_vars
from Domain.ProjectFileManager import ProjectFileManager
from Domain.enums import FileState
from Domain.insert_data_domain import InsertDataDomain
from GUI.ButtonWidget import ButtonWidget
from GUI.DialogWindows.remove_project_files_window import RemoveProjectFilesWindow
from GUI.Screens.data_visualisation_screen import DataVisualisationScreen
from GUI.Screens.screen import Screen
import qtawesome as qta


class InsertDataScreen(Screen):
    def __init__(self, language_settings=None):
        super().__init__()
        self._ = language_settings
        self.container_insert_data_screen = QVBoxLayout()
        self.feedback_message_box = QFrame()
        self.stacked_widget = None
        self.message_icon = QLabel()
        self.message = QLabel()
        self.input_file_label = QLabel()
        self.control_button = ButtonWidget()
        self.input_file_field: QTreeWidget = QTreeWidget()
        self.asset_info = QListWidget()
        self.assets = []
        self.input_file_button = ButtonWidget()
        self.reset_button = ButtonWidget()

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
        window_layout = QHBoxLayout()
        left_side = self.left_side()
        right_side = self.right_side()
        window_layout.setContentsMargins(32, 0, 16, 0)
        window_layout.addWidget(left_side)
        window_layout.addWidget(right_side)
        window.setLayout(window_layout)
        return window

    def button_set(self):
        button_frame = QFrame()
        button_frame_layout = QHBoxLayout()
        self.control_button.setText(self._('control_button'))
        self.control_button.setDisabled(True)
        self.control_button.clicked.connect(lambda: self.validate_documents(self.input_file_field))
        self.control_button.setProperty('class', 'primary-button')

        reset_button = QPushButton()
        reset_button.setText(self._('reset_fields'))
        reset_button.setProperty('class', 'secondary-button')
        reset_button.clicked.connect(lambda: self.reset_button_functionality())

        self.input_file_button.setText(self._('choose_file'))
        self.input_file_button.setProperty('class', 'primary-button')
        self.input_file_button.clicked.connect(lambda: self.open_file_picker())

        button_frame_layout.addWidget(self.input_file_button)
        button_frame_layout.addStretch()
        button_frame_layout.addWidget(self.control_button)
        button_frame_layout.addWidget(reset_button)
        button_frame.setLayout(button_frame_layout)
        return button_frame

    def validate_documents(self, documents: QTreeWidget):
        error_set = set()
        domain = InsertDataDomain()
        self.asset_info.clear()
        assets = []
        doc_list = [documents.topLevelItem(i).data(1, 1) for i in range(documents.topLevelItemCount())]
        global_vars.single_project.templates_in_memory = []
        for doc in doc_list:
            if Path(doc).suffix == '.xls' or Path(doc).suffix == '.xlsx':
                temp_path = domain.start_excel_changes(doc=doc)
            elif Path(doc).suffix == '.csv':
                temp_path = Path(doc)
            try:
                asset = domain.check_document(doc_location=temp_path)
                ProjectFileManager().add_template_file_to_project(Path(doc))
                assets.append(asset)
            except ExceptionsGroup as e:
                for ex in e.exceptions:
                    self.add_error_to_feedback_list(ex, doc)
                error_set.add(Path(doc))
            except ValueError:
                self.add_error_to_feedback_list("The document is not OTL conform", doc)
                error_set.add(Path(doc))
            except InvalidColumnNamesInExcelTabError as ex:
                self.add_error_to_feedback_list(ex, doc)
                error_set.add(Path(doc))
            except NoTypeUriInExcelTabError as ex:
                self.add_error_to_feedback_list(ex, doc)
                error_set.add(Path(doc))
            except TypeUriNotInFirstRowError as ex:
                self.add_error_to_feedback_list(ex, doc)
                error_set.add(Path(doc))
            except FailedToImportFileError as ex:
                self.add_error_to_feedback_list(ex, doc)
                error_set.add(Path(doc))
            except Exception as ex:
                self.add_error_to_feedback_list(ex, doc)
                error_set.add(Path(doc))
            else:
                InsertDataDomain().add_template_file_to_project(project=global_vars.single_project, filepath=Path(doc),
                                                                state=FileState.OK.name)
        if error_set:
            logging.debug('negative feedback needed')
            self.negative_feedback_message()
            for item in error_set:
                InsertDataDomain().add_template_file_to_project(project=global_vars.single_project, filepath=Path(item),
                                                                state=FileState.ERROR.name)
        else:
            logging.debug('positive feedback needed')
            self.stacked_widget.reset_ui(self._)
            self.positive_feedback_message()
        self.fill_feedback_list(assets)
        ProjectFileManager().add_project_files_to_file(global_vars.single_project)
        self.fill_list()

        DataVisualisationScreen.load_assets_and_create_html()

    def add_input_file_field(self):
        input_file = QFrame()
        input_file_layout = QHBoxLayout()
        self.input_file_field.setColumnCount(3)
        header = self.input_file_field.header()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setStretchLastSection(False)
        self.input_file_field.setHeaderHidden(True)
        input_file_layout.addWidget(self.input_file_field)
        input_file.setLayout(input_file_layout)
        return input_file

    def left_side(self):
        left_side = QFrame()
        left_side_layout = QVBoxLayout()
        left_side_layout.addSpacing(100)
        self.input_file_label.setText(self._('input_file'))
        left_side_layout.addWidget(self.input_file_label)
        left_side_layout.addWidget(self.add_input_file_field(), alignment=Qt.AlignmentFlag.AlignBottom)
        left_side_layout.addWidget(self.button_set(), alignment=Qt.AlignmentFlag.AlignTop)
        left_side_layout.addSpacing(30)
        left_side_layout.addStretch()
        left_side.setLayout(left_side_layout)
        return left_side

    def right_side(self):
        right_side = QFrame()
        right_side_layout = QVBoxLayout()
        list_item = self.add_list()
        self.construct_feedback_message()
        right_side_layout.addSpacing(100)
        right_side_layout.addWidget(list_item)
        right_side_layout.addWidget(self.feedback_message_box, alignment=Qt.AlignmentFlag.AlignTop)
        right_side.setLayout(right_side_layout)
        right_side_layout.addStretch()
        return right_side

    def construct_feedback_message(self):
        logging.debug("constructing feedback message")
        frame_layout = QHBoxLayout()
        frame_layout.addWidget(self.message_icon)
        self.message.setProperty('class', 'feedback-message')
        frame_layout.addWidget(self.message)
        frame_layout.addStretch()
        self.feedback_message_box.setLayout(frame_layout)

    def add_list(self):
        frame = QFrame()
        frame_layout = QHBoxLayout()
        frame_layout.addWidget(self.asset_info)
        frame_layout.setContentsMargins(0, 30, 50, 85)
        frame.setLayout(frame_layout)
        return frame

    def fill_list(self):
        self.input_file_field.clear()
        logging.debug("list with " + str(global_vars.single_project.templates_in_memory))
        logging.debug("Filled list with " + str(len(global_vars.single_project.templates_in_memory)) + " items")
        for asset in global_vars.single_project.templates_in_memory:
            self.add_file_to_list([asset.file_path], asset.state)

    def positive_feedback_message(self):
        self.message_icon.setPixmap(qta.icon('mdi.check', color="white").pixmap(QSize(48, 48)))
        self.message.setText(self._('all_info_correct'))
        self.feedback_message_box.setStyleSheet('background-color: #1DCA94; border-radius: 10px;')

    def warning_feedback_message(self):
        self.message_icon.setPixmap(qta.icon('mdi.alert', color="white").pixmap(QSize(48, 48)))
        self.message.setText(self._('warning'))
        self.feedback_message_box.setStyleSheet('background-color: #F8AA62; border-radius: 10px;')

    def clear_feedback_message(self):
        self.message.setText('')
        self.feedback_message_box.setStyleSheet('')

    def negative_feedback_message(self):
        self.message_icon.setPixmap(qta.icon('mdi.alert-circle-outline', color="white").pixmap(QSize(48, 48)))
        self.message.setText(self._('error'))
        self.feedback_message_box.setStyleSheet('background-color: #CC3300; border-radius: 10px;')

    def reset_ui(self, _):
        self._ = _
        self.input_file_label.setText(self._('input_file'))
        self.control_button.setText(self._('control_button'))
        self.clear_feedback_message()
        self.clear_feedback()
        self.clear_list()

    def open_file_picker(self):
        file_path = str(Path.home())
        file_picker = QFileDialog()
        file_picker.setWindowTitle("Selecteer bestand")
        file_picker.setDirectory(file_path)
        file_picker.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_picker.setNameFilter("EXCEL files (*.xlsx);;CSV files (*.csv);;JSON files (*.json)")
        if file_picker.exec():
            self.add_file_to_list(file_picker.selectedFiles())
            self.clear_feedback_message()

    def add_file_to_list(self, files: List[str], asset_state: FileState = FileState.WARNING):
        self.control_button.setDisabled(False)
        for file in files:
            list_item = QTreeWidgetItem()
            doc_name = Path(file).name
            list_item.setText(1, doc_name)
            if asset_state == FileState.OK or asset_state == "OK":
                list_item.setIcon(0, qta.icon('mdi.check', color="green"))
            elif asset_state == FileState.WARNING or asset_state == "WARNING":
                list_item.setIcon(0, qta.icon('mdi.alert', color="orange"))
            elif asset_state == FileState.ERROR or asset_state == "ERROR":
                list_item.setIcon(0, qta.icon('mdi.close', color="red"))
            list_item.setData(1, 1, file)
            list_item.setSizeHint(1, QSize(0, 30))
            self.input_file_field.addTopLevelItem(list_item)
            button = ButtonWidget()
            button.clicked.connect(lambda: self.delete_file_from_list())
            button.setIcon(qta.icon('mdi.close'))
            self.input_file_field.setItemWidget(list_item, 2, button)

    def delete_file_from_list(self):
        items = self.input_file_field.selectedItems()
        item_data = items[0].data(1, 1)
        file_in_memory = next((asset.file_path for asset in global_vars.single_project.templates_in_memory if
                               asset.file_path == item_data), None)
        if file_in_memory is not None:
            logging.debug("We've struck gold")
            InsertDataDomain().delete_project_file_from_project(global_vars.single_project, file_in_memory)
        self.input_file_field.removeItemWidget(items[0], 1)
        self.input_file_field.takeTopLevelItem(self.input_file_field.indexOfTopLevelItem(items[0]))
        if self.input_file_field.topLevelItemCount() == 0:
            self.control_button.setDisabled(True)
            self.clear_feedback()
            self.clear_feedback_message()

    def clear_list(self):
        self.input_file_field.clear()
        self.clear_feedback()
        self.control_button.setDisabled(True)

    def reset_button_functionality(self):
        RemoveProjectFilesWindow(project=global_vars.single_project, language_settings=self._)
        self.fill_list()
        self.clear_feedback()
        self.clear_feedback_message()

    def clear_feedback(self):
        self.asset_info.clear()
        self.clear_feedback_message()

    def add_error_to_feedback_list(self, e, doc):
        doc_name = Path(doc).name
        error_widget = QListWidgetItem()
        if str(e) == "argument of type 'NoneType' is not iterable":
            error_text = self._("{doc_name}: Data nodig in een datasheet om objecten in te laden.\n").format(
                doc_name=doc_name)
        elif issubclass(type(e), NoTypeUriInExcelTabError):
            error_text = self._("{doc_name}: No type uri in {tab}\n").format(doc_name=doc_name, tab=e.tab)
        elif issubclass(type(e), InvalidColumnNamesInExcelTabError):
            error_text = self._("{doc_name}: invalid columns in {tab}, bad columns are {bad_columns} \n").format(
                doc_name=doc_name, tab=e.tab, bad_columns=str(e.bad_columns))
        elif issubclass(type(e), TypeUriNotInFirstRowError):
            error_text = self._("{doc_name}: type uri not in first row of {tab}\n").format(doc_name=doc_name, tab=e.tab)
        elif issubclass(type(e), ValueError):
            error_text = self._(f'{doc_name}: {e}\n')
        elif issubclass(type(e), FailedToImportFileError):
            error_text = self._(f'{doc_name}: {e}\n')
        error_widget.setText(error_text)
        self.asset_info.addItem(error_widget)
        item = self.asset_info.findItems(error_text, Qt.MatchFlag.MatchExactly)
        for item in item:
            self.asset_info.item(self.asset_info.row(item)).setForeground(Qt.GlobalColor.red)

    def fill_feedback_list(self, assets):
        total_assets = 0
        if assets is None:
            return
        for asset in assets:
            asset_dict = count_assets_by_type(asset)
            for key, value in asset_dict.items():
                key_split = key.split('#')
                asset_widget = QListWidgetItem()
                asset_widget.setText(f'{value} objecten van het type {key_split[-1]} ingeladen\n')
                total_assets += value
                self.asset_info.addItem(asset_widget)
        asset_widget = QListWidgetItem()
        asset_widget.setText(
            f'In het totaal zijn er {total_assets} objecten ingeladen die conform zijn met de OTL standaard\n')
        self.asset_info.addItem(asset_widget)
