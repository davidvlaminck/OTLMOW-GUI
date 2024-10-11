import logging
from pathlib import Path
from typing import List

from otlmow_converter.OtlmowConverter import OtlmowConverter
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import create_dict_from_asset, OTLObject
from otlmow_model.OtlmowModel.Helpers.OTLObjectHelper import compare_two_lists_of_objects_attribute_level

from Domain import global_vars
from Domain.Project import Project
from Domain.ProjectFileManager import ProjectFileManager
from Domain.enums import ReportAction, FileState
from Domain.ProjectFile import ProjectFile
from Domain.ReportItem import ReportItem


class AssetChangeDomain:

    @classmethod
    def generate_diff_report(cls, original_data: list, new_data: list, model_directory: Path) -> List[ReportItem]:
        report_list = []
        diff_lists = cls.generate_difference_between_two_lists(list1=original_data, list2=new_data,
                                                               model_directory=model_directory)
        logging.debug(f"diff lists {str(diff_lists)}")
        original_data_dict = {item.assetId.identificator: item for item in original_data}
        for item in diff_lists:
            old_item = original_data_dict.get(item.assetId.identificator)
            if old_item is None:
                report_list.append(cls.generate_new_asset_report(item))
            else:
                report_list.extend(cls.generate_asset_change_report(item, old_item))
        return report_list

    @classmethod
    def generate_asset_change_report(cls, item, old_item) -> List[ReportItem]:
        report_list = []
        item_dict = create_dict_from_asset(item)
        old_item_dict = create_dict_from_asset(old_item)
        for key, value in item_dict.items():
            if key not in ['assetId', 'typeURI']:
                if isinstance(value, dict):
                    report_list.extend(
                        cls.generate_complex_asset_report(item=item, attribute=key, old_item_dict=old_item_dict,
                                                          complex_list=value))
                else:
                    report_list.append(cls.generate_simple_asset_report(item=item, key=key, value=value,
                                                                        old_item_dict=old_item_dict))
        return report_list

    @classmethod
    def get_diff_report(cls, original_documents: list) -> List[ReportItem]:
        model_dir = ProjectFileManager.get_otl_wizard_model_dir()
        logging.debug(f"original docs {original_documents}")
        original_assets = []
        for x in original_documents:
            original_assets.extend(OtlmowConverter().from_file_to_objects(file_path=Path(x)))
        new_assets = []
        for x in global_vars.current_project.saved_objects_lists:
            new_assets.extend(OtlmowConverter().from_file_to_objects(file_path=Path(x.file_path)))
        return cls.generate_diff_report(original_assets, new_assets, model_dir)

    @classmethod
    def replace_files_with_diff_report(cls, original_documents: List[str], project: Project, file_name: str) -> None:
        logging.debug("started replacing files with diff report")
        changed_assets = cls.generate_changed_assets_from_files(project=project)
        original_assets = cls.generate_original_assets_from_files(original_documents=original_documents)
        diff_1 = compare_two_lists_of_objects_attribute_level(first_list=original_assets,
                                                              second_list=changed_assets,
                                                              model_directory=ProjectFileManager.get_otl_wizard_model_dir())
        ProjectFileManager.delete_template_folder()
        project.saved_objects_lists = []
        tempdir = ProjectFileManager.create_empty_temporary_map()
        temp_loc = Path(tempdir) / file_name
        OtlmowConverter().from_objects_to_file(file_path=temp_loc, sequence_of_objects=diff_1)
        end_loc = ProjectFileManager.add_template_file_to_project(filepath=temp_loc)
        template_file = ProjectFile(file_path=end_loc, state=FileState.OK)
        project.saved_objects_lists.append(template_file)
        ProjectFileManager.add_project_files_to_file(project=project)

    @staticmethod
    def generate_changed_assets_from_files(project: Project) -> list:
        changed_assets = []
        for file in project.saved_objects_lists:
            logging.debug(f"file state {file.state}")
            if file.state == FileState.OK:
                changed_assets.extend(OtlmowConverter().from_file_to_objects(file_path=Path(file.file_path)))
        return changed_assets

    @staticmethod
    def generate_original_assets_from_files(original_documents: List[str]) -> List[OTLObject]:
        original_assets = []
        for path in original_documents:
            original_assets.extend(OtlmowConverter().from_file_to_objects(file_path=Path(path)))
        return original_assets

    @staticmethod
    def generate_new_asset_report(item) -> ReportItem:
        return ReportItem(
            id=item.assetId.identificator,
            actie=ReportAction.ASS,
            attribute="",
            original_value="",
            new_value=""
        )

    @staticmethod
    def generate_complex_asset_report(item, attribute, complex_list, old_item_dict) -> List[ReportItem]:
        return [ReportItem(
            id=item.assetId.identificator, actie=ReportAction.ATC, attribute=attribute,
            original_value=f"{str(key)}: {str(old_item_dict.get(attribute).get(key))}",
            new_value=f"{str(key)}: {str(value)}"
        ) for key, value in complex_list.items()]

    @staticmethod
    def generate_simple_asset_report(item, key, value, old_item_dict) -> ReportItem:
        return ReportItem(
            id=item.assetId.identificator,
            actie=ReportAction.ATC,
            attribute=str(key),
            original_value=str(old_item_dict.get(key)),
            new_value=str(value)
        )

    @staticmethod
    def generate_difference_between_two_lists(list1: list, list2: list, model_directory: Path) -> list:
        diff_1 = compare_two_lists_of_objects_attribute_level(
            first_list=list1, second_list=list2, model_directory=model_directory)
        return compare_two_lists_of_objects_attribute_level(
            first_list=list1, second_list=diff_1, model_directory=model_directory)
