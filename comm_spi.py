""" Object-oriented interface for SPI interface communications allowing
    either hardware or software (bit-banged) driver mode
"""
################################################################################
import RPi.GPIO as GPIO

################################################################################
class CommSPI(object):
    """ Provides hardware of software (bit-banged) IO using SPI protocol
    """
    def __init__(self, device = None):
        self.transfer = None
        #by default setup the hardware SPI if device is specified
        if not device is None:
            self.setup_hardware(device = device)
        
    def setup_hardware(self, device):
        """ configure the driver for hardware communications at the port 
            specified by 'device', i.e. "/dev/spidev0.0"
        """ 
        self._device  = device
        #overload transfer with the right method
        self.transfer = self._transfer_hardware
    
    def setup_software(self, clockpin, mosipin, misopin, cspin):
        """ setup the GPIO pins to perform software (bit-banged) communications
        """ 
        # set up the SPI interface pins
        GPIO.setup(clockpin, GPIO.OUT)
        GPIO.setup(mosipin , GPIO.OUT)
        GPIO.setup(misopin , GPIO.IN )
        GPIO.setup(cspin   , GPIO.OUT)
        #cache the pin settings
        self._clockpin = clockpin
        self._mosipin  = mosipin
        self._misopin  = misopin
        self._cspin    = cspin
        #overload transfer with the right method
        self.transfer  = self._transfer_software
        
    def _transfer_hardware(self, bytes_out):
        """transfer bytes using hardware SPI driver
        """ 
        raise NotImplemented
        
    def _transfer_software(self, out_bytes):
        """transfer bytes using using bit-banged SPI 
           ref. git://gist.github.com/3151375.git
        """ 
        #start transmission by toggling chip select low
        GPIO.output(self._cspin, True)
        GPIO.output(self._clockpin, False) #start clock low
        GPIO.output(self._cspin, False)    #bring CS low
        
        #perform transfer
        out_bytes = bytearray(out_bytes)   #convert strings or integer lists to one type
        inp_bytes = bytearray()            #input buffer
        for out_byte in out_bytes:
            inp_byte = 0
            for i in range(7,-1,-1):       #binary places in MSB order
                #send the output bit
                if (2**i & out_byte) != 0:
                    GPIO.output(self._mosipin, True)
                else:
                    GPIO.output(self._mosipin, False)
                #pulse the clock
                GPIO.output(self._clockpin, True)
                GPIO.output(self._clockpin, False)
                #read the input bit
                if (GPIO.input(self._misopin)):
                    inp_byte += 2**i
            inp_bytes.append(inp_byte)
            
        #finish transmission by toggling chip select     
        GPIO.output(cspin, True)
        return inp_bytes
 
################################################################################
# TEST CODE
################################################################################
if __name__ == "__main__":
    pass
