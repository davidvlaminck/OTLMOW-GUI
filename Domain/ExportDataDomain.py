import logging
import os
from pathlib import Path
from typing import cast

from otlmow_converter.OtlmowConverter import OtlmowConverter
from otlmow_model.OtlmowModel.Classes.ImplementatieElement.RelatieObject import RelatieObject

from Domain.InsertDataDomain import InsertDataDomain
from Domain.RelationChangeDomain import RelationChangeDomain
from Domain.enums import FileState
from UnitTests.TestClasses.Classes.ImplementatieElement.AIMObject import AIMObject


class ExportDataDomain:



    @classmethod
    def generate_files(cls, end_file, project, separate_per_class_csv_option, separate_relations_option):

        # objects_in_memory = cls.extract_objects_from_files(project=project)
        assets_in_memory = sorted(RelationChangeDomain.owned_objects, key=lambda relation1: relation1.typeURI)
        relations_in_memory = sorted(RelationChangeDomain.existing_relations + RelationChangeDomain.get_inactive_aim_id_relations(), key=lambda relation1: relation1.typeURI)
        if separate_relations_option:
            # assets_in_memory, relations_in_memory = cls.split_relations_and_objects(objects_in_memory)
            relations_path, assets_path = cls.create_relation_and_class_path(end_file)
            if relations_in_memory:
                if not separate_per_class_csv_option:
                    OtlmowConverter.from_objects_to_file(file_path=relations_path,
                                                         sequence_of_objects=relations_in_memory,
                                                         abbreviate_excel_sheettitles=True)
                else:
                    OtlmowConverter.from_objects_to_file(file_path=relations_path,
                                                         sequence_of_objects=relations_in_memory,
                                                         split_per_type=separate_per_class_csv_option,
                                                         abbreviate_excel_sheettitles=True)

            if assets_in_memory:
                if not separate_per_class_csv_option:
                    OtlmowConverter.from_objects_to_file(file_path=assets_path,
                                                         sequence_of_objects=assets_in_memory,
                                                         abbreviate_excel_sheettitles = True)
                else:
                    OtlmowConverter.from_objects_to_file(file_path=assets_path,
                                                         sequence_of_objects=assets_in_memory,
                                                         split_per_type=separate_per_class_csv_option,
                                                         abbreviate_excel_sheettitles=True)
        else:
            objects_in_memory = assets_in_memory
            objects_in_memory.extend(relations_in_memory)

            if not separate_per_class_csv_option:
                OtlmowConverter.from_objects_to_file(file_path=Path(end_file),
                                                     sequence_of_objects=objects_in_memory,
                                                     abbreviate_excel_sheettitles=True )
            else:
                OtlmowConverter.from_objects_to_file(file_path=Path(end_file),
                                                     sequence_of_objects=objects_in_memory,
                                                     split_per_type=separate_per_class_csv_option,
                                                     abbreviate_excel_sheettitles=True)

    @staticmethod
    def extract_objects_from_files(project):
        logging.debug("started extracting objects from files for export")
        valid_file_paths = [file.file_path for file in project.saved_project_files if file.state == FileState.OK]
        objects_in_memory = []
        for path in valid_file_paths:
            objects_in_memory.extend(OtlmowConverter.from_file_to_objects(
                file_path=Path(path), model_directory=project.subset_path))
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
