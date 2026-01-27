import inspect
import os
from pathlib import Path
from typing import Optional, List, cast

from otlmow_model.OtlmowModel.BaseClasses.RelationInteractor import RelationInteractor
from otlmow_model.OtlmowModel.Classes.Agent import Agent
from otlmow_model.OtlmowModel.Classes.ImplementatieElement.AIMObject import AIMObject
from otlmow_model.OtlmowModel.Helpers import OTLObjectHelper
from otlmow_template.SubsetTemplateCreator import ROOT_DIR

from otlmow_gui.Domain import global_vars
from otlmow_gui.GUI.translation.GlobalTranslate import GlobalTranslate

ROOT_DIR_GUI = Path(__file__).parent.parent.parent.parent
SITE_PACKAGES_ROOT = ROOT_DIR
class RelationChangeHelpers:

    unspecified_direction_icon:str = "<->"
    outgoing_direction_icon: str = "-->"
    incoming_direction_icon: str = "<--"
    @classmethod
    def get_abbreviated_typeURI(cls, typeURI, add_namespace=False, is_relation=False):
        split_typeURI = typeURI.split("#")
        type_name = split_typeURI[-1]

        if typeURI == "http://purl.org/dc/terms/Agent":
            return typeURI.replace("http://purl.org/dc/terms/","")

        if is_relation:
            return typeURI.replace(
                "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#", "")
        elif add_namespace:
            return typeURI.replace(
                "https://wegenenverkeer.data.vlaanderen.be/ns/", "")
        else:
            return type_name

    @classmethod
    def get_screen_name(cls, otl_object: RelationInteractor) -> Optional[str]:
        if otl_object is None:
            return None
        naam = cls.abbreviate_if_AIM_id(cls.get_corrected_identificator(otl_object))
        if otl_object.typeURI == 'http://purl.org/dc/terms/Agent':
            agent: Agent = cast(Agent, otl_object)
            # agent will always be external
            external_tranlation = GlobalTranslate._("external")

            if hasattr(agent, 'naam') and agent.naam:
                naam = " ".join([agent.naam,f"({external_tranlation})"])
            else:
                naam = " ".join([naam,f"({external_tranlation})"])
        else:
            aim_object: AIMObject = cast(AIMObject, otl_object)
            if hasattr(aim_object, 'naam') and aim_object.naam:
                naam = aim_object.naam
            else:
                naam = naam

            if aim_object.assetId.toegekendDoor == global_vars.external_toegekendDoor_label:
                external_tranlation = GlobalTranslate._("external")
                naam = " ".join([naam,f"({external_tranlation})"])

        return naam

    @classmethod
    def abbreviate_if_AIM_id(cls,id):
        return id.split("-")[0] + "-..." if OTLObjectHelper.is_aim_id(id) else id

    @classmethod
    def is_unique_across_namespaces(cls, typeURI,objects):
        split_typeURI = typeURI.split("#")
        type_name = split_typeURI[-1]

        unique_typeURIs = {otl_object.typeURI for otl_object in objects}
        list_type_names = [typeURI.split("#")[-1] for typeURI in unique_typeURIs]

        list_of_non_unique_type_names = filter(
            lambda type_name: list_type_names.count(type_name) < 2, list_type_names)

        return type_name not in list_of_non_unique_type_names

    @classmethod
    def get_screen_icon_direction(cls, input_richting:str) -> str:
        richting = cls.unspecified_direction_icon
        if input_richting == "Source -> Destination":
            richting = cls.outgoing_direction_icon
        elif input_richting == "Destination -> Source":
            richting = cls.incoming_direction_icon
        return richting


    @classmethod
    def list_all_non_abstract_class_type_uris(cls, otl_assets_only=False,
                                              model_directory='otlmow_model/OtlmowModel'):
        classes_to_instantiate = {}
        type_uri_list: List[str] = []

        class_location = Path(SITE_PACKAGES_ROOT) / model_directory / 'Classes/'

        for location, dirs, file in os.walk(class_location):
            dirs.remove("__pycache__")

            for dir in dirs:
                dir_location = Path(location, dir)

                for f in os.listdir(dir_location):
                    f = str(f)
                    if not os.path.isfile(dir_location / f):
                        continue
                    classes_to_instantiate[Path(f).stem] = Path(
                        dir_location / Path(f).stem).resolve()

        classes_to_instantiate['Agent'] = class_location / 'Agent'

        for class_name, file_path in classes_to_instantiate.items():
            
            import_path = f'{file_path.parts[-3]}.{file_path.parts[-2]}.{file_path.parts[-1]}'
            if "Agent" in str(file_path.absolute()):
                import_path = f'{file_path.parts[-2]}.{file_path.parts[-1]}'
            if 'otlmow_model' not in import_path:
                import_path = f'otlmow_model.OtlmowModel.{import_path}'

            try:
                py_mod = __import__(name=import_path, fromlist=f'{class_name}')
            except ModuleNotFoundError as e:
                raise ModuleNotFoundError(f'Could not import the module for {import_path}'
                ) from e

            class_ = getattr(py_mod, class_name)

            if not inspect.isabstract(class_):
                instance = class_()
                if hasattr(instance, "typeURI"):
                    if otl_assets_only and OTLObjectHelper.is_relation(instance):
                        continue
                    type_uri_list.append(instance.typeURI)
        return type_uri_list

    @classmethod
    def get_corrected_identificator(cls, otl_object: RelationInteractor):
        identificator = GlobalTranslate._("no_identificator")
        if hasattr(otl_object,"assetId"):
            identificator = str(otl_object.assetId.identificator)
        elif hasattr(otl_object,"agentId"):
            identificator = str(otl_object.agentId.identificator)

        return identificator
