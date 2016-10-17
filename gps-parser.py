# -*- coding: utf-8 -*-
import csv

# abrir csv y preparar para tomar datos del archivo
datafile = open('data.csv', 'r')
datareader = csv.reader(datafile,delimiter=',')
data = []

# el script crea el csv con muchas filas vacias, hay que checar si es el caso para brincarlas
for row in datareader:
    if row:
        data.append(row)
        
# separar datos en arreglos diferentes

rmc = [] # Recommended minimum data for gps
gga = [] # Fix information
gsv = [] # Detailed Satellite data
hdg = [] # Compass output
gsa = [] # Overall Satellite data

for row in data:
    if row[0] == '$GPRMC':
        rmc.append(row)
    elif row[0] == '$GPGGA':
        gga.append(row)
    elif row[0] == '$GPGSV':
        gsv.append(row)
    elif row[0] == '$HCHDG':
        hdg.append(row)
    else:
        gsa.append(row)