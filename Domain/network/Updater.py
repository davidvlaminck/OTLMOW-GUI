import json
import logging
import os
import shutil
import sys
import tomllib
from pathlib import Path

import toml

from Domain.network.GitHubDownloader import GitHubDownloader


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

    @classmethod
    def download_fresh_otlmow_model(cls, model_dir_path) -> None:

        ghdl = GitHubDownloader('davidvlaminck/OTLMOW-Model')
        ghdl.download_full_repo(model_dir_path / 'temp')
        shutil.unpack_archive(model_dir_path / 'temp' / 'full_repo_download.zip',
                              model_dir_path / 'temp' / 'downloaded_model')

    @classmethod
    def get_otlmow_model_version(cls, model_dir_path) -> str:
        ghdl = GitHubDownloader('davidvlaminck/OTLMOW-Model')
        ghdl.download_file_to_dir(file_path='otlmow_model/version_info.json',
                                  destination_dir=model_dir_path / 'temp')
        with open(model_dir_path / 'temp' / 'version_info.json') as json_file:
            version_info = json.load(json_file)

        return version_info['model_version']