from multiprocessing import Process
from time import sleep
from datetime import datetime
import serial
import time
import math
import csv
import pigpio

def gpsRead():
	gps = serial.Serial(port='/dev/gps',
					baudrate=57600,
					parity=serial.PARITY_NONE,
					stopbits=serial.STOPBITS_ONE,
					bytesize=serial.EIGHTBITS,
					timeout = 1)
	#creamos csv
	gpsFile = open('/home/pi/datalog/'+timestamp+'_GPS'+'.csv', 'w')
	gpsWriter = csv.writer(gpsFile)
	while 1:
		#timestr = time.strftime("%H_%M_%S")
		#dt = datetime.now()
		gpsWriter.writerow([datetime.utcnow(), gps.readline()])

def lidarRead():
	lidar = serial.Serial('/dev/ttyAMA0', 
						baudrate = 115200,
						bytesize = serial.EIGHTBITS,
						parity = serial.PARITY_NONE,
						stopbits = serial.STOPBITS_ONE)
	# si no se hace esto el lidar no jala a menos que se cierre el programa y se vuelva a correr
	# because f logic
	lidar.close()
	lidar.open()

	lidarFile = open('/home/pi/datalog/'+timestamp+'_LIDAR'+'.csv', 'w')
	lidarWriter = csv.writer(lidarFile)
	while 1:
		#byte_l = ord(lidar.read(1))
		#byte_h = ord(lidar.read(1))
		#timestr = time.strftime("%H_%M_%S")
		#dt = datetime.now()
		lidarWriter.writerow([datetime.utcnow(), ord(lidar.read(1)), ord(lidar.read(1))])

def imuRead():
	imu = serial.Serial('/dev/arduinoUNO', 115200, timeout = 1)
	imuFile = open('/home/pi/datalog/'+timestamp+'_IMU'+'.csv', 'w')
	imuWriter = csv.writer(imuFile)
	while 1:
			#timestr = time.strftime("%H_%M_%S")
			#dt = datetime.now()
			imuWriter.writerow([datetime.utcnow(), imu.readline()])

def escMotor():
	# objeto para manipular GPIO del Pi
	pi = pigpio.pi()
	# inicializar ESC y girar motor
	pi.set_servo_pulsewidth(26,1000)
	sleep(5)

	while 1:
		pi.set_servo_pulsewidth(26, 1370)

if __name__ == '__main__':
	#variable para tomar la fecha y hora del tiempo del logger
	timestamp = time.strftime("%Y_%m_%d-%H_%M_%S")

	Process(target=escMotor).start()
	Process(target=gpsRead).start()
	Process(target=lidarRead).start()
	Process(target=imuRead).start()
