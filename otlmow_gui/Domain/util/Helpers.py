
import base64
import os
import subprocess
import sys
import tempfile
import traceback
import warnings
from pathlib import Path
from typing import Optional, Iterable

from otlmow_converter.Exceptions.ExceptionsGroup import ExceptionsGroup
from otlmow_converter.Exceptions.UnknownExcelError import UnknownExcelError
from otlmow_converter.OtlmowConverter import OtlmowConverter
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject, \
    dynamic_create_instance_from_ns_and_name, dynamic_create_instance_from_uri

from otlmow_model.OtlmowModel.Helpers import OTLObjectHelper
from otlmow_model.OtlmowModel.Helpers.GenericHelper import validate_guid, get_ns_and_name_from_uri, \
    get_titlecase_from_ns
from otlmow_model.OtlmowModel.Helpers.generated_lists import get_hardcoded_class_dict, get_hardcoded_relation_dict
from packaging.version import Version

from otlmow_gui.Domain.logger.OTLLogger import OTLLogger
from otlmow_gui.GUI.dialog_windows.LoadingImageWindow import add_loading_screen
from otlmow_gui.GUI.screens.RelationChange_elements.RelationChangeHelpers import RelationChangeHelpers



class Helpers:
    all_OTL_asset_types_dict = {}

    @classmethod
    def get_hardcoded_class_dict(cls) -> dict:
        return get_hardcoded_class_dict()

    @classmethod
    def create_external_typeURI_options(cls):
        cls.all_OTL_asset_types_dict = {}
        all_type_uris = cls.get_hardcoded_class_dict()
        buckets_dict = {'assets': {}, 'legacy':{}}

        for uri, info in all_type_uris.items():
            if info['abstract']:
                continue
            if uri in get_hardcoded_relation_dict():
                continue

            ns, name = get_ns_and_name_from_uri(uri)
            screen_name = info['name'] if ns == 'legacy' else info['label']
            if ns is not None:
                screen_name += f" ({get_titlecase_from_ns(ns)})"

            if ns == 'legacy':
                screen_name = screen_name.replace("(Legacy) (Legacy)", "(Legacy)")
                buckets_dict['legacy'][screen_name] = uri
            else:
                buckets_dict['assets'][screen_name] = uri

            cls.all_OTL_asset_types_dict[screen_name] = uri

        # combine and sort the dictionary by keys (screen name)
        cls.all_OTL_asset_types_dict = dict(sorted(buckets_dict['assets'].items()))
        cls.all_OTL_asset_types_dict.update(dict(sorted(buckets_dict['legacy'].items())))

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
    async def converter_from_file_to_object_async(cls, file_path:Path,allow_non_otl_conform_attributes:bool=False, **kwargs):

        OTLLogger.logger.debug(f"Execute OtlmowConverter.from_file_to_objects({file_path.name})",
                               extra={"timing_ref": f"file_to_objects_{file_path.stem}"})

        exception_group = ExceptionsGroup(
            message=f'Failed to create objects')

        try:
            object_lists = list(await OtlmowConverter.from_file_to_objects_async(file_path,allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,**kwargs))
        except ExceptionsGroup as group:
            exception_group = group
            object_lists = group.objects
        except BaseException as ex:
            object_lists = []
            exc_type, exc_value, exc_tb = sys.exc_info()
            tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
            OTLLogger.logger.error("error caught!")
            OTLLogger.logger.error("error message: \n: " + tb)
            exception_group.add_exception(UnknownExcelError(original_exception=ex, tab=""))

        object_count = len(object_lists)
        OTLLogger.logger.debug(f"Execute OtlmowConverter.from_file_to_objects({file_path.name}) ({object_count} objects)",
                               extra={"timing_ref": f"file_to_objects_{file_path.stem}"})
        return object_lists,exception_group

    @classmethod
    async def converter_from_file_to_object(cls, file_path, **kwargs):

        OTLLogger.logger.debug(f"Execute OtlmowConverter.from_file_to_objects({file_path.name})",
                               extra={"timing_ref": f"file_to_objects_{file_path.stem}"})
        exception_group = None
        try:
            object_lists = list(
                OtlmowConverter.from_file_to_objects(file_path, **kwargs))
        except ExceptionsGroup as group:
            exception_group = group
            object_lists = group.objects

        object_count = len(object_lists)
        OTLLogger.logger.debug(
            f"Execute OtlmowConverter.from_file_to_objects({file_path.name}) ({object_count} objects)",
            extra={"timing_ref": f"file_to_objects_{file_path.stem}"})
        return object_lists, exception_group

    @classmethod
    async def start_async_converter_from_object_to_file(cls, file_path: Path,
                                            sequence_of_objects: Iterable[OTLObject], **kwargs) -> None:

        await Helpers.converter_from_object_to_file(file_path=file_path,
                                              sequence_of_objects=sequence_of_objects,
                                              **kwargs)



    @classmethod
    @add_loading_screen
    async def converter_from_object_to_file(cls, file_path: Path, sequence_of_objects: Iterable[OTLObject], **kwargs) -> None:
        OTLLogger.logger.debug(f"Execute OtlmowConverter.from_objects_to_file({file_path.name})",
                               extra={"timing_ref": f"sequence_of_objects_{file_path.stem}"})
        await OtlmowConverter.from_objects_to_file_async(file_path=file_path,
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

        tempdir = Helpers.get_base_temp_dir_path()
        if not tempdir.exists():
            os.makedirs(tempdir)
        doc_name = Path(path_to_template_file_and_extension).name
        return Path(tempdir) / doc_name

    @classmethod
    def get_base_temp_dir_path(cls):
        return Path(tempfile.gettempdir()) / 'temp-otlmow'

    @classmethod
    def extract_typeURI_from_aim_id(cls,aim_id:str,model_directory:Optional[Path]=None) -> Optional[str]:
        uuid = aim_id[:36]
        short_uri_encoded = aim_id[37:]

        if not validate_guid(uuid):
            return None
        if not short_uri_encoded:
            return None

        if missing_padding := len(short_uri_encoded) % 4:
            short_uri_encoded += '=' * (4 - missing_padding)

        short_uri_bytes = base64.b64decode(short_uri_encoded)
        try:
            short_uri = short_uri_bytes.decode('ascii')
        except UnicodeDecodeError:
            return None
        try:
            if short_uri == 'purl:Agent':
                agent = dynamic_create_instance_from_uri('http://purl.org/dc/terms/Agent',
                                                         model_directory=model_directory)
                return agent.typeURI

            ns, name = short_uri.split('#')
            instance:OTLObject = dynamic_create_instance_from_ns_and_name(ns, name,
                                                                          model_directory=model_directory)
            return instance.typeURI
        except ModuleNotFoundError:
            warnings.warn(
            'Could not import the module for the given aim_id, did you forget the model_directory?',
            category=ImportWarning)
            return None

        except ValueError:
            return None

    @classmethod
    def extract_corrected_relation_partner_typeURI(cls, partner_type_uri, partner_id,
                                                   id_to_typeURI_dict, ref_assets) -> Optional[
        str]:
        if partner_type_uri is None:
            if not id_to_typeURI_dict:
                id_to_typeURI_dict = {RelationChangeHelpers.get_corrected_identificator(asset): asset.typeURI
                                      for asset in ref_assets}

            if partner_id in id_to_typeURI_dict.keys():
                partner_type_uri = id_to_typeURI_dict[partner_id]

        # incase there is no asset with the correct assetId in the application
        if partner_type_uri is None and OTLObjectHelper.is_aim_id(partner_id):
            partner_type_uri = Helpers.extract_typeURI_from_aim_id(partner_id)

        return partner_type_uri

    @classmethod
    def open_folder_and_select_document(cls,document_path:Path):
        if document_path.exists():
            command = f'explorer /select,"{document_path}"'
        else:
            command = f'explorer "{document_path.parent}"'
        OTLLogger.logger.debug(command)
        subprocess.Popen(command)

    @classmethod
    def compare_RelatieObjects(cls, obj1, obj2):
        dict1 = OTLObject.to_dict(obj1)
        dict2 = OTLObject.to_dict(obj2)

        if "isActief" in dict1:
            dict1.pop("isActief")
        if "isActief" in dict2:
            dict2.pop("isActief")

        return dict1 == dict2

    @classmethod
    def from_objects_to_file(cls, save_path,assets_in_memory):
        OtlmowConverter.from_objects_to_file(file_path=save_path,
                                             sequence_of_objects=assets_in_memory)

    @classmethod
    async def from_objects_to_file_async(cls, save_path,assets_in_memory):
        return await OtlmowConverter.from_objects_to_file_async(file_path=save_path,
                                                          sequence_of_objects=assets_in_memory)