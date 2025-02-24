import asyncio
import logging
import os
from pathlib import Path
from typing import Optional, Iterable
import tempfile

from otlmow_model.OtlmowModel.Helpers.generated_lists import get_hardcoded_class_dict
from packaging.version import Version

from Domain.logger.OTLLogger import OTLLogger
from GUI.screens.RelationChange_elements.RelationChangeHelpers import RelationChangeHelpers


class Helpers:
    all_OTL_asset_types_dict = {}

    @classmethod
    def create_external_typeURI_options(cls):
        all_type_uris = get_hardcoded_class_dict()
        for uri, info in all_type_uris.items():
            abbr_type_uri = RelationChangeHelpers.get_abbreviated_typeURI(uri, add_namespace=True)
            screen_name = info['label']
            if "#" in abbr_type_uri:
                abbr_type_uri_split = abbr_type_uri.split("#")
                screen_name = "#".join([screen_name, abbr_type_uri_split[0]])

            cls.all_OTL_asset_types_dict[screen_name] = uri
        cls.all_OTL_asset_types_dict = Helpers.sort_nested_dict(cls.all_OTL_asset_types_dict)

    @classmethod
    def sort_nested_dict(cls, dictionary, by='keys'):
        """Recursively sorts a dictionary by keys or values."""
        if not isinstance(dictionary, dict):
            if isinstance(dictionary, list):
                return sorted(dictionary, key=lambda relation_object: relation_object.typeURI)
            return dictionary

        # Sort the current dictionary
        if by == 'keys':
            sorted_dict = {
                k: cls.sort_nested_dict(v, by=by)
                for k, v in sorted(dictionary.items())
            }

        elif by == 'values':
            sorted_dict = {
                k: cls.sort_nested_dict(v, by=by)
                for k, v in sorted(dictionary.items(), key=lambda item: item[1])
            }

        else:
            raise ValueError("Invalid sort parameter. Use 'keys' or 'values'.")

        return sorted_dict
    
    @classmethod
    def equal_paths(cls,path1: Optional[Path], path2: Optional[Path]):
        if path1 and path2:
            return path1.name == path2.name
        elif path1 or path2:
            return False
        else:
            return True



    @classmethod
    def is_version_equal_or_higher(cls, current_version:str, other_version:str) -> bool:
        res = Version(current_version) >= Version(other_version)
        OTLLogger.logger.info(f"Version comparison {current_version} >= {other_version} => {res}")
        return  res

    @classmethod
    def create_temp_path(cls, path_to_template_file_and_extension: Path) -> Path:
        """
        Creates a temporary path for storing files based on a template file.

        This method generates a temporary directory specifically for storing
        files related to the OTL project. It constructs the path using the
        name of the provided template file and ensures that the directory
        exists before returning the full path.

        :param cls: The class itself.
        :param path_to_template_file_and_extension: The path to the template file
                                                    for which the temporary path is created.
        :type path_to_template_file_and_extension: Path
        :returns: The path to the newly created temporary file location.
        :rtype: Path
        """

        tempdir = Path(tempfile.gettempdir()) / 'temp-otlmow'
        if not tempdir.exists():
            os.makedirs(tempdir)
        doc_name = Path(path_to_template_file_and_extension).name
        return Path(tempdir) / doc_name