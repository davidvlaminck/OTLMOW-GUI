from pathlib import Path

import pytest
import xmltodict
from _pytest.fixtures import fixture
from openpyxl.styles.builtins import output

from Domain.SDFHandler import SDFHandler
from Exceptions.FDOToolboxNotInstalledError import FDOToolboxNotInstalledError
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
@pytest.mark.skip
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
    output = SDFHandler._get_classes_from_SDF_file(sdf_path_example)

    assert output == expected_output


@pytest.mark.skip
@pytest.mark.parametrize("rel_sdf_file_path,expected_exception,expected_error_msg", [
    ("UnitTests/test_files/input/DA-2025-00023_export_sdf_corrupted_example.sdf",FDOToolboxProcessError,
     ('Er is een fout opgetreden tijdens de FDO-toolbox-oproep: \n'
      'Oproep: "C:\\Program Files\\FDO Toolbox\\FdoCmd.exe" list-classes '
      '--from-file '
      '"C:\\Users\\chris\\PycharmProjects\\OTLMOW-GUI\\UnitTests\\test_files\\input\\DA-2025-00023_export_sdf_corrupted_example.sdf" \n'
      'Fout:\n'
      '\n'
      '\n'
      'OSGeo.FDO.Common.Exception: File is not an SDF file, or is an SDF file with '
      'an unsupported version.  ---> OSGeo.FDO.Common.Exception: An error occurred '
      'during SDF database access.  \n'
      '   --- End of inner exception stack trace ---\n'
      '   at OSGeo.FDO.Connections.IConnectionImp.Open()\n'
      '   at FdoCmd.Commands.ProviderConnectionCommand.Execute()\n'))
], ids=["invalid_sdf_content"])
def test_get_classes_from_SDF_file_error(root_directory,create_translations,rel_sdf_file_path,expected_exception,expected_error_msg):

    sdf_path_example = root_directory / rel_sdf_file_path

    with pytest.raises(expected_exception) as exc_info:
        output = SDFHandler._get_classes_from_SDF_file(sdf_path_example)

    # addin the correct absolute path in the expected error
    if '{0}' in expected_error_msg:
        expected_error_msg = expected_error_msg.format(sdf_path_example)

    if expected_exception == FileNotFoundError:
        assert exc_info.value.args[0] == expected_error_msg
    else:
        assert str(exc_info.value) == expected_error_msg

@pytest.mark.skip
@pytest.mark.parametrize("rel_sdf_file_path, sdf_class, expected_output", [
    ("UnitTests/test_files/input/DA-2024-03992_export_sdf_example.sdf", 'OTL_Brandblusser',
     Path("UnitTests/test_files/output_ref/output_get_object_from_class_DA-2024-03992_export.txt")),
    ("UnitTests/test_files/input/DA-2025-00023_export_sdf_example.sdf", 'OTL_WVLichtmast',
     Path("UnitTests/test_files/output_ref/output_get_object_from_class_DA-2025-00023_export.txt")),
], ids=["DA-2024-03992_export_sdf_example",
        "DA-2025-00023_export_sdf_example"])
def test_get_objects_from_class(root_directory,rel_sdf_file_path, sdf_class,expected_output):

    sdf_path_example = root_directory / rel_sdf_file_path
    output = SDFHandler._get_objects_from_class(sdf_path_example, sdf_class)

    if isinstance(expected_output,Path):
        # the expected_output can be big so it is eassier to store it in file sometimes
        expected_output_path = root_directory / expected_output

        with open(expected_output_path.absolute(), mode="r", encoding="utf-8") as expected_output_file:
            expected_output = expected_output_file.read()

    assert output == expected_output + "\n"

@pytest.mark.skip
@pytest.mark.parametrize("rel_sdf_file_path,sdf_class,expected_exception,expected_error_msg", [
     ("UnitTests/test_files/input/DA-2025-00023_export_sdf_corrupted_example.sdf","",FDOToolboxProcessError,
      ('Er is een fout opgetreden tijdens de FDO-toolbox-oproep: \n'
       'Oproep: "C:\\Program Files\\FDO Toolbox\\FdoCmd.exe" query-features --class '
       '"" --from-file '
       '"C:\\Users\\chris\\PycharmProjects\\OTLMOW-GUI\\UnitTests\\test_files\\input\\DA-2025-00023_export_sdf_corrupted_example.sdf"  '
       '--format CSV \n'
       'Fout:\n'
       '\n'
       '\n'
       'OSGeo.FDO.Common.Exception: File is not an SDF file, or is an SDF file with '
       'an unsupported version.  ---> OSGeo.FDO.Common.Exception: An error occurred '
       'during SDF database access.  \n'
       '   --- End of inner exception stack trace ---\n'
       '   at OSGeo.FDO.Connections.IConnectionImp.Open()\n'
       '   at FdoCmd.Commands.ProviderConnectionCommand.Execute()\n')),
    ("UnitTests/test_files/input/DA-2024-03992_export_sdf_example.sdf","class_not_in_sdf",FDOToolboxProcessError,
     (('Er is een fout opgetreden tijdens de FDO-toolbox-oproep: \n'
     'Oproep: "C:\\Program Files\\FDO Toolbox\\FdoCmd.exe" query-features --class '
     '"class_not_in_sdf" --from-file '
     '"C:\\Users\\chris\\PycharmProjects\\OTLMOW-GUI\\UnitTests\\test_files\\input\\DA-2024-03992_export_sdf_example.sdf"  '
     '--format CSV \n'
     'Fout:\n'
     '\n'
     '\n'
     "OSGeo.FDO.Common.Exception: Class 'class_not_in_sdf' is not found. \n"
     '   at OSGeo.FDO.Commands.Feature.ISelectImp.Execute()\n'
     '   at FdoCmd.Commands.QueryFeaturesCommand.ExecuteCommand(IConnection conn, '
     'String provider, ISelect cmd)\n'
     '   at '
     'FdoCmd.Commands.ProviderConnectionCommand`1.ExecuteConnection(IConnection '
     'conn, String provider)\n'
     '   at FdoCmd.Commands.ProviderConnectionCommand.Execute()\n')))
], ids=["invalid_sdf_content",
        "class_not_in_sdf"])
def test_get_objects_from_class_error(root_directory,create_translations,rel_sdf_file_path,sdf_class,expected_exception,expected_error_msg):

    sdf_path_example = root_directory / rel_sdf_file_path

    with pytest.raises(expected_exception) as exc_info:
        output = SDFHandler._get_objects_from_class(sdf_path_example, sdf_class)

    # adding the correct absolute path in the expected error
    if '{0}' in expected_error_msg:
        expected_error_msg = expected_error_msg.format(sdf_path_example)

    if expected_exception == FileNotFoundError:
        assert exc_info.value.args[0] == expected_error_msg
    else:
        assert str(exc_info.value) == expected_error_msg

@pytest.mark.skip
@pytest.mark.parametrize("rel_sdf_file_path, rel_csv_output_file_path, expected_output_dirpath, expected_output_file_basename", [
    # ("UnitTests/test_files/input/DA-2024-03992_export_sdf_example.sdf",
    #  Path("UnitTests/test_files/output_test/convert_SDF_to_CSV_DA-2024-03992_export/da-2024-03992_export.csv"),
    #  Path("UnitTests/test_files/output_ref/convert_SDF_to_CSV_DA-2024-03992_export"),"da-2024-03992_export"),

    ("UnitTests/test_files/input/DA-2025-00023_export_sdf_example.sdf",
     Path("UnitTests/test_files/output_test/convert_SDF_to_CSV_DA-2025-00023_export/da-2025-00023_export.csv"),
     Path("UnitTests/test_files/output_ref/convert_SDF_to_CSV_DA-2025-00023_export"),"da-2025-00023_export"),

    # ("UnitTests/test_files/input/DA-2024-03992_export_sdf_example.sdf",
    #  Path("UnitTests/test_files/output_test/convert_SDF_to_CSV_DA-2024-03992_export_csv_output_dir_given"),
    #  Path("UnitTests/test_files/output_ref/convert_SDF_to_CSV_DA-2024-03992_export"),"da-2024-03992_export"),

    ("UnitTests/test_files/input/DA-2025-00023_export_sdf_example.sdf",
     Path("UnitTests/test_files/output_test/convert_SDF_to_CSV_DA-2025-00023_export_csv_output_dir_given"),
     Path("UnitTests/test_files/output_ref/convert_SDF_to_CSV_DA-2025-00023_export"),"da-2025-00023_export")

], ids=[
    # "DA-2024-03992_export_sdf_example",
        "DA-2025-00023_export_sdf_example",
        # "DA-2024-03992_export_sdf_example_csv_output_dir_given",
        "DA-2025-00023_export_sdf_example_csv_output_dir_given"])
def test_convert_SDF_to_CSV(root_directory,create_translations,cleanup_after_creating_a_file_to_delete,
                            rel_sdf_file_path:str, rel_csv_output_file_path:Path,
                            expected_output_dirpath:Path,expected_output_file_basename:str):

    sdf_path_example = root_directory / rel_sdf_file_path
    csv_output_path = root_directory / rel_csv_output_file_path
    expected_output_path = root_directory / expected_output_dirpath

    # format the expected output csv files based on the classes in the sdf file

    output_classes = SDFHandler._get_classes_from_SDF_file(sdf_path_example)
    # build absolute paths to csv of test output
    if ((os.path.exists(csv_output_path) and os.path.isdir(csv_output_path)) or
            csv_output_path.suffix == ""):
        test_output_basepath: str = str(csv_output_path)
        test_output_filepath_list = [str(
                    Path(test_output_basepath) / f"{otlclass}.csv") for otlclass in
                                     output_classes]
    else:
        test_output_basepath: str = os.path.splitext(csv_output_path)[0]
        test_output_filepath_list = [test_output_basepath + otlclass + ".csv" for otlclass in
                                     output_classes]

    # build absolute paths to csv of expected output
    expected_output_basepath: str = str((expected_output_path / expected_output_file_basename).absolute())
    expected_output_filepath_list = [(expected_output_basepath + otlclass + " .csv"
                                      if ("Seinbrug" not in otlclass and "Voedingskabel" not in otlclass)
                                      else expected_output_basepath + otlclass + ".csv")
                                     for otlclass in output_classes]

    #Setup cleanup
    cleanup_after_creating_a_file_to_delete.extend(test_output_filepath_list)

    #Act
    SDFHandler.convert_SDF_to_CSV(sdf_filepath=sdf_path_example,
                                  csv_output_path=csv_output_path)

    #Test
    for i in range(len(test_output_filepath_list)):

        filepath_of_test_output_csv_for_one_class = test_output_filepath_list[i]
        assert(os.path.exists(filepath_of_test_output_csv_for_one_class))

        filepath_of_expected_output_csv_for_one_class = expected_output_filepath_list[i]
        if not os.path.exists(filepath_of_expected_output_csv_for_one_class):
            raise FileNotFoundError(f"Reference file doesn't exist: {filepath_of_expected_output_csv_for_one_class}")

        #read test and expected output file and compare
        test_output_content = Path(filepath_of_test_output_csv_for_one_class).read_text()
        expected_output_content = Path(filepath_of_expected_output_csv_for_one_class).read_text().replace("mmÃƒâ€šÃ‚Â²","mmÃ‚Â²")

        assert(test_output_content == expected_output_content)

@pytest.mark.skip
@pytest.mark.parametrize("rel_sdf_file_path, rel_csv_output_file_path, expected_exception,expected_error_msg", [
    ("UnitTests/test_files/input/does_not_exist.sdf",
     Path("UnitTests/test_files/output_test/convert_SDF_to_CSV_DA-2024-03992_export/da-2024-03992_export.csv"),
     FileNotFoundError,
     "{0} is not a valid path. File does not exist."),

    ("UnitTests/test_files/input/wrong_type_for_sdf.txt",
     Path("UnitTests/test_files/output_test/convert_SDF_to_CSV_DA-2024-03992_export/da-2024-03992_export.csv"),
     WrongFileTypeError,
     ('Het pad naar het opgegeven bestand is niet een SDF-file bestand met extensie (.sdf)\n')),

    ("UnitTests/test_files/input/DA-2025-00023_export_sdf_corrupted_example.sdf",
     Path(
         "UnitTests/test_files/output_test/convert_SDF_to_CSV_DA-2024-03992_export/da-2024-03992_export.csv"),
     FDOToolboxProcessError,
     ('Er is een fout opgetreden tijdens de FDO-toolbox-oproep: \n'
      'Oproep: "C:\\Program Files\\FDO Toolbox\\FdoCmd.exe" list-classes '
      '--from-file '
      '"C:\\Users\\chris\\PycharmProjects\\OTLMOW-GUI\\UnitTests\\test_files\\input\\DA-2025-00023_export_sdf_corrupted_example.sdf" \n'
      'Fout:\n'
      '\n'
      '\n'
      'OSGeo.FDO.Common.Exception: File is not an SDF file, or is an SDF file with '
      'an unsupported version.  ---> OSGeo.FDO.Common.Exception: An error occurred '
      'during SDF database access.  \n'
      '   --- End of inner exception stack trace ---\n'
      '   at OSGeo.FDO.Connections.IConnectionImp.Open()\n'
      '   at FdoCmd.Commands.ProviderConnectionCommand.Execute()\n'))
], ids=["no_file",
        "not_a_sdf_file",
        "invalid_sdf_content"])
def test_convert_SDF_to_CSV_error(root_directory,create_translations,
                                  rel_sdf_file_path,rel_csv_output_file_path,
                                  expected_exception,expected_error_msg):

    sdf_path_example = root_directory / rel_sdf_file_path
    csv_output_path = root_directory / rel_csv_output_file_path

    with pytest.raises(expected_exception) as exc_info:
        # Act
        SDFHandler.convert_SDF_to_CSV(sdf_filepath=sdf_path_example,
                                      csv_output_path=csv_output_path)

    # adding the correct absolute path in the expected error
    if '{0}' in expected_error_msg:
        expected_error_msg = expected_error_msg.format(sdf_path_example)

    if expected_exception == FileNotFoundError:
        assert exc_info.value.args[0] == expected_error_msg
    else:
        assert str(exc_info.value) == expected_error_msg

@fixture
def mock_wrong_FDOToolbox_path():
    original_path = global_vars.FDO_toolbox_path_str
    global_vars.FDO_toolbox_path_str = 'C:\\Program Files\\FDO Toolbox\\FdoCmd1_wrong.exe'
    yield
    global_vars.FDO_toolbox_path_str = original_path

@pytest.mark.skip
def test_convert_SDF_to_CSV_FDOToolbox_not_installed_error(root_directory,create_translations,mock_wrong_FDOToolbox_path):

    #setup test
    rel_sdf_file_path = "UnitTests/test_files/input/DA-2024-03992_export_sdf_example.sdf"
    rel_csv_output_file_path = Path("UnitTests/test_files/output_test/convert_SDF_to_CSV_DA-2024-03992_export/da-2024-03992_export.csv")
    expected_exception = FDOToolboxNotInstalledError
    expected_error_msg = ('FDO toolbox executable kon niet gevonden worden.\n'
                         'Waarschijnlijk omdat het niet (correct) is geïnstalleerd",\n'
                         'U kunt de OTL wizard installer opnieuw uitvoeren met admin privileges om '
                         'deze fout te verhelpen.\n'
                         'Zorg ervoor dat het in de juiste directory is geïnstalleerd, zodat het '
                         'volgende pad bestaat: \n'
                         'C:\\Program Files\\FDO Toolbox\\FdoCmd1_wrong.exe\n')

    sdf_path_example = root_directory / rel_sdf_file_path
    csv_output_path = root_directory / rel_csv_output_file_path

    with pytest.raises(expected_exception) as exc_info:
        # Act
        SDFHandler.convert_SDF_to_CSV(sdf_filepath=sdf_path_example,
                                      csv_output_path=csv_output_path)

    assert str(exc_info.value) == expected_error_msg

# cannot really compare 2 SDF on content alone (ignoring metadata such as date of creation)
# these SDF's have no objects only class-definitions
@pytest.mark.skip
@pytest.mark.parametrize(
    "rel_input_xsd_path, rel_output_sdf_path, expected_output_dirpath, expected_output_file_basename",
    [
        (Path("UnitTests/test_files/input/created_wegkantkast.xsd"),
     Path("UnitTests/test_files/output_test/created-wegkantkast-3-2-empty.sdf"),
     Path("UnitTests/test_files/output_ref"),"created-wegkantkast-3-2-empty.sdf")
     ],
    ids=[
        "created-wegkantkast"
    ])
def test_convert_XSD_to_SDF(root_directory,create_translations,cleanup_after_creating_a_file_to_delete,
                       rel_input_xsd_path: Path, rel_output_sdf_path: Path,
                       expected_output_dirpath:Path,expected_output_file_basename:str):

    #SETUP
    input_xsd_path = root_directory / rel_input_xsd_path
    output_sdf_path = root_directory / rel_output_sdf_path
    cleanup_after_creating_a_file_to_delete.append(output_sdf_path)

    #ACT
    SDFHandler._convert_XSD_to_SDF(input_xsd_path=input_xsd_path, output_sdf_path=output_sdf_path)

    #TEST
    assert output_sdf_path.exists()

    with open(output_sdf_path, mode="r") as output_sdf_file:
        output_test = output_sdf_file.read()

    expected_output_path = root_directory / expected_output_dirpath / expected_output_file_basename
    with open(expected_output_path.absolute(), mode="r") as expected_output_file:
        expected_output = expected_output_file.read()

    assert output_test == expected_output


@pytest.mark.skip
def test_create_sdf_from_filtered_subset_slagbomen(root_directory,cleanup_after_creating_a_file_to_delete):
    # SETUP
    kast_path = root_directory / 'UnitTests' /'test_files' / 'input' / 'voorbeeld-slagboom.db'
    created_path = root_directory / 'UnitTests' / 'test_files' / 'output_test' / 'xsd_export_no_contactor_no_kokerafsluiting.sdf'
    selected_classes_typeURI_list = ["https://wegenenverkeer.data.vlaanderen.be/ns/installatie#Slagboom",
                                     "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Slagboomarm",
                                     "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#SlagboomarmVerlichting",
                                     "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#Slagboomkolom"]
    cleanup_after_creating_a_file_to_delete.append(created_path)

    # ACT
    SDFHandler.create_filtered_SDF_from_subset(subset_path=kast_path, sdf_path=created_path,
                                               selected_classes_typeURI_list=selected_classes_typeURI_list)

    # TEST
    created_sdf = Path(created_path)
    expected_sdf = (root_directory / 'UnitTests' / 'test_files' / 'output_ref' /  'test_sdf_slagboom_new.sdf')

    with open(created_sdf,mode="rb") as created_sdf_file:
        created_sdf_bytes = created_sdf_file.read()
    with open(expected_sdf, mode="rb") as expected_sdf_file:
        expected_sdf_bytes= expected_sdf_file.read()

    assert created_sdf_bytes == expected_sdf_bytes
