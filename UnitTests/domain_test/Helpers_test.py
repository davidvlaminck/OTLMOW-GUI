from otlmow_gui.Domain.util.Helpers import Helpers
from UnitTests.general_fixtures.DomainFixtures import mock_get_hardcoded_class_dict


def test_create_external_typeURI_options(mock_get_hardcoded_class_dict):
    Helpers.create_external_typeURI_options()

    # Check if the dictionary is populated correctly
    assert Helpers.all_OTL_asset_types_dict == {
        'OTL A (Onderdeel)': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#OTLA',
        'OTL B (Installatie)': 'https://wegenenverkeer.data.vlaanderen.be/ns/installatie#OTLB',
        'lgcA (Legacy)': 'https://lgc.wegenenverkeer.data.vlaanderen.be/ns/installatie#lgcA',
        'lgcB (Legacy)': 'https://lgc.wegenenverkeer.data.vlaanderen.be/ns/installatie#lgcB'
    }
