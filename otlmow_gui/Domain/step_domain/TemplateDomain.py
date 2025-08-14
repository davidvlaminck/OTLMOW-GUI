import asyncio
import os
import platform
import traceback
from pathlib import Path
from typing import List

from otlmow_converter.Exceptions.ExceptionsGroup import ExceptionsGroup
from otlmow_model.OtlmowModel.Classes.Agent import Agent
from otlmow_modelbuilder.SQLDataClasses.OSLOClass import OSLOClass
from otlmow_template.SubsetTemplateCreator import SubsetTemplateCreator
from otlmow_gui.Domain import global_vars
from otlmow_gui.Domain.util.Helpers import Helpers
from otlmow_gui.Domain.util.SDFHandler import SDFHandler
from otlmow_gui.Domain.logger.OTLLogger import OTLLogger
from otlmow_gui.Domain.network.Updater import Updater
from otlmow_gui.Exceptions.FDOToolboxNotInstalledError import FDOToolboxNotInstalledError
from otlmow_gui.GUI.dialog_windows.LoadingImageWindow import add_loading_screen, LoadingImageWindow
from otlmow_gui.GUI.dialog_windows.NotificationWindow import NotificationWindow
from otlmow_gui.GUI.dialog_windows.SuggestUpdateWindow import SuggestUpdateWindow
from otlmow_gui.GUI.screens.screen_interface.TemplateScreenInterface import TemplateScreenInterface
from otlmow_gui.GUI.translation.GlobalTranslate import GlobalTranslate
from otlmow_gui.exception_handler.ExceptionHandlers import create_task_reraise_exception


class TemplateDomain:

    classes: list[OSLOClass] = []
    selected_classes_indexes: list[int] = []
    all_classes_selected: bool = True
    has_a_class_with_deprecated_attributes: bool = False
    has_agent:bool = False

    @classmethod
    def check_for_no_deprecated_present(cls) -> bool:
        return all(len(value.deprecated_version) == 0 for value in cls.classes)

    @classmethod
    def check_for_agent(cls) -> bool:
        return any(Agent.typeURI == value.objectUri for value in cls.classes)

    @classmethod
    @add_loading_screen
    async def create_template(cls, subset_path: Path, document_path: Path, selected_classes_typeURI_list: List, generate_choice_list: bool,
                              add_geo_artefact: bool, add_attribute_info: bool, highlight_deprecated_attributes: bool,
                              amount_of_examples: int, model_directory: Path = None) -> None:
        OTLLogger.logger.debug("Creating template", extra={"timing_ref": f"create_template_{document_path.name}"})
        try:
            template_creator = SubsetTemplateCreator()

            if not selected_classes_typeURI_list:
                # if selected_class_dir is empty fill it with all classes in the domain
                selected_classes_typeURI_list = [oslo_class.objectUri for oslo_class in cls.classes]

            if selected_classes_typeURI_list and 'http://purl.org/dc/terms/Agent' in selected_classes_typeURI_list:
                # filter out agent
                selected_classes_typeURI_list.remove('http://purl.org/dc/terms/Agent')

            if document_path.suffix == ".sdf":
                await SDFHandler.create_filtered_SDF_from_subset(
                    subset_path=subset_path,
                    sdf_path=document_path,
                    selected_classes_typeURI_list=selected_classes_typeURI_list,
                    model_directory=model_directory)

            else:
                await template_creator.generate_template_from_subset_async(
                    subset_path=subset_path, template_file_path=document_path,
                    class_uris_filter=selected_classes_typeURI_list,
                    generate_choice_list=generate_choice_list,
                    add_geometry=add_geo_artefact, add_attribute_info=add_attribute_info,
                    add_deprecated=highlight_deprecated_attributes,
                    dummy_data_rows=amount_of_examples,
                    model_directory=model_directory,
                    abbreviate_excel_sheettitles=True)
        except FDOToolboxNotInstalledError as e:
            pass
            # document_path_str = str(document_path)
            # OTLLogger.logger.debug(f"Permission to file was denied: {document_path_str}")
            # NotificationWindow(GlobalTranslate._("permission_to_file_was_denied_likely_due_to_the_file_being_open_in_excel") + ":\n" + document_path_str, title=GlobalTranslate._("permission_denied"))
        except PermissionError as e:
            document_path_str = str(document_path)
            OTLLogger.logger.debug(f"Permission to file was denied: {document_path_str}")
            NotificationWindow(GlobalTranslate._(
                "permission_to_file_was_denied_likely_due_to_the_file_being_open_in_excel") + ":\n" + document_path_str,
                               title=GlobalTranslate._("permission_denied"))

        except ExceptionsGroup as e:
            OTLLogger.logger.debug("Error while creating template")
            OTLLogger.logger.error(e)
            OTLLogger.logger.error("".join(traceback.format_exception(e)))
            for ex in e.exceptions:
                OTLLogger.logger.error(ex)
                OTLLogger.logger.error("".join(traceback.format_exception(ex)))

            LoadingImageWindow.attempt_destoy_loading_screen(ref="crash")
            raise e
        except Exception as e:
            OTLLogger.logger.debug("Error while creating template")
            OTLLogger.logger.error(e)
            OTLLogger.logger.error("".join(traceback.format_exception(e)))
            LoadingImageWindow.attempt_destoy_loading_screen(ref="crash")
            raise e
        OTLLogger.logger.debug("Creating template", extra={"timing_ref": f"create_template_{document_path.name}"})

    @classmethod
    def update_subset_information(cls, screen):
        screen.reset_ui( screen._)

    @classmethod
    def init_static(cls):
        if global_vars.current_project:
            create_task_reraise_exception(cls.fill_list())

    @classmethod
    async def fill_list(cls):
        cls.classes.clear()
        cls.has_a_class_with_deprecated_attributes = False
        cls.get_screen().set_gui_list_to_loading_state()
        OTLLogger.logger.debug("Load OTL classes from Subset", extra={"timing_ref": f"class_from_subset_{global_vars.current_project.eigen_referentie}"})
        try:
            await asyncio.sleep(0)  # Give the UI thread the chance to switch the screen to
                                    # TemplateScreen

            modelbuilder = global_vars.current_project.get_model_builder()
            subset_otl_version = global_vars.current_project.get_otl_version()

            otl_model_version = await Updater.async_get_local_otl_model_library_version()
            if not Helpers.is_version_equal_or_higher(otl_model_version, subset_otl_version):
                OTLLogger.logger.info("otlmow-model version is outdated")
                SuggestUpdateWindow(language_settings=GlobalTranslate._,
                                    local_version=Updater.local_version,
                                    new_version=Updater.master_version,
                                    otl_model_out_of_date=True)
            else:
                OTLLogger.logger.info("otlmow-model version is high enough")

            cls.classes = modelbuilder.filter_relations_and_abstract()

            cls.has_a_class_with_deprecated_attributes = TemplateDomain.check_for_no_deprecated_present()
            cls.has_agent = TemplateDomain.check_for_agent()
            cls.select_all_classes()


        except FileNotFoundError as e:
            #TODO: give proper feedback to user if the subset file is not found
            cls.get_screen().set_gui_list_to_no_classes_found()
        OTLLogger.logger.debug("Load OTL classes from Subset", extra={"timing_ref": f"class_from_subset_{global_vars.current_project.eigen_referentie}"})

        cls.update_frontend()
        cls.get_screen().reset_ui(GlobalTranslate._)

    @classmethod
    def select_all_classes(cls):
        total_class_count = cls.get_total_amount_of_classes()
        cls.selected_classes_indexes = list(range(total_class_count))
        TemplateDomain.all_classes_selected = True

        cls.get_screen().set_all_classes_selected()

        cls.get_screen().update_all_classes_selected(cls.all_classes_selected)
        cls.get_screen().update_label_under_list(
            total_amount_of_items=cls.get_total_amount_of_classes(),
            counter=total_class_count)

    @classmethod
    def deselect_all_classes(cls):
        cls.selected_classes_indexes.clear()
        TemplateDomain.all_classes_selected = False

        cls.get_screen().deselect_all_classes()

        cls.get_screen().update_all_classes_selected(cls.all_classes_selected)
        cls.get_screen().update_label_under_list(total_amount_of_items=cls.get_total_amount_of_classes(),
                                                 counter=0)

    @classmethod
    def update_frontend(cls):
        cls.get_screen().update_project_info(global_vars.current_project)
        cls.get_screen().set_classes(classes=cls.classes,
                                     selected_classes= cls.selected_classes_indexes,
                                     all_classes_selected_checked=cls.all_classes_selected,
                                     has_a_class_with_deprecated_attributes=cls.has_a_class_with_deprecated_attributes)

    @classmethod
    def get_screen(cls) -> TemplateScreenInterface:
        return global_vars.otl_wizard.main_window.step1

    @classmethod
    @add_loading_screen
    async def async_export_template(cls, document_path:Path,
                        generate_choice_list: bool, geometry_column_added: bool,
                        export_attribute_info: bool, highlight_deprecated_attributes:bool,
                        amount_of_examples: int):
        return await cls.export_template(document_path,generate_choice_list,
                                   geometry_column_added,export_attribute_info,
                                   highlight_deprecated_attributes,amount_of_examples)

    @classmethod
    async def export_template(cls, document_path:Path ,
                        generate_choice_list: bool, geometry_column_added: bool,
                        export_attribute_info: bool, highlight_deprecated_attributes:bool,
                        amount_of_examples: int):

        project = global_vars.current_project

        selected_classes = [cls.classes[i].objectUri for i in cls.selected_classes_indexes]

        if not document_path or not project:
            return
        await TemplateDomain.create_template(subset_path=project.subset_path,
                                             document_path=Path(document_path),
                                             selected_classes_typeURI_list= selected_classes,
                                             generate_choice_list=generate_choice_list,
                                             add_geo_artefact=geometry_column_added,
                                             add_attribute_info=export_attribute_info,
                                             highlight_deprecated_attributes=highlight_deprecated_attributes,
                                             amount_of_examples=amount_of_examples,
                                             )
        if ".xlsx" in str(document_path):
            if platform.system() == 'Linux':
                os.open(document_path, os.O_WRONLY)
            elif platform.system() == 'Windows':
                os.startfile(document_path)
            else:
                OTLLogger.logger.error("Opening a file on this OS is not implemented yet")
        else:
            cls.get_screen().open_folder_of_created_template(document_path)

    @classmethod
    def toggle_class_index(cls,index:int):
        if index in cls.selected_classes_indexes:
            cls.selected_classes_indexes.remove(index)
        else:
            cls.selected_classes_indexes.append(index)

        cls.get_screen().update_label_under_list(total_amount_of_items=cls.get_total_amount_of_classes(),
                                                 counter=len(cls.selected_classes_indexes))
        cls.update_all_classes_selected_state()

    @classmethod
    def get_total_amount_of_classes(cls):

        count = len(cls.classes)
        if cls.has_agent:
            count -= 1
        return count

    @classmethod
    def update_all_classes_selected_state(cls):
        cls.all_classes_selected = len(cls.selected_classes_indexes) == cls.get_total_amount_of_classes()
        cls.get_screen().update_all_classes_selected(cls.all_classes_selected)

    @classmethod
    def set_select_all_classes(cls, new_state:bool):

        if new_state:
            cls.select_all_classes()
            return

        total_amount_of_items = cls.get_total_amount_of_classes()
        counter = len(cls.selected_classes_indexes)
        if total_amount_of_items == counter:
            cls.deselect_all_classes()
            return

        cls.all_classes_selected = False

    @classmethod
    def set_selected_indexes(cls,new_indexes: list[int]):

        cls.selected_classes_indexes = new_indexes
        cls.get_screen().update_label_under_list(
            total_amount_of_items=cls.get_total_amount_of_classes(),
            counter=len(cls.selected_classes_indexes))
        cls.update_all_classes_selected_state()