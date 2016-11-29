# -*- coding: utf-8 -*-
import csv
import math
import multiprocessing
from multiprocessing import Process, Queue

def gpsData(q):
    # abrir archivo con datos de GPS
    dataFileGPS = open('C:\\Users\\luis\\Desktop\\datalog\\2016_11_25-13_12_55_GPS.csv', 'r')
    dataReaderGPS = csv.reader(dataFileGPS,delimiter=',')
    rawDataGPS = []

    # copiar y pegar datos desde CSV a una lista
    for row in dataReaderGPS:
        if row:
            # copiamos solo las oraciones que tienen informacion relevante para nosotros
            # TODO - copiar y pegar solo coordenadas x, y, z
            if '$GPGGA' in row[1] or '$GPRMC' in row[1]:
                rawDataGPS.append(row)

    # cuando acaba, poner la lista en un queue para poder usarla en main
    q.put(rawDataGPS)

def imuData(q):
    dataFileIMU = open('C:\\Users\\luis\\Desktop\\datalog\\2016_11_25-13_12_55_IMU.csv', 'r')
    dataReaderIMU = csv.reader(dataFileIMU,delimiter=',')
    rawDataIMU = []
    for row in dataReaderIMU:
        if row[1]:
            rawDataIMU.append(row)
    # separar los datos de yaw, pitch y roll en una lista dentro de la lista
    # luego individualmente cambiarlos de radianes a grados
    for i in range(len(rawDataIMU)):
        rawDataIMU[i][1] = rawDataIMU[i][1].strip().split(",")
        rawDataIMU[i][1][0] = float(rawDataIMU[i][1][0])*180/math.pi
        rawDataIMU[i][1][1] = float(rawDataIMU[i][1][1])*180/math.pi
        rawDataIMU[i][1][2] = float(rawDataIMU[i][1][2])*180/math.pi

    q.put(rawDataIMU)

def lidarData(q):
    dataFileLIDAR = open('C:\\Users\\luis\\Desktop\\datalog\\2016_11_25-13_12_55_LIDAR.csv', 'r')
    dataReaderLIDAR = csv.reader(dataFileLIDAR,delimiter=',')
    rawDataLIDAR = []

    for row in dataReaderLIDAR:
        if row:
            if int(row[1]) < 1:
                pass
            else:
                rawDataLIDAR.append(row)
    # tomar bytes de datos y unirlos segun la formula del datasheet
    # distancia = byteH + byteL/256
    for i in range(len(rawDataLIDAR)):
        rawDataLIDAR[i][1] = (int(rawDataLIDAR[i][1]) + (int(rawDataLIDAR[i][2])/256))

    q.put(rawDataLIDAR)

if __name__ == '__main__':
    # crear queues para almacenar listas de datos
    gpsQueue = multiprocessing.Queue()
    imuQueue = multiprocessing.Queue()
    lidarQueue = multiprocessing.Queue()

    # paralelizar el procesamiento de listas con un proceso dedicado a cada uno
    gpsProcess = Process(target=gpsData, args=(gpsQueue,)).start()
    imuProcess = Process(target=imuData, args=(imuQueue,)).start()
    lidarProcess = Process(target=lidarData, args=(lidarQueue,)).start()

    # tomar datos de queues
    dataGPS = gpsQueue.get()
    dataImu = imuQueue.get()
    dataLidar = lidarQueue.get()
