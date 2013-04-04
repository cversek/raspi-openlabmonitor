/*
   libdht   - A Raspberry-Pi wiringPi based library for one-wire communication 
              with Aosong(Guangzhou) Electronics' DHT11 and DHT22 humidity and 
              temperature sensors.  This library is safe to access from
              a foreign function interface in languages like Python and
              will not crash the interpreter on error conditions.
              
              Author: cversek@gmail.com  
              
              Attribution:  This code is based off of Adafruit's experimental 
                  driver located at https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/tree/master/Adafruit_DHT_Driver
                  and Technion's (technion@lolware.net) wiringPi driver located 
                  at https://github.com/technion/lol_dht22/blob/master/dht22.c
              
              Note: This code must be compiled on the Raspberry Pi or in a
                    suitable cross-compiler or emulation environment.
*/
#ifndef LIB_DHT_H
#define LIB_DHT_H

#define DHT11 11
#define DHT22 22
#define AM2302 22

#define ERROR_NO_ROOT_PERMISSION -1
#define ERROR_WIRINGPI_SETUP_FAILED -2
#define ERROR_COULD_NOT_DROP_PRIVILEDGES -3
#define ERROR_BAD_DATA_CHECKSUM -4
#define ERROR_CORRUPTED_READ -5
#define ERROR_NO_RESPONSE -6


extern int setup(void);
extern int read_dht22(int pin, float *humidity, float *temperature);

#endif //LIB_DHT_H
