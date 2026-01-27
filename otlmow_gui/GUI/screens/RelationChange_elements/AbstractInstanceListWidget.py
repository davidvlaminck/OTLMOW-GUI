import abc
from typing import Optional, Collection

from PyQt6.QtCore import Qt, QModelIndex, QItemSelectionModel
from PyQt6.QtGui import QColor, QStandardItem, QPixmap, QIcon, QPainter, QBrush, QFont
from PyQt6.QtWidgets import QTreeWidget, QFrame, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, \
    QHeaderView, QTreeWidgetItem, QHBoxLayout, QLineEdit, QPushButton, QTreeView, \
    QStyledItemDelegate

import qtawesome as qta
from otlmow_model.OtlmowModel.Classes.ImplementatieElement.AIMObject import AIMObject
from otlmow_visuals.PyVisWrapper import PyVisWrapper

from otlmow_gui.Domain.ProgramFileStructure import ProgramFileStructure
from otlmow_gui.Domain.logger.OTLLogger import OTLLogger
from otlmow_gui.Domain.step_domain.RelationChangeDomain import RelationChangeDomain
from otlmow_gui.GUI.Styling import Styling
from otlmow_gui.GUI.screens.general_elements.ButtonWidget import ButtonWidget
from otlmow_gui.GUI.screens.RelationChange_elements.FolderTreeView import FolderTreeView

IMG_DIR = ProgramFileStructure.get_dynamic_library_path('img')
MULTI_SELECTION = QListWidget.SelectionMode.MultiSelection


class AbstractInstanceListWidget:

    def __init__(self, language_settings,parent,labels,list_gui_style_class=None,needs_source_object= False):
        self._ = language_settings
        self.parent = parent
        self.search_text = ""

        self.search_bar = None
        self.clear_search_bar_button = None

        self.list_gui: Optional[FolderTreeView] = None
        self.list_button = ButtonWidget()

        self.list_label = None
        self.list_subtext_frame = None
        self.list_subtext_layout = None
        self.list_subtext_label = None
        self.attribute_field: QTreeWidget = QTreeWidget()
        self.attribute_field.setSelectionMode(QTreeWidget.SelectionMode.NoSelection)
        self.frame_layout = None

        # self.type_to_items_dict = {}
        self.type_open_status = {}
        self.selected_object = None
        self.selected_item = None
        self.list_gui_style_class = list_gui_style_class

        self.item_type_data_index = 3
        self.data_1_index = 4
        self.data_last_added_index = 5
        self.data_item_count_index = 8

        # self.data_1_index = 4
        # self.data_2_index = 5
        # self.data_3_index = 8
        # self.data_last_added_index = 9

        self.color_legend = PyVisWrapper().relatie_color_dict
        self.needs_source_object= needs_source_object

        self.labels = labels
        self.first_paint = False
        self.second_paint = False
        self.multi_col_list = True

        self.id_to_object_with_text_and_data_dict: dict = {}


    class LastAddedHighlightDelegate(QStyledItemDelegate):

        def __init__(self, list_widget):

            super().__init__()
            self.parent : AbstractInstanceListWidget = list_widget
            self.second_paint = False
            self.first_paint = False

        def paint(self, painter: QPainter, option, index: QModelIndex):
            painter.save()

            if(self.first_paint and not self.second_paint):
                self.parent.list_gui.resize_columns(self.parent.multi_col_list)
                self.second_paint = True
            else:
                self.first_paint = True

            # Apply custom background for specific rows or items
            if  self.parent.list_gui.model.itemFromIndex(index.siblingAtColumn(0)).data(self.parent.data_last_added_index) :
                painter.fillRect(option.rect, QBrush(Styling.last_added_color))

            painter.restore()
            super().paint(painter, option, index)

    def create_object_list_gui(self, multi_select: bool = False) -> QFrame:
        frame = QFrame()
        self.frame_layout = QVBoxLayout()
        self.list_label = QLabel()
        self.list_label.setText(self.list_label_text)

        list_label_font = QFont()
        list_label_font.setPointSize(11)
        list_label_font.setBold(True)
        self.list_label.setFont(list_label_font)
        # self.list_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.list_subtext_frame = self.create_list_subtext_frame()

        self.list_gui = FolderTreeView()
        self.list_gui.setProperty('class', 'list')
        self.list_gui.selectionModel().selectionChanged.connect(self.on_item_selectionChange_listener)
        self.list_gui.expanded.connect(self.record_expanse_listener)
        self.list_gui.collapsed.connect(self.record_collapse_listener)
        self.list_gui.clicked.connect(self.clicked_item_listener)
        self.list_gui.setExpandsOnDoubleClick(False)
        self.list_gui.setItemDelegate(self.LastAddedHighlightDelegate(self))
        if multi_select:
            self.list_gui.setSelectionMode(QTreeView.SelectionMode.MultiSelection)
        if self.list_gui_style_class:
            self.list_gui.setObjectName(self.list_gui_style_class)




        self.frame_layout.addWidget(self.list_label)
        self.frame_layout.addWidget(self.list_subtext_frame)

        self.frame_layout.addWidget(self.create_search_bar())
        self.frame_layout.addWidget(self.list_gui,10)

        object_attribute_label = QLabel()
        object_attribute_label.setText(self.attribute_field_label_text)
        self.frame_layout.addWidget(self.create_button())
        self.frame_layout.addWidget(object_attribute_label)

        self.frame_layout.addWidget(self.create_attribute_field(),5)

        # self.frame_layout.setSpacing(1)
        frame.setLayout(self.frame_layout)

        return frame

    def create_list_subtext_frame(self) -> QFrame:
        list_subtext_frame = QFrame()
        self.list_subtext_layout = QVBoxLayout()
        self.list_subtext_layout.setContentsMargins(0, 0, 0, 0)

        list_subtext_label_font = QFont()
        list_subtext_label_font.setItalic(True)

        self.list_subtext_label = QLabel()
        self.list_subtext_label.setText(self.list_subtext_label_text)
        self.list_subtext_label.setFont(list_subtext_label_font)
        self.list_subtext_label.setWordWrap(True)
        self.list_subtext_label.setAlignment(Qt.AlignmentFlag.AlignTop )

        self.list_subtext_layout.addWidget(self.list_subtext_label)
        self.add_extra_elements_to_list_subtext_layout()

        list_subtext_frame.setLayout(self.list_subtext_layout)

        return list_subtext_frame

    def clicked_item_listener(self, table_coord: QModelIndex) -> None:
        """
        Intended to connect to self.list_gui.clicked signal which is triggered when an item in the
        list is clicked

        Responds to item click events in the list widget by checking if the clicked item is a
        folder. If the item is a folder, it toggles the expand state of that item in the GUI.

        :param table_coord: The index of the clicked item in the table.
        :type table_coord: QModelIndex

        :return: None
        """

        table_coord = table_coord.siblingAtColumn(0)
        if self.is_item_a_type_folder_at_row(table_coord):
           self.list_gui.toggle_expand_state_of_item_at_row(table_coord)
        else:
          self.asset_clicked_listener()

    def is_item_a_type_folder_at_row(self, model_index):
        folder_item = self.list_gui.model.itemFromIndex(model_index)
        if folder_item.hasChildren():
            return folder_item
        else:
            return None

    def fill_list(self, source_object: Optional[AIMObject], objects: Collection, last_added) -> None:
        list_label_text = "None"
        if self.list_label:
            list_label_text = self.list_label.text()

        timing_ref = f"fill_list_{list_label_text}"
        object_list_length = len(objects)
        OTLLogger.logger.debug(
            f"Execute AbstractInstanceListWidget.fill_list() ({object_list_length} objects) in list: {list_label_text} ",
            extra={"timing_ref": timing_ref})

        # sourcery skip: remove-dict-keys
        # objects = RelationChangeDomain.objects
        self.list_gui.setSortingEnabled(False)
        self.list_gui.clear()

        item_list = []
        type_to_instance_dict = {}
        self.list_gui.itemDelegate().first_paint = False
        self.list_gui.itemDelegate().second_paint = False

        text_and_data_per_element = self.extract_text_and_data_per_item(source_object, objects,
                                                                        last_added)

        if self.needs_source_object and not source_object:
            self.add_no_asset_selected_placeholder()
        elif not objects:
            self.add_no_options_placeholder()


        for text_and_data in text_and_data_per_element:

            abbr_typeURI = text_and_data['text'].typeURI

            if abbr_typeURI in type_to_instance_dict.keys():
                type_to_instance_dict[abbr_typeURI].append(text_and_data)
            else:
                type_to_instance_dict[abbr_typeURI] = [text_and_data]

        folder_items_expanded = []
        previously_selected_item = None
        self.multi_col_list = False
        for asset_type, text_and_data_list in type_to_instance_dict.items():

            add_folder_based_on_search_text = False
            folder_item = self.create_asset_type_standard_item(asset_type,text_and_data_list)
            folder_item_font = QFont()
            folder_item_font.setBold(True)
            folder_item_font.setPointSize(10)
            folder_item.setFont(folder_item_font)

            # self.type_to_items_dict[asset_type] = []

            if asset_type not in self.type_open_status:
                self.type_open_status[asset_type] = False
            elif self.type_open_status[asset_type]:
                folder_items_expanded.append(folder_item)

            for text_and_data in text_and_data_list:

                instance_item_tuple: tuple[QStandardItem] = self.create_instance_standard_item(text_and_data)
                search_match = False

                # search on all columns
                for instance_item in instance_item_tuple:
                    if (    self.search_text in instance_item.text().lower() or
                            self.search_text in folder_item.text().lower()):
                        search_match = True

                        instance_item.setEditable(False)  # Make the item name non-editable
                        if self.is_last_added(text_and_data):
                            instance_item.setBackground(QBrush(QColor("#ecf0f1")))


                if search_match:
                    if self.is_previously_selected_requirement(text_and_data):
                        previously_selected_item = instance_item_tuple[0]

                    if len(instance_item_tuple) > 1:
                        instance_item_tuple[1].setData(instance_item_tuple[0].data(self.data_1_index), self.data_1_index)
                        instance_item_tuple[1].setData(instance_item_tuple[0].data(self.item_type_data_index), self.item_type_data_index)
                        instance_item_tuple[1].setEditable(False)
                        self.multi_col_list = True

                    folder_item.appendRow(instance_item_tuple)
                    add_folder_based_on_search_text = True

                    if self.search_text:
                        #if you are searching then open all the folders that have the results
                        folder_items_expanded.append(folder_item)

            if add_folder_based_on_search_text:
                item_list.append(folder_item)


        for folder_item in item_list:
            folder_item.sortChildren(0,Qt.SortOrder.AscendingOrder)
            if self.multi_col_list:
                padding_item = QStandardItem("")
                padding_item.setData(folder_item.data(self.data_1_index), self.data_1_index)
                padding_item.setData(folder_item.data(self.item_type_data_index), self.item_type_data_index)
                padding_item.setEditable(False)  # Make the folder name non-editable
                padding_item.setSelectable(False)  # Optional: make the folder itself non-selectable

                self.list_gui.addItem((folder_item, padding_item))
            else:
                self.list_gui.addItem(folder_item)

        self.list_gui.setSortingEnabled(True)
        self.list_gui.sortByColumn(0, Qt.SortOrder.AscendingOrder)

        self.list_gui.expandAll()
        self.list_gui.resizeColumnToContents(0)  # Resizes the first column based on its content
        if self.multi_col_list:
            self.list_gui.resizeColumnToContents(1)

        self.list_gui.collapseAll()

        # expand previously expanded items
        for folder_item in folder_items_expanded:
            folder_item_index = self.list_gui.model.indexFromItem(folder_item)
            self.list_gui.expand(folder_item_index)

        # select previously selected item
        self.select_object_id(previously_selected_item=previously_selected_item)
        if not previously_selected_item:
            self.set_list_button_enabled( False)
            self.selected_object = None
            self.selected_item = None


        if self.needs_source_object and not source_object:
            self.list_gui.model.setHeaderData(0, Qt.Orientation.Horizontal,"")
        elif not objects:
            self.list_gui.model.setHeaderData(0, Qt.Orientation.Horizontal,"")
        else:
            for i in range(len(self.labels)):
                self.list_gui.model.setHeaderData(i, Qt.Orientation.Horizontal, self.labels[i])

        OTLLogger.logger.debug(
            f"Execute AbstractInstanceListWidget.fill_list() ({object_list_length} objects) in list: {list_label_text} ",
            extra={"timing_ref": timing_ref})

    @abc.abstractmethod
    def create_instance_standard_item(self, text_and_data):
        raise NotImplementedError

    @abc.abstractmethod
    def create_button(self):
        raise NotImplementedError

    @abc.abstractmethod
    def extract_text_and_data_per_item(self, source_object, objects, last_added):
        raise NotImplementedError

    @abc.abstractmethod
    def on_item_selectionChange_listener(self, selected: QItemSelectionModel, deselected:QItemSelectionModel):
        raise NotImplementedError

    @abc.abstractmethod
    def is_last_added(self, text_and_data: dict):
        raise NotImplementedError

    def create_attribute_field(self) -> None:

        self.attribute_field.setColumnCount(2)
        self.attribute_field.setProperty('class', 'attribute_field')
        self.attribute_field.setHeaderHidden(True)

        header = self.attribute_field.header()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(False)

        self.add_attribute_field_placeholder(self.attribute_field,
                                             self.get_no_instance_selected_message())

        return self.attribute_field

    def fill_object_attribute_field(self, object_attribute_dict:dict) -> None:

        self.attribute_field.clear()

        if not object_attribute_dict:
           self.add_attribute_field_placeholder(self.attribute_field,
                                                self.get_no_instance_selected_message())

        for attribute, value in object_attribute_dict.items():
            list_item = QTreeWidgetItem()
            list_item.setText(0, attribute)
            list_item.setText(1, str(value))
            self.attribute_field.addTopLevelItem(list_item)

    def create_search_bar(self) -> QFrame:
        frame = QFrame()
        frame_layout = QHBoxLayout()
        frame_layout.setContentsMargins(5, 5, 0, 5)
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText(self._("search_button"))
        self.search_bar.textChanged.connect(self.search_listener)

        self.clear_search_bar_button = QPushButton()
        self.set_clear_icon(self.clear_search_bar_button)
        self.clear_search_bar_button.clicked.connect(self.clear_search_listener)
        self.clear_search_bar_button.setProperty('class', 'secondary-button')

        frame_layout.addWidget(self.search_bar)
        frame_layout.addWidget(self.clear_search_bar_button)
        frame.setLayout(frame_layout)
        return frame

    def search_listener(self,text:str) -> None:
        self.search_text = text.lower()
        if not self.search_text:
            self.set_all_folder_items_collapsed()

        self.update_this_gui_list_content()


        # RelationChangeDomain.update_frontend()

    def clear_search_listener(self) -> None:
        self.search_bar.setText("")
        RelationChangeDomain.update_frontend()

    def set_search_text(self, text) -> None:
        self.search_bar.setText(text)

    def filter_on_search_text(self, items:list[QListWidgetItem]) -> list[QListWidgetItem]:

        return   [item for item in items
                  if self.search_text in item.text().lower()]

    def get_no_instance_selected_message(self):
        return self._("no_instance_selected")


    def create_asset_type_standard_item(self, asset_type:str, text_and_data_list) -> QStandardItem:
        item_count = len(text_and_data_list)
        selected_item_count = 0

        item = QStandardItem()
        self.set_type_folder_text(type_folder_item= item,
                                  otl_type= asset_type,
                                  item_count=item_count,
                                  selected_item_count=selected_item_count)
        item.setEditable(False)  # Make the folder name non-editable
        item.setSelectable(False)  # Optional: make the folder itself non-selectable

        item.setData(asset_type,self.data_1_index)
        item.setData("type", self.item_type_data_index)
        item.setData(False, self.data_last_added_index)

        # there are only so many data indexes you can use so we have to bundle information
        item.setData([selected_item_count,item_count],self.data_item_count_index)

        return item

    def set_type_folder_text(self, type_folder_item, otl_type, item_count, selected_item_count = 0):
        if not selected_item_count:
            type_folder_item.setText(f"{otl_type} ({item_count})")
        else:
            type_folder_item.setText(f"{otl_type} ({selected_item_count}/{item_count})")

    def update_selected_count_data(self, type_folder_item, selected_item_count):
        item_count = type_folder_item.data(self.data_item_count_index)[1]
        type_folder_item.setData([selected_item_count, item_count], self.data_item_count_index)
        return item_count

    def reset_selected_item_count(self, type_folder_item):
        selected_item_count = 0
        item_count = self.update_selected_count_data(type_folder_item, selected_item_count)
        asset_type = type_folder_item.data(self.data_1_index)
        self.set_type_folder_text(type_folder_item=type_folder_item,
                                  otl_type=asset_type,
                                  item_count=item_count,
                                  selected_item_count=selected_item_count)

    def select_object_id(self, previously_selected_item: QStandardItem):
        pass

    def is_previously_selected_requirement(self, text_and_data):
        return False

    def record_expanse_listener(self, index):
        folder_item: QStandardItem = self.is_item_a_type_folder_at_row(index)
        if folder_item:
            asset_type = folder_item.data(self.data_1_index)
            self.type_open_status[asset_type] = True

    def record_collapse_listener(self, index):

        folder_item: QStandardItem = self.is_item_a_type_folder_at_row(index)
        if folder_item:
            asset_type = folder_item.data(self.data_1_index)
            self.type_open_status[asset_type] = False


    def expand_folder_of(self,typeURI: str):
        self.type_open_status[typeURI] = True

    def set_list_button_enabled(self, item_selected:bool):
        pass

    def set_all_folder_items_collapsed(self):
        self.type_open_status.clear()

    def add_direction_icon_to_item(self, instance_item: QStandardItem, direction: str, typeURI: str):
        direction_icon_path = f'{str(IMG_DIR)}/bidirect.png'
        if direction == "-->":
            direction_icon_path = f'{str(IMG_DIR)}/right.png'
        elif direction == "<--":
            direction_icon_path = f'{str(IMG_DIR)}/left.png'

        pixmap = QPixmap(direction_icon_path)
        self.apply_relation_color(pixmap, typeURI)

        instance_item.setIcon(QIcon(pixmap))

    def add_colored_relation_bol_icon_to_item(self, instance_item: QStandardItem, typeURI: str):
        direction_icon_path = f'{str(IMG_DIR)}/bol.png'

        pixmap = QPixmap(direction_icon_path)
        self.apply_relation_color(pixmap, typeURI)

        instance_item.setIcon(QIcon(pixmap))

    def apply_relation_color(self, pixmap, typeURI):
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        color_code = '000000'
        if typeURI in self.color_legend.keys():
            color_code = self.color_legend[typeURI]
        color = QColor(f"#{color_code}")  # Choose the color you want
        painter.setBrush(color)
        painter.setPen(color)
        painter.drawRect(pixmap.rect())  # Draw over the pixmap with the chosen color
        painter.end()

    def add_no_asset_selected_placeholder(self):
        pass

    def add_no_options_placeholder(self):
        place_holder_item = QStandardItem(
            self._("no_options_available"))
        place_holder_item.setEditable(False)
        place_holder_item.setEnabled(False)
        place_holder_item.setSelectable(False)

        placeholder_font = QFont()
        placeholder_font.setItalic(True)
        place_holder_item.setFont(placeholder_font)

        # padding_item = QStandardItem("")
        # padding_item.setEditable(False)
        # padding_item.setEnabled(False)
        # padding_item.setSelectable(False)

        self.list_gui.addItem([place_holder_item])

    @classmethod
    def add_attribute_field_placeholder(cls, field,text):
        place_holder_item = QTreeWidgetItem()
        place_holder_item.setText(0, text)

        placeholder_font = QFont()
        placeholder_font.setItalic(True)
        place_holder_item.setFont(0,placeholder_font)
        field.addTopLevelItem(place_holder_item)

    def add_loading_placeholder(self):
        place_holder_item = QStandardItem(
            self._("loading"))
        place_holder_item.setEditable(False)
        place_holder_item.setEnabled(False)
        place_holder_item.setSelectable(False)

        placeholder_font = QFont()
        placeholder_font.setItalic(True)
        place_holder_item.setFont(placeholder_font)

        self.list_gui.addItem(place_holder_item)

    def clear(self):
        self.list_gui.clear()
        self.attribute_field.clear()

    # noinspection PyMethodMayBeStatic
    def set_clear_icon(self, button: QPushButton):
        button.setIcon(qta.icon('mdi.close', color=Styling.button_icon_color))

    def update_color_scheme(self):
        self.set_clear_icon(self.clear_search_bar_button)

    def asset_clicked_listener(self):
        pass

    def get_current_list_content_dict(self) -> dict:
        return self.id_to_object_with_text_and_data_dict

    def add_extra_elements_to_list_subtext_layout(self) -> None:
        pass

    def get_adjustable_subtext_frame(self):
        return self.list_subtext_frame

    @abc.abstractmethod
    def update_this_gui_list_content(self):
        pass