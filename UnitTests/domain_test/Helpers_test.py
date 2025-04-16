from Domain.util.Helpers import Helpers
from UnitTests.general_fixtures.DomainFixtures import *

def test_create_external_typeURI_options(mock_get_hardcoded_class_dict):



    Helpers.create_external_typeURI_options()

    # Check if the dictionary is populated correctly
    assert Helpers.all_OTL_asset_types_dict == {
        "https://wegenenverkeer.data.vlaanderen.be/ns/installatie#OTLB": {
            "abstract": False,
            "name": "OTLB",
            "label": "OTL B",
            "deprecated_version": "",
            "direct_subclasses": []
        },
        "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#OTLA": {
            "abstract": False,
            "name": "OTLA",
            "label": "OTL A",
            "deprecated_version": "",
            "direct_subclasses": []
        }

    }
