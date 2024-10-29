import datetime
import json
from pathlib import Path
from typing import Optional


class Project:
    def __init__(self, project_path: Path = None, subset_path: Path = None, assets_path: Path = None,
                 eigen_referentie: str = None, bestek: str = None, laatst_bewerkt: datetime.datetime = None,
                 last_quick_save:Optional[Path] = None):
        self.project_path: Path = project_path
        self.subset_path: Path = subset_path
        self.assets_path: Path = assets_path
        self.last_quick_save:Path = last_quick_save
        self.eigen_referentie: str = eigen_referentie
        self.bestek: str = bestek
        self.laatst_bewerkt: datetime.datetime = laatst_bewerkt

        self.assets_in_memory = [] #TODO: implement mechanisms to store, save and load validated assets
        self.saved_project_files = []

    @classmethod
    def load_project(cls, project_path: Path = None):
        if not project_path.exists():
            raise FileNotFoundError(f"Project dir {project_path} does not exist")

        project_details_file = project_path / 'project_details.json'
        if not project_details_file.exists():
            raise FileNotFoundError(f"Project details file {project_details_file} does not exist")

        with open(project_details_file) as json_file:
            project_details = json.load(json_file)

        if 'last_quick_save' not in project_details :
            last_quick_save = None
        else:
            last_quick_save = Path(project_details['last_quick_save'])


        return cls(project_path,
                   project_path / project_details['subset'],
                   project_path / 'assets.json',
                   project_details['eigen_referentie'],
                   project_details['bestek'],
                   datetime.datetime.strptime(project_details['laatst_bewerkt'], "%Y-%m-%d %H:%M:%S"),
                   last_quick_save)

    def is_in_project(self, file_path):
        return [project_file.file_path for project_file in self.saved_project_files].__contains__(file_path)

