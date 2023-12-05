from enum import Enum
from pathlib import Path


class ProjectFile:

    def __init__(self, file_path: Path, state: Enum):
        self.file_path: Path = file_path
        self.state: Enum = state
