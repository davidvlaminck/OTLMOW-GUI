import asyncio
import base64
import pathlib

from PyQt6.QtCore import QUrl
from folium import folium, JsCode

from otlmow_gui.Domain.logger.OTLLogger import OTLLogger

from shapely.wkt import loads
from pyproj import Transformer


class MapHelper:
    added_layer_asset_id_list = []
    normal_color = "#FF7F00"
    highlight_color = "#004d5c"

    @classmethod
    async def create_html_map(cls,id_to_object_with_text_and_data_dict:dict,IMG_DIR,HTML_DIR,prev_selected_asset_id=None):
        m = cls.create_folium_map()

        OTLLogger.logger.debug(pathlib.Path.home().drive)
        OTLLogger.logger.debug(IMG_DIR)
        OTLLogger.logger.debug(str(
            (IMG_DIR/ "bol_orange.png")))

        img_qurl = QUrl(pathlib.Path.home().drive + str(
            (IMG_DIR / "bol_orange.png").absolute()).replace("\\", "/"))
        img_path = img_qurl.path()

        with open(img_path, 'rb') as img_file:
            b64_data = base64.b64encode(img_file.read()).decode('utf-8')

        # Create the data URL
        data_url = f"data:image/png;base64,{b64_data}"

        click_js = ("function onMapClick(e) {\n"
                    f"var icon_path = '{data_url}';\n ")
        click_js += """
                               
                                var map_id = e.originalEvent.srcElement.id;
                                var lat = e.latlng.lat;
                                var lng = e.latlng.lng;
             
                                //drawPoint(lat,lng,map_id,"","");
                                

                                //console.log(e);-

                                //drawing polygons
                                var lat1 = lat+1;
                                var lng1 = lng+1;

                                //// var latlngs = [[lat, lng],[lat1, lng],[lat1, lng1],[lat, lng1]];// sqaure
                                //// var latlngs = [[lat, lng],[lat1, lng]];// line
                                var latlngs = [[lat, lng],[lat1, lng],[lat1, lng1]];// corner
                                ////var latlngs = [[lat, lng]];// dot
                                //var map = e.originalEvent.srcElement;
                                
                                ////var polygon = L.polygon(latlngs, {color: "red"}).addTo(eval(map_id));
                                //// zoom the map to the polygon
                                ////eval(e.originalEvent.srcElement.id).fitBounds(polygon.getBounds());
                                
                                //drawLines(latlngs, map_id);

                                // Send coordinates to Python
                                //activateHighlightLayer( 'e64e7fcb-d429-4e3d-8651-706297f14ca4-b25kZXJkZWVsI1ZvZXJ0dWlnbGFudGFhcm4');
                                
                            //}
                             activateHighlightLayer( 'a303e80b-9863-4b47-b0c0-dadb8fc9b651-b25kZXJkZWVsI1ZvZXJ0dWlnbGFudGFhcm4');
                            if('a303e80b-9863-4b47-b0c0-dadb8fc9b651-b25kZXJkZWVsI1ZvZXJ0dWlnbGFudGFhcm4' && ('a303e80b-9863-4b47-b0c0-dadb8fc9b651-b25kZXJkZWVsI1ZvZXJ0dWlnbGFudGFhcm4' in idToLayerDict))
                            {
                              eval(map_id).fitBounds(idToLayerDict['a303e80b-9863-4b47-b0c0-dadb8fc9b651-b25kZXJkZWVsI1ZvZXJ0dWlnbGFudGFhcm4'].getBounds());
                              }
                        """

        click_js += "}"
        m.add_js_link(name="QWebChannel_script", url="qrc:///qtwebchannel/qwebchannel.js")
        m.on(click=JsCode(click_js))

        js_webchannel_script =  (f"var mapEl = document.getElementById('{m.get_name()}');\n"
                                f"var icon_path = '{data_url}';\n "
                                 f"var normal_color = '{cls.normal_color}';\n"
                                 f"var highlight_color = '{cls.highlight_color}';\n")
        js_webchannel_script += """
        
        //global state vars
        var previousSelectedId = null;
        var idToLayerDict = {}
        var featureGroup = L.featureGroup()
        
        //turn cursor/mousepointer into crosshair
        mapEl.style.cursor = "crosshair";
        
        // add webchannel to javascript to communicate with python
        try{
            var channel = new QWebChannel(qt.webChannelTransport, function(channel) {
                window.pywebchannel = channel.objects.webBridge;
            });
        } catch (error) {
          console.error(error);
          alert("MapScreen: QWebChannel creation error");
        }
        
        
        function drawLines(latlngs, map_id, text, id)
        {
            var line = L.polyline(latlngs, {color:normal_color, weight:5}).addTo(eval(map_id)).bindPopup(text,{autoPan:false});
            idToLayerDict[id] = line
            line.on('click', function (e)
            {
                //highlight on click
                var layer = e.target;
                activateHighlightLayer(id);
                sendSelectedIdToPython(id);
            
            });
            featureGroup.addLayer(line);
        }
        
        function drawPolygons(latlngs, map_id, text, id)
        {
            var line = L.polygon(latlngs, {color:normal_color, weight:5}).addTo(eval(map_id));
            line.bindPopup(text,{offset:L.point(0,0),autoPan:false})
            idToLayerDict[id] = line;
            line.on('click', function (e)
            {
                //highlight on click
                var layer = e.target;
                activateHighlightLayer(id);
                sendSelectedIdToPython(id);
             
            });
            featureGroup.addLayer(line);
        }
        
        function drawPoint(lat, lng, map_id, text, id)
        {
            var bolIcon = L.icon(
            {
                    iconUrl: icon_path,
                    iconSize:     [15, 15], // size of the icon
                    iconAnchor:   [7.5, 7.5], // point of the icon which will correspond to marker's location
                    popupAnchor:  [0.5, 3] // point from which the popup should open relative to the iconAnchor
            });
            // Add marker dynamically
            var marker = L.marker([lat, lng], {icon: bolIcon}).addTo(eval(map_id))
            .bindPopup(text,{autoPan:false})
            //.openPopup();
            idToLayerDict[id] = marker
           
            // sendCoordinatesToPython(lat,lng);
            marker.on('click', function (e)
            {
                //highlight on click
                var layer = e.target;
                activateHighlightLayer(id);
                sendSelectedIdToPython(id);
           
            });
            featureGroup.addLayer(marker);
        }
        
        function activateHighlightLayer(id)
        {
            if(id in idToLayerDict)
            {
                var layer = idToLayerDict[id];
                var htmlElement = undefined
                if (layer._icon == undefined)
                {
                    //if the visual is line
                    htmlElement = layer._path
                    if(layer.options.color == normal_color)
                    {
                        disablePreviousHighlightLayer();
                        layer.setStyle({color: highlight_color, weight:8})
                        layer.options.color = highlight_color;
                        layer.options.weight = 8;
                        layer.redraw()
                        previousSelectedId = id;
                        layer.openPopup();
                    }
                }
                else
                {
                    //if the visual is marker
                    htmlElement = layer._icon
                
                    if(!L.DomUtil.hasClass(htmlElement, 'dash-border'))
                    {
                        disablePreviousHighlightLayer();
                        L.DomUtil.addClass(htmlElement,'dash-border');
                        previousSelectedId = id
                        layer.openPopup();
                    }
                }
            }
            else
            {
                disablePreviousHighlightLayer();
                previousSelectedId = id
            }    
        }
        
        function sendCoordinatesToPython(lat,lng)
        {
            if (window.pywebchannel) 
            {
                window.pywebchannel.receive_coordinates(JSON.stringify({lat: lat, lng: lng}));
            } 
            else 
            {
                console.log("QWebChannel is not initialized yet.");
                alert("MapScreen: QWebChannel is not initialized");
            }
        }
        
        function sendSelectedIdToPython(id)
        {
            if (window.pywebchannel) 
            {
                window.pywebchannel.receive_selection_id(JSON.stringify({id: id}));
            } 
            else 
            {
                console.log("QWebChannel is not initialized yet.");
            }
        }
        
        function disablePreviousHighlightLayer()
        {
            if(previousSelectedId && (previousSelectedId in idToLayerDict))
            {
                var prevLayer = idToLayerDict[previousSelectedId]
                var prevLayerhtmlElement = undefined
                if (prevLayer._icon == undefined)
                {
                    //if the previous visual is line
                    prevLayer.setStyle({color: normal_color, weight:5})
                    prevLayer.options.color = normal_color
                    prevLayer.options.weight = 5
                    prevLayer.redraw()
                }
                else
                {
                    //if the previous visual is marker
                    prevLayerhtmlElement = prevLayer._icon
                    L.DomUtil.removeClass(prevLayerhtmlElement,'dash-border');
                }
                    
            }
        }
        
        function goToLayer(id, map_id)
        {
            if(id && (id in idToLayerDict))
            {
                var layer = idToLayerDict[id];
                if (layer._icon == undefined)
                {
                    eval(map_id).fitBounds(layer.getBounds(),{maxZoom:20.5});
                }
                else
                {
                    //this means this is a marker (point geometry)
                    eval(map_id).panTo(layer.getLatLng())
                }
            }
        }
        
        
        
            """

        m.get_root().script.add_child(folium.Element(js_webchannel_script))
        marker_count = len(id_to_object_with_text_and_data_dict)
        OTLLogger.logger.debug(f"Adding markers to map ({marker_count} markers",extra={"timing_ref":"adding_marker_to_map"})
        init_script = 'document.addEventListener("DOMContentLoaded", (event) => {\n'
        for id, otl_object_with_text_and_data in id_to_object_with_text_and_data_dict.items():
            await asyncio.sleep(0)
            otl_object = otl_object_with_text_and_data[0]

            text_and_data = otl_object_with_text_and_data[1]

            if hasattr(otl_object, "geometry") and otl_object.geometry:
                if "POINT" in otl_object.geometry:

                    transformed_geometry = MapHelper.convert_wkt_to_wgs84(otl_object.geometry)
                    coord_list = MapHelper.extract_first_level(transformed_geometry)
                    # MapHelper.addProjectedMarker()
                    popup_text = text_and_data["text"].screen_name + "<br>" + text_and_data[
                        "text"].typeURI #+ "<br>" + otl_object.geometry
                    for coord in coord_list:
                        init_script += MapHelper.add_projected_marker(coord, m.get_name(),popup_text, id)

                if "LINESTRING" in otl_object.geometry:
                    transformed_geometry = MapHelper.convert_wkt_to_wgs84(otl_object.geometry)
                    coord_list = MapHelper.extract_first_level(transformed_geometry)

                    popup_text = text_and_data["text"].screen_name + "<br>" + text_and_data[
                        "text"].typeURI #+ "<br>" + otl_object.geometry
                    for pair in coord_list:
                        init_script += MapHelper.add_projected_line(pair.split(","), m.get_name(),popup_text, id)

                if "POLYGON" in otl_object.geometry:
                    transformed_geometry = MapHelper.convert_wkt_to_wgs84(otl_object.geometry)
                    polygon_list = MapHelper.extract_first_level(transformed_geometry)
                    coord_list = []
                    for polygon in polygon_list:
                        second_level_list = MapHelper.extract_first_level(polygon)
                        for coordinates in second_level_list:
                            coord_list.append(coordinates.split(","))

                    popup_text = text_and_data["text"].screen_name + "<br>" + text_and_data[
                        "text"].typeURI
                    init_script += MapHelper.add_projected_polygon(coord_list, m.get_name(),
                                                                popup_text, id)

        OTLLogger.logger.debug(f"Added markers to map ({marker_count} markers",
                               extra={"timing_ref": "adding_marker_to_map"})
        init_script += cls.get_zoom_to_assets_js_code(map_id=m.get_name(), prev_selected_asset_id=prev_selected_asset_id)
        init_script += "});"

        # make highlight style when clicked
        m.get_root().script.add_child(folium.Element(init_script))
        dash_style = ("""
        <style>
        .dash-border {"""
            f"border: 2px dashed {cls.highlight_color};"
            f"background-color: {cls.highlight_color};"
        """}
        
        
        </style>
        """)
        m.get_root().header.add_child(folium.Element(dash_style))

        map_path = cls.get_map_html_save_path(HTML_DIR, IMG_DIR)
        m.save(map_path)
        map_id = m.get_name()
        map = m
        return map_path, map , map_id

    @classmethod
    def get_map_html_save_path(cls, HTML_DIR: pathlib.Path, IMG_DIR: pathlib.Path) -> str:
        html_dir = IMG_DIR.parent / 'html'
        if not html_dir.exists():
            html_dir = HTML_DIR

        return str((html_dir / "folium_map.html").absolute())

    @classmethod
    def create_folium_map(cls):
        coordinate = (51.16872907594677, 4.41375968966803)# antwerpen
        cls.added_layer_asset_id_list.clear()
        # satelite image layer from google maps instead of open street road map
        tile = folium.TileLayer(
            tiles='https://geo.api.vlaanderen.be/OMW/wmts?SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&LAYER=omwrgb24vl&STYLE=&FORMAT=image/png&TILEMATRIXSET=GoogleMapsVL&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}',
            attr='GRB',
            name='GRB Satellite',
            maxZoom=23,
            maxNativeZoom=21,
            overlay=False,
            control=True
        )
        return folium.Map(
            zoom_start=13,
            location=coordinate,
            tiles=tile
        )

    @classmethod
    def add_marker(cls, lat, lon, map_id, web_view):
        """Adds a marker dynamically without reloading the map."""
        # js_code = f'L.marker([{lat}, {lon}]).addTo({self.map_id}).bindPopup("Marker at {lat}, {lon}").openPopup();'
        """add a polygon sqaure to the map and go to it"""
        insert = '{color: "red"}'
        # js_code =f'var polyline = L.polygon([[{lat}, {lon}],[{lat+1}, {lon}],[{lat+1}, {lon+1}],[{lat}, {lon+1}]],{insert} ).addTo(eval({self.map_id}));\neval({self.map_id}).fitBounds(polyline.getBounds());'
        js_code = f"drawPoint({lat},{lon},{map_id},"");"
        web_view.page().runJavaScript(js_code)

    @classmethod
    def add_projected_marker(cls, coord:str, map_id:str, tooltip_text:str,id:str):
        """Adds a marker dynamically without reloading the map."""

        js_code = (f"var split = '{coord}'.split(' ');\n"
            "var point = L.CRS.EPSG3857.unproject(L.point([parseFloat(split[0]), parseFloat(split[1])] ));\n"
                   f"drawPoint(point.lat,point.lng,'{map_id}','{tooltip_text}','{id}');\n")

        cls.added_layer_asset_id_list.append(id)

        return js_code

    @classmethod
    def add_projected_line(cls, coord_pair: str, map_id: str, tooltip_text: str, id: str):
        """Adds a marker dynamically without reloading the map."""

        js_code = (f"var split_pair = {coord_pair}\n"
                   "latlngs = [];\n"
                   "for (const  coord of split_pair) \n"
                   "{\n"
                   "    //console.log(coord);\n"
                   "    var split = coord.trim().split(' ');\n"
                   "    var point = L.CRS.EPSG3857.unproject(L.point([parseFloat(split[0].trim()), parseFloat(split[1].trim())] ));\n"
                   "    //console.log(point);\n"
                   "    latlngs.push([point.lat,point.lng]);\n"
                   "}\n"
                    f"drawLines(latlngs,'{map_id}','{tooltip_text}','{id}');\n")

        cls.added_layer_asset_id_list.append(id)

        return js_code

    @classmethod
    def add_projected_polygon(cls, coord_pair: list, map_id: str, tooltip_text: str, id: str):
        """Adds a marker dynamically without reloading the map."""

        js_code = (f"var polygons = {coord_pair}\n"
                   "for (const  split_pair of polygons) \n"
                   "{\n"
                       "    latlngs = [];\n"
                       "    for (const  coord of split_pair) \n"
                       "    {\n"
                       "        //console.log(coord);\n"
                       "        var split = coord.trim().split(' ');\n"
                       "        var point = L.CRS.EPSG3857.unproject(L.point([parseFloat(split[0].trim()), parseFloat(split[1].trim())] ));\n"
                       "        //console.log(point);\n"
                       "        latlngs.push([point.lat,point.lng]);\n"
                       "    }\n"
                       f"   drawPolygons(latlngs,'{map_id}','{tooltip_text}','{id}');\n"
                    "}\n")
        cls.added_layer_asset_id_list.append(id)

        return js_code

    @classmethod
    def activate_highlight_layer_by_id(cls, asset_id, web_view,map_id):

        js_code = ( f"activateHighlightLayer( '{asset_id}');\n"
                    f"goToLayer('{asset_id}', '{map_id}');\n")

        web_view.page().runJavaScript(js_code)

    @classmethod
    def extract_first_level(cls,s):
        results = []
        level = 0
        start = None
        for i, char in enumerate(s):
            if char == '(':
                level += 1
                if level == 1:  # starting a new top-level group
                    start = i + 1  # content starts after the '('
            elif char == ')':
                if level == 1 and start is not None:
                    results.append(s[start:i])
                level -= 1
        return results

    @classmethod
    def convert_wkt_to_wgs84(cls,wkt_string):
        # Load the geometry from the WKT string
        geometry = loads(wkt_string)

        # Define the source CRS (EPSG:31370)
        source_crs = 'EPSG:31370'

        # Define the target CRS (WGS84)
        target_crs = 'EPSG:3857'

        transformer = Transformer.from_crs(crs_from=source_crs, crs_to=target_crs)
        # Transform the coordinates
        if geometry.geom_type == 'Point':
            x, y = geometry.x, geometry.y


            transformer.transform(12, 12)
            lon, lat = transformer.transform( x, y)
            return f'POINT ({lon} {lat})'

        elif geometry.geom_type in ['LineString', 'MultiPoint']:
            transformed_coords = [
                transformer.transform( x, y) for x, y, z in geometry.coords
            ]
            return f'LINESTRING ({", ".join(f"{lon} {lat}" for lon, lat in transformed_coords)})'

        elif geometry.geom_type in ['Polygon', 'MultiLineString']:
            transformed_coords = [
                transformer.transform( x, y) for x, y,z in geometry.exterior.coords
            ]
            return f'POLYGON (({" , ".join(f"{lon} {lat}" for lon, lat in transformed_coords)}))'

        elif geometry.geom_type == 'MultiPolygon':
            transformed_polygons = []
            for polygon in geometry.geoms:
                transformed_coords = [
                    transformer.transform( x, y) for x, y in polygon.exterior.coords
                ]
                transformed_polygons.append(
                    f'POLYGON (({" , ".join(f"{lon} {lat}" for lon, lat in transformed_coords)}))')
            return f'MULTIPOLYGON ({", ".join(transformed_polygons)})'

        else:
            raise ValueError(f"Unsupported geometry type: {geometry.geom_type}")

    @classmethod
    def zoom_to_assets(cls,web_view,map_id, prev_selected_asset_id=None):
        js_code = cls.get_zoom_to_assets_js_code(map_id=map_id,prev_selected_asset_id=prev_selected_asset_id)
        web_view.page().runJavaScript(js_code)

    @classmethod
    def get_zoom_to_assets_js_code(cls,map_id, prev_selected_asset_id):
        js_code = f"var previousSelectedId = '{prev_selected_asset_id}'"
        js_code += ("""
                  if(previousSelectedId && previousSelectedId in idToLayerDict)
                  {
                      activateHighlightLayer(previousSelectedId)
                  """)
        js_code += f"eval('{map_id}').fitBounds(idToLayerDict[previousSelectedId].getBounds());"
        js_code += ("""
                  }
                  else if(featureGroup)
                  {
                 """)
        js_code += f"eval('{map_id}').fitBounds(featureGroup.getBounds());"
        js_code +="}"

        return js_code

