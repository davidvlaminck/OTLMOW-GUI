import logging
from pathlib import Path

from otlmow_converter.OtlmowConverter import OtlmowConverter
from otlmow_model.OtlmowModel.Classes.ImplementatieElement.RelatieObject import RelatieObject

from Domain.enums import FileState


class ExportDataDomain:
    @classmethod
    def generate_files(cls, end_file, project, csv_option, relations_option):

        objects_in_memory = cls.extract_objects_from_files(project=project)

        if relations_option:
            assets_in_memory, relations_in_memory = cls.split_relations_and_objects(objects_in_memory)
            relations_path, assets_path = cls.create_relation_and_class_path(end_file)
            if relations_in_memory:
                if not csv_option:
                    OtlmowConverter().create_file_from_assets(filepath=relations_path,
                                                              list_of_objects=relations_in_memory,
                                                              )
                else:
                    OtlmowConverter().create_file_from_assets(filepath=relations_path,
                                                              list_of_objects=relations_in_memory,
                                                              split_per_type=csv_option)
            if assets_in_memory:
                if not csv_option:
                    OtlmowConverter().create_file_from_assets(filepath=assets_path, list_of_objects=assets_in_memory,
                                                              )
                else:
                    OtlmowConverter().create_file_from_assets(filepath=assets_path, list_of_objects=assets_in_memory,
                                                              split_per_type=csv_option)
        else:
            if not csv_option:
                OtlmowConverter().create_file_from_assets(list_of_objects=objects_in_memory, filepath=Path(end_file))
            else:
                OtlmowConverter().create_file_from_assets(list_of_objects=objects_in_memory, filepath=Path(end_file),
                                                          split_per_type=csv_option)

    @staticmethod
    def extract_objects_from_files(project):
        logging.debug("started extracting objects from files for export")
        valid_file_paths = [file.file_path for file in project.templates_in_memory if file.state == FileState.OK]
        objects_in_memory = []
        for path in valid_file_paths:
            objects_in_memory.extend(OtlmowConverter().create_assets_from_file(
                filepath=Path(path), path_to_subset=project.subset_path))
        return objects_in_memory

    @staticmethod
    def split_relations_and_objects(objects_in_memory):
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

    @staticmethod
    def create_relation_and_class_path(end_file):
        logging.debug("started creating relation and class path for export")
        parent_directory = Path(end_file).parent
        file_stem = Path(end_file).stem
        file_suffix = Path(end_file).suffixes[0]
        relations_file_name = (
            f"{file_stem}_relations{file_suffix}"
        )
        assets_file_name = f"{file_stem}_assets{file_suffix}"
        relations_path = Path(parent_directory) / relations_file_name
        assets_path = Path(parent_directory) / assets_file_name
        return relations_path, assets_path
