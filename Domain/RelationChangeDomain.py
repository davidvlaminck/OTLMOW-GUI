from typing import List, Optional, cast

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


class RelationChangeDomain:

    project:Project
    collector:OSLOCollector
    objects: list[AIMObject] = []
    existing_relations: list[RelatieObject] = []
    possible_relations_per_class: dict[str,list[OSLORelatie]] = {}
    possible_object_to_object_relations: dict[str,dict[str,list[RelatieObject]]] =  {}

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
        cls.possible_relations_per_class = {}

    @classmethod
    def set_instances(cls, objects_list: List[AIMObject]):


        for instance in objects_list:
            if is_relation(instance):
                cls.existing_relations.append(instance)
            else:
                cls.objects.append(instance)

        cls.get_screen().fill_object_list(cls.objects)
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

        if not cls.possible_relations_per_class.__contains__(selected_object.typeURI):
            cls.possible_relations_per_class[selected_object.typeURI] = cls.collector.find_all_concrete_relations(selected_object.typeURI, False)

        related_objects: list[AIMObject] = list(
            filter(RelationChangeDomain.filter_out(selected_object), cls.objects))



        if selected_object.assetId.identificator not in cls.possible_object_to_object_relations.keys():
            relation_list = cls.possible_relations_per_class[selected_object.typeURI]
            for relation in relation_list:



                if relation.bron_uri == selected_object.typeURI:

                    for related_object in related_objects:
                        if cls.get_same_existing_relations(relation_def= relation,
                                                           selected_object=selected_object,
                                                           related_object=related_object):
                            continue

                        # if(related_object.assetId.identificator == 'dummy_TyBGmXfXC'):
                        #     print(related_object.assetId.identificator  == 'dummy_TyBGmXfXC')
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

        cls.possible_object_to_object_relations = cls.sort_nested_dict(cls.possible_object_to_object_relations)

        possible_relations_for_this_object = cls.possible_object_to_object_relations[
                                                          selected_object.assetId.identificator]

        cls.get_screen().fill_possible_relations_list(selected_object,possible_relations_for_this_object)

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

        if cls.possible_object_to_object_relations.__contains__(selected_object_id):
            if cls.possible_object_to_object_relations[selected_object_id].__contains__(
                    related_object_id):
                cls.possible_object_to_object_relations[selected_object_id][
                    related_object_id].append(relation_object)
            else:
                cls.possible_object_to_object_relations[selected_object_id][
                    related_object_id] = [relation_object]
        else:
            cls.possible_object_to_object_relations[selected_object_id] = {
                related_object_id: [relation_object]}

    @classmethod
    def filter_out(cls, object_to_filter_for:AIMObject):
        def filter_func(related_object:AIMObject):
            return object_to_filter_for.assetId.identificator != related_object.assetId.identificator

        return filter_func

    @classmethod
    def get_all_relations(cls, class_type):
        found_relations = []
        try:
            found_relations = cls.collector.find_all_relations(class_type.typeURI,False)
            print(
                "Add {1}  relations of {0} ".format(class_type.typeURI, len(found_relations)))
        except AttributeError:
            pass

        print("found parents {0}".format(class_type.__bases__))

        for parentClass in class_type.__bases__:
            found_relations.extend(cls.get_all_relations(parentClass))

        return found_relations

    @classmethod
    def get_screen(cls):
        return global_vars.otl_wizard.main_window.step3_relations

    @classmethod
    def invert_relation(cls, relation):
        if (relation.richting == "Source -> Destination"):
            richting = "Destination -> Source"
        elif (relation.richting == "Destination -> Source"):
            richting = "Source -> Destination"
        else:
            richting = relation.richting

        return OSLORelatie(bron_uri = relation.doel_uri,
                               doel_uri = relation.bron_uri,
                               objectUri = relation.objectUri,
                               richting = richting,
                               usagenote="",
                               deprecated_version=relation.deprecated_version,
                               bron_overerving = relation.doel_overerving,
                               doel_overerving = relation.bron_overerving)

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
    def add_possible_relation_to_existing_relations(cls, bron_asset_id, target_asset_id,
                                                    relation_object_index):
        relation_object = cls.possible_object_to_object_relations[bron_asset_id][target_asset_id].pop(relation_object_index)
        cls.existing_relations.append(relation_object)

        cls.update_frontend()

    @classmethod
    def update_frontend(cls):
        if cls.selected_object:
            selected_object_id = cls.selected_object.assetId.identificator
            possibleRelations = cls.possible_object_to_object_relations[selected_object_id]
            cls.get_screen().fill_possible_relations_list(cls.selected_object, possibleRelations)
        cls.get_screen().fill_existing_relations_list(cls.existing_relations)

    @classmethod
    def remove_existing_relation(cls, index:int) -> RelatieObject:
        removed_relation = cls.existing_relations.pop(index)

        source = removed_relation.bronAssetId.identificator
        target = removed_relation.doelAssetId.identificator

        cls.if_possible_relations_list_exists_then_add(source, target, removed_relation)
        cls.if_possible_relations_list_exists_then_add(target,source , removed_relation)

        cls.update_frontend()

        return removed_relation

    @classmethod
    def if_possible_relations_list_exists_then_add(cls, source, target, removed_relation):
        if source in cls.possible_object_to_object_relations:
            if target in cls.possible_object_to_object_relations[source]:
                cls.possible_object_to_object_relations[source][target].append(removed_relation)
            else:
                cls.possible_object_to_object_relations[source][target] = [removed_relation]