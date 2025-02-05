import unittest
from pathlib import Path

import xmltodict

from Domain.XSDCreator import XSDCreator


def test_create_xsd_from_subset_wegkantkast():
    kast_path = Path(__file__).parent / 'subset_wegkantkast.db'
    created_path = Path(__file__).parent / 'created_wegkantkast.xsd'

    XSDCreator.create_xsd_from_subset(kast_path, created_path)

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

    XSDCreator.create_xsd_from_subset(kast_path, created_path, model_directory)

    created_xml = Path(created_path).read_text()
    expected_xml = (Path(__file__).parent / 'xsd_export_testclass.xsd').read_text()

    created_xml_dict = xmltodict.parse(created_xml)
    expected_xml_dict = xmltodict.parse(expected_xml)

    assert created_xml_dict == expected_xml_dict
