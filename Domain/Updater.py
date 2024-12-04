import logging
import os
import sys
import tomllib
from pathlib import Path

import toml

from Domain.GitHubDownloader import GitHubDownloader


class Updater:

    pyproject_filename = "pyproject.toml"
    pyproject_config = None
    needs_update = False
    github_downloader = GitHubDownloader('davidvlaminck/OTLMOW-GUI')

    local_version = None
    master_version = None

    @classmethod
    def check_for_updates(cls):

        pyproject_path = Path(f'{cls.pyproject_filename}')

        if hasattr(sys, '_MEIPASS'):  # when in .exe file
            pyproject_path = Path(os.path.join(sys._MEIPASS, f'{cls.pyproject_filename}'))
        elif not pyproject_path.exists():
            pyproject_path = Path(f'data/{cls.pyproject_filename}')

        cls.pyproject_config = toml.load(pyproject_path)

        # TODO: catch and process ratelimit exceeded error
        try:
            contents = cls.github_downloader.download_file_to_memory("pyproject.toml").decode("utf-8")
            master_pyproject_config = tomllib.loads(contents)

            cls.local_version = cls.pyproject_config['project']['version']
            cls.master_version = master_pyproject_config['project']['version']

            if cls.local_version == cls.master_version:
                logging.info(f"Local version {cls.local_version} is up to date with master version")
            else:
                cls.needs_update = True
                logging.info(f"Update needed: Local version {cls.local_version} != {cls.master_version} master version" )
        except Exception as e:
            logging.info(f"Couldn't check if new version is available for update")
            logging.debug(e)