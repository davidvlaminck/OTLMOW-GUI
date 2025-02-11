import logging
from pathlib import Path

from Domain.logger.OTLLogger import OTLLogger
from Domain.step_domain.AssetChangeDomain import ExportFilteredDataSubDomain, ReportItem
from Domain.enums import ReportAction
from UnitTests.project_files_test.OTLWizardProjects.Model.OtlmowModel.Classes.Onderdeel.AllCasesTestClass import \
    AllCasesTestClass
from UnitTests.project_files_test.OTLWizardProjects.Model.OtlmowModel.Classes.Onderdeel.AnotherTestClass import \
    AnotherTestClass

model_directory_path = Path(__file__).parent.parent / 'project_files_test' / 'OTLWizardProjects' / 'Model'


def test_generate_report():
    OTLLogger.logger.debug(str(model_directory_path))
    instance_1_1 = AllCasesTestClass()
    instance_1_1.assetId.identificator = '1'
    instance_1_1.isActief = True

    instance_2_1 = AllCasesTestClass()
    instance_2_1.assetId.identificator = '1'
    instance_2_1.isActief = True

    instance_1_2 = AllCasesTestClass()
    instance_1_2.assetId.identificator = '2'
    instance_1_2.isActief = True
    instance_1_2.testStringField = 'test'
    instance_1_2.testComplexType.testStringField = 'complexe waarde'

    instance_2_2 = AllCasesTestClass()
    instance_2_2.assetId.identificator = '2'
    instance_2_2.isActief = False
    instance_2_2.testStringField = 'gewijzigd'
    instance_2_2.testComplexType.testStringField = 'gewijzigde complexe waarde'

    instance_1_3 = AllCasesTestClass()
    instance_1_3.assetId.identificator = '3'
    instance_1_3.isActief = True
    # TODO bert navragen of dit de bedoeling is

    instance_2_4 = AnotherTestClass()
    instance_2_4.assetId.identificator = '4'
    instance_2_4.isActief = True

    instance_list_1 = [ instance_1_2, instance_1_3]
    instance_list_2 = [ instance_2_2, instance_2_4]

    report = ExportFilteredDataSubDomain().generate_diff_report(original_data=instance_list_1, new_data=instance_list_2,
                                                                model_directory=model_directory_path)

    assert report == [
        ReportItem(id='2', actie=ReportAction.ATC, attribute='isActief', original_value='True', new_value='False'),
        ReportItem(id='2', actie=ReportAction.ATC, attribute='testComplexType',
                   original_value="testStringField: complexe waarde",
                   new_value="testStringField: gewijzigde complexe waarde"),
        ReportItem(id='2', actie=ReportAction.ATC, attribute='testStringField', original_value='test',
                   new_value='gewijzigd'),
        ReportItem(id='4', actie=ReportAction.ASS, attribute='', original_value='', new_value='')
    ]
