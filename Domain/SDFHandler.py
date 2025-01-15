import os
import re
import subprocess
import sys
from pathlib import Path
ROOT_DIR =  Path(Path(__file__).absolute()).parent.parent
sys.path.insert(0,str(ROOT_DIR.absolute()))# needed for python to import project files

from Exceptions.FDOToolboxProcessError import FDOToolboxProcessError
from Exceptions.WrongFileTypeError import WrongFileTypeError
from GUI.translation.GlobalTranslate import GlobalTranslate


class SDFHandler:
    FDO_toolbox_path_str =  'C:\\Program Files\\FDO Toolbox\\FdoCmd.exe'


    @classmethod
    def _get_classes_from_SDF_file(cls, sdf_file_path:Path) -> list[str]:

        sdf_file_path_str = sdf_file_path.absolute()
        command = f'"{cls.FDO_toolbox_path_str}" list-classes --from-file "{sdf_file_path_str}"'

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
        pattern = re.compile(
            r'\(\d+\) DefaultDir: "C:\\ProgramData\\Autodesk\\Geospatial Coordinate Systems" is not a directory! Install the Coordinate System library into this directory or set MENTOR_DICTIONARY_PATH to where they are currently installed\.\n'
            r'\(\d+\) MgCoordinateSystemInitializationFailedException caught in CCoordinateSystemCatalog constructor - The coordinate system initialization failed\.\n\n'
            r'- MgCoordinateSystemCatalog\.SetDefaultDictionaryDirAndFileNames\(\) line 603 file \.\.\\CoordinateSystem\\CoordSysCatalog\.cpp\n'
            r'- MgCoordinateSystemCatalog\.GetDefaultDictionaryDir\(\) line 263 file \.\.\\CoordinateSystem\\CoordSysCatalog\.cpp'
        )
        filtered_error, instance_count = pattern.subn("", error)
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
        command = f'"{cls.FDO_toolbox_path_str}" query-features --class "{sdf_class}" --from-file "{sdf_file_path_str}"  --format CSV'

        output, error = cls.run_command(command)
        if error:
            cls._filter_out_coordinate_system_not_installed_error(command, error)

        output = output.replace("_",".")
        output = output.replace("Geometry", "geometry")
        output = output.replace("XYZ", "Z")

        return output + "\n" # added for compatibility with old OTL-wizard csv generation

    @classmethod
    def convert_SDF_to_CSV(cls, sdf_filepath:Path=None, csv_output_path:Path=None) -> None:

        cls._validate_SDF_file(sdf_filepath)

        # format the expected output csv files based on the classes in the sdf file
        output_classes: list[str] = SDFHandler._get_classes_from_SDF_file(sdf_filepath)
        if ((os.path.exists(csv_output_path) and os.path.isdir(csv_output_path)) or
            csv_output_path.suffix == ""):
            output_basepath: str = str(csv_output_path / "")
            os.makedirs(csv_output_path, exist_ok=True)
        else:
            output_basepath: str = os.path.splitext(csv_output_path)[0]
            os.makedirs(csv_output_path.parent, exist_ok=True)

        for otlclass in output_classes:

            objects_str:str = SDFHandler._get_objects_from_class(sdf_filepath=sdf_filepath, sdf_class=otlclass)

            # build absolute path to csv of output
            filepath_of_output_csv_for_one_class = output_basepath + otlclass + ".csv"

            with open(filepath_of_output_csv_for_one_class,mode='w+') as output_csv_file:
                output_csv_file.write(objects_str)


    @classmethod
    def run_command(cls,command):
        # Using subprocess.run to execute the command without opening a terminal window
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True)
        return result.stdout.strip(), result.stderr.strip()


if __name__ == "__main__":
    settings = {"language": "ENGLISH"}
    root = Path(Path(__file__).absolute()).parent.parent
    GlobalTranslate(settings, root/ 'locale')
    # sdf_path_input = Path("C:\\Users\\chris\\Documents\\job_related\\wegen_en_verkeer\\new_python_otl_wizard\\testData\\Ruben_SDF_test\\DA-2024-03992_export\\download.sdf")
    sdf_path_input = Path(
        "C:\\Users\\chris\\Documents\\job_related\\wegen_en_verkeer\\new_python_otl_wizard\\testData\\Ruben_SDF_test\\DA-2025-00023_export\\download.sdf")

    # sdf_file_classes = SDFHandler.get_classes_from_SDF_file(sdf_file_path=sdf_path_input)
    # sdf_objects = SDFHandler.get_objects_from_class(sdf_file_path=sdf_path_input,sdf_class="OTL_Brandblusser")
    # sdf_objects = SDFHandler.get_objects_from_class(sdf_filepath=sdf_path_input, sdf_class="OTL_Voedingskabel")
    # print(sdf_objects)

    # write output to test files
    # output = root / "UnitTests\\test_files\\output_ref\\output_get_object_from_class_DA-2025-00023_export.txt"
    output_csv = root / "UnitTests\\test_files\\output_test\\convert_SDF_to_CSV_DA-2025-00023_export\\test_DA-2024-03992_export.csv"

    SDFHandler.convert_SDF_to_CSV(sdf_path_input,output_csv)

