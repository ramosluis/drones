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
  
*/
#include <Servo.h>                                                    // para controlar el ESC


#define terminal_baud_rate    230400                                  // baud rate de terminal 230400
#define sf30_baud_rate        921600                                   // baud rate del Sf30 (Se puede cambiar, ver manual de LiDar para especificaciones)

Servo esc;
float distance;                                                        // Variable de distancia que mida el LiDar
int Byte_L, Byte_H;
// int throttlePin = 0;                                                   // lectura de potenciometro para controlar ESC 

void setup()                                          
{
  esc.attach(9);
  esc.writeMicroseconds(1000);
  delay(10000);
  Serial.begin(terminal_baud_rate);                                     // Abre el puerto serial USB en el Arduino para la aplicación
  // while (!Serial);                                                      // Espera a que se conecte el puerto serial
  Serial1.begin(sf30_baud_rate);                                        // Abre el segundo puerto serial para conectarse al sf30
}

void loop()
{  
    Serial1.available();
    while (Serial1.available() > 0)                                 // Espera a que llegue el siguiente caracter
    {
    Byte_H = Serial1.read();                                        // Guarda el byte en Byte_H
    Byte_L = Serial1.read();                                        // Guarda el byte en Byte_L
    distance = (float(Byte_L))/256 + Byte_H;                            // Toma la distancia de los bytes
    Serial.print("Distancia en metros = ");                              
    Serial.println(distance, 2);                                        // Imprime la distancia a dos decimales y se va a una línea nueva
    //delay(10);                                                          // Pausa 0.1 segundos
    

    // int throttle = analogRead(throttlePin);                         // lee el valor analogo del potenciometro para mandarle el pulso al ESC
    // map(variable, valor minimo real, valor maximo real, valor minimo out, valor maximo out)
    // throttle = map(throttle, 0, 1023, 1000, 2000);
    esc.writeMicroseconds(1370);                                // manda el pulso al ESC

    Serial1.available();                                            // Checa el buffer si hay bytes disponibles
    }
}

