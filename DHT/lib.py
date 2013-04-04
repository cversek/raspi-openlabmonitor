"""
 DHT.lib.py
 
 Python interface to the LibDHT driver for Aosong(Guangzhou) Electronics' 
 DHT11 and DHT22 humidity and temperature sensors. 

 author: Craig Wm. Versek, Pioneer Valley Open Science
 author_email: cversek@gmail.com
"""
import sys, os
from ctypes import CDLL, cdll, c_int
###############################################################################
THIS_PATH = os.path.dirname(os.path.abspath(__file__))
LIB_NAME  = "libdht.so"
LIB_PATH  = os.path.sep.join((THIS_PATH,LIB_NAME))

DEFAULT_PINMODE = "BCM" #use Broadcom SoC's numbering scheme, this best matches Adafruit's Pi Cobbler pinout

# C library definitions
ERROR_NO_ROOT_PERMISSION         = c_int(-1)
ERROR_WIRINGPI_SETUP_FAILED      = c_int(-2)
ERROR_COULD_NOT_DROP_PRIVILEDGES = c_int(-3)
ERROR_BAD_DATA_CHECKSUM          = c_int(-4)
ERROR_CORRUPTED_READ             = c_int(-5)
ERROR_NO_RESPONSE                = c_int(-6)
###############################################################################
class DHTLibrary:
    __dll = None
    @staticmethod
    def setup(pinmode = DEFAULT_PINMODE):
        """pinmode - sets the mapping of the GPIO pins:
                     'BCM' - Broadcom SoC numbering scheme, this best
                             matches Adafruit's Pi Cobbler pinout
                     'wiring' - Simplified mapping for wiringPi
                     (see https://projects.drogon.net/raspberry-pi/wiringpi/pins/)
        """
        dll = DHTLibrary.getDll()
        res = None
        if   pinmode == "BCM":
            res = dll.setupBCM()
        elif pinmode == "wiring":
            res = dll.setupWiring()
        else:
            raise ValueError("'pinmode' must be eithe 'BCM' or 'wiring'")
        #check errors
        if res == ERROR_NO_ROOT_PERMISSION:
            raise RuntimeError("Must run with root permissions ('sudo python ...')")
            
    @staticmethod
    def getDll(debug = False):
        if DHTLibrary.__dll is None:
            if sys.platform == 'linux2':
                DHTLibrary.__dll = cdll.LoadLibrary(LIB_PATH)
            else:
                raise RuntimeError("Platform not supported")
        if debug:
            #DHTLibrary.__dll.setDebugLevel(None,) #TODO
            pass
        return DHTLibrary.__dll

###############################################################################
# TEST CODE
###############################################################################
if __name__ == "__main__":
    DHTLibrary.setup('BCM')
    libdht = DHTLibrary.getDll(debug=True)
