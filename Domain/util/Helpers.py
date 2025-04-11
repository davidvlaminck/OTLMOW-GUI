import asyncio
import base64
import logging
import os
import tempfile
import warnings
from pathlib import Path
from typing import Optional, Iterable

from otlmow_converter.Exceptions.ExceptionsGroup import ExceptionsGroup
from otlmow_converter.OtlmowConverter import OtlmowConverter
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject, \
    dynamic_create_instance_from_ns_and_name, dynamic_create_instance_from_uri
from otlmow_model.OtlmowModel.Classes.Agent import Agent
from otlmow_model.OtlmowModel.Helpers import OTLObjectHelper
from otlmow_model.OtlmowModel.Helpers.GenericHelper import validate_guid
from otlmow_model.OtlmowModel.Helpers.generated_lists import get_hardcoded_class_dict
from packaging.version import Version

from Domain.logger.OTLLogger import OTLLogger
from GUI.dialog_windows.LoadingImageWindow import add_loading_screen
from GUI.screens.RelationChange_elements.RelationChangeHelpers import RelationChangeHelpers


class Helpers:
    all_OTL_asset_types_dict = {}
    legacy_type_uris = {'https://lgc.data.wegenenverkeer.be/ns/installatie#IRVerlichter','https://lgc.data.wegenenverkeer.be/ns/installatie#Voedingskeuzeschakelaar','https://lgc.data.wegenenverkeer.be/ns/installatie#Z30Controller','https://lgc.data.wegenenverkeer.be/ns/installatie#CaDoGroep','https://lgc.data.wegenenverkeer.be/ns/installatie#LWP','https://lgc.data.wegenenverkeer.be/ns/installatie#HY.CI','https://lgc.data.wegenenverkeer.be/ns/installatie#HY.GR','https://lgc.data.wegenenverkeer.be/ns/installatie#Poortbedieningen','https://lgc.data.wegenenverkeer.be/ns/installatie#MotorLegacy','https://lgc.data.wegenenverkeer.be/ns/onderdeel#StuurklepLeiding','https://lgc.data.wegenenverkeer.be/ns/onderdeel#FlexibeleBuis','https://lgc.data.wegenenverkeer.be/ns/installatie#ZoutBijlaadPlaats','https://lgc.data.wegenenverkeer.be/ns/installatie#ITSApp-RIS','https://lgc.data.wegenenverkeer.be/ns/installatie#Zoutsilo','https://lgc.data.wegenenverkeer.be/ns/installatie#Pekeltank','https://lgc.data.wegenenverkeer.be/ns/installatie#BelInstallatie','https://lgc.data.wegenenverkeer.be/ns/installatie#RIOOL','https://lgc.data.wegenenverkeer.be/ns/installatie#LokaalLegacy','https://lgc.data.wegenenverkeer.be/ns/installatie#Dienstdeur','https://lgc.data.wegenenverkeer.be/ns/installatie#FietsTelDisplayLegacy','https://lgc.data.wegenenverkeer.be/ns/installatie#FietsTelSysteemLegacy','https://lgc.data.wegenenverkeer.be/ns/installatie#DPBS','https://lgc.data.wegenenverkeer.be/ns/installatie#DPBSOnd','https://lgc.data.wegenenverkeer.be/ns/installatie#WegDetectorLegacy','https://lgc.data.wegenenverkeer.be/ns/installatie#SegC','https://lgc.data.wegenenverkeer.be/ns/installatie#Netwerktoegang','https://lgc.data.wegenenverkeer.be/ns/installatie#Turbine','https://lgc.data.wegenenverkeer.be/ns/installatie#WeegsensorLegacy','https://lgc.data.wegenenverkeer.be/ns/installatie#WeegsensorGroep','https://lgc.data.wegenenverkeer.be/ns/installatie#Luchtkwaliteitssensor','https://lgc.data.wegenenverkeer.be/ns/installatie#Beacon','https://lgc.data.wegenenverkeer.be/ns/installatie#Leidingkoker','https://lgc.data.wegenenverkeer.be/ns/installatie#SeinBak','https://lgc.data.wegenenverkeer.be/ns/installatie#SeinSpui','https://lgc.data.wegenenverkeer.be/ns/installatie#RLCGUI','https://lgc.data.wegenenverkeer.be/ns/installatie#SlbGroep','https://lgc.data.wegenenverkeer.be/ns/installatie#Calam','https://lgc.data.wegenenverkeer.be/ns/installatie#Glad','https://lgc.data.wegenenverkeer.be/ns/installatie#Ijking','https://lgc.data.wegenenverkeer.be/ns/installatie#VOTLus','https://lgc.data.wegenenverkeer.be/ns/installatie#VVOPGroep','https://lgc.data.wegenenverkeer.be/ns/installatie#Brandvoorz','https://lgc.data.wegenenverkeer.be/ns/installatie#RRGroep','https://lgc.data.wegenenverkeer.be/ns/installatie#AntenneI2V','https://lgc.data.wegenenverkeer.be/ns/installatie#Monitor','https://lgc.data.wegenenverkeer.be/ns/installatie#LuiLegacy','https://lgc.data.wegenenverkeer.be/ns/installatie#NIC','https://lgc.data.wegenenverkeer.be/ns/installatie#Winter','https://lgc.data.wegenenverkeer.be/ns/installatie#Z30Paal','https://lgc.data.wegenenverkeer.be/ns/installatie#Z30','https://lgc.data.wegenenverkeer.be/ns/installatie#Pluvio','https://lgc.data.wegenenverkeer.be/ns/installatie#ARS','https://lgc.data.wegenenverkeer.be/ns/installatie#RHZ','https://lgc.data.wegenenverkeer.be/ns/installatie#Picto','https://lgc.data.wegenenverkeer.be/ns/installatie#Nooddeur','https://lgc.data.wegenenverkeer.be/ns/installatie#KeuringLegacy','https://lgc.data.wegenenverkeer.be/ns/installatie#Deb','https://lgc.data.wegenenverkeer.be/ns/installatie#MON','https://lgc.data.wegenenverkeer.be/ns/installatie#Kwik','https://lgc.data.wegenenverkeer.be/ns/installatie#Div','https://lgc.data.wegenenverkeer.be/ns/installatie#Peil','https://lgc.data.wegenenverkeer.be/ns/installatie#Lev','https://lgc.data.wegenenverkeer.be/ns/installatie#Cal','https://lgc.data.wegenenverkeer.be/ns/installatie#Sensor','https://lgc.data.wegenenverkeer.be/ns/installatie#GebUitr','https://lgc.data.wegenenverkeer.be/ns/installatie#GebouwLegacy','https://lgc.data.wegenenverkeer.be/ns/installatie#ServerGrp','https://lgc.data.wegenenverkeer.be/ns/installatie#Server','https://lgc.data.wegenenverkeer.be/ns/installatie#IVSBGroep','https://lgc.data.wegenenverkeer.be/ns/installatie#SeinbrugIVS','https://lgc.data.wegenenverkeer.be/ns/installatie#MDeC','https://lgc.data.wegenenverkeer.be/ns/installatie#Kast','https://lgc.data.wegenenverkeer.be/ns/installatie#Wilddet','https://lgc.data.wegenenverkeer.be/ns/installatie#Terrein','https://lgc.data.wegenenverkeer.be/ns/installatie#Druk','https://lgc.data.wegenenverkeer.be/ns/installatie#Wind','https://lgc.data.wegenenverkeer.be/ns/installatie#VPBevestig','https://lgc.data.wegenenverkeer.be/ns/installatie#VPConsole','https://lgc.data.wegenenverkeer.be/ns/installatie#KAR','https://lgc.data.wegenenverkeer.be/ns/installatie#RRB','https://lgc.data.wegenenverkeer.be/ns/installatie#RIS','https://lgc.data.wegenenverkeer.be/ns/installatie#Tekstkar','https://lgc.data.wegenenverkeer.be/ns/installatie#SoftwareLegacy','https://lgc.data.wegenenverkeer.be/ns/installatie#MobADR','https://lgc.data.wegenenverkeer.be/ns/installatie#IP','https://lgc.data.wegenenverkeer.be/ns/installatie#TWeg','https://lgc.data.wegenenverkeer.be/ns/installatie#VSB','https://lgc.data.wegenenverkeer.be/ns/installatie#AWeg','https://lgc.data.wegenenverkeer.be/ns/installatie#NWeg','https://lgc.data.wegenenverkeer.be/ns/installatie#BWeg','https://lgc.data.wegenenverkeer.be/ns/installatie#RWeg','https://lgc.data.wegenenverkeer.be/ns/installatie#VOT','https://lgc.data.wegenenverkeer.be/ns/installatie#Instal','https://lgc.data.wegenenverkeer.be/ns/installatie#RTU','https://lgc.data.wegenenverkeer.be/ns/installatie#Kan','https://lgc.data.wegenenverkeer.be/ns/installatie#Com','https://lgc.data.wegenenverkeer.be/ns/installatie#TTN3','https://lgc.data.wegenenverkeer.be/ns/installatie#TTN2','https://lgc.data.wegenenverkeer.be/ns/installatie#TTN1','https://lgc.data.wegenenverkeer.be/ns/installatie#Dummy','https://lgc.data.wegenenverkeer.be/ns/installatie#TraCoLegacy','https://lgc.data.wegenenverkeer.be/ns/installatie#WIM','https://lgc.data.wegenenverkeer.be/ns/installatie#CBBS','https://lgc.data.wegenenverkeer.be/ns/installatie#VWS','https://lgc.data.wegenenverkeer.be/ns/installatie#TGB','https://lgc.data.wegenenverkeer.be/ns/installatie#WKD','https://lgc.data.wegenenverkeer.be/ns/installatie#BAf','https://lgc.data.wegenenverkeer.be/ns/installatie#MVE','https://lgc.data.wegenenverkeer.be/ns/installatie#ICU','https://lgc.data.wegenenverkeer.be/ns/installatie#VDP','https://lgc.data.wegenenverkeer.be/ns/installatie#Veer','https://lgc.data.wegenenverkeer.be/ns/installatie#WV','https://lgc.data.wegenenverkeer.be/ns/installatie#WDM','https://lgc.data.wegenenverkeer.be/ns/installatie#WBr','https://lgc.data.wegenenverkeer.be/ns/installatie#VVOP','https://lgc.data.wegenenverkeer.be/ns/installatie#VRLegacy','https://lgc.data.wegenenverkeer.be/ns/installatie#VL','https://lgc.data.wegenenverkeer.be/ns/installatie#VGL','https://lgc.data.wegenenverkeer.be/ns/installatie#UPSLegacy','https://lgc.data.wegenenverkeer.be/ns/installatie#TuV','https://lgc.data.wegenenverkeer.be/ns/installatie#Tu','https://lgc.data.wegenenverkeer.be/ns/installatie#TTN','https://lgc.data.wegenenverkeer.be/ns/installatie#TT','https://lgc.data.wegenenverkeer.be/ns/installatie#TGC','https://lgc.data.wegenenverkeer.be/ns/installatie#Tel','https://lgc.data.wegenenverkeer.be/ns/installatie#TCC','https://lgc.data.wegenenverkeer.be/ns/installatie#Str','https://lgc.data.wegenenverkeer.be/ns/installatie#Stuw','https://lgc.data.wegenenverkeer.be/ns/installatie#Ssig','https://lgc.data.wegenenverkeer.be/ns/installatie#Sluis','https://lgc.data.wegenenverkeer.be/ns/installatie#SDH','https://lgc.data.wegenenverkeer.be/ns/installatie#Schuiven','https://lgc.data.wegenenverkeer.be/ns/installatie#Rooster','https://lgc.data.wegenenverkeer.be/ns/installatie#Ramp','https://lgc.data.wegenenverkeer.be/ns/installatie#Radio','https://lgc.data.wegenenverkeer.be/ns/installatie#PTK','https://lgc.data.wegenenverkeer.be/ns/installatie#PP','https://lgc.data.wegenenverkeer.be/ns/installatie#PoS','https://lgc.data.wegenenverkeer.be/ns/installatie#NSG','https://lgc.data.wegenenverkeer.be/ns/installatie#ModRck','https://lgc.data.wegenenverkeer.be/ns/installatie#Modem','https://lgc.data.wegenenverkeer.be/ns/installatie#MobDet','https://lgc.data.wegenenverkeer.be/ns/installatie#Meteo','https://lgc.data.wegenenverkeer.be/ns/installatie#LS','https://lgc.data.wegenenverkeer.be/ns/installatie#Lift','https://lgc.data.wegenenverkeer.be/ns/installatie#KlimaLegacy','https://lgc.data.wegenenverkeer.be/ns/installatie#Roltrap','https://lgc.data.wegenenverkeer.be/ns/installatie#Vent','https://lgc.data.wegenenverkeer.be/ns/installatie#KL','https://lgc.data.wegenenverkeer.be/ns/installatie#IVSB','https://lgc.data.wegenenverkeer.be/ns/installatie#Int','https://lgc.data.wegenenverkeer.be/ns/installatie#HS','https://lgc.data.wegenenverkeer.be/ns/installatie#HHW','https://lgc.data.wegenenverkeer.be/ns/installatie#FCel','https://lgc.data.wegenenverkeer.be/ns/installatie#Elc','https://lgc.data.wegenenverkeer.be/ns/installatie#Det','https://lgc.data.wegenenverkeer.be/ns/installatie#CVL','https://lgc.data.wegenenverkeer.be/ns/installatie#Slb','https://lgc.data.wegenenverkeer.be/ns/installatie#CC','https://lgc.data.wegenenverkeer.be/ns/installatie#BVE','https://lgc.data.wegenenverkeer.be/ns/installatie#Bus','https://lgc.data.wegenenverkeer.be/ns/installatie#Brug','https://lgc.data.wegenenverkeer.be/ns/installatie#BiF','https://lgc.data.wegenenverkeer.be/ns/installatie#BIB','https://lgc.data.wegenenverkeer.be/ns/installatie#BDV','https://lgc.data.wegenenverkeer.be/ns/installatie#BBT','https://lgc.data.wegenenverkeer.be/ns/installatie#ATOS','https://lgc.data.wegenenverkeer.be/ns/installatie#Asw','https://lgc.data.wegenenverkeer.be/ns/installatie#Audio','https://lgc.data.wegenenverkeer.be/ns/installatie#AfGroep','https://lgc.data.wegenenverkeer.be/ns/installatie#Af','https://lgc.data.wegenenverkeer.be/ns/installatie#AB','https://lgc.data.wegenenverkeer.be/ns/installatie#COD','https://lgc.data.wegenenverkeer.be/ns/installatie#PLCLegacy','https://lgc.data.wegenenverkeer.be/ns/installatie#Bareel','https://lgc.data.wegenenverkeer.be/ns/installatie#BAFG','https://lgc.data.wegenenverkeer.be/ns/installatie#Poortbediening','https://lgc.data.wegenenverkeer.be/ns/installatie#VPLMast','https://lgc.data.wegenenverkeer.be/ns/installatie#Mpt','https://lgc.data.wegenenverkeer.be/ns/installatie#HPGroep','https://lgc.data.wegenenverkeer.be/ns/installatie#CaDoLegacy','https://lgc.data.wegenenverkeer.be/ns/installatie#Buitendeur','https://lgc.data.wegenenverkeer.be/ns/installatie#Brandmelder','https://lgc.data.wegenenverkeer.be/ns/installatie#ADRBuffer','https://lgc.data.wegenenverkeer.be/ns/installatie#VerbindD','https://lgc.data.wegenenverkeer.be/ns/installatie#BBLegacy','https://lgc.data.wegenenverkeer.be/ns/installatie#HulppostLegacy','https://lgc.data.wegenenverkeer.be/ns/installatie#Rookmelder','https://lgc.data.wegenenverkeer.be/ns/installatie#Astrid','https://lgc.data.wegenenverkeer.be/ns/installatie#BevRelais','https://lgc.data.wegenenverkeer.be/ns/installatie#DiffRelais','https://lgc.data.wegenenverkeer.be/ns/installatie#HSMelder','https://lgc.data.wegenenverkeer.be/ns/installatie#OvRelais','https://lgc.data.wegenenverkeer.be/ns/installatie#LVS','https://lgc.data.wegenenverkeer.be/ns/installatie#LSBordLegacy','https://lgc.data.wegenenverkeer.be/ns/installatie#NDVL','https://lgc.data.wegenenverkeer.be/ns/installatie#PompLegacy','https://lgc.data.wegenenverkeer.be/ns/installatie#Sstart','https://lgc.data.wegenenverkeer.be/ns/installatie#Vlot','https://lgc.data.wegenenverkeer.be/ns/installatie#SNCPaal','https://lgc.data.wegenenverkeer.be/ns/installatie#RLCPaal','https://lgc.data.wegenenverkeer.be/ns/installatie#Deurcontact','https://lgc.data.wegenenverkeer.be/ns/installatie#ContourVLLegacy','https://lgc.data.wegenenverkeer.be/ns/installatie#Beton','https://lgc.data.wegenenverkeer.be/ns/installatie#HSDeel','https://lgc.data.wegenenverkeer.be/ns/installatie#LSDeel','https://lgc.data.wegenenverkeer.be/ns/installatie#HSCabineLegacy','https://lgc.data.wegenenverkeer.be/ns/installatie#OTN','https://lgc.data.wegenenverkeer.be/ns/installatie#CEN','https://lgc.data.wegenenverkeer.be/ns/installatie#Rijstrook','https://lgc.data.wegenenverkeer.be/ns/installatie#Noodstroom','https://lgc.data.wegenenverkeer.be/ns/installatie#Beheersys','https://lgc.data.wegenenverkeer.be/ns/installatie#VC','https://lgc.data.wegenenverkeer.be/ns/installatie#ADW','https://lgc.data.wegenenverkeer.be/ns/installatie#SeinBaan','https://lgc.data.wegenenverkeer.be/ns/installatie#SeinRiv','https://lgc.data.wegenenverkeer.be/ns/installatie#SeinOnd','https://lgc.data.wegenenverkeer.be/ns/installatie#SeinRicht','https://lgc.data.wegenenverkeer.be/ns/installatie#SeinSch','https://lgc.data.wegenenverkeer.be/ns/installatie#SeinbrugRRB','https://lgc.data.wegenenverkeer.be/ns/installatie#OmvormerLegacy','https://lgc.data.wegenenverkeer.be/ns/installatie#Decoder','https://lgc.data.wegenenverkeer.be/ns/installatie#ADR','https://lgc.data.wegenenverkeer.be/ns/installatie#Fietstel','https://lgc.data.wegenenverkeer.be/ns/installatie#MIVLVE','https://lgc.data.wegenenverkeer.be/ns/installatie#CCTVPaal','https://lgc.data.wegenenverkeer.be/ns/installatie#TH','https://lgc.data.wegenenverkeer.be/ns/installatie#Relais','https://lgc.data.wegenenverkeer.be/ns/installatie#MS','https://lgc.data.wegenenverkeer.be/ns/installatie#Thermo','https://lgc.data.wegenenverkeer.be/ns/installatie#TransfoLegacy','https://lgc.data.wegenenverkeer.be/ns/installatie#HVS','https://lgc.data.wegenenverkeer.be/ns/installatie#Paal','https://lgc.data.wegenenverkeer.be/ns/installatie#SeinbrugRR','https://lgc.data.wegenenverkeer.be/ns/installatie#PKGroep','https://lgc.data.wegenenverkeer.be/ns/installatie#PK','https://lgc.data.wegenenverkeer.be/ns/installatie#RSSGroep','https://lgc.data.wegenenverkeer.be/ns/installatie#VMSGroep','https://lgc.data.wegenenverkeer.be/ns/installatie#RVMSGroep','https://lgc.data.wegenenverkeer.be/ns/installatie#RSSBord','https://lgc.data.wegenenverkeer.be/ns/installatie#RVMS','https://lgc.data.wegenenverkeer.be/ns/installatie#RRBGroep','https://lgc.data.wegenenverkeer.be/ns/installatie#WegPunt','https://lgc.data.wegenenverkeer.be/ns/installatie#HPicto','https://lgc.data.wegenenverkeer.be/ns/installatie#Switch','https://lgc.data.wegenenverkeer.be/ns/installatie#CamGroep','https://lgc.data.wegenenverkeer.be/ns/installatie#SeinbrugDVM','https://lgc.data.wegenenverkeer.be/ns/installatie#MIVSat','https://lgc.data.wegenenverkeer.be/ns/installatie#PTZ','https://lgc.data.wegenenverkeer.be/ns/installatie#ANPR','https://lgc.data.wegenenverkeer.be/ns/installatie#CCTV','https://lgc.data.wegenenverkeer.be/ns/installatie#AID','https://lgc.data.wegenenverkeer.be/ns/installatie#Encoder','https://lgc.data.wegenenverkeer.be/ns/installatie#DIZV','https://lgc.data.wegenenverkeer.be/ns/installatie#CameraLegacy','https://lgc.data.wegenenverkeer.be/ns/installatie#RLC','https://lgc.data.wegenenverkeer.be/ns/installatie#ANPRPaal','https://lgc.data.wegenenverkeer.be/ns/installatie#SNC','https://lgc.data.wegenenverkeer.be/ns/installatie#VMS'}

    @classmethod
    def create_external_typeURI_options(cls):
        all_type_uris = get_hardcoded_class_dict()
        for uri, info in all_type_uris.items():
            abbr_type_uri = RelationChangeHelpers.get_abbreviated_typeURI(uri, add_namespace=True)
            screen_name = info['label']
            if "#" in abbr_type_uri:
                abbr_type_uri_split = abbr_type_uri.split("#")
                screen_name = "#".join([screen_name, abbr_type_uri_split[0]])
            cls.all_OTL_asset_types_dict[screen_name] = uri
        cls.all_OTL_asset_types_dict = Helpers.sort_nested_dict(cls.all_OTL_asset_types_dict)

        # no need to sort after adding these types
        for legacy_uri in sorted(cls.legacy_type_uris):
            screen_name = f'{legacy_uri.split("#")[-1]} (Legacy)'
            cls.all_OTL_asset_types_dict[screen_name] = legacy_uri

    @classmethod
    def sort_nested_dict(cls, dictionary, by='keys'):
        """Recursively sorts a dictionary by keys or values."""
        if not isinstance(dictionary, dict):
            if isinstance(dictionary, list):
                return sorted(dictionary, key=lambda relation_object: relation_object.typeURI)
            return dictionary

        # Sort the current dictionary
        if by == 'keys':
            sorted_dict = {
                k: cls.sort_nested_dict(v, by=by)
                for k, v in sorted(dictionary.items())
            }

        elif by == 'values':
            sorted_dict = {
                k: cls.sort_nested_dict(v, by=by)
                for k, v in sorted(dictionary.items(), key=lambda item: item[1])
            }

        else:
            raise ValueError("Invalid sort parameter. Use 'keys' or 'values'.")

        return sorted_dict
    
    @classmethod
    def equal_paths(cls,path1: Optional[Path], path2: Optional[Path]):
        if path1 and path2:
            return path1.name == path2.name
        elif path1 or path2:
            return False
        else:
            return True

    @classmethod
    async def converter_from_file_to_object_async(cls, file_path, **kwargs):

        OTLLogger.logger.debug(f"Execute OtlmowConverter.from_file_to_objects({file_path.name})",
                               extra={"timing_ref": f"file_to_objects_{file_path.stem}"})
        exception_group = None
        try:
            object_lists = list(await OtlmowConverter.from_file_to_objects_async(file_path,**kwargs))
        except ExceptionsGroup as group:
            exception_group = group
            object_lists = group.objects

        object_count = len(object_lists)
        OTLLogger.logger.debug(f"Execute OtlmowConverter.from_file_to_objects({file_path.name}) ({object_count} objects)",
                               extra={"timing_ref": f"file_to_objects_{file_path.stem}"})
        return object_lists,exception_group

    @classmethod
    async def converter_from_file_to_object(cls, file_path, **kwargs):

        OTLLogger.logger.debug(f"Execute OtlmowConverter.from_file_to_objects({file_path.name})",
                               extra={"timing_ref": f"file_to_objects_{file_path.stem}"})
        exception_group = None
        try:
            object_lists = list(
                OtlmowConverter.from_file_to_objects(file_path, **kwargs))
        except ExceptionsGroup as group:
            exception_group = group
            object_lists = group.objects

        object_count = len(object_lists)
        OTLLogger.logger.debug(
            f"Execute OtlmowConverter.from_file_to_objects({file_path.name}) ({object_count} objects)",
            extra={"timing_ref": f"file_to_objects_{file_path.stem}"})
        return object_lists, exception_group

    @classmethod
    async def start_async_converter_from_object_to_file(cls, file_path: Path,
                                            sequence_of_objects: Iterable[OTLObject], **kwargs) -> None:
        await Helpers.converter_from_object_to_file(file_path=file_path,
                                              sequence_of_objects=sequence_of_objects,
                                              **kwargs)

    @classmethod
    @add_loading_screen
    async def converter_from_object_to_file(cls, file_path: Path, sequence_of_objects: Iterable[OTLObject], **kwargs) -> None:
        OTLLogger.logger.debug(f"Execute OtlmowConverter.from_objects_to_file({file_path.name})",
                               extra={"timing_ref": f"sequence_of_objects_{file_path.stem}"})
        await OtlmowConverter.from_objects_to_file_async(file_path=file_path,
                                             sequence_of_objects=sequence_of_objects,
                                             **kwargs)
        object_count = len(list(sequence_of_objects))
        OTLLogger.logger.debug(
            f"Execute OtlmowConverter.from_objects_to_file({file_path.name}) ({object_count} objects)",
            extra={"timing_ref": f"sequence_of_objects_{file_path.stem}"})

    @classmethod
    def is_version_equal_or_higher(cls, current_version:str, other_version:str) -> bool:
        res = Version(current_version) >= Version(other_version)
        OTLLogger.logger.info(f"Version comparison {current_version} >= {other_version} => {res}")
        return  res

    @classmethod
    def create_temp_path(cls, path_to_template_file_and_extension: Path) -> Path:
        """
        Creates a temporary path for storing files based on a template file.

        This method generates a temporary directory specifically for storing
        files related to the OTL project. It constructs the path using the
        name of the provided template file and ensures that the directory
        exists before returning the full path.

        :param cls: The class itself.
        :param path_to_template_file_and_extension: The path to the template file
                                                    for which the temporary path is created.
        :type path_to_template_file_and_extension: Path
        :returns: The path to the newly created temporary file location.
        :rtype: Path
        """

        tempdir = Helpers.get_base_temp_dir_path()
        if not tempdir.exists():
            os.makedirs(tempdir)
        doc_name = Path(path_to_template_file_and_extension).name
        return Path(tempdir) / doc_name

    @classmethod
    def get_base_temp_dir_path(cls):
        return Path(tempfile.gettempdir()) / 'temp-otlmow'

    @classmethod
    def extract_typeURI_from_aim_id(cls,aim_id:str,model_directory:Optional[Path]=None) -> Optional[str]:
        uuid = aim_id[:36]
        short_uri_encoded = aim_id[37:]

        if not validate_guid(uuid):
            return None
        if not short_uri_encoded:
            return None

        if missing_padding := len(short_uri_encoded) % 4:
            short_uri_encoded += '=' * (4 - missing_padding)

        short_uri_bytes = base64.b64decode(short_uri_encoded)
        try:
            short_uri = short_uri_bytes.decode('ascii')
        except UnicodeDecodeError:
            return None
        try:
            if short_uri == 'purl:Agent':
                pre, name = short_uri.split(':')
                agent = dynamic_create_instance_from_uri(name, model_directory=model_directory)
                return agent.typeURI

            ns, name = short_uri.split('#')
            instance:OTLObject = dynamic_create_instance_from_ns_and_name(ns, name,
                                                                model_directory=model_directory)
            return instance.typeURI
        except ModuleNotFoundError:
            warnings.warn(
            'Could not import the module for the given aim_id, did you forget the model_directory?',
            category=ImportWarning)
            return None

        except ValueError:
            return None

    @classmethod
    def extract_corrected_relation_partner_typeURI(cls, partner_type_uri, partner_id,
                                                   id_to_typeURI_dict, ref_assets) -> Optional[
        str]:
        if partner_type_uri is None:
            if not id_to_typeURI_dict:
                id_to_typeURI_dict = {RelationChangeHelpers.get_corrected_identificator(asset): asset.typeURI
                                      for asset in ref_assets}

            if partner_id in id_to_typeURI_dict.keys():
                partner_type_uri = id_to_typeURI_dict[partner_id]

        # incase there is no asset with the correct assetId in the application
        if partner_type_uri is None and OTLObjectHelper.is_aim_id(partner_id):
            partner_type_uri = Helpers.extract_typeURI_from_aim_id(partner_id)

        return partner_type_uri