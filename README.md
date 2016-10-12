# drones
Scripts de python para proyecto de drones en agricultura.


## Dependencias

Estos scripts fueron hechos en Python 3.4 con el paquete de Python Científico [Anaconda](https://www.continuum.io/downloads "Anaconda").
Para el script de **Strong** __mapas__ es necesario descargar algunos módulos, si se usa Anaconda es fácil pues el mismo package manager se encarga de descargar dependencias, sólo es necesario correr lo siguiente:

* `conda install gdal`
* `conda install numpy`
* `conda install bokeh`
* `conda install matplotlib`
* `conda install utm`

Hay que notar que es posible no necesitar instalar matplotlib y numpy si se instala bokeh con Anaconda ya que se encargará de instalarlos si no los encuentra.

Si se usa pip se necesita instalar los mismos paquetes y la forma de hacerlo es muy similar:

* `pip install [paquete]`

La única diferencia es que pip no instala dependencias entonces hay que leer con cuidado la documentación de los paquetes [bokeh](http://bokeh.pydata.org/en/latest/docs/installation.html "bokeh"), [matplotlib](http://matplotlib.org/ "matplotlib"), [numpy](http://www.numpy.org/ "numpy") y [UTM](https://pypi.python.org/pypi/utm "UTM").
