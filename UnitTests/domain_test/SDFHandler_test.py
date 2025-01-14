from pathlib import Path

import pytest
from _pytest.fixtures import fixture

from Domain.SDFHandler import SDFHandler
from Exceptions.FDOToolboxProcessError import FDOToolboxProcessError
from Exceptions.WrongFileTypeError import WrongFileTypeError

from UnitTests.general_fixtures.GUIFixtures import *
from UnitTests.general_fixtures.DomainFixtures import *

"""
This will test the FDO toolbox interface class called SDFHandler
It can only be used on Windows so these test should only be run on Windows systems
"""

@fixture
def root_directory() -> Path:
    return Path(__file__).parent.parent.parent

@pytest.mark.parametrize("rel_sdf_file_path, expected_output", [
    ("UnitTests/test_files/input/DA-2024-03992_export_sdf_example.sdf",
     ['OTL_Brandblusser', 'OTL_Galgpaal', 'OTL_Hydrant', 'OTL_IntercomToestel',
                       'OTL_Luchtkwaliteitreflector', 'OTL_LuchtkwaliteitZenderOntvanger',
                       'OTL_Pictogram', 'OTL_RechteSteun', 'OTL_Ventilatierooster',
                       'OTL_VerlichtingstoestelHgLP', 'OTL_Voertuiglantaarn',
                       'OTL_ASTRIDInstallatie', 'OTL_Deur', 'OTL_NietSelectieveDetectielus',
                       'OTL_Slagboomarm', 'OTL_Datakabel', 'OTL_Ladder', 'OTL_Leuning',
                       'OTL_Hulppost', 'OTL_Luchtkwaliteitsensor', 'OTL_Slagboom',
                       'OTL_Pompstation', 'OTL_BasisverlichtingTunnel',
                       'OTL_Kokerafsluiting', 'OTL_Kokerventilatie', 'OTL_Ventilatiecluster',
                       'OTL_VersterkingsverlichtingTunnel', 'OTL_Vluchtganginrichting',
                       'OTL_Montagekast', 'OTL_Slagboomkolom', 'OTL_Ventilator', 'OTL_Seinbrug']),
    ("UnitTests/test_files/input/DA-2025-00023_export_sdf_example.sdf",
     ['OTL_WVLichtmast', 'OTL_Voedingskabel']),
], ids=["DA-2024-03992_export_sdf_example",
        "DA-2025-00023_export_sdf_example"])
def test_get_classes_from_SDF_file(root_directory,rel_sdf_file_path,expected_output):

    sdf_path_example = root_directory / rel_sdf_file_path
    output = SDFHandler.get_classes_from_SDF_file(sdf_path_example)

    assert output == expected_output



@pytest.mark.parametrize("rel_sdf_file_path,expected_exception,expected_error_msg", [
    ("UnitTests/test_files/input/does_not_exist.sdf",FileNotFoundError,"{0} is not a valid path. File does not exist."),
    ("UnitTests/test_files/input/wrong_type_for_sdf.txt",WrongFileTypeError,'The path to the provided file is not a SDF-file file with extension (.sdf)'),
    ("UnitTests/test_files/input/DA-2025-00023_export_sdf_corrupted_example.sdf",FDOToolboxProcessError,
     ('An error occured during FDO toolbox call:  \n'
 'Call: "C:\\Program Files\\FDO Toolbox\\FdoCmd.exe" list-classes --from-file '
 '"{0}" \n'
 'Error:\n'
 '\n'
 '\n'
 'OSGeo.FDO.Common.Exception: File is not an SDF file, or is an SDF file with '
 'an unsupported version.  ---> OSGeo.FDO.Common.Exception: An error occurred '
 'during SDF database access.  \n'
 '   --- End of inner exception stack trace ---\n'
 '   at OSGeo.FDO.Connections.IConnectionImp.Open()\n'
 '   at FdoCmd.Commands.ProviderConnectionCommand.Execute()'))
], ids=["no_file",
        "not_a_sdf_file",
        "invalid_sdf_content"])
def test_get_classes_from_SDF_file_error(root_directory,create_translations,rel_sdf_file_path,expected_exception,expected_error_msg):

    sdf_path_example = root_directory / rel_sdf_file_path

    with pytest.raises(expected_exception) as exc_info:
        output = SDFHandler.get_classes_from_SDF_file(sdf_path_example)

    # addin the correct absolute path in the expected error
    if '{0}' in expected_error_msg:
        expected_error_msg = expected_error_msg.format(sdf_path_example)

    if expected_exception == FileNotFoundError:
        assert exc_info.value.args[0] == expected_error_msg
    else:
        assert str(exc_info.value) == expected_error_msg
