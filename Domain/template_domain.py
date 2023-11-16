import logging
from typing import List


class TemplateDomain:

    @staticmethod
    def check_for_no_deprecated_present(values):
        for value in values:
            if len(value.deprecated_version) != 0:
                return False
        return True

    def create_template(self, subset_path, document_path, selected_classes: List, generate_choice_list: bool,
                        add_geo_artefact: bool, add_attribute_info: bool, highlight_deprecated_attributes: bool,
                        amount_of_examples: int):
        pass
