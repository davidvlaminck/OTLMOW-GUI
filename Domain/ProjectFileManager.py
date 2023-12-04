import datetime
import json
import logging
import ntpath
import os
import shutil
import zipfile
from pathlib import Path

from otlmow_converter.OtlmowConverter import OtlmowConverter

from Domain import global_vars
from Domain.GitHubDownloader import GitHubDownloader
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

    @classmethod
    def get_all_otl_wizard_projects(cls) -> [Project]:
        otl_wizard_project_dir = cls.get_otl_wizard_projects_dir()

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
        logging.debug("Saving project to %s", project_dir_path)
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
        global_vars.projects = cls.get_all_otl_wizard_projects()

    @classmethod
    def export_project_to_file(cls, project: Project, file_path: Path):
        with zipfile.ZipFile(file_path, 'w') as project_zip:
            project_zip.write(project.project_path / 'project_details.json', arcname='project_details.json',
                              compresslevel=zipfile.ZIP_DEFLATED)
            project_zip.write(project.assets_path, arcname=project.assets_path.name)
            project_zip.write(project.subset_path, arcname=project.subset_path.name)

    @classmethod
    def add_template_files_to_file(cls, project: Project, ):
        otl_wizard_project_dir = cls.get_otl_wizard_projects_dir()
        object_array = []
        for template in project.templates_in_memory:
            template_details = {
                'file_path': str(template.file_path),
                'state': template.state.name
            }
            object_array.append(template_details)
        project_dir_path = otl_wizard_project_dir / project.project_path.name
        with open(project_dir_path / "assets.json", "w") as project_details_file:
            json.dump(object_array, project_details_file)

    @classmethod
    def get_templates_in_memory(cls, project: Project):
        with open(project.project_path / "assets.json", "r") as project_details_file:
            templates = json.load(project_details_file)
        project.templates_in_memory = templates

    @classmethod
    def load_project_file(cls, file_path) -> Project:
        project_dir_path = Path(cls.get_otl_wizard_projects_dir() / file_path.stem)
        try:
            project_dir_path.mkdir(exist_ok=False, parents=True)  # TODO: raise error if dir already exists?
        except FileExistsError as ex:
            logging.error("Project dir %s already exists", project_dir_path)
            raise ex

        with zipfile.ZipFile(file_path) as project_file:
            project_file.extractall(path=project_dir_path)

        project = cls.get_project_from_dir(project_dir_path)
        cls.get_templates_in_memory(project)
        return project

    @classmethod
    def delete_project_files_by_path(cls, file_path: Path):
        logging.debug("Deleting project %s", file_path)
        shutil.rmtree(file_path)
        global_vars.projects = cls.get_all_otl_wizard_projects()

    @classmethod
    def load_projects_into_global(cls):
        global_vars.projects = ProjectFileManager.get_all_otl_wizard_projects()

    @classmethod
    def download_fresh_otlmow_model(cls, model_dir_path):
        ghdl = GitHubDownloader('davidvlaminck/OTLMOW-Model')
        ghdl.download_full_repo(model_dir_path / 'temp')
        shutil.unpack_archive(model_dir_path / 'temp' / 'full_repo_download.zip',
                              model_dir_path / 'temp' / 'downloaded_model')

    @classmethod
    def get_otlmow_model_version(cls, model_dir_path) -> str:
        ghdl = GitHubDownloader('davidvlaminck/OTLMOW-Model')
        ghdl.download_file(destination_dir=model_dir_path / 'temp', file_path='otlmow_model/version_info.json')
        with open(model_dir_path / 'temp' / 'version_info.json') as json_file:
            version_info = json.load(json_file)

        return version_info['model_version']

    @classmethod
    def add_template_file_to_project(cls, filepath: Path):
        project = global_vars.single_project
        location_dir = project.project_path / 'OTL-template-files'
        if not location_dir.exists():
            location_dir.mkdir()
        doc_name = filepath.name
        end_location = location_dir / doc_name
        if end_location == filepath:
            return end_location
        shutil.copy(filepath, end_location)
        logging.debug("file manager" + str(end_location))
        return end_location

    @classmethod
    def template_map_exists(cls):
        if global_vars.single_project is None:
            return False
        project = global_vars.single_project
        location_dir = project.project_path / 'OTL-template-files'
        return location_dir.exists()

    @classmethod
    def delete_template_folder(cls):
        project = global_vars.single_project
        location_dir = project.project_path / 'OTL-template-files'
        if not location_dir.exists():
            return
        shutil.rmtree(location_dir)
