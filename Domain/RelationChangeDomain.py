from pathlib import Path
from typing import List, Dict

from otlmow_model.OtlmowModel.Classes.ImplementatieElement.AIMObject import \
    AIMObject
from otlmow_modelbuilder.OSLOCollector import OSLOCollector
from otlmow_modelbuilder.SQLDataClasses.OSLORelatie import OSLORelatie

from Domain import global_vars
from Domain.Project import Project


class RelationChangeDomain:

    project:Project
    collector:OSLOCollector
    objects: List[AIMObject]
    possible_relations_per_object: dict = {}

    @classmethod
    def init_static(cls, project:Project):
        cls.project = project
        cls.collector = OSLOCollector(project.subset_path)
        cls.collector.collect_all()

    @classmethod
    def set_objects(cls,objects_list: List[AIMObject]):

        cls.objects = objects_list
        cls.get_screen().fill_class_list(cls.objects)
        # if len(objects) != 0:
        #     cls.set_possible_relations(cls.objects[0])

    # @classmethod
    # def get_possible_relations(cls, subset_location:Path):
    #
    #     subset_collector = OSLOCollector(subset_location)
    #     subset_collector.collect_all()
    #     for object in cls.objects:
    #         cls.get_screen().subset_collector.find_outgoing_relations(object)

    @classmethod
    def set_possible_relations(cls, object:AIMObject):
        cls.possible_relations_per_object[object.typeURI] = cls.collector.find_outgoing_relations(object.typeURI)
        cls.get_screen().fill_possible_relations_list(cls.possible_relations_per_object[object.typeURI])

    @classmethod
    def get_screen(cls):
        return global_vars.otl_wizard.main_window.step3_relations