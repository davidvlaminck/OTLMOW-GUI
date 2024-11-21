import inspect
import os
from pathlib import Path
from typing import Optional, List

from otlmow_model.OtlmowModel.Helpers import OTLObjectHelper
from otlmow_template.SubsetTemplateCreator import ROOT_DIR

from GUI.translation.GlobalTranslate import GlobalTranslate
from LatestReleaseMulti.OTLWizard.data.otlmow_template.SubsetTemplateCreator import \
    SubsetTemplateCreator
from UnitTests.TestClasses.Classes.ImplementatieElement.AIMObject import AIMObject

ROOT_DIR_GUI = Path(__file__).parent.parent.parent.parent
SITE_PACKAGES_ROOT = ROOT_DIR
class RelationChangeHelpers:
    @classmethod
    def get_abbreviated_typeURI(cls, typeURI, add_namespace, is_relation=False):
        split_typeURI = typeURI.split("#")
        type_name = split_typeURI[-1]

        if is_relation:
            return typeURI.replace(
                "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#", "")
        elif add_namespace:
            return typeURI.replace(
                "https://wegenenverkeer.data.vlaanderen.be/ns/", "")
        else:
            return type_name

    @classmethod
    def get_screen_name(cls, OTL_object: AIMObject) -> Optional[str]:
        if OTL_object is None:
            return None
        naam = ""
        if hasattr(OTL_object, 'naam') and OTL_object.naam:
            naam = OTL_object.naam
            if GlobalTranslate._("external") in OTL_object.assetId.identificator:
                naam = " ".join([naam,"(external)"])
        else:
            naam = str(OTL_object.assetId.identificator)

        return naam
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
    def get_screen_icon_direction(self, input_richting:str):
        richting = "<->"
        if input_richting == "Source -> Destination":
            richting = "-->"
        elif input_richting == "Destination -> Source":
            richting = "<--"
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

            try:
                import_path = f'{file_path.parts[-3]}.{file_path.parts[-2]}.{file_path.parts[-1]}'
                if "Agent" in str(file_path.absolute()):
                    import_path = f'{file_path.parts[-2]}.{file_path.parts[-1]}'
                if 'otlmow_model' not in import_path:
                    import_path = 'otlmow_model.OtlmowModel.' + import_path

                py_mod = __import__(name=import_path, fromlist=f'{class_name}')
            except ModuleNotFoundError:
                raise ModuleNotFoundError(f'Could not import the module for {import_path}')

            class_ = getattr(py_mod, class_name)

            if not inspect.isabstract(class_):
                instance = class_()
                if hasattr(instance, "typeURI"):
                    if otl_assets_only and OTLObjectHelper.is_relation(instance):
                        continue
                    type_uri_list.append(instance.typeURI)
        return type_uri_list