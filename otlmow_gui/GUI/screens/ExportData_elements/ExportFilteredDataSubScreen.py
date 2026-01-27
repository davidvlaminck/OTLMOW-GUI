import traceback
from pathlib import Path

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QVBoxLayout, QFrame, QHBoxLayout, QLabel, QTreeWidget, QHeaderView, \
    QPushButton, QTableWidget, QTreeWidgetItem
from otlmow_converter.Exceptions.ExceptionsGroup import ExceptionsGroup

from otlmow_gui.Domain.logger.OTLLogger import OTLLogger
from otlmow_gui.Domain.step_domain.ExportFilteredDataSubDomain import ExportFilteredDataSubDomain
from otlmow_gui.GUI.dialog_windows.file_picker_dialog.LoadFilePickerDialog import LoadFilePickerDialog
from otlmow_gui.GUI.screens.ExportData_elements.ChangesTableView import ChangesTableView
from otlmow_gui.GUI.screens.ExportData_elements.TableErrorModel import TableErrorModel
from otlmow_gui.GUI.screens.ExportData_elements.TableModel import TableModel
from otlmow_gui.GUI.screens.ExportData_elements.AbstractExportDataSubScreen import AbstractExportDataSubScreen
from otlmow_gui.GUI.screens.general_elements.ButtonWidget import ButtonWidget
import qtawesome as qta

from otlmow_gui.GUI.translation.ValidationErrorReportTranslations import ValidationErrorReportTranslations
from otlmow_gui.exception_handler.ExceptionHandlers import create_task_reraise_exception


class ExportFilteredDataSubScreen(AbstractExportDataSubScreen):
    def __init__(self, language_settings=None):
        self.original_file_label = QLabel()
        self.original_file_field = QTreeWidget()

        self.control_button = ButtonWidget()
        self.refresh_button = QPushButton()
        # self.export_button = ButtonWidget()
        self.input_file_button = QPushButton()
        self.feedback_diff_label = QLabel()
        self.feedback_diff_table = ChangesTableView()
        self.message_icon = QLabel()
        self.message = QLabel()
        self.feedback_message_box = QFrame()
        self.model = None
        super().__init__(language_settings=language_settings)
        self.load_file_dialog_window = LoadFilePickerDialog(self._)

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
        layout.addWidget(self.left_side(),stretch=1)
        layout.addWidget(self.right_side(),stretch=2)
        frame.setLayout(layout)
        return frame

    def left_side(self):
        frame = QFrame()
        frame_layout = QVBoxLayout()
        frame_layout.addWidget(self.input_original_file_field())
        frame_layout.addWidget(self.button_group())
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
        self.message_icon.setVisible(True)
        self.message_icon.setPixmap(qta.icon('mdi.check', color="white").pixmap(QSize(48, 48)))
        self.message.setText(self._('all_info_correct'))
        self.feedback_message_box.setStyleSheet('background-color: #1DCA94; border-radius: 10px;')

    def clear_feedback_message(self):
        self.message.setText('')
        self.message_icon.setVisible(False)
        self.feedback_message_box.setStyleSheet('')

    def negative_feedback_message(self):
        self.message_icon.setVisible(True)
        self.message_icon.setPixmap(qta.icon('mdi.alert-circle-outline', color="white").pixmap(QSize(48, 48)))
        self.message.setText(self._('error'))
        self.feedback_message_box.setStyleSheet('background-color: #CC3300; border-radius: 10px;')

    def change_table(self):
        self.feedback_diff_table.setEnabled(True)
        self.feedback_diff_table.verticalHeader().setHidden(True)
        self.feedback_diff_table.horizontalHeader().setStretchLastSection(False)
        self.feedback_diff_table.resetPainting()
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
        self.refresh_button.clicked.connect(lambda: self.remove_all_original_documents())
        frame_layout.addWidget(self.input_file_button)
        frame_layout.addStretch()
        frame_layout.addWidget(self.control_button)
        # frame_layout.addWidget(self.export_button)
        frame_layout.addWidget(self.refresh_button)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame.setLayout(frame_layout)
        return frame

    def remove_all_original_documents(self):
        ExportFilteredDataSubDomain.remove_all_original_documents()


    def navigate_to_diff_report(self, table):
        try:
            create_task_reraise_exception(ExportFilteredDataSubDomain.get_diff_report())
        except Exception as e:
            # TODO: proper error message when original file to be loaded for comparison cannot be loaded
            raise e


    def fill_up_change_table(self, report):
        data = [
            [
                str(i+1),
                str(rep.id),
                str(rep.actie.value),
                str(rep.attribute),
                str(rep.original_value),
                str(rep.new_value),
            ]
            for i,rep in enumerate(report)
        ]
        self.model = TableModel(data, self._)
        self.feedback_diff_table.setModel(self.model)

    def clear_change_table(self):
        self.fill_up_change_table([])

    def open_original_file_picker(self):
        selected_file_path_list = self.load_file_dialog_window.summon()

        if selected_file_path_list:
            OTLLogger.logger.debug("file picker executed")
            ExportFilteredDataSubDomain.add_original_documents(selected_file_path_list)

            

    def update_original_files_list(self, files:dict[str,Path]):
        
        files_str = str(files)
        OTLLogger.logger.debug(f"adding file to list {files_str}")
        self.original_file_field.clear()
        self.clear_change_table()
        self.clear_feedback_message()

        for doc_name in files.keys():
            list_item = QTreeWidgetItem()
            list_item.setText(0, doc_name)
            list_item.setData(0, 1, doc_name)
            self.original_file_field.addTopLevelItem(list_item)
            button = ButtonWidget()
            button.clicked.connect(lambda: self.delete_file_from_list())
            button.setIcon(qta.icon('mdi.close'))
            self.original_file_field.setItemWidget(list_item, 1, button)



        if self.original_file_field.topLevelItemCount() == 0:
            self.control_button.setDisabled(True)
            self.export_btn.setDisabled(True)

        else:
            self.control_button.setDisabled(False)
            self.export_btn.setDisabled(False)

    def delete_file_from_list(self):
        items = self.original_file_field.selectedItems()
        doc_name = items[0].data(0,1)
        ExportFilteredDataSubDomain.delete_original_file(doc_name=doc_name)


    def process_export(self, document_path_list, csv_option, split_relations_and_objects):

        OTLLogger.logger.debug(document_path_list)
        create_task_reraise_exception(
            ExportFilteredDataSubDomain.export_diff_report(file_name=document_path_list[0],
                                                           separate_per_class_csv_option=csv_option,
                                                           separate_relations_option=split_relations_and_objects))

    def add_error_to_feedback_list(self, exception: Exception, doc: str) -> None:
        """Adds an error message to the feedback list based on the exception type.

        This method constructs a user-friendly error message from the provided
        exception and document name, then adds it to the feedback list. It
        handles various types of errors, formatting the message accordingly,
        and highlights the error in red for visibility.

        Args:
            self: The instance of the class.
            exception (Exception): The exception that occurred, used to determine the error message.
            doc (str): The path of the document associated with the error.

        Returns:
            None
        """

        OTLLogger.logger.debug(str(exception))
        traceback.print_exception(exception)
        doc_name = Path(doc).name

        return ValidationErrorReportTranslations.translate_exception(doc_name, exception)



    def fill_up_change_table_with_error_feedback(self, error_set: list[dict]):
        """Processes a set of errors and populates the feedback list.

        This method iterates through the provided error set, extracting exceptions
        and their associated document paths. It adds each error to the feedback
        list, handling both individual exceptions and groups of exceptions.

        Args:
            self: The instance of the class.
            error_set (list): A list of error items, each containing an exception
                              and a document path.

        Returns:
            None
        """
        data = []
        for item in error_set:
            exception = item["exception"]
            doc = item["path_str"]

            if isinstance(exception, ExceptionsGroup):
                for ex in exception.exceptions:
                    data.append([self.add_error_to_feedback_list(ex, doc)])
            else:
                data.append([self.add_error_to_feedback_list(exception, doc)])

        self.model = TableErrorModel(data, self._)
        self.feedback_diff_table.setModel(self.model)

    def create_button_box(self):
        frame = super().create_button_box()
        self.export_btn.setDisabled(True)
        return frame

