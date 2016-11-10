import serial
import time
import csv
import pigpio
from time import sleep

# objeto para manipular GPIO del Pi
pi = pigpio.pi()

# Para mover el motor via el ESC
#pi.set_servo_pulsewidth(17,0)
#sleep(2)

#pi.set_servo_pulsewidth(17,1000)
#sleep(10)

#pi.set_servo_pulsewidth(17, 1350)

#variable para tomar la fecha y hora del tiempo del logger
timestr = time.strftime("%Y_%m_%d-%H_%M_%S")

#creamos csv
dataFile = open('/home/pi/Documents/python/datalog/'+timestr+'.csv', 'w')
dataWriter = csv.writer(dataFile)
data = []

# objetos para leer sensores
gps = serial.Serial(port='/dev/gps',
					baudrate=57600,
					parity=serial.PARITY_NONE,
					stopbits=serial.STOPBITS_ONE,
					bytesize=serial.EIGHTBITS,
					timeout=1)
					
lidar = serial.Serial('/dev/ttyAMA0', 
						baudrate = 115200,
						bytesize = serial.EIGHTBITS,
						parity = serial.PARITY_NONE,
						stopbits = serial.STOPBITS_ONE)
						

imu = serial.Serial('/dev/arduinoUNO', 115200)

while 1:
	# guardamos valores de sensores
	x = gps.readline()
	y = imu.readline()
	# los valores del lidar vienen codificados como caracteres ASCII
	# con la funcion ord() los cambiamos a decimal
	data_H = ord(lidar.read(1))
	data_L = ord(lidar.read(1))
	# las oraciones que empiezan con $GPRMC y $GPGGA son las que nos dan
	# informacion util del GPS
	if "$GPRMC" in x or "$GPGGA" in x:
		data.append(x)
		data.append(y)
		data.append(data_H)
		data.append(data_L)
		# encendemos LED indicador de escritura de datos
		pi.write(17, 1)
		dataWriter.writerow([data])
		pi.write(17, 0)
		# borramos lista para tomar datos nuevos
		data[:] = []
		# si se comentan las siguientes tres lineas se pueden escribir 
		# 2x la cantidad de datos
		gps.flushInput()
		imu.flushInput()
		lidar.flushInput()
	else:
		# si no entra una de las oraciones del GPS necesarias
		# limpiamos el bufer serial de los datos
		gps.flushInput()
		imu.flushInput()
		lidar.flushInput()
