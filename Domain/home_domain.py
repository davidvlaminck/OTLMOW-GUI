from datetime import datetime
from pathlib import Path

from Domain.ProjectFileManager import ProjectFileManager
from Exceptions.EmptyFieldError import EmptyFieldError


class HomeDomain:

    def __init__(self, database, language_settings):
        self.db = database
        self._ = language_settings

    def get_amount_of_rows(self) -> int:
        return self.db.count_projects()

    @staticmethod
    def get_all_projects() -> list:
        return ProjectFileManager.get_all_otl_wizard_projects()

    @staticmethod
    def remove_project(project_path: Path, table) -> None:
        ProjectFileManager.delete_project(project_path)
        table.removeRow(table.currentRow())

    def alter_table(self, properties: list, dlg, overview_table, id_=None):
        time_of_alter = datetime.now()
        properties += [time_of_alter]
        project_exists = id_ is not None
        if project_exists:
            self.db.update_project(id_, properties[0], properties[1], properties[2], time_of_alter)
        else:
            id_ = self.db.add_project(properties[0], properties[1], properties[2], time_of_alter)
        overview_table.draw_table()
        dlg.close()

    def validate(self, input_eigen_ref: str, input_subset: str):
        if input_eigen_ref.strip() == "":
            raise EmptyFieldError(self._('own_reference_empty_error'))
        elif input_subset.strip() == "":
            raise EmptyFieldError(self._('bestek_empty_error'))
        else:
            return True
