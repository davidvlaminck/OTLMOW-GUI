import unittest
from pathlib import Path
import xml.etree.cElementTree as ET

from Domain.XSDCreator import XSDCreator


def test_create_xsd_from_subset_wegkantkast():
    kast_path = Path(__file__).parent / 'subset_wegkantkast.db'
    created_path = Path(__file__).parent / 'created_wegkantkast.xsd'

    XSDCreator.create_xsd_from_subset(kast_path, created_path)

    result = ET.tostring(ET.parse(created_path).getroot())
    expected = ET.tostring(ET.parse(Path(__file__).parent / 'xsd_export_wegkantkast.xsd').getroot())

    assert expected == result


@unittest.skip('Test is not yet implemented')
def test_create_xsd_from_subset_testclass():
    kast_path = Path(__file__).parent / 'subset_testclass.db'
    created_path = Path(__file__).parent / 'created_testclass.xsd'

    model_directory = Path(__file__).parent.parent / 'TestModel'

    XSDCreator.create_xsd_from_subset(kast_path, created_path, model_directory)

    result = ET.tostring(ET.parse(created_path).getroot())
    expected = ET.tostring(ET.parse(Path(__file__).parent / 'xsd_export_testclass.xsd').getroot())

    assert expected == result
