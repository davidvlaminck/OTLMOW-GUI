import logging
import os
import tempfile
from pathlib import Path

from Domain import global_vars
from Domain.Settings import Settings
from Domain.project.ProgramFileStructure import ProgramFileStructure
from Domain.project.Project import Project


class ProgramFileManager:
    """
        Manager to manage OTL projects files on local computer
    """

    @classmethod
    def create_empty_temporary_map(cls) -> Path:
        """
        Creates an empty temporary directory for storing files.

        This class method checks for the existence of a specific temporary directory and creates it
        if it does not exist. It also removes any existing files within the directory before
        returning the path to the temporary directory.

        :return: The path to the temporary directory.
        :rtype: Path
        """

        tempdir = Path(tempfile.gettempdir()) / 'temp-otlmow'
        tempdir_str = str(tempdir)
        logging.debug(f"tempdir {tempdir_str}")
        if not tempdir.exists():
            os.makedirs(tempdir)
        [f.unlink() for f in Path(tempdir).glob("*") if f.is_file()]
        return tempdir
