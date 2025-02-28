import asyncio
import logging
import os
from pathlib import Path
from typing import Optional, Iterable
import tempfile

from otlmow_converter.Exceptions.ExceptionsGroup import ExceptionsGroup
from otlmow_converter.OtlmowConverter import OtlmowConverter
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject
from otlmow_model.OtlmowModel.Helpers.generated_lists import get_hardcoded_class_dict
from packaging.version import Version
from universalasync import async_to_sync_wraps

from Domain.logger.OTLLogger import OTLLogger
from GUI.dialog_windows.LoadingImageWindow import add_loading_screen
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
    @async_to_sync_wraps
    async def converter_from_file_to_object(cls,file_path,**kwargs):

        OTLLogger.logger.debug(f"Execute OtlmowConverter.from_file_to_objects({file_path.name})",
                               extra={"timing_ref": f"file_to_objects_{file_path.stem}"})
        exception_group = None
        object_count = 0
        try:
            object_lists = list(await OtlmowConverter.from_file_to_objects(file_path,**kwargs))
        except ExceptionsGroup as group:
            exception_group = group
            object_lists = group.objects

        object_count = len(object_lists)
        OTLLogger.logger.debug(f"Execute OtlmowConverter.from_file_to_objects({file_path.name}) ({object_count} objects)",
                               extra={"timing_ref": f"file_to_objects_{file_path.stem}"})
        return object_lists,exception_group

    @classmethod
    def start_async_converter_from_object_to_file(cls, file_path: Path,
                                            sequence_of_objects: Iterable[OTLObject],
                                            synchronous: bool=False,**kwargs) -> None:

        if not synchronous:
            event_loop = asyncio.get_event_loop()
            event_loop.create_task(Helpers.converter_from_object_to_file(file_path=file_path,sequence_of_objects=sequence_of_objects,**kwargs))
        else:
            Helpers.converter_from_object_to_file(file_path=file_path,
                                                  sequence_of_objects=sequence_of_objects,
                                                  **kwargs)

    @classmethod
    @async_to_sync_wraps
    @add_loading_screen
    async def converter_from_object_to_file(cls, file_path: Path, sequence_of_objects: Iterable[OTLObject], **kwargs) -> None:
        OTLLogger.logger.debug(f"Execute OtlmowConverter.from_objects_to_file({file_path.name})",
                               extra={"timing_ref": f"sequence_of_objects_{file_path.stem}"})
        await OtlmowConverter.from_objects_to_file(file_path=file_path,
                                             sequence_of_objects=sequence_of_objects,
                                             **kwargs)
        object_count = len(list(sequence_of_objects))
        OTLLogger.logger.debug(
            f"Execute OtlmowConverter.from_objects_to_file({file_path.name}) ({object_count} objects)",
            extra={"timing_ref": f"sequence_of_objects_{file_path.stem}"})

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