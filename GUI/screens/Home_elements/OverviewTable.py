import asyncio
import logging

from typing import Union, Callable
import datetime
import qtawesome as qta
from PyQt6.QtCore import Qt

from PyQt6.QtWidgets import QTableWidget, QHeaderView, QTableWidgetItem

from Domain.step_domain.HomeDomain import HomeDomain
from Domain.project.Project import Project

from GUI.screens.general_elements.ButtonWidget import ButtonWidget
from GUI.dialog_windows.ExportProjectWindow import ExportProjectWindow
from GUI.dialog_windows.UpsertProjectWindow import UpsertProjectWindow
from GUI.dialog_windows.RemoveProjectWindow import RemoveProjectWindow


class OverviewTable(QTableWidget):

    def __init__(self, language_settings: Callable):
        super().__init__()
        self._ = language_settings
        self.projects: list
        self.main_window = None
        self.error_widget = QTableWidgetItem()
        self.projects = None
        self.cellDoubleClicked.connect(self.open_project)


    def draw_table(self) -> None:
        """
        Draws the table with specific configurations and settings.
        
        This method sets up the table by configuring its headers, enabling it, 
        and adjusting the visibility and behavior of the table elements. It 
        ensures that the table is not editable and that selection is done by 
        rows rather than individual cells.
        
        :param self: The instance of the class.
        
        :return: None
        """

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

    def fill_table(self, projects: [Project], search_text: str) -> None:
        """
        Fills the table with project data and applies a filter if necessary.
        
        This method populates the table with information from the provided 
        projects, adding the eigen referentie of the projects to each row as data. If a search text is 
        provided, it filters the displayed projects based on that text.
        
        :param self: The instance of the class.
        :param projects: A list of Project objects to be displayed in the table.
        :type projects: list[Project]
        :param search_text: A string used to filter the projects in the table.
        :type search_text: str
        
        :return: None
        """
        self.setRowCount(len(projects))
        for row_index, project in enumerate(projects.values()):
            self.add_cell_to_table(row_index, 0, project.eigen_referentie)
            self.add_cell_to_table(row_index, 1, project.bestek)
            self.add_cell_to_table( row_index, 2,project.get_subset_db_name())
            self.add_cell_to_table( row_index, 3, project.laatst_bewerkt)
            self.add_action_buttons(row= row_index, project=project)
            self.add_data_to_row(row=row_index, eigen_referentie=project.eigen_referentie)

        if search_text:
            self.filter(search_text=search_text)


    def add_cell_to_table(self, row: int, column: int, item: Union[str, datetime.datetime]) -> None:
        """Adds a cell to the table at the specified row and column with the given item.

           This method checks the type of the item being added to the table. If the item 
           is a date, it formats it as a string in the "dd-mm-yyyy" format; otherwise, 
           it converts the item to a string before adding it to the specified cell.

           :param self: The instance of the class.
           :param row: The row index where the cell will be added.
           :param column: The column index where the cell will be added.
           :param item: The item to be added to the cell, which can be a string or a datetime object.

           :return: None
           """
        if isinstance(item, datetime.date):
            self.setItem(row, column, QTableWidgetItem(item.strftime("%d-%m-%Y")))
        else:
            self.setItem(row, column, QTableWidgetItem(str(item)))

    def add_action_buttons(self, row: int, project: Project) -> None:
        """
        Adds action buttons to the specified row for a given project.

        This method creates and configures three action buttons: an edit button, 
        a delete button, and a share button. Each button is connected to its respective 
        action, allowing users to edit project details, remove the project, or share 
        the project.

        :param self: The instance of the class.
        :param row: The row index where the buttons will be added.
        :type row: int
        :param project: The project object associated with the buttons.
        :type project: Project

        :return: None
        """
        edit_btn = ButtonWidget()
        edit_btn.setIcon(qta.icon('mdi.pencil'))
        edit_btn.setProperty('class','alter-button')
        edit_btn.clicked.connect(
            lambda _, input_projects=project: self.start_dialog_window(project=input_projects))
       

        delete_btn = ButtonWidget()
        delete_btn.setIcon(qta.icon('mdi.trash-can'))
        delete_btn.setProperty('class', 'alter-button')
        delete_btn.clicked.connect(lambda _, input_project=project:
                                   RemoveProjectWindow(language_settings=self._,
                                                       project=input_project))
       

        share_btn = ButtonWidget()
        share_btn.setIcon(qta.icon("mdi.share"))
        share_btn.setProperty('class', 'alter-button')
        share_btn.clicked.connect(lambda _, input_project=project:
                                  ExportProjectWindow().export_project_window(project=input_project))
        
        self.setCellWidget(row, 4, edit_btn)
        self.setCellWidget(row, 5, delete_btn)
        self.setCellWidget(row, 6, share_btn)

    def open_project(self, row) -> None:
        """
        Opens a project based on the specified row index.

        This method retrieves the project reference from the specified row in the 
        table and sets the main window to the project view. It then calls the 
        appropriate method to open the project using the retrieved reference.

        :param self: The instance of the class.
        :param row: The row index from which to retrieve the project reference.

        :return: None
        """

        self.main_window.setCurrentIndex(1)
        project_ref = self.item(row, 0).data(1)

        HomeDomain.open_project(project_ref=project_ref)

    def filter(self, search_text: str = "") -> None:
        """
        Filters the table rows based on the absence of the provided search text.

        This method searches through all columns of the table for the specified
        search text. If the text is not found in any of the relevant fields,
        the corresponding rows are marked for removal from the table.

        Args:
            self: The instance of the class.
            search_text (str): The text to search for in the table rows. Defaults to an empty string.

        Returns:
            None
        """

        rows_to_remove = []

        # search on all columns
        for i in range(self.rowCount()):
            eigen_referentie = self.item(i,0).text()
            bestek = self.item(i,1).text()
            subset = self.item(i,2).text()
            laatst_bewerkt = self.item(i,3).text()

            if (
                search_text not in eigen_referentie.lower()
                and search_text not in bestek.lower()
                and search_text not in subset.lower()
                and search_text not in laatst_bewerkt.lower()
            ):
                rows_to_remove.append(i)

        for row_i in rows_to_remove:
            self.removeRow(row_i)

    def start_dialog_window(self, project: Project = None) -> None:
        """
        Starts a dialog window for upserting project information.

        This method initializes the UpsertProjectWindow, allowing users to
        create or update project details. It can optionally take a project
        object to pre-fill the dialog with existing project information.

        Args:
            self: The instance of the class.
            project (Project, optional): The project object to be edited. Defaults to None.

        Returns:
            None
        """

        UpsertProjectWindow(language_settings=self._,project=project)

    def reset_ui(self, lang_settings: dict) -> None:
        """
        Resets the user interface with the provided language settings.

        This method updates the UI elements based on the specified language settings.
        It redraws the table, sets the horizontal header labels, and updates the error
        widget to display a message indicating no results.

        Args:
            self: The instance of the class.
            lang_settings (dict): A dictionary containing language settings for the UI.

        Returns:
            None
        """

        self._ = lang_settings
        self.draw_table()
        self.setHorizontalHeaderLabels(
            [self._('own_reference'), self._('service_order'), self._('subset'), self._('last_edited'), '', ''])
        self.error_widget.setText(self._('no_results'))

    def add_data_to_row(self, row: int, eigen_referentie: str) -> None:
        """
        Adds data to the specified row in the table.

        This method updates the first item in the specified row with the given
        eigen referentie value. It sets the data for the item at the first column
        of the specified row.

        Args:
            self: The instance of the class.
            row: The row index where the data will be added.
            eigen_referentie: The value to be set in the first item of the row.

        Returns:
            None
        """

        first_item_in_row = self.item(row, 0)
        first_item_in_row.setData(1,eigen_referentie)
