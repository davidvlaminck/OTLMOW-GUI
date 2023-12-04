import json
import logging
import os
import shutil
from pathlib import Path

import requests

from Domain.GitHubDownloader import GitHubDownloader
from Domain.ProjectFileManager import ProjectFileManager


class ModelManager:
    @classmethod
    def get_valid_model_if_needed(cls):
        model_dir_path = ProjectFileManager.get_otl_wizard_model_dir()
        try:
            if not model_dir_path.exists():
                logging.debug("No model found, downloading fresh model")
                cls.download_fresh_otlmow_model(model_dir_path)
                return

            if not (model_dir_path / 'version_info.json').exists():
                logging.debug("No model version info found, downloading fresh model")
                cls.download_fresh_otlmow_model(model_dir_path)
                return

            current_model_version = cls.get_package_otlmow_model_version(model_dir_path)
            local_model_version = cls.get_local_otlmow_model_version(model_dir_path)
            if current_model_version != local_model_version:
                logging.debug("Local model is outdated, downloading fresh model")
                cls.download_fresh_otlmow_model(model_dir_path)
            else:
                logging.debug(f'Current model is up to date (version: {current_model_version})')
        except requests.Timeout as e:
            logging.debug('Timeout while getting valid model. Are you connected to the internet and is it working?')
            logging.error(e)
            raise e
        except Exception as e:
            logging.debug('Error while getting valid model')
            logging.error(e)
            raise e

    @classmethod
    def download_fresh_otlmow_model(cls, model_dir_path: Path) -> None:
        logging.debug("Downloading fresh OTLMOW model")

        shutil.rmtree(model_dir_path)
        ghdl = GitHubDownloader('davidvlaminck/OTLMOW-Model')
        ghdl.download_full_repo(model_dir_path / 'temp')
        shutil.unpack_archive(filename=model_dir_path / 'temp' / 'full_repo_download.zip',
                              extract_dir=model_dir_path / 'temp' / 'downloaded_model')
        downloaded_model_path = model_dir_path / 'temp' / 'downloaded_model'
        child_dir_name = next(os.walk(downloaded_model_path))[1][0]
        otlmow_model_temp_dir = downloaded_model_path / child_dir_name / 'otlmow_model'

        shutil.move(src=otlmow_model_temp_dir / 'version_info.json',
                    dst=model_dir_path / 'version_info.json')
        shutil.move(src=otlmow_model_temp_dir / 'OtlmowModel' / 'Classes',
                    dst=model_dir_path / 'OtlmowModel' / 'Classes')
        shutil.move(src=otlmow_model_temp_dir / 'OtlmowModel' / 'Datatypes',
                    dst=model_dir_path / 'OtlmowModel' / 'Datatypes')
        shutil.rmtree(model_dir_path / 'temp')

        logging.debug("Finished fresh OTLMOW model")

    @classmethod
    def get_package_otlmow_model_version(cls, model_dir_path: Path) -> str:
        ghdl = GitHubDownloader('davidvlaminck/OTLMOW-Model')
        ghdl.download_file(destination_dir=model_dir_path / 'temp', file_path='otlmow_model/version_info.json')
        with open(model_dir_path / 'temp' / 'version_info.json') as json_file:
            version_info = json.load(json_file)
        shutil.rmtree(model_dir_path / 'temp')

        return version_info['model_version']

    @classmethod
    def get_local_otlmow_model_version(cls, model_dir_path: Path) -> str:
        with open(model_dir_path / 'version_info.json') as json_file:
            version_info = json.load(json_file)

        return version_info['model_version']
