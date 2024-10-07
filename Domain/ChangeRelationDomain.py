from typing import List

from otlmow_model.OtlmowModel.Classes.ImplementatieElement.AIMObject import \
    AIMObject
from otlmow_modelbuilder.OSLOCollector import OSLOCollector

from Domain import global_vars


class ChangeRelationDomain:

    objects: List[AIMObject]

    @classmethod
    def set_objects(cls,objects_list: List[AIMObject]):
        objects = objects_list
        global_vars.otl_wizard.main_window.step3_relations.fill_class_list(objects)

    @classmethod
    def getPossibleRelations(cls,subset_location):

        subset_collector = OSLOCollector(subset_location)
        subset_collector.collect_all()