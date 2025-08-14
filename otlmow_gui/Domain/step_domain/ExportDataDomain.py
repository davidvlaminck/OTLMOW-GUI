from copy import deepcopy
from pathlib import Path

from otlmow_model.OtlmowModel.Classes.ImplementatieElement.RelatieObject import RelatieObject
from otlmow_gui.Domain import global_vars
from otlmow_gui.Domain.util.Helpers import Helpers
from otlmow_gui.Domain.logger.OTLLogger import OTLLogger
from otlmow_gui.Domain.step_domain.RelationChangeDomain import RelationChangeDomain
from otlmow_gui.GUI.dialog_windows.NotificationWindow import NotificationWindow
from otlmow_gui.GUI.translation.GlobalTranslate import GlobalTranslate


class ExportDataDomain:
    """
    Handles the generation and management of export files for assets and relations.
    This class provides methods to create, split, and organize data for export, ensuring that the
    output meets specified requirements.

    Attributes:
        None

    Methods:
        generate_files(end_file: Path, separate_per_class_csv_option: bool = False, separate_relations_option: bool = False) -> None: Generates output files based on the current assets and relations in memory.
        split_relations_and_objects(objects_in_memory: list) -> tuple: Splits a list of objects into two categories: assets and relations.
        create_relation_and_asset_path(end_file: Path | str) -> tuple: Creates file paths for relations and assets based on the provided end file path.
    """


    @classmethod
    async def generate_files(cls, end_file: Path, separate_per_class_csv_option : bool =False,
                       separate_relations_option:bool =False, **kwargs) -> None:
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
        try:
            assets_in_memory = sorted(RelationChangeDomain.get_internal_objects(), key=lambda relation1: relation1.typeURI)
            relations_in_memory = sorted(RelationChangeDomain.get_persistent_relations(), key=lambda relation1: relation1.typeURI)
            await cls.export_to_files(assets_in_memory, relations_in_memory, end_file,
                                separate_per_class_csv_option, separate_relations_option, **kwargs)
            cls.get_screen().open_folder_of_created_export_files(end_file)
        except ValueError as e:
            if e.args == ('There are no asset data to export to Excel',):
                notification = NotificationWindow(title="Geen data",
                                                  message="Er is geen data om te exporteren")
                notification.exec()
            else:
                raise e

    @classmethod
    async def export_to_files(cls, assets, relations, end_file, separate_per_class_csv_option,
                        separate_relations_option, **kwargs):
        try:
            if separate_relations_option:
                relations_path, assets_path = cls.create_relation_and_asset_path(end_file)
                if relations:
                    await Helpers.start_async_converter_from_object_to_file(file_path=relations_path,
                                                                      sequence_of_objects=relations,
                                                                      split_per_type=separate_per_class_csv_option,
                                                                      abbreviate_excel_sheettitles=True, **kwargs)
                else:
                    OTLLogger.logger.info(
                        f"No Relations in memory for project {global_vars.current_project.eigen_referentie}")
                if assets:
                    await Helpers.start_async_converter_from_object_to_file(file_path=assets_path,
                                                                      sequence_of_objects=assets,
                                                                      split_per_type=separate_per_class_csv_option,
                                                                      abbreviate_excel_sheettitles=True, **kwargs)
                else:
                    OTLLogger.logger.info(
                        f"No Assets in memory for project {global_vars.current_project.eigen_referentie}")

            else:
                objects_in_memory = deepcopy(assets)
                objects_in_memory.extend(relations)
                await Helpers.start_async_converter_from_object_to_file(file_path=Path(end_file),
                                                                  sequence_of_objects=objects_in_memory,
                                                                  split_per_type=separate_per_class_csv_option,
                                                                  abbreviate_excel_sheettitles=True, **kwargs)
        except PermissionError as e:
            notification = NotificationWindow(title= GlobalTranslate._("Toestemming geweigerd"),
                                              message= GlobalTranslate._("Geen toestemming om te exporteren naar \n{filename}\nIs het bestand nog open?").format(filename=e.filename))
            notification.exec()
            return
    @classmethod
    def split_relations_and_objects(cls,objects_in_memory):
        """
        Splits a list of objects into two categories: assets and relations. This method iterates
        through the provided objects, classifying them based on their attributes, and returns
        two separate lists for further processing.

        :param objects_in_memory: A list of objects to be classified into assets and relations.
        :type objects_in_memory: list

        :return: A tuple containing two lists: the first list of assets and the second list of relations.
        :rtype: tuple[list, list]
        """

        OTLLogger.logger.debug("started splitting relations and objects for export")
        assets_in_memory = []
        relations_in_memory = []

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

        OTLLogger.logger.debug("started creating relation and class path for export")
        parent_directory = Path(end_file).parent
        file_stem = Path(end_file).stem
        file_suffix = Path(end_file).suffixes[0]

        relations_file_name = f"{file_stem}_relations{file_suffix}"
        assets_file_name = f"{file_stem}_assets{file_suffix}"

        relations_path = Path(parent_directory) / relations_file_name
        assets_path = Path(parent_directory) / assets_file_name
        return relations_path, assets_path

    @classmethod
    def update_frontend(cls):
        pass

    @classmethod
    def get_screen(cls):
        return global_vars.otl_wizard.main_window.step4_export