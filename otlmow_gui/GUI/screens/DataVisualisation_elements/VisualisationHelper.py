import json
from copy import deepcopy
from pathlib import Path
from typing import List

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject
from otlmow_visuals.PyVisWrapper import PyVisWrapper

from otlmow_gui.Domain.ProgramFileStructure import ProgramFileStructure
from otlmow_gui.Domain.logger.OTLLogger import OTLLogger



class VisualisationHelper:
    object_count_limit = 100000

    @classmethod
    def get_std_vis_wrap_instance(cls):
        return PyVisWrapper()

    @classmethod
    def create_html(cls,html_loc:Path,
                    objects_in_memory: List[OTLObject],
                    vis_mode="1 Hiërarchische visualisatie",
                    collection_threshold=-1):


        objects_in_memory = deepcopy(objects_in_memory)
        # sort on typeURI to ensure color coding is always the same for the same set of assets
        objects_in_memory.sort(key=lambda otl_object: otl_object.typeURI)

        visualisation_option = 1
        if vis_mode == "1 Hiërarchische visualisatie":
            visualisation_option = 1
        elif vis_mode == "2 Spinnenweb visualisatie":
            visualisation_option= 4
        elif vis_mode == "3 Shell visualisatie":
            visualisation_option = 3
        elif vis_mode == "4 Repulsion visualisatie":
            visualisation_option = 4
        elif vis_mode == "4 ForceAtlas2Based visualisatie":
            visualisation_option = 5



        stdVis = cls.get_std_vis_wrap_instance()
        stdVis.show(list_of_objects=objects_in_memory, visualisation_option = visualisation_option,
                    html_path=Path(html_loc), launch_html=False,collection_threshold=collection_threshold)

        cls.modify_html(html_loc)

        return stdVis

    @classmethod
    def modify_html(cls, file_path: Path) -> None:
        with open(file_path) as file:
            file_data = file.readlines()

        replace_index_lib = next((
                index for index, line in enumerate(file_data)
                if '<script src="lib/bindings/utils.js"></script>' in line),
            -1)
        if replace_index_lib > 0:
            cls.replace_and_add_lines(file_data, replace_index_lib,
                                      '<script src="lib/bindings/utils.js"></script>',
                                      '<script src="lib/bindings/utils.js"></script>',

                                      ['<script src="qrc:///qtwebchannel/qwebchannel.js"></script>'])

        replace_index = next((
                index for index, line in enumerate(file_data)
                if "drawGraph();" in line),
            -1)
        if replace_index > 0:
            path_for_in_js = str(file_path.absolute()).replace("\\","\\\\")

            add_data = ["var container = document.getElementById('mynetwork');",
                        f'var html_path = "{path_for_in_js}";',
                        "",
                        "// add webchannel to javascript to communicate with python",
                        'document.addEventListener("DOMContentLoaded", function() '
                        '{',

                        "   network.on('stabilizationIterationsDone',onIterationStabilized)",
                        "   network.on('stabilized',onStabilized)",
                        "   container.addEventListener('mouseover', disablePhysics);",
                        "   setTimeout(disablePhysics, 300);",
                        "   makeMeMultiSelect(container, network, nodes);",
                        "   try",
                        "   {",
                        """     new QWebChannel(qt.webChannelTransport, function(channel) 
                                {
                                    window.backend = channel.objects.backend;
                                    
                                    if (window.backend)   
                                    {window.backend.receive_network_loaded_notification();}
                                    else
                                    { 
                                       alert('window.backend.receive_network_loaded_notification() doesnt exist yet');
                                       console.log('QWebChannel is not initialized yet.');
                                    }
                                    
                                });""",
                        "   } ",
                        "   catch (error) ",
                        "   {",
                        "       console.error(error);",
                        # '       alert("DataVisualisationScreen:Error in webchannel creation: " + error);',
                        "   }",

                        "})"]

            add_data.extend(cls.create_disablePhysics_js_function_and_add_to_event())
            add_data.extend(cls.create_ExtractNodeList_js_function())
            add_data.extend(cls.create_ExtractEdgeList_js_function())
            add_data.extend(cls.create_sendCurrentCombinedDataToPython_js_function())
            add_data.extend(cls.create_AddEdge_js_function())
            add_data.extend(cls.create_AddEdgeWithLabel_js_function())
            add_data.extend(cls.create_removeEdge_js_function())
            add_data.extend(cls.create_removeEdgeJointNode_js_function())
            add_data.extend(cls.create_UpdateCollectionAttributes_js_function())
            add_data.extend(cls.create_getFlatListOfRelationIdsInCollection())
            add_data.extend(cls.create_UpdateAllRelationHiddenStatesOfColor_js_function())
            add_data.extend(cls.create_setAllNonCollectionEdgesToUnhidden_js_function())


            add_data.extend(cls.load_js_script_file("dragMultiSelect.js"))

            cls.replace_and_add_lines(file_data, replace_index,
              "drawGraph();",
              "var network = drawGraph();\n"
                "var loadingBar = document.getElementById('loadingBar');\n"
                "if (loadingBar) { loadingBar.style.display = 'none'; }"
                ,add_data)

        with open(file_path, 'w') as file:
            for line in file_data:
                file.write(line)

    @classmethod
    def load_js_script_file(cls, script_filename):
        library_path = ProgramFileStructure.get_dynamic_library_path("javascripts_visualisation")
        script_path = library_path / script_filename
        with open(script_path) as js_script_file:
            js_script_lines = js_script_file.readlines()
            return js_script_lines
        return []

    @classmethod
    def replace_and_add_lines(cls, file_data, replace_index, start_line_to_replace: str,
                              start_replacement: str, list_of_followup_lines: list[str]):
        file_data[replace_index] = file_data[replace_index].replace(start_line_to_replace,
                                                                    start_replacement)
        for i, followup_line in enumerate(list_of_followup_lines):
            file_data.insert(replace_index + i, followup_line + "\n")

    @classmethod
    def create_disablePhysics_js_function_and_add_to_event(cls):
        return ["var isPhysicsOn = true;",
                "function disablePhysics()",
                "{",
                "   //use this if the layout IS hierarchical",
                "   if(isPhysicsOn && network['layoutEngine']['options']['hierarchical']['enabled'])",
                "   {",
                # '       alert("disabled by disablePhysics")' ,
                '       newOptions={"layout":{"hierarchical":{"enabled":false}}};\n',
                "       network.setOptions(newOptions);",
                '       newOptions={\"physics\":{\"enabled\":false}};\n',
                "       network.setOptions(newOptions);",
                "       isPhysicsOn = false;\n",
                "   }",
                "};",

                "function onStabilized()",
                "{",
                "   //use this if the layout is NOT hierarchical",
                "   if(isPhysicsOn && !(network['layoutEngine']['options']['hierarchical']['enabled']))",
                "   {",
                # '       alert("disabled by stabilized")' ,
                '       newOptions={"layout":{"hierarchical":{"enabled":false}}};\n',
                "       network.setOptions(newOptions);",
                '       newOptions={\"physics\":{\"enabled\":false}};\n',
                "       network.setOptions(newOptions);",
                # "       sendCurrentCombinedDataToPython()",
                "       isPhysicsOn = false;\n",
                "   }",
                "};",
                "function onIterationStabilized()",
                "{",
                "   //use this if the layout is NOT hierarchical",
                "   if(isPhysicsOn && !(network['layoutEngine']['options']['hierarchical']['enabled']))",
                "   {",
                # '       alert("disabled by iteration stabilized")',
                '       newOptions={"layout":{"hierarchical":{"enabled":false}}};\n',
                "       network.setOptions(newOptions);",
                '       newOptions={\"physics\":{\"enabled\":false}};\n',
                "       network.setOptions(newOptions);",
                # "       sendCurrentCombinedDataToPython()",
                "       isPhysicsOn = false;\n",
                "   }",
                "};",

                ]

    @classmethod
    def create_AddEdge_js_function(cls):
        return ["function AddEdge(id,from_id, to_id,color,arrow,hidden)",
                "{",
                '   applyAddEdgesToNetwork([{'
                '       "id": id,'
                '       "arrowStrikethrough": false,'
                '       "arrows": arrow,'
                '       "color": color,'
                '       "from": from_id,'
                '       "hidden": hidden,'
                '       "smooth": '
                '           {'
                '           "enabled": false'
                '           },'
                '               "to": to_id,'
                '               "width": 2'
                '           }]);',
                "}"]

    @classmethod
    def create_sendCurrentCombinedDataToPython_js_function(cls):
        return ["function sendCurrentCombinedDataToPython()",
                "{",
                # '   unhideAllRelations()',
                '   network.storePositions() // alters the data in network.body.data.nodes with the current coordinates so i can be read and stored',
                # '   console.log("called storePositions()")',
                "   var nodeList = ExtractNodeList();    //nodes and their position (including edgeJointNodes)",
                "   var edgeList = ExtractEdgeList();    //edges (including subEdges)",
                "   ",
                "   var relationIdToSubEdgesList = Array.from(relationIdToSubEdges.entries());   //data supporting dynamic removal functionality",
                "   var relationIdToTotalSubEdgeCountList = Array.from(relationIdToTotalSubEdgeCount.entries());   //data supporting dynamic removal functionality",
                "   var relationIdToJointNodesList = Array.from(relationIdToJointNodes.entries());   //data supporting dynamic removal functionality",
                "   var SubEdgesToOriginalRelationIdList = Array.from(SubEdgesToOriginalRelationId.entries());   //data supporting dynamic removal functionality",
                "   var edgeJointNodesIdToConnectionDataDictList = Array.from(edgeJointNodesIdToConnectionDataDict.entries());   //data supporting right-click edgeJointNode removal functionality",
                "   ",
                "   //set all relations to unhidden if they were hidden by the python interface",
                "   setAllNonCollectionEdgesToUnhidden(edgeList);",
                "   ",
                "   ",
                # "   var edgeJointNodesIdToConnectionDataDictList = JSON.parse(edgeJointNodesIdToConnectionDataDict;   //data supporting right-click edgeJointNode removal functionality",
                "   var combinedData = {'html_path': html_path,"
                "                       'nodeList': nodeList,"
                "                       'edgeList': edgeList,"
                "                       'relationIdToSubEdgesList':relationIdToSubEdgesList,"
                "                       'relationIdToTotalSubEdgeCountList': relationIdToTotalSubEdgeCountList,"
                "                       'relationIdToJointNodesList': relationIdToJointNodesList,"
                "                       'SubEdgesToOriginalRelationIdList': SubEdgesToOriginalRelationIdList,"
                "                       'edgeJointNodesIdToConnectionDataDictList' : edgeJointNodesIdToConnectionDataDictList,"
                "                       'collection_id_to_list_of_relation_ids' : collection_id_to_list_of_relation_ids"
                "                       }",
                '   var combinedDataStr = JSON.stringify(combinedData)',
                # '   console.log(combinedDataStr)',
                # '   alert("DataVisualisationScreen: " + combinedDataStr);'
                "   if (window.backend)",
                "   {",
                "       window.backend.receive_new_combined_data(combinedDataStr);",
                # "       alert('sent new node'); ",
                # "       window.backend.receive_coordinates(JSON.stringify({lat: 56, lng: 30}));",
                "   }"
                "   else",
                "   {"
                '       console.log("QWebChannel is not initialized yet.");',
                # '       alert("DataVisualisationScreen: QWebChannel is not initialized");',
                "   }",

                "}"]

    @classmethod
    def create_ExtractNodeList_js_function(cls):
        return ["function ExtractNodeList()   "
                "{"
                "   var node_attributes = Object.fromEntries(network.body.data.nodes._data);",
                "   var nodeList = [];",
                "   for (const nodeId of network.body.data.nodes._data.keys()) ",
                "   {",
                "       if (network.body.data.nodes._data.get(nodeId).title)",
                "       {",
                "           var strTitle = network.body.data.nodes._data.get(nodeId).title.innerHTML; // use the innerhtml so it can be converted to json",
                "           if (strTitle)",
                "           node_attributes[nodeId].title = 'htmlTitle(\"' + strTitle.replace('\"','\\\"') +  '\")'; //add htmlTitle so is looks exactly like how the nodes are normally created",
                "       }",
                "       nodeList.push(node_attributes[nodeId]);",
                "   }",
                "   return nodeList",
                "}"]

    @classmethod
    def create_setAllNonCollectionEdgesToUnhidden_js_function(cls):
        return ["function setAllNonCollectionEdgesToUnhidden(edgeList)",
                '{',
                '   //collect all relation_ids that are in a collection they should not be unhidden',
                '   var relation_ids_in_collection_id = getFlatListOfRelationIdsInCollection()',
                '   edgeList.forEach((edgeData) =>',
                '   {',
                '       if( !relation_ids_in_collection_id.includes(edgeData["id"]))',
                '           edgeData["hidden"] = false;',
                '   })',
                '   return edgeList',
                '} ']

    @classmethod
    def create_getFlatListOfRelationIdsInCollection(cls):
        return ["function getFlatListOfRelationIdsInCollection()",
                '{',
                '   relation_ids_in_collection_id = []',
                '   for (collection_id in collection_id_to_list_of_relation_ids)',
                '   {',
                '       for (rel_tuple_index in collection_id_to_list_of_relation_ids[collection_id])',
                '       {',
                '           relation_ids_in_collection_id.push(collection_id_to_list_of_relation_ids[collection_id][rel_tuple_index][0])',
                '       }',
                '   }',
                '   return relation_ids_in_collection_id;',
                '}']

    @classmethod
    def create_ExtractEdgeList_js_function(cls):
        return ["function ExtractEdgeList()   "
                "{"
                "   var edge_attributes = Object.fromEntries(network.body.data.edges._data);",
                "   var edgeList = [];",
                "   for (const edgeId of network.body.data.edges._data.keys()) ",
                "   {",
                "       edgeList.push(edge_attributes[edgeId]);",
                "   }",
                "   return edgeList",
                "}"]
    @classmethod
    def create_AddEdgeWithLabel_js_function(cls):
        return ["function AddEdgeWithLabel(id,from_id, to_id,color,arrow,label,hidden)",
                "{",
                '   applyAddEdgesToNetwork([{'
                '   "id": id,'
                '   "arrowStrikethrough": false,'
                '   "arrows": arrow,'
                '   "color": color,'
                '   "from": from_id,'
                '   "label": label,'
                '   "smooth": {'
                '   "enabled": false'
                '    },'
                '   "hidden": hidden,'
                '   "to": to_id,'
                '   "width": 2'
                '    }]);',
                "}"]



    @classmethod
    def create_removeEdge_js_function(cls):
        return ['function removeEdge(id)',
                '{',
                '  if (network.body.data.edges._data.has(id))',
                '       applyRemoveEdgesFromNetwork([id]);//defined in PyViswrapper',
                '  else if (!relationIdToSubEdges)',
                '      console.log("attempted to remove: " + id)',
                '  else if (relationIdToSubEdges.has(id))',
                '  {',
                '      //remove all selfmade subEdges and jointNodes that the original relations was replaced with',
                '      subEdges = relationIdToSubEdges.get(id)',
                '      jointNodes = relationIdToJointNodes.get(id)',
                '      ',
                '      applyRemoveEdgesFromNetwork(subEdges); //defined in PyViswrapper',
                '      applyRemoveNodesFromNetwork(jointNodes); //defined in PyViswrapper',
                '      ',
                '      //remove stored data on subedges and jointnodes',
                '      subEdges.forEach((subEdgeId) =>',
                '      {',
                '          SubEdgesToOriginalRelationId.delete(subEdgeId);',
                '      })',
                '      relationIdToTotalSubEdgeCount.delete(id);',
                '      relationIdToSubEdges.delete(id);',
                '      relationIdToJointNodes.delete(id);',
                '  }',
                '  else',
                '      {console.log("attempted to remove: " + id)}',
                '}']

    @classmethod
    def create_UpdateCollectionAttributes_js_function(cls):
        return ['function UpdateCollectionAttributes(collection_id,new_label,new_title,new_collection_id_to_list_of_relation_ids)',
                '{',
                "      var newPos = network.getPosition(collection_id)",
                '      applyUpdateNodeInNetwork({"id": collection_id, "label": new_label, "title":new_title,"x":  newPos.x,"y": newPos.y});',
                '      collection_id_to_list_of_relation_ids = new_collection_id_to_list_of_relation_ids;',
                '}']

    @classmethod
    def create_UpdateAllRelationHiddenStatesOfColor_js_function(cls):
        return [
            'function UpdateAllRelationHiddenStatesOfColor(color,hidden)',
            '{',
            '       var newAttributesEdgesList = [];'
            '       network.body.data.edges._data.forEach((data,key) =>',
            '       {',
            '           var relation_ids_in_collection_id = getFlatListOfRelationIdsInCollection()',
            # '           if (data["color"] == color &&(data["id"].includes("special_edge")|| !relation_ids_in_collection_id.includes(data["id"])))'  ,
            '           if (data["color"] == color && !relation_ids_in_collection_id.includes(data["id"]))',
            '               newAttributesEdgesList.push({"id": data["id"], "hidden": hidden});',
            '       })',
            '       applyUpdateEdgeInNetwork(newAttributesEdgesList,false);',
            '}'
        ]

    @classmethod
    def create_unhideAllRelations_js_function(cls):
        return [
            'function unhideAllRelations()',
            '{',
            '       var newAttributesEdgesList = [];'
            '       network.body.data.edges._data.forEach((data,key) =>',
            '       {',
            '               newAttributesEdgesList.push({"id": data["id"], "hidden": false});'
            '       })',
            '       applyUpdateEdgeInNetwork(newAttributesEdgesList,false);',
            '}'
        ]

    @classmethod
    def create_removeEdgeJointNode_js_function(cls):
        return ['function removeEdgeJointNode(node_id)',
                '{',
                '   if (edgeJointNodesIdToConnectionDataDict.has(node_id))',
                '   {',
                '       var edgeNodeConnectionData = edgeJointNodesIdToConnectionDataDict.get(node_id);',
                '       var originalEdgeId = edgeNodeConnectionData["originalEdgeId"]; ',
                '       var previousEdgeId = edgeNodeConnectionData["previousEdgeId"];',
                '       var subEdge1Id = edgeNodeConnectionData["newSubEdge1Id"]; ',
                '       var subEdge2Id = edgeNodeConnectionData["newSubEdge2Id"]; ',
                '       var toNodeId = edgeNodeConnectionData["newSubEdge1Data.to"]; ',
                '       var fromNodeId = edgeNodeConnectionData["newSubEdge2Data.from"]; ',
                '       ',
                '       //get attribute of a subedge',
                '       newEdgeAttributes = JSON.parse(JSON.stringify(network.body.data.edges._data.get(subEdge1Id)));',
                '       //remove the 2 subedges in network',
                '       applyRemoveEdgesFromNetwork([subEdge1Id,subEdge2Id]);',
                '       ',
                '       //also remove them from supporting data'
                '       SubEdgesToOriginalRelationId.delete(subEdge1Id);',
                '       SubEdgesToOriginalRelationId.delete(subEdge2Id);',

                '       var currCount = relationIdToTotalSubEdgeCount.get(originalEdgeId);',
                '       relationIdToTotalSubEdgeCount.set(originalEdgeId, currCount-1);',
                '       relationIdToSubEdges.get(originalEdgeId).splice(subEdge1Id,1);',
                '       relationIdToSubEdges.get(originalEdgeId).splice(subEdge2Id,1);',
                '       relationIdToSubEdges.get(originalEdgeId).push(previousEdgeId)',
                '       SubEdgesToOriginalRelationId.set(previousEdgeId,originalEdgeId);',

                '       //add a new subedge with originalEdgeId between the to and from node',
                '       newEdgeAttributes.id = previousEdgeId;'   ,
                '       newEdgeAttributes.to = toNodeId;',
                '       newEdgeAttributes.from = fromNodeId; ',
                "       applyAddEdgesToNetwork([newEdgeAttributes])",
                '       ',
                '       //edit supporting data of the to and from nodes so they have the correct',
                '       //to and from themselves',
                '       updateNeighbouringEdgeJointNode(toNodeId, node_id, fromNodeId)',
                '       updateNeighbouringEdgeJointNode(fromNodeId, node_id, toNodeId)',
                '       updateConnectingEdgeOnNeighbouringEdgeJointNode(toNodeId,subEdge1Id,previousEdgeId)',
                '       updateConnectingEdgeOnNeighbouringEdgeJointNode(toNodeId,subEdge2Id,previousEdgeId)',
                '       updateConnectingEdgeOnNeighbouringEdgeJointNode(fromNodeId,subEdge1Id,previousEdgeId)',
                '       updateConnectingEdgeOnNeighbouringEdgeJointNode(fromNodeId,subEdge2Id,previousEdgeId)',
                '       ' ,
                # '   console.log("remove edge jointnode")',
                # 'edgeJointNodesIdToConnectionDataDict.forEach((data,key) =>',
                # '      {',
                # '         console.log(key +": " + JSON.stringify(data))',
                # '      })',
                # '   console.log(" network.body.data.edges:\\n ")',
                # 'network.body.data.edges._data.forEach((data,key) =>',
                # '      {',
                # '         console.log(key +": " + JSON.stringify(data))',
                # '      })',
                 # '   console.log(" edges:\\n "+  Array.from(network.body.data.edges._data.entries()))',
                '       //remove edgeJointNode from supporting data',
                '       relationIdToJointNodes.delete(node_id);',
                '       //remove edgeJointNode from network',
                '       applyRemoveNodesFromNetwork([node_id])',
                '       currentlyHoveredNode = null',
                '   }',
                '}',

                ]

    @classmethod
    def remove_relations(cls,to_remove_list, vis_wrap, webview):
        if not vis_wrap:
            return

        # if there are removed relations remove them from the visualisation
        for relation_object in to_remove_list:
            rel_id = relation_object.assetId.identificator

            if rel_id in vis_wrap.relation_id_to_collection_id:
                collection_ids = vis_wrap.relation_id_to_collection_id.pop(rel_id)
                js_code = ""
                for collection_id in collection_ids:
                    vis_wrap.collection_id_to_list_of_relation_ids[collection_id] = \
                        [rel_set for rel_set in vis_wrap.collection_id_to_list_of_relation_ids[
                            collection_id] if rel_set[0] != rel_id]
                    new_label, new_title = cls.create_new_special_node_text(collection_id,vis_wrap)

                    js_code += f'UpdateCollectionAttributes("{collection_id}", "{new_label}","{new_title}",{json.dumps(vis_wrap.collection_id_to_list_of_relation_ids)});\n'
                js_code += f'\nremoveEdge("{relation_object.assetId.identificator}");'
            else:
                js_code = f'removeEdge("{relation_object.assetId.identificator}");'

            OTLLogger.logger.debug(js_code)
            webview.page().runJavaScript(js_code)

    @classmethod
    def add_new_relations(cls, to_add_list, vis_wrap,webview,relation_visible_dict):

        if not vis_wrap:
            return
        # if there are new relations add them to the visualisation
        for relation_object in to_add_list:
            rel_id = relation_object.assetId.identificator
            add_edge_arguments = vis_wrap.create_edge_inject_arguments(relation_object)
            collect_id_to_original_asset_id_dict= {}

            if "label" in add_edge_arguments:  # a heeftBetrokkene relation with their rol as label
                # first check if the new relation needs to be added to a current collection
                added_to_collection = False
                for special_edge in vis_wrap.special_edges:
                    # first check if the new relation is the same type as the special edge
                    if (special_edge["label"] == add_edge_arguments["label"] and
                            special_edge["arrows"] == add_edge_arguments["arrow"] and
                            special_edge["color"] == add_edge_arguments["color"]):
                        if special_edge["from"] == add_edge_arguments["from_id"]:
                            # is this case:
                            # special_edge["from"] is the id of the asset that has relations to many assets
                            collection_id = special_edge["to"]  # special_edge["to"] is the id of the collection_node
                            try:
                                screen_name_of_new_asset = vis_wrap.asset_id_to_display_name_dict[add_edge_arguments["to_id"]]
                            except:
                                OTLLogger.logger.debug(f"Couldn't find display name of node id: {add_edge_arguments['to_id']}\n Needs refresh")
                                screen_name_of_new_asset = vis_wrap.asset_id_to_display_name_dict[collect_id_to_original_asset_id_dict[add_edge_arguments["to_id"]]]

                            added_to_collection = True
                            js_code = cls.create_js_code_to_add_to_collection(vis_wrap,
                                                                               collection_id,
                                                                               rel_id,
                                                                               screen_name_of_new_asset)
                            OTLLogger.logger.debug(js_code)
                            webview.page().runJavaScript(js_code)
                            # point the original relation to the collection instead of its intended target
                            collect_id_to_original_asset_id_dict[collection_id] = add_edge_arguments["from_id"]
                            add_edge_arguments["from_id"] = collection_id

                        elif special_edge["to"] == add_edge_arguments["to_id"]:
                            # is this case:
                            # special_edge["to"] is the id of the asset that has relations to many assets
                            collection_id = special_edge["from"]  # special_edge["from"] is the id of the collection_node
                            try:
                                screen_name_of_new_asset = vis_wrap.asset_id_to_display_name_dict[add_edge_arguments["from_id"]]
                            except:
                                OTLLogger.logger.debug(f"Couldn't find display name of node id: {add_edge_arguments['from_id']}\n Needs refresh")
                                screen_name_of_new_asset = vis_wrap.asset_id_to_display_name_dict[collect_id_to_original_asset_id_dict[add_edge_arguments["from_id"]]]
                            added_to_collection = True
                            js_code = cls.create_js_code_to_add_to_collection(vis_wrap,
                                                                               collection_id,
                                                                               rel_id,
                                                                               screen_name_of_new_asset)
                            OTLLogger.logger.debug(js_code)
                            webview.page().runJavaScript(js_code)
                            # point the original relation to the collection instead of its intended target
                            collect_id_to_original_asset_id_dict[collection_id] = \
                            add_edge_arguments["to_id"]
                            add_edge_arguments["to_id"] = collection_id

                if not added_to_collection:
                    js_bool_hidden = "false"
                    rel_type = relation_object.typeURI
                    if rel_type in relation_visible_dict.keys() and not relation_visible_dict[rel_type]:
                        js_bool_hidden = "true"

                    js_code = f'AddEdgeWithLabel("{add_edge_arguments["id"]}","{add_edge_arguments["from_id"]}", "{add_edge_arguments["to_id"]}","{add_edge_arguments["color"]}","{add_edge_arguments["arrow"]}","{add_edge_arguments["label"]}", {js_bool_hidden})'
                    OTLLogger.logger.debug(js_code)
                    webview.page().runJavaScript(js_code)
                else:
                    js_code = f'\nAddEdgeWithLabel("{add_edge_arguments["id"]}","{add_edge_arguments["from_id"]}", "{add_edge_arguments["to_id"]}","{add_edge_arguments["color"]}","{add_edge_arguments["arrow"]}","{add_edge_arguments["label"]}", true)'
                    OTLLogger.logger.debug(js_code)
                    webview.page().runJavaScript(js_code)

            elif "arrow" in add_edge_arguments:  # a directional relation
                # first check if the new relation needs to be added to a current collection
                added_to_collection = False
                for special_edge in vis_wrap.special_edges:
                    # first check if the new relation is the same type as the special edge
                    if (special_edge["arrows"] == add_edge_arguments["arrow"] and
                            special_edge["color"] == add_edge_arguments["color"]):
                        if special_edge["from"] == add_edge_arguments["from_id"]:
                            # is this case:
                            # special_edge["from"] is the id of the asset that has relations to many assets
                            collection_id = special_edge[
                                "to"]  # special_edge["to"] is the id of the collection_node
                            try:
                                screen_name_of_new_asset = \
                                    vis_wrap.asset_id_to_display_name_dict[
                                        add_edge_arguments["to_id"]]
                            except:
                                OTLLogger.logger.debug(f"Couldn't find display name of node id: {add_edge_arguments['to_id']}\n Needs refresh")
                                screen_name_of_new_asset = vis_wrap.asset_id_to_display_name_dict[collect_id_to_original_asset_id_dict[add_edge_arguments["to_id"]]]


                            added_to_collection = True
                            js_code = cls.create_js_code_to_add_to_collection(vis_wrap,
                                                                               collection_id,
                                                                               rel_id,
                                                                               screen_name_of_new_asset)
                            OTLLogger.logger.debug(js_code)
                            webview.page().runJavaScript(js_code)
                            # point the original relation to the collection instead of its intended target
                            collect_id_to_original_asset_id_dict[collection_id] = \
                                add_edge_arguments["to_id"]
                            add_edge_arguments["from_id"] = collection_id
                        elif special_edge["to"] == add_edge_arguments["to_id"]:
                            # is this case:
                            # special_edge["to"] is the id of the asset that has relations to many assets
                            collection_id = special_edge[
                                "from"]  # special_edge["from"] is the id of the collection_node
                            try:
                                screen_name_of_new_asset = \
                                    vis_wrap.asset_id_to_display_name_dict[
                                        add_edge_arguments["from_id"]]
                            except:
                                OTLLogger.logger.debug(
                                f"Couldn't find display name of node id: {add_edge_arguments['from_id']}\n Needs refresh")
                                screen_name_of_new_asset = vis_wrap.asset_id_to_display_name_dict[collect_id_to_original_asset_id_dict[add_edge_arguments["from_id"]]]
                            added_to_collection = True
                            js_code = cls.create_js_code_to_add_to_collection(vis_wrap,
                                                                               collection_id,
                                                                               rel_id,
                                                                               screen_name_of_new_asset)
                            OTLLogger.logger.debug(js_code)
                            webview.page().runJavaScript(js_code)
                            # point the original relation to the collection instead of its intended target
                            collect_id_to_original_asset_id_dict[collection_id] = \
                                add_edge_arguments["to_id"]
                            add_edge_arguments["to_id"] = collection_id

                if not added_to_collection:
                    js_bool_hidden = "false"
                    rel_type = relation_object.typeURI
                    if rel_type in relation_visible_dict.keys() and not relation_visible_dict[
                        rel_type]:
                        js_bool_hidden = "true"
                    js_code = f'AddEdge("{add_edge_arguments["id"]}","{add_edge_arguments["from_id"]}", "{add_edge_arguments["to_id"]}","{add_edge_arguments["color"]}","{add_edge_arguments["arrow"]}", {js_bool_hidden});'
                    OTLLogger.logger.debug(js_code)
                    webview.page().runJavaScript(js_code)
                else:
                    js_code = f'AddEdge("{add_edge_arguments["id"]}","{add_edge_arguments["from_id"]}", "{add_edge_arguments["to_id"]}","{add_edge_arguments["color"]}","{add_edge_arguments["arrow"]}", true);'
                    OTLLogger.logger.debug(js_code)
                    webview.page().runJavaScript(js_code)
            else:  # a bidirectional relation
                # first check if the new relation needs to be added to a current collection
                added_to_collection = False

                for special_edge in vis_wrap.special_edges:
                    # first check if the new relation is the same type as the special edge
                    if (special_edge["color"] == add_edge_arguments["color"]):
                        if (special_edge["from"] == add_edge_arguments["from_id"] or
                                special_edge["from"] == add_edge_arguments["to_id"]):
                            # is this case:
                            # special_edge["from"] is the id of the asset that has relations to many assets
                            collection_id = special_edge["to"]  # special_edge["to"] is the id of the collection_node

                            if special_edge["from"] == add_edge_arguments["to_id"]:
                                try:
                                    screen_name_of_new_asset = \
                                        vis_wrap.asset_id_to_display_name_dict[
                                            add_edge_arguments["from_id"]]
                                except:
                                    OTLLogger.logger.debug(
                                        f"Couldn't find display name of node id: {add_edge_arguments['from_id']}\n Needs refresh")
                                    OTLLogger.logger.debug(
                                        f"add_edge_arguments[\"from_id\"]: {add_edge_arguments['from_id']}\ncollect_id_to_original_asset_id_dict: {collect_id_to_original_asset_id_dict}\n  vis_wrap.asset_id_to_display_name_dict: {vis_wrap.asset_id_to_display_name_dict}")

                                    screen_name_of_new_asset = \
                                    vis_wrap.asset_id_to_display_name_dict[
                                        collect_id_to_original_asset_id_dict[add_edge_arguments["from_id"]]]
                            elif special_edge["from"] == add_edge_arguments["from_id"]:
                                try:
                                    screen_name_of_new_asset = \
                                        vis_wrap.asset_id_to_display_name_dict[
                                            add_edge_arguments["to_id"]]

                                except:
                                    OTLLogger.logger.debug(
                                    f"Couldn't find display name of node id: {add_edge_arguments['to_id']}\n Needs refresh")
                                    OTLLogger.logger.debug(
                                        f"add_edge_arguments[\"to_id\"]: {add_edge_arguments['to_id']}\ncollect_id_to_original_asset_id_dict: {collect_id_to_original_asset_id_dict}\n  vis_wrap.asset_id_to_display_name_dict: {vis_wrap.asset_id_to_display_name_dict}")

                                    screen_name_of_new_asset = vis_wrap.asset_id_to_display_name_dict[collect_id_to_original_asset_id_dict[add_edge_arguments["to_id"]]]
                            added_to_collection = True
                            js_code =  cls.create_js_code_to_add_to_collection(vis_wrap,
                                                                               collection_id,
                                                                               rel_id,
                                                                               screen_name_of_new_asset)
                            OTLLogger.logger.debug(js_code)
                            webview.page().runJavaScript(js_code)
                            # point the original relation to the collection instead of its intended target
                            # collect_id_to_original_asset_id_dict[collection_id] = \
                            #     special_edge["from"]
                            if special_edge["from"] == add_edge_arguments["to_id"]:
                                add_edge_arguments["to_id"] = collection_id
                                collect_id_to_original_asset_id_dict[collection_id] = \
                                    add_edge_arguments["to_id"]
                            elif special_edge["from"] == add_edge_arguments["from_id"]:
                                add_edge_arguments["from_id"] = collection_id
                                collect_id_to_original_asset_id_dict[collection_id] = \
                                    add_edge_arguments["from_id"]

                        elif special_edge["to"] == add_edge_arguments["to_id"] or special_edge["to"] == add_edge_arguments["from_id"]:
                            # is this case:
                            # special_edge["to"] is the id of the asset that has relations to many assets
                            collection_id = special_edge["from"]  # special_edge["from"] is the id of the collection_node

                            if special_edge["to"] == add_edge_arguments["to_id"]:
                                try:
                                    screen_name_of_new_asset = \
                                        vis_wrap.asset_id_to_display_name_dict[
                                            add_edge_arguments["from_id"]]
                                except:
                                    OTLLogger.logger.debug(
                                        f"Couldn't find display name of node id: {add_edge_arguments['from_id']}\n Needs refresh")
                                    OTLLogger.logger.debug(
                                        f"add_edge_arguments[\"from_id\"]: {add_edge_arguments['from_id']}\ncollect_id_to_original_asset_id_dict: {collect_id_to_original_asset_id_dict}\n  vis_wrap.asset_id_to_display_name_dict: {vis_wrap.asset_id_to_display_name_dict}")
                                    screen_name_of_new_asset = \
                                    vis_wrap.asset_id_to_display_name_dict[
                                        collect_id_to_original_asset_id_dict[
                                            add_edge_arguments["from_id"]]]

                            elif special_edge["to"] == add_edge_arguments["from_id"]:
                                try:
                                    screen_name_of_new_asset = \
                                        vis_wrap.asset_id_to_display_name_dict[
                                            add_edge_arguments["to_id"]]
                                except:
                                    OTLLogger.logger.debug(
                                        f"Couldn't find display name of node id: {add_edge_arguments['to_id']}\n Needs refresh")
                                    OTLLogger.logger.debug(
                                        f"add_edge_arguments[\"to_id\"]: {add_edge_arguments['to_id']}\ncollect_id_to_original_asset_id_dict: {collect_id_to_original_asset_id_dict}\n  vis_wrap.asset_id_to_display_name_dict: {vis_wrap.asset_id_to_display_name_dict}")
                                    screen_name_of_new_asset = \
                                    vis_wrap.asset_id_to_display_name_dict[
                                        collect_id_to_original_asset_id_dict[
                                            add_edge_arguments["to_id"]]]



                            added_to_collection = True
                            js_code = cls.create_js_code_to_add_to_collection(vis_wrap,
                                                                               collection_id,
                                                                               rel_id,
                                                                               screen_name_of_new_asset)
                            OTLLogger.logger.debug(js_code)
                            webview.page().runJavaScript(js_code)
                            # point the original relation to the collection instead of its intended target
                            # collect_id_to_original_asset_id_dict[collection_id] = \
                            #     special_edge["to"]
                            if special_edge["to"] == add_edge_arguments["to_id"]:
                                collect_id_to_original_asset_id_dict[collection_id] = \
                                    add_edge_arguments["to_id"]
                                add_edge_arguments["to_id"] = collection_id
                            elif special_edge["to"] == add_edge_arguments["from_id"]:
                                collect_id_to_original_asset_id_dict[collection_id] = \
                                    add_edge_arguments["from_id"]
                                add_edge_arguments["from_id"] = collection_id


                if not added_to_collection:
                    js_bool_hidden = "false"
                    rel_type = relation_object.typeURI
                    if rel_type in relation_visible_dict.keys() and not relation_visible_dict[
                        rel_type]:
                        js_bool_hidden = "true"
                    js_code = f'AddEdge("{add_edge_arguments["id"]}","{add_edge_arguments["from_id"]}", "{add_edge_arguments["to_id"]}","{add_edge_arguments["color"]}",null, {js_bool_hidden});'
                    OTLLogger.logger.debug(js_code)
                    webview.page().runJavaScript(js_code)
                else:
                    js_code = f'\nAddEdge("{add_edge_arguments["id"]}","{add_edge_arguments["from_id"]}", "{add_edge_arguments["to_id"]}","{add_edge_arguments["color"]}",null, true);'
                    OTLLogger.logger.debug(js_code)
                    webview.page().runJavaScript(js_code)


    @classmethod
    def create_js_code_to_add_to_collection(cls, vis_wrap, collection_id, rel_id,
                                            screen_name_of_new_asset):
        new_rel_id_and_asset_screen_name_set = (rel_id, screen_name_of_new_asset)
        vis_wrap.relation_id_to_collection_id[rel_id].append(collection_id)
        vis_wrap.collection_id_to_list_of_relation_ids[
            collection_id].append(new_rel_id_and_asset_screen_name_set)
        new_label, new_title = cls.create_new_special_node_text(collection_id, vis_wrap)

        js_code = f'UpdateCollectionAttributes("{collection_id}", "{new_label}","{new_title}",{json.dumps(vis_wrap.collection_id_to_list_of_relation_ids)});'

        return js_code

    @classmethod
    def create_new_special_node_text(cls, collection_id, vis_wrap):
        new_collection_content = "\n".join([rel_set[1] for rel_set in
                                            vis_wrap.collection_id_to_list_of_relation_ids[
                                                collection_id]])
        new_collection_size = len(
            vis_wrap.collection_id_to_list_of_relation_ids[
                collection_id])
        new_label = f"<i><b>Collectie ({new_collection_size})</b></i>"
        new_title = f"Collectie ({new_collection_size}):\n{new_collection_content}"
        # next line is so it can be communicated the to javascript correctly
        new_title = new_title.replace("\n", "\\n")
        return new_label, new_title
