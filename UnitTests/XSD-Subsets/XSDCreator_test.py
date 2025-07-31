import unittest

import pytest
import xmltodict

from Domain.util.XSDCreator import XSDCreator

from UnitTests.general_fixtures.DomainFixtures import *

@fixture
def root_directory() -> Path:
    return Path(__file__).parent.parent.parent

#TODO fix test after discussion with David
@unittest.skip('Difference between old OTL-wizard generated XSD and new python generate XSD')
# @pytest.mark.asyncio
async def test_create_xsd_from_filtered_subset_slagbomen(root_directory,cleanup_after_creating_a_file_to_delete):
    # SETUP
    kast_path = root_directory / 'UnitTests' /'test_files' / 'input' / 'voorbeeld-slagboom.db'
    created_path = root_directory / 'UnitTests' / 'test_files' / 'output_test' / 'xsd_export_no_contactor_no_kokerafsluiting.xsd'
    selected_classes_typeURI_list = ["https://wegenenverkeer.data.vlaanderen.be/ns/installatie#Slagboom",
                                     "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Slagboomarm",
                                     "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#SlagboomarmVerlichting",
                                     "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Slagboomkolom"]
    cleanup_after_creating_a_file_to_delete.append(created_path)


    # ACT
    await XSDCreator.create_filtered_xsd_from_subset(subset_path=kast_path, xsd_path=created_path,
                                               selected_classes_typeURI_list=selected_classes_typeURI_list)

    # TEST
    created_xml = Path(created_path).read_text()
    expected_xml = (root_directory / 'UnitTests' / 'test_files' / 'output_ref' /  'xsd_export_no_contactor_no_kokerafsluiting.xsd').read_text()

    created_xml_dict = xmltodict.parse(created_xml)
    expected_xml_dict = xmltodict.parse(expected_xml)

    assert created_xml_dict == expected_xml_dict


def test_create_xsd_from_subset_wegkantkast():
    #SETUP
    kast_path = Path(__file__).parent / 'subset_wegkantkast.db'
    created_path = Path(__file__).parent / 'created_wegkantkast.xsd'

    #ACT
    XSDCreator.create_xsd_from_subset(subset_path=kast_path, xsd_path=created_path)

    #TEST
    created_xml = Path(created_path).read_text()
    expected_xml = (Path(__file__).parent / 'xsd_export_wegkantkast.xsd').read_text()

    created_xml_dict = xmltodict.parse(created_xml)
    expected_xml_dict = xmltodict.parse(expected_xml)

    assert created_xml_dict == expected_xml_dict

@unittest.skip('Test is not yet implemented')
def test_create_xsd_from_subset_testclass():
    kast_path = Path(__file__).parent / 'subset_testclass.db'
    created_path = Path(__file__).parent / 'created_testclass.xsd'

    model_directory = Path(__file__).parent.parent / 'TestModel'

    XSDCreator.create_xsd_from_subset(subset_path=kast_path, xsd_path=created_path, model_directory=model_directory)

    created_xml = Path(created_path).read_text()
    expected_xml = (Path(__file__).parent / 'xsd_export_testclass.xsd').read_text()

    created_xml_dict = xmltodict.parse(created_xml)
    expected_xml_dict = xmltodict.parse(expected_xml)

    assert created_xml_dict == expected_xml_dict
