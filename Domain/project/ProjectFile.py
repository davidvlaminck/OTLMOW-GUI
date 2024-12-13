from pathlib import Path

from Domain.enums import FileState


class ProjectFile:

    def __init__(self, file_path: Path| str, state: FileState):
        if isinstance(file_path, str):
            file_path = Path(file_path)

        self.file_path: Path = file_path
        self.state: FileState = state
