import logging
from typing import Union
import datetime
import qtawesome as qta
from PyQt6.QtCore import Qt

from PyQt6.QtWidgets import QTableWidget, QHeaderView, QTableWidgetItem, QPushButton

from Domain.Project import Project
from Domain.home_domain import HomeDomain
from Domain.model_builder import ModelBuilder
from Exceptions.EmptySearchWarning import EmptySearchWarning
from GUI.dialog_window import DialogWindow


class OverviewTable(QTableWidget):

    def __init__(self, search_message, language_settings, home_domain, message_box, database):
        super().__init__()
        self.search_message = search_message
        self._ = language_settings
        self.home_domain = home_domain
        self.projects: list
        self.message_box = message_box
        self.database = database
        self.stacked_widget = None
        self.error_widget = QTableWidgetItem()
        self.projects = None

    def draw_table(self, input_text: str = None):
        self.setEnabled(True)
        self.verticalHeader().setVisible(False)
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels(
            [self._('own_reference'), self._('service_order'), self._('subset'), self._('last_edited'), '', '', ''])
        # ALign titles of header to the left
        self.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
        for column in range(self.columnCount() - 2):
            self.horizontalHeader().setSectionResizeMode(column, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        self.setShowGrid(False)
        try:
            self.search_message.setText("")
            self.projects = self.filter_projects(self._, input_text)
        except EmptySearchWarning as e:
            self.add_the_error_row(self)
            return
        self.setRowCount(len(self.projects))
        # Zorgt ervoor dat selectie op row is niet op cell
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        # Zorgt ervoor dat de table niet editable is
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.fill_table()

    def fill_table(self):
        indices = self.selectionModel().selectedRows()
        for index in sorted(indices):
            self.removeRow(index.row())
        self.setRowCount(len(self.projects))
        for count, element in enumerate(self.projects):
            self.add_cell_to_table(self, count, 0, element.eigen_referentie)
            self.add_cell_to_table(self, count, 1, element.bestek)
            self.add_cell_to_table(self, count, 2, ModelBuilder(element.subset_path).get_name_project())
            logging.debug(element.subset_path)
            self.add_cell_to_table(self, count, 3, element.laatst_bewerkt)
            self.add_update_and_delete_button(count, element, self)
            self.doubleClicked.connect(lambda _, project=element: self.navigate_to_project(project))

    @staticmethod
    def add_cell_to_table(table: QTableWidget, row: int, column: int, item: Union[str, datetime.datetime]) -> None:
        if isinstance(item, datetime.date):
            table.setItem(row, column, QTableWidgetItem(item.strftime("%d-%m-%Y")))
        else:
            table.setItem(row, column, QTableWidgetItem(str(item)))

    def add_the_error_row(self, table):
        table.setEnabled(False)
        table.setRowCount(1)
        table.clearContents()
        self.error_widget.setText(self._('no_results'))
        table.setItem(0, 0, self.error_widget)

    def add_update_and_delete_button(self, count: int, project: Project, table: QTableWidget) -> None:
        edit = QPushButton()
        edit.setIcon(qta.icon('mdi.pencil'))
        edit.setProperty('class', 'alter-button')
        edit.clicked.connect(
            lambda _, project_details=project: self.start_dialog_window(project=project_details, is_project=True))
        table.setCellWidget(count, 4, edit)

        delete_btn = QPushButton()
        delete_btn.setIcon(qta.icon('mdi.trash-can'))
        delete_btn.setProperty('class', 'alter-button')
        delete_btn.clicked.connect(lambda _, i=project:
                                   self.message_box.draw_remove_project_screen(i, self))
        table.setCellWidget(count, 5, delete_btn)

        share_btn = QPushButton()
        share_btn.setIcon(qta.icon("mdi.share"))
        share_btn.setProperty('class', 'alter-button')
        table.setCellWidget(count, 6, share_btn)

    def navigate_to_project(self, project):
        self.stacked_widget.widget(1).tab1.project = project
        self.stacked_widget.widget(1).tab1.fill_list()
        self.stacked_widget.widget(1).tab1.update_project_info()
        self.stacked_widget.setCurrentIndex(1)

    @staticmethod
    def filter_projects(_, input_text: str = None):
        projects = HomeDomain.get_all_projects()
        if type(input_text) is str:
            input_text.strip()
            if len(input_text) != 0:
                projects = [k for k in projects if k.eigen_referentie.startswith(input_text) or k.bestek.startswith(input_text)]
                if len(projects) == 0:
                    projects.append(HomeDomain.get_all_projects())
                    raise EmptySearchWarning(_('no_results'))
        return projects

    def start_dialog_window(self, project: Project = None, is_project=False) -> None:
        dialog_window = DialogWindow(self._)
        if is_project:
            dialog_window.draw_upsert_project(project=project, overview_table=self)

    def reset_ui(self, lang_settings):
        self._ = lang_settings
        self.fill_table()
        self.setHorizontalHeaderLabels(
            [self._('own_reference'), self._('service_order'), self._('subset'), self._('last_edited'), '', ''])
        self.error_widget.setText(self._('no_results'))
