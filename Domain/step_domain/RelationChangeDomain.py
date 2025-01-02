import asyncio
import logging
from copy import deepcopy
from pathlib import Path
from typing import List, Optional, Union, Callable

from otlmow_converter.DotnotationDictConverter import DotnotationDictConverter
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import dynamic_create_type_from_uri, \
    dynamic_create_instance_from_uri
from otlmow_model.OtlmowModel.BaseClasses.RelationInteractor import RelationInteractor
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
from GUI.screens.RelationChange_elements.RelationChangeHelpers import RelationChangeHelpers
from GUI.screens.screen_interface.RelationChangeScreenInterface import \
    RelationChangeScreenInterface

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
    project: Project = None
    collector: OSLOCollector = None

    internal_objects: list[AIMObject] = []  # Object in the project (placed by contractor)
    external_objects: list[AIMObject] = []  # Object outside the project (from DAVIE)
    agent_objects: list[Agent] = []  # Agent objects (not an AIMobject)
    shown_objects: list[RelationInteractor] = []  # All objects combined that are displayed on GUI (col 1)

    possible_relations_per_class_dict: dict[str, list[OSLORelatie]] = {}
    possible_object_to_object_relations_dict: dict[
        str, dict[str, list[RelatieObject]]] = {}  # (col 2)

    existing_relations: list[RelatieObject] = []  # relations
    aim_id_relations = []  # pre-existing relations from DAVIE

    selected_object: Optional[RelationInteractor] = None  # the asset/agent in col 1 selected by user
    last_added_to_existing: Optional[list[RelatieObject]] = []  # relation last added to col 3
    last_added_to_possible: Optional[list[RelatieObject]] = []  # relation last added to col 2

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

        cls.set_instances(objects_list=cls.project.load_validated_assets())
        global_vars.otl_wizard.main_window.step3_visuals.reload_html()

    @classmethod
    def set_instances(cls, objects_list: List[AIMObject]) -> None:
        # sourcery skip: use-contextlib-suppress
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
                # noinspection PyTypeChecker
                relation_instance: RelatieObject = instance
                is_aim_id = False
                # noinspection PyBroadException
                try:
                    is_aim_id = OTLObjectHelper.is_aim_id(aim_id=relation_instance.assetId.identificator)
                except Exception:
                    pass

                if is_aim_id or not relation_instance.isActief:
                    cls.aim_id_relations.append(relation_instance)
                else:
                    cls.existing_relations.append(relation_instance)

            else:
                if instance.typeURI == 'http://purl.org/dc/terms/Agent':
                    # noinspection PyTypeChecker
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
    def get_all_relations(cls) -> list[RelatieObject]:
        """Retrieves all existing relations from the class.

        This method combines and returns the lists of existing relations and AIM ID
        relations stored in the class. It provides a unified view of all relations
        for further processing or display.

        :param cls: The class itself.
        :returns: A list containing all existing and AIM ID relations.
        :rtype: list
        """

        return cls.existing_relations + cls.aim_id_relations

    @classmethod
    def get_object(cls, identificator: str) -> Optional[RelationInteractor]:
        # sourcery skip: use-named-expression
        """
        Retrieves an object from the list of shown objects based on its identificator.

        This method filters the list of shown objects to find an object that matches
        the provided identificator. If multiple objects are found, it currently does
        not handle the error case, but if exactly one object is found, it returns that object.

        :param cls: The class itself.
        :param identificator: The identificator of the object to retrieve.
        :type identificator: str
        :returns: The matching OTL object if found, otherwise None.
        :rtype: Optional[RelationInteractor]
        """
        filtered_objects = list(filter(cls.filter_on_id(id_to_check=identificator), cls.shown_objects))

        if filtered_objects:
            if len(filtered_objects) > 1:
                logging.debug(f"ERROR RelationChangeDomain.get_object function found multiple "
                              f"objects with id: {identificator}")
                pass  # TODO: raise error of 2 objects with the same identificator in the list
            else:
                return filtered_objects[0]
        return None

    @classmethod
    def filter_on_id(cls, id_to_check: str):
        """
        Filters objects based on a specified identifier.
        This class method returns a lambda function that checks if the identifier of a
        given object matches the provided ID.

        :param id_to_check: The identifier to compare against.
        :type id_to_check: str

        :return: A lambda function that takes an object and returns True if its identifier matches the specified ID, otherwise False.
        :rtype: function
        """

        return lambda otl_object: RelationChangeHelpers.get_correct_identificator(
            otl_object) == id_to_check

    @classmethod
    def set_possible_relations(cls, selected_object: RelationInteractor):
        """
        Sets the possible relations for the specified selected object and updates the user
        interface accordingly. This method manages the collection and display of relations based
        on the selected object's typeURI.

        :param selected_object: The object for which possible relations are to be displayed.
        :type selected_object: AIMObject

        :return: None

        :raises ValueError: If the selected_object is invalid or cannot be processed.

        :Examples:
            RelationChangeDomain.set_possible_relations(selected_object)
        """

        cls.selected_object = selected_object
        if not selected_object:
            cls.get_screen().clear_possible_relation_elements()
            return

        if (cls.external_object_added or not
                RelationChangeDomain.are_possible_relations_to_other_class_types_collected_for(
                selected_object.typeURI)):
            cls.collect_possible_relations_to_class_types_from(selected_object)
            cls.external_object_added = False

        related_objects: list[RelationInteractor] = list(
            filter(RelationChangeDomain.filter_out(object_to_filter_for=selected_object), 
                   cls.shown_objects))

        selected_id = RelationChangeHelpers.get_correct_identificator(otl_object=selected_object)
        relation_list = cls.possible_relations_per_class_dict[selected_object.typeURI]

        cls.possible_object_to_object_relations_dict[selected_id] = {}
        cls.add_inactive_relations_to_possible_relations(selected_id=selected_id)
        cls.add_all_possible_relations_between_selected_and_related_objects(
            relation_list=relation_list,selected_object=selected_object,
            related_objects=related_objects)
        cls.possible_object_to_object_relations_dict = (
            Helpers.sort_nested_dict(dictionary=cls.possible_object_to_object_relations_dict))

        possible_relations_for_this_object = cls.get_possible_relations_for(selected_id=selected_id)

        # noinspection PyTypeChecker
        object_attributes_dict = DotnotationDictConverter.to_dict(otl_object=selected_object)

        cls.get_screen().fill_possible_relations_list(source_object=selected_object,
                                                      relations=possible_relations_for_this_object,
                                                      last_added=cls.last_added_to_possible)
        cls.get_screen().fill_object_attribute_field(object_attribute_dict=object_attributes_dict)

    @classmethod
    def get_possible_relations_for(cls, selected_id=str):
        """
        Retrieves the possible relations for a given selected ID. This method checks if the selected ID exists in the internal dictionary of possible relations and returns the corresponding relations if found.

        :param selected_id: The identifier for which possible relations are to be retrieved.
        :type selected_id: Any

        :return: A dictionary of possible relations for the selected ID, or an empty dictionary if none are found.
        :rtype: dict
        """

        if selected_id in cls.possible_object_to_object_relations_dict:
            return cls.possible_object_to_object_relations_dict[selected_id]
        return {}

    @classmethod
    def add_all_possible_relations_between_selected_and_related_objects(
            cls, relation_list: list[OSLORelatie],selected_object: RelationInteractor,
            related_objects: list[RelationInteractor]) -> None:
        """
        Adds all possible relations between a selected object and its related objects based on the
        provided relation list. This method checks existing relations to avoid duplicates and
        establishes new relations as necessary.

        :param relation_list: A list of relations that define how objects can be related.
        :type relation_list:  list[OSLORelatie]

        :param selected_object: The object for which relations are being established.
        :type selected_object: RelationInteractor

        :param related_objects: A list of objects that may be related to the selected object.
        :type related_objects:  list[RelationInteractor]

        :return: None
        """

        for relation in relation_list:
            if relation.bron_uri == selected_object.typeURI:
                for related_object in related_objects:
                    if cls.get_same_relations_in_list(
                            relation_list=cls.existing_relations, relation_def=relation,
                            selected_object=selected_object, related_object=related_object):
                        continue
                    if relation.doel_uri == related_object.typeURI:
                        cls.add_relation_between(relation=relation,selected_object=selected_object,
                                                 related_object=related_object)

            if relation.doel_uri == selected_object.typeURI:
                for related_object in related_objects:
                    if cls.get_same_relations_in_list(
                            relation_list=cls.existing_relations, relation_def=relation,
                            selected_object=selected_object, related_object=related_object,
                            reverse=True):
                        continue

                    if relation.bron_uri == related_object.typeURI:
                        cls.add_relation_between(relation=relation,selected_object=selected_object,
                                                 related_object=related_object, reverse=True)

    @classmethod
    def add_inactive_relations_to_possible_relations(cls, selected_id: str) -> None:
        """
        Adds inactive relations to the list of possible relations for a given selected ID.
        This method retrieves inactive relations and checks if the selected ID matches either
        the source or target of those relations, adding them accordingly.

        :param selected_id: The identifier of the selected object for which inactive relations
                            are to be added.
        :type selected_id: str

        :return: None
        """

        inactive_relations = cls.get_inactive_aim_id_relations()
        for relation_instance in inactive_relations:
            source_id = relation_instance.bronAssetId.identificator
            target_id = relation_instance.doelAssetId.identificator
            if source_id == selected_id:
                cls.add_possible_relation_object(relation_object=relation_instance,
                                                 selected_object_id=source_id,
                                                 related_object_id=target_id)
            if target_id == selected_id:
                cls.add_possible_relation_object(relation_object=relation_instance,
                                                 selected_object_id=target_id,
                                                 related_object_id=source_id)

    @classmethod
    def are_possible_relations_to_other_class_types_collected_for(cls, typeURI: str):
        """
        Checks if possible relations for a given class type URI have been collected.
        This method verifies the presence of the type URI in the internal dictionary of
        possible relations.

        :param typeURI: The URI of the class type to check for collected relations.
        :type typeURI: str

        :return: True if possible relations have been collected for the specified type URI, otherwise False.
        :rtype: bool
        """

        return typeURI in cls.possible_relations_per_class_dict.keys()

    @classmethod
    def collect_possible_relations_to_class_types_from(cls, selected_object:RelationInteractor):
        """
        Collects possible relations for a specified selected object based on its type.
        This method populates the internal dictionary of possible relations, considering both
        internal and external objects, and handles exceptions during the collection process.

        :param selected_object: The object from which possible relations are to be collected.
        :type selected_object: RelationInteractor

        :return: None
        """

        try:
            if cls.external_objects or cls.agent_objects:
                # this is the long search, but it includes relations with external assets
                cls.possible_relations_per_class_dict[selected_object.typeURI] = (
                    RelationChangeDomain.get_all_concrete_relation_from_full_model(
                        selected_object=selected_object))
            else:
                cls.possible_relations_per_class_dict[selected_object.typeURI] = \
                    cls.collector.find_all_concrete_relations(objectUri=selected_object.typeURI,
                                                              allow_duplicates=False)
        except ValueError as e:
            logging.debug(e)
            cls.possible_relations_per_class_dict[selected_object.typeURI] = (
                RelationChangeDomain.get_all_concrete_relation_from_full_model(
                    selected_object=selected_object))

    @classmethod
    def get_all_concrete_relation_from_full_model(cls, selected_object:RelationInteractor):
        """
        Retrieves all concrete relations from the full model for a specified selected object.
        This method processes the relations and returns them in a structured format suitable for
        further use.

        :param selected_object: The object for which all concrete relations are to be retrieved.
        :type selected_object: RelationInteractor

        :return: A list of concrete OSLORelatie objects representing the relations.
        :rtype: list[OSLORelatie]
        """

        # noinspection PyProtectedMember
        all_relations = selected_object._get_all_concrete_relations()
        concrete_OSLO_relations: list[OSLORelatie] = [OSLORelatie(
            bron_overerving="",
            doel_overerving="",
            bron_uri=concrete_relation[0],
            doel_uri=concrete_relation[2],
            objectUri=concrete_relation[1],
            richting=concrete_relation[3],
            deprecated_version=concrete_relation[4],
            usagenote="") for concrete_relation in all_relations]
        return concrete_OSLO_relations


    @classmethod
    def get_same_relations_in_list(cls, relation_list: list[RelatieObject],
                                   relation_def: OSLORelatie,
                                   selected_object: RelationInteractor,
                                   related_object: RelationInteractor,
                                   reverse: bool = False):
        """
        Retrieves all relations from a given list that match a specified relation definition.
        This method checks for existing relations that are equivalent to the provided relation
        definition, considering the selected and related objects, and can account for reverse
        relationships.

        :param relation_list: A list of relation objects to search through.
        :type relation_list: list[RelatieObject]

        :param relation_def: The relation definition to match against.
        :type relation_def: OSLORelatie

        :param selected_object: The selected object involved in the relation.
        :type selected_object: RelationInteractor

        :param related_object: The related object involved in the relation.
        :type related_object: RelationInteractor

        :param reverse: A boolean indicating whether to check for reverse relations. Defaults to False.
        :type reverse: bool, optional

        :return: A list of relations that match the specified relation definition.
        :rtype: list
        """

        return [relation for relation in relation_list
                if cls.is_same_relation(existing_relation=relation, relation_def=relation_def,
                                        selected=selected_object, related=related_object,
                                        reverse=reverse)
                ]


    @classmethod
    def is_same_relation(cls, existing_relation: RelatieObject, relation_def: OSLORelatie,
                         selected:RelationInteractor, related: RelationInteractor,
                         reverse: bool = False) -> bool:
        """
        Determines whether an existing relation matches a specified relation definition
        based on the selected and related objects. This method checks the identifiers of the
        existing relation against the provided relation definition and can account for both standard
        and reverse relationships.

        :param existing_relation: The relation object to compare against the relation definition.
        :type existing_relation: RelatieObject

        :param relation_def: The relation definition to match.
        :type relation_def: OSLORelatie

        :param selected: The selected object involved in the relation.
        :type selected: RelationInteractor

        :param related: The related object involved in the relation.
        :type related: RelationInteractor

        :param reverse: A boolean indicating whether to check for reverse relations. Defaults to False.
        :type reverse: bool, optional

        :return: True if the existing relation matches the relation definition, otherwise False.
        :rtype: bool
        """

        existing_source_id:str = existing_relation.bronAssetId.identificator
        existing_target_id:str  = existing_relation.doelAssetId.identificator
        related_id:str = RelationChangeHelpers.get_correct_identificator(related)
        selected_id:str = RelationChangeHelpers.get_correct_identificator(selected)

        if existing_relation.typeURI == relation_def.objectUri:
            if relation_def.richting == "Unspecified":
                return ((existing_source_id == related_id and existing_target_id == selected_id) or
                        (existing_source_id == selected_id and existing_target_id == related_id))
            else:
                return ((existing_source_id == related_id  and existing_target_id == selected_id)
                        if reverse else
                        (existing_source_id == selected_id and existing_target_id == related_id))

    @classmethod
    def add_relation_between(cls, relation: OSLORelatie, selected_object: RelationInteractor,
                             related_object: RelationInteractor, reverse: bool = False) -> None:
        """
        Adds a relation between two specified objects, considering the direction of the relation.
        This method creates a relation object based on the provided relation definition and adds it
        to the internal dictionary of possible relations if it does not already exist.

        :param relation: The relation definition that describes how the objects are related.
        :type relation: OSLORelatie

        :param selected_object: The first object involved in the relation.
        :type selected_object: RelationInteractor

        :param related_object: The second object involved in the relation.
        :type related_object: RelationInteractor

        :param reverse: A boolean indicating whether to create the relation in the reverse direction. Defaults to False.
        :type reverse: bool, optional

        :return: None
        """

        selected_object_id:str = RelationChangeHelpers.get_correct_identificator(selected_object)
        related_object_id:str = RelationChangeHelpers.get_correct_identificator(related_object)

        # the relation object is reversed from the wrong direction to the right direction
        # noinspection PyUnusedLocal
        relation_object = None
        if reverse:
            relation_object = cls.create_relation_object(OSLO_relation=relation,
                                                         source_object=related_object,
                                                         target_object= selected_object)
        else:
            relation_object = cls.create_relation_object(OSLO_relation=relation,
                                                         source_object=selected_object,
                                                         target_object=related_object)

        if not relation_object:
            return

        if (selected_object_id in cls.possible_object_to_object_relations_dict.keys() and
                related_object_id in cls.possible_object_to_object_relations_dict[
                    selected_object_id].keys() and
                cls.get_same_relations_in_list(
                    cls.possible_object_to_object_relations_dict[selected_object_id][
                        related_object_id],
                    relation_def=relation,
                    selected_object=selected_object,
                    related_object=related_object,
                    reverse=reverse)):
            return

        cls.add_possible_relation_object(relation_object, selected_object_id, related_object_id)

    @classmethod
    def add_possible_relation_object(cls, relation_object, selected_object_id, related_object_id) \
            -> None:
        """
        Adds a relation object to the internal dictionary of possible relations between two
        specified objects. This method updates the dictionary to either append the relation to an
        existing list or create a new entry if no relations currently exist.

        :param relation_object: The relation object to be added.
        :type relation_object: Any

        :param selected_object_id: The identifier of the first object involved in the relation.
        :type selected_object_id: str

        :param related_object_id: The identifier of the second object involved in the relation.
        :type related_object_id: str

        :return: None
        """

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
    def filter_out(cls, object_to_filter_for: RelationInteractor)-> Callable:
        """
        Creates a filter function that excludes a specified object from a list of related objects.
        This method returns a callable that can be used to filter out the object to ensure it is
        not included in subsequent operations.

        :param object_to_filter_for: The object that should be excluded from the filtering process.
        :type object_to_filter_for: RelationInteractor

        :return: A callable function that takes a related object and returns True
                 if it should be included, or False if it should be excluded.
        :rtype: Callable
        """

        def filter_func(related_object: RelationInteractor):
            return (RelationChangeHelpers.get_correct_identificator(object_to_filter_for) != 
                    RelationChangeHelpers.get_correct_identificator(related_object))

        return filter_func


    @classmethod
    def get_screen(cls) -> RelationChangeScreenInterface:
        return global_vars.otl_wizard.main_window.step3_relations

    @classmethod
    def create_relation_object(cls,
                               OSLO_relation: OSLORelatie,
                               source_object: RelationInteractor,
                               target_object: RelationInteractor) -> Optional[RelatieObject]:
        """
        Creates a relation object based on the provided OSLO relation and the specified source and
        target objects. This method attempts to instantiate the relation object and assigns it
        relevant properties, logging any errors encountered during the process.

        :param OSLO_relation: The OSLO relation definition used to create the relation object.
        :type OSLO_relation: OSLORelatie

        :param source_object: The object that serves as the source in the relation.
        :type source_object: RelationInteractor

        :param target_object: The object that serves as the target in the relation.
        :type target_object: RelationInteractor

        :return: The created relation object if successful, or None if an error occurred.
        :rtype: Optional[RelatieObject]
        """

        try:
            relation_type = dynamic_create_type_from_uri(OSLO_relation.objectUri)
            # noinspection PyTypeChecker
            relation_object = RelationCreator.create_relation(relation_type= relation_type,
                                                              source=source_object,
                                                              target=target_object)
            relation_object.assetId.toegekendDoor = global_vars.external_toegekendDoor_label
        except Exception as e:
            source_id = None
            source_type = None
            if source_object:
                source_id = RelationChangeHelpers.get_correct_identificator(
                    otl_object=source_object)
                source_type = RelationChangeHelpers.get_abbreviated_typeURI(
                        typeURI=source_object.typeURI, add_namespace=True)

            target_id = None
            target_type = None
            if target_object:

                target_id = RelationChangeHelpers.get_correct_identificator(
                    otl_object=target_object)
                target_type = RelationChangeHelpers.get_abbreviated_typeURI(
                        target_object.typeURI, True)

            logging.debug(
                f"Couldn't make relation between source_type:{source_type} source_id:{source_id} {OSLO_relation.richting} target_type:{target_type} target_id:{target_id} for relation typeURI {OSLO_relation.objectUri}: \n {e}")
            return None

        return relation_object

    @classmethod
    @save_assets
    def add_multiple_possible_relations_to_existing_relations(cls, data_list):
        """
        Adds multiple possible relations to existing relations based on the provided data list.
        This method checks for specific attributes in the relations and either displays a dialog
        for user confirmation or directly updates the existing relations.

        :param data_list: A list of data objects containing source and target IDs along with their respective indices for the relations to be added.
        :type data_list: list

        :return: None
        """

        # sourcery skip: use-named-expression
        heeft_betrokkene_in_selection = [True for data in data_list
                                         if cls.possible_object_to_object_relations_dict[
                                             data.source_id][data.target_id][
                                             data.index].typeURI == 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#HeeftBetrokkene']

        if heeft_betrokkene_in_selection:
            data_list_and_relation_objects = [(data.source_id, data.target_id,
                                               cls.possible_object_to_object_relations_dict[
                                                   data.source_id][
                                                   data.target_id].pop(data.index)) for data in
                                              data_list]
            cls.get_screen().showMultiSelectionHeeftBetrokkeneAttributeDialogWindow(
                data_list_and_relation_objects=data_list_and_relation_objects)
        else:
            cls.last_added_to_existing = [
                RelationChangeDomain.add_possible_relation_to_existing_relations(
                    bron_asset_id=data.source_id,target_asset_id=data.target_id,
                    relation_object_index=data.index) for data in data_list]
        cls.update_frontend()

    @classmethod
    def add_possible_relation_to_existing_relations(cls, bron_asset_id, target_asset_id,
                                                    relation_object_index) -> RelatieObject:
        """
        Adds a possible relation to the existing relations using the specified source and target
        asset IDs along with the index of the relation object. This method retrieves the relation
        object from the internal dictionary, adds it to the existing relations, and returns the
        relation object.

        :param bron_asset_id: The identifier of the source asset for the relation.
        :type bron_asset_id: str

        :param target_asset_id: The identifier of the target asset for the relation.
        :type target_asset_id: str

        :param relation_object_index: The index of the relation object to be added.
        :type relation_object_index: int

        :return: The relation object that was added to the existing relations.
        :rtype: RelatieObject
        """

        relation_object = cls.possible_object_to_object_relations_dict[bron_asset_id][
            target_asset_id].pop(relation_object_index)

        cls.add_relation_object_to_existing_relations(relation_object=relation_object)

        return relation_object

    @classmethod
    def add_relation_object_to_existing_relations(cls, relation_object: RelatieObject):
        """
        Adds a relation object to the list of existing relations and marks it as active.
        This method also updates the user interface to reflect the addition by expanding the folder
        corresponding to the relation type.

        :param relation_object: The relation object to be added to the existing relations.
        :type relation_object: RelatieObject

        :return: None
        """

        relation_object.isActief = True
        cls.existing_relations.append(relation_object)
        cls.get_screen().expand_existing_relations_folder_of(
            relation_typeURI=relation_object.typeURI)

    @classmethod
    def update_frontend(cls):
        """
        Updates the user interface to reflect the current state of objects and relations.
        This method populates the object list and existing relations list, and sets the possible
        relations for the selected object.

        :return: None
        """

        cls.get_screen().fill_object_list(objects=cls.shown_objects)
        cls.get_screen().fill_existing_relations_list(relations_objects=cls.existing_relations,
                                                      last_added=cls.last_added_to_existing)

        cls.set_possible_relations(selected_object=cls.selected_object)

    @classmethod
    @save_assets
    def remove_multiple_existing_relations(cls, indices: list[int]) -> None:
        """
        Removes multiple existing relations based on the provided indices. This method updates the
        internal state by removing the specified relations and refreshes the user interface to
        reflect the changes.

        :param indices: A list of indices corresponding to the existing relations to be removed.
        :type indices: list[int]

        :return: None
        """

        cls.last_added_to_possible = [cls.remove_existing_relation(index) for index in indices]

        cls.update_frontend()

    @classmethod
    def remove_existing_relation(cls, index: int) -> RelatieObject:
        """
        Removes an existing relation from the list based on the specified index. This method marks
        the removed relation as inactive, updates the user interface to reflect the change, and
        returns the removed relation object.

        :param index: The index of the existing relation to be removed.
        :type index: int

        :return: The relation object that was removed from the existing relations.
        :rtype: RelatieObject
        """

        removed_relation = cls.existing_relations.pop(index)
        # if the removed relation already had an AIM ID it is set to false and kept if not it is
        # removed and made again in the possible relations
        removed_relation.isActief = False
        cls.get_screen().expand_possible_relations_folder_of(
            relation_typeURI=removed_relation.typeURI)

        return removed_relation

    @classmethod
    def select_existing_relation_indices(cls, indices: list[int]) -> None:
        """
        Selects existing relations based on the provided indices and updates the user interface
        accordingly. This method retrieves the last selected relation and populates the attribute
        field with its details, or clears the field if no indices are provided.

        :param indices: A list of indices corresponding to the existing relations to be selected.
        :type indices: list[int]

        :return: None
        """

        if not indices:
            cls.get_screen().fill_existing_relation_attribute_field(
                existing_relation_attribute_dict={})
            return

        last_index = indices[-1]
        last_selected_relation = cls.existing_relations[last_index]
        cls.get_screen().fill_existing_relation_attribute_field(
            existing_relation_attribute_dict=DotnotationDictConverter.to_dict(
                last_selected_relation))

    @classmethod
    def select_possible_relation_data(cls, selected_relations_data: list) -> None:
        """
        Selects and displays data for possible relations based on the provided selected relations
        data. This method updates the user interface with the attributes of the last selected
        relation partner asset, or clears the attribute field if no relations are selected.

        :param selected_relations_data: A list of data objects representing the selected possible
                                        relations.
        :type selected_relations_data: list

        :return: None
        """

        if not selected_relations_data:
            cls.get_screen().fill_possible_relation_attribute_field({})
            return
        last_selected_keys = selected_relations_data[-1]
        last_selected_relation = \
        cls.possible_object_to_object_relations_dict[last_selected_keys.source_id][
            last_selected_keys.target_id][last_selected_keys.index]

        last_selected_relation_partner_asset: RelationInteractor = RelationChangeDomain.get_object(
            identificator=last_selected_relation.doelAssetId.identificator)
        if last_selected_relation_partner_asset == cls.selected_object:
            last_selected_relation_partner_asset = RelationChangeDomain.get_object(
                identificator=last_selected_relation.bronAssetId.identificator)

        # noinspection PyTypeChecker
        cls.get_screen().fill_possible_relation_attribute_field(
            possible_relation_attribute_dict=DotnotationDictConverter.to_dict(
                                             otl_object=last_selected_relation_partner_asset))

    @classmethod
    def get_internal_objects(cls) -> list[RelationInteractor]:
        """
        Retrieves the list of internal objects managed by the class.
        This method provides access to the internal state of the class, allowing other components
        to utilize the internal objects as needed.

        :return: A list of internal RelationInteractor objects.
        :rtype: list[RelationInteractor]
        """

        return cls.internal_objects

    @classmethod
    def get_persistent_relations(cls) -> list[RelatieObject]:
        """
        Retrieves a combined list of persistent relations, this contains all active relations but
        only those inactive relations that are in the DAVIE database.
        This method provides access to all relations that are currently stored, allowing
        for comprehensive management of relational data.

        :return: A list of persistent relations, including existing and inactive (DAVIE) relations.
        :rtype: list[RelatieObject]
        """

        return cls.existing_relations + cls.get_inactive_aim_id_relations()

    @classmethod
    def get_export_instances(cls) -> list[Union[RelatieObject, RelationInteractor]]:
        """
         Retrieves a combined list of instances that need to be included in an exported file,
         including both internal objects and persistent relations.
         This method provides a comprehensive view of all objects that can be exported,
         facilitating data management and export operations.

        :return: A list of export instances, which may include RelatieObject and RelationInteractor types.
        :rtype: list[Union[RelatieObject, RelationInteractor]]
        """

        return cls.internal_objects + cls.get_persistent_relations()

    @classmethod
    def get_quicksave_instances(cls) -> list[Union[RelatieObject, RelationInteractor]]:
        """
        Retrieves a combined list of  instances to make a quicksave file,
        including both shown objects and persistent relations.
        This method provides a convenient way to access all objects that are currently visible
        and can be quickly saved, enhancing data management efficiency.

        :return: A list of quicksave instances, which may include RelatieObject and RelationInteractor types.
        :rtype: list[Union[RelatieObject, RelationInteractor]]
        """

        return cls.shown_objects + cls.get_persistent_relations()

    @classmethod
    def apply_active_aim_id_relations(cls) -> None:
        """
        Applies active AIM ID relations (already in DAVIE) to the list of existing relations.
        This method iterates through the AIM ID relations and appends only those that are
        marked as active to the existing relations, ensuring that the current state reflects only
        the relevant relations.

        :return: None
        """

        for relation_instance in cls.aim_id_relations:
            if relation_instance.isActief:
                cls.existing_relations.append(relation_instance)

    @classmethod
    def get_inactive_aim_id_relations(cls):
        """
        Retrieves a list of inactive AIM ID relations from the collection of AIM ID relations
        (already in DAVIE).
        This method filters the relations to return only those that are marked as inactive,
        providing a way to access non-active relations for further processing or analysis.

        :return: A list of inactive AIM ID relations.
        :rtype: list
        """

        return [relation_instance for relation_instance in cls.aim_id_relations if
                not relation_instance.isActief]

    @classmethod
    def add_external_objects_to_shown_objects(cls):
        """
        Adds external objects to the list of shown objects.
        This method updates the internal state by extending the shown objects with external objects
        and marks that external objects have been added.

        :return: None
        """

        cls.shown_objects.extend(cls.external_objects)
        cls.external_object_added = True

    @classmethod
    def add_agent_objects_to_shown_objects(cls):
        """
        Adds agent objects to the list of shown objects. This method updates the internal state by
        extending the shown objects with agent objects and marks that external objects have been
        added.

        :return: None
        """
        cls.shown_objects.extend(cls.agent_objects)
        cls.external_object_added = True

    # noinspection PyUnresolvedReferences,PyTypeChecker
    @classmethod
    def create_and_add_new_external_asset(cls, id_or_name: str, type_uri: str):
        """
        Creates a new external asset based on the provided identifier or name and type URI,
        and adds it to the appropriate collections. This method distinguishes between agent objects
        and other asset types, updating the relevant lists and the user interface accordingly.

        :param id_or_name: The identifier or name to assign to the new external asset.
        :type id_or_name: str

        :param type_uri: The type URI that defines the kind of external asset to create.
        :type type_uri: str

        :return: None
        """

        new_external_object: RelationInteractor = dynamic_create_instance_from_uri(type_uri)
        if  hasattr(new_external_object,"agentId"):
            new_external_object.agentId.identificator = id_or_name
            cls.agent_objects.append(new_external_object)
        else:
            new_external_object.assetId.identificator = id_or_name
            new_external_object.assetId.toegekendDoor = global_vars.external_toegekendDoor_label
            cls.external_objects.append(new_external_object)

        cls.shown_objects.append(new_external_object)

        cls.external_object_added = True
        cls.update_frontend()
