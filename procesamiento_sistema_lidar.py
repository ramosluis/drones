# -*- coding: utf-8 -*-
import csv
import math
import scipy.interpolate
import multiprocessing
from multiprocessing import Process, Queue

def gpsData(q):
    # abrir archivo con datos de GPS
    dataFileGPS = open('C:\\Users\\luis\\Desktop\\datalog\\2016_11_25-13_12_55_GPS.csv', 'r')
    dataReaderGPS = csv.reader(dataFileGPS,delimiter=',')
    rawDataGPS = []
    cleanDataGPS = []

    # copiar y pegar datos desde CSV a una lista
    for row in dataReaderGPS:
        if row:
            # copiamos solo las oraciones que tienen informacion relevante para nosotros
            if '$GPGGA' in row[1] or '$GPRMC' in row[1]:
                rawDataGPS.append(row)

    for i in range(len(rawDataGPS)):
        # primero convertimos el timestamp en segundos para facilitar su uso
        rawDataGPS[i][0] = rawDataGPS[i][0].strip().split(" ")
        rawDataGPS[i][0][1] = rawDataGPS[i][0][1].strip().split(":")
        rawDataGPS[i][0][1][0] = (int(rawDataGPS[i][0][1][0])*60*60) + (int(rawDataGPS[i][0][1][1])*60) + float(rawDataGPS[i][0][1][2])

        rawDataGPS[i][1] = rawDataGPS[i][1].strip().split(",")
        # tomar solo lo necesario: timestamp, latitud y longitud
        if '$GPRMC' in rawDataGPS[i][1]:
            a_list = [rawDataGPS[i][0][1][0], rawDataGPS[i][1][3], str(float(rawDataGPS[i][1][5])*-1)]
            cleanDataGPS.append(a_list)
        # las oraciones GPGGA tambien nos dan altitud sobre la media del nivel del mar
        # adjuntamos ese dato despues de latitud y longitud en este caso
        else:
            a_list = [rawDataGPS[i][0][1][0], rawDataGPS[i][1][2], str(float(rawDataGPS[i][1][4])*-1), rawDataGPS[i][1][9]]
            cleanDataGPS.append(a_list)

    # cuando acaba, poner la lista en un queue para poder usarla en main
    q.put(cleanDataGPS)

def imuData(q):
    dataFileIMU = open('C:\\Users\\luis\\Desktop\\datalog\\2016_11_25-13_12_55_IMU.csv', 'r')
    dataReaderIMU = csv.reader(dataFileIMU,delimiter=',')
    rawDataIMU = []
    cleanDataIMU = []
    # llenar una lista con los datos del archivo
    for row in dataReaderIMU:
        if row[1]:
            rawDataIMU.append(row)
    # separar los datos de yaw, pitch y roll en una lista dentro de la lista
    # luego individualmente cambiarlos de radianes a grados
    for i in range(len(rawDataIMU)):
        rawDataIMU[i][0] = rawDataIMU[i][0].strip().split(" ")
        rawDataIMU[i][0][1] = rawDataIMU[i][0][1].strip().split(":")
        rawDataIMU[i][0][1][0] = (int(rawDataIMU[i][0][1][0])*60*60) + (int(rawDataIMU[i][0][1][1])*60) + float(rawDataIMU[i][0][1][2])

        rawDataIMU[i][1] = rawDataIMU[i][1].strip().split(",")
        rawDataIMU[i][1][0] = float(rawDataIMU[i][1][0])*180/math.pi
        rawDataIMU[i][1][1] = float(rawDataIMU[i][1][1])*180/math.pi
        rawDataIMU[i][1][2] = float(rawDataIMU[i][1][2])*180/math.pi

        # formatear los datos en una lista que sea facil de usar, no listas dentro
        # de listas, etc.
        a_list = [rawDataIMU[i][0][1][0], rawDataIMU[i][1][0], rawDataIMU[i][1][1], rawDataIMU[i][1][2]]
        cleanDataIMU.append(a_list)

    q.put(cleanDataIMU)

def lidarData(q):
    dataFileLIDAR = open('C:\\Users\\luis\\Desktop\\datalog\\2016_11_25-13_12_55_LIDAR.csv', 'r')
    dataReaderLIDAR = csv.reader(dataFileLIDAR,delimiter=',')
    rawDataLIDAR = []
    cleanDataLIDAR = []
    for row in dataReaderLIDAR:
        if row:
            if int(row[1]) < 1: #si la lectura es menor a 1 metro, no sirve
                pass
            else:
                rawDataLIDAR.append(row)
    # tomar bytes de datos y unirlos segun la formula del datasheet
    # distancia = byteH + byteL/256
    for i in range(len(rawDataLIDAR)):
        rawDataLIDAR[i][0] = rawDataLIDAR[i][0].strip().split(" ")
        rawDataLIDAR[i][0][1] = rawDataLIDAR[i][0][1].strip().split(":")
        rawDataLIDAR[i][0][1][0] = (int(rawDataLIDAR[i][0][1][0])*60*60) + (int(rawDataLIDAR[i][0][1][1])*60) + float(rawDataLIDAR[i][0][1][2])

        a_list = [rawDataLIDAR[i][0][1][0], ((int(rawDataLIDAR[i][1]) + (int(rawDataLIDAR[i][2])/256)))]
        cleanDataLIDAR.append(a_list)

    q.put(cleanDataLIDAR)

def interpolacion(x, y):
    return scipy.interpolate.interp1d(x, y)

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
    dataGps = gpsQueue.get()
    dataImu = imuQueue.get()
    dataLidar = lidarQueue.get()
