# Drones
Scripts de python y Arduino para proyecto de drones en agricultura


## Mapas (Python)

Este script fue hecho en Python 3.4 con el paquete de Python Científico [Anaconda](https://www.continuum.io/downloads "Anaconda").
Para el script de **mapas** es necesario descargar algunos módulos, si se usa Anaconda es fácil pues el mismo package manager se encarga de descargar dependencias, sólo es necesario correr lo siguiente:

* `conda install gdal`
* `conda install numpy`
* `conda install bokeh`
* `conda install matplotlib`
* `conda install utm`

Hay que notar que es posible no necesitar instalar matplotlib y numpy si se instala bokeh con Anaconda ya que se encargará de instalarlos si no los encuentra. Adicionalmente, puede que algunos de los paquetes no esten en los repositorios de Anaconda, caso en el cual se deben instalar con **pip**, el cual viene instalado junto a Anaconda.

Si se usa pip se necesita instalar los mismos paquetes y la forma de hacerlo es muy similar:

* `pip install [paquete]`

La única diferencia es que pip no instala dependencias entonces hay que leer con cuidado la documentación de los paquetes [gdal](https://pypi.python.org/pypi/GDAL/ "gdal"), [bokeh](http://bokeh.pydata.org/en/latest/docs/installation.html "bokeh"), [matplotlib](http://matplotlib.org/ "matplotlib"), [numpy](http://www.numpy.org/ "numpy") y [UTM](https://pypi.python.org/pypi/utm "UTM").

## LIDAR

### Python

Se usó un Raspberry Pi 2 para leer datos del LiDar por medio del UART, GPS por medio de USB e IMU por medio de I2C. El código está hecho en Python 2.7 y está diseñado para correr de manera automática cuando se enciende el RPi. Adicionalmente, se usa el módulo de pigpio para tener acceso y control sobre los puertos de salida y entrada del RPi, las versiones más nuevas de las imágenes de Raspbian ya deben de tener la librería instalada, si se usa otra imagen o una versión vieja de Raspbian, se puede descargar (así como consultar la documentación) [aquí](http://abyz.co.uk/rpi/pigpio/index.html "aquí"). Para poder correr pigpio desde que se enciende el RPi, es necesario inicializar el daemon automáticamente, para lograr esto se abre una terminal y se escribe:

```
sudo crontab -e
```
Se selecciona la opción 2 para editar con nano (o se escoje el editor con el que se esté más cómodo). Al final del archivo que se abrirá agregar la siguiente línea:

```
@reboot /usr/bin/pigpiod
```

Para configurar el script de python para que corra automáticamente al encender el RPi, se siguieron las instrucciones [aquí](http://www.instructables.com/id/Raspberry-Pi-Launch-Python-script-on-startup/ "aquí"). Agregar las líneas de crontab después de la línea que ya se hizo inicializando el daemon de pigpio.

A pesar de que el LiDar y el GPS se pueden usar conectándolos directamente al RPi, para el IMU es necesario usar los scripts para el MPU6050 escritos por Stefan Kolla (basada en la librería original de [Jeff Rowberg](http://www.i2cdevlib.com/devices/mpu6050#source "Jeff Rowberg")) para poder usarlo con Python en el RPi. Estos scripts se pueden descargar de [aquí](https://github.com/cTn-dev/PyComms "aquí"). En total se necesitan descargar tres (y deben estar en la misma carpeta): 
* `pycomms.py`
* `mpu6050.py`
* `6axis_dmp.py`

Adicionalmente, se necesita cambiar en pycomms.py el puerto SMBus dependiendo del IMU que se use, en el caso de este proyecto era un IMU revisión 2, por lo que se cambió el parámetro de SMBus(0) a SMBus(1), si el IMU es revisión 1 entonces no se necesita hacer este cambio. El MPU 6050 cuenta con un DMP (digital motion processor) que permite la fusión de roll y pitch y hace los cálculos para determinar el yaw en el mismo chip, para no gastar recursos de procesamiento en el microcontrolador para hacer estos cálculos. Por último, se controla también un motor por medio de un ESC, el cual recibe una señal igual a la de un servo motor, proveniente del RPi.
