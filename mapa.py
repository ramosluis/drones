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
  HoverTool,
)

# para el HoverTool
from collections import OrderedDict

###################################
###################################
#### PREPARACION DE INFORMACION ###
###################################
###################################

# seleccionar shapefile que se va a analizar
#shapefile = "C:/Users/Luis/Documents/xantronic/agricultura/vuelos/vuelo_3_25m/vuelo_3_25m/4_index/indices/ndvi/vuelo_3_25m_index_ndvi.shp"
shapefile = "C:/Users/Luis/Documents/xantronic/agricultura/vuelos/test/4_index/indices/ndvi/test_index_ndvi.shp"
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
    ndvi.append(float(feature.GetField("ndvi")))
    geom = feature.GetGeometryRef()
    coords_utm.append(geom.Centroid().ExportToWkt())



# tomar solo los valores de las coordenadas y guardarlas en nuevas variables
for i in range(0, len(coords_utm)):
    # tomamos coordenadas como 4 valores, 1 par numeros enteros y 1 par de decimales
    coords.append(re.findall('\d+', coords_utm[i]))
    # hacemos casting como string para agregar punto decimal
    coords[i][0] = str(coords[i][0])+"."+str(coords[i][1])
    coords[i][1] = str(coords[i][2])+"."+str(coords[i][3])
    # poner los valores donde van para facilidad de uso / acceso
    latitud.append(coords[i][0])
    longitud.append(coords[i][1])


# convertir de UTM a LAT-LON
# argumentos de la funcion utm.to_latlon(EASTING, NORTHING, ZONE NUMBER, ZONE LETTER)
# la zona se puede obtener del archivo con extensión PRJ
# y abriéndolo en un editor de texto
for i in range(0, len(latitud)):
    # la funcion para convertir solo acepta floats como coordenadas...
    coords[i] = utm.to_latlon(float(latitud[i]), float(longitud[i]), 12, 'N')
    # ... pero si se quieren convertir de vuelta a strings usar las siguientes dos lineas
#    latitud[count] = str(coords[count][0])
#    longitud[count] = str(coords[count][1])
    # o dejarlos como floats
    latitud[i] = coords[i][0]
    longitud[i] = coords[i][1]
    

# para generar los colores que se veran en el mapa
colores_ndvi = []

# de aqui en adelante la lista de NDVI debe ser conformada por strings para ver 
# los valores bien en el mapa
for i in range(0, len(ndvi)):
    # si el NDVI es negativo será rojo
    if ndvi[i] < 0:
        colores_ndvi.append("ff0000")
    # si el NDVI es entre 0 y 0.49 será verde claro
    elif ndvi[i] > 0 and ndvi[i] < 0.49:
        colores_ndvi.append("ccff66")
    # si el NDVI es mayor o igual a 0.5 será verde
    else:
        colores_ndvi.append("00cc00")
    ndvi[i] = str(ndvi[i])
    
    
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
map_options = GMapOptions(lat=latitud[0], lng=longitud[0], map_type='hybrid', zoom=16)

# para graficar los valores de NDVI/Coordenadas se usa un tipo de plot especial 
# que usa Google Maps de fondo
plot = GMapPlot(
    x_range=DataRange1d(), y_range=DataRange1d(), map_options=map_options,
    api_key=API_KEY,
    webgl=True,
    lod_threshold=1000,
)

plot.title.text = "NDVI"

# herramientas que habilitamos en el mapa para agregar interactividad
plot.add_tools(PanTool(), WheelZoomTool(), HoverTool())

# la fuente de los datos de nuestra gráfica
source = ColumnDataSource(
    data=dict(
        x=longitud,
        y=latitud,
        indice=ndvi,
        colores=colores_ndvi,
    )
)

# cada valor será representado por un color correspondiente al NDVI
circle = Circle(x="x", y="y", size=5, fill_color="colores", fill_alpha=0.8, line_color=None)

# generar gráfica
plot.add_glyph(source, circle)

hover = plot.select(dict(type=HoverTool))

# aqui seleccionamos qué tooltips queremos que salgan al hacer hover en un punto
hover.tooltips = OrderedDict([
    ("NDVI", "@indice"),
    ("(x,y)", "(@x, @y)"),
])

# guardamos la gráfica como un html para visualizarlo en cualquier navegador
#output_file("gmap_plot.html")
output_file("test_plot.html")
show(plot)
