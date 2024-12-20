import logging
from copy import deepcopy
from pathlib import Path

from otlmow_converter.OtlmowConverter import OtlmowConverter
from otlmow_model.OtlmowModel.Classes.ImplementatieElement.RelatieObject import RelatieObject


from Domain.step_domain.RelationChangeDomain import RelationChangeDomain
from Domain.enums import FileState



class ExportDataDomain:

    @classmethod
    def generate_files(cls, end_file: Path, separate_per_class_csv_option : bool =False,
                       separate_relations_option:bool =False):
        """
        Generates output files based on the current assets and relations in memory.
        This class method allows for the option to separate relations and assets into
        different files, and can also split the output by class type if specified.

        Args:
            end_file (Path): The path where the output file(s) will be saved.
            separate_per_class_csv_option (bool, optional): If True, splits the output into separate CSV files per class type. Defaults to False.
            separate_relations_option (bool, optional): If True, generates separate files for relations and assets. Defaults to False.

        Returns:
            None

        Raises:
            OSError: If there is an issue writing to the specified output file(s).
        """
        assets_in_memory = sorted(RelationChangeDomain.get_internal_objects(), key=lambda relation1: relation1.typeURI)
        relations_in_memory = sorted(RelationChangeDomain.get_persistent_relations(), key=lambda relation1: relation1.typeURI)
        if separate_relations_option:
            relations_path, assets_path = cls.create_relation_and_asset_path(end_file)
            if relations_in_memory:
                OtlmowConverter.from_objects_to_file(file_path=relations_path,
                                                     sequence_of_objects=relations_in_memory,
                                                     split_per_type=separate_per_class_csv_option,
                                                     abbreviate_excel_sheettitles=True)
            if assets_in_memory:
                OtlmowConverter.from_objects_to_file(file_path=assets_path,
                                                     sequence_of_objects=assets_in_memory,
                                                     split_per_type=separate_per_class_csv_option,
                                                     abbreviate_excel_sheettitles=True)
        else:
            objects_in_memory = deepcopy(assets_in_memory)
            objects_in_memory.extend(relations_in_memory)
            OtlmowConverter.from_objects_to_file(file_path=Path(end_file),
                                                 sequence_of_objects=objects_in_memory,
                                                 split_per_type=separate_per_class_csv_option,
                                                 abbreviate_excel_sheettitles=True)

    @classmethod
    def extract_objects_from_files(cls,project):
        logging.debug("started extracting objects from files for export")
        valid_file_paths = [file.file_path for file in project.get_saved_projectfiles() if file.state == FileState.OK]
        objects_in_memory = []
        for path in valid_file_paths:
            objects_in_memory.extend(OtlmowConverter.from_file_to_objects(
                file_path=Path(path), model_directory=project.subset_path))
        return objects_in_memory

    @classmethod
    def split_relations_and_objects(cls,objects_in_memory):
        logging.debug("started splitting relations and objects for export")
        assets_in_memory = []
        relations_in_memory = []
        logging.debug(f'objects in memory: {objects_in_memory}')
        for obj in objects_in_memory:
            if hasattr(obj, 'bronAssetId') or isinstance(obj, RelatieObject):
                relations_in_memory.append(obj)
            else:
                assets_in_memory.append(obj)
        return assets_in_memory, relations_in_memory

    @classmethod
    def create_relation_and_asset_path(cls, end_file):
        """
        Creates file paths for relations and assets based on the provided end file path.
        This class method constructs new file names by appending appropriate suffixes to the original file name and returns the paths for both relations and assets.

        Args:
            end_file (Path | str): The path of the original file used to derive the new file paths.

        Returns:
            tuple: A tuple containing the paths for the relations file and the assets file.
        """

        logging.debug("started creating relation and class path for export")
        parent_directory = Path(end_file).parent
        file_stem = Path(end_file).stem
        file_suffix = Path(end_file).suffixes[0]

        relations_file_name = f"{file_stem}_relations{file_suffix}"
        assets_file_name = f"{file_stem}_assets{file_suffix}"

        relations_path = Path(parent_directory) / relations_file_name
        assets_path = Path(parent_directory) / assets_file_name
        return relations_path, assets_path
