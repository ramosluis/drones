#include <Servo.h>
 
Servo esc;
int throttlePin = 0;
 
void setup()
{
esc.attach(9);
}
 
void loop()
{
int throttle = analogRead(throttlePin);
// map(variable, valor minimo real, valor maximo real, valor minimo out, valor maximo out)
throttle = map(throttle, 0, 1023, 1000, 2000);
esc.writeMicroseconds(throttle);
}
