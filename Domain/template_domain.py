import logging
import os
from typing import List

from otlmow_template.SubsetTemplateCreator import SubsetTemplateCreator


# from otlmow_template.SubsetTemplateCreator import SubsetTemplateCreator


class TemplateDomain:

    @staticmethod
    def check_for_no_deprecated_present(values):
        for value in values:
            if len(value.deprecated_version) != 0:
                return False
        return True

    # TODO change selected_classes to selected_classes_dir
    # TODO: geef model_directory mee
    @staticmethod
    def create_template(subset_path, document_path, selected_classes: List, generate_choice_list: bool,
                        add_geo_artefact: bool, add_attribute_info: bool, highlight_deprecated_attributes: bool,
                        amount_of_examples: int):
        try:
            logging.debug("Creating template")
            template_creator = SubsetTemplateCreator()
            template_creator.generate_template_from_subset(path_to_subset=subset_path,
                                                           path_to_template_file_and_extension=document_path,
                                                           selected_classes=selected_classes,
                                                           generate_choice_list=generate_choice_list,
                                                           add_geo_artefact=add_geo_artefact,
                                                           add_attribute_info=add_attribute_info,
                                                           highlight_deprecated_attributes=highlight_deprecated_attributes,
                                                           amount_of_examples=amount_of_examples)
            os.startfile(document_path)
        except Exception as e:
            logging.debug("Error while creating template")
            logging.error(e)
