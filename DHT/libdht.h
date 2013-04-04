/*
   libdht   - A Raspberry-Pi library for one-wire communication with 
              Aosong(Guangzhou) Electronics' DHT11 and DHT22 humidity and 
              temperature sensors.
              
              This code is based off of Adafruit's experimental driver located
              at https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/tree/master/Adafruit_DHT_Driver
              
              Note: This code must be compiled on the Raspberry Pi or in a 
                    suitable cross-compiler or emulation environment.
*/
#ifndef LIB_DHT_H
#define LIB_DHT_H

#define DHT11 11
#define DHT22 22
#define AM2302 22

int LibDHTinit(void);
int LibDHTread(int type, int pin);

#endif //LIB_DHT_H
