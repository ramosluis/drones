from bokeh.charts import Histogram, output_file, show
import numpy as np

# abrir archivo y preparar para tomar datos del archivo
data_original = []
data = []
byte_h = []
byte_l = []
distancia = []

# guardamos datos en una lista sin incluir los newline characters '\n'
data_original = [line.rstrip('\n') for line in open('DATALOG2.txt')]
    
# distance = (float(Byte_L))/256 + Byte_H; 
                 
for i in range(0, len(data_original)):
    data.append(data_original[i].strip().split(","))
    byte_h.append(float(data[i][0]))
    byte_l.append(float(data[i][1]))
    data[i] = (byte_l[i]/256) + byte_h[i]

    if data[i] < 10.00 and data[i] > 0.0:
        distancia.append(data[i])
        

hist = Histogram(np.asarray(distancia), xlabel="Distancia (m)", ylabel="Frecuencia", title="Distancia de LiDar en metros", plot_width=400)


output_file('hist.html')
show(hist)