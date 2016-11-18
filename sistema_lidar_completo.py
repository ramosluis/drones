import serial
import time
import math
import mpu6050
import csv
import pigpio
from time import sleep

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

# inicializar ESC y girar motor
pi.set_servo_pulsewidth(26,1000)
sleep(5)

pi.set_servo_pulsewidth(26, 1370)

while 1:
	# tomar valor de INT_STATUS
	mpuIntStatus = mpu.getIntStatus()
  
	if mpuIntStatus >= 2: # checar que este listo el interrupt de datos del DMP 
        # tomar cuenta actual de FIFO
		fifoCount = mpu.getFIFOCount()
        
        # checar si hay overflow de datos
		if fifoCount == 1024:
            # reinicar conte
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
    
        # ver cuenta del FIFO aqui, en caso de tener mas de 1
        # esto nos permite leer mas sin esperar un interrupt        
		fifoCount -= packetSize  
		# guardamos valores de sensores
		x = gps.readline()
		# los valores del lidar vienen codificados como caracteres ASCII
		# con la funcion ord() los cambiamos a decimal
		data_L = ord(lidar.read(1))
		data_H = ord(lidar.read(1))
	
		data.append(x)
		data.append(y)
		data.append(data_H)
		data.append(data_L)
		# encendemos LED indicador de escritura de datos
		pi.write(23, 1)
		dataWriter.writerow([data])
		pi.write(23, 0)
		# borramos lista para tomar datos nuevos
		data[:] = []
