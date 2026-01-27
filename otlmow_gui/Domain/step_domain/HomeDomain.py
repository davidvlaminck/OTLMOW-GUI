from pathlib import Path

from otlmow_gui.Domain import global_vars
from otlmow_gui.Domain.logger.OTLLogger import OTLLogger
from otlmow_gui.Domain.project.Project import Project
from otlmow_gui.Domain.ProgramFileStructure import ProgramFileStructure
from otlmow_gui.Domain.database.SubsetDatabase import SubsetDatabase
from otlmow_gui.Domain.step_domain.ExportFilteredDataSubDomain import ExportFilteredDataSubDomain
from otlmow_gui.Domain.step_domain.InsertDataDomain import InsertDataDomain
from otlmow_gui.Domain.step_domain.RelationChangeDomain import RelationChangeDomain
from otlmow_gui.Domain.step_domain.TemplateDomain import TemplateDomain
from otlmow_gui.Exceptions.EmptyFieldError import EmptyFieldError
from otlmow_gui.Exceptions.NotASqlliteFileError import NotASqlliteFileError
from otlmow_gui.Exceptions.WrongDatabaseError import WrongDatabaseError
from otlmow_gui.GUI.dialog_windows.ProjectExistsError import ProjectExistsError
from otlmow_gui.GUI.screens.Screen import Screen
from otlmow_gui.GUI.screens.screen_interface.HomeScreenInterface import HomeScreenInterface

from otlmow_gui.GUI.translation.GlobalTranslate import GlobalTranslate


class HomeDomain:

    projects = {}

    @classmethod
    def init_static(cls, home_screen: HomeScreenInterface):
        cls.projects = cls.get_all_otl_wizard_projects()
        cls.update_frontend(screen=home_screen)

    @classmethod
    def get_all_otl_wizard_projects(cls) -> [Project]:
        """
        Retrieves all OTL wizard projects from the designated projects directory.

        This class method scans the directory for valid project directories,
        attempts to load each project, and collects them into a list,
        logging any directories that are not valid projects.

        :return: A list of loaded Project instances.
        :rtype: list[Project]

        :raises FileNotFoundError: If a project directory cannot be loaded due to missing files.
        """
        OTLLogger.logger.info(f"Execute HomeDomain.get_all_otl_wizard_projects",
                              extra={"timing_ref": f"get_all_otl_wizard_projects"})
        otl_wizard_project_dir = ProgramFileStructure.get_otl_wizard_projects_dir()

        project_dirs = [project_dir for project_dir in otl_wizard_project_dir.iterdir() if
                        project_dir.is_dir()]
        projects = {}
        for project_dir in project_dirs:
            try:
                project = Project.load_project(project_path=project_dir)
                projects[project.eigen_referentie] = project
            except FileNotFoundError:
                OTLLogger.logger.warning('Project dir %s is not a valid project directory', project_dir)

        project_count = len(projects)
        OTLLogger.logger.info(f"Execute HomeDomain.get_all_otl_wizard_projects ({project_count} projects)",
                              extra={"timing_ref": f"get_all_otl_wizard_projects"})

        return projects


    @classmethod
    def remove_project(cls, project: Project) -> None:
        """
        Removes a specified project and updates the project list in the frontend.

        This class method deletes the project's directory and refreshes the project data
        displayed to the user.

        :param project: The project instance to be removed.
        :type project: Project

        :return: None
        """

        project.delete_project_dir_by_path()
        cls.reload_projects()
        cls.update_frontend()

    @classmethod
    def validate(cls, input_eigen_ref: str, input_subset: str, db_path: str) -> bool:
        """
        Validates the input parameters for the operation. This class method checks that the
        provided eigen reference, subset, and database path are not empty and that the database
        path points to a valid subset database.

        The method raises specific errors if any of the input fields are empty or if the database
        path is invalid. If all checks pass, it returns True, indicating that the inputs are valid.

        :param input_eigen_ref: The eigen reference input to validate.
        :type input_eigen_ref: str
        :param input_subset: The subset input to validate.
        :type input_subset: str
        :param db_path: The path to the database to validate.
        :type db_path: str

        :return: True if all inputs are valid.
        :rtype: bool

        :raises EmptyFieldError: If any of the input fields are empty.
        :raises WrongDatabaseError: If the database path does not point to a valid subset database.
        """
        try:
            subset_db = SubsetDatabase(db_path=Path(db_path))
            is_valid_subset = subset_db.is_valid_subset_database()
            subset_db.close_connection()
        except NotASqlliteFileError:
            is_valid_subset = False

        if not input_eigen_ref.strip():
            raise EmptyFieldError(GlobalTranslate._('own_reference_empty_error'))
        elif not input_subset.strip():
            raise EmptyFieldError(GlobalTranslate._('bestek_empty_error'))
        elif not db_path.strip():
            raise EmptyFieldError(GlobalTranslate._('db_path_empty_error'))
        elif is_valid_subset is False:
            raise WrongDatabaseError(GlobalTranslate._('wrong_database_error'))
        else:
            return True

    @classmethod
    def change_subset(cls, new_path) -> None:
        """
        Changes the subset of a specified project and updates the associated UI components.
        This class method updates the project's last modified date, validates the new subset path,
         and refreshes the relevant information in the main window.

        The method first checks if the new subset path points to a valid database.
        If valid, it updates the project's subset and refreshes the UI to reflect the changes.

        :param project: The project instance whose subset is to be changed.
        :type project: Project
        :param new_path: The new path for the subset.
        :type new_path: str
        :param main_window: The main window instance to update the UI.
        :type main_window: QWidget

        :return: None

        :raises WrongDatabaseError: If the new path does not point to a valid subset database.
        """

        project = global_vars.current_project
        main_window = global_vars.otl_wizard.main_window

        if SubsetDatabase(db_path=Path(new_path)).is_valid_subset_database() is False:
            raise WrongDatabaseError("Wrong database")

        project.change_subset(new_path=Path(new_path))

        TemplateDomain.init_static()
        RelationChangeDomain.clear_data()
        RelationChangeDomain.init_static(project=project)

        main_window.reset_ui(GlobalTranslate._)

    @classmethod
    def get_screen(cls) -> HomeScreenInterface:
        return global_vars.otl_wizard.main_window.home_screen

    @classmethod
    def update_frontend(cls,screen: HomeScreenInterface = None)  -> None:
        """
        Updates the frontend display with the current list of projects.
        This class method fills the specified screen's table with project data, or
        defaults to the main screen if no screen is provided.

        The method checks if a specific screen is passed as an argument; if so, it updates that
        screen. Otherwise, it retrieves the main screen and updates it with the current projects.

        :param screen: The screen instance to update. If None, the main screen will be updated.
        :type screen: Screen or None

        :return: None
        """
        if screen:
            screen.fill_table(projects=cls.projects)
        else:
            cls.get_screen().fill_table(projects=cls.projects)

    @classmethod
    def open_project(cls, project_ref:str)  -> None:
        """
        Opens a specified project and prepares the application to work with it.

        This class method retrieves the project reference, sets it as the current project
        and loads any associated document filenames. It also updates the main window to reflect
        the selected project and initiates the process of filling the relevant UI components
        asynchronously.

        :param project_ref: The reference identifier for the project to be opened.
        :type project_ref: str

        :return: None
        """

        selected_project = cls.projects[project_ref]
        global_vars.current_project = selected_project

        global_vars.otl_wizard.main_window.go_to_project()

        selected_project.load_saved_document_filenames()

        TemplateDomain.init_static()
        InsertDataDomain.init_static()
        # RelationChangeDomain.clear_data()
        RelationChangeDomain.init_static(project=selected_project)
        ExportFilteredDataSubDomain.clear_data()
        global_vars.otl_wizard.main_window.step3_visuals.changed_project_bool = True

        global_vars.otl_wizard.main_window.enable_steps()



    @classmethod
    def process_upsert_dialog_input(cls, input_bestek: str, input_eigen_ref: str,
                                    input_subset: str, project: Project = None) -> None:
        """
        Processes input from the upsert dialog to create or update a project.

        This class method takes user input for project details and either creates a new project or
        updates an existing one based on the provided information. It then reloads the project list
        and updates the frontend to reflect the changes.

        :param input_bestek: The bestek input for the project.
        :type input_bestek: str
        :param input_eigen_ref: The eigen reference input for the project.
        :type input_eigen_ref: str
        :param input_subset: The subset input for the project.
        :type input_subset: str
        :param project: An optional Project instance to update. If None, a new project will be
        created.
        :type project: Project, optional

        :return: None
        """

        if project is None:
            project = cls.create_and_add_project(eigen_ref=input_eigen_ref,
                                       bestek=input_bestek,
                                       subset_path=Path(input_subset))
        else:
            project.update_information(new_eigen_ref=input_eigen_ref,
                                       new_bestek=input_bestek,
                                       new_subset_path=Path(input_subset))

        global_vars.otl_wizard.main_window.home_screen.last_added_ref = project.eigen_referentie
        cls.reload_projects()
        cls.update_frontend()

    @classmethod
    def create_and_add_project(cls, eigen_ref: str, bestek: str, subset_path: Path) -> Project:
        """
        Creates a new project and adds it to the project list.

        This class method initializes a Project instance with the provided eigen reference,
        bestek, and subset path, then saves the project to the designated directory. The newly
        created project is also added to the class's project collection for future reference.

        :param eigen_ref: The eigen reference for the new project.
        :type eigen_ref: str
        :param bestek: The bestek associated with the new project.
        :type bestek: str
        :param subset_path: The path to the subset for the new project.
        :type subset_path: Path

        :return: None
        """

        project = Project(eigen_referentie=eigen_ref, subset_path=subset_path, bestek=bestek)

        project_dir_path = project.get_project_local_path()
        if  project_dir_path.exists():
            OTLLogger.logger.error("Project dir %s already exists", project_dir_path)
            raise ProjectExistsError(eigen_referentie=project.eigen_referentie)

        cls.projects[eigen_ref] = project
        project.save_project_to_dir()

        return project

    @classmethod
    def reload_projects(cls) -> None:
        """
        Reloads the list of projects from the OTL wizard.

        This class method retrieves the current projects by calling a method that fetches all
        OTL wizard projects from disk storage and updates the class's project collection
        ccordingly.

        :return: None
        """

        cls.projects = cls.get_all_otl_wizard_projects()