import os
import shutil
from pathlib import Path

from _pytest.fixtures import fixture
from otlmow_modelbuilder.SQLDataClasses.OSLOClass import OSLOClass

from Domain.step_domain.TemplateDomain import TemplateDomain

PARENT_OF_THIS_FILE = Path(__file__).parent

@fixture
def mock_non_deprecated_classes():
    original_classes = TemplateDomain.classes
    TemplateDomain.classes = [OSLOClass(deprecated_version="")]
    yield
    TemplateDomain.classes = original_classes

@fixture
def mock_deprecated_classes():
    original_classes = TemplateDomain.classes
    TemplateDomain.classes = [OSLOClass(deprecated_version="1.0.0")]
    yield
    TemplateDomain.classes = original_classes

def test_check_for_no_deprecated_present_detects_deprecated(mock_deprecated_classes):
    # values = [OSLOClass(deprecated_version="1.0.0")]
    assert TemplateDomain.check_for_no_deprecated_present() is False


def test_check_for_no_deprecated_present_detects_no_deprecated(mock_non_deprecated_classes):
    # values = [OSLOClass(deprecated_version="")]
    assert TemplateDomain.check_for_no_deprecated_present() is True


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
