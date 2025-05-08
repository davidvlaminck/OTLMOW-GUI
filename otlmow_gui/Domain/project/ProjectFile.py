from pathlib import Path

from otlmow_gui.Domain.util.Helpers import Helpers
from otlmow_gui.Domain.enums import FileState


class ProjectFile:
    """
    Represents a project file with its associated file path and state of validation.
    This class initializes a project file object with the specified file path and state,
    ensuring that the file path is stored as a Path object.

    Args:
        file_path (Path | str): The path of the project file, which can be a string or a Path object.
        state (FileState): The state of the project file.

    Attributes:
        file_path (Path): The path of the project file.
        state (FileState): The state of the project file.
    """

    def __init__(self, file_path: Path| str, state: FileState):
        if isinstance(file_path, str):
            file_path = Path(file_path)

        self.file_path: Path = file_path
        self.state: FileState = state

    def __eq__(self, __value):
        return Helpers.equal_paths(self.file_path,__value.file_path) and self.state == __value.state

