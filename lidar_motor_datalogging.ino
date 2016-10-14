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

#define terminal_baud_rate    230400                                  // baud rate de terminal 230400
#define sf30_baud_rate        921600                                   // baud rate del Sf30 (Se puede cambiar, ver manual de LiDar para especificaciones)

Servo esc;                                                              // define un objeto tipo servo
float distance;                                                        // Variable de distancia que mida el LiDar
int Byte_L, Byte_H;
int throttlePin = 0;                                                   // lectura de potenciometro para controlar ESC 

// En el shield de ethernet, CS es el pin 4. Hay que notar que aunque no
// se vaya a usar como el pin de CS, el pin CS de hardware (10 en el Arduino UNO,
// 53 en el MEGA) debe dejarse como output, de lo contrario la librería SD no funcionará.
const int chipSelect = 53;

void setup()                                          
{
  esc.attach(9);
  esc.writeMicroseconds(1000);                                          // manda señal para activar ESC
  delay(10000);
  // asegurarse que el pin de chipSelect se haya definido como 
  // output, aunque no se use
  pinMode(53, OUTPUT);

  // inicializar la tarjeta
  SD.begin(chipSelect);

  // Serial.begin(terminal_baud_rate);                                     // Abre el puerto serial USB en el Arduino para la aplicación
  Serial1.begin(sf30_baud_rate);                                        // Abre el segundo puerto serial para conectarse al sf30
}

void loop()
{
  Serial1.available();
  esc.writeMicroseconds(1370);                                // manda el pulso al ESC
   while (Serial1.available() > 0)                                 // Espera a que llegue el siguiente caracter
  {
    Byte_H = Serial1.read();                                        // Guarda el byte en Byte_H
    Byte_L = Serial1.read();                                        // Guarda el byte en Byte_L

    // abrir el archivo, notar que solo se puede abrir un archivo a la vez,
    // si se quiere abrir otro hay que cerrar este primero.
    File dataFile = SD.open("datalog.txt", FILE_WRITE);
    dataFile.println(String(Byte_H) + "," + String(Byte_L));
    dataFile.close();

    Serial1.available();                                            // Checa el buffer si hay bytes disponibles
  }
}
