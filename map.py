from folium import plugins
import folium
import pandas

from templates import template, template2
from branca.element import Template, MacroElement
basemaps = {
    'Google Terrain': folium.TileLayer(
        tiles='https://mts1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}&hl=en',
        attr='Google',
        name='Google Terrain',
        control=True,
        min_zoom=2
    ),
    'Stamen Toner': folium.TileLayer(
        tiles='stamentoner',
        name='Stamen Toner',
        control=True,
        min_zoom=2
    ),
    'Esri Satellite': folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services' +
        '/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Esri Satellite',
        control=True,
        min_zoom=2,
        max_zoom=13
    )
}


def volcano_color_producer(elevation: float) -> str:
    if elevation < 1000:
        return 'green'
    elif elevation < 3000:
        return 'orange'
    else:
        return 'red'


def read_data(filepath):
    data = pandas.read_csv(filepath)
    lats = list(data['Latitude'])
    lons = list(data['Longitude'])
    elevs = list(data['Elev'])
    names = list(data['Volcano Name'])
    statuses = list(data['Status'])
    types = list(data['Type'])
    return lats, lons, elevs, names, statuses, types


def produce_marker(lat, lon, elev, name, status, typ):
    html = f"{str(elev)} m<br><br><b>Name: </b>{name}<br><b>Type: "
    html += f"</b>{typ}<br><b>Status: </b>{status}"
    marker = folium.CircleMarker(
        location=[lat, lon],
        popup=folium.Popup(html=html, sticky=False, max_width=500),
        fill=True,
        fill_color=volcano_color_producer(elev),
        color='grey',
        fill_opacity=0.7,
        radius=10
    )
    return marker


def popula_color(x):
    if x['properties']['POP2005'] < 10000000:
        color = 'green'
    elif 10000000 <= x['properties']['POP2005'] < 20000000:
        color = 'orange'
    else:
        color = 'red'
    return color


def main():
    # Creates map object
    my_map = folium.Map(tiles='openstreetmap', min_zoom=1,
                        max_bounds=True, control_scale=True, control=False)

    # Adds drawing and download feature
    plugins.Draw(
        draw_options={
          'polyline': False,
          'rectangle': True,
          'polygon': True,
          'circle': False,
          'marker': False,
          'circlemarker': False},
        edit_options={'edit': False},
        export=False,
        filename='data.geojson').add_to(my_map)

    # Defines marker cluster
    marker_cluster = plugins.MarkerCluster(overlay=True,
                                           control=True,
                                           show=True,
                                           name='Volcanoes').add_to(my_map)

    # Unpacks volcanos data from csv file
    lats, lons, elevs, names, statuses, types = read_data(
        'data/(1569)volcano.csv')

    # Adds every single volcano to the marker cluster
    for lat, lon, elev, name, status, typ in zip(lats, lons, elevs, names,
                                                 statuses, types):
        produce_marker(lat, lon, elev, name,
                       status, typ).add_to(marker_cluster)

    # Fills with tiles
    for key in basemaps:
        basemaps[key].add_to(my_map)

    # Creates and Adds population group
    fgp = folium.FeatureGroup(name='Population', show=False)

    data = open('data/world.json', 'r', encoding='utf-8-sig')
    fgp.add_child(folium.GeoJson(data=data.read(),
                                 style_function=lambda x: {'fillColor':
                                                           popula_color(x)}
                                 ))
    data.close()

    my_map.add_child(fgp)

    # Adds tiles control
    folium.LayerControl().add_to(my_map)

    # Adds Fullscreen button to map
    plugins.Fullscreen().add_to(my_map)

    # Adds My Location button to map
    plugins.LocateControl().add_to(my_map)

    macro = MacroElement()
    macro._template = Template(template2)
    my_map.get_root().add_child(macro)

    macro = MacroElement()
    macro._template = Template(template)
    my_map.get_root().add_child(macro)

    my_map.save('index.html')
    return


if __name__ == '__main__':
    main()
