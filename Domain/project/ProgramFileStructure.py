from pathlib import Path


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

            # cls.download_fresh_otlmow_model(model_dir_path)
            # cls.get_otlmow_model_version(model_dir_path)
        return model_dir_path