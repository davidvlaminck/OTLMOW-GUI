import datetime
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
