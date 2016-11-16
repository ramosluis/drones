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

Se usó un Raspberry Pi 2 para leer datos del LiDar por medio del UART, GPS por medio de USB e IMU por medio de un Arduino conectado via USB. El código está hecho en Python 2.7 y está diseñado para correr de manera automática cuando se enciende el RPi. Adicionalmente, se usa el módulo de pigpio para tener acceso y control sobre los puertos de salida y entrada del RPi, las versiones más nuevas de las imágenes de Raspbian ya deben de tener la librería instalada, si se usa otra imagen o una versión vieja de Raspbian, se puede descargar (así como consultar la documentación) [aquí](http://abyz.co.uk/rpi/pigpio/index.html "aquí"). Para poder correr pigpio desde que se enciende el RPi, es necesario inicializar el daemon automáticamente, para lograr esto se abre una terminal y se escribe:

```
sudo crontab -e
```
Se selecciona la opción 2 para editar con nano (o se escoje el editor con el que se esté más cómodo). Al final del archivo que se abrirá agregar la siguiente línea:

```
@reboot /usr/bin/pigpiod
```

Para configurar el script de python para que corra automáticamente al encender el RPi, se siguieron las instrucciones [aquí](http://www.instructables.com/id/Raspberry-Pi-Launch-Python-script-on-startup/ "aquí"). Agregar las líneas de crontab después de la línea que ya se hizo inicializando el daemon de pigpio.

### Arduino

Se usó un Arduino UNO para leer los datos del IMU (MPU 6050) y controlar el ESC del motor, el Arduino se alimenta y se comunica con el Raspberry Pi por medio del puerto USB. El MPU 6050 cuenta con un DMP (digital motion processor) que permite la fusión de roll y pitch y hace los cálculos para determinar el yaw en el mismo chip, para no gastar recursos de procesamiento en el microcontrolador para hacer estos cálculos. Sin embargo, no hay documentación sobre cómo se utiliza este módulo, para poderlo usar se necesita importar una librería escrita por Jeff Rowberg. La librería se puede descargar [aquí](http://www.i2cdevlib.com/devices/mpu6050#source "aquí"). 
