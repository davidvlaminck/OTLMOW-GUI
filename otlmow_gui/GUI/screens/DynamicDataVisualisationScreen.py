import json
import re
from pathlib import Path
from typing import List

import qtawesome as qta

from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QComboBox, QSizePolicy, \
    QWidget, QFrame, QHBoxLayout, QCheckBox, QSlider
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QObject, pyqtSlot, QUrl, Qt
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject
from otlmow_visuals.PyVisWrapper import PyVisWrapper

from otlmow_gui.Domain import global_vars

from otlmow_gui.Domain.logger.OTLLogger import OTLLogger
from otlmow_gui.Domain.step_domain.RelationChangeDomain import RelationChangeDomain
from otlmow_gui.Domain.util.Helpers import Helpers
from otlmow_gui.GUI.dialog_windows.NotificationWindow import NotificationWindow
from otlmow_gui.GUI.dialog_windows.OverwriteGraphWarningWindow import OverwriteGraphWarningWindow
from otlmow_gui.GUI.screens.DataVisualisation_elements.VisualisationHelper import VisualisationHelper
from otlmow_gui.GUI.screens.Screen import Screen
from otlmow_gui.GUI.screens.general_elements.ButtonWidget import ButtonWidget
from otlmow_gui.GUI.translation.GlobalTranslate import GlobalTranslate


class Backend(QObject):

    def __init__(self, parent_screen):
        super().__init__()
        self.parent_screen = parent_screen

    @pyqtSlot(str)
    def receive_new_combined_data(self, message):
        """Receives receive_new_combined_data from JavaScript."""
        data = json.loads(message)  # Convert string back to dict

        OTLLogger.logger.debug(f"Received new combined data: {message}")

        # test_json_path = global_vars.current_project.get_current_visuals_folder_path() / "new_nodes.json"
        # with open(test_json_path, 'w') as json_file:
        #     json.dump(data, json_file)


        new_node_data_str = json.dumps(data['nodeList']) #nodes and their position (including edgeJointNodes)
        new_edge_data_str = json.dumps(data['edgeList']) #edges (including subEdges)
        new_relationIdToSubEdges_data_str = json.dumps(data['relationIdToSubEdgesList']) #data supporting dynamic removal functionality
        new_relationIdToTotalSubEdgeCountList_data_str = json.dumps(data['relationIdToTotalSubEdgeCountList']) #data supporting dynamic removal functionality
        new_relationIdToJointNodesList_data_str = json.dumps(data['relationIdToJointNodesList']) #data supporting dynamic removal functionality
        new_SubEdgesToOriginalRelationIdList_data_str = json.dumps(data['SubEdgesToOriginalRelationIdList']) #data supporting dynamic removal functionality
        new_edgeJointNodesIdToConnectionDataDictList_data_str = json.dumps(data[
                                                                       'edgeJointNodesIdToConnectionDataDictList'])  # data supporting right-click edgeJointNode removal functionality
        new_collection_id_to_list_of_relation_ids_data_str = "{}"
        if 'collection_id_to_list_of_relation_ids' in data.keys():
            new_collection_id_to_list_of_relation_ids_data_str = json.dumps(data[
                                                                                   'collection_id_to_list_of_relation_ids'])  # data supporting hover to show collection edge functionality

        OTLLogger.logger.debug(new_collection_id_to_list_of_relation_ids_data_str)

        new_node_data_str = self.correct_node_title_attributes(new_node_data_str)

        try:
            html_path = self.parent_screen.get_current_html_path()
        except:
            OTLLogger.logger.error("Couldn't save the html because the html is outdated and the project is already closed")
            notification = NotificationWindow(title=GlobalTranslate._("Couldn't save visualisation"),
                                              message=GlobalTranslate._("Couldn't save the html because the html is outdated and the project is already closed\nTo fix this refresh the visualisation."))
            notification.exec()
            return

        self.parent_screen.save_html(file_path=html_path,
                                     new_node_data=new_node_data_str,
                                     new_edge_data=new_edge_data_str,
                                     new_relationIdToSubEdges_data=new_relationIdToSubEdges_data_str,
                                     new_relationIdToTotalSubEdgeCount_data=new_relationIdToTotalSubEdgeCountList_data_str,
                                     new_relationIdToJointNodes_data=new_relationIdToJointNodesList_data_str,
                                     new_SubEdgesToOriginalRelationId_data=new_SubEdgesToOriginalRelationIdList_data_str,
                                     new_edgeJointNodesIdToConnectionDataDict_data=new_edgeJointNodesIdToConnectionDataDictList_data_str,
                                     new_collection_id_to_list_of_relation_ids_dict=new_collection_id_to_list_of_relation_ids_data_str)
        global_vars.current_project.visualisation_uptodate.reset_full_state()
        global_vars.current_project.save_visualisation_python_support_data(self.parent_screen.std_vis_wrap)
    @pyqtSlot()
    def receive_network_changed_notification(self):
        self.parent_screen.set_graph_saved_status(False)

    @pyqtSlot()
    def receive_network_loaded_notification(self):
        OTLLogger.logger.info("js says network is loaded")
        self.parent_screen.js_is_loading = False
        self.parent_screen.loading_graph_status_label.setText("")

    @classmethod
    def correct_node_title_attributes(cls, new_node_data_str):
        # correcting the formatting of the title attribute of the node
        new_node_data_str = new_node_data_str.replace('"htmlTitle(\\', 'htmlTitle(')
        new_node_data_str = new_node_data_str.replace('</div>\\")"', '</div>")')
        return new_node_data_str




class DynamicDataVisualisationScreen(Screen):

    def __init__(self, _):
        super().__init__()
        # self.setWindowTitle("PyQt6 QWebEngine QWebChannel Example")
        # self.resize(800, 600)

        # data variables
        self.objects_in_memory = []
        self.std_vis_wrap = None
        self.js_is_loading = False
        self.max_slider_value = 50

        # translation model
        self._ = _

        #smaller support widgets
        self.refresh_needed_label = QLabel()
        self.graph_saved_status_label = QLabel()
        self.loading_graph_status_label = QLabel()
        self.visualisation_mode = QComboBox()
        self.collection_threshold_slider = QSlider(Qt.Orientation.Horizontal)
        self.collection_threshold_label = QLabel()
        self.too_many_objects_message = QLabel()
        self.relation_color_legend_title = QLabel()
        self.relation_id_to_relation_show_checkbox_dict = {}

        self.main_layout = QVBoxLayout()
        self.main_widget = self.create_main_widget()
        self.main_layout.addWidget(self.main_widget)
        self.setLayout(self.main_layout)



    def create_main_widget(self):
        main_widget = QWidget()
        main_widget.setProperty('class', 'background-box')

        window_layout = QVBoxLayout()
        window_layout.setContentsMargins(0, 0, 0, 0)

        # Set up the channel and backend for communication from js to python backend
        self.channel = QWebChannel()
        self.backend = Backend(parent_screen=self)
        self.channel.registerObject("backend", self.backend)

        # main QWebEngineView widget
        self.view = QWebEngineView(self)
        self.view.page().setWebChannel(self.channel)
        self.view.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, False)
        self.view.setContentsMargins(0, 0, 0, 0)
        self.view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


        self.view.settings().setAttribute( QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        self.view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)

        self.too_many_objects_message.setVisible(False)

        self.relation_color_legend_title.setText(self._("relations legend") + ":")

        window_layout.addWidget(self.create_button_container())
        window_layout.addWidget(self.view, 2)
        window_layout.addWidget(self.too_many_objects_message, 2)
        window_layout.addWidget(self.relation_color_legend_title)
        window_layout.addWidget(self.create_color_legend())

        main_widget.setLayout(window_layout)
        return main_widget

    def create_button_container(self):
        frame = QFrame()
        frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        frame_layout = QHBoxLayout()


        regenerate_btn = ButtonWidget()
        regenerate_btn.setIcon(qta.icon('mdi.refresh', color='white'))
        regenerate_btn.setProperty('class', 'primary-button')
        regenerate_btn.clicked.connect(lambda: OverwriteGraphWarningWindow(self,self._))
        regenerate_btn.setToolTip(self._("Regenerate the visualisation"))

        self.visualisation_mode.addItems(["1 Hiërarchische visualisatie",
                                          "2 Spinnenweb visualisatie",
                                          "3 Shell visualisatie",
                                          "4 ForceAtlas2Based visualisatie",
                                          ])
        self.visualisation_mode.setToolTip(self._("Options to generate the visualisation differently"))
        self.visualisation_mode.currentTextChanged.connect(self.on_visualisation_option_change)

        collection_threshold_tooltip = self._("Deze slider duidt de hoeveelheid van dezelfde relaties naar één asset nodig voor het bundelen in een collectie")
        self.collection_threshold_slider.setRange(0, 50)
        self.collection_threshold_slider.setValue(10)
        self.collection_threshold_slider.setToolTip(collection_threshold_tooltip)
        self.collection_threshold_slider.setFixedWidth(100)

        self.collection_threshold_label.setText((str(self.collection_threshold_slider.value())))
        self.collection_threshold_label.setToolTip(collection_threshold_tooltip)

        # Connect slider change to label update
        self.collection_threshold_slider.valueChanged.connect(self.on_value_changed)

        self.refresh_needed_label.setText(
            self._("The visualisation is outdated, refresh to see new changes"))
        self.refresh_needed_label.setStyleSheet('color:#DD1111;')
        # self.set_refresh_need_label_hidden_status(True)

        self.set_graph_saved_status(True)

        save_btn = ButtonWidget()
        # see all qta mdi icon options in: https://cdn.jsdelivr.net/npm/@mdi/font@5.9.55/preview.html
        save_btn.setIcon(qta.icon('mdi.content-save', color='white'))
        save_btn.setProperty('class', 'primary-button')
        save_btn.clicked.connect(lambda: self.save_in_memory_changes_to_html())
        save_btn.setToolTip(self._("Save changes"))

        help_btn = ButtonWidget()
        # see all qta mdi icon options in: https://cdn.jsdelivr.net/npm/@mdi/font@5.9.55/preview.html
        help_btn.setIcon(qta.icon('mdi.help', color='white'))
        help_btn.setProperty('class', 'primary-button')
        help_btn.clicked.connect(lambda: self.show_help_dialog_window())
        help_btn.setToolTip(self._("Help for data visualisation screen"))


        open_html_location_btn = ButtonWidget()
        # see all qta mdi icon options in: https://cdn.jsdelivr.net/npm/@mdi/font@5.9.55/preview.html
        open_html_location_btn.setIcon(qta.icon('mdi.folder-marker', color='white'))
        open_html_location_btn.setProperty('class', 'primary-button')
        open_html_location_btn.clicked.connect(lambda: Helpers.open_folder_and_select_document(
            global_vars.current_project.get_current_visuals_html_path()))
        open_html_location_btn.setToolTip(self._("Open visualisation html file location"))

        frame_layout.addWidget(regenerate_btn)
        frame_layout.addWidget(self.visualisation_mode)
        frame_layout.addWidget(self.collection_threshold_slider)
        frame_layout.addWidget(self.collection_threshold_label)
        frame_layout.addWidget(self.refresh_needed_label)
        frame_layout.addStretch()
        frame_layout.addWidget(self.loading_graph_status_label)
        frame_layout.addStretch()
        frame_layout.addWidget(self.graph_saved_status_label)
        frame_layout.addWidget(save_btn)
        frame_layout.addWidget(open_html_location_btn)
        frame_layout.addWidget(help_btn)
        frame_layout.setContentsMargins(0, 0, 0, 0)

        frame.setLayout(frame_layout)
        return frame

    def on_visualisation_option_change(self):
        global_vars.current_project.visualisation_uptodate.set_clear_all(True)
        self.update_refresh_need_label_state()

    def on_value_changed(self, val: int):
        self.collection_threshold_label.setText(str(val))
        self.check_if_slider_is_at_maxSliderValue()
        global_vars.current_project.visualisation_uptodate.set_clear_all(True)
        self.update_refresh_need_label_state()

    def show_help_dialog_window(self):
        title = self._("Help for data visualisation screen")
        message = self._("""
Help voor het gebruik van het datavisualisatie scherm:
        
- Linker-muisknop inhouden op OTL-asset => slepen
- Linker-muisknop op relatie pijl => een versleepbaar gewricht toevoegen
- Rechter-muisknop inhouden en slepen in lege ruimte => selectie box om meerder OTL-assets (+ gewrichten) te selecteren
- Ctrl-knop + Linker-muisknop op OTL-asset => toevoegen/verwijderen van OTL-asset aan selectie
        """)

        dialog = NotificationWindow(message = message,title=title)
        dialog.exec()

    def create_color_legend(self):

        frame = QFrame()
        self.frame_layout_legend = QHBoxLayout()
        self.frame_layout_legend.setContentsMargins(0, 0, 0, 0)
        self.fill_frame_layout_legend()
        frame.setLayout(self.frame_layout_legend)
        return frame

    def fill_frame_layout_legend(self):
        typeURIs_in_memory = [object_in_memory.typeURI for object_in_memory in
                              self.objects_in_memory]

        initial_state_per_relation_dict = {}
        key_list = list(self.relation_id_to_relation_show_checkbox_dict.keys())
        for relatie in typeURIs_in_memory:
            if relatie in key_list:
                initial_state_per_relation_dict[relatie] = self.relation_id_to_relation_show_checkbox_dict[
                    relatie].isChecked()
            else:
                initial_state_per_relation_dict[relatie] =  True


        for i in reversed(range(self.frame_layout_legend.count())):
            item = self.frame_layout_legend.takeAt(i)
            if item.widget():
                item.widget().deleteLater()
        self.relation_id_to_relation_show_checkbox_dict.clear()

        relatie_color_dict = PyVisWrapper().relatie_color_dict


        for relatie, color in relatie_color_dict.items():

            if relatie not in typeURIs_in_memory:
                continue

            item_frame = QFrame()
            item_layout_legend = QHBoxLayout()

            show_checkbox = QCheckBox()
            show_checkbox.setChecked(initial_state_per_relation_dict[relatie])
            show_checkbox.stateChanged.connect(self.create_on_stateChange_listener(relation_color=color))
            # store checkbox tied to it's relation typeURI
            self.relation_id_to_relation_show_checkbox_dict[
                relatie] = show_checkbox

            label = QLabel()
            relatie_name = relatie.split('#')[-1]
            label.setText(relatie_name)
            label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
            # label.setFixedWidth(50)

            color_label = QLabel()
            color_label.setStyleSheet(f"background-color: #{color}; ")
            color_label.setSizePolicy(QSizePolicy.Policy.Maximum,QSizePolicy.Policy.Expanding)
            color_label.setFixedWidth(30)




            item_layout_legend.addWidget(label)
            item_layout_legend.addWidget(show_checkbox)
            item_layout_legend.addWidget(color_label)
            item_layout_legend.setContentsMargins(10, 0, 0, 0)

            item_frame.setLayout(item_layout_legend)
            item_frame.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
            self.frame_layout_legend.addWidget(item_frame)

        if self.frame_layout_legend:
            self.frame_layout_legend.addStretch()


    def create_on_stateChange_listener(self,relation_color):
        return lambda state : self.set_relations_visibility(relation_color,state)

    def set_relations_visibility(self,relation_color:str, visibility:bool):
        if visibility:
            js_bool_hidden = "false"
        else:
            js_bool_hidden = "true"
        js_code = f"UpdateAllRelationHiddenStatesOfColor('{relation_color}',{js_bool_hidden})"
        OTLLogger.logger.debug(js_code)
        self.view.page().runJavaScript(js_code)

    def reset_ui(self, _):
        pass

    def load_html(self, html_loc):

        self.loading_graph_status_label.setText(self._("Loading graph"))

        self.view.setUrl(QUrl.fromLocalFile(str(html_loc).replace("\\","/")))

        if not self.std_vis_wrap:
            self.std_vis_wrap = VisualisationHelper.get_std_vis_wrap_instance()

        global_vars.current_project.load_visualisation_python_support_data(self.std_vis_wrap)

        self.set_graph_saved_status(True)

    def recreate_html(self,html_path:Path):
        OTLLogger.logger.debug(
            f"Executing DataVisualisationScreen.reload_html() for project {global_vars.current_project.eigen_referentie}",
            extra={"timing_ref": f"reload_html_{global_vars.current_project.eigen_referentie}"})

        self.objects_in_memory = self.load_assets()

        self.fill_frame_layout_legend()


        global_vars.current_project.visualisation_uptodate.reset_full_state()
        self.update_refresh_need_label_state()


        object_count = len(self.objects_in_memory)
        if object_count > VisualisationHelper.object_count_limit:
            # OBSOLETE: since V1.1 this will nearly never be entered since the threshold is so high
            # do not draw the visualisation when there are too many assets
            self.view.setVisible(False)
            if not self.too_many_objects_message.isVisible():
                self.too_many_objects_message.setVisible(True)

            translation = self._(
                "There are too many assets and relations to create a visualisation.\nmaximum: {0}\ncurrent: {1}")
            self.too_many_objects_message.setText(translation.format(
                VisualisationHelper.object_count_limit,
                object_count))

        else:

            self.too_many_objects_message.setVisible(False)
            if not self.view.isVisible():
                self.view.setVisible(True)

            self.std_vis_wrap = VisualisationHelper.create_html(html_loc= html_path,
                                                                objects_in_memory=self.objects_in_memory,
                                                                vis_mode=self.visualisation_mode.currentText(),
                                                                collection_threshold = self.collection_threshold_slider.value())
            global_vars.current_project.visualisation_uptodate.reset_full_state()
            global_vars.current_project.save_visualisation_python_support_data(self.std_vis_wrap)
            self.load_html(html_path)
            self.set_graph_saved_status(False)

        #reset the state of all color legend checkboxes
        self.relation_id_to_relation_show_checkbox_dict.clear()
        self.update_only_legend()

        object_count = len(self.objects_in_memory)
        OTLLogger.logger.debug(
            f"Executing DataVisualisationScreen.reload_html() for project {global_vars.current_project.eigen_referentie} ({object_count} objects)",
            extra={"timing_ref": f"reload_html_{global_vars.current_project.eigen_referentie}"})



    def get_current_html_path(self):
        return global_vars.current_project.get_current_visuals_html_path()

    def opened(self):
        if self.changed_project_bool:
            self.changed_project()


        elif not RelationChangeDomain.is_visualisation_uptodate():
            # if self.visualisation_mode.currentText() != "standaard visualisatie":
            #     self.set_refresh_need_label_hidden_status(False)
            #     return


            to_add_list = global_vars.current_project.visualisation_uptodate.get_to_be_inserted_relations()
            to_remove_list = global_vars.current_project.visualisation_uptodate.get_to_be_removed_relations()

            VisualisationHelper.add_new_relations(to_add_list=to_add_list,
                                   vis_wrap=self.std_vis_wrap, webview=self.view,relation_visible_dict=self.relation_id_to_relation_show_checkbox_dict)
            VisualisationHelper.remove_relations(to_remove_list=to_remove_list,
                                  vis_wrap=self.std_vis_wrap, webview=self.view)

            global_vars.current_project.visualisation_uptodate.reset_relations_uptodate()

        self.update_refresh_need_label_state()

    def update_refresh_need_label_state(self):
        if global_vars.current_project.visualisation_uptodate.is_uptodate():
            self.set_refresh_need_label_hidden_status(True)
        else:
            self.set_refresh_need_label_hidden_status(False)

    def update_slider_range(self):
        asset_count_in_project = len(RelationChangeDomain.get_shown_objects())
        self.max_slider_value = asset_count_in_project + 1
        self.collection_threshold_slider.blockSignals(True)
        self.collection_threshold_slider.setRange(0, self.max_slider_value)
        if self.max_slider_value > 10:
            self.collection_threshold_slider.setValue(10)
            self.collection_threshold_label.setText(str(self.collection_threshold_slider.value()))
        else:
            self.collection_threshold_slider.setValue(self.max_slider_value)
            self.check_if_slider_is_at_maxSliderValue()
        self.collection_threshold_slider.blockSignals(False)

    def check_if_slider_is_at_maxSliderValue(self):
        if self.collection_threshold_slider.value() >= self.max_slider_value:
            self.collection_threshold_label.setText(self._("uit"))

    def update_only_legend(self):
        self.objects_in_memory = self.load_assets()
        self.fill_frame_layout_legend()

    def changed_project(self):
        html_path: Path = self.get_current_html_path()
        self.relation_id_to_relation_show_checkbox_dict.clear()
        if html_path.exists():

            self.load_html(html_path)
            global_vars.current_project.visualisation_uptodate.reset_relations_uptodate()
            self.update_slider_range()
            self.update_only_legend()

        else:
            # self.recreate_html(html_path)
            self.view.setHtml("")
            global_vars.current_project.visualisation_uptodate.set_clear_all(True)

        self.changed_project_bool = False

    def set_refresh_need_label_hidden_status(self,new_state:bool):
        self.refresh_needed_label.setHidden(new_state)

    def load_assets(self) -> List[OTLObject]:
        assets = RelationChangeDomain.get_visualisation_instances()
        return  assets

    def save_in_memory_changes_to_html(self):

        # TODO: fix the code to create the png form html (currently hangs the program)
        # hti = Html2Image(output_path=global_vars.current_project.get_project_local_path(),
        #                  size=(1920, 1080 ), )
        # hti.screenshot(
        #     html_file=str(self.get_current_html_path()),
        #     save_as="screenshot.png",
        #     size=(1920, 1080 )
        # )

        js_code = 'sendCurrentCombinedDataToPython();\n'
        self.view.page().runJavaScript(js_code)
        self.set_graph_saved_status(True)

    def set_graph_saved_status(self,saved:bool) -> None:
        if global_vars.current_project:
            global_vars.current_project.set_saved_graph_status(saved)

        if saved:
            self.graph_saved_status_label.setText(self._("Changes saved"))
            self.graph_saved_status_label.setStyleSheet('color:#11DD11;justify-content:right;')
        else:
            self.graph_saved_status_label.setText(self._("Changes are not saved"))
            self.graph_saved_status_label.setStyleSheet('color:#DD1111;justify-content:right;')

    def save_html(cls, file_path: Path,
                  new_node_data:str,
                  new_edge_data:str,
                  new_relationIdToSubEdges_data:str="",
                  new_relationIdToTotalSubEdgeCount_data:str="",
                  new_relationIdToJointNodes_data:str="",
                  new_SubEdgesToOriginalRelationId_data:str="",
                  new_edgeJointNodesIdToConnectionDataDict_data:str="",
                  new_collection_id_to_list_of_relation_ids_dict:str = ""
                  ) -> None:

        OTLLogger.logger.debug(
            f"Executing DataVisualisationScreen.save_html() for project {global_vars.current_project.eigen_referentie}",
            extra={"timing_ref": f"save_html_{global_vars.current_project.eigen_referentie}"})

        with open(file_path) as file:
            file_data = file.read()

        old_node_data = cls.extract_node_dataset(file_data)
        old_edge_data = cls.extract_edges_dataset(file_data)

        old_relationIdToSubEdges_data = cls.extract_support_data(
            variable_name="relationIdToSubEdges",
            file_data=file_data)
        old_relationIdToTotalSubEdgeCount_data = cls.extract_support_data(
            variable_name="relationIdToTotalSubEdgeCount",
            file_data=file_data)
        old_relationIdToJointNodes_data = cls.extract_support_data(
            variable_name="relationIdToJointNodes",
            file_data=file_data)
        old_SubEdgesToOriginalRelationId_data = cls.extract_support_data(
            variable_name="SubEdgesToOriginalRelationId",
            file_data=file_data)
        old_edgeJointNodesIdToConnectionDataDict_data = cls.extract_support_data(
            variable_name="edgeJointNodesIdToConnectionDataDict",
            file_data=file_data)

        old_collection_id_to_list_of_relation_ids_dict = cls.extract_support_dict_data(
            variable_name="collection_id_to_list_of_relation_ids",
            file_data=file_data)

        if old_node_data and old_edge_data:

            if old_node_data:
                file_data = cls.replace_node_data(old_node_data, new_node_data,file_data)
            if old_edge_data:
                file_data = cls.replace_edge_data(old_edge_data, new_edge_data,file_data)

            file_data = cls.replace_support_data(variable_name="relationIdToSubEdges",
                                                 old_data=old_relationIdToSubEdges_data,
                                                 new_data=new_relationIdToSubEdges_data,
                                                 file_data=file_data)
            file_data = cls.replace_support_data(variable_name="relationIdToTotalSubEdgeCount",
                                                 old_data=old_relationIdToTotalSubEdgeCount_data,
                                                 new_data=new_relationIdToTotalSubEdgeCount_data,
                                                 file_data=file_data)
            file_data = cls.replace_support_data(variable_name="relationIdToJointNodes",
                                                 old_data=old_relationIdToJointNodes_data,
                                                 new_data=new_relationIdToJointNodes_data,
                                                 file_data=file_data)
            file_data = cls.replace_support_data(variable_name="SubEdgesToOriginalRelationId",
                                                 old_data=old_SubEdgesToOriginalRelationId_data,
                                                 new_data=new_SubEdgesToOriginalRelationId_data,
                                                 file_data=file_data)
            file_data = cls.replace_support_data(variable_name="edgeJointNodesIdToConnectionDataDict",
                                                 old_data=old_edgeJointNodesIdToConnectionDataDict_data,
                                                 new_data=new_edgeJointNodesIdToConnectionDataDict_data,
                                                 file_data=file_data)
            file_data = cls.replace_support_dict_data(
                variable_name="collection_id_to_list_of_relation_ids",
                old_data=old_collection_id_to_list_of_relation_ids_dict,
                new_data=new_collection_id_to_list_of_relation_ids_dict,
                file_data=file_data)

            file_data = cls.disable_hierarchical_options(file_data)
            file_data = cls.disable_physics_option(file_data)
            file_data = cls.disable_stabilisation_loading_screen(file_data)

            with open(file_path,mode="w") as file:
                file.write(file_data)

            OTLLogger.logger.info(f"Saved html to: {file_path}")
            OTLLogger.logger.debug(
                f"Executing DataVisualisationScreen.save_html() for project {global_vars.current_project.eigen_referentie}",
                extra={"timing_ref": f"save_html_{global_vars.current_project.eigen_referentie}"})

        else:
            OTLLogger.logger.error(f"FAILED to save html: old node and edge data not found")

    @classmethod
    def replace_support_data(cls, variable_name, old_data, new_data, file_data):
        file_data = file_data.replace(
            f"var {variable_name} = new Map({old_data});",
            f"var {variable_name} = new Map({new_data});")
        return file_data

    @classmethod
    def replace_support_dict_data(cls, variable_name, old_data, new_data, file_data):
        file_data = file_data.replace(
            f"var {variable_name} = {old_data}",
            f"var {variable_name} = {new_data}")
        return file_data

    @classmethod
    def disable_physics_option(cls, file_data):
        new_physics_setting = ", \"physics\": {\"enabled\": false,\"stabilization\":{\"enabled\": false}, "
        if new_physics_setting not in file_data:
            file_data = file_data.replace(", \"physics\": {", new_physics_setting)
        return file_data

    @classmethod
    def disable_hierarchical_options(cls, file_data):
        file_data = file_data.replace("\"hierarchical\": {\"enabled\": true",
                                      "\"hierarchical\": {\"enabled\": false")
        return file_data

    @classmethod
    def disable_stabilisation_loading_screen(cls,file_data):
        new_code = (
            "var network = drawGraph();\n"
            "var loadingBar = document.getElementById('loadingBar');\n"
            "if (loadingBar) { loadingBar.style.display = 'none'; }"
        )
        if "var network = drawGraph();" in file_data:
            file_data = file_data.replace(
                "var network = drawGraph();",
                new_code
            )
        return file_data

    @classmethod
    def extract_node_dataset(cls, file_data):
        pattern = re.compile(
            r'nodes\s*=\s*new\s+vis\.DataSet\(([\s\S]*?)\);',
            re.DOTALL
        )
        m = pattern.search(file_data)
        if m:
            old_node_data = m.group(1)
        else:
            old_node_data = None
        return old_node_data

    @classmethod
    def replace_node_data(cls, old_data, new_data, file_data):
        # replace the whole node dataset statement to prevent wrong replacement
        return file_data.replace(f"nodes = new vis.DataSet({old_data})",
                                 f"nodes = new vis.DataSet({new_data})")

    @classmethod
    def replace_edge_data(cls, old_data, new_data, file_data):
        # replace the whole node dataset statement to prevent wrong replacement
        return file_data.replace(f"edges = new vis.DataSet({old_data})",
                                 f"edges = new vis.DataSet({new_data})")

    @classmethod
    def extract_edges_dataset(cls, file_data):
        pattern = re.compile(
            r'edges\s*=\s*new\s+vis\.DataSet\(([\s\S]*?)\);',
            re.DOTALL
        )
        m = pattern.search(file_data)
        if m:
            old_edges_data = m.group(1)
        else:
            old_edges_data = None
        return old_edges_data

    @classmethod
    def extract_support_data(cls, variable_name ,file_data):
        pattern = re.compile(
            fr'var\s*{variable_name}\s*=\s*new\s+Map\(([\s\S]*?)\);',
            re.DOTALL
        )
        m = pattern.search(file_data)
        if m:
            old_edges_data = m.group(1)
        else:
            old_edges_data = None
        return old_edges_data

    @classmethod
    def extract_support_dict_data(cls, variable_name, file_data):


        pattern = re.compile(
            fr'var\s*{variable_name}\s*=\s*([\s\S]*?);',
            re.DOTALL
        )
        m = pattern.search(file_data)
        if m:
            old_edges_data = m.group(1)
        else:
            old_edges_data = None
        return old_edges_data

    @classmethod
    def test_extract_support_dict_data(cls, regex:str, file_data):

        pattern = re.compile(
            regex,
            re.DOTALL
        )
        m = pattern.search(file_data)
        if m:
            old_edges_data = "{" + m.group(1) + "}"
        else:
            old_edges_data = None
        return old_edges_data