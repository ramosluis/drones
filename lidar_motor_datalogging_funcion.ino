/*
  NOTA PARA SF30:
    -Se asume que el LiDar esta a baud rate de 921600.
    -Se asume que el LiDar esta a una Snapshot Resolution de 0.03m.
    -Se asume que el LiDar tiene un Serial Port Update Rate de 1144/sec.

  Diagrama de Cableado LiDar:
  Pin_GND (Negro)     SF30 Laser Rangefinder - GND
  Pin_+5V (Rojo)      SF30 Laser Rangefinder - +5V
  Pin_TXD (Amarillo)  SF30 Laser Rangefinder - Arduino MEGA TX1 Pin (19)
  Pin_RXD (Naranja)   SF30 Laser Rangefinder - Arduino MEGA RX1 Pin (18)
  
  NOTA ARDUINO MEGA:
    -El MEGA que tenemos tiene los pines TX1 y RX1 volteados, por eso se conecta como
    se describe arriba.

  Ejemplo original en: http://learn.parallax.com/propeller-c-simple-devices/
 
  Diagrama de Cableado Tarjeta SD:
  * Sensores analogicos en  analog ins 0, 1, y 2
  * Tarjeta SD en el bus SPI de la siguiente manera:
  ** MOSI - pin 51
  ** MISO - pin 50
  ** CLK - pin 52
  ** CS - pin 53
*/

#include <Servo.h>                                                    // para controlar el ESC
#include <SD.h>                                                       // para manejar memorias SD

#define sf30_baud_rate        921600                                   // baud rate del Sf30 (Se puede cambiar, ver manual de LiDar para especificaciones)

Servo esc;                                                              // define un objeto tipo servo

int Byte_H, Byte_L;

void setup()                                          
{
  esc.attach(9);
  esc.writeMicroseconds(1000);                                          // manda señal para activar ESC
  delay(7500);                                                         // delay que nos permite encender todo el equipo antes de iniciar
  // asegurarse que el pin de chipSelect se haya definido como 
  // output, aunque no se use
  pinMode(53, OUTPUT);

  // inicializar la tarjeta
  SD.begin(53);

  Serial1.begin(sf30_baud_rate);                                        // Abre el segundo puerto serial para conectarse al sf30
  esc.writeMicroseconds(1370); 
  Serial1.available();
}

void loop()
{
  Serial1.available();
    // leer lidar
    lidar_datos(&Byte_H, &Byte_L);
  
    // escribir a tarjeta microsd
    File dataFile = SD.open("lidar5.txt", FILE_WRITE);
    dataFile.println(String(Byte_H) + "," + String(Byte_L));
    dataFile.close();

    
}

void lidar_datos(int* Byte_H, int* Byte_L)
{
  if (Serial1.available() != 0)
  {
    *Byte_H = Serial1.read();
    *Byte_L = Serial1.read();
  }
  else
  {
    *Byte_H = 255;
    *Byte_L = 255;
  }
}

