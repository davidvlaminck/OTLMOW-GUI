import asyncio
import inspect
import logging
import os
from copy import deepcopy
from pathlib import Path
from typing import List, Optional, cast, Union

from otlmow_model.OtlmowModel.Helpers.generated_lists import get_hardcoded_class_dict

from otlmow_converter.DotnotationDictConverter import DotnotationDictConverter
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject, dynamic_create_type_from_uri, \
    dynamic_create_instance_from_uri
from otlmow_model.OtlmowModel.Classes.Agent import Agent
from otlmow_model.OtlmowModel.Classes.ImplementatieElement.AIMObject import \
    AIMObject
from otlmow_model.OtlmowModel.Classes.ImplementatieElement.RelatieObject import RelatieObject
from otlmow_model.OtlmowModel.Helpers import RelationCreator, OTLObjectHelper
from otlmow_model.OtlmowModel.Helpers.OTLObjectHelper import is_relation

from otlmow_modelbuilder.OSLOCollector import OSLOCollector
from otlmow_modelbuilder.SQLDataClasses.OSLORelatie import OSLORelatie

from Domain import global_vars
from Domain.Helpers import Helpers
from Domain.project.Project import Project

from GUI.screens.RelationChange_elements.RelationChangeHelpers import RelationChangeHelpers, \
    SITE_PACKAGES_ROOT

ROOT_DIR = Path(__file__).parent.parent

def save_assets(func):
    """Decorator that saves assets after executing the decorated function.

    This decorator wraps a function to ensure that after its execution, the current
    project's assets in memory are updated and saved. It also starts the event loop
    for the header in the main window to animate the OTL Wizard 2 logo during saving.

    :param func: The function to be decorated.
    :returns: The wrapper function that includes the saving logic.
    """

    def wrapper_func(*args, **kwargs):
        res = func(*args, **kwargs)
        global_vars.current_project.assets_in_memory = RelationChangeDomain.get_quicksave_instances()
        global_vars.current_project.save_validated_assets()
        global_vars.otl_wizard.main_window.step_3_tabwidget.header.start_event_loop()
        return res

    return wrapper_func

class RelationChangeDomain:

    project:Project = None
    collector:OSLOCollector = None

    internal_objects: list[AIMObject] = [] # Object in the project (placed by contractor)
    external_objects: list[AIMObject] = [] # Object outside the project (from DAVIE)
    agent_objects: list[Agent] = []        # Agent objects (not an AIMobject)
    shown_objects: list[OTLObject] = []    # All objects combined that are displayed on GUI (col 1)

    possible_relations_per_class_dict: dict[str,list[OSLORelatie]] = {}
    possible_object_to_object_relations_dict: dict[str, dict[str, list[RelatieObject]]] = {}#(col 2)

    existing_relations: list[RelatieObject] = []  # relations
    aim_id_relations = [] # pre-existing relations from DAVIE


    selected_object: Optional[AIMObject] = None # the asset/agent in col 1 currently selected by user
    last_added_to_existing: Optional[list[AIMObject]] = [] # relation last added to col 3
    last_added_to_possible: Optional[list[AIMObject]] = [] # relation last added to col 2

    external_object_added = False

    no_id_count = 0

    @classmethod
    def init_static(cls, project: Project) -> None:
        """
        Initializes static resources for the RelationChangeDomain class.
        Call this when the project or project.subset_path changes or everytime you go to the window

        This method sets up the project and initializes various attributes related
        to object relations, including collectors and lists for managing internal
        and external objects. It also starts loading project relation data asynchronously.

        :param cls: The class itself.
        :param project: The project to be initialized.
        :type project: Project
        :returns: None
        """

        cls.project = project
        cls.collector = OSLOCollector(project.subset_path)
        cls.collector.collect_all()

        cls.selected_object = None

        cls.shown_objects = []
        cls.internal_objects = []
        cls.external_objects = []
        cls.existing_relations = []
        cls.possible_relations_per_class_dict = {}
        cls.possible_object_to_object_relations_dict = {}
        cls.aim_id_relations = []
        cls.no_id_count = 0
        cls.external_object_added = False


        if global_vars.current_project:
            event_loop = asyncio.get_event_loop()
            event_loop.create_task(cls.load_project_relation_data())

    @classmethod
    async def load_project_relation_data(cls) -> None:
        """
        Loads project relation data asynchronously.

        This method sets the GUI to a loading state while it retrieves and processes
        project relation data. It populates a dictionary with asset type URIs and
        updates the user interface accordingly once the data is loaded.

        :param cls: The class itself.
        :returns: None
        """

        cls.get_screen().set_gui_lists_to_loading_state()

        await asyncio.sleep(0)  # Give the UI thread the chance to switch the screen to
                                # RelationChangeScreen
        await asyncio.sleep(0)  # Give the UI thread another chance to switch the screen to
                                # RelationChangeScreen

        Helpers.create_external_typeURI_options()
        cls.set_instances(cls.project.load_validated_assets())
        global_vars.otl_wizard.main_window.step3_visuals.reload_html()

    @classmethod
    def set_instances(cls, objects_list: List[AIMObject]) -> None:
        """Processes and categorizes AIM objects for relation management.

        This method takes a list of AIM objects and categorizes them into various
        groups based on their properties.
        It updates the class attributes to reflect the current state of these objects
        and ensures that the user interface is populated with the correct information.

        :param cls: The class itself.
        :param objects_list: A list of AIM objects to be processed and categorized.
        :type objects_list: List[AIMObject]
        :returns: None
        """

        cls.existing_relations = []
        cls.aim_id_relations = []

        cls.internal_objects = []
        cls.external_objects = []
        cls.agent_objects = []
        cls.shown_objects = []

        for instance in objects_list:

            if is_relation(instance):
                relation_instance:RelatieObject = instance
                is_aim_id = False
                try:
                    is_aim_id = OTLObjectHelper.is_aim_id(relation_instance.assetId.identificator)
                except Exception:
                    pass

                if is_aim_id or not relation_instance.isActief:
                    cls.aim_id_relations.append(relation_instance)
                else:
                    cls.existing_relations.append(relation_instance)

            else:
                if instance.typeURI == 'http://purl.org/dc/terms/Agent':
                    agent_instance: Agent = instance
                    cls.agent_objects.append(agent_instance)
                elif instance.assetId.toegekendDoor == global_vars.external_toegekendDoor_label:
                    cls.external_objects.append(instance)
                else:
                    cls.internal_objects.append(instance)

        cls.apply_active_aim_id_relations()

        cls.shown_objects = deepcopy(cls.internal_objects)
        cls.add_external_objects_to_shown_objects()
        cls.add_agent_objects_to_shown_objects()

        cls.create_and_add_missing_external_assets_from_relations()

        cls.get_screen().fill_object_list(cls.shown_objects)
        cls.get_screen().fill_possible_relations_list(None, {})
        cls.get_screen().fill_existing_relations_list(cls.existing_relations)

    @classmethod
    def create_and_add_missing_external_assets_from_relations(cls) -> None:
        """
        Creates and adds missing external assets based on existing relations.

        This method iterates through all relations and checks for the existence of
        source and target objects. If either object is missing, it attempts to create
        and add a new external asset using the relation's identifiers and type URIs.

        :param cls: The class itself.
        :returns: None
        """

        for relation_object in RelationChangeDomain.get_all_relations():
            source_id = relation_object.bronAssetId.identificator
            target_id = relation_object.doelAssetId.identificator

            source_object = RelationChangeDomain.get_object(identificator=source_id)
            if not source_object:
                try:
                    cls.create_and_add_new_external_asset(id_or_name=source_id,
                                                          type_uri=relation_object.bron.typeURI)
                except ValueError as e:
                    # should there be a wrong typeURI
                    logging.debug(e)

            target_object = RelationChangeDomain.get_object(identificator=target_id)
            if not target_object:
                try:
                    cls.create_and_add_new_external_asset(id_or_name=target_id,
                                                          type_uri=relation_object.doel.typeURI)
                except ValueError as e:
                    # should there be a wrong typeURI
                    logging.debug(e)

    @classmethod
    def get_all_relations(cls) -> list:
        """Retrieves all existing relations from the class.

        This method combines and returns the lists of existing relations and AIM ID
        relations stored in the class. It provides a unified view of all relations
        for further processing or display.

        :param cls: The class itself.
        :returns: A list containing all existing and AIM ID relations.
        :rtype: list
        """

        return (cls.existing_relations + cls.aim_id_relations)

    @classmethod
    def get_object(cls, identificator: str) -> Optional[OTLObject]:
        """
        Retrieves an object from the list of shown objects based on its identificator.

        This method filters the list of shown objects to find an object that matches
        the provided identificator. If multiple objects are found, it currently does
        not handle the error case, but if exactly one object is found, it returns that object.

        :param cls: The class itself.
        :param identificator: The identificator of the object to retrieve.
        :type identificator: str
        :returns: The matching OTL object if found, otherwise None.
        :rtype: Optional[OTLObject]
        """
        filtered_objects = list(filter(cls.filter_on_id(identificator), cls.shown_objects))

        if filtered_objects:
            if len(filtered_objects) > 1:
                logging.debug(f"ERROR RelationChangeDomain.get_object function found multiple "
                              f"objects with id: {identificator}")
                pass #TODO: raise error of 2 objects with the same identificator in the list
            else:
                return filtered_objects[0]
        return None

    @classmethod
    def filter_on_id(cls, id_to_check:str):

        return lambda otl_object: RelationChangeHelpers.get_correct_identificator(otl_object) == id_to_check


    @classmethod
    def set_possible_relations(cls, selected_object:AIMObject):

        cls.selected_object = selected_object
        if not selected_object:
            cls.get_screen().fill_possible_relations_list(selected_object,{})
            cls.get_screen().fill_object_attribute_field({})
            cls.get_screen().fill_possible_relation_attribute_field({})
            return

        if cls.external_object_added or selected_object.typeURI not in cls.possible_relations_per_class_dict.keys():
            try:
                if cls.external_objects or cls.agent_objects:
                    # this is the long search but it includes relations with external assets
                    cls.possible_relations_per_class_dict[selected_object.typeURI] = (
                        RelationChangeDomain.get_all_concrete_relation_from_full_model(
                        selected_object))
                else:
                    cls.possible_relations_per_class_dict[selected_object.typeURI] =\
                        cls.collector.find_all_concrete_relations(selected_object.typeURI, False)
            except ValueError as e:
                logging.debug(e)
                cls.possible_relations_per_class_dict[selected_object.typeURI] = (
                    RelationChangeDomain.get_all_concrete_relation_from_full_model(
                    selected_object))

            cls.external_object_added = False

        related_objects: list[AIMObject] = list(
            filter(RelationChangeDomain.filter_out(selected_object), cls.shown_objects))

        relation_list = cls.possible_relations_per_class_dict[selected_object.typeURI]

        cls.clear_possible_object_to_object_relations_dict(selected_object)

        inactive_relations = cls.get_inactive_aim_id_relations()

        for relation_instance in inactive_relations:
            if (relation_instance.bronAssetId.identificator == 
                    RelationChangeHelpers.get_correct_identificator(selected_object)):
                cls.add_possible_relation_object(relation_instance,
                                                 relation_instance.bronAssetId.identificator,
                                                 relation_instance.doelAssetId.identificator)
            if(relation_instance.doelAssetId.identificator == RelationChangeHelpers.get_correct_identificator(selected_object)):
                cls.add_possible_relation_object(relation_instance,
                                                 relation_instance.doelAssetId.identificator,
                                                 relation_instance.bronAssetId.identificator)

        for relation in relation_list:



            if relation.bron_uri == selected_object.typeURI:

                for related_object in related_objects:
                    if cls.get_same_relations_in_list(cls.existing_relations,
                                                      relation_def= relation,
                                                      selected_object=selected_object,
                                                      related_object=related_object):
                        continue
                    if relation.doel_uri == related_object.typeURI:
                        cls.add_relation_between(relation, selected_object, related_object)

            if relation.doel_uri == selected_object.typeURI :
                for related_object in related_objects:
                    if cls.get_same_relations_in_list(cls.existing_relations,
                                                      relation_def= relation,
                                                      selected_object=selected_object,
                                                      related_object=related_object,
                                                      reverse=True):
                        continue



                    if relation.bron_uri == related_object.typeURI:
                        cls.add_relation_between(relation, selected_object,related_object,True)

        cls.possible_object_to_object_relations_dict = Helpers.sort_nested_dict(cls.possible_object_to_object_relations_dict)

        possible_relations_for_this_object = {}
        if RelationChangeHelpers.get_correct_identificator(selected_object) in cls.possible_object_to_object_relations_dict:
            possible_relations_for_this_object = cls.possible_object_to_object_relations_dict[
                                                              RelationChangeHelpers.get_correct_identificator(selected_object)]

        cls.get_screen().fill_possible_relations_list(selected_object,possible_relations_for_this_object,cls.last_added_to_possible)

        object_attributes_dict = DotnotationDictConverter.to_dict(selected_object)
        cls.get_screen().fill_object_attribute_field(object_attributes_dict)

    @classmethod
    def get_all_concrete_relation_from_full_model(cls, selected_object):
        all_relations = selected_object._get_all_concrete_relations()
        concrete_OSLO_relations: list[OSLORelatie] = [OSLORelatie(
            bron_overerving="",
            doel_overerving="",
            bron_uri= concrete_relation[0],
            doel_uri= concrete_relation[2],
            objectUri= concrete_relation[1],
            richting= concrete_relation[3],
            deprecated_version=concrete_relation[4],
            usagenote="")for concrete_relation in all_relations]
        return concrete_OSLO_relations

    @classmethod
    def clear_possible_object_to_object_relations_dict(cls, selected_object):
        cls.possible_object_to_object_relations_dict[RelationChangeHelpers.get_correct_identificator(selected_object)] = {}

    @classmethod
    def get_same_relations_in_list(cls,relation_list: list[RelatieObject],
                                    relation_def: OSLORelatie,
                                    selected_object: AIMObject,
                                    related_object: AIMObject,
                                    reverse: bool=False):
        return [relation for relation in relation_list
                if cls.is_same_relation(relation,relation_def,selected_object,related_object,
                                        reverse)
               ]

    @classmethod
    def get_same_existing_relations(cls, relation_def: OSLORelatie,
                                   selected_object: AIMObject,
                                   related_object: AIMObject,
                                    reverse: bool=False):
        return list(filter(
            lambda existed_relation: cls.is_same_relation(existed_relation,
                                                          relation_def,
                                                          selected_object,
                                                          related_object,
                                                          reverse),
            cls.existing_relations))

    @classmethod
    def is_same_relation(cls, existing_relation:RelatieObject, relation_def: OSLORelatie, selected: AIMObject, related: AIMObject, reverse: bool= False) -> bool:
        if (existing_relation.typeURI == relation_def.objectUri):
            if relation_def.richting == "Unspecified":
                return ((
                            existing_relation.bronAssetId.identificator == RelationChangeHelpers.get_correct_identificator(related) and
                            existing_relation.doelAssetId.identificator == RelationChangeHelpers.get_correct_identificator(selected)) or
                        (existing_relation.bronAssetId.identificator == RelationChangeHelpers.get_correct_identificator(selected) and
                         existing_relation.doelAssetId.identificator == RelationChangeHelpers.get_correct_identificator(related)))
            if reverse:
                return (
                            existing_relation.bronAssetId.identificator == RelationChangeHelpers.get_correct_identificator(related) and
                            existing_relation.doelAssetId.identificator == RelationChangeHelpers.get_correct_identificator(selected))
            else:
                return (existing_relation.bronAssetId.identificator == RelationChangeHelpers.get_correct_identificator(selected) and
                        existing_relation.doelAssetId.identificator == RelationChangeHelpers.get_correct_identificator(related))



    @classmethod
    def add_relation_between(cls, relation: OSLORelatie, selected_object: AIMObject, related_object:AIMObject, reverse:bool = False) -> None:

        selected_object_id = RelationChangeHelpers.get_correct_identificator(selected_object)
        related_object_id = RelationChangeHelpers.get_correct_identificator(related_object)

        # if ( related_object_id == 'dummy_TyBGmXfXC'):
        #     print( related_object_id == 'dummy_TyBGmXfXC')

        # the relation object is reversed from the wrong direction to the right direction
        relation_object = None
        if reverse:
            relation_object =  cls.create_relation_object(relation, related_object, selected_object)
        else:
            relation_object = cls.create_relation_object(relation,selected_object,related_object)

        if not relation_object:
            return

        if (    selected_object_id in cls.possible_object_to_object_relations_dict.keys() and
                related_object_id in cls.possible_object_to_object_relations_dict[selected_object_id].keys() and
                cls.get_same_relations_in_list(cls.possible_object_to_object_relations_dict[selected_object_id][related_object_id],
                                          relation_def=relation,
                                          selected_object=selected_object,
                                          related_object=related_object,
                                          reverse=reverse)):
            return

        cls.add_possible_relation_object(relation_object, selected_object_id, related_object_id)

    @classmethod
    def add_possible_relation_object(cls, relation_object, selected_object_id, related_object_id):
        if selected_object_id in cls.possible_object_to_object_relations_dict:
            if related_object_id in cls.possible_object_to_object_relations_dict[
                selected_object_id]:
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
            return RelationChangeHelpers.get_correct_identificator(object_to_filter_for)!= RelationChangeHelpers.get_correct_identificator(related_object)

        return filter_func

    @classmethod
    def get_screen(cls):
        return global_vars.otl_wizard.main_window.step3_relations

    @classmethod
    def create_relation_object(cls,
                               OSLO_relation:OSLORelatie,
                               source_object:AIMObject,
                               target_object:AIMObject) -> RelatieObject:
        try:
            relation_type = dynamic_create_type_from_uri(OSLO_relation.objectUri)
            relation_object = RelationCreator.create_relation(relation_type,source_object,target_object)
            relation_object.assetId.toegekendDoor = global_vars.external_toegekendDoor_label
        except Exception as e:
            source_id = None
            source_type = None
            if source_object:
                if hasattr(source_object,"assetId"):
                    source_id = source_object.assetId.identificator
                elif hasattr(source_object,"agentId"):
                    source_id = source_object.agentId.identificator
                if hasattr(source_object,"typeURI"):
                    source_type = RelationChangeHelpers.get_abbreviated_typeURI(source_object.typeURI,True)

            target_id = None
            target_type = None
            if target_object:
                if  hasattr(target_object,"assetId"):
                    target_id = target_object.assetId.identificator
                elif hasattr(target_object,"agentId"):
                    target_id = target_object.agentId.identificator
                if hasattr(target_object,"typeURI"):
                    target_type = RelationChangeHelpers.get_abbreviated_typeURI(target_object.typeURI,True)

            logging.debug(f"Couldn't make relation between source_type:{source_type} source_id:{source_id} {OSLO_relation.richting} target_type:{target_type} target_id:{target_id} for relation typeURI {OSLO_relation.objectUri}: \n {e}" )
            return None

        return relation_object



    @classmethod
    @save_assets
    def add_multiple_possible_relations_to_existing_relations(cls, data_list):

        heeft_betrokkene_in_selection = [True for data in data_list
                                         if cls.possible_object_to_object_relations_dict[data.source_id][data.target_id][data.index].typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#HeeftBetrokkene']

        if heeft_betrokkene_in_selection:
            data_list_and_relation_objects = [(data.source_id,data.target_id, cls.possible_object_to_object_relations_dict[data.source_id][
                data.target_id].pop(data.index)) for data in data_list]
            cls.get_screen().showMultiSelectionHeeftBetrokkeneAttributeDialogWindow(data_list_and_relation_objects)
        else:
            cls.last_added_to_existing = [RelationChangeDomain.dadd_possible_relation_to_existing_relations(data.source_id,
                                                                             data.target_id,
                                                                             data.index) for data in data_list]
        cls.update_frontend()

    @classmethod
    def add_possible_relation_to_existing_relations(cls, bron_asset_id, target_asset_id,
                                                    relation_object_index):
        relation_object = cls.possible_object_to_object_relations_dict[bron_asset_id][target_asset_id].pop(relation_object_index)

        # if relation_object.typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#HeeftBetrokkene':
        #     # don't add the relation
        #     cls.get_screen().showHeeftBetrokkeneAttributeDialogWindow(bron_asset_id,target_asset_id,relation_object)
        # else:
        cls.add_relation_object_to_existing_relations(relation_object)

        return relation_object

    @classmethod
    def add_relation_object_to_existing_relations(cls, relation_object):
        relation_object.isActief = True
        cls.existing_relations.append(relation_object)
        cls.get_screen().expand_existing_relations_folder_of(relation_typeURI=relation_object.typeURI)

    @classmethod
    def update_frontend(cls):
        cls.get_screen().fill_object_list(cls.shown_objects)
        cls.get_screen().fill_existing_relations_list(cls.existing_relations, cls.last_added_to_existing)
        if cls.selected_object:
            cls.set_possible_relations(selected_object=cls.selected_object)
            selected_object_id = RelationChangeHelpers.get_correct_identificator(cls.selected_object)
            possibleRelations = cls.possible_object_to_object_relations_dict[selected_object_id]
            cls.get_screen().fill_possible_relations_list(cls.selected_object, possibleRelations,last_added=cls.last_added_to_possible)

    @classmethod
    @save_assets
    def remove_multiple_existing_relations(cls, indices: list[int]) -> RelatieObject:
        cls.last_added_to_possible = [cls.remove_existing_relation(index) for index in indices]

        cls.update_frontend()

    @classmethod
    def remove_existing_relation(cls, index:int) -> RelatieObject:
        removed_relation = cls.existing_relations.pop(index)
        #if the removed relation already had a AIM ID it is set to false and kept if not it is
        # removed and made again in the possible relations
        removed_relation.isActief = False
        cls.get_screen().expand_possible_relations_folder_of(relation_typeURI=removed_relation.typeURI)

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
            cls.get_screen().fill_existing_relation_attribute_field(existing_relation_attribute_dict={})
            return
        
        last_index = indices[-1]
        last_selected_relation = cls.existing_relations[last_index]
        cls.get_screen().fill_existing_relation_attribute_field(
            existing_relation_attribute_dict=DotnotationDictConverter.to_dict(last_selected_relation))

    @classmethod
    def select_possible_relation_data(cls, selected_relations_data: list) -> None:
        if not selected_relations_data:
            cls.get_screen().fill_possible_relation_attribute_field({})
            return
        last_selected_keys = selected_relations_data[-1]
        last_selected_relation = cls.possible_object_to_object_relations_dict[last_selected_keys.source_id][last_selected_keys.target_id][last_selected_keys.index]

        last_selected_relation_partner_asset = RelationChangeDomain.get_object(
            identificator=last_selected_relation.doelAssetId.identificator)
        if last_selected_relation_partner_asset == cls.selected_object:
            last_selected_relation_partner_asset = RelationChangeDomain.get_object(
                identificator=last_selected_relation.bronAssetId.identificator)

        cls.get_screen().fill_possible_relation_attribute_field(possible_relation_attribute_dict=
            DotnotationDictConverter.to_dict(otl_object=last_selected_relation_partner_asset))

    @classmethod
    def get_internal_objects(cls):
        return cls.internal_objects

    @classmethod
    def get_persistent_relations(cls):
        return cls.existing_relations + cls.get_inactive_aim_id_relations()

    @classmethod
    def get_export_instances(cls) -> list[Union[RelatieObject, OTLObject]]:
        return cls.internal_objects + cls.get_persistent_relations()

    @classmethod
    def get_quicksave_instances(cls) -> list[Union[RelatieObject, OTLObject]]:
        return cls.shown_objects + cls.get_persistent_relations()

    @classmethod
    def apply_active_aim_id_relations(cls):
        for relation_instance in cls.aim_id_relations:
            if relation_instance.isActief:
                cls.existing_relations.append(relation_instance)

    @classmethod
    def get_inactive_aim_id_relations(cls):

        return [relation_instance for relation_instance in cls.aim_id_relations if not relation_instance.isActief]

    @classmethod
    def add_external_objects_to_shown_objects(cls):
        cls.shown_objects.extend(cls.external_objects)
        cls.external_object_added = True

    @classmethod
    def add_agent_objects_to_shown_objects(cls):
        cls.shown_objects.extend(cls.agent_objects)
        cls.external_object_added = True

    @classmethod
    def create_and_add_new_external_asset(cls, id_or_name, type_uri):
        new_external_object =  dynamic_create_instance_from_uri(type_uri)
        if new_external_object.typeURI == 'http://purl.org/dc/terms/Agent':
            new_external_agent: Agent = cast(Agent,new_external_object)
            new_external_agent.agentId.identificator = id_or_name
            cls.agent_objects.append(new_external_agent)
            cls.shown_objects.append(new_external_agent)
        else:
            new_external_asset: AIMObject = cast(AIMObject,new_external_object)
            new_external_asset.assetId.identificator = id_or_name
            new_external_asset.assetId.toegekendDoor = global_vars.external_toegekendDoor_label

            cls.external_objects.append(new_external_asset)
            cls.shown_objects.append(new_external_asset)

        cls.external_object_added = True
        cls.update_frontend()