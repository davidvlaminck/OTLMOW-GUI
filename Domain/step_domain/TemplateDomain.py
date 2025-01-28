import asyncio
import logging
import os
import platform
from pathlib import Path
from typing import List

from PyQt6.QtWidgets import QListWidgetItem
from otlmow_modelbuilder.SQLDataClasses.OSLOClass import OSLOClass
from otlmow_template.SubsetTemplateCreator import SubsetTemplateCreator

from Domain import global_vars
from Domain.logger.OTLLogger import OTLLogger, add_loading_screen
from Domain.step_domain.InsertDataDomain import InsertDataDomain
from Domain.step_domain.RelationChangeDomain import RelationChangeDomain
from GUI.dialog_windows.ExportToTemplateWindow import ExportToTemplateWindow
from GUI.dialog_windows.NotificationWindow import NotificationWindow
from GUI.screens.screen_interface.TemplateScreenInterface import TemplateScreenInterface
from GUI.translation.GlobalTranslate import GlobalTranslate


class TemplateDomain:

    classes: list[OSLOClass] = []
    has_a_class_with_deprecated_attributes = False


    @classmethod
    def check_for_no_deprecated_present(cls) -> bool:
        return all(len(value.deprecated_version) == 0 for value in cls.classes)


    @classmethod
    def create_template(cls,subset_path: Path, document_path: Path, selected_classes_dir: List, generate_choice_list: bool,
                        add_geo_artefact: bool, add_attribute_info: bool, highlight_deprecated_attributes: bool,
                        amount_of_examples: int, model_directory: Path = None) -> None:
        OTLLogger.logger.debug("Creating template", extra={"timing_ref": f"create_template_{document_path.name}"})
        try:
            template_creator = SubsetTemplateCreator()

            if selected_classes_dir and 'http://purl.org/dc/terms/Agent' in selected_classes_dir:
                selected_classes_dir.remove('http://purl.org/dc/terms/Agent')

            template_creator.generate_template_from_subset(
                path_to_subset=subset_path, path_to_template_file_and_extension=document_path,
                list_of_otl_objectUri=selected_classes_dir, generate_choice_list=generate_choice_list,
                add_geo_artefact=add_geo_artefact, add_attribute_info=add_attribute_info,
                highlight_deprecated_attributes=highlight_deprecated_attributes, amount_of_examples=amount_of_examples,
                model_directory=model_directory,
                abbreviate_excel_sheettitles=True)
        except PermissionError as e:
            document_path_str = str(document_path)
            OTLLogger.logger.debug(f"Permission to file was denied: {document_path_str}")
            NotificationWindow(GlobalTranslate._("permission_to_file_was_denied_likely_due_to_the_file_being_open_in_excel") + ":\n" + document_path_str, title=GlobalTranslate._("permission_denied"))
        except Exception as e:
            OTLLogger.logger.debug("Error while creating template")
            OTLLogger.logger.error(e)
            raise e
        OTLLogger.logger.debug("Creating template", extra={"timing_ref": f"create_template_{document_path.name}"})

    @classmethod
    def update_subset_information(cls, screen):
        screen.reset_ui( screen._)

    @classmethod
    def init_static(cls):
        if global_vars.current_project:
            event_loop = asyncio.get_event_loop()
            event_loop.create_task(cls.fill_list())

    @classmethod
    @add_loading_screen
    async def fill_list(cls):
        cls.classes.clear()
        cls.has_a_class_with_deprecated_attributes = False
        cls.get_screen().set_gui_list_to_loading_state()
        OTLLogger.logger.debug("Load OTL classes from Subset", extra={"timing_ref": f"class_from_subset_{global_vars.current_project.eigen_referentie}"})
        try:
            await asyncio.sleep(0)  # Give the UI thread the chance to switch the screen to
                                    # TemplateScreen

            modelbuilder = global_vars.current_project.get_model_builder()

            cls.classes = modelbuilder.filter_relations_and_abstract()
            cls.has_a_class_with_deprecated_attributes = TemplateDomain.check_for_no_deprecated_present()

            cls.get_screen().set_classes(classes=cls.classes,has_a_class_with_deprecated_attributes=cls.has_a_class_with_deprecated_attributes)

        except FileNotFoundError as e:
            #TODO: give proper feedback to user if the subset file is not found
            cls.get_screen().set_gui_list_to_no_classes_found()
        OTLLogger.logger.debug("Load OTL classes from Subset", extra={"timing_ref": f"class_from_subset_{global_vars.current_project.eigen_referentie}"})
        cls.get_screen().update_project_info(global_vars.current_project)




    @classmethod
    def get_screen(cls) -> TemplateScreenInterface:
        return global_vars.otl_wizard.main_window.step1

    @classmethod
    def export_template(cls, document_path:Path ,selected_classes: list[str],
                        generate_choice_list: bool, geometry_column_added: bool,
                        export_attribute_info: bool, highlight_deprecated_attributes:bool,
                        amount_of_examples: int):

        project = global_vars.current_project

        if not document_path or not project:
            return
        TemplateDomain.create_template(subset_path=project.subset_path,
                                       document_path=Path(document_path),
                                       selected_classes_dir= selected_classes,
                                       generate_choice_list=generate_choice_list,
                                       add_geo_artefact=geometry_column_added,
                                       add_attribute_info=export_attribute_info,
                                       highlight_deprecated_attributes=highlight_deprecated_attributes,
                                       amount_of_examples=amount_of_examples)
        if platform.system() == 'Linux':
            os.open(document_path, os.O_WRONLY)
        elif platform.system() == 'Windows':
            os.startfile(document_path)
        else:
            OTLLogger.logger.error("Opening a file on this OS is not implemented yet")