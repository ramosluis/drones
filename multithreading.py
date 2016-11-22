import serial
import time
import math
import mpu6050
import csv
import pigpio
from threading import Thread
from time import sleep
from os import getpid


def gps_read():
	# guardamos valores de sensores
	while 1:
		gps_data = gps.readline()
		print gps_data

def lidar_read():
	while 1:
		byte_l = ord(lidar.read(1))
		byte_h = ord(lidar.read(1))
	
	print byte_l, byte_h

def imprimir():
	while 1:
		test_string = 'test'
		print test_string


if __name__ == '__main__':
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

	# objeto para manipular GPIO del Pi
	pi = pigpio.pi()
	#variable para tomar la fecha y hora del tiempo del logger
	timestr = time.strftime("%Y_%m_%d-%H_%M_%S")

	#creamos csv
	dataFile = open('/home/pi/Documents/python/datalog/'+timestr+'.csv', 'w')
	dataWriter = csv.writer(dataFile)
	data = []

	t1 = Thread(target = gps_read)
    t2 = Thread(target = lidar_read)
    t3 = Thread(target = imprimir)
    t1.setDaemon(True)
    t2.setDaemon(True)
    t3.setDaemon(True)
    t1.start()
    t2.start()
    t3.start()
    while True:
        pass
