
from typing import List, Optional

from PyQt6.QtWidgets import QVBoxLayout, QFrame, QHBoxLayout, QWidget, QSizePolicy
from otlmow_model.OtlmowModel.BaseClasses.RelationInteractor import RelationInteractor
from otlmow_model.OtlmowModel.Classes.ImplementatieElement.AIMObject import AIMObject
from otlmow_model.OtlmowModel.Classes.ImplementatieElement.RelatieObject import RelatieObject

from otlmow_gui.Domain.step_domain.RelationChangeDomain import RelationChangeDomain
from otlmow_gui.GUI.dialog_windows.DefineHeeftBetrokkeneRelationWindow import \
    DefineHeeftBetrokkeneRelationWindow
from otlmow_gui.GUI.screens.MapScreen import MapScreen
from otlmow_gui.GUI.screens.RelationChange_elements.ExistingRelationListWidget import \
    ExistingRelationListWidget
from otlmow_gui.GUI.screens.RelationChange_elements.ObjectListWidget import ObjectListWidget
from otlmow_gui.GUI.screens.RelationChange_elements.PossibleRelationListWidget import \
    PossibleRelationListWidget
from otlmow_gui.GUI.screens.RelationChange_elements.RelationChangeHelpers import RelationChangeHelpers
from otlmow_gui.GUI.screens.general_elements.ButtonWidget import ButtonWidget
from otlmow_gui.GUI.screens.screen_interface.RelationChangeScreenInterface import \
    RelationChangeScreenInterface
import qtawesome as qta

class RelationChangeScreen(RelationChangeScreenInterface):
    """
    Represents the screen for managing relation changes in the application.

    This class provides the user interface for displaying and modifying relations
    between objects, including options for selecting, expanding, and defining relations.
    It integrates various UI components to facilitate user interactions and data management.

    Args:
        language_settings (optional): Language settings for the user interface.

    Attributes:
        selected_object_col1 (optional): The currently selected object in the first column.
        container_insert_data_screen (QVBoxLayout): Layout for organizing UI components vertically.
        window (optional): Reference to the main window for the screen.
        window_layout (optional): Layout for the window.
        input_field (optional): Input field for user data entry.
        input_file_button (optional): Button for selecting input files.
        frame_layout (optional): Layout for organizing frame components.
        objects_list_gui (ObjectListWidget): GUI component for displaying object lists.
        possible_relation_list_gui (PossibleRelationListWidget): GUI component for displaying possible relations.
        existing_relation_list_gui (ExistingRelationListWidget): GUI component for displaying existing relations.
    """


    def __init__(self, language_settings=None):
        super().__init__()
        self._ = language_settings

        self.selected_object_col1 = None

        #gui elements
        self.container_insert_data_screen = QVBoxLayout()
        self.window = None
        self.window_layout = None

        self.input_field = None
        self.input_file_button = None

        self.frame_layout = None

        self.objects_list_gui = ObjectListWidget(self._,self)
        self.possible_relation_list_gui = PossibleRelationListWidget(self._,self)
        self.existing_relation_list_gui = ExistingRelationListWidget(self._,self)

        self.possible_relation_frame:QFrame = None
        self.existing_relation_frame:QFrame = None

        self.map_window:MapScreen = None

        self.init_ui()




    def set_gui_lists_to_loading_state(self) -> None:
        """
        Sets the GUI lists to a loading state.

        This method clears the current contents of the objects and relations lists
        in the user interface and adds a loading placeholder to indicate that data
        is being processed. It provides visual feedback to the user while the
        application retrieves or updates data.

        :param self: The instance of the class.
        :returns: None
        """

        self.objects_list_gui.clear()
        self.possible_relation_list_gui.clear()
        self.existing_relation_list_gui.clear()

        self.objects_list_gui.add_loading_placeholder()
        self.possible_relation_list_gui.add_loading_placeholder()
        self.existing_relation_list_gui.add_loading_placeholder()


    def paintEvent(self, a0):
        self.synchronize_subtext_label_heights()
        super().paintEvent(a0)


    def synchronize_subtext_label_heights(self) -> None:
        """
        Synchronizes the heights of subtext labels across different GUI lists.

        This method adjusts the minimum height of the subtext labels in the objects
        list and existing relations list to match the height of the subtext label in
        the possible relations list. This ensures a consistent appearance in the user
        interface.

        :param self: The instance of the class.
        :returns: None
        """

        possible_subtext_frame = self.possible_relation_list_gui.get_adjustable_subtext_frame()
        object_subtext_frame = self.objects_list_gui.get_adjustable_subtext_frame()
        exist_subtext_frame = self.existing_relation_list_gui.get_adjustable_subtext_frame()

        frame_rect_height = possible_subtext_frame.frameRect().height()
        frame_rect_object = object_subtext_frame.frameRect()
        frame_rect_exist = exist_subtext_frame.frameRect()

        if self.existing_relation_frame.isVisible():
            if frame_rect_height != frame_rect_object.height():
                object_subtext_frame.setMinimumHeight(frame_rect_height)
            if frame_rect_height != frame_rect_exist.height():
                exist_subtext_frame.setMinimumHeight(frame_rect_height)
        else:
            object_subtext_frame.setMinimumHeight(15)

    def init_ui(self) -> None:
        """
        Initializes the user interface for the relation change screen.

        This method sets up the main layout by adding the menu to the container
        and configuring the layout margins. It ensures that the user interface
        is properly structured for user interaction.

        :param self: The instance of the class.
        :returns: None
        """

        self.container_insert_data_screen.addWidget(self.create_menu())
        self.container_insert_data_screen.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.container_insert_data_screen)


    def create_menu(self) -> QWidget:
        """
        Creates and configures the menu for the relation change screen.

        This method initializes a QWidget that serves as the menu container,
        setting its layout and adding the necessary components. It ensures that
        the menu is properly structured and styled for the user interface.

        :param self: The instance of the class.
        :returns: The configured menu widget.
        :rtype: QWidget
        """

        self.window = QWidget()
        self.window.setProperty('class', 'background-box')

        self.window_layout = QVBoxLayout()
        self.window_layout.setContentsMargins(0,0,0,0)
        self.window_layout.addWidget(self.horizontal_layout())

        self.window.setLayout(self.window_layout)

        return self.window


    def fill_object_list(self, objects: List[RelationInteractor]) -> None:
        """
        Fills the object list GUI with the provided AIM objects.

        This method updates the objects list in the user interface by passing the
        specified list of AIM objects to the GUI component responsible for displaying
        the objects. It ensures that the list is populated with the current data for
        user interaction.

        :param self: The instance of the class.
        :param objects: A list of AIM objects to be displayed in the object list.
        :type objects: List[AIMObject]
        :returns: None
        """

        self.objects_list_gui.fill_list(source_object=None, objects=objects, last_added=[])


    def fill_existing_relations_list(self, relations_objects: List[RelatieObject],
                                     last_added: list[RelatieObject] = None) -> None:
        """
        Fills the existing relations list GUI with the provided relation objects.

        This method updates the existing relations list in the user interface by
        populating it with the specified relation objects and any last added relations.
        It ensures that the list reflects the current state of relations for user interaction.

        :param self: The instance of the class.
        :param relations_objects: A list of relation objects to be displayed in the existing relations list.
        :type relations_objects: List[RelatieObject]
        :param last_added: An optional list of last added relation objects to highlight in the list.
        :type last_added: list[RelatieObject], optional
        :returns: None
        """

        if last_added is None:
            last_added = []
        self.existing_relation_list_gui.fill_list(source_object=None,
                                                  objects=relations_objects,
                                                  last_added=last_added)


    def fill_possible_relations_list(self, source_object: Optional[RelationInteractor],
                                     relations: dict[str, list[RelatieObject]],
                                     last_added=None) -> None:
        """
        Fills the possible relations list GUI with relations for a given source object.

        This method updates the possible relations list in the user interface by
        populating it with relations associated with the specified source object.
        It also highlights any previously added relations to provide context for the user.

        :param self: The instance of the class.
        :param source_object: The source object for which possible relations are being displayed.
        :type source_object: AIMObject
        :param relations: A dictionary mapping relation types to lists of relation objects.
        :type relations: dict[str, list[RelatieObject]]
        :param last_added: An optional list of last added relation objects to highlight in the list.
        :type last_added: list[RelatieObject], optional
        :returns: None
        """

        if last_added is None:
            last_added = []
        self.possible_relation_list_gui.fill_list(source_object=source_object,
                                                  objects=relations,
                                                  last_added=last_added)


    def horizontal_layout(self) -> QFrame:
        """
        Creates a horizontal layout for displaying object and relation lists.

        This method constructs a QFrame containing a horizontal layout that includes
        three object list GUI components: the objects list, possible relations list,
        and existing relations list. It sets the layout's spacing and stretch factors
        to ensure a balanced and responsive design.

        :param self: The instance of the class.
        :returns: The configured frame containing the horizontal layout.
        :rtype: QFrame
        """

        frame = QFrame()
        self.frame_layout = QHBoxLayout()
        self.frame_layout.setSpacing(0)

        self.frame_layout.addWidget(self.objects_list_gui.create_object_list_gui())

        self.possible_relation_frame =self.possible_relation_list_gui.create_object_list_gui(multi_select=True)
        self.frame_layout.addWidget(self.possible_relation_frame)

        self.existing_relation_frame = self.existing_relation_list_gui.create_object_list_gui(multi_select=True)
        self.frame_layout.addWidget( self.existing_relation_frame)

        map_button = ButtonWidget()
        map_button.setIcon(qta.icon("mdi.map",color='white',options=[{
                'scale_factor': 1.5
            }]))
        map_button.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Expanding)
        map_button.setProperty('class', 'map-button')
        map_button.clicked.connect(lambda: self.toggle_map_window())
        map_button.setToolTip(self._("Toon kaart met OTL-assets uit de eerste kolom"))
        # map_button.setContentsMargins(22,0,0,0)

        self.frame_layout.addWidget(map_button)
        # self.step3_map: MapScreen = MapScreen(self._)

        self.frame_layout.setStretch(0, 5)
        self.frame_layout.setStretch(1, 5)
        self.frame_layout.setStretch(2, 5)
        # self.frame_layout.setStretch(3, 1)

        # self.possible_relation_frame.setHidden(True)
        # self.existing_relation_frame.setHidden(True)

        frame.setLayout(self.frame_layout)
        return frame


    def reset_ui(self, _):
        super().reset_ui(_)
        self._ = _

    def fill_object_attribute_field(self, object_attribute_dict: dict) -> None:
        """
        Fills the object attribute field with the provided attributes.

        This method updates the object attribute field in the user interface by
        passing a dictionary of object attributes to the corresponding GUI component.
        It ensures that the displayed attributes are current and reflect the selected object.

        :param self: The instance of the class.
        :param object_attribute_dict: A dictionary containing object attributes to be displayed.
        :type object_attribute_dict: dict
        :returns: None
        """

        self.objects_list_gui.fill_object_attribute_field(
            object_attribute_dict=object_attribute_dict)

    def fill_possible_relation_attribute_field(self,
                                               possible_relation_attribute_dict: dict) -> None:
        """
        Fills the possible relation attribute field with the provided attributes.

        This method updates the possible relation attribute field in the user interface
        by passing a dictionary of possible relation attributes to the corresponding GUI
        component. It ensures that the displayed attributes accurately reflect the selected
        possible relation.

        :param self: The instance of the class.
        :param possible_relation_attribute_dict: A dictionary containing possible relation attributes to be displayed.
        :type possible_relation_attribute_dict: dict
        :returns: None
        """

        self.possible_relation_list_gui.fill_object_attribute_field(
            object_attribute_dict=possible_relation_attribute_dict)

    def fill_existing_relation_attribute_field(self,
                                               existing_relation_attribute_dict: dict) -> None:
        """
        Fills the existing relation attribute field with the provided attributes.

        This method updates the existing relation attribute field in the user interface
        by passing a dictionary of existing relation attributes to the corresponding GUI
        component. It ensures that the displayed attributes accurately reflect the selected
        existing relation.

        :param self: The instance of the class.
        :param existing_relation_attribute_dict: A dictionary containing existing relation attributes to be displayed.
        :type existing_relation_attribute_dict: dict
        :returns: None
        """

        self.existing_relation_list_gui.fill_object_attribute_field(
            object_attribute_dict=existing_relation_attribute_dict)

    def expand_existing_relations_folder_of(self, relation_typeURI: str) -> None:
        """Expands the folder of existing relations for a specified relation type.

        This method determines if the given relation type URI is unique across namespaces
        and retrieves its abbreviated form. It then expands the corresponding folder
        in the existing relations list GUI to display related items.

        :param self: The instance of the class.
        :param relation_typeURI: The type URI of the relation whose folder is to be expanded.
        :type relation_typeURI: str
        :returns: None
        """

        add_namespace = RelationChangeHelpers.is_unique_across_namespaces(
            typeURI=relation_typeURI,
            objects=RelationChangeDomain.shown_objects)
        abbr_relation_typeURI = RelationChangeHelpers.get_abbreviated_typeURI(
            typeURI=relation_typeURI,
            add_namespace=add_namespace,
            is_relation=True)
        self.existing_relation_list_gui.expand_folder_of(typeURI=abbr_relation_typeURI)

    def expand_possible_relations_folder_of(self, relation_typeURI: str) -> None:
        """Expands the folder of possible relations for a specified relation type.

        This method checks if the given relation type URI is unique across namespaces
        and retrieves its abbreviated form. It then expands the corresponding folder
        in the possible relations list GUI to display related items.

        :param self: The instance of the class.
        :param relation_typeURI: The type URI of the relation whose folder is to be expanded.
        :type relation_typeURI: str
        :returns: None
        """

        add_namespace = RelationChangeHelpers.is_unique_across_namespaces(
            typeURI=relation_typeURI,
            objects=RelationChangeDomain.shown_objects)
        abbr_relation_typeURI = RelationChangeHelpers.get_abbreviated_typeURI(
            typeURI=relation_typeURI,
            add_namespace=add_namespace,
            is_relation=True)
        self.possible_relation_list_gui.expand_folder_of(abbr_relation_typeURI)

    def showMultiSelectionHeeftBetrokkeneAttributeDialogWindow(self,
                                                               data_list_and_relation_objects: list) -> None:
        """Displays a dialog window for defining the 'HeeftBetrokkene' relation.

        This method initializes and opens a dialog window that allows the user to
        define the 'HeeftBetrokkene' relation based on the provided data list and
        relation objects. It ensures that the user can interactively set the necessary
        attributes for the relation.

        :param self: The instance of the class.
        :param data_list_and_relation_objects: A list containing data and relation objects
                                                relevant to the 'Heeft Betrokkene' relation.
        :type data_list_and_relation_objects: list
        :returns: None
        """

        dialogWindow = DefineHeeftBetrokkeneRelationWindow(
            language_settings=self._,
            data_list_and_relation_objects=data_list_and_relation_objects)
        dialogWindow.draw_define_heeft_betrokkene_rol_window()

    def clear_possible_relation_elements(self) -> None:
        """
        Clears all possible relation elements from the user interface.
        This method resets the displayed lists and fields related to possible relations,
        ensuring that no outdated or irrelevant information is shown.

        :return: None
        """

        self.fill_possible_relations_list(None, {})
        self.fill_object_attribute_field({})
        self.fill_possible_relation_attribute_field({})

    def update_color_scheme(self):
        self.objects_list_gui.update_color_scheme()
        self.possible_relation_list_gui.update_color_scheme()
        self.existing_relation_list_gui.update_color_scheme()

    def set_object_search_bar_text(self, search_text: str) -> None:
        """
        Sets the text of the object search bar in the GUI.

        This method updates the search bar with the provided search text, allowing users to filter the displayed objects based on their input.

        :param search_text: The text to set in the object search bar.
        :type search_text: str

        :return: None
        """
        self.objects_list_gui.set_search_text(search_text)

    def set_possible_relation_search_bar_text(self, search_text: str) -> None:
        """
        Sets the text of the possible relation search bar in the GUI.

        This method updates the search bar with the provided search text, enabling users to filter the displayed possible relations based on their input.

        :param search_text: The text to set in the possible relation search bar.
        :type search_text: str

        :return: None
        """
        self.possible_relation_list_gui.set_search_text(search_text)

    def set_existing_relation_search_bar_text(self, search_text: str) -> None:
        """
        Sets the text of the existing relation search bar in the GUI.

        This method updates the search bar with the provided search text, allowing users to filter the displayed existing relations based on their input.

        :param search_text: The text to set in the existing relation search bar.
        :type search_text: str

        :return: None
        """
        self.existing_relation_list_gui.set_search_text(search_text)

    def get_current_object_list_content_dict(self) -> dict[str,list]:
        return self.objects_list_gui.get_current_list_content_dict()

    def set_selected_object(self, identificator:str):
        self.objects_list_gui.select_item_via_identificator(identificator)

    def toggle_map_window(self):
        if self.map_window:
            self.map_window.close()
        else:
            self.map_window = MapScreen(self._,parent_screen=self)
            self.map_window.show()
            self.map_window.start_async_reload()

    def is_show_all_OTL_relations_checked(self) -> bool:
        return self.possible_relation_list_gui.is_show_all_OTL_relations_checked()