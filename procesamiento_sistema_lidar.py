"""
Codigo para post procesamiento de datos obtenidos de
LiDar, GPS e IMU escritos a archivos CSV.

Para el procesamiento de LiDar, convierte los datos de bytes a distancia
en metros.

Para el IMU, toma los valores de yaw, pitch, roll en radianes y los
convierte a grados.

Para el GPS, escanea todas las oraciones que se escribieron al archivos CSV
por el mismo y toma solo la informacion relevante al proyecto (longitud,
latitud, altitud, rumbo magnetico)

Para todos los datos, se modificaron los timestamps para tenerlos todos
en segundos (a diferencia de HH:MM:SS

Adicionalmente, se interpolan los valores de todos los archivos para tener
los datos en todos los timestamps disponibles, esto se debe a que los
sensores trabajan a diferentes velocidades, por lo que la mayoria de los datos
entre archivos no concuerdan entre si, al interpolarlos podemos asegurarnos
que se tengan todos los valores para todos los timestamps disponibles.

Para correr el script solo es necesario modificar el path a los archivos que se
desean procesar en las funciones correspondientes de cada sensor.
"""
# -*- coding: utf-8 -*-
import csv
import multiprocessing
from multiprocessing import Process


def gpsData(q):
    """
    Funcion para tomar datos relevantes de CSV de GPS

    Args:
        q: queue al que escribiremos la lista con los datos del GPS

    Returns:
        None. Se escribe al queue que se usa como argumento de entrada.
    """
    # abrir archivo con datos de GPS
    dataFileGPS = open('C:\\Users\\luis\\Desktop\\datalog'
                       '\\2016_12_12-12_10_39_GPS.csv', 'r')
    dataReaderGPS = csv.reader(dataFileGPS, delimiter=',')
    rawDataGPS = []
    cleanDataGPS = []
    # copiar y pegar datos desde CSV a una lista
    for row in skip_last(dataReaderGPS):
        if row[1]:
            # copiamos solo las oraciones que tienen informacion
            # relevante para nosotros
            if '$GPGGA' in row[1] or '$HCHDG' in row[1]:
                rawDataGPS.append(row)

    for i in range(len(rawDataGPS)):
        # primero convertimos el timestamp en segundos para facilitar su uso
        rawDataGPS[i][0] = rawDataGPS[i][0].strip().split(" ")
        rawDataGPS[i][0][1] = rawDataGPS[i][0][1].strip().split(":")
        rawDataGPS[i][0][1][0] = ((int(rawDataGPS[i][0][1][0])*3600) +
                                  (int(rawDataGPS[i][0][1][1])*60) +
                                  float(rawDataGPS[i][0][1][2]))

        rawDataGPS[i][1] = rawDataGPS[i][1].strip().split(",")

        if '$GPGGA' in rawDataGPS[i][1]:
            a_list = ([float(rawDataGPS[i][0][1][0]),
                       float(rawDataGPS[i][1][2]),
                       float(rawDataGPS[i][1][4])*-1,
                       float(rawDataGPS[i][1][9])])
            cleanDataGPS.append(a_list)
        else:
            a_list = ([float(rawDataGPS[i][0][1][0]),
                       float(rawDataGPS[i][1][1])])
            cleanDataGPS.append(a_list)

    # interpolacion para completar datos GPS
    # interpolar valores de rumbo magnetico para las oraciones que no lo tengan
    for i in range(1, len(cleanDataGPS)):
        if len(cleanDataGPS[i]) == 4:
            heading_interpolado = (interpolacion(cleanDataGPS[i][0],
                                                 cleanDataGPS[i-1][0],
                                                 cleanDataGPS[i+1][0],
                                                 cleanDataGPS[i-1][1],
                                                 cleanDataGPS[i+1][1]))
            cleanDataGPS[i].insert(4, heading_interpolado)

        # interpolar valores de latitud, longitud y altura para las oraciones
        # que no los tengan
        if len(cleanDataGPS[i]) == 2 and i+1 < len(cleanDataGPS):
            latitud_interpolada = (interpolacion(cleanDataGPS[i][0],
                                                 cleanDataGPS[i-1][0],
                                                 cleanDataGPS[i+1][0],
                                                 cleanDataGPS[i-1][1],
                                                 cleanDataGPS[i+1][1]))

            longitud_interpolada = (interpolacion(cleanDataGPS[i][0],
                                                  cleanDataGPS[i-1][0],
                                                  cleanDataGPS[i+1][0],
                                                  cleanDataGPS[i-1][2],
                                                  cleanDataGPS[i+1][2]))

            altitud_interpolada = (interpolacion(cleanDataGPS[i][0],
                                                 cleanDataGPS[i-1][0],
                                                 cleanDataGPS[i+1][0],
                                                 cleanDataGPS[i-1][3],
                                                 cleanDataGPS[i+1][3]))

            cleanDataGPS[i].insert(1, latitud_interpolada)
            cleanDataGPS[i].insert(2, longitud_interpolada)
            cleanDataGPS[i].insert(3, altitud_interpolada)

    # quitamos primer y ultima fila de la lista
    # no se pueden interpolar (entonces no nos sirven) :C
    del cleanDataGPS[0]
    del cleanDataGPS[len(cleanDataGPS)-1]

    # cuando acaba, poner la lista en un queue para poder usarla en main
    q.put(cleanDataGPS)


def imuData(q):
    """
    Funcion para tomar datos relevantes de CSV de IMU, cambiar su rango de (1,
    180) & (-180, 0) a (0, 360), y guardarlos en una queue.

    Args:
        q: Queue donde se guarda la lista final con datos

    Returns:
        None. Se escribe a la queue los datos requeridos.
    """

    # abrir archivo CSV y crear objeto para leerlo
    dataFileIMU = open('C:\\Users\\luis\\Desktop\\datalog'
                       '\\2016_12_12-12_10_39_IMU.csv', 'r')
    dataReaderIMU = csv.reader(dataFileIMU, delimiter=',')
    rawDataIMU = []
    cleanDataIMU = []

    # llenar una lista con los datos del archivo
    # nos brincamos la ultima linea porque puede contener informacion
    # incompleta
    for row in skip_last(dataReaderIMU):
        if row[1]:
            rawDataIMU.append(row)

    # separar los datos de yaw, pitch y roll en una lista dentro de la lista
    for i in range(len(rawDataIMU)):
        rawDataIMU[i][0] = rawDataIMU[i][0].strip().split(" ")
        rawDataIMU[i][0][1] = rawDataIMU[i][0][1].strip().split(":")
        rawDataIMU[i][0][1][0] = ((int(rawDataIMU[i][0][1][0])*3600) +
                                  (int(rawDataIMU[i][0][1][1])*60) +
                                  float(rawDataIMU[i][0][1][2]))

        # cambiamos los valores de string a floats para poderlos manipular
        # facilmente
        rawDataIMU[i][1] = rawDataIMU[i][1].strip().split(",")
        rawDataIMU[i][1][0] = float(rawDataIMU[i][1][0])
        rawDataIMU[i][1][1] = float(rawDataIMU[i][1][1])
        rawDataIMU[i][1][2] = float(rawDataIMU[i][1][2])

        # formatear los datos en una lista que sea facil de usar, no listas
        # dentro de listas, dentro de listas, etc.
        a_list = ([rawDataIMU[i][0][1][0], rawDataIMU[i][1][0],
                   rawDataIMU[i][1][1], rawDataIMU[i][1][2]])
        cleanDataIMU.append(a_list)

    # las primeras lecturas son los offsets de YPR
    if cleanDataIMU[0][1] < 0:
        yawOffset = convertirA360(cleanDataIMU[0][1])
    else:
        yawOffset = cleanDataIMU[0][1]

    if cleanDataIMU[0][2] < 0:
        pitchOffset = convertirA360(cleanDataIMU[0][2])
    else:
        pitchOffset = cleanDataIMU[0][2]

    if cleanDataIMU[0][3] < 0:
        rollOffset = convertirA360(cleanDataIMU[0][3])
    else:
        rollOffset = cleanDataIMU[0][3]

    # convertimos los valores negativos a positivos
    for row in cleanDataIMU:
        if row[1] < 0:
            row[1] = convertirA360(row[1])

        if row[2] < 0:
            row[2] = convertirA360(row[2])

        if row[3] < 0:
            row[3] = convertirA360(row[3])

        row[1] = row[1] - yawOffset
        row[2] = row[2] - pitchOffset
        row[3] = row[3] - rollOffset

        if row[1] < 0:
            row[1] = convertirA360(row[1])

        if row[2] < 0:
            row[2] = convertirA360(row[2])

        if row[3] < 0:
            row[3] = convertirA360(row[3])

    q.put(cleanDataIMU)


def lidarData(q):
    """
    Funcion para tomar datos relevantes de CSV de LiDar y convertir la
    distancia a metros.

    Args:
        q: Queue donde se guardan los datos que se necesitan.

    Returns:
        None. Se guarda en la queue la lista con los datos.
    """
    dataFileLIDAR = open('C:\\Users\\luis\\Desktop\\datalog'
                         '\\2016_12_12-12_10_39_LIDAR.csv', 'r')
    dataReaderLIDAR = csv.reader(dataFileLIDAR, delimiter=',')
    rawDataLIDAR = []
    cleanDataLIDAR = []
    for row in skip_last(dataReaderLIDAR):
        if row[1]:  # si hay informacion de lidar, guardar en una lista
            rawDataLIDAR.append(row)
    # tomar bytes de datos y unirlos segun la formula del datasheet
    # distancia = byteH + byteL/256
    for i in range(len(rawDataLIDAR)):
        rawDataLIDAR[i][0] = rawDataLIDAR[i][0].strip().split(" ")
        rawDataLIDAR[i][0][1] = rawDataLIDAR[i][0][1].strip().split(":")
        rawDataLIDAR[i][0][1][0] = ((int(rawDataLIDAR[i][0][1][0])*3600) +
                                    (int(rawDataLIDAR[i][0][1][1])*60) +
                                    float(rawDataLIDAR[i][0][1][2]))

        a_list = ([rawDataLIDAR[i][0][1][0], ((int(rawDataLIDAR[i][1]) +
                                               (int(rawDataLIDAR[i][2]) /
                                                256)))])
        cleanDataLIDAR.append(a_list)

    q.put(cleanDataLIDAR)


def interpolacion(x, x1, x2, y1, y2):
    """
    Funcion para hacer interpolacion lineal.

    Args:
        x: Valor de timestamp conocido.
        x1: Valor de timestamp mas cercano con un valor menor al conocido.
        x2: Valor de timestamp mas cercano con un valor mayor al conocido.
        y1: Valor de dato correspondiente a x1.
        y2: Valor de dato correspondiente a x2.

    Returns:
        y: El valor desconocido que corresponde a x.
    """
    y = y1 + (((x - x1) / (x2 - x1)) * (y2 - y1))
    return y


def skip_last(iterator):
    """
    Funcion para iterar por todas las lineas de un CSV a excepcion de la
    ultima, ya que se apaga el Raspberry Pi mientras se estan escribienod
    datos, normalmente la ultima linea contiene informacion 'a medias'.

    Args:
        iterator (list): Objeto con la informacion del CSV.
    Returns:
        None. Se manda llamar dentro de un for, itera por todas las lineas del
        archivo menos la ultima.

    Use example:
        dataFile = open('path_to_file')

        for row in skip_last(dataFile):
            process_data
    """
    prev = next(iterator)
    for item in iterator:
        yield prev
        prev = item


def convertirA360(grados):
    """
    Funcion para convertir los valores de grados negativos de yaw, pitch y roll
    a grados positivos en el rango 0 - 360.

    Args:
        grados: Variable con grados negativos.

    Returns:
        gradosPositivos: Grados convertidos a positivos de 0 - 360 grados.

    Use example:
        yaw[1] = -15.50
        yaw[1] = convertirA360(yaw[1])

        print(yaw[1])
        > 344.5
    """
    return 360 - abs(grados)

def interpolacion_imu(rango_inferior, rango_superior, lidarImu):
    """
    Funcion para interpolar bloques de datos de IMU para integrarlos a la lista
    final.

    Args:
        rango_inferior: Indice inferior del bloque para interpolar
        rango_superior: Indice superior del bloque para interpolar
        indice_sensore: Indice del tipo de dato que se desea interpolar
            1 = Distancia
            2 = Yaw
            3 = Pitch
            4 = Roll
        lidarImu: Lista donde se guardan los valores interpolados
    Returns:
        lidarImu: La lista original, pero con los valores interpolados
        agregados
    """
    contador = 1

    # timestamps nunca cambian
    x1 = lidarImu[rango_inferior][0]
    x2 = lidarImu[rango_superior][0]

    # sensores si cambian
    y1_yaw = lidarImu[rango_inferior][2]
    y2_yaw = lidarImu[rango_superior][2]

    y1_pitch = lidarImu[rango_inferior][3]
    y2_pitch = lidarImu[rango_superior][3]

    y1_roll = lidarImu[rango_inferior][4]
    y2_roll = lidarImu[rango_superior][4]

    for i in range(rango_inferior, rango_superior):
        # valor actual, este si cambia, es el valor que se desea encontrar
        indice = (rango_inferior + contador)

        contador += 1

        x = lidarImu[indice][0]

        yaw_interpolado = (interpolacion(x, x1, x2, y1_yaw, y2_yaw))
        pitch_interpolado = (interpolacion(x, x1, x2, y1_pitch, y2_pitch))
        roll_interpolado = (interpolacion(x, x1, x2, y1_roll, y2_roll))

        lidarImu[indice].insert(2, yaw_interpolado)
        lidarImu[indice].insert(3, pitch_interpolado)
        lidarImu[indice].insert(4, roll_interpolado)

    return lidarImu

if __name__ == '__main__':
    """
    Funcion MAIN.

    Esta funcion solo corre si este programa se corre directamente, i.e., si se
    importa como modulo en otro programa el siguiente codigo no se ejecuta.

    Se crean procesos para el procesamiento de cada archivos de datos para
    minimizar el tiempo de procesamiento. Posteriormente, se interpolan los
    valores para tener la gama completa de informacion relevante.
    """
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

    # unimos las listas de LiDar e IMU primero (son las mas grandes)
    lidarImu = []
    lidarImu = dataLidar + dataImu

    # ordenamos la lista por timestamps usando lambda
    lidarImu = sorted(lidarImu, key=lambda x: x[0])

    indice_valores_lidarImu = []

    for i in range(1, len(lidarImu)):
        # insertar distancia en las filas con informacion de IMU
        if i+1 <= len(lidarImu) and (len(lidarImu[i]) == 4 and
                                     len(lidarImu[i-1]) == 2 and
                                     len(lidarImu[i+1]) == 2):

            distancia_interpolada = (interpolacion(lidarImu[i][0],
                                     lidarImu[i-1][0], lidarImu[i+1][0],
                                     lidarImu[i-1][1], lidarImu[i+1][1]))

            lidarImu[i].insert(1, distancia_interpolada)

    # guardamos los indices donde se tengan los valores de lidar e IMU
    for i in range(0, len(lidarImu)):
        if len(lidarImu[i]) == 5:
            indice_valores_lidarImu.append(i)

    # interpolar los valores de yaw, pitch y roll en todos los renglones donde
    # se pueda
    for i in range(1, len(indice_valores_lidarImu)):
        lidarImu = interpolacion_imu(indice_valores_lidarImu[i-1],
                                         indice_valores_lidarImu[i],
                                         lidarImu)

    csvFile = "output.csv"
    with open(csvFile, 'w') as output:
        writer = csv.writer(output)
        for row in lidarImu:
            writer.writerow([row])
