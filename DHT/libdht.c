/*
   libdht   - A Raspberry-Pi library for one-wire communication with 
              Aosong(Guangzhou) Electronics' DHT11 and DHT22 humidity and 
              temperature sensors.
              
              This code is based off of Adafruit's experimental driver located
              at https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/tree/master/Adafruit_DHT_Driver
              
              Note: This code must be compiled on the Raspberry Pi or in a
                    suitable cross-compiler or emulation environment.
*/
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <dirent.h>
#include <fcntl.h>
#include <assert.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <bcm2835.h>
#include <unistd.h>
#include "libDHT.h"

//#define DEBUG
#define MAXTIMINGS 100

//  How to access GPIO registers from C-code on the Raspberry-Pi
//  Example program
//  15-January-2012
//  Dom and Gert
//
// Access from ARM Running Linux
#define BCM2708_PERI_BASE        0x20000000
#define GPIO_BASE                (BCM2708_PERI_BASE + 0x200000) /* GPIO controller */

#define ERROR_BCM2835_INIT_FAIL -1

//allocate data buffers
int bits[250], data[100];
int bitidx = 0;

// LibDHTinit - initialize 
int LibDHTinit(void)
{
  if (!bcm2835_init())
        return ERROR_BCM2835_INIT_FAIL;
  return 0;
}

// LibDHTread - read a sensor of a 'type' at 'pin'
int readDHT(int type, int pin)
{
  int counter = 0;
  int laststate = HIGH;
  int j=0;

  // Set GPIO pin to output
  bcm2835_gpio_fsel(pin, BCM2835_GPIO_FSEL_OUTP);

  bcm2835_gpio_write(pin, HIGH);
  usleep(500000);  // 500 ms
  bcm2835_gpio_write(pin, LOW);
  usleep(20000);

  bcm2835_gpio_fsel(pin, BCM2835_GPIO_FSEL_INPT);

  data[0] = data[1] = data[2] = data[3] = data[4] = 0;

  // wait for pin to drop?
  while (bcm2835_gpio_lev(pin) == 1)
  {
    usleep(1);
  }

  // read data!
  for (int i=0; i< MAXTIMINGS; i++)
    {
    counter = 0;
    while ( bcm2835_gpio_lev(pin) == laststate)
    {
      counter++
      //nanosleep(1);  // overclocking might change this?
      if (counter == 1000)
          break;
    }
    laststate = bcm2835_gpio_lev(pin);
    if (counter == 1000) 
      break;
    bits[bitidx++] = counter;

    if ((i>3) && (i%2 == 0)) 
    {
      // shove each bit into the storage bytes
      data[j/8] <<= 1;
      if (counter > 200)
        data[j/8] |= 1;
      j++;
    }
  }
  
  #ifdef DEBUG
  for (int i=3; i<bitidx; i+=2) 
  {
    printf("bit %d: %d\n", i-3, bits[i]);
    printf("bit %d: %d (%d)\n", i-2, bits[i+1], bits[i+1] > 200);
  }
  #endif
}
/*  */
/*  switch(type){*/
/*  case DHT11:*/
/*    break;*/
/*  case DHT22:*/
/*    break;*/
/*  case AM2302:*/
/*    break;*/
/*  }*/
/*  int dhtpin = atoi(argv[2]);*/

/*  if (dhtpin <= 0) {*/
/*	printf("Please select a valid GPIO pin #\n");*/
/*	return 3;*/
/*  }*/


/*  printf("Using pin #%d\n", dhtpin);*/



/*  printf("Data (%d): 0x%x 0x%x 0x%x 0x%x 0x%x\n", j, data[0], data[1], data[2], data[3], data[4]);*/

/*  if ((j >= 39) &&*/
/*      (data[4] == ((data[0] + data[1] + data[2] + data[3]) & 0xFF)) ) {*/
/*     // yay!*/
/*     if (type == DHT11)*/
/*	printf("Temp = %d *C, Hum = %d \%\n", data[2], data[0]);*/
/*     if (type == DHT22) {*/
/*	float f, h;*/
/*	h = data[0] * 256 + data[1];*/
/*	h /= 10;*/

/*	f = (data[2] & 0x7F)* 256 + data[3];*/
/*        f /= 10.0;*/
/*        if (data[2] & 0x80)  f *= -1;*/
/*	printf("Temp =  %.1f *C, Hum = %.1f \%\n", f, h);*/
/*    }*/
/*    return 1;*/
/*  }*/

/*  return 0;*/
/*}*/
