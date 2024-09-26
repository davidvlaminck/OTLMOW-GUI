import datetime
import json
from pathlib import Path


class Project:
    def __init__(self, project_path: Path = None, subset_path: Path = None, assets_path: Path = None,
                 eigen_referentie: str = None, bestek: str = None, laatst_bewerkt: datetime.datetime = None):
        self.project_path: Path = project_path
        self.subset_path: Path = subset_path
        self.assets_path: Path = assets_path
        self.eigen_referentie: str = eigen_referentie
        self.bestek: str = bestek
        self.laatst_bewerkt: datetime.datetime = laatst_bewerkt

        self.assets_in_memory = []
        self.files_in_memory = []
        self.templates_in_memory = []

    @classmethod
    def load_project(cls, project_path: Path = None):
        if not project_path.exists():
            raise FileNotFoundError(f"Project dir {project_path} does not exist")

        project_details_file = project_path / 'project_details.json'
        if not project_details_file.exists():
            raise FileNotFoundError(f"Project details file {project_details_file} does not exist")

        with open(project_details_file) as json_file:
            project_details = json.load(json_file)

        return cls(project_path,
                   project_path / project_details['subset'],
                   project_path / 'assets.json',
                   project_details['eigen_referentie'],
                   project_details['bestek'],
                   datetime.datetime.strptime(project_details['laatst_bewerkt'], "%Y-%m-%d %H:%M:%S"))