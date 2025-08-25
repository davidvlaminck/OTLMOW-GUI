import importlib.metadata
import json
import os
import shutil
import tomllib
import traceback
from pathlib import Path

import toml

from otlmow_gui.Domain.ProgramFileStructure import ProgramFileStructure
from otlmow_gui.Domain.logger.OTLLogger import OTLLogger
from otlmow_gui.Domain.network.GitHubDownloader import GitHubDownloader
from otlmow_gui.Domain.util.Helpers import Helpers


class Updater:

    pyproject_filename = "pyproject.toml"
    pyproject_config = None
    needs_update = False
    github_downloader = GitHubDownloader('davidvlaminck/OTLMOW-GUI')

    local_version = None
    master_version = None

    @classmethod
    def get_project_version(cls):
        if not cls.pyproject_config:
            pyproject_path = ProgramFileStructure.get_dynamic_library_path(cls.pyproject_filename)
            cls.pyproject_config = toml.load(pyproject_path)

        return cls.pyproject_config['project']['version']

    @classmethod
    def check_for_OTL_wizard_updates(cls):
        # TODO: catch and process ratelimit exceeded error
        try:
            contents = cls.github_downloader.download_file_to_memory("pyproject.toml").decode("utf-8")
            master_pyproject_config = tomllib.loads(contents)

            cls.local_version = cls.get_project_version()
            cls.master_version = master_pyproject_config['project']['version']

            if Helpers.is_version_equal_or_higher(cls.local_version, cls.master_version):
                OTLLogger.logger.info(f"Local version {cls.local_version} is up to date with master version")
            else:
                cls.needs_update = True
                OTLLogger.logger.info(f"Update needed: Local version {cls.local_version} != {cls.master_version} master version" )
        except Exception as e:
            OTLLogger.logger.info(f"Couldn't check if new version is available for update")
            OTLLogger.logger.debug(e)

    @classmethod
    def download_fresh_otlmow_model(cls) -> Path:

        ghdl = GitHubDownloader('davidvlaminck/OTLMOW-Model')
        download_filename = 'full_repo_download.zip'
        temp_download_dest_path = Helpers.create_temp_path(path_to_template_file_and_extension=Path(download_filename))
        temp_base_dir_path = Helpers.get_base_temp_dir_path()

        ghdl.download_full_repo(temp_download_dest_path)

        unzip_dir_path = temp_base_dir_path / 'downloaded_model'
        if unzip_dir_path.exists():
            shutil.rmtree(unzip_dir_path)

        OTLLogger.logger.info(f"unpack downloaded otlmow-model to {unzip_dir_path}",extra={"timing_ref":"unpack_otlmow_model"} )
        shutil.unpack_archive(temp_download_dest_path,
                              unzip_dir_path)
        OTLLogger.logger.info("unpack downloaded otlmow-model", extra={"timing_ref":"unpack_otlmow_model"} )


        return unzip_dir_path

    @classmethod
    def get_otlmow_model_version(cls) -> str:
        ghdl = GitHubDownloader('davidvlaminck/OTLMOW-Model')
        # ghdl.download_file_to_dir(file_path='otlmow_model/version_info.json',
        #                           destination_dir=model_dir_path / 'temp')
        # with open(model_dir_path / 'temp' / 'version_info.json') as json_file:
        #     version_info = json.load(json_file)
        contents = ghdl.download_file_to_memory("otlmow_model/version_info.json").decode("utf-8")
        version_info = json.loads(contents)
        print(f"version info {version_info}")
        if not isinstance(version_info,dict):
            return ""

        try:
            model_version = version_info["current"]['model_version']
        except:
            model_version = ""

        OTLLogger.logger.info(f"online otlmow-model version: {model_version}")
        return model_version

    @classmethod
    def update_oltmow_model(cls, model_dir_path=None):
        OTLLogger.logger.info(
            "Checking for new otlmow-model versions to update to")

        library_name = "otlmow_model"
        otlmow_model_lib_path = ProgramFileStructure.get_dynamic_library_path(library_name)

        if not otlmow_model_lib_path.exists():
            OTLLogger.logger.info("No otlmow-model library directory found to update! are you in testing environment?")
            return
        try:
            local_model_version = cls.get_local_otl_model_library_version()
            online_model_version = cls.get_otlmow_model_version()

            if  (local_model_version and online_model_version and
                    Helpers.is_version_equal_or_higher(local_model_version, online_model_version)):
                OTLLogger.logger.info("otlmow-model is uptodate")
                return

            try:

                OTLLogger.logger.info("Updating otlmow-model", extra={"timing_ref": "update_otlmow_model"})
                unzip_dir_path = cls.download_fresh_otlmow_model()

                files_in_unzip_dir_path_list = os.listdir(unzip_dir_path)
                if files_in_unzip_dir_path_list:

                    new_otlmow_model_dir_path = unzip_dir_path/ files_in_unzip_dir_path_list[0] / 'otlmow_model'

                    # replace old otlmow_model folder in application site_packages with new otlmow_model
                    OTLLogger.logger.info(
                        f"Replacing old otlmow_model folder at: {otlmow_model_lib_path}", extra={"timing_ref": "replace_otl_model"})
                    if otlmow_model_lib_path.exists():
                        shutil.rmtree(otlmow_model_lib_path)

                    shutil.copytree(new_otlmow_model_dir_path,otlmow_model_lib_path)
                    OTLLogger.logger.info(
                        "Replaced old otlmow_model folder", extra={"timing_ref": "replace_otl_model"})
                    OTLLogger.logger.info("Updated otlmow-model",
                                          extra={"timing_ref": "update_otlmow_model"})
                    return

                OTLLogger.logger.info("FAILED Updating otlmow-model", extra={"timing_ref": "update_otlmow_model"})
            except Exception as e:
                OTLLogger.logger.info("FAILED Updating otlmow-model",
                                      extra={"timing_ref": "update_otlmow_model"})
                OTLLogger.logger.error("".join(traceback.format_exception(e)))

        except Exception as e:
            OTLLogger.logger.info("FAILED determining if local otlmow-model library is out of date (probably connection issue)")
            OTLLogger.logger.error("".join(traceback.format_exception(e)))
    @classmethod
    async def async_get_local_otl_model_library_version(cls):

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

    @classmethod
    def get_local_otl_model_library_version(cls):

        # first if there is a version file in the otlmow-model library itself
        # this is there if the model was downloaded from github
        library_name = "otlmow_model"
        otlmow_model_lib_path = ProgramFileStructure.get_dynamic_library_path(library_name)
        otlmow_model_lib_version_file_path = otlmow_model_lib_path / "version_info.json"

        if otlmow_model_lib_version_file_path.exists():
            with open(otlmow_model_lib_version_file_path) as version_file:
                otl_version_dict = json.load(version_file)
                otl_model_version = otl_version_dict["current"]["model_version"]
                OTLLogger.logger.info(
                    f"the model was downloaded from github {otl_model_version}")
        else:

            # second go off the metadata from the pip install
            metadata = importlib.metadata.metadata("otlmow-model")
            otl_model_version = metadata['Version']
            OTLLogger.logger.info(f"checked second go off the metadata from the pip install {otl_model_version}")
        return otl_model_version