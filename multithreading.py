import serial
import time
import math
import mpu6050
import csv
import pigpio
from threading import Thread
from time import sleep

class gpsRead(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        while True:
			gps_data = gps.readline()
			#print gps_data
			dataWriter.writerow([gps_data])


class lidarRead(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        while True:
			byte_l = ord(lidar.read(1))
			byte_h = ord(lidar.read(1))
			#print byte_l, byte_h
			dataWriter.writerow([byte_l, byte_h])

class imuRead(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        while True:
            # tomar valor de INT_STATUS
			mpuIntStatus = mpu.getIntStatus()
  
			if mpuIntStatus >= 2: # checar que este listo el interrupt de datos del DMP 
				# tomar cuenta actual de FIFO
				fifoCount = mpu.getFIFOCount()
        
				# checar si hay overflow de datos
				if fifoCount == 1024:
					# reinicar conteo
					mpu.resetFIFO()
					# y = 255
            
            
				# esperar para que el paquete de datos sea del tamano correcto
				fifoCount = mpu.getFIFOCount()
				while fifoCount < packetSize:
					fifoCount = mpu.getFIFOCount()
        
				result = mpu.getFIFOBytes(packetSize)
				q = mpu.dmpGetQuaternion(result)
				g = mpu.dmpGetGravity(q)
				ypr = mpu.dmpGetYawPitchRoll(q, g)
        
				y = ypr['yaw']
				#print y
				dataWriter.writerow([y])
				# ver cuenta del FIFO aqui, en caso de tener mas de 1
				# esto nos permite leer mas sin esperar un interrupt        
				fifoCount -= packetSize 	


if __name__ == '__main__':
	# inicializacion de IMU
	mpu = mpu6050.MPU6050()
	mpu.dmpInitialize()
	mpu.setDMPEnabled(True)

	# get expected DMP packet size for later comparison
	packetSize = mpu.dmpGetFIFOPacketSize() 

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
	dataFile = open('/home/pi/datalog/'+timestr+'.csv', 'w')
	dataWriter = csv.writer(dataFile)
	data = []

	# inicializar threads
	gpsRead()
	lidarRead()
	imuRead()
   	while True:
		pass
