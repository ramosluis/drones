# para manejar shapefiles
# para instalar: pip install gdal
from osgeo import ogr, gdal
# para convertir entre coordenadas UTM > LAT_LON
# para instalar: pip install utm
import utm 
import re
# para visualizar en google maps y estadisticas
# NOTA: si se instala con pip no instala dependencias ver http://bokeh.pydata.org/en/latest/docs/installation.html
# pip install bokeh
from bokeh.io import output_file, show
from bokeh.models import (
  GMapPlot, 
  GMapOptions, 
  ColumnDataSource, 
  Circle, 
  DataRange1d, 
  PanTool, 
  WheelZoomTool, 
  BoxSelectTool,
  HoverTool
)

###################################
###################################
#### PREPARACION DE INFORMACION ###
###################################
###################################

# seleccionar shapefile que se va a analizar
shapefile = "C:/Users/Luis/Documents/xantronic/agricultura/vuelos/vuelo_3_25m/vuelo_3_25m/4_index/indices/ndvi/vuelo_3_25m_index_ndvi.shp"

# variables para guardar la informacion
ndvi = []
coords_utm = []
coords = []
latitud = []
longitud = []

# abrimos shapefile y guardamos informacion de NDVI y de coordenadas
driver = ogr.GetDriverByName("ESRI Shapefile")
dataSource = driver.Open(shapefile, 0)
layer = dataSource.GetLayer()

for feature in layer:
    ndvi.append(str(feature.GetField("ndvi")))
    geom = feature.GetGeometryRef()
    coords_utm.append(geom.Centroid().ExportToWkt())


count = 0
# tomar solo los valores de las coordenadas y guardarlas en nuevas variables
for i in coords_utm:
    # tomamos coordenadas como 4 valores, 1 par numeros enteros y 1 par de decimales
    coords.append(re.findall('\d+', coords_utm[count]))
    # hacemos casting como string para agregar punto decimal
    coords[count][0] = str(coords[count][0])+"."+str(coords[count][1])
    coords[count][1] = str(coords[count][2])+"."+str(coords[count][3])
    # poner los valores donde van para facilidad de uso / acceso
    latitud.append(coords[count][0])
    longitud.append(coords[count][1])
    count += 1


# convertir de UTM a LAT-LON
# argumentos de la funcion utm.to_latlon(EASTING, NORTHING, ZONE NUMBER, ZONE LETTER)
# la zona se puede obtener del archivo con extensión PRJ
# y abriéndolo en un editor de texto
count = 0
for i in latitud:
    # la funcion para convertir solo acepta floats como coordenadas...
    coords[count] = utm.to_latlon(float(latitud[count]), float(longitud[count]), 12, 'N')
    # ... pero si se quieren convertir de vuelta a strings usar las siguientes dos lineas
#    latitud[count] = str(coords[count][0])
#    longitud[count] = str(coords[count][1])
    # o dejarlos como floats
    latitud[count] = coords[count][0]
    longitud[count] = coords[count][1]
    count += 1
    


###################################
###################################
#### GRAFICAR Y VISUALIZAR MAPA ###
###################################
###################################

# llave mia (luis) personal e intransferible :^)
# llaves API son gratis de google
# ver https://developers.google.com/maps/documentation/javascript/get-api-key#key
API_KEY = "AIzaSyAIKNV7XZFPkFZFPGeNnnKHfoYwAegTIB0"

# property type: map_type:Enum(‘satellite’, ‘roadmap’, ‘terrain’, ‘hybrid’)
map_options = GMapOptions(lat=latitud[0], lng=longitud[0], map_type="terrain", zoom=16)

plot = GMapPlot(
    x_range=DataRange1d(), y_range=DataRange1d(), map_options=map_options,
    api_key=API_KEY,
)

plot.title.text = "NDVI"

source = ColumnDataSource(
    data=dict(
        x=longitud,
        y=latitud,
        indice=ndvi
    )
)
    
hover = HoverTool(
        tooltips=[
            ("index", "$index"),
            ("(x,y)", "($x, $y)"),
            ("NDVI", "@ndvi"),
        ]
    )

circle = Circle(x="x", y="y", size=5, fill_color="blue", fill_alpha=0.8, line_color=None)
plot.add_glyph(source, circle)

plot.add_tools(PanTool(), WheelZoomTool(), BoxSelectTool(), HoverTool())

output_file("gmap_plot.html")
show(plot)
