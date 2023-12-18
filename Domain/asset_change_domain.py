import logging
import os
import tempfile
from pathlib import Path

from otlmow_converter.OtlmowConverter import OtlmowConverter
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import create_dict_from_asset
from otlmow_model.OtlmowModel.Helpers.OTLObjectHelper import compare_two_lists_of_objects_attribute_level

from Domain import global_vars
from Domain.ProjectFileManager import ProjectFileManager
from Domain.enums import ReportAction, FileState
from Domain.project_file import ProjectFile
from Domain.report_item import ReportItem


class AssetChangeDomain:

    @classmethod
    def generate_diff_report(cls, original_data, new_data, model_directory):
        report = []
        diff_lists = cls.generate_difference_between_two_lists(list1=original_data, list2=new_data,
                                                               model_directory=model_directory)
        logging.debug(f"diff lists {str(diff_lists)}")
        original_data_dict = {item.assetId.identificator: item for item in original_data}
        for item in diff_lists:
            old_item = original_data_dict.get(item.assetId.identificator)
            if old_item is None:
                report.append(cls.generate_new_asset_report(item))
            else:
                report.extend(cls.generate_asset_change_report(item, old_item))
        return report

    @classmethod
    def generate_asset_change_report(cls, item, old_item):
        report = []
        item_dict = create_dict_from_asset(item)
        old_item_dict = create_dict_from_asset(old_item)
        for key, value in item_dict.items():
            if key not in ['assetId', 'typeURI']:
                if isinstance(value, dict):
                    report.extend(
                        cls.generate_complex_asset_report(item=item, attribute=key, old_item_dict=old_item_dict,
                                                          complex_list=value))
                else:
                    report.append(cls.generate_simple_asset_report(item=item, key=key, value=value,
                                                                   old_item_dict=old_item_dict))
        return report

    @classmethod
    def get_diff_report(cls, original_documents):
        model_dir = ProjectFileManager().get_otl_wizard_model_dir()
        logging.debug(f"original docs {str(original_documents)}")
        original_assets = []
        for x in original_documents:
            original_assets.extend(OtlmowConverter().create_assets_from_file(Path(x)))
        new_assets = []
        for x in global_vars.single_project.templates_in_memory:
            new_assets.extend(OtlmowConverter().create_assets_from_file(Path(x.file_path)))
        return cls.generate_diff_report(original_assets, new_assets, model_dir)

    @classmethod
    def replace_files_with_diff_report(cls, original_documents, project, file_name):
        changed_assets = cls.generate_changed_assets_from_files(project=project)
        original_assets = cls.generate_original_assets_from_files(original_documents=original_documents)
        diff_1 = compare_two_lists_of_objects_attribute_level(first_list=original_assets,
                                                              second_list=changed_assets,
                                                              model_directory=ProjectFileManager().get_otl_wizard_model_dir())
        final_file_name = file_name
        ProjectFileManager.delete_template_folder()
        project.templates_in_memory = []
        tempdir = ProjectFileManager().create_empty_temporary_map()
        temp_loc = Path(tempdir) / final_file_name
        OtlmowConverter().create_file_from_assets(filepath=temp_loc, list_of_objects=diff_1)
        end_loc = ProjectFileManager().add_template_file_to_project(filepath=temp_loc)
        template_file = ProjectFile(file_path=end_loc, state=FileState.OK.value)
        project.templates_in_memory.append(template_file)
        ProjectFileManager().add_project_files_to_file(project=project)

    @classmethod
    def generate_changed_assets_from_files(cls, project):
        changed_assets = []
        for file in project.templates_in_memory:
            logging.debug(f"file state {file.state}")
            if file.state in ['OK', 'ok']:
                changed_assets.extend(OtlmowConverter().create_assets_from_file(Path(file.file_path)))
        return changed_assets

    @classmethod
    def generate_original_assets_from_files(cls, original_documents):
        original_assets = []
        for path in original_documents:
            original_assets.extend(OtlmowConverter().create_assets_from_file(Path(path)))
        return original_assets

    @classmethod
    def generate_new_asset_report(cls, item):
        return ReportItem(
            id=item.assetId.identificator,
            actie=ReportAction.ASS,
            attribute="",
            original_value="",
            new_value=""
        )

    @classmethod
    def generate_complex_asset_report(cls, item, attribute, complex_list, old_item_dict):
        report = []
        for key, value in complex_list.items():
            rep = ReportItem(
                id=item.assetId.identificator,
                actie=ReportAction.ATC,
                attribute=attribute,
                original_value=f"{str(key)}: {str(old_item_dict.get(attribute).get(key))}",
                new_value=f"{str(key)}: {str(value)}"
            )
            report.append(rep)
        return report

    @classmethod
    def generate_simple_asset_report(cls, item, key, value, old_item_dict):
        return ReportItem(
            id=item.assetId.identificator,
            actie=ReportAction.ATC,
            attribute=str(key),
            original_value=str(old_item_dict.get(key)),
            new_value=str(value)
        )

    @classmethod
    def generate_difference_between_two_lists(cls, list1, list2, model_directory):
        diff_1 = compare_two_lists_of_objects_attribute_level(first_list=list1, second_list=list2,
                                                              model_directory=model_directory)
        return compare_two_lists_of_objects_attribute_level(first_list=list1, second_list=diff_1,
                                                            model_directory=model_directory)
