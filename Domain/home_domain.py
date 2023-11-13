import logging
from datetime import datetime
from pathlib import Path

from Domain.Project import Project
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
    def remove_project(project: Project, table) -> None:
        ProjectFileManager.delete_project(project.project_path)
        table.removeRow(table.currentRow())

    def alter_table(self, dlg, overview_table, project: Project = None):
        time_of_alter = datetime.now().date()
        project_exists = project is not None
        if project_exists:
            project.laatst_bewerkt = time_of_alter
            ProjectFileManager.save_project_to_dir(project)
        else:
            logging.debug("Creating new project")
            # project = self.db.add_project(properties[0], properties[1], properties[2], time_of_alter)
        overview_table.draw_table()
        dlg.close()

    def validate(self, input_eigen_ref: str, input_subset: str):
        if input_eigen_ref.strip() == "":
            raise EmptyFieldError(self._('own_reference_empty_error'))
        elif input_subset.strip() == "":
            raise EmptyFieldError(self._('bestek_empty_error'))
        else:
            return True
