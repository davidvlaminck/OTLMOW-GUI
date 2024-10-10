import asyncio
import logging
from typing import Union
import datetime
import qtawesome as qta
from PyQt6.QtCore import Qt

from PyQt6.QtWidgets import QTableWidget, QHeaderView, QTableWidgetItem


from Domain import global_vars
from Domain.RelationChangeDomain import RelationChangeDomain
from Domain.Project import Project
from Domain.ProjectFileManager import ProjectFileManager
from Domain.HomeDomain import HomeDomain
from Domain.ModelBuilder import ModelBuilder
from Exceptions.EmptySearchWarning import EmptySearchWarning
from GUI.ButtonWidget import ButtonWidget
from GUI.DialogWindows.ExportProjectWindow import ExportProjectWindow
from GUI.DialogWindows.UpsertProjectWindow import UpsertProjectWindow


class OverviewTable(QTableWidget):

    def __init__(self, search_message, language_settings, home_domain, message_box):
        super().__init__()
        self.search_message = search_message
        self._ = language_settings
        self.home_domain = home_domain
        self.projects: list
        self.message_box = message_box
        self.main_window = None
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
        # Zorgt ervoor dat selectie op row is niet op cell
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        # Zorgt ervoor dat de table niet editable is
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        projects = global_vars.projects
        try:
            projects = self.filter_projects(projects, input_text)
            self.fill_table(projects=projects)
        except EmptySearchWarning as e:
            self.add_the_error_row(table=self)

    def fill_table(self, projects: [Project]):
        indices = self.selectionModel().selectedRows()
        for index in sorted(indices):
            self.removeRow(index.row())
        self.setRowCount(len(projects))
        for row_index, element in enumerate(projects):
            self.add_cell_to_table(self, row=row_index, column=0, item=element.eigen_referentie)
            self.add_cell_to_table(self, row=row_index, column=1, item=element.bestek)
            self.add_cell_to_table(self, row=row_index, column=2,
                                   item=ModelBuilder(element.subset_path).get_name_project())
            self.add_cell_to_table(self, row=row_index, column=3, item=element.laatst_bewerkt)
            self.add_action_buttons(row_index, element, self)
        self.cellDoubleClicked.connect(self.create_async_task)

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
        error_widget = QTableWidgetItem()
        error_widget.setText(self._("no_result"))
        table.setItem(0, 0, error_widget)

    def add_action_buttons(self, row: int, project: Project, table: QTableWidget) -> None:
        edit_btn = ButtonWidget()
        edit_btn.setIcon(qta.icon('mdi.pencil'))
        edit_btn.setProperty('class', 'alter-button')
        edit_btn.clicked.connect(
            lambda _, project_details=project: self.start_dialog_window(project=project_details))
        table.setCellWidget(row, 4, edit_btn)

        delete_btn = ButtonWidget()
        delete_btn.setIcon(qta.icon('mdi.trash-can'))
        delete_btn.setProperty('class', 'alter-button')
        delete_btn.clicked.connect(lambda _, i=project:
                                   self.message_box.draw_remove_project_screen(i, self))
        table.setCellWidget(row, 5, delete_btn)

        share_btn = ButtonWidget()
        share_btn.setIcon(qta.icon("mdi.share"))
        share_btn.setProperty('class', 'alter-button')
        share_btn.clicked.connect(lambda _, i=project:
                                  ExportProjectWindow().export_project_window(project=i))
        table.setCellWidget(row, 6, share_btn)

    def create_async_task(self, row):
        logging.debug("called this loopdieloop")
        self.main_window.setCurrentIndex(1)
        project = self.item(row, 0).text()
        projects = ProjectFileManager.get_all_otl_wizard_projects()
        p = next(k for k in projects if k.eigen_referentie == project)
        self.main_window.widget(1).tab1.project = p
        p = ProjectFileManager.get_objects_list_saved_in_project(p)
        global_vars.single_project = p
        self.main_window.reset_ui(self._)
        self.main_window.widget(2).tab1.fill_list()
        self.main_window.widget(1).tab1.update_project_info()
        self.main_window.widget(2).tab1.fill_list()
        RelationChangeDomain.init_static(global_vars.single_project)
        event_loop = asyncio.get_event_loop()
        event_loop.create_task(self.navigate_to_project())

    async def navigate_to_project(self):
        logging.debug("called")
        await self.main_window.widget(1).tab1.fill_list()

    @staticmethod
    def filter_projects(projects, input_text: str = None):
        projects = global_vars.projects
        if type(input_text) is str:
            input_text.strip()
            if len(input_text) != 0:
                projects = [k for k in projects if
                            k.eigen_referentie.startswith(input_text) or k.bestek.startswith(input_text)]
                if len(projects) == 0:
                    projects.append(global_vars.projects)
                    raise EmptySearchWarning('no_results')
        return projects

    def start_dialog_window(self, project: Project = None) -> None:
        upsert_project_window = UpsertProjectWindow(self._)
        # TODO: return waarden uit dialog om daar dan alles af te handelen bv draw_table uit home_domain
        upsert_project_window.draw_upsert_project(project=project, overview_table=self)

    def reset_ui(self, lang_settings):
        self._ = lang_settings
        self.draw_table()
        self.setHorizontalHeaderLabels(
            [self._('own_reference'), self._('service_order'), self._('subset'), self._('last_edited'), '', ''])
        self.error_widget.setText(self._('no_results'))
