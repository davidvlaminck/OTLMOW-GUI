import logging
from pathlib import Path

from otlmow_converter.OtlmowConverter import OtlmowConverter
from otlmow_model.OtlmowModel.Classes.ImplementatieElement.RelatieObject import RelatieObject


class ExportDataDomain:

    @classmethod
    def generate_files(cls, end_file, project, csv_option, relations_option):
        logging.debug(f'relations option: {relations_option}')
        valid_file_paths = []
        objects_in_memory = []
        logging.debug(f'project_files in memory: {project.templates_in_memory}')
        for file in project.templates_in_memory:
            logging.debug(f'file state: {file.state}')
            if file.state == 'OK' or file.state == 'ok':
                valid_file_paths.append(file.file_path)
        for path in valid_file_paths:
            objects_in_file = OtlmowConverter().create_assets_from_file(filepath=Path(path), path_to_subset=project.subset_path)
            logging.debug(f'objects in file: {objects_in_file}')
            for obj in objects_in_file:
                objects_in_memory.append(obj)
        if relations_option:
            assets_in_memory = []
            relations_in_memory = []
            logging.debug(f'objects in memory: {objects_in_memory}')
            for obj in objects_in_memory:
                if hasattr(obj, 'source') and isinstance(obj, RelatieObject):
                    relations_in_memory.append(obj)
                else:
                    assets_in_memory.append(obj)
            parent_directory = Path(end_file).parent
            relations_file_name = "relations_" + Path(end_file).name
            assets_file_name = "assets_" + Path(end_file).name
            relations_path = Path(parent_directory) / relations_file_name
            assets_path = Path(parent_directory) / assets_file_name
            if relations_in_memory:
                OtlmowConverter().create_file_from_assets(filepath=Path(relations_path), list_of_objects=relations_in_memory, split_per_type=csv_option)
            if assets_in_memory:
                OtlmowConverter().create_file_from_assets(filepath=Path(assets_path), list_of_objects=assets_in_memory, split_per_type=csv_option)
        else:
            OtlmowConverter().create_file_from_assets(list_of_objects=objects_in_memory, filepath=Path(end_file), split_per_type=csv_option)
