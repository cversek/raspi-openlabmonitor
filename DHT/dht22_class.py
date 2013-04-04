"""
 DHT.dht22.py
 
 Object Oriented Raspberry Pi Python interface to Aosong(Guangzhou) Electronics' 
 DHT22 humidity and temperature sensors. 

 author: Craig Wm. Versek, Pioneer Valley Open Science
 author_email: cversek@gmail.com
"""
import time
from ctypes import byref, sizeof, c_int, c_float
                   
from lib import DHTLibrary, ERROR_CORRUPTED_READ, ERROR_BAD_DATA_CHECKSUM, ERROR_NO_RESPONSE

###############################################################################
DEBUG = True
DEFAULT_READ_ATTEMPTS = 10
NO_RESPONSE_DELAY = 0.4 #seconds
###############################################################################
class DHT22(object):
    _libdht = DHTLibrary.getDll(debug=DEBUG)
    def __init__(self, pin):
        self.pin = pin
        
    def read(self, attempts = DEFAULT_READ_ATTEMPTS):
        humidity    = c_float()
        temperature = c_float()
        res = None
        
        for i in range(attempts):
            res = self._libdht.read_dht22(c_int(self.pin), 
                                    byref(humidity), 
                                    byref(temperature)
                                    )
            if res == 0: # the checksum matches, read was good
                break
            elif res == ERROR_NO_RESPONSE.value:
                if DEBUG:
                    print "no response - delaying %0.2f seconds" % NO_RESPONSE_DELAY
                time.sleep(NO_RESPONSE_DELAY)
            elif res == ERROR_BAD_DATA_CHECKSUM.value:
                if DEBUG:
                    print "bad checksum"
                time.sleep(0)
            if DEBUG:
                print "retry #%d" % (i+1)
        else:
            raise IOError("read failed after %d attempts" % (READ_ATTEMPTS,))
            
        return (humidity.value, temperature.value)

###############################################################################
# TEST CODE
###############################################################################
if __name__ == "__main__":
    DHTLibrary.setup('BCM')
    DATAPIN = 4
    dht = DHT22(pin = DATAPIN)
    
    try:
        while True:
            print "---"
            H, T = dht.read()
            print "timestamp: %s" % time.time()
            print "humidity: %0.2f" % H
            print "temperature: %0.2f" % T
            time.sleep(1.0)
    except KeyboardInterrupt:
        pass
