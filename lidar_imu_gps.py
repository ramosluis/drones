import serial
import time
import csv
#import pigpio
from time import sleep


#pi = pigpio.pi()

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
	x = gps.readline()
	y = imu.readline()
	data_H = ord(lidar.read(1))
	data_L = ord(lidar.read(1))
	if "$GPRMC" in x or "$GPGGA" in x:
		data.append(x)
		data.append(y)
		data.append(data_H)
		data.append(data_L)
		dataWriter.writerow([data])
		data[:] = []
	else:
			continue
