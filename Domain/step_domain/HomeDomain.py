from datetime import datetime
from pathlib import Path

from Domain.project.ProgramFileStructure import ProgramFileStructure
from Domain.step_domain.RelationChangeDomain import RelationChangeDomain
from Domain.project.Project import Project
from Domain.project.ProgramFileManager import ProgramFileManager
from Domain.database.SubsetDatabase import SubsetDatabase
from Domain.step_domain.TemplateDomain import TemplateDomain
from Exceptions.EmptyFieldError import EmptyFieldError
from Exceptions.WrongDatabaseError import WrongDatabaseError


class HomeDomain:

    def __init__(self, language_settings):
        self._ = language_settings

    @classmethod
    def get_all_projects(cls) -> list:
        return ProgramFileManager.get_all_otl_wizard_projects()

    @classmethod
    def remove_project(cls,project: Project, table) -> None:
        project.delete_project_dir_by_path()
        table.removeRow(table.currentRow())

    # TODO: Remove draw_table naar ergens anders
    # TODO: Rename alter_table want je past geen table aan maar de projecten
    @classmethod
    def alter_table(cls,dlg, overview_table, project: Project = None):
        time_of_alter = datetime.now().date()
        project.laatst_bewerkt = time_of_alter
        project_exists = project.project_path is not None
        if not project_exists:
            project.project_path = Path(
                ProgramFileStructure.get_otl_wizard_projects_dir() / 'Projects' / project.eigen_referentie)
        project.save_project_to_dir()
        HomeDomain.get_all_projects()
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

    @classmethod
    def change_subset(cls, project: Project, new_path, main_window) -> None:
        time_of_alter = datetime.now().date()
        project.laatst_bewerkt = time_of_alter
        if SubsetDatabase(Path(new_path)).is_valid_subset_database() is False:
            raise WrongDatabaseError("Wrong database")

        project.change_subset(Path(new_path))

        main_window.widget(1).tab1.project = project
        TemplateDomain.update_subset_information(main_window.widget(1).tab1)
        RelationChangeDomain.init_static(project)
