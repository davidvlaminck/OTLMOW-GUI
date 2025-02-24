import logging
import os
import re
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Optional

import otlmow_converter
from otlmow_converter.DotnotationDictConverter import DotnotationDictConverter
from otlmow_converter.OtlmowConverter import OtlmowConverter
from otlmow_model.OtlmowModel.Helpers import OTLObjectHelper
from universalasync import async_to_sync_wraps

from Domain import global_vars
from Domain.Helpers import Helpers
from Domain.XSDCreator import XSDCreator
from Domain.logger.OTLLogger import OTLLogger
from Exceptions.FDOToolboxNotInstalledError import FDOToolboxNotInstalledError
from Exceptions.NotASqlliteFileError import NotASqlliteFileError
from UnitTests.TestModel.OtlmowModel.BaseClasses.OTLObject import OTLObject, \
    dynamic_create_type_from_uri

ROOT_DIR =  Path(Path(__file__).absolute()).parent.parent
sys.path.insert(0,str(ROOT_DIR.absolute()))# needed for python to import project files

from Exceptions.FDOToolboxProcessError import FDOToolboxProcessError
from Exceptions.WrongFileTypeError import WrongFileTypeError
from GUI.translation.GlobalTranslate import GlobalTranslate


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
    def _get_schema_name_from_SDF_file(cls,sdf_file_path:Path) -> str:

        sdf_file_path_str = sdf_file_path.absolute()
        command = f'"{global_vars.FDO_toolbox_path_str}" list-schemas --from-file "{sdf_file_path_str}"'

        output, error = cls.run_command(command=command)

        if error:
            cls._filter_out_coordinate_system_not_installed_error(command=command, error=error)

        if output:
            return output
        else:
            return ""
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
    def _validate_SDF_file(cls, sdf_filepath: Path) -> None:
        if not sdf_filepath.exists():
            raise FileNotFoundError(f'{sdf_filepath} is not a valid path. File does not exist.')
        if sdf_filepath.suffix != ".sdf":
            raise WrongFileTypeError(language=GlobalTranslate._,
                                     expected_filetype_name="SDF-file",
                                     expected_filetype_suffix=".sdf")

    @classmethod
    def _validate_XSD_file(cls, xsd_filepath:Path) -> None:
        if not xsd_filepath.exists():
            raise FileNotFoundError(f'{xsd_filepath} is not a valid path. File does not exist.')
        # XSD files a special type of xml file sometimes the extension is .xml
        if xsd_filepath.suffix != ".xml" and xsd_filepath.suffix != ".xsd":
            raise WrongFileTypeError(language=GlobalTranslate._,
                                     expected_filetype_name="XSD-file",
                                     expected_filetype_suffix=".xsd")

    @classmethod
    def _force_to_SDF_extension(cls, sdf_filepath:Path) -> Path:
        if sdf_filepath.suffix != ".sdf":
            return sdf_filepath.parent / f"{sdf_filepath.stem}.sdf"
        return sdf_filepath

    @classmethod
    def _force_to_SQLite_extension(cls, sqlite_filepath: Path) -> Path:
        if sqlite_filepath.suffix != ".db":
            return sqlite_filepath.parent / f"{sqlite_filepath.stem}.db"
        return sqlite_filepath

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

        cls._check_if_FDOToolbox_is_installed()
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
    def _check_if_FDOToolbox_is_installed(cls):
        if not os.path.exists(global_vars.FDO_toolbox_path_str):
            raise FDOToolboxNotInstalledError(GlobalTranslate._)

    @classmethod
    def _convert_XSD_to_SDF(cls, input_xsd_path:Path, output_sdf_path:Path) -> None:

        output_sdf_path = cls._force_to_SDF_extension(output_sdf_path)

        sdf_file_path_str = output_sdf_path.absolute()
        input_xsd_path_str = input_xsd_path.absolute()

        command = (f'"{global_vars.FDO_toolbox_path_str}" create-file '
                   f'--file "{sdf_file_path_str}"  --schema-path "{input_xsd_path_str}"')
        OTLLogger.logger.debug(f"convert_XSD_to_SDF:\n{command}", extra={"ref_timing":"convert_XSD_to_SDF"})
        output, error = cls.run_command(command)
        OTLLogger.logger.debug(f"convert_XSD_to_SDF:\n{output}", extra={"ref_timing":"convert_XSD_to_SDF"})

        if error:
            cls._filter_out_coordinate_system_not_installed_error(command, error)

    @classmethod
    def _convert_XSD_to_SQLite(cls, input_xsd_path: Path, output_sqlite_path: Path) -> None:

        output_sqlite_path = cls._force_to_SQLite_extension(output_sqlite_path)

        sdf_file_path_str = output_sqlite_path.absolute()
        input_xsd_path_str = input_xsd_path.absolute()

        command = (f'"{global_vars.FDO_toolbox_path_str}" create-file '
                   f'--file "{sdf_file_path_str}"  --schema-path "{input_xsd_path_str}"')
        OTLLogger.logger.debug(f"convert_XSD_to_SDF:\n{command}",
                               extra={"ref_timing": "convert_XSD_to_SQLite"})
        output, error = cls.run_command(command)
        OTLLogger.logger.debug(f"convert_XSD_to_SDF:\n{output}",
                               extra={"ref_timing": "convert_XSD_to_SQLite"})

        if error:
            cls._filter_out_coordinate_system_not_installed_error(command, error)

    @classmethod
    @async_to_sync_wraps
    async def create_filtered_SDF_from_subset(cls, subset_path: Path, sdf_path: Path,
                                        selected_classes_typeURI_list: Optional[list[str]]=None,
                                        model_directory: Path = None) -> None:

        cls._check_if_FDOToolbox_is_installed()

        temp_xsd_filename_path = Path(f'{sdf_path.stem}.xsd')
        temp_path: Path = Helpers.create_temp_path(
            path_to_template_file_and_extension=temp_xsd_filename_path)

        await XSDCreator.create_filtered_xsd_from_subset(
            subset_path=subset_path,xsd_path=temp_path,
            selected_classes_typeURI_list=selected_classes_typeURI_list,
            model_directory=model_directory)

        SDFHandler._convert_XSD_to_SDF(input_xsd_path=temp_path,output_sdf_path=sdf_path)

    @classmethod
    @async_to_sync_wraps
    async def create_filtered_SQLite_from_subset(cls, subset_path: Path, sqlite_path: Path,
                                                 selected_classes_typeURI_list: Optional[
                                                  list[str]] = None,
                                                 model_directory: Path = None) -> None:

        cls._check_if_FDOToolbox_is_installed()

        temp_xsd_filename_path = Path(f'{sqlite_path.stem}.xsd')
        temp_path: Path = Helpers.create_temp_path(
            path_to_template_file_and_extension=temp_xsd_filename_path)


        await XSDCreator.create_filtered_xsd_from_subset(
            subset_path=subset_path, xsd_path=temp_path,
            selected_classes_typeURI_list=selected_classes_typeURI_list,
            model_directory=model_directory)

        SDFHandler._convert_XSD_to_SQLite(input_xsd_path=temp_path, output_sqlite_path=sqlite_path)

    @classmethod
    def copy_SQLite_data_to_SDF_file(cls,source_sqlite_path:Path,target_sdf_path:Path, dest_class:str):

        source_sqlite_file_path_str = source_sqlite_path.absolute()
        target_sdf_path_str = target_sdf_path.absolute()

        schema_name = cls._get_schema_name_from_SDF_file(target_sdf_path)
        print(f"schema  {schema_name}")

        command = (f'"{global_vars.FDO_toolbox_path_str}" copy-class --dst-class {dest_class} --dst-connect-params File "{target_sdf_path_str}" --dst-schema {schema_name} --src-class {dest_class} --src-connect-params File "{source_sqlite_file_path_str}" --src-schema Default --dst-provider OSGeo.SDF --src-provider OSGeo.SQLite')
        OTLLogger.logger.debug(f"convert_XSD_to_SDF:\n{command}",
                               extra={"ref_timing": "copy_SQLite_data_to_SDF_file"})
        output, error = cls.run_command(command)
        OTLLogger.logger.debug(f"convert_XSD_to_SDF:\n{output}",
                               extra={"ref_timing": "copy_SQLite_data_to_SDF_file"})

        if error:
            cls._filter_out_coordinate_system_not_installed_error(command, error)

    @classmethod
    @async_to_sync_wraps
    async def convert_object_to_SDF_file(cls, object_list: list[OTLObject], output_sdf_path:Path):

        # create temporary XSD schema from objects in memory
        temp_xsd_filename_path = output_sdf_path.parent / f'{output_sdf_path.stem}.xsd'
        temp_path: Path = Helpers.create_temp_path(
            path_to_template_file_and_extension=temp_xsd_filename_path)
        # temp_path = temp_xsd_filename_path
        await XSDCreator.create_xsd_from_objects(object_list=object_list,xsd_path=temp_path)



        # create temporary sqlite from XSD schema
        temp_sqlite_filename_path = output_sdf_path.parent / f'{output_sdf_path.stem}.db'
        temp_path_sqlite: Path = Helpers.create_temp_path(
            path_to_template_file_and_extension=temp_sqlite_filename_path)
        # temp_path_sqlite = temp_sqlite_filename_path

        cls._convert_XSD_to_SQLite(input_xsd_path=temp_path, output_sqlite_path=temp_path_sqlite)

        # create SDF from XSD schema
        cls._convert_XSD_to_SDF(input_xsd_path=temp_path, output_sdf_path=output_sdf_path)

        # fill SQLite file with object data
        try:
            connection = sqlite3.connect(temp_path_sqlite)
            cursor = connection.cursor()


            for object_ in object_list:
                object_dict = await DotnotationDictConverter.to_dict(object_)
                object_class = dynamic_create_type_from_uri(object_.typeURI)



                table_name = f"OTL_{object_class.__name__}"

                placeholders = ', '.join(['?'] * len(object_dict))
                columns_str = ', '.join('"' +col.replace(".","_")+'"' for col in object_dict.keys())
                sql = f'INSERT INTO "{table_name}" ({columns_str}) VALUES ({placeholders})'

                values = list(object_dict.values())
                for i in range(len(values)):
                    if isinstance(values[i],str):
                        values[i] = values[i].replace(" Z "," XYZ ")
                logging.debug(values)

                # Execute the statement
                cursor.execute(sql, values)

            # Commit changes and close the connection
            connection.commit()

            connection.close()
        except sqlite3.OperationalError as e:
            OTLLogger.logger.error(e)
            raise NotASqlliteFileError(e)

        for object_ in object_list:

            object_class = dynamic_create_type_from_uri(object_.typeURI)

            table_name = f"OTL_{object_class.__name__}"

            # copy SQLite data into SDF file
            cls.copy_SQLite_data_to_SDF_file(source_sqlite_path=temp_path_sqlite,
                                             target_sdf_path=output_sdf_path,dest_class=table_name)


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

