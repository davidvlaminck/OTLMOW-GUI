import logging
from pathlib import Path

from otlmow_converter.OtlmowConverter import OtlmowConverter


class ExportDataDomain:

    @classmethod
    def generate_files(cls, end_file, project):
        valid_file_paths = []
        objects_in_memory = []
        logging.debug(f'project_files in memory: {project.templates_in_memory}')
        for file in project.templates_in_memory:
            logging.debug(f'file state: {file.state}')
            if file.state == 'OK':
                valid_file_paths.append(file.file_path)
        for path in valid_file_paths:
            objects_in_file = OtlmowConverter().create_assets_from_file(filepath=Path(path), path_to_subset=project.subset_path)
            logging.debug(f'objects in file: {objects_in_file}')
            for obj in objects_in_file:
                objects_in_memory.append(obj)
        OtlmowConverter().create_file_from_assets(list_of_objects=objects_in_memory, filepath=Path(end_file))
