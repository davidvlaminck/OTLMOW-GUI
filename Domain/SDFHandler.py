import re
import logging
import subprocess
from argparse import FileType
from pathlib import Path

from Exceptions.FDOToolboxProcessError import FDOToolboxProcessError
from Exceptions.WrongFileTypeError import WrongFileTypeError
from GUI.translation.GlobalTranslate import GlobalTranslate


class SDFHandler:
    FDO_toolbox_path_str =  'C:\\Program Files\\FDO Toolbox\\FdoCmd.exe'


    @classmethod
    def get_classes_from_SDF_file(cls, sdf_file_path:Path) -> list[str]:

        if not sdf_file_path.exists():
            raise FileNotFoundError(f'{sdf_file_path} is not a valid path. File does not exist.')

        if sdf_file_path.suffix != ".sdf":
            raise WrongFileTypeError(language=GlobalTranslate._,
                                     expected_filetype_name="SDF-file",
                                     expected_filetype_suffix=".sdf")

        sdf_file_path_str = sdf_file_path.absolute()
        command = f'"{cls.FDO_toolbox_path_str}" list-classes --from-file "{sdf_file_path_str}"'

        output, error = cls.run_command(command)

        if error:
            # The following error occurs even though the program works properly
            # Here we filter out this error to be able to capture and use other critical errors
            pattern = re.compile(
                r'\(\d+\) DefaultDir: "C:\\ProgramData\\Autodesk\\Geospatial Coordinate Systems" is not a directory! Install the Coordinate System library into this directory or set MENTOR_DICTIONARY_PATH to where they are currently installed\.\n'
                r'\(\d+\) MgCoordinateSystemInitializationFailedException caught in CCoordinateSystemCatalog constructor - The coordinate system initialization failed\.\n\n'
                r'- MgCoordinateSystemCatalog\.SetDefaultDictionaryDirAndFileNames\(\) line 603 file \.\.\\CoordinateSystem\\CoordSysCatalog\.cpp\n'
                r'- MgCoordinateSystemCatalog\.GetDefaultDictionaryDir\(\) line 263 file \.\.\\CoordinateSystem\\CoordSysCatalog\.cpp'
            )
            filtered_error,instance_count = pattern.subn("",error)
            if filtered_error:
                raise FDOToolboxProcessError(language=GlobalTranslate._, command=command, fdo_toolbox_error=filtered_error)

        if output:
            return output.split("\n")
        else:
            return []

    @classmethod
    def get_objects_from_class(cls, sdf_file_path, sdf_class):
        command = '"C:\\Program Files\\FDO Toolbox\\FdoCmd.exe" query-features --class "OTL_Brandblusser" --from-file "C:\\Users\\chris\\Documents\\job_related\\wegen_en_verkeer\\new_python_otl_wizard\\testData\\Ruben_SDF_test\\DA-2024-03992_export\\download.sdf"  --format CSV'

        output, error = cls.run_command(command)
        print(output)

    @classmethod
    def convert_SDF_to_CSV(cls,sdf_input_path:Path=None, csv_output_path:Path=None):
        output, error = cls.run_command('ECHO "write me this program"')
        print(output)

    @classmethod
    def run_command(cls,command):
        # Using subprocess.run to execute the command without opening a terminal window
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True)
        return result.stdout.strip(), result.stderr.strip()


if __name__ == "__main__":

    # sdf_path_input = Path("C:\\Users\\chris\\Documents\\job_related\\wegen_en_verkeer\\new_python_otl_wizard\\testData\\Ruben_SDF_test\\DA-2024-03992_export\\download.sdf")
    sdf_path_input = Path(
        "C:\\Users\\chris\\Documents\\job_related\\wegen_en_verkeer\\new_python_otl_wizard\\testData\\Ruben_SDF_test\\DA-2025-00023_export\\download.sdf")

    sdf_file_classes = SDFHandler.get_classes_from_SDF_file(sdf_file_path=sdf_path_input)
    print(sdf_file_classes)