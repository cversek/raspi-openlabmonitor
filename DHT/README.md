This Python package uses [ctypes](http://docs.python.org/2/library/ctypes.html) 
to access a C coded "shared object" driver library implementing the 
peculiar one wire communication protocol of [Aosong(Guangzhou) Electronics' 
DHT22](http://www.adafruit.com/products/385) humidity and temperature sensors.
This C code driver component is directly based off of open source code from 
https://github.com/technion/lol_dht22 which is very likely ultimately derived
from "Adafruit's Raspberry-Pi Python Code Library" particularly 
[Adafruit_DHT_Driver](https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/tree/master/Adafruit_DHT_Driver).
Go buy your DHT sensor from them, because they are awesome.

The excellent [wiringPi](https://projects.drogon.net/raspberry-pi/wiringpi)
is a *required dependency* which probably makes this code a little more 
portable across future revisions than Adafruit_DHT_Driver which uses 
the Broadcom library header "bcm2835.h" to access the GPIO pins from C.

Author: Craig Wm. Versek, [Pioneer Valley Open Science](http://pvos.cc)

Here is the included license text for Adafruit:
>Adafruit's Raspberry-Pi Python Code Library
> ===
>  Here is a growing collection of libraries and example python scripts
>  for controlling a variety of Adafruit electronics with a Raspberry Pi
>  
>  In progress!
>
>  Adafruit invests time and resources providing this open source code,
>  please support Adafruit and open-source hardware by purchasing
>  products from Adafruit!
>
>  Written by Limor Fried, Kevin Townsend and Mikey Sklar for Adafruit Industries.
>  BSD license, all text above must be included in any redistribution
