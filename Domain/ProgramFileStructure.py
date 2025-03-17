from pathlib import Path
import sys


class ProgramFileStructure:
    @classmethod
    def get_home_path(cls) -> Path:
        return Path.home()


    @classmethod
    def get_otl_wizard_work_dir(cls) -> Path:
        work_dir_path = cls.get_home_path() / 'OTLWizardProjects'
        if not work_dir_path.exists():
            work_dir_path.mkdir()
        return work_dir_path


    @classmethod
    def get_otl_wizard_projects_dir(cls) -> Path:
        projects_dir_path = cls.get_otl_wizard_work_dir() / 'Projects'
        if not projects_dir_path.exists():
            projects_dir_path.mkdir()
        return projects_dir_path

    @classmethod
    def get_otl_wizard_model_dir(cls) -> Path:
        model_dir_path = cls.get_otl_wizard_work_dir() / 'Model'
        if not model_dir_path.exists():
            model_dir_path.mkdir()

        return model_dir_path

    @classmethod
    def get_dynamic_library_path(cls, library_name: str) -> Path:
        dynamic_library_path = Path(library_name)
        if hasattr(sys, '_MEIPASS'):  # when in .exe file
            dynamic_library_path = Path(sys._MEIPASS, library_name)
        elif not dynamic_library_path.exists():
            dynamic_library_path = Path('data', library_name)

        return dynamic_library_path