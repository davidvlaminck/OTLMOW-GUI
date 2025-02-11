import asyncio
from pathlib import Path

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QVBoxLayout, QFrame, QHBoxLayout, QLabel, QTreeWidget, QHeaderView, \
    QPushButton, QTableView, QTableWidget, QFileDialog, QTreeWidgetItem

from Domain import global_vars
from Domain.logger.OTLLogger import OTLLogger
from Domain.step_domain.AssetChangeDomain import ExportFilteredDataSubDomain
from GUI.dialog_windows.ChooseFileNameWindow import ChooseFileNameWindow
from GUI.screens.ExportData_elements.TableModel import TableModel
from GUI.screens.ExportData_elements.AbstractExportDataSubScreen import AbstractExportDataSubScreen
from GUI.screens.general_elements.ButtonWidget import ButtonWidget
import qtawesome as qta

class ExportFilteredDataSubScreen(AbstractExportDataSubScreen):
    def __init__(self, language_settings=None):
        self.original_file_label = QLabel()
        self.original_file_field = QTreeWidget()

        self.control_button = ButtonWidget()
        self.refresh_button = QPushButton()
        # self.export_button = ButtonWidget()
        self.input_file_button = QPushButton()
        self.feedback_diff_label = QLabel()
        self.feedback_diff_table = QTableView()
        self.message_icon = QLabel()
        self.message = QLabel()
        self.feedback_message_box = QFrame()
        self.model = None

        super().__init__(language_settings=language_settings)



    def init_ui(self) -> None:
        """
        Initializes the user interface for the export data screen. This method sets up the layout
        by adding spacing, a menu, and configuring the container's margins and stretch properties
        to ensure proper alignment and appearance.

        :return: None
        """
        sub_window_layout = QVBoxLayout()
        sub_window_layout.addWidget(self.create_filter_unedited_data_box())
        sub_window_layout.addSpacing(10)
        sub_window_layout.addWidget(self.create_filetype_combobox())
        sub_window_layout.addWidget(self.create_relations_split_optionality())
        sub_window_layout.addSpacing(10)
        sub_window_layout.addWidget(self.create_button_box())
        sub_window_layout.addSpacing(10)

        self.setLayout(sub_window_layout)

    def create_filter_unedited_data_box(self):
        frame:QFrame = QFrame()
        layout:QHBoxLayout = QHBoxLayout()
        layout.addWidget(self.left_side())
        layout.addWidget(self.right_side())
        frame.setLayout(layout)
        return frame

    def left_side(self):
        frame = QFrame()
        frame_layout = QVBoxLayout()
        frame_layout.addWidget(self.input_original_file_field())
        frame_layout.addWidget(self.button_group())
        frame_layout.addStretch()
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame.setLayout(frame_layout)
        return frame

    def right_side(self):
        frame = QFrame()
        frame_layout = QVBoxLayout()
        frame_layout.addWidget(self.create_feedback_diff_table())
        frame_layout.addWidget(self.feedback_message_box)
        frame_layout.setContentsMargins(0,0,0,0)
        frame.setLayout(frame_layout)
        return frame

    def create_feedback_diff_table(self):
        frame = QFrame()
        frame_layout = QVBoxLayout()
        self.feedback_diff_label.setText(self._('changes preview'))
        frame_layout.addWidget(self.feedback_diff_label)
        self.change_table()
        frame_layout.addWidget(self.feedback_diff_table)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        self.construct_feedback_message()
        frame.setLayout(frame_layout)
        return frame

    def construct_feedback_message(self):
        # OTLLogger.logger.debug("constructing feedback message")
        frame_layout = QHBoxLayout()
        frame_layout.addWidget(self.message_icon)
        self.message.setProperty('class', 'feedback-message')
        frame_layout.addWidget(self.message)
        frame_layout.addStretch()
        frame_layout.setContentsMargins(0, 0, 0, 0)
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

    def change_table(self):
        self.feedback_diff_table.setEnabled(True)
        self.feedback_diff_table.verticalHeader().setHidden(True)
        self.feedback_diff_table.horizontalHeader().setStretchLastSection(False)
        self.feedback_diff_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.feedback_diff_table.setShowGrid(False)
        self.feedback_diff_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)


    def input_original_file_field(self):
        input_file = QFrame()
        input_file_layout = QVBoxLayout()
        self.original_file_label.setText(self._('original_file_load'))

        self.original_file_field.setHeaderHidden(True)
        self.original_file_field.setColumnCount(2)
        self.original_file_field.header().setStretchLastSection(False)
        self.original_file_field.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        input_file_layout.addWidget(self.original_file_label)
        input_file_layout.addWidget(self.original_file_field)
        input_file_layout.setContentsMargins(0, 0, 0, 0)
        input_file.setLayout(input_file_layout)
        return input_file

    def button_group(self):
        frame = QFrame()
        frame_layout = QHBoxLayout()
        self.input_file_button.setText(self._('choose_file'))
        self.input_file_button.setProperty('class', 'primary-button')
        self.input_file_button.clicked.connect(lambda: self.open_original_file_picker())
        self.control_button.setText(self._('show differences'))
        self.control_button.setProperty('class', 'primary-button')
        self.control_button.setDisabled(True)
        self.control_button.clicked.connect(lambda: self.navigate_to_diff_report(self.feedback_diff_table))

        # self.export_button.setText(self._('apply differences'))
        # self.export_button.setDisabled(True)
        # self.export_button.setProperty('class', 'primary-button')
        # self.export_button.clicked.connect(lambda: self.replace_file_with_diff_report())

        self.refresh_button.setText(self._('empty fields'))
        self.refresh_button.setProperty('class', 'secondary-button')
        self.refresh_button.clicked.connect(lambda: self.clear_user_fields())
        frame_layout.addWidget(self.input_file_button)
        frame_layout.addStretch()
        frame_layout.addWidget(self.control_button)
        # frame_layout.addWidget(self.export_button)
        frame_layout.addWidget(self.refresh_button)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame.setLayout(frame_layout)
        return frame

    def clear_user_fields(self):
        self.original_file_field.clear()
        if self.model is not None:
            self.model._data = []
        self.feedback_diff_table.clearSpans()
        self.control_button.setDisabled(True)
        # self.export_button.setDisabled(True)

    def navigate_to_diff_report(self, table):
        original_documents = [self.original_file_field.topLevelItem(i).data(0, 1) for i in
                              range(self.original_file_field.topLevelItemCount())]
        event_loop = asyncio.get_event_loop()
        event_loop.create_task(ExportFilteredDataSubDomain.get_diff_report(original_documents=original_documents))


    def insert_change_report(self,report:dict):
        self.fill_up_change_table(report, self.feedback_diff_table)
        # self.export_button.setDisabled(False)

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
        original_documents = [self.original_file_field.topLevelItem(i).data(0, 1) for i in
                              range(self.original_file_field.topLevelItemCount())]
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

    def open_original_file_picker(self):
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
            self.original_file_field.addTopLevelItem(list_item)
            button = ButtonWidget()
            button.clicked.connect(lambda: self.delete_file_from_list())
            button.setIcon(qta.icon('mdi.close'))
            self.original_file_field.setItemWidget(list_item, 1, button)

    def delete_file_from_list(self):
        items = self.original_file_field.selectedItems()
        self.original_file_field.removeItemWidget(items[0], 1)
        self.original_file_field.takeTopLevelItem(self.original_file_field.indexOfTopLevelItem(items[0]))
        if self.original_file_field.topLevelItemCount() == 0:
            self.control_button.setDisabled(True)

    def open_file_picker(self):
        """
        Opens a file picker dialog for the user to select a location to save exported files.
        This method configures the dialog based on the currently selected file format and options,
        and triggers the file generation process if a valid file location is chosen.

        :return: None
        """

        file_path = str(Path.home())

        file_picker = QFileDialog()
        file_picker.setModal(True)
        file_picker.setDirectory(file_path)

        chosen_file_format = self.file_extension_selection.currentText()
        if chosen_file_format in self.supported_export_formats:
            file_suffix = self.supported_export_formats[chosen_file_format]
            filter_filepicker = f"{chosen_file_format} files (*.{file_suffix})"
            document_loc = file_picker.getSaveFileName(filter=filter_filepicker)
        else:
            document_loc = file_picker.getSaveFileName()

        if document_loc != ('', ''):
            csv_option = self.extra_option_csv.isChecked()
            split_relations_and_objects = self.relations_split_optionality.isChecked()

            original_documents = [self.original_file_field.topLevelItem(i).data(0, 1) for i in
                                  range(self.original_file_field.topLevelItemCount())]
            OTLLogger.logger.debug(f"original documents {original_documents}")

            event_loop = asyncio.get_event_loop()
            event_loop.create_task(ExportFilteredDataSubDomain.export_diff_report(project=global_vars.current_project,
                                                                                  original_documents=original_documents,
                                                                                  file_name=document_loc[0],
                                                                                  separate_per_class_csv_option=csv_option,
                                                                                  separate_relations_option=split_relations_and_objects))
