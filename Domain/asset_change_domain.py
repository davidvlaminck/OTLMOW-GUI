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
        diff_1 = compare_two_lists_of_objects_attribute_level(first_list=original_data, second_list=new_data,
                                                              model_directory=model_directory)
        diff_2 = compare_two_lists_of_objects_attribute_level(first_list=original_data, second_list=diff_1, )
        for item in diff_2:
            old_item = next((x for x in original_data if x.assetId.identificator == item.assetId.identificator), None)
            if old_item is None:
                rep_item = ReportItem(
                    id=item.assetId.identificator,
                    actie=ReportAction.ASS,
                    attribute="",
                    original_value="",
                    new_value=""
                )
                report.append(rep_item)
            else:
                item_dict = create_dict_from_asset(item)
                old_item_dict = create_dict_from_asset(old_item)
                item_id = item_dict.get('assetId').get('identificator')
                for key, value in item_dict.items():
                    if key == 'assetId' or key == 'typeURI':
                        continue
                    else:
                        if isinstance(value, dict):
                            for k, v in value.items():
                                rep_item = ReportItem(
                                    id=item_id,
                                    actie=ReportAction.ATC,
                                    attribute=str(key),
                                    original_value=str(k) + ": " + str(old_item_dict.get(key).get(k)),
                                    new_value=str(k) + ": " + str(v)
                                )
                                report.append(rep_item)
                        else:
                            rep_item = ReportItem(
                                id=item_id,
                                actie=ReportAction.ATC,
                                attribute=str(key),
                                original_value=str(old_item_dict.get(key)),
                                new_value=str(value)
                            )
                            report.append(rep_item)
        return report

    @classmethod
    def get_diff_report(cls, original_documents):
        model_dir = ProjectFileManager().get_otl_wizard_model_dir()
        logging.debug("original docs " + str(original_documents))
        original_assets = [OtlmowConverter().create_assets_from_file(Path(x)) for x in original_documents]
        new_assets = [OtlmowConverter().create_assets_from_file(Path(x.file_path)) for x in
                      global_vars.single_project.templates_in_memory]
        report = cls.generate_diff_report(original_assets[0], new_assets[0], model_dir)
        return report

    @classmethod
    def replace_files_with_diff_report(cls, original_documents, project, file_name, extension):
        changed_assets = [OtlmowConverter().create_assets_from_file(Path(x.file_path)) for x in
                          project.templates_in_memory]
        original_assets = [OtlmowConverter().create_assets_from_file(Path(x)) for x in original_documents]
        diff_1 = compare_two_lists_of_objects_attribute_level(first_list=original_assets[0], second_list=changed_assets[0],
                                                              model_directory=ProjectFileManager().get_otl_wizard_model_dir())
        final_file_name = file_name + extension
        ProjectFileManager.delete_template_folder()
        project.templates_in_memory = []
        tempdir = Path(tempfile.gettempdir()) / 'temp-otlmow'
        logging.debug("tempdir" + str(tempdir))
        if not tempdir.exists():
            os.makedirs(tempdir)
        [f.unlink() for f in Path(tempdir).glob("*") if f.is_file()]
        temp_loc = Path(tempdir) / final_file_name
        OtlmowConverter().create_file_from_assets(filepath=temp_loc, list_of_objects=diff_1)
        things_in_there = os.listdir(tempdir)
        files_created = [x for x in things_in_there if str(x).startswith(file_name)]
        logging.debug("files created" + str(files_created))
        for file in files_created:
            temp_loc = Path(tempdir) / file
            end_loc = ProjectFileManager().add_template_file_to_project(filepath=temp_loc)
            template_file = ProjectFile(file_path=end_loc, state=FileState.OK.value)
            project.templates_in_memory.append(template_file)
        ProjectFileManager().add_project_files_to_file(project=project)


