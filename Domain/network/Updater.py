import importlib.metadata
import json
import logging
import os
import shutil
import sys
import tomllib
from pathlib import Path

import toml

from Domain.ProgramFileStructure import ProgramFileStructure
from Domain.logger.OTLLogger import OTLLogger
from Domain.network.GitHubDownloader import GitHubDownloader
from Domain.util.Helpers import Helpers


class Updater:

    pyproject_filename = "pyproject.toml"
    pyproject_config = None
    needs_update = False
    github_downloader = GitHubDownloader('davidvlaminck/OTLMOW-GUI')

    local_version = None
    master_version = None

    @classmethod
    def check_for_OTL_wizard_updates(cls):

        pyproject_path = ProgramFileStructure.get_dynamic_library_path(cls.pyproject_filename)
        cls.pyproject_config = toml.load(pyproject_path)

        # TODO: catch and process ratelimit exceeded error
        try:
            contents = cls.github_downloader.download_file_to_memory("pyproject.toml").decode("utf-8")
            master_pyproject_config = tomllib.loads(contents)

            cls.local_version = cls.pyproject_config['project']['version']
            cls.master_version = master_pyproject_config['project']['version']

            if Helpers.is_version_equal_or_higher(cls.local_version, cls.master_version):
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

    @classmethod
    def update_oltmow_model(cls):


        library_name = "otlmow_model"
        otlmow_model_lib_path = ProgramFileStructure.get_dynamic_library_path(library_name)

    @classmethod
    async def get_local_otl_model_library_version(cls):

        # first if there is a version file in the otlmow-model library itself
        # this is there if the model was downloaded from github
        library_name = "otlmow_model"
        otlmow_model_lib_path = ProgramFileStructure.get_dynamic_library_path(library_name)
        otlmow_model_lib_version_file_path = otlmow_model_lib_path / "version_info.json"

        if otlmow_model_lib_version_file_path.exists():
            with open(otlmow_model_lib_version_file_path) as version_file:
                otl_version_dict = json.load(version_file)
                otl_model_version = otl_version_dict["current"]["model_version"]
        else:

            # second go off the metadata from the pip install
            metadata = importlib.metadata.metadata("otlmow-model")
            otl_model_version = metadata['Version']
        return otl_model_version