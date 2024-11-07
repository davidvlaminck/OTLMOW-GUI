from typing import List, Optional, cast, Union

from otlmow_converter.DotnotationDictConverter import DotnotationDictConverter
from otlmow_converter.OtlmowConverter import OtlmowConverter
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject, dynamic_create_type_from_uri
from otlmow_model.OtlmowModel.Classes.ImplementatieElement.AIMObject import \
    AIMObject
from otlmow_model.OtlmowModel.Classes.ImplementatieElement.RelatieObject import RelatieObject
from otlmow_model.OtlmowModel.Helpers import RelationCreator
from otlmow_model.OtlmowModel.Helpers.OTLObjectHelper import is_relation

from otlmow_modelbuilder.OSLOCollector import OSLOCollector
from otlmow_modelbuilder.SQLDataClasses.OSLORelatie import OSLORelatie

from Domain import global_vars
from Domain.Project import Project
from Domain.ProjectFileManager import ProjectFileManager



def save_assets(func):
    def wrapper_func(*args, **kwargs):
        res = func(*args, **kwargs)
        global_vars.current_project.assets_in_memory = RelationChangeDomain.objects + RelationChangeDomain.existing_relations
        ProjectFileManager.save_validated_assets(global_vars.current_project,
                                                 global_vars.current_project.project_path)
        global_vars.otl_wizard.main_window.step_3_tabwidget.header.start_event_loop()
        return res

    return wrapper_func

class RelationChangeDomain:

    project:Project
    collector:OSLOCollector
    objects: list[AIMObject] = []
    existing_relations: list[RelatieObject] = []
    possible_relations_per_class_dict: dict[str,list[OSLORelatie]] = {}
    possible_object_to_object_relations_dict: dict[str,dict[str,list[RelatieObject]]] =  {}

    selected_object: Optional[AIMObject] = None
    """
    Call this when the project or project.subset_path changes or everytime you go to the window
    """
    @classmethod
    def init_static(cls, project:Project):
        cls.project = project
        cls.collector = OSLOCollector(project.subset_path)
        cls.collector.collect_all()
        cls.objects = []
        cls.existing_relations = []
        cls.possible_relations_per_class_dict = {}
        cls.possible_object_to_object_relations_dict = {}

        cls.set_instances(ProjectFileManager.load_validated_assets())


    @classmethod
    def set_instances(cls, objects_list: List[AIMObject]):
        cls.existing_relations = []
        cls.objects = []

        for instance in objects_list:
            if is_relation(instance):
                cls.existing_relations.append(instance)
            else:
                cls.objects.append(instance)

        cls.get_screen().fill_object_list(cls.objects)
        cls.get_screen().fill_possible_relations_list(None, cls.possible_object_to_object_relations_dict)
        cls.get_screen().fill_existing_relations_list(cls.existing_relations)

    @classmethod
    def get_object(cls,identificator:str) -> Optional[AIMObject]:
        filtered_objects = list(filter(lambda aim_object: aim_object.assetId.identificator == identificator, cls.objects))

        if filtered_objects:
            if len(filtered_objects) > 1:
                pass #TODO: raise error of 2 objects with the same identificator in the list
            else:
                return filtered_objects[0]
        return None

    @classmethod
    def set_possible_relations(cls, selected_object:AIMObject):

        cls.selected_object = selected_object
        if not selected_object:
            cls.get_screen().fill_possible_relations_list(selected_object,{})
            cls.get_screen().fill_object_attribute_field({})
            return

        if selected_object.typeURI not in cls.possible_relations_per_class_dict:
            cls.possible_relations_per_class_dict[selected_object.typeURI] = cls.collector.find_all_concrete_relations(selected_object.typeURI, False)

        related_objects: list[AIMObject] = list(
            filter(RelationChangeDomain.filter_out(selected_object), cls.objects))

        relation_list = cls.possible_relations_per_class_dict[selected_object.typeURI]
        cls.possible_object_to_object_relations_dict[selected_object.assetId.identificator] = {}

        for relation in relation_list:
            if relation.bron_uri == selected_object.typeURI:

                for related_object in related_objects:
                    if cls.get_same_existing_relations(relation_def= relation,
                                                       selected_object=selected_object,
                                                       related_object=related_object):
                        continue

                    if relation.doel_uri == related_object.typeURI:
                        cls.add_relation_between(relation, selected_object, related_object)

            elif relation.doel_uri == selected_object.typeURI:
                for related_object in related_objects:
                    if cls.get_same_existing_relations(relation_def= relation,
                                                       selected_object=selected_object,
                                                       related_object=related_object):
                        continue
                    if relation.bron_uri == related_object.typeURI:
                        cls.add_relation_between(relation, selected_object,related_object,True)

        cls.possible_object_to_object_relations_dict = cls.sort_nested_dict(cls.possible_object_to_object_relations_dict)

        possible_relations_for_this_object = {}
        if selected_object.assetId.identificator in cls.possible_object_to_object_relations_dict:
            possible_relations_for_this_object = cls.possible_object_to_object_relations_dict[
                                                              selected_object.assetId.identificator]

        cls.get_screen().fill_possible_relations_list(selected_object,possible_relations_for_this_object)

        object_attributes_dict = DotnotationDictConverter.to_dict(selected_object)
        cls.get_screen().fill_object_attribute_field(object_attributes_dict)

    @classmethod
    def get_same_existing_relations(cls, relation_def: OSLORelatie,
                                    selected_object: AIMObject,
                                    related_object: AIMObject):
        return list(filter(
            lambda existed_relation: cls.is_same_relation(existed_relation,
                                                        relation_def,
                                                        selected_object,
                                                        related_object),
            cls.existing_relations))

    @classmethod
    def is_same_relation(cls, existing_relation:RelatieObject, relation_def: OSLORelatie, selected: AIMObject, related: AIMObject) -> bool:
        return  (existing_relation.typeURI == relation_def.objectUri) and ((
                existing_relation.bronAssetId.identificator == selected.assetId.identificator and
                existing_relation.doelAssetId.identificator == related.assetId.identificator) or(
                existing_relation.bronAssetId.identificator == related.assetId.identificator and
                existing_relation.doelAssetId.identificator == selected.assetId.identificator))

    @classmethod
    def add_relation_between(cls, relation: OSLORelatie, selected_object: AIMObject, related_object:AIMObject, reversed:bool = False) -> None:

        selected_object_id = selected_object.assetId.identificator
        related_object_id = related_object.assetId.identificator

        # if ( related_object_id == 'dummy_TyBGmXfXC'):
        #     print( related_object_id == 'dummy_TyBGmXfXC')

        # the relation object is reversed from the wrong direction to the right direction
        relation_object = None
        if reversed:
            relation_object =  cls.create_relation_object(relation, related_object, selected_object)
        else:
            relation_object = cls.create_relation_object(relation,selected_object,related_object)

        if selected_object_id in cls.possible_object_to_object_relations_dict:
            if related_object_id in cls.possible_object_to_object_relations_dict[selected_object_id]:
                cls.possible_object_to_object_relations_dict[selected_object_id][
                    related_object_id].append(relation_object)
            else:
                cls.possible_object_to_object_relations_dict[selected_object_id][
                    related_object_id] = [relation_object]
        else:
            cls.possible_object_to_object_relations_dict[selected_object_id] = {
                related_object_id: [relation_object]}

    @classmethod
    def filter_out(cls, object_to_filter_for:AIMObject):
        def filter_func(related_object:AIMObject):
            return object_to_filter_for.assetId.identificator != related_object.assetId.identificator

        return filter_func

    @classmethod
    def get_screen(cls):
        return global_vars.otl_wizard.main_window.step3_relations

    @classmethod
    def create_relation_object(cls,
                               OSLO_relation:OSLORelatie,
                               source_object:AIMObject,
                               target_object:AIMObject) -> RelatieObject:
        relation_type = dynamic_create_type_from_uri(OSLO_relation.objectUri)
        return RelationCreator.create_relation(relation_type,source_object,target_object)

    @classmethod
    def sort_nested_dict(cls,d, by='keys'):
        """Recursively sorts a dictionary by keys or values."""
        if not isinstance(d, dict):
            if isinstance(d,list):
                return sorted(d,key= lambda relation_object: relation_object.typeURI)
            return d

        # Sort the current dictionary
        if by == 'keys':
            sorted_dict = dict(
                (k, cls.sort_nested_dict(v, by=by)) for k, v in sorted(d.items())
            )
        elif by == 'values':
            sorted_dict = dict(
                (k, cls.sort_nested_dict(v, by=by)) for k, v in
                sorted(d.items(), key=lambda item: item[1])
            )
        else:
            raise ValueError("Invalid sort parameter. Use 'keys' or 'values'.")

        return sorted_dict

    @classmethod
    @save_assets
    def add_possible_relation_to_existing_relations(cls, bron_asset_id, target_asset_id,
                                                    relation_object_index):
        relation_object = cls.possible_object_to_object_relations_dict[bron_asset_id][target_asset_id].pop(relation_object_index)
        cls.existing_relations.append(relation_object)

        cls.get_screen().expand_existing_relations_folder_of(relation_object.typeURI)

        cls.update_frontend()

    @classmethod
    def update_frontend(cls):
        cls.get_screen().fill_object_list(cls.objects)
        cls.get_screen().fill_existing_relations_list(cls.existing_relations)
        if cls.selected_object:
            cls.set_possible_relations(selected_object=cls.selected_object)
            selected_object_id = cls.selected_object.assetId.identificator
            possibleRelations = cls.possible_object_to_object_relations_dict[selected_object_id]
            cls.get_screen().fill_possible_relations_list(cls.selected_object, possibleRelations)



    @classmethod
    @save_assets
    def remove_existing_relation(cls, index:int) -> RelatieObject:
        removed_relation = cls.existing_relations.pop(index)

        if cls.selected_object:
            selected_id = cls.selected_object.assetId.identificator
            source_id = removed_relation.bronAssetId.identificator
            target_id = removed_relation.doelAssetId.identificator

            if selected_id in [source_id, target_id]:
                cls.get_screen().expand_possible_relations_folder_of(removed_relation.typeURI)

        cls.update_frontend()

        return removed_relation

    @classmethod
    def if_possible_relations_list_exists_then_add(cls, source, target, removed_relation):
        if source in cls.possible_object_to_object_relations_dict:
            if target in cls.possible_object_to_object_relations_dict[source]:
                cls.possible_object_to_object_relations_dict[source][target].append(removed_relation)
            else:
                cls.possible_object_to_object_relations_dict[source][target] = [removed_relation]

    @classmethod
    def select_existing_relation_indices(cls, indices: list[int]) -> None:
        if not indices:
            return
        
        last_index = indices[-1]
        last_selected_relation = cls.existing_relations[last_index]
        cls.get_screen().fill_existing_relation_attribute_field(DotnotationDictConverter.to_dict(last_selected_relation))

    @classmethod
    def select_possible_relation_data(cls, selected_relations_data: list) -> None:
        if not selected_relations_data:
            return
        last_selected_keys = selected_relations_data[-1]
        last_selected_relation = cls.possible_object_to_object_relations_dict[last_selected_keys.source_id][last_selected_keys.target_id][last_selected_keys.index]
        cls.get_screen().fill_possible_relation_attribute_field(
            DotnotationDictConverter.to_dict(last_selected_relation))

    @classmethod
    def get_instances(cls) -> list[Union[RelatieObject, AIMObject]]:
        return cls.objects + cls.existing_relations
