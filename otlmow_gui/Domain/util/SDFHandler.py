import logging
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

from otlmow_gui.Domain import global_vars
from otlmow_gui.Domain.util.Helpers import Helpers
from otlmow_gui.Domain.util.XSDCreator import XSDCreator
from otlmow_gui.Domain.logger.OTLLogger import OTLLogger
from otlmow_gui.Exceptions.FDOToolboxNotInstalledError import FDOToolboxNotInstalledError

ROOT_DIR =  Path(Path(__file__).absolute()).parent.parent
sys.path.insert(0,str(ROOT_DIR.absolute()))# needed for python to import project files

from otlmow_gui.Exceptions.FDOToolboxProcessError import FDOToolboxProcessError
from otlmow_gui.Exceptions.WrongFileTypeError import WrongFileTypeError
from otlmow_gui.GUI.translation.GlobalTranslate import GlobalTranslate


class SDFHandler:
    """
    documentation for FDOcmd.exe:
    https://jumpinjackie.github.io/fdotoolbox/userdoc/1.5.0/cmdline.html?highlight=fdocmd
    """


    @classmethod
    def _get_classes_from_SDF_file(cls, sdf_file_path:Path) -> list[str]:

        sdf_file_path_str = sdf_file_path.absolute()
        command = f'"{global_vars.FDO_toolbox_path_str}" list-classes --from-file "{sdf_file_path_str}"'

        output, error = cls.run_command(command=command)

        if error:
            cls._filter_out_coordinate_system_not_installed_error(command=command, error=error)

        if output:
            return output.split("\n")
        else:
            return []

    @classmethod
    def _filter_out_coordinate_system_not_installed_error(cls, command:str, error:str) -> None:
        # The following error occurs even though the program works properly
        # Here we filter out this error to be able to capture and use other critical errors
        pattern1 = re.compile(
            r'\(\d+\) DefaultDir: "C:\\ProgramData\\Autodesk\\Geospatial Coordinate Systems" is not a directory! Install the Coordinate System library into this directory or set MENTOR_DICTIONARY_PATH to where they are currently installed\.\n'
            r'\(\d+\) MgCoordinateSystemInitializationFailedException caught in CCoordinateSystemCatalog constructor - The coordinate system initialization failed\.\n\n'
            r'- MgCoordinateSystemCatalog\.SetDefaultDictionaryDirAndFileNames\(\) line 603 file \.\.\\CoordinateSystem\\CoordSysCatalog\.cpp\n'
            r'- MgCoordinateSystemCatalog\.GetDefaultDictionaryDir\(\) line 263 file \.\.\\CoordinateSystem\\CoordSysCatalog\.cpp'
        )
        filtered_error, instance_count = pattern1.subn("", error)

        # pattern2 = re.compile()
        # The following error occurs with the create-file command even though the program works properly
        # Here we filter out this error to be able to capture and use other critical errors
        # negative_precision_error = ('\n'
        #                      '\n'
        #                      'OSGeo.FDO.Common.Exception: A Data Property cannot have a negative '
        #                      'precision. \n'
        #                      '   at OSGeo.FDO.Schema.DataPropertyDefinition.set_Precision(Int32 value)\n'
        #                      '   at '
        #                      'FdoToolbox.Core.Feature.SchemaCapabilityChecker.FixDataProperties(ClassDefinition& '
        #                      'classDef)\n'
        #                      '   at '
        #                      'FdoToolbox.Core.Feature.SchemaCapabilityChecker.AlterClassDefinition(ClassDefinition '
        #                      'classDef, IncompatibleClass incClass, Func`1 getActiveSpatialContext, '
        #                      'Action`2 fixGeomSc)\n'
        #                      '   at '
        #                      'FdoToolbox.Core.Feature.SchemaCapabilityChecker.AlterSchema(FeatureSchema '
        #                      'schema, IncompatibleSchema incompatibleSchema, Func`1 '
        #                      'getActiveSpatialContext)\n'
        #                      '   at FdoToolbox.Core.Feature.FdoFeatureService.LoadSchemasFromXml(String '
        #                      'xmlFile, Boolean fix)\n'
        #                      '   at FdoCmd.Commands.CreateFileCommand.Execute()')
        #
        # filtered_error = filtered_error.replace(negative_precision_error,"")

        if filtered_error:
            raise FDOToolboxProcessError(language=GlobalTranslate._, command=command,
                                         fdo_toolbox_error=filtered_error)


    @classmethod
    def _validate_SDF_file(cls, sdf_filepath) -> None:
        if not sdf_filepath.exists():
            raise FileNotFoundError(f'{sdf_filepath} is not a valid path. File does not exist.')
        if sdf_filepath.suffix != ".sdf":
            raise WrongFileTypeError(language=GlobalTranslate._,
                                     expected_filetype_name="SDF-file",
                                     expected_filetype_suffix=".sdf")

    @classmethod
    def _get_objects_from_class(cls, sdf_filepath, sdf_class) -> str:

        sdf_file_path_str = sdf_filepath.absolute()
        command = f'"{global_vars.FDO_toolbox_path_str}" query-features --class "{sdf_class}" --from-file "{sdf_file_path_str}"  --format CSV'

        output, error = cls.run_command(command)
        if error:
            cls._filter_out_coordinate_system_not_installed_error(command, error)

        output = output.replace("_",".")
        output = output.replace("Geometry", "geometry")
        output = output.replace("XYZ", "Z")

        return output + "\n" # added for compatibility with old OTL-wizard csv generation

    @classmethod
    def convert_SDF_to_CSV(cls, sdf_filepath:Path, csv_output_path:Path) -> list[str]:

        OTLLogger.logger.debug(
            f"Executing Domain.SDFHandler.SDFHandler.convert_SDF_to_CSV for {sdf_filepath.name}",
            extra={"timing_ref": f"validate_{sdf_filepath.name}"})

        output_csv_filepath_list = []

        if not cls.check_if_FDOToolbox_is_installed():
            pass
            # return []
        cls._validate_SDF_file(sdf_filepath)

        # format the expected output csv files based on the classes in the sdf file
        output_classes: list[str] = SDFHandler._get_classes_from_SDF_file(sdf_filepath)
        if ((os.path.exists(csv_output_path) and os.path.isdir(csv_output_path)) or
            csv_output_path.suffix == ""):
            csv_output_path_is_dir = True
            output_basepath: str = str(csv_output_path)
            os.makedirs(csv_output_path, exist_ok=True)
        else:
            csv_output_path_is_dir = False
            output_basepath: str = os.path.splitext(csv_output_path)[0]
            os.makedirs(csv_output_path.parent, exist_ok=True)

        for otlclass in output_classes:

            objects_str:str = SDFHandler._get_objects_from_class(sdf_filepath=sdf_filepath, sdf_class=otlclass)



            # build absolute path to csv of output
            if csv_output_path_is_dir:
                filepath_of_output_csv_for_one_class = str(
                    Path(output_basepath) / f"{otlclass}.csv")
            else:
                filepath_of_output_csv_for_one_class = output_basepath + otlclass + ".csv"

            with open(filepath_of_output_csv_for_one_class,mode='w+') as output_csv_file:
                output_csv_file.write(objects_str)

            logging.debug(f"created file: {filepath_of_output_csv_for_one_class}")
            output_csv_filepath_list.append(filepath_of_output_csv_for_one_class)

        OTLLogger.logger.debug(
            f"Executing Domain.SDFHandler.SDFHandler.convert_SDF_to_CSV for {sdf_filepath.name}",
            extra={"timing_ref": f"validate_{sdf_filepath.name}"})

        return output_csv_filepath_list

    @classmethod
    def run_command(cls,command):
        # Using subprocess.run to execute the command without opening a terminal window
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True)
        return result.stdout.strip(), result.stderr.strip()

    @classmethod
    def check_if_FDOToolbox_is_installed(cls) -> bool:

        try:
            if not os.path.exists(global_vars.FDO_toolbox_path_str):
                raise FDOToolboxNotInstalledError(GlobalTranslate._)
        except FDOToolboxNotInstalledError as e:
            #only show the notification window if the GUI MainWindow object exists²
            if global_vars.otl_wizard and global_vars.otl_wizard.main_window:


                answer = global_vars.otl_wizard.main_window.show_blocking_yes_no_notification_window(
                    text=str(e),
                    title=GlobalTranslate._("FDOToolbox not installed")
                )

                if answer != 16384: # QMessageBox.ButtonRole.NoRole:
                    return False

                test_path = Path(os.getcwd()) / Path(
                    "LatestReleaseMulti\\additional_programs\\FDOToolbox-Release-v1.5.3-x64-Setup.exe")

                if os.path.exists(global_vars.FDO_toolbox_installer_path_str):
                    OTLLogger.logger.debug(f"go to {global_vars.FDO_toolbox_installer_path_str}")
                    subprocess.Popen(f'explorer /select,"{global_vars.FDO_toolbox_installer_path_str}"')
                else:
                    OTLLogger.logger.debug(f"go to {test_path}")
                    subprocess.Popen(
                        f'explorer /select,"{test_path}"')

                return False

                # raise FDOToolboxNotInstalledError(GlobalTranslate._) from e
        return True

    @classmethod
    def _convert_XSD_to_SDF(cls, input_xsd_path:Path, output_sdf_path:Path) -> None:
        sdf_file_path_str = output_sdf_path.absolute()
        input_xsd_path_str = input_xsd_path.absolute()

        command = (f'"{global_vars.FDO_toolbox_path_str}" create-file '
                   f'--file "{sdf_file_path_str}"  --schema-path "{input_xsd_path_str}"')

        output, error = cls.run_command(command)
        OTLLogger.logger.debug(f"convert_XSD_to_SDF:\n{output}")

        if error:

            cls._filter_out_coordinate_system_not_installed_error(command, error)

    @classmethod
    async def create_filtered_SDF_from_subset(cls, subset_path: Path, sdf_path: Path,
                                        selected_classes_typeURI_list: Optional[list[str]]=None,
                                        model_directory: Path = None) -> None:

        if not cls.check_if_FDOToolbox_is_installed():
            pass

        temp_path: Path = Helpers.create_temp_path(path_to_template_file_and_extension=sdf_path)
        temp_path = temp_path.parent / f'{temp_path.name}.xsd'

        await XSDCreator.create_filtered_xsd_from_subset(
            subset_path=subset_path,xsd_path=temp_path,
            selected_classes_typeURI_list=selected_classes_typeURI_list,
            model_directory=model_directory)

        SDFHandler._convert_XSD_to_SDF(input_xsd_path=temp_path,output_sdf_path=sdf_path)

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    settings = {"language": "ENGLISH"}
    root = Path(Path(__file__).absolute()).parent.parent
    GlobalTranslate(settings, root/ 'locale')
    # sdf_path_input = Path("C:\\Users\\chris\\Documents\\job_related\\wegen_en_verkeer\\new_python_otl_wizard\\testData\\Ruben_SDF_test\\DA-2024-03992_export\\download.sdf")
    sdf_path_input = Path(
        "C:\\Users\\chris\\Documents\\job_related\\wegen_en_verkeer\\new_python_otl_wizard\\testData\\Ruben_SDF_test\\DA-2025-00023_export\\download.sdf")

    # sdf_file_classes = SDFHandler.get_classes_from_SDF_file(sdf_file_path=sdf_path_input)
    # sdf_objects = SDFHandler._get_objects_from_class(sdf_file_path=sdf_path_input,sdf_class="OTL_Brandblusser")
    sdf_objects = SDFHandler._get_objects_from_class(sdf_filepath=sdf_path_input, sdf_class="OTL_Voedingskabel")
    print(sdf_objects)

    # write output to test files
    # output = root / "UnitTests\\test_files\\output_ref\\output_get_object_from_class_DA-2025-00023_export.txt"
    # output_csv = root / "UnitTests\\test_files\\output_test\\convert_SDF_to_CSV_DA-2025-00023_export\\test_DA-2024-03992_export.csv"
    # output_csv = root / "C:\\Users\\chris\\Documents\\job_related\\wegen_en_verkeer\\new_python_otl_wizard\\testData\\Ruben_SDF_test\\DA-2025-00023_export\\christiaan_omzetting"
    # SDFHandler.convert_SDF_to_CSV(sdf_path_input,output_csv)

