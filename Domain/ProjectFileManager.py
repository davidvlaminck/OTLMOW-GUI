import datetime
import json
import logging
import shutil
import zipfile
from pathlib import Path

from otlmow_converter.OtlmowConverter import OtlmowConverter

from Domain.Project import Project


class ProjectFileManager:
    @classmethod
    def get_project_from_dir(cls, project_dir_path: Path) -> Project:
        if not project_dir_path.exists():
            raise FileNotFoundError(f"Project dir {project_dir_path} does not exist")

        project_details_file = project_dir_path / 'project_details.json'
        if not project_details_file.exists():
            raise FileNotFoundError(f"Project details file {project_details_file} does not exist")

        with open(project_details_file) as json_file:
            project_details = json.load(json_file)

        project = Project()
        project.project_path = project_dir_path
        project.bestek = project_details['bestek']
        project.eigen_referentie = project_details['eigen_referentie']
        project.laatst_bewerkt = datetime.datetime.strptime(project_details['laatst_bewerkt'], "%Y-%m-%d %H:%M:%S")
        project.subset_path = project_dir_path / project_details['subset']
        project.assets_path = project_dir_path / 'assets.json'

        return project

    @classmethod
    def get_otl_wizard_projects_dir(cls) -> Path:
        return Path(Path.home() / 'OTLWizardProjects')

    @classmethod
    def get_all_otl_wizard_projects(cls) -> [Project]:
        otl_wizard_project_dir = cls.get_otl_wizard_projects_dir()
        if not otl_wizard_project_dir.exists():
            return []

        project_dirs = [project_dir for project_dir in otl_wizard_project_dir.iterdir() if project_dir.is_dir()]
        projects = []
        for project_dir in project_dirs:
            try:
                project = cls.get_project_from_dir(project_dir)
                projects.append(project)
            except FileNotFoundError:
                logging.warning('Project dir %s is not a valid project directory', project_dir)
        return projects

    @classmethod
    def save_project_to_dir(cls, project: Project):
        otl_wizard_project_dir = cls.get_otl_wizard_projects_dir()
        project_dir_path = otl_wizard_project_dir / project.project_path.name
        project_dir_path.mkdir(exist_ok=True, parents=True)

        project_details_dict = {
            'bestek': project.bestek,
            'eigen_referentie': project.eigen_referentie,
            'laatst_bewerkt': project.laatst_bewerkt.strftime("%Y-%m-%d %H:%M:%S"),
            'subset': project.subset_path.name
        }

        with open(project_dir_path / "project_details.json", "w") as project_details_file:
            json.dump(project_details_dict, project_details_file)

        OtlmowConverter().create_file_from_assets(filepath=Path(project_dir_path / "assets.json"),
                                                  list_of_objects=project.assets_in_memory)

        if project.subset_path.parent.absolute() != project_dir_path.absolute():
            # move subset to project dir
            new_subset_path = project_dir_path / project.subset_path.name
            shutil.copy(project.subset_path, new_subset_path)

    @classmethod
    def export_project_to_file(cls, project: Project, file_path: Path):
        with zipfile.ZipFile(file_path, 'w') as project_zip:
            project_zip.write(project.project_path / 'project_details.json', arcname='project_details.json',
                              compresslevel=zipfile.ZIP_DEFLATED)
            project_zip.write(project.assets_path, arcname=project.assets_path.name)
            project_zip.write(project.subset_path, arcname=project.subset_path.name)

    @classmethod
    def load_project_file(cls, file_path) -> Project:
        project_dir_path = Path(file_path.parent / file_path.stem)
        project_dir_path.mkdir(exist_ok=False, parents=True)  # TODO: raise error if dir already exists?

        with zipfile.ZipFile(file_path) as project_file:
            project_file.extractall(path=project_dir_path)

        project = cls.get_project_from_dir(project_dir_path)
        return project
