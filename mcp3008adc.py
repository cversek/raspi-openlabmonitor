""" Object-oriented interface for MCP3008 8-Channel 10-Bit A/D Converters
    with SPI Serial Interface
"""
################################################################################
import time, os
from comm_spi import CommSPI

DEFAULT_VREF = 3.3
################################################################################ 
class MCP3008ADC(object):
    """ Interface for MCP3008 8-Channel 10-Bit A/D Converters
        with SPI Serial Interface.  
    
        Hardware mode SPI can be used by specifying 'device' 
        during initialization or through 'setup_hardware_spi'.
        
        Software mode SPI (bit-banged) can configured using 
        'setup_software_spi'.  
    """
    NUM_CHANNELS   = 8
    MODEL          = 'MCP3008'
    BIT_RESOLUTION = 10
    def __init__(self, 
                 spi_device = None, 
                 vref = DEFAULT_VREF,
                ):
        self._spi = CommSPI(device = spi_device)
        self.vref       = float(vref)
        self.resolution = 2**self.BIT_RESOLUTION - 1
        self.scale      = self.vref/self.resolution
        
    def setup_hardware_spi(self, device):
        """ configure the driver for hardware communications at the port 
            specified by 'device', i.e. "/dev/spidev0.0"
        """ 
        self._spi.setup_hardware(device)
    
    def setup_software_spi(self, clockpin, mosipin, misopin, cspin, pinmode):
        """ setup the GPIO pins to perform software (bit-banged) communications
        """ 
        self._spi.setup_software(clockpin, mosipin, misopin, cspin, pinmode)
        
    def read(self, chan, mode = 's'):
        """ get the ADC voltage scaled value in specified 'mode':
              's': single-ended, chan = IN+, gnd = IN-
              'd': differential, for each channel pair
                   e.g. chan = 0 => CH0 = IN+, CH1 = IN-
                        chan = 1 => CH0 = IN-, CH1 = IN+
        """
        raw_val = self.read_raw(chan=chan,mode=mode)
        V = raw_val*self.scale
        return V
        
    def read_raw(self, chan, mode = 's'):
        """ get the raw ADC value in specified 'mode':
              's': single-ended, chan = IN+, gnd = IN-
              'd': differential, for each channel pair
                   e.g. chan = 0 => CH0 = IN+, CH1 = IN-
                        chan = 1 => CH0 = IN-, CH1 = IN+
        """
        if not chan in range(self.NUM_CHANNELS):
            raise ValueError, "'chan' must be in %r" % range(self.NUM_CHANNELS)
        #command byte is (sgl/diff,D2,D1,D0,X,X,X,X)
        cmd  = None
        if   mode == 's':
            cmd  = 1 << 7        #single-ended bit
        elif mode == 'd':
            cmd  = 0             #differential, null bit
        else:
            raise ValueError, "mode must be 's' (or 'diff'"
        cmd |= chan << 4         #D2,D1,D0
        raw_val = self._run_transaction(cmd)
        return raw_val
        
    def _run_transaction(self, cmd):
        bytes_out = bytearray()
        bytes_out.append(0x01)   #start bit
        #command byte is (sgl/diff,D2,D1,D0,X,X,X,X)
        bytes_out.append(cmd)
        #extra byte to receive data
        bytes_out.append(0)
        #do transmit/receive
        bytes_in = self._spi.transfer(bytes_out)
        #data is in 2nd and 3rd bytes (?,?,?,?,?,0,B9,B8), (B7,B6,B5,B4,B3,B2,B1,B0)
        #print " ".join(map(bin,bytes_in))
        val  = (bytes_in[1] & 0b11) << 8
        val += bytes_in[2]
        return val
        
################################################################################
# TEST CODE
################################################################################
if __name__ == "__main__":
    import RPi.GPIO as GPIO
    # change these as desired - they're the pins connected from the
    # SPI port on the ADC to the Cobbler
    SPICLK  = 18
    SPIMISO = 23
    SPIMOSI = 24
    SPICS   = 25
    PINMODE = GPIO.BCM  #configure the pin order as Broadcom SoC channels
    
    adc = MCP3008ADC()
    adc.setup_software_spi(clockpin = SPICLK,
                           misopin  = SPIMISO,
                           mosipin  = SPIMOSI,
                           cspin    = SPICS,
                           pinmode  = PINMODE
                          )
    
    #read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
    try:
        while True:
            print "---"
            print "timestamp: %s" % time.time()
            for i in range(adc.NUM_CHANNELS):
                val = adc.read_single(i)
                print "chan%d: %d" % (i,val)
            #do nothing for a second
            time.sleep(1.0)
    except KeyboardInterrupt:
        pass
