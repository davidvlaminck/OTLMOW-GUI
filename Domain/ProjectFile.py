from pathlib import Path

from Domain.enums import FileState


class ProjectFile:

    def __init__(self, file_path: Path, state: FileState):
        self.file_path: Path = file_path
        self.state: FileState = state
