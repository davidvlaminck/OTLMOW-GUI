import logging
from datetime import datetime
from pathlib import Path

from Domain import global_vars
from Domain.Project import Project
from Domain.ProjectFileManager import ProjectFileManager
from Exceptions.EmptyFieldError import EmptyFieldError


class HomeDomain:

    def __init__(self, language_settings):
        self._ = language_settings

    @staticmethod
    def get_all_projects() -> list:
        return ProjectFileManager.get_all_otl_wizard_projects()

    @staticmethod
    def remove_project(project: Project, table) -> None:
        ProjectFileManager.delete_project_files_by_path(project.project_path)
        table.removeRow(table.currentRow())

    # TODO: Remove draw_table naar ergens anders
    # TODO: Rename alter_table want je past geen table aan maar de projecten
    @staticmethod
    def alter_table(dlg, overview_table, project: Project = None):
        time_of_alter = datetime.now().date()
        project.laatst_bewerkt = time_of_alter
        project_exists = project.project_path is not None
        if project_exists:
            ProjectFileManager.save_project_to_dir(project)
            # TODO: load projects from files from load_projects_from_file
        else:
            project.project_path = Path(ProjectFileManager.get_otl_wizard_projects_dir() / 'Projects' / project.eigen_referentie)
            ProjectFileManager.save_project_to_dir(project)
        overview_table.draw_table()
        dlg.close()

    def validate(self, input_eigen_ref: str, input_subset: str):
        if input_eigen_ref.strip() == "":
            raise EmptyFieldError(self._('own_reference_empty_error'))
        elif input_subset.strip() == "":
            raise EmptyFieldError(self._('bestek_empty_error'))
        else:
            return True

    @staticmethod
    def change_subset(project, new_path, dialog, stacked_widget):
        time_of_alter = datetime.now().date()
        project.laatst_bewerkt = time_of_alter
        project.subset_path = Path(new_path)
        ProjectFileManager.save_project_to_dir(project)
        stacked_widget.widget(1).tab1.project = project
        dialog.close()
