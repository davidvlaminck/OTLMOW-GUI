from datetime import datetime
from pathlib import Path

from Domain.RelationChangeDomain import RelationChangeDomain
from Domain.Project import Project
from Domain.ProjectFileManager import ProjectFileManager
from Domain.SubsetDatabase import SubsetDatabase
from Domain.TemplateDomain import TemplateDomain
from Exceptions.EmptyFieldError import EmptyFieldError
from Exceptions.WrongDatabaseError import WrongDatabaseError


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
        if not project_exists:
            project.project_path = Path(
                ProjectFileManager.get_otl_wizard_projects_dir() / 'Projects' / project.eigen_referentie)
        ProjectFileManager.save_project_to_dir(project)
        ProjectFileManager.load_projects_into_global()
        overview_table.draw_table()
        dlg.close()

    def validate(self, input_eigen_ref: str, input_subset: str, db_path: str) -> bool:
        if not input_eigen_ref.strip():
            raise EmptyFieldError(self._('own_reference_empty_error'))
        elif not input_subset.strip():
            raise EmptyFieldError(self._('bestek_empty_error'))
        elif not db_path.strip():
            raise EmptyFieldError(self._('db_path_empty_error'))
        elif SubsetDatabase(Path(db_path)).is_valid_subset_database() is False:
            raise WrongDatabaseError(self._('wrong_database_error'))
        else:
            return True

    @staticmethod
    def change_subset(project: Project, new_path, main_window) -> None:
        time_of_alter = datetime.now().date()
        project.laatst_bewerkt = time_of_alter
        if SubsetDatabase(Path(new_path)).is_valid_subset_database() is False:
            raise WrongDatabaseError("Wrong database")
        project.change_subset(Path(new_path))
        ProjectFileManager.save_project_to_dir(project)
        main_window.widget(1).tab1.project = project
        TemplateDomain.update_subset_information(main_window.widget(1).tab1)
        RelationChangeDomain.init_static(project)
