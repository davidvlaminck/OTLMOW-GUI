import os
import shutil
from pathlib import Path

import pytest
from otlmow_modelbuilder.SQLDataClasses.OSLOClass import OSLOClass

from Domain.TemplateDomain import TemplateDomain

PARENT_OF_THIS_FILE = Path(__file__).parent


def test_check_for_no_deprecated_present_detects_deprecated():
    values = [OSLOClass(deprecated_version="1.0.0")]
    assert TemplateDomain.check_for_no_deprecated_present(values) is False


def test_check_for_no_deprecated_present_detects_no_deprecated():
    values = [OSLOClass(deprecated_version="")]
    assert TemplateDomain.check_for_no_deprecated_present(values) is True


def test_create_template():
    if not os.path.exists(PARENT_OF_THIS_FILE / 'test_template'):
        os.mkdir(PARENT_OF_THIS_FILE / 'test_template')

    subset_path = (PARENT_OF_THIS_FILE.parent / 'project_files_test' / 'OTLWizardProjects' / 'Projects' / 'project_1' /
                   'OTL_AllCasesTestClass_no_double_kard.db')
    model_path = PARENT_OF_THIS_FILE.parent / 'project_files_test' / 'OTLWizardProjects' / 'Model'
    template_path = PARENT_OF_THIS_FILE / 'test_template' / 'test_template.xlsx'

    TemplateDomain.create_template(subset_path=subset_path, document_path=template_path, selected_classes_dir=None,
                                   generate_choice_list=True, add_geo_artefact=True, add_attribute_info=True,
                                   highlight_deprecated_attributes=True, amount_of_examples=1,
                                   model_directory=model_path)

    assert os.path.exists(template_path)

    shutil.rmtree(PARENT_OF_THIS_FILE / 'test_template')
