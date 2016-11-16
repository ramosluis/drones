import serial
import time
import csv
import pigpio
from time import sleep

# objeto para manipular GPIO del Pi
pi = pigpio.pi()

#variable para tomar la fecha y hora del tiempo del logger
timestr = time.strftime("%Y_%m_%d-%H_%M_%S")

#creamos csv
dataFile = open('/home/pi/Documents/python/datalog/'+timestr+'.csv', 'w')
dataWriter = csv.writer(dataFile)
data = []


# objetos para leer sensores
imu = serial.Serial('/dev/arduinoUNO', 115200, timeout = 1)
sleep(10)
# mandar senal a arduino para iniciar a mover motor
imu.write(".")


gps = serial.Serial(port='/dev/gps',
					baudrate=57600,
					parity=serial.PARITY_NONE,
					stopbits=serial.STOPBITS_ONE,
					bytesize=serial.EIGHTBITS,
					timeout = 1)
					
lidar = serial.Serial('/dev/ttyAMA0', 
						baudrate = 115200,
						bytesize = serial.EIGHTBITS,
						parity = serial.PARITY_NONE,
						stopbits = serial.STOPBITS_ONE)
						


# si no se hace esto el lidar no jala a menos que se cierre el programa y se vuelva a correr
# because f logic
lidar.close()
lidar.open()

while 1:
	# guardamos valores de sensores
	#gps.flushInput()
	x = gps.readline()
	y = imu.readline()
	# los valores del lidar vienen codificados como caracteres ASCII
	# con la funcion ord() los cambiamos a decimal
	data_L = ord(lidar.read(1))
	data_H = ord(lidar.read(1))
	
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
