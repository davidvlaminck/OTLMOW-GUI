import os
from copy import deepcopy
from dataclasses import replace
from typing import List

import qtawesome as qta

from pathlib import Path

from PyQt6.QtGui import QFont
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QWidget, QFrame, QHBoxLayout, QSizePolicy, \
    QComboBox
from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject
from otlmow_visuals.PyVisWrapper import PyVisWrapper
from otlmow_visuals.PyVisWrapper1 import PyVisWrapper1
from otlmow_visuals.PyVisWrapper2 import PyVisWrapper2
from otlmow_visuals.PyVisWrapper3 import PyVisWrapper3
from otlmow_visuals.PyVisWrapper4 import PyVisWrapper4
from otlmow_visuals.PyVisWrapper5 import PyVisWrapper5
from otlmow_visuals.PyVisWrapper6 import PyVisWrapper6
from otlmow_visuals.PyVisWrapper7 import PyVisWrapper7
from otlmow_visuals.PyVisWrapper8 import PyVisWrapper8

from Domain import global_vars
from Domain.logger.OTLLogger import OTLLogger
from Domain.step_domain.RelationChangeDomain import RelationChangeDomain
from GUI.screens.general_elements.ButtonWidget import ButtonWidget
from GUI.screens.Screen import Screen

ROOT_DIR = Path(__file__).parent

# HTML_DIR = ROOT_DIR.parent.parent / 'img' / 'html'
HTML_DIR = Path.home() / 'OTLWizardProjects' / 'img' / 'html'

class DataVisualisationScreen(Screen):

    object_count_limit = 300

    def __init__(self, _):
        super().__init__()

        if not HTML_DIR.exists():
            os.makedirs(HTML_DIR,exist_ok=True)

        self.frame_layout_legend = None
        self.objects_in_memory = []
        self.stdVis = None

        self.refresh_needed_label = QLabel()
        self.visualisation_mode = QComboBox()
        self.container_insert_data_screen = QVBoxLayout()
        self._ = _
        self.view = QWebEngineView()
        self.too_many_objects_message = QLabel()
        self.color_label_title = QLabel()
        self.init_ui()




    def init_ui(self):
        self.container_insert_data_screen.addWidget(self.create_html_container())

        self.setLayout(self.container_insert_data_screen)

    def create_html_container(self):
        window = QWidget()
        window.setProperty('class', 'background-box')
        
        window_layout = QVBoxLayout()
        window_layout.setContentsMargins(0,0,0,0)
        
        html_loc = ROOT_DIR.parent.parent / 'img' / 'html' / "basic.html"
        self.view.setHtml(open(html_loc).read())
        self.view.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, False)
        self.view.setContentsMargins(0, 0, 0, 0)
        self.view.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding )

        self.too_many_objects_message.setVisible(False)

        self.color_label_title.setText(self._("relations legend") + ":")
        
        window_layout.addWidget(self.create_button_container())
        window_layout.addWidget(self.view,2)
        window_layout.addWidget(self.too_many_objects_message,2)
        window_layout.addWidget(self.color_label_title)
        window_layout.addWidget(self.create_color_legend())
        
        window.setLayout(window_layout)
        return window


    def create_color_legend(self):

        frame = QFrame()
        self.frame_layout_legend = QHBoxLayout()
        self.fill_frame_layout_legend()
        frame.setLayout(self.frame_layout_legend)
        return frame

    def fill_frame_layout_legend(self):
        for i in reversed(range(self.frame_layout_legend.count())):
            self.frame_layout_legend.itemAt(i).widget().deleteLater()

        relatie_color_dict = PyVisWrapper().relatie_color_dict

        typeURIs_in_memory = [object_in_memory.typeURI for object_in_memory in
                              self.objects_in_memory]
        for relatie, color in relatie_color_dict.items():

            if relatie not in typeURIs_in_memory:
                continue

            color_label = QLabel()
            label = QLabel()
            relatie_name = relatie.split('#')[-1]
            label.setText(relatie_name)
            color_label.setStyleSheet(f"background-color: #{color}")
            self.frame_layout_legend.addWidget(color_label)
            self.frame_layout_legend.addWidget(label)

    def create_button_container(self):
        frame = QFrame()
        frame_layout = QHBoxLayout()
        
        refresh_btn = ButtonWidget()
        refresh_btn.setIcon(qta.icon('mdi.refresh', color='white'))
        refresh_btn.setProperty('class', 'primary-button')
        refresh_btn.clicked.connect(lambda: self.reload_html())

        self.refresh_needed_label.setText(self._("The visualisation is outdated, refresh to see new changes"))
        self.refresh_needed_label.setStyleSheet('color:#DD1111;')
        # self.refresh_needed_label.setHidden(True)

        self.visualisation_mode.addItems(["standaard visualisatie",
                                          "alternatief 1 visualisatie",
                                          "alternatief 2 visualisatie",
                                          "alternatief 3 visualisatie",
                                          "alternatief 4 visualisatie",
                                          "alternatief 5 visualisatie",
                                          "alternatief 6 visualisatie",
                                          "alternatief 7 visualisatie",
                                          "vorige"])

        frame_layout.addWidget(refresh_btn)
        frame_layout.addWidget(self.visualisation_mode)
        frame_layout.addWidget(self.refresh_needed_label)
        frame_layout.addStretch()
        frame_layout.setContentsMargins(0,0,0,0)
        
        frame.setLayout(frame_layout)
        return frame

    def reset_ui(self, _):
        super().reset_ui(_)
        # self.refresh_needed_label.setHidden(True)
        self._ = _
        self.color_label_title.setText(self._("relations legend") + ":")

    def reload_html(self):
        OTLLogger.logger.debug(
            f"Executing DataVisualisationScreen.reload_html() for project {global_vars.current_project.eigen_referentie}",
            extra={"timing_ref": f"reload_html_{global_vars.current_project.eigen_referentie}"})

        self.objects_in_memory = self.load_assets()
        RelationChangeDomain.visualisation_uptodate.reset_full_state()
        self.refresh_needed_label.setHidden(True)
        self.fill_frame_layout_legend()
        self.create_html(objects_in_memory=self.objects_in_memory,vis_mode= self.visualisation_mode.currentText())
        object_count = len(self.objects_in_memory)
        OTLLogger.logger.debug(
            f"Executing DataVisualisationScreen.reload_html() for project {global_vars.current_project.eigen_referentie} ({object_count} objects)",
            extra={"timing_ref": f"reload_html_{global_vars.current_project.eigen_referentie}"})
        js_code = 'newOptions = {"physics":{"enabled":false}};\nnetwork.setOptions(newOptions);\n'
        self.view.page().runJavaScript(js_code)

    def load_assets(self) -> List[OTLObject]:
        assets = RelationChangeDomain.get_visualisation_instances()
        return  assets

    def create_html(self, objects_in_memory:List[OTLObject],vis_mode="standaard visualisatie"):
        object_count = len(objects_in_memory)
        if object_count > DataVisualisationScreen.object_count_limit:
            self.view.setVisible(False)
            if not self.too_many_objects_message.isVisible():
                self.too_many_objects_message.setVisible(True)

            translation = self._("There are too many assets and relations to create a visualisation.\nmaximum: {0}\ncurrent: {1}")
            self.too_many_objects_message.setText(translation.format(
                DataVisualisationScreen.object_count_limit,
                object_count))

        else:
            self.too_many_objects_message.setVisible(False)
            if not self.view.isVisible():
                self.view.setVisible(True)
            html_loc = HTML_DIR / "visuals.html"
            previous_cwd = os.getcwd()
            os.chdir(Path.home() / 'OTLWizardProjects')
            objects_in_memory = deepcopy(objects_in_memory)

            if vis_mode == "alternatief 7 visualisatie":
                PyVisWrapper1().show(list_of_objects=objects_in_memory,
                                    html_path=Path(html_loc), launch_html=False)
            elif vis_mode == "alternatief 6 visualisatie":
                PyVisWrapper2().show(list_of_objects=objects_in_memory,
                                    html_path=Path(html_loc), launch_html=False)
            elif vis_mode == "alternatief 5 visualisatie":
                PyVisWrapper3().show(list_of_objects=objects_in_memory,
                                     html_path=Path(html_loc), launch_html=False)
            elif vis_mode == "alternatief 4 visualisatie":
                PyVisWrapper4().show(list_of_objects=objects_in_memory,
                                     html_path=Path(html_loc), launch_html=False)
            elif vis_mode == "alternatief 3 visualisatie":
                PyVisWrapper5().show(list_of_objects=objects_in_memory,
                                     html_path=Path(html_loc), launch_html=False)
            elif vis_mode == "alternatief 2 visualisatie":
                PyVisWrapper6().show(list_of_objects=objects_in_memory,
                                     html_path=Path(html_loc), launch_html=False)
            elif vis_mode == "alternatief 1 visualisatie":
                PyVisWrapper7().show(list_of_objects=objects_in_memory,
                                     html_path=Path(html_loc), launch_html=False)
            elif vis_mode == "standaard visualisatie":
                self.stdVis = PyVisWrapper8()
                self.stdVis.show(list_of_objects=objects_in_memory,
                                     html_path=Path(html_loc), launch_html=False)
            else:
                PyVisWrapper().show(list_of_objects=objects_in_memory,
                                    html_path=Path(html_loc), launch_html=False)
            os.chdir(previous_cwd)

            self.modify_html(html_loc)

            self.view.setHtml(open(html_loc).read())

    def modify_html(cls, file_path: Path) -> None:
        with open(file_path) as file:
            file_data = file.readlines()

        replace_index = -1
        for index, line in enumerate(file_data):
            if "drawGraph();" in line:
                replace_index = index

        if replace_index > 0:
            file_data[replace_index] = file_data[replace_index].replace("drawGraph();","var network = drawGraph();")
            file_data.insert(replace_index,"var container = document.getElementById('mynetwork');\n")
            file_data.insert(replace_index+1,
                             "var isPhysicsOn = true;\n")
            file_data.insert(replace_index+2,
                             "function disablePhysics(){\n")
            file_data.insert(replace_index+3,"if(isPhysicsOn){")
            file_data.insert(replace_index+4,'newOptions={"layout":{"hierarchical":{"enabled":false}}};\n')
            file_data.insert(replace_index + 5, "network.setOptions(newOptions);\n")
            file_data.insert(replace_index + 6,
                             'newOptions={"physics":{"enabled":false}};\n')
            file_data.insert(replace_index+7,'network.setOptions(newOptions);\n')
            file_data.insert(replace_index + 8, "isPhysicsOn = false;\n}};\n")
            file_data.insert(replace_index+9,"container.addEventListener('mouseover', disablePhysics);\n")
        file_data.insert(replace_index + 10, "function AddEdge(id,from_id, to_id,color,arrow)")
        file_data.insert(replace_index + 11, "{")
        file_data.insert(replace_index + 12, 'network.body.data.edges.add([{'
                                             '"id": id,'
                                             '"arrowStrikethrough": false,'
                                             '"arrows": arrow,'
                                             '"color": color,'
                                             '"from": from_id,'
                                             '"smooth": {'
                                             '"enabled": false'
                                             '},'
                                             '  "to": to_id,'
                                             '  "width": 2'
                                             '}]);')
        file_data.insert(replace_index + 13, "}")

        file_data.insert(replace_index + 14,
                         "function AddEdgeWithLabel(id,from_id, to_id,color,arrow,label)")
        file_data.insert(replace_index + 15, "{")
        file_data.insert(replace_index + 16, 'network.body.data.edges.add([{'
                                             '"id": id,'
                                             '"arrowStrikethrough": false,'
                                             '"arrows": arrow,'
                                             '"color": color,'
                                             '"from": from_id,'
                                             '"label": label,'
                                             '"smooth": {'
                                             '"enabled": false'
                                             '    },'
                                             '        "to": to_id,'
                                             '       "width": 2'
                                             '}]);')
        file_data.insert(replace_index + 17, "}")
        file_data.insert(replace_index + 18, 'function removeEdge(id)')
        file_data.insert(replace_index + 19, '{')
        file_data.insert(replace_index + 20, 'if (network.body.data.edges._data.has(id))')
        file_data.insert(replace_index + 21, '   { network.body.data.edges.remove([id]);}')
        file_data.insert(replace_index + 22, 'else')
        file_data.insert(replace_index + 23, '   {console.log("attempted to remove: " + id)}')
        file_data.insert(replace_index + 24, '}')

        with open(file_path, 'w') as file:
            for line in file_data:
                file.write(line)

    def opened(self):
        if not RelationChangeDomain.is_visualisation_uptodate():
            if (self.visualisation_mode.currentText() != "standaard visualisatie"):
                self.refresh_needed_label.setHidden(False)
                return


            # if there are new relations add them to the visualisation
            for relation_object in RelationChangeDomain.visualisation_uptodate.get_to_be_inserted_relations():

                add_edge_arguments = PyVisWrapper8().create_edge_inject_arguments(relation_object)
                if "label" in add_edge_arguments: #a heeftBetrokkene relation with their rol as label
                    js_code = f'AddEdgeWithLabel("{add_edge_arguments["id"]}","{add_edge_arguments["from_id"]}", "{add_edge_arguments["to_id"]}","#{add_edge_arguments["color"]}","{add_edge_arguments["arrow"]}","{add_edge_arguments["label"]}")'
                elif "arrow" in add_edge_arguments: #a bidirectional relation
                    js_code = f'AddEdge("{add_edge_arguments["id"]}","{add_edge_arguments["from_id"]}", "{add_edge_arguments["to_id"]}","#{add_edge_arguments["color"]}","{add_edge_arguments["arrow"]}");'
                else:  #een directional relation
                    js_code = f'AddEdge("{add_edge_arguments["id"]}","{add_edge_arguments["from_id"]}", "{add_edge_arguments["to_id"]}","#{add_edge_arguments["color"]}",null);'
                OTLLogger.logger.debug(js_code)
                self.view.page().runJavaScript(js_code)

            # if there are removed relations remove them from the visualisation
            for relation_object in RelationChangeDomain.visualisation_uptodate.get_to_be_removed_relations():
                rel_id = relation_object.assetId.identificator

                if rel_id in self.stdVis.relation_id_to_collection_id:
                    collection_id = self.stdVis.relation_id_to_collection_id.pop(rel_id)
                    self.stdVis.collection_id_to_list_of_relation_ids[collection_id] = [rel_set for rel_set in self.stdVis.collection_id_to_list_of_relation_ids[collection_id] if rel_set[0] != rel_id]
                    new_collection_content = "\n".join([rel_set[1] for rel_set in self.stdVis.collection_id_to_list_of_relation_ids[collection_id]])
                    new_collection_size = len(self.stdVis.collection_id_to_list_of_relation_ids[collection_id])
                    new_label = f"<i><b>Collectie ({new_collection_size})</b></i>"
                    new_title = f"Collectie ({new_collection_size}):\n{new_collection_content}"
                    # https://stackoverflow.com/questions/32765015/vis-js-modify-node-properties-on-click
                    js_code = f'network.body.data.nodes.updateOnly({{id: "{collection_id}", label: "{new_label}", title:`{new_title}`}});'
                else:
                    js_code = f'removeEdge("{relation_object.assetId.identificator}");'

                OTLLogger.logger.debug(js_code)
                self.view.page().runJavaScript(js_code)
            RelationChangeDomain.visualisation_uptodate.reset_relations_uptodate()

            if RelationChangeDomain.visualisation_uptodate.get_clear_all():
                self.refresh_needed_label.setHidden(False)
                return

        self.refresh_needed_label.setHidden(True)




