This Python package uses [ctypes](http://docs.python.org/2/library/ctypes.html) 
to access a C coded "shared object" driver library implementing the 
peculiar one wire communication protocol of [Aosong(Guangzhou) Electronics' 
DHT22](http://www.adafruit.com/products/385) humidity and temperature sensors.
Since the code is built for Raspberry Pi Linux ARM architecture, the timings
implemented by the library may not always be gauranteed (i.e., is not "real-time")
so the data request protocol will fail frequently.  In order to migitate 
the effect of this failure at the application level, the high level Python 
driver retries the request if the previous data's checksum does not match.
Also, if the sensor does not respond to the request, there is a refractory 
period of approximately 0.4s that it waits out before sending another request.
The number of data request attempts is set by the parameter 
```DEFAULT_READ_ATTEMPTS = 10``` in ```dht22_class.py``` but can be overidden
by the argument ```attempts``` in the method ```DHT22.read```.  Occasionally,
all the attempts might fail, then an ```IOError``` exception is thrown which 
must be handled by the user's Python application.

The C code driver component with its protocol timings is directly based off 
of open source code from https://github.com/technion/lol_dht22 which compiles
as a handy stand-alone commandline application.  This program may be more 
than adequate to call and parse the output from Python using another process.
However, we wanted a little more control over the details of the implementation 
and flexibility in the Python environment, so we went with the wrapper approach.
Note that the afforementioned project very likely derives from 
"Adafruit's Raspberry-Pi Python Code Library"  particularly 
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
