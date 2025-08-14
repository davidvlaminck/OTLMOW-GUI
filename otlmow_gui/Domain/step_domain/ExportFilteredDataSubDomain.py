from dataclasses import dataclass
from pathlib import Path
from typing import List

from otlmow_converter.Exceptions.ExceptionsGroup import ExceptionsGroup
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import create_dict_from_asset, OTLObject
from otlmow_model.OtlmowModel.Helpers.OTLObjectHelper import \
    compare_two_lists_of_objects_attribute_level, is_relation
from otlmow_gui.Domain import global_vars
from otlmow_gui.Domain.logger.OTLLogger import OTLLogger
from otlmow_gui.Domain.enums import ReportAction
from otlmow_gui.Domain.step_domain.ExportDataDomain import ExportDataDomain
from otlmow_gui.Domain.step_domain.InsertDataDomain import InsertDataDomain
from otlmow_gui.Domain.step_domain.RelationChangeDomain import async_save_assets, RelationChangeDomain
from otlmow_gui.GUI.dialog_windows.LoadingImageWindow import add_loading_screen, add_loading_screen_no_delay
from otlmow_gui.GUI.dialog_windows.NotificationWindow import NotificationWindow
from otlmow_gui.GUI.translation.GlobalTranslate import GlobalTranslate


@dataclass
class ReportItem:
    id: str
    actie: ReportAction
    attribute: str
    original_value: str
    new_value: str

class ExportFilteredDataSubDomain:
    original_documents:dict[str,Path] = {}


    @classmethod
    def init_static(cls):
        cls.clear_data()

    @classmethod
    def clear_data(cls):
        cls.original_documents = {}

    @classmethod
    def add_original_documents(cls,paths:list[Path]):
        for path in paths:
            filename = path.name
            cls.original_documents[filename] = path
        cls.update_frontend()

    @classmethod
    def delete_original_file(cls,doc_name:str):
        cls.original_documents.pop(doc_name)
        cls.update_frontend()

    @classmethod
    def update_frontend(cls):
        cls.get_screen().update_original_files_list(cls.original_documents)

    @classmethod
    def generate_diff_report(cls, original_data: list, new_data: list, model_directory: Path=None) -> List[ReportItem]:
        report_list = []
        diff_lists = cls.generate_difference_between_two_lists(list1=original_data, list2=new_data,
                                                               model_directory=model_directory)

        original_data_dict = {item.assetId.identificator: item for item in original_data}
        for item in diff_lists:
            old_item = original_data_dict.get(item.assetId.identificator)
            if old_item is None:
                if is_relation(item):
                    report_list.append(cls.generate_new_relation_report(item))
                else:
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
    @add_loading_screen_no_delay
    @async_save_assets
    async def get_diff_report(cls) -> None:
        # model_dir = ProgramFileStructure.get_otl_wizard_model_dir()
        original_assets, error_set = await cls.generate_original_assets_from_files(original_documents=list(cls.original_documents.values()))

        if error_set:
            cls.get_screen().negative_feedback_message()
            cls.get_screen().fill_up_change_table_with_error_feedback(error_set)
            return

        new_assets = RelationChangeDomain.get_export_instances()

        cls.get_screen().positive_feedback_message()
        cls.get_screen().fill_up_change_table(cls.generate_diff_report(original_assets, new_assets))

    @classmethod
    def sync_export_diff_report(cls,
                           file_name: str,
                           separate_per_class_csv_option:bool = False,
                           separate_relations_option:bool = False,**kwargs) -> None:
        cls.export_diff_report(file_name= file_name,
                               separate_per_class_csv_option=separate_per_class_csv_option,
                               separate_relations_option=separate_relations_option,**kwargs)

    @classmethod
    @add_loading_screen
    async def export_diff_report(cls,
                           file_name: str,
                           separate_per_class_csv_option:bool = False,
                           separate_relations_option:bool = False,**kwargs) -> None:
        OTLLogger.logger.debug("started exporting diff report")
        try:

            changed_assets = sorted(RelationChangeDomain.get_internal_objects(),
                                      key=lambda relation1: relation1.typeURI)
            changed_relations = sorted(RelationChangeDomain.get_persistent_relations(),
                                         key=lambda relation1: relation1.typeURI)

            original_objects, error_set = await cls.generate_original_assets_from_files(original_documents=list(cls.original_documents.values()))
            original_assets = [original_object for original_object in original_objects if not is_relation(original_object)]
            original_relations =[original_object for original_object in original_objects if is_relation(original_object)]



            diff_1_assets = compare_two_lists_of_objects_attribute_level(first_list=original_assets,
                                                                  second_list=changed_assets)
            diff_1_relations = compare_two_lists_of_objects_attribute_level(first_list=original_relations,
                                                                         second_list=changed_relations)

            assets = sorted(diff_1_assets,key=lambda relation1: relation1.typeURI)
            relations = sorted(diff_1_relations, key=lambda relation1: relation1.typeURI)

            await ExportDataDomain.export_to_files(assets, relations , file_name,
                                separate_per_class_csv_option, separate_relations_option,**kwargs)
            cls.get_screen().open_folder_of_created_export_files(file_name)
        except ValueError as e:
            if e.args == ('There are no asset data to export to Excel',):
                notification = NotificationWindow(title=GlobalTranslate._("Geen data"),
                                                  message=GlobalTranslate._("Er is geen data om te exporteren"))
                notification.exec()
            else:
                raise e
        except Exception as e:
            notification = NotificationWindow(title=GlobalTranslate._("Fout in originele bestanden"),
                                              message=GlobalTranslate._("Er is een fout in de originele bestanden\nKlik op \"Toon verschillen\" om een overzicht van de fouten te zien"))
            notification.exec()
            return



    @classmethod
    async def generate_original_assets_from_files(cls,original_documents: List[Path]) -> tuple[List[OTLObject],list]:
        original_assets = []
        error_set = []
        for path in original_documents:
            assets, exceptions_group = await InsertDataDomain.check_document( doc_location=path)

            if exceptions_group and exceptions_group.exceptions:
                for ex in exceptions_group.exceptions:
                    error_set.append({"exception": ex, "path_str": path.name})

            rounded_attribute_assets = []
            for asset in assets:
                waarde_shortcut = True
                allow_non_otl_conform_attributes = True
                warn_for_non_otl_conform_attributes = True

                d = create_dict_from_asset(asset, cast_datetime=True,
                                           waarde_shortcut=waarde_shortcut,
                                           allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                                           warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)

                rounded_asset = OTLObject.from_dict(d,
                                    waarde_shortcut=waarde_shortcut,
                                    cast_datetime=True,
                                    allow_non_otl_conform_attributes=allow_non_otl_conform_attributes,
                                    warn_for_non_otl_conform_attributes=warn_for_non_otl_conform_attributes)

                rounded_attribute_assets.append(rounded_asset)

            original_assets.extend(rounded_attribute_assets)
        try:
            original_assets = await InsertDataDomain.combine_assets_wrapper(original_assets)
        except ExceptionsGroup as group:
            if group.exceptions:
                for ex in group.exceptions:
                    error_set.append({"exception": ex, "path_str": ""})

        return original_assets, error_set

    @classmethod
    def generate_new_asset_report(cls,item) -> ReportItem:
        return ReportItem(
            id=item.assetId.identificator,
            actie=ReportAction.ASS,
            attribute="",
            original_value="",
            new_value=""
        )

    @classmethod
    def generate_new_relation_report(cls, item) -> ReportItem:
        return ReportItem(
            id=item.assetId.identificator,
            actie=ReportAction.REL,
            attribute="",
            original_value="",
            new_value=""
        )

    @classmethod
    def generate_complex_asset_report(cls,item, attribute, complex_list, old_item_dict) -> List[ReportItem]:
        return [ReportItem(
            id=item.assetId.identificator, actie=ReportAction.ATC, attribute=attribute,
            original_value="{0}: {1}".format(str(key),str(old_item_dict.get(attribute).get(key))),
            new_value="{0}: {1}".format(str(key),str(value))
        ) for key, value in complex_list.items()]

    @classmethod
    def generate_simple_asset_report(cls,item, key, value, old_item_dict) -> ReportItem:
        return ReportItem(
            id=item.assetId.identificator,
            actie=ReportAction.ATC,
            attribute=str(key),
            original_value=str(old_item_dict.get(key)),
            new_value=str(value)
        )

    @classmethod
    def generate_difference_between_two_lists(cls,list1: list, list2: list, model_directory: Path=None) -> list:
        diff_1 = compare_two_lists_of_objects_attribute_level(
            first_list=list1, second_list=list2, model_directory=model_directory)
        return compare_two_lists_of_objects_attribute_level(
            first_list=list1, second_list=diff_1, model_directory=model_directory)

    @classmethod
    def get_screen(cls):
        return global_vars.otl_wizard.main_window.step4_export.sub_screen_option_2_only_unedited_data

    @classmethod
    def remove_all_original_documents(cls):
        cls.original_documents.clear()

        cls.update_frontend()
