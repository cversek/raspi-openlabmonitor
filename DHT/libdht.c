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

#include <wiringPi.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <sys/types.h>
#include <unistd.h>
#include "libdht.h"

#define MAXWAIT_ACK 50
#define COUNTERMAX 255
#define MAXTIMINGS 85

#define COUNTERTHRESH 20

static int dht22_dat[5] = {0,0,0,0,0};

//
// Setup the wiringPi library in Broadcom numbering scheme, this best
// matches Adafruit's Pi Cobbler pinout
//   see: https://projects.drogon.net/raspberry-pi/wiringpi/pins/
int setupBCM(void)
{
  int res;
  
  if(geteuid() != 0)
  {
    perror("Must run with root permissions ('sudo python ...')\n");
    return ERROR_NO_ROOT_PERMISSION;
  }
  
  if (wiringPiSetupGpio() == -1)
    perror("Setup of wiringPi failed\n");
    return ERROR_WIRINGPI_SETUP_FAILED;

  if (setuid(getuid()) < 0)
  {
    perror("Dropping privileges failed\n");
    return ERROR_COULD_NOT_DROP_PRIVILEDGES;
  }
  // try to get realtime priority to enhance timing reliabilty
  res = piHiPri(99);
  if (res < 0){
    printf("WARNING: 'piHiPri' priority could not be set to 99\n");
  }
  return 0 ;
}

//
// Setup the wiringPi library in the simplified numbering scheme
//  see: https://projects.drogon.net/raspberry-pi/wiringpi/pins/
int setupWiring(void)
{
  int res;
  
  if(geteuid() != 0)
  {
    perror("Must run with root permissions ('sudo python ...')\n");
    return ERROR_NO_ROOT_PERMISSION;
  }
  
  if (wiringPiSetup() == -1)
    perror("Setup of wiringPi failed\n");
    return ERROR_WIRINGPI_SETUP_FAILED;

  if (setuid(getuid()) < 0)
  {
    perror("Dropping privileges failed\n");
    return ERROR_COULD_NOT_DROP_PRIVILEDGES;
  }
  // try to get realtime priority to enhance timing reliabilty
  res = piHiPri(99);
  if (res < 0){
    printf("WARNING: 'piHiPri' priority could not be set to 99\n");
  }
  return 0 ;
}

int read_dht22(int pin, float *humidity, float *temperature)
{
  uint8_t currstate = HIGH;
  uint8_t laststate = HIGH;
  uint8_t counter = 0;
  uint8_t j = 0, i;

  dht22_dat[0] = dht22_dat[1] = dht22_dat[2] = dht22_dat[3] = dht22_dat[4] = 0;

  pinMode(pin, OUTPUT);
  // start with pin pulled up
  digitalWrite(pin, HIGH);
  delayMicroseconds(500);
  // pull pin down for 18 milliseconds
  digitalWrite(pin, LOW);
  delay(18);
  //delayMicroseconds(18000);
  // then pull it up for 40 microseconds
  digitalWrite(pin, HIGH);
  //delayMicroseconds(30);
  // prepare to read the pin
  pinMode(pin, INPUT);
  delayMicroseconds(30);
  
  
  // wait for pin to drop?
  // detect change and read data
  for ( i=0; i < MAXWAIT_ACK; i++) {
    if (digitalRead(pin) == LOW) break;
    delayMicroseconds(1);
  }
  if (i == MAXWAIT_ACK){
    return ERROR_NO_RESPONSE;
  }

  // detect change and read data
  for ( i=0; i < MAXTIMINGS; i++) {
    counter = 0;
    currstate = digitalRead(pin);
    while (currstate == laststate) {
      counter++;
      delayMicroseconds(1);
      if (counter == COUNTERMAX) {break;
      }
      currstate = digitalRead(pin);
    }
    laststate = currstate;
    if (counter == COUNTERMAX) break;
    // ignore first 3 transitions
    if ((i >= 4) && (i%2 == 0)) {
      // shove each bit into the storage bytes
      dht22_dat[j/8] <<= 1;
      if (counter > COUNTERTHRESH)
        dht22_dat[j/8] |= 1;
      j++;
    }
  }
  //printf("Data (%d): 0x%x 0x%x 0x%x 0x%x 0x%x", j, dht22_dat[0], dht22_dat[1], dht22_dat[2], dht22_dat[3], dht22_dat[4]);
  // check we read 40 bits (8bit x 5 ) + verify checksum in the last byte
  // print it out if data is good
  if ((j >= 40) &&
      (dht22_dat[4] == ((dht22_dat[0] + dht22_dat[1] + dht22_dat[2] + dht22_dat[3]) & 0xFF)) ) {
        float t, h;
        h = (float)dht22_dat[0] * 256 + (float)dht22_dat[1];
        h /= 10;
        t = (float)(dht22_dat[2] & 0x7F)* 256 + (float)dht22_dat[3];
        t /= 10.0;
        if ((dht22_dat[2] & 0x80) != 0) t *= -1;
    //pass back data by reference
    *humidity = h;
    *temperature = t;
    //printf("\n");
    return 0;
  }
  else
  {
    //printf(" BAD CHECKSUM\n");
    return ERROR_BAD_DATA_CHECKSUM;
  }
}


