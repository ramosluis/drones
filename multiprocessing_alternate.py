import multiprocessing
from multiprocessing import Process, Queue
from time import sleep
import serial
import time
import math
import mpu6050
import csv
import pigpio

def gpsRead(q):
	while 1:
		q.put([gps.readline()])

def lidarRead(q):
	while 1:
		byte_l = ord(lidar.read(1))
		byte_h = ord(lidar.read(1))
		#print [byte_h, byte_l]
		q.put([byte_h, byte_l])

def imuRead(q):
	while 1:
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
			qx = mpu.getQX(result)
			qy = mpu.getQY(result)
			qz = mpu.getQZ(result)
			qw = mpu.getQW(result)
        #g = mpu.dmpGetGravity(q)
			y = mpu.dmpGetYaw(qx, qy, qw, qz)
			#print y
			q.put(y)

			# ver cuenta del FIFO aqui, en caso de tener mas de 1
			# esto nos permite leer mas sin esperar un interrupt        
			fifoCount -= packetSize


def writeFile(lidar, gps, imu):
	dataFile = open('/home/pi/datalog/'+timestr+'.csv', 'w')
	dataWriter = csv.writer(dataFile)
	data = []
	while 1:
		data.append(lidar.get())
		data.append(imu.get())
		data.append(gps.get())
		pi.write(23, 1)
		dataWriter.writerow([data])
		pi.write(23, 0)
		data[:] = []



if __name__ == '__main__':
	# inicializacion de IMU
	mpu = mpu6050.MPU6050()
	mpu.dmpInitialize()
	mpu.setDMPEnabled(True)

	# get expected DMP packet size for later comparison
	packetSize = mpu.dmpGetFIFOPacketSize() 

	# objeto para manipular GPIO del Pi
	pi = pigpio.pi()

	#variable para tomar la fecha y hora del tiempo del logger
	timestr = time.strftime("%Y_%m_%d-%H_%M_%S")

	gpsQueue = multiprocessing.Queue()
	lidarQueue = multiprocessing.Queue()
	imuQueue = multiprocessing.Queue()

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
	
	Process(target=gpsRead, args=(gpsQueue,)).start()
	Process(target=lidarRead, args=(lidarQueue,)).start()
	Process(target=imuRead, args=(imuQueue,)).start()
	Process(target=writeFile, args=(lidarQueue, gpsQueue, imuQueue,)).start()
