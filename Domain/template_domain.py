import logging
from pathlib import Path
from typing import List

from otlmow_modelbuilder.SQLDataClasses.OSLOClass import OSLOClass
from otlmow_template.SubsetTemplateCreator import SubsetTemplateCreator

from GUI.DialogWindows.NotificationWindow import NotificationWindow


class TemplateDomain:
    @staticmethod
    def check_for_no_deprecated_present(values: List[OSLOClass]) -> bool:
        return all(len(value.deprecated_version) == 0 for value in values)

    @staticmethod
    def create_template(subset_path, document_path, selected_classes_dir: List, generate_choice_list: bool,
                        add_geo_artefact: bool, add_attribute_info: bool, highlight_deprecated_attributes: bool,
                        amount_of_examples: int, model_directory: Path = None) -> None:
        try:
            logging.debug("Creating template")
            template_creator = SubsetTemplateCreator()
            template_creator.generate_template_from_subset(
                path_to_subset=subset_path, path_to_template_file_and_extension=document_path,
                list_of_otl_objectUri=selected_classes_dir, generate_choice_list=generate_choice_list,
                add_geo_artefact=add_geo_artefact, add_attribute_info=add_attribute_info,
                highlight_deprecated_attributes=highlight_deprecated_attributes, amount_of_examples=amount_of_examples,
                model_directory=model_directory)
        except PermissionError as e:
            logging.debug("Permission to file was denied: " + str(document_path))
            NotificationWindow("permission_to_file_was_denied_likely_due_to_the_file_being_open_in_excel" + ":\n" + str(document_path),title="permission_denied")
        except Exception as e:
            logging.debug("Error while creating template")
            logging.error(e)
            raise e
