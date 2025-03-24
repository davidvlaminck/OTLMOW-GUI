import base64
import pathlib

from PyQt6.QtCore import QUrl
from folium import folium, JsCode

from Domain.logger.OTLLogger import OTLLogger

from shapely.wkt import loads
from pyproj import Proj, transform


class MapHelper:
    @classmethod
    def create_html_map(self,id_to_object_with_text_and_data_dict:dict,ROOT_DIR,HTML_DIR):
        coordinate = (37.8199286, -122.4782551)


        # satelite image layer from google maps instead of open street road map
        tile = folium.TileLayer(
            tiles='http://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}',
            attr='Google',
            name='Google Satellite',
            maxZoom= 20,
            maxNativeZoom= 18,
            overlay=False,
            control=True
        )

        m = folium.Map(
            zoom_start=13,
            location=coordinate,
            tiles=tile
        )
        img_qurl = QUrl(pathlib.Path.home().drive + str(
            (ROOT_DIR.parent.parent / "img" / "bol.png").absolute()).replace("\\", "/"))
        img_path = img_qurl.path()

        with open(img_path, 'rb') as img_file:
            b64_data = base64.b64encode(img_file.read()).decode('utf-8')

        # Create the data URL
        data_url = f"data:image/png;base64,{b64_data}"

        OTLLogger.logger.debug({data_url})
        click_js = ("function onMapClick(e) {\n"
                    f"var icon_path = '{data_url}';\n ")
        click_js += """
                                console.log(icon_path)
                                var map_id = e.originalEvent.srcElement.id;
                                var lat = e.latlng.lat;
                                var lng = e.latlng.lng;
                                console.log("Map clicked at: " + lat + ", " + lng);
                                drawPoint(lat,lng,map_id,"","");
                                

                                console.log(e);

                                //drawing polygons
                                var lat1 = lat+1;
                                var lng1 = lng+1;

                                //// var latlngs = [[lat, lng],[lat1, lng],[lat1, lng1],[lat, lng1]];// sqaure
                                //// var latlngs = [[lat, lng],[lat1, lng]];// line
                                var latlngs = [[lat, lng],[lat1, lng],[lat1, lng1]];// corner
                                ////var latlngs = [[lat, lng]];// dot
                                //var map = e.originalEvent.srcElement;
                                
                                ////var polygon = L.polygon(latlngs, {color: "red"}).addTo(eval(e.originalEvent.srcElement.id));
                                //// zoom the map to the polygon
                                ////eval(e.originalEvent.srcElement.id).fitBounds(polygon.getBounds());
                                
                                drawLines(latlngs, map_id);

                                // Send coordinates to Python
                                
                            }

                        """
        m.add_js_link(name="QWebChannel_script", url="qrc:///qtwebchannel/qwebchannel.js")
        m.on(click=JsCode(click_js))

        js_webchannel_script =  (f"var mapEl = document.getElementById('{m.get_name()}');\n"
                                f"var icon_path = '{data_url}';\n ")
        js_webchannel_script += """
        
        //global state vars
        var previousSelectedTarget = null;
        
        //turn cursor/mousepointer into crosshair
        mapEl.style.cursor = "crosshair";
        
        // add webchannel to javascript to communicate with python
        try{
            var channel = new QWebChannel(qt.webChannelTransport, function(channel) {
                window.pywebchannel = channel.objects.webBridge;
            });
        } catch (error) {
          console.error(error);
        }
        
        
        function drawLines(latlngs,map_id)
        {
            L.polyline(latlngs, {color: "red"}).addTo(eval(map_id));
        }
        
        function drawPoint(lat,lng,map_id,text,id)
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
            .bindPopup(text)
            .openPopup();
            console.log("send coordinates to python");
            sendCoordinatesToPython(lat,lng);
            marker.on('click', function (e)
            {
                //highlight on click
                var layer = e.target;
                if(!L.DomUtil.hasClass(layer._icon, 'dash-border'))
                {
                    if(previousSelectedTarget)
                    {
                        L.DomUtil.removeClass(previousSelectedTarget._icon,'dash-border');
                    }
                    L.DomUtil.addClass(layer._icon,'dash-border');
                    sendSelectedIdToPython(id);
                }
            });
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
        
        
        
            """

        m.get_root().script.add_child(folium.Element(js_webchannel_script))


        init_script = 'document.addEventListener("DOMContentLoaded", (event) => {'
        for id, otl_object_with_text_and_data in id_to_object_with_text_and_data_dict.items():
            otl_object = otl_object_with_text_and_data[0]

            #  {
            #  "text": namedtuple('text', ['typeURI', 'screen_name', 'full_typeURI'])
            #  "data": namedtuple('data', ['selected_object_id','last_added'])
            #  }
            text_and_data = otl_object_with_text_and_data[1]

            if hasattr(otl_object, "geometry") and otl_object.geometry:
                if "POINT" in otl_object.geometry:

                    transformed_geometry = MapHelper.convert_wkt_to_wgs84(otl_object.geometry)
                    OTLLogger.logger.debug(text_and_data["text"].typeURI)
                    OTLLogger.logger.debug(text_and_data["text"].screen_name)
                    coord_list = MapHelper.extract_first_level(transformed_geometry)
                    # MapHelper.addProjectedMarker()
                    for coord in coord_list:
                        popup_text =  text_and_data["text"].screen_name +"<br>" + text_and_data["text"].typeURI +"<br>" + otl_object.geometry
                        init_script += MapHelper.add_projected_marker(coord, m.get_name(),popup_text, id)

        init_script += "});"

        # make highlight style when clicked
        m.get_root().script.add_child(folium.Element(init_script))
        dash_style = """
        <style>
        .dash-border {
            border: 2px dashed #3388ff;
            background-color: #3388ff4d;
        }
        
        
        </style>
        """
        m.get_root().header.add_child(folium.Element(dash_style))

        html_dir = ROOT_DIR.parent.parent / 'img' / 'html'
        if not html_dir.exists():
            html_dir = HTML_DIR
        map_path = str((html_dir / "folium_map.html").absolute())
        m.save(map_path)
        map_id = m.get_name()
        map = m
        return map_path, map , map_id

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
        OTLLogger.logger.debug("called add_projected_marker")
        # js_code = f'L.marker([{lat}, {lon}]).addTo({self.map_id}).bindPopup("Marker at {lat}, {lon}").openPopup();'
        """add a polygon sqaure to the map and go to it"""
        insert = '{color: "red"}'
        # js_code =f'var polyline = L.polygon([[{lat}, {lon}],[{lat+1}, {lon}],[{lat+1}, {lon+1}],[{lat}, {lon+1}]],{insert} ).addTo(eval({self.map_id}));\neval({self.map_id}).fitBounds(polyline.getBounds());'


        js_code = (f"var split = '{coord}'.split(' ');\n"
            "var point = L.CRS.EPSG3857.unproject(L.point([parseFloat(split[0]), parseFloat(split[1])] ));\n"
                   f"drawPoint(point.lat,point.lng,'{map_id}','{tooltip_text}','{id}');\n")

        js_code += ("  if (window.pywebchannel) {\n"
                "window.pywebchannel.receive_coordinates(JSON.stringify({lat: point.lat, lng: point.lng}));\n"
            "} else {\n"
                    " console.log('QWebChannel is not initialized yet.');\n"
            "}\n")

        return js_code


    @classmethod
    def add_projected_marker2(cls, coord, map_id, web_view):
        """Adds a marker dynamically without reloading the map."""
        OTLLogger.logger.debug("called add_projected_marker")

        """add a polygon sqaure to the map and go to it"""
        insert = '{color: "red"}'
        js_code = (f"var split = '{coord}'.split(' ');\n"
                   "var point = L.CRS.EPSG3857.unproject(L.point([parseFloat(split[0]), parseFloat(split[1])] ));\n"
                   f"drawPoint(point.lat,point.lng,'{map_id}','');\n")

        js_code += "sendCoordinatesToPython(point.lat,point.lng)"
        # js_code += ("  if (window.pywebchannel) {\n"
        #         "window.pywebchannel.receive_coordinates(JSON.stringify({lat: point.lat, lng: point.lng}));\n"
        #     "} else {\n"
        #             " console.log('QWebChannel is not initialized yet.');\n"
        #     "}\n")


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
        source_crs = Proj('EPSG:31370')

        # Define the target CRS (WGS84)
        target_crs = Proj('EPSG:3857')

        # Transform the coordinates
        if geometry.geom_type == 'Point':
            x, y = geometry.x, geometry.y
            lon, lat = transform(source_crs, target_crs, x, y)
            return f'POINT ({lon} {lat})'

        elif geometry.geom_type in ['LineString', 'MultiPoint']:
            transformed_coords = [
                transform(source_crs, target_crs, x, y) for x, y in geometry.coords
            ]
            return f'LINESTRING ({", ".join(f"{lon} {lat}" for lon, lat in transformed_coords)})'

        elif geometry.geom_type in ['Polygon', 'MultiLineString']:
            transformed_coords = [
                transform(source_crs, target_crs, x, y) for x, y in geometry.exterior.coords
            ]
            return f'POLYGON (({" , ".join(f"{lon} {lat}" for lon, lat in transformed_coords)}))'

        elif geometry.geom_type == 'MultiPolygon':
            transformed_polygons = []
            for polygon in geometry.geoms:
                transformed_coords = [
                    transform(source_crs, target_crs, x, y) for x, y in polygon.exterior.coords
                ]
                transformed_polygons.append(
                    f'POLYGON (({" , ".join(f"{lon} {lat}" for lon, lat in transformed_coords)}))')
            return f'MULTIPOLYGON ({", ".join(transformed_polygons)})'

        else:
            raise ValueError(f"Unsupported geometry type: {geometry.geom_type}")
