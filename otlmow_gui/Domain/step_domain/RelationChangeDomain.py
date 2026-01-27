import asyncio
import gc
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Optional, Union, Callable

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
from otlmow_model.OtlmowModel.Helpers.generated_lists import get_hardcoded_class_dict, \
    get_concrete_subclasses_from_class_dict
from otlmow_modelbuilder.OSLOCollector import OSLOCollector
from otlmow_modelbuilder.SQLDataClasses.OSLORelatie import OSLORelatie
from otlmow_gui.Domain import global_vars

from otlmow_gui.Domain.util.Helpers import Helpers
from otlmow_gui.Domain.logger.OTLLogger import OTLLogger
from otlmow_gui.Domain.project.Project import Project
from otlmow_gui.GUI.dialog_windows.LoadingImageWindow import add_loading_screen
from otlmow_gui.GUI.screens.RelationChange_elements.RelationChangeHelpers import RelationChangeHelpers
from otlmow_gui.GUI.screens.screen_interface.RelationChangeScreenInterface import \
    RelationChangeScreenInterface
from otlmow_gui.exception_handler.ExceptionHandlers import create_task_reraise_exception

ROOT_DIR = Path(__file__).parent.parent

def async_save_assets(func):
    """Decorator that saves assets after executing the decorated function.

    This decorator wraps a function to ensure that after its execution, the current
    project's assets in memory are updated and saved. It also starts the event loop
    for the header in the main window to animate the OTL Wizard 2 logo during saving.

    :param func: The function to be decorated.
    :returns: The wrapper function that includes the saving logic.
    """

    async def wrapper_func(*args, **kwargs):
        res = await func(*args, **kwargs)
        global_vars.current_project.assets_in_memory = RelationChangeDomain.get_quicksave_instances()
        await global_vars.current_project.save_validated_assets()
        global_vars.otl_wizard.main_window.step_3_tabwidget.header.start_event_loop()
        return res

    return wrapper_func

class RelationChangeDomain:
    """
    RelationChangeDomain manages the relationships between various objects within a project. It provides methods for initializing project data, managing internal and external objects, and handling relations, including adding, removing, and retrieving relations.

    Attributes:
        project (Project): The current project being managed.
        collector (OSLOCollector): The collector for OSLO data.
        internal_objects (list[Union[RelatieObject, RelationInteractor]]): Objects placed by the contractor within the project.
        external_objects (list[Union[RelatieObject, RelationInteractor]]): Object outside the project (from DAVIE)
        agent_objects (list[Agent]): Agent objects that are not AIM objects.
        shown_objects (list[RelationInteractor]): All objects displayed in the GUI.
        possible_relations_per_class_dict (dict[str, list[OSLORelatie]]): Possible relations
            categorized by class type
        possible_object_to_object_relations_dict (dict[str, dict[str, list[RelatieObject]]]):
            Possible Relations between objects that the user can choose from.
        existing_relations (list[RelatieObject]): Currently active relations.
        aim_id_relations (list): Pre-existing relations sourced from DAVIE.
        selected_object (Optional[RelationInteractor]): The currently selected object from
            the OTL-asset column in the GUI.
        last_added_to_existing (Optional[list[RelatieObject]]): The last relations added to
            existing relations.
        last_added_to_possible (Optional[list[RelatieObject]]): The last relations added to
            possible relations.
        external_object_added (bool): Flag indicating if an external object has been added.

    Methods:
        init_static(project: Project) -> None: Initializes static resources for the class.
        load_project_relation_data() -> None: Loads project relation data asynchronously.
        set_instances(objects_list: list[Union[RelatieObject, RelationInteractor]]) -> None: Processes and categorizes AIM objects.
        create_and_add_missing_external_assets_from_relations() -> None: Creates missing external
            assets from relations.
        get_all_relations() -> list[RelatieObject]: Retrieves all existing relations.
        get_object(identificator: str) -> Optional[RelationInteractor]: Retrieves an object by its
            identifier.
        filter_on_id(id_to_check: str): Filters objects based on a specified identifier.
        set_possible_relations(selected_object: RelationInteractor) -> None: Sets possible
            relations for a selected object.
        get_possible_relations_for(selected_id: str) -> dict: Retrieves possible relations for a
            given ID.
        add_all_possible_relations_between_selected_and_related_objects(
            relation_list: list[OSLORelatie], selected_object: RelationInteractor,
            related_objects: list[RelationInteractor]) -> None: Adds possible relations between
            selected and related objects.
        add_inactive_relations_to_possible_relations(selected_id: str) -> None: Adds inactive
            relations to possible relations.
        are_possible_relations_to_other_class_types_collected_for(typeURI: str) -> bool: Checks if
            possible relations for a class type URI have been collected.
        collect_possible_relations_to_class_types_from(selected_object: RelationInteractor)
            -> None: Collects possible relations for a selected object.
        get_all_concrete_relation_from_full_model(selected_object: RelationInteractor)
            -> list[OSLORelatie]: Retrieves all concrete relations for a selected object.
        get_same_relations_in_list(relation_list: list[RelatieObject], relation_def: OSLORelatie,
            selected_object: RelationInteractor, related_object: RelationInteractor,
            reverse: bool = False) -> list: Retrieves relations matching a specified definition.
        is_same_relation(existing_relation: RelatieObject, relation_def: OSLORelatie,
            selected: RelationInteractor, related: RelationInteractor, reverse: bool = False)
            -> bool: Determines if an existing relation matches a specified definition.
        add_relation_between(relation: OSLORelatie, selected_object: RelationInteractor,
            related_object: RelationInteractor, reverse: bool = False) -> None: Adds a relation
            between two objects.
        add_possible_relation_object(relation_object, selected_object_id, related_object_id)
            -> None: Adds a relation object to possible relations.
        filter_out(object_to_filter_for: RelationInteractor) -> Callable: Creates a filter function
            to exclude a specified object.
        get_screen() -> RelationChangeScreenInterface: Retrieves the current screen interface.
        create_relation_object(OSLO_relation: OSLORelatie, source_object: RelationInteractor,
            target_object: RelationInteractor) -> Optional[RelatieObject]: Creates a relation
            object based on provided definitions.
        add_multiple_possible_relations_to_existing_relations(data_list): Adds multiple possible
            relations to existing relations.
        add_possible_relation_to_existing_relations( bron_asset_id:str, target_asset_id:str,
            relation_object_index:int) -> RelatieObject: Adds a possible relation to existing
            relations.
        add_relation_object_to_existing_relations(relation_object: RelatieObject): Adds a relation
            object to existing relations.
        update_frontend(): Updates the user interface to reflect the current state of objects and
            relations.
        remove_multiple_existing_relations(indices: list[int]) -> None: Removes multiple existing
            relations based on indices.
        remove_existing_relation(index: int) -> RelatieObject: Removes an existing relation by
            index.
        select_existing_relation_indices(indices: list[int]) -> None: Selects existing relations
            based on indices.
        select_possible_relation_data(selected_relations_data: list) -> None: Selects and displays
            data for possible relations.
        get_internal_objects() -> list[RelationInteractor]: Retrieves the list of internal objects.
        get_persistent_relations() -> list[RelatieObject]: Retrieves a combined list of persistent
            relations.
        get_export_instances() -> list[Union[RelatieObject, RelationInteractor]]: Retrieves a
            combined list of instances for export.
        get_quicksave_instances() -> list[Union[RelatieObject, RelationInteractor]]: Retrieves a
            combined list of instances for quicksave.
        apply_active_aim_id_relations() -> None: Applies active AIM ID relations to existing
            relations.
        get_inactive_aim_id_relations() -> list: Retrieves a list of inactive AIM ID relations.
        add_external_objects_to_shown_objects() -> None: Adds external objects to shown objects.
        add_agent_objects_to_shown_objects() -> None: Adds agent objects to shown objects.
        create_and_add_new_external_asset(id_or_name: str, type_uri: str) -> None: Creates and
            adds a new external asset.
    """

    project: Project = None
    collector: OSLOCollector = None

    internal_objects: list[RelationInteractor] = []  # Object in the project (placed by contractor)
    external_objects: list[RelationInteractor] = []  # Object outside the project (from DAVIE)
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

    regenerate_relation_types = False

    map_uptodate = True

    search_full_OTL_mode = False

    cleared_data = True

    @classmethod
    def init_static(cls, project: Project, asynchronous=True) -> None:
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

        cls.clear_data()

        if not Helpers.all_OTL_asset_types_dict:
            Helpers.create_external_typeURI_options()

        if global_vars.current_project:
            if asynchronous:
                try:
                    create_task_reraise_exception(cls.load_project_relation_data_async())
                except DeprecationWarning:
                    # should only go here if you are testing
                    create_task_reraise_exception(cls.load_project_relation_data_async())
            else:
                try:
                    cls.load_project_relation_data()
                except DeprecationWarning:
                    # should only go here if you are testing
                    cls.load_project_relation_data()


    @classmethod
    def get_empty_visualisation_uptodate(cls):
        return {"remove":[],"add":[],"clear_all": False}


    @classmethod
    def clear_data(cls):
        cls.selected_object = None

        cls.shown_objects = []
        cls.internal_objects = []
        cls.external_objects = []
        cls.existing_relations = []
        cls.possible_relations_per_class_dict = {}
        cls.possible_object_to_object_relations_dict = {}
        cls.aim_id_relations = []
        cls.regenerate_relation_types = False
        global_vars.current_project.visualisation_uptodate.reset_relations_uptodate()
        # global_vars.current_project.visualisation_uptodate.set_clear_all(True)
        cls.map_uptodate = False
        cls.cleared_data = True

    @classmethod
    @add_loading_screen
    async def load_project_relation_data_async(cls) -> None:
        """
        Loads project relation data asynchronously.

        This method sets the GUI to a loading state while it retrieves and processes
        project relation data. It populates a dictionary with asset type URIs and
        updates the user interface accordingly once the data is loaded.

        :param cls: The class itself.
        :returns: None
        """
        timing_ref = f"load_project_data_async"
        OTLLogger.logger.debug(
            f"Execute RelationChangeDomain.load_project_relation_data_async() for project "
            f"{global_vars.current_project.eigen_referentie}",
            extra={"timing_ref": timing_ref})
        cls.get_screen().set_gui_lists_to_loading_state()


        # throw away old data before loading the new
        cls.clear_data()
        gc.collect()

        await cls.set_instances(objects_list=await cls.project.load_validated_assets_async())
        # global_vars.otl_wizard.main_window.step3_visuals.reload_html()
        timing_ref = f"load_project_data_async"
        OTLLogger.logger.debug(
            f"Execute RelationChangeDomain.load_project_relation_data_async() for project "
            f"{global_vars.current_project.eigen_referentie}",
            extra={"timing_ref": timing_ref})

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
        timing_ref = f"load_project_data"
        OTLLogger.logger.debug(
            f"Execute RelationChangeDomain.load_project_relation_data() for project "
            f"{global_vars.current_project.eigen_referentie}",
            extra={"timing_ref": timing_ref})
        cls.get_screen().set_gui_lists_to_loading_state()

        # throw away old data before loading the new
        cls.clear_data()
        gc.collect()

        await cls.set_instances(objects_list=cls.project.load_validated_assets())
        # global_vars.otl_wizard.main_window.step3_visuals.reload_html()
        timing_ref = f"load_project_data"
        OTLLogger.logger.debug(
            f"Execute RelationChangeDomain.load_project_relation_data() for project "
            f"{global_vars.current_project.eigen_referentie}",
            extra={"timing_ref": timing_ref})

    @classmethod
    async def set_instances(cls, objects_list: list[Union[RelatieObject, RelationInteractor]]) -> None:
        # sourcery skip: use-contextlib-suppress
        """Processes and categorizes AIM objects for relation management.

        This method takes a list of AIM objects and categorizes them into various
        groups based on their properties.
        It updates the class attributes to reflect the current state of these objects
        and ensures that the user interface is populated with the correct information.

        :param cls: The class itself.
        :param objects_list: A list of AIM objects to be processed and categorized.
        :type objects_list: list[Union[RelatieObject, RelationInteractor]]
        :returns: None
        """
        timing_ref = f"set_instances"
        OTLLogger.logger.debug(
            f"Execute RelationChangeDomain.set_instances() for project "
            f"{global_vars.current_project.eigen_referentie}",
            extra={"timing_ref": timing_ref})

        cls.existing_relations = []
        cls.aim_id_relations = []

        cls.internal_objects = []
        cls.external_objects = []
        cls.agent_objects = []
        cls.shown_objects = []

        for instance in objects_list:
            await asyncio.sleep(0)
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

        await cls.create_and_add_missing_external_assets_from_relations()

        cls.get_screen().fill_object_list(cls.shown_objects)
        cls.get_screen().fill_possible_relations_list(None, {})
        cls.get_screen().fill_existing_relations_list(cls.existing_relations)
        global_vars.otl_wizard.main_window.step3_visuals.update_only_legend()
        global_vars.otl_wizard.main_window.step3_visuals.update_slider_range()

        cls.cleared_data = False
        cls.map_uptodate = False
        timing_ref = f"set_instances"
        OTLLogger.logger.debug(
            f"Execute RelationChangeDomain.set_instances() for project "
            f"{global_vars.current_project.eigen_referentie}",
            extra={"timing_ref": timing_ref})

    @classmethod
    async def create_and_add_missing_external_assets_from_relations(cls) -> None:
        """
        Creates and adds missing external assets based on existing relations.

        This method iterates through all relations and checks for the existence of
        source and target objects. If either object is missing, it attempts to create
        and add a new external asset using the relation's identifiers and type URIs.

        :param cls: The class itself.
        :returns: None
        """
        timing_ref = f"create_missing_external_assets"
        OTLLogger.logger.debug(
            f"Execute RelationChangeDomain.create_and_add_missing_external_assets_from_relations() for project "
            f"{global_vars.current_project.eigen_referentie}",
            extra={"timing_ref": timing_ref})


        for relation_object in RelationChangeDomain.get_all_relations():
            await asyncio.sleep(0)
            source_id =  relation_object.bronAssetId.identificator
            target_id = relation_object.doelAssetId.identificator

            source_object = RelationChangeDomain.get_object(identificator=source_id)
            id_to_typeURI_dict: Optional[dict[str, str]] = None
            if not source_object:
                try:
                    bron_type_uri = Helpers.extract_corrected_relation_partner_typeURI(
                        relation_object.bron.typeURI,
                        relation_object.bronAssetId.identificator,
                        id_to_typeURI_dict,
                        RelationChangeDomain.get_shown_objects())

                    cls.create_and_add_new_external_asset(id_or_name=source_id,
                                                          type_uri=bron_type_uri)
                except ValueError as e:
                    # should there be a wrong typeURI
                    OTLLogger.logger.debug(e)

            target_object = RelationChangeDomain.get_object(identificator=target_id)
            if not target_object:
                try:
                    doel_type_uri = Helpers.extract_corrected_relation_partner_typeURI(
                        relation_object.doel.typeURI,
                        relation_object.doelAssetId.identificator,
                        id_to_typeURI_dict,
                        RelationChangeDomain.get_shown_objects())

                    cls.create_and_add_new_external_asset(id_or_name=target_id,
                                                          type_uri=doel_type_uri)
                except ValueError as e:
                    # should there be a wrong typeURI
                    OTLLogger.logger.debug(e)

        OTLLogger.logger.debug(
            f"Execute RelationChangeDomain.create_and_add_missing_external_assets_from_relations() for project "
            f"{global_vars.current_project.eigen_referentie}",
            extra={"timing_ref": timing_ref})

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
                OTLLogger.logger.debug(f"ERROR RelationChangeDomain.get_object function found multiple "
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

        return lambda otl_object: RelationChangeHelpers.get_corrected_identificator(
            otl_object) == id_to_check

    @classmethod
    async def set_possible_relations(cls, selected_object: RelationInteractor):
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



        cls.set_selected_object(selected_object)
        if not cls.selected_object:
            cls.get_screen().clear_possible_relation_elements()
            return

        # generate all relation types that the selected asset can have (within subset or full OTL)
        # only update this list when an external asset is added
        # OR when the user switches to the full OTL
        if (cls.regenerate_relation_types or not
                RelationChangeDomain.are_possible_relations_to_other_class_types_collected_for(
                selected_object.typeURI)):
            cls.collect_possible_relations_to_class_types_from(selected_object)
            cls.regenerate_relation_types = False

        # get all assets except the selected_object
        candidate_partner_assets: list[RelationInteractor] = list(
            filter(RelationChangeDomain.filter_out(object_to_filter_for=selected_object), 
                   cls.shown_objects))

        selected_id = RelationChangeHelpers.get_corrected_identificator(otl_object=selected_object)
        relation_types_list = cls.possible_relations_per_class_dict[selected_object.typeURI]

        # remove all previously generated relations for the selected_id
        cls.possible_object_to_object_relations_dict[selected_id] = {}
        # add all relations loaded that have isActief == False
        cls.add_inactive_relations_to_possible_relations(selected_id=selected_id)

        cls.add_all_possible_relations_between_selected_and_related_objects(
            relation_list=relation_types_list,selected_object=selected_object,
            related_objects=candidate_partner_assets)

        # sort generated relations
        cls.possible_object_to_object_relations_dict = (
            Helpers.sort_nested_dict(dictionary=cls.possible_object_to_object_relations_dict))

        possible_relations_for_this_object = cls.get_possible_relations_for(selected_id=selected_id)

        # noinspection PyTypeChecker
        object_attributes_dict = await DotnotationDictConverter.to_dict_async(otl_object=selected_object)

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
    def set_selected_object(cls,selected_object:RelationInteractor) -> None:
        cls.selected_object = selected_object

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
        log_typeURI = RelationChangeHelpers.get_abbreviated_typeURI(selected_object.typeURI)
        selected_object_id: str = RelationChangeHelpers.get_corrected_identificator(
            selected_object)

        related_objects_dict = defaultdict(list)
        legacy_hoortbij_relations_dict = {}
        for related_object in related_objects:
            related_objects_dict[related_object.typeURI].append(related_object)
            # if the related object is a legacy object create a new OSLO relation from legacy to otl_class
            if related_object.typeURI.startswith("https://lgc"):
                hoortbij_relation = RelationChangeDomain.create_hoortbij_OSLORelatie_with_legacy_class(
                    legacy_class_typeURI=related_object.typeURI,
                    OTL_class_typeURI= selected_object.typeURI)
                legacy_hoortbij_relations_dict[related_object.typeURI] = hoortbij_relation

        # add the hoortbij OSLORelations to legacy classes to the list of possible relations
        relation_list.extend(list(legacy_hoortbij_relations_dict.values()))

        OTLLogger.logger.debug(
            f"Execute RelationChangeDomain.add_all_possible_relations_between_selected_and_related_objects({log_typeURI}) for project {global_vars.current_project.eigen_referentie}",
            extra={"timing_ref": f"add_possible_relations_real_objects"})
        for relation in relation_list:
            if relation.bron_uri == selected_object.typeURI:
                for related_object in related_objects_dict[relation.doel_uri]:
                    if cls.get_same_relations_in_list(
                            relation_list=cls.existing_relations, relation_def=relation,
                            selected_object=selected_object, related_object=related_object):
                        continue
                    cls.add_relation_between(relation=relation,selected_object=selected_object,
                                             related_object=related_object)

            if relation.doel_uri == selected_object.typeURI:
                for related_object in related_objects_dict[relation.bron_uri]:
                    if cls.get_same_relations_in_list(
                            relation_list=cls.existing_relations, relation_def=relation,
                            selected_object=selected_object, related_object=related_object,
                            reverse=True):
                        continue
                    cls.add_relation_between(relation=relation,selected_object=selected_object,
                                             related_object=related_object, reverse=True)

        relation_count = 0
        if (cls.possible_object_to_object_relations_dict[selected_object_id]):
            for rel_obj in cls.possible_object_to_object_relations_dict[selected_object_id].keys():
                relation_count += len(cls.possible_object_to_object_relations_dict[selected_object_id][rel_obj])

        OTLLogger.logger.debug(
            f"Execute RelationChangeDomain.add_all_possible_relations_between_selected_and_related_objects({log_typeURI}) for project {global_vars.current_project.eigen_referentie} ({relation_count} relations)",
            extra={"timing_ref": f"add_possible_relations_real_objects"})

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
        selected_typeURI:str = selected_object.typeURI
        log_typeURI = RelationChangeHelpers.get_abbreviated_typeURI(selected_typeURI)
        OTLLogger.logger.debug(f"Execute RelationChangeDomain.collect_possible_relations_to_class_types_from({log_typeURI}) for project {global_vars.current_project.eigen_referentie}",
                               extra={"timing_ref": f"collect_possible_relations_classes"})

        if selected_typeURI.startswith("https://lgc"): # selected_object is legacy
            cls.possible_relations_per_class_dict[selected_typeURI] = (
                cls.get_hoortbij_relaties_from_legacy_asset(selected_typeURI))
        else:
            if (cls.external_objects or
                cls.agent_objects or
                cls.search_full_OTL_mode):
                # this is the long search, but it includes relations with external assets
                cls.possible_relations_per_class_dict[selected_typeURI] = (
                    RelationChangeDomain.get_all_concrete_relation_from_full_model(
                        selected_object=selected_object))
            else:
                try:
                    cls.possible_relations_per_class_dict[selected_typeURI] = \
                        cls.collector.find_all_concrete_relations(objectUri=selected_typeURI,
                                                              allow_duplicates=False)
                except ValueError as e:
                    OTLLogger.logger.debug(f"Didn't find relations in subset:\n {e}")
                    cls.possible_relations_per_class_dict[selected_typeURI] = (
                        RelationChangeDomain.get_all_concrete_relation_from_full_model(
                            selected_object=selected_object))

        relation_count = len(cls.possible_relations_per_class_dict[selected_object.typeURI])
        OTLLogger.logger.debug(
            f"Execute RelationChangeDomain.collect_possible_relations_to_class_types_from({log_typeURI}) for project {global_vars.current_project.eigen_referentie} ({relation_count} relations)",
            extra={"timing_ref": f"collect_possible_relations_classes"})

    @classmethod
    def get_hoortbij_relaties_from_legacy_asset(cls, selected_typeURI):
        all_concrete_classes = []
        all_classes_in_OTL = get_hardcoded_class_dict()
        for otl_class in all_classes_in_OTL.keys():
            if not otl_class.startswith("https://lgc"):
                concrete_classes = [non_legacy_class for non_legacy_class in
                                    get_concrete_subclasses_from_class_dict(otl_class) if
                                    not non_legacy_class.startswith("https://lgc")]
                all_concrete_classes.extend(concrete_classes)
        all_concrete_classes = list(set(all_concrete_classes))
        possible_relations = [
            RelationChangeDomain.create_hoortbij_OSLORelatie_with_legacy_class(selected_typeURI,
                                                                               concrete_class) for concrete_class in all_concrete_classes]
        return possible_relations

    @classmethod
    def create_hoortbij_OSLORelatie_with_legacy_class(cls, legacy_class_typeURI,
                                                      OTL_class_typeURI):
        return OSLORelatie(
            bron_overerving="",
            doel_overerving="",
            bron_uri=OTL_class_typeURI,
            doel_uri=legacy_class_typeURI,
            objectUri="https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#HoortBij",
            richting="Source -> Destination",
            deprecated_version="",
            usagenote="")

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
        related_id:str = RelationChangeHelpers.get_corrected_identificator(related)
        selected_id:str = RelationChangeHelpers.get_corrected_identificator(selected)

        if existing_relation.typeURI != relation_def.objectUri:
            return False
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

        selected_object_id:str = RelationChangeHelpers.get_corrected_identificator(selected_object)
        related_object_id:str = RelationChangeHelpers.get_corrected_identificator(related_object)

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
            return (RelationChangeHelpers.get_corrected_identificator(object_to_filter_for) !=
                    RelationChangeHelpers.get_corrected_identificator(related_object))

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
                source_id = RelationChangeHelpers.get_corrected_identificator(
                    otl_object=source_object)
                source_type = RelationChangeHelpers.get_abbreviated_typeURI(
                        typeURI=source_object.typeURI, add_namespace=True)

            target_id = None
            target_type = None
            if target_object:

                target_id = RelationChangeHelpers.get_corrected_identificator(
                    otl_object=target_object)
                target_type = RelationChangeHelpers.get_abbreviated_typeURI(
                        target_object.typeURI, True)

            OTLLogger.logger.debug(
                f"Couldn't make relation between source_type:{source_type} source_id:{source_id} {OSLO_relation.richting} target_type:{target_type} target_id:{target_id} for relation typeURI {OSLO_relation.objectUri}: \n {e}")
            return None

        return relation_object

    @classmethod
    @async_save_assets
    async def add_multiple_possible_relations_to_existing_relations(cls, data_list):
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
    def add_possible_relation_to_existing_relations(cls, bron_asset_id:str, target_asset_id:str,
                                                    relation_object_index:int) -> RelatieObject:
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
        global_vars.current_project.visualisation_uptodate.insert_relation(relation_object)
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
        OTLLogger.logger.debug("Execute RelationChangeDomain.update_frontend",
                               extra={"timing_ref": f"update_frontend"})
        cls.update_frontend_objects()
        cls.update_frontend_existing_relations()

        if cls.selected_object:
            create_task_reraise_exception(cls.set_possible_relations(selected_object=cls.selected_object))

        global_vars.otl_wizard.main_window.step3_visuals.update_only_legend()

        OTLLogger.logger.debug("Execute RelationChangeDomain.update_frontend",
                               extra={"timing_ref": f"update_frontend"})

    @classmethod
    def update_frontend_objects(cls):
        cls.get_screen().fill_object_list(objects=cls.shown_objects)

    @classmethod
    def update_frontend_existing_relations(cls):
        cls.get_screen().fill_existing_relations_list(relations_objects=cls.existing_relations,
                                                      last_added=cls.last_added_to_existing)

    @classmethod
    def update_frontend_possible_relations(cls):
        if cls.selected_object:
            selected_id = RelationChangeHelpers.get_corrected_identificator(otl_object=cls.selected_object)
            possible_relations_for_this_object = cls.get_possible_relations_for(
                selected_id=selected_id)

            cls.get_screen().fill_possible_relations_list(source_object=cls.selected_object,
                                                      relations=possible_relations_for_this_object,
                                                      last_added=cls.last_added_to_possible)

    @classmethod
    def set_selected_object_from_map(cls, identificator):
        cls.set_selected_object(cls.get_object(identificator))
        cls.get_screen().set_selected_object(identificator)

    @classmethod
    @async_save_assets
    async def remove_multiple_existing_relations(cls, indices: list[int]) -> None:
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
        global_vars.current_project.visualisation_uptodate.remove_relation(removed_relation)
        # if the removed relation already had an AIM ID it is set to false and kept if not it is
        # removed and made again in the possible relations
        removed_relation.isActief = False
        cls.get_screen().expand_possible_relations_folder_of(
            relation_typeURI=removed_relation.typeURI)

        return removed_relation

    @classmethod
    async def select_existing_relation_indices(cls, indices: list[int]) -> None:
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
            existing_relation_attribute_dict=await DotnotationDictConverter.to_dict_async(
                last_selected_relation))

    @classmethod
    async def select_possible_relation_data(cls, selected_relations_data: list) -> None:
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
            possible_relation_attribute_dict=await DotnotationDictConverter.to_dict_async(
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
    def get_visualisation_instances(cls)-> list[Union[RelatieObject, RelationInteractor]]:
        # cls.visualisation_uptodate = True
        return [asset for asset in RelationChangeDomain.get_quicksave_instances() if
         asset.isActief != False]

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
            if relation_instance.isActief != False:
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
                relation_instance.isActief == False]

    @classmethod
    def add_external_objects_to_shown_objects(cls):
        """
        Adds external objects to the list of shown objects.
        This method updates the internal state by extending the shown objects with external objects
        and marks that external objects have been added.

        :return: None
        """

        cls.shown_objects.extend(cls.external_objects)
        cls.regenerate_relation_types = True

    @classmethod
    def add_agent_objects_to_shown_objects(cls):
        """
        Adds agent objects to the list of shown objects. This method updates the internal state by
        extending the shown objects with agent objects and marks that external objects have been
        added.

        :return: None
        """
        cls.shown_objects.extend(cls.agent_objects)
        cls.regenerate_relation_types = True

    @classmethod
    @add_loading_screen
    @async_save_assets
    async def user_input_to_create_and_add_new_external_asset(cls, id_or_name: str, type_uri: str):
        cls.create_and_add_new_external_asset( id_or_name, type_uri)
        global_vars.current_project.visualisation_uptodate.set_clear_all(True)
        RelationChangeDomain.update_frontend()

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

        cls.regenerate_relation_types = True

        
    @classmethod
    def is_visualisation_uptodate(cls):
        return global_vars.current_project.visualisation_uptodate.is_uptodate()

    @classmethod
    def get_current_relation_change_screen_object_list_content_dict(cls):
        cls.map_uptodate = True
        return cls.get_screen().get_current_object_list_content_dict()

    @classmethod
    def get_map_screen(cls):
        return cls.get_screen().map_window
        # return global_vars.otl_wizard.main_window.step3_map

    @classmethod
    def get_shown_objects(cls):
        return cls.shown_objects

    @classmethod
    def set_search_full_OTL_mode(cls,state:bool) -> None:
        cls.search_full_OTL_mode = state
        cls.regenerate_relation_types = True

