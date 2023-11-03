from typing import Union
import datetime
import qtawesome as qta
from PyQt6.QtCore import Qt

from PyQt6.QtWidgets import QTableWidget, QHeaderView, QTableWidgetItem, QPushButton

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

    def draw_table(self, input_text: str = None):
        try:
            self.search_message.setText("")
            self.projects = self.filter_projects(self._, self.home_domain, input_text)
        except EmptySearchWarning as e:
            self.search_message.setText(str(e))
        self.setRowCount(len(self.projects))
        self.verticalHeader().setVisible(False)
        self.setColumnCount(6)
        # Set the width of the columns to stretch except the last two columns for buttons
        for column in range(self.columnCount() - 2):
            self.horizontalHeader().setSectionResizeMode(column, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.setShowGrid(False)
        # Zorgt ervoor dat selectie op row is niet op cell
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        # Zorgt ervoor dat de table niet editable is
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setHorizontalHeaderLabels(
            [self._('own_reference'), self._('service_order'), self._('subset'), self._('last_edited'), '', ''])
        # ALign titles of header to the left
        self.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)

        # TODO: add data to the table in aparte functie
        for count, element in enumerate(self.projects):
            for i in range(4):
                self.add_cell_to_table(self, count, i, element[i + 1])
            self.add_update_and_delete_button(count, element[0], self)
            self.doubleClicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

    @staticmethod
    def add_cell_to_table(table: QTableWidget, row: int, column: int, item: Union[str, datetime.datetime]) -> None:
        if isinstance(item, datetime.date):
            table.setItem(row, column, QTableWidgetItem(item.strftime("%d-%m-%Y")))
        else:
            table.setItem(row, column, QTableWidgetItem(item))

    def add_update_and_delete_button(self, count: int, id_: int, table: QTableWidget) -> None:
        edit = QPushButton()
        edit.setIcon(qta.icon('mdi.pencil'))
        edit.setProperty('class', 'alter-button')
        edit.clicked.connect(
            lambda _, row_id=id_: self.start_dialog_window(id_=row_id, is_project=True))
        table.setCellWidget(count, 4, edit)
        button = QPushButton()
        button.setIcon(qta.icon('mdi.trash-can'))
        button.setProperty('class', 'alter-button')
        button.clicked.connect(lambda _, i=id_:
                               self.message_box.draw_remove_project_screen(i, self))
        table.setCellWidget(count, 5, button)

    @staticmethod
    def filter_projects(_, home_domain, input_text: str = None):
        projects = home_domain.get_all_projects()
        if type(input_text) is str:
            input_text.strip()
            if len(input_text) != 0:
                projects = [k for k in projects if k[1].startswith(input_text) or k[2].startswith(input_text)]
                if len(projects) == 0:
                    projects.append(home_domain.get_all_projects())
                    # TODO: make this a custom exception (if time)
                    raise EmptySearchWarning(_('no_results'))
        return projects

    def start_dialog_window(self, id_: int = None, is_project=False) -> None:
        dialog_window = DialogWindow(self.database, self._)
        if is_project:
            dialog_window.draw_upsert_project(id_=id_, overview_table=self)

    def reset_language(self, lang_settings):
        self._ = lang_settings
        self.draw_table()