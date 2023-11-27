from otlmow_modelbuilder.SQLDataClasses.OSLOClass import OSLOClass

from Domain.template_domain import TemplateDomain


def test_check_for_no_deprecated_present_detects_deprecated():
    values = [OSLOClass(deprecated_version="1.0.0")]
    assert TemplateDomain.check_for_no_deprecated_present(values) is False


def test_check_for_no_deprecated_present_detects_no_deprecated():
    values = [OSLOClass(deprecated_version="")]
    assert TemplateDomain.check_for_no_deprecated_present(values) is True
