from typing import Optional

from otlmow_model.OtlmowModel.Helpers import OTLObjectHelper

from Domain.RelationChangeDomain import RelationChangeDomain
from UnitTests.TestClasses.Classes.ImplementatieElement.AIMObject import AIMObject


class RelationChangeHelpers:
    @classmethod
    def get_abbreviated_typeURI(cls, otl_object):
        split_typeURI = otl_object.typeURI.split("#")
        type_name = split_typeURI[-1]

        if OTLObjectHelper.is_relation(otl_object):
            return otl_object.typeURI.replace(
                "https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#", "")
        elif cls.is_unique_across_namespaces(type_name):
            return otl_object.typeURI.replace(
                "https://wegenenverkeer.data.vlaanderen.be/ns/", "")
        else:
            return type_name

    @classmethod
    def get_screen_name(cls, OTL_object: AIMObject) -> Optional[str]:
        if OTL_object is None:
            return None

        return (
            OTL_object.naam
            if hasattr(OTL_object, 'naam') and OTL_object.naam
            else str(OTL_object.assetId.identificator)
        )

    @classmethod
    def is_unique_across_namespaces(cls, selected_type_name):
        unique_typeURIs = {otl_object.typeURI for otl_object in RelationChangeDomain.objects}
        list_type_names = [typeURI.split("#")[-1] for typeURI in unique_typeURIs]

        list_of_non_unique_type_names = filter(
            lambda type_name: list_type_names.count(type_name) < 2, list_type_names)

        return selected_type_name not in list_of_non_unique_type_names

    @classmethod
    def get_screen_icon_direction(self, input_richting:str):
        richting = "<->"
        if input_richting == "Source -> Destination":
            richting = "-->"
        elif input_richting == "Destination -> Source":
            richting = "<--"
        return richting