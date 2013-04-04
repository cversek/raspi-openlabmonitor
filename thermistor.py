""" Object-oriented interface for reading thermistor sensors temperature values
    using a voltage divider circuit.
"""
################################################################################
import numpy as np

DEFAULT_SAMP_NUM = 100
T_ABS = -273.15
################################################################################ 
class Thermistor(object):
    """ Configure an analog thermistor sensor with voltage divider circuit and 
        ADC.
        The 'adc' object must provide a method matching "adc.read_raw(chan)",
        have an attribute 'adc.scale' which converts the raw ADC counts
        to a voltage value, and an attribute 'adc.vref' which describes the
        voltage of the highest ADC value.
        
        Calculations:
            If 'V_ref' is the reference voltage, 'V' is the sensed ADC voltage, 
            'R_std' is the resistance of the upper leg of the voltage divider, 
            and 'R_thrm' is the thermistor's resistance on the lower leg, then
                R_thrm = V*R_std/(V_ref - V)
            The temperature is computed from a version of the Steinhart-Hart 
            formula
                logR = log10(R_thrm/R_25C)
                T_kelvin = 1000/(A + B*logR + C*logR^2)
                T_celcius = T_kelvin - 273.15
            where 'R_25C' is the thermsitors nominal resistance at 25 degrees 
            Celcius.
    """
    def __init__(self, A, B, C, R_25C, R_std, adc, adc_channel):
        self._A = A
        self._B = B
        self._C = C
        self._R_25C = R_25C
        self._R_std = R_std
        self.adc = adc
        self.adc_channel = adc_channel
        
    def read_temperature(self, samp_num = DEFAULT_SAMP_NUM):
        """ read the sensor and convert to temperature
            'samp_num' - the number of ADC samples to average
        """
        R = self.read_resistance(samp_num = samp_num)
        logR = np.log10(R/self._R_25C)
        T_kelvin = 1000.0/(self._A + self._B*logR + self._C*logR**2)
        return T_kelvin + T_ABS
        
    def read_resistance(self, samp_num = DEFAULT_SAMP_NUM):
        """ read the resistance of the thermistor
            'samp_num' - the number of ADC samples to average
        """
        V = self.read_voltage(samp_num=samp_num)
        return V*self._R_std/(self.adc.vref - V)
        
    def read_voltage(self, samp_num = DEFAULT_SAMP_NUM):
        """ read the voltage of the sensor voltage divider circuit
            'samp_num' - the number of ADC samples to average
        """
        adc  = self.adc
        chan = self.adc_channel
        #collect samples
        samps = [adc.read_raw(chan) for i in xrange(samp_num)]
        samps = np.array(samps)
        V = samps.mean()*adc.scale
        return V
        
################################################################################
# TEST CODE
################################################################################
if __name__ == "__main__":
    import time
    import RPi.GPIO as GPIO
    from mcp3008adc import MCP3008ADC  #ADC for sampling
    
    # calibration coeffs for RSBR-302J-Z50 Teflon-Coated 3k Thermistor
    A = 3.3501
    B = 0.5899
    C = 0.0104
    R_25C = 3000.0 #ohms
    R_STD = 3190.0 #ohms
    ADC_CHANNEL = 0
    
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
    therm = Thermistor(A=A,
                       B=B,
                       C=C,
                       R_25C=R_25C,
                       R_std=R_STD,
                       adc=adc,
                       adc_channel = ADC_CHANNEL
                       )
    #read thermistor in a loop
    try:
        while True:
            T = therm.read_temperature()
            print "---"
            print "timestamp: %s" % time.time()
            print "temperature: %0.2f" % T
            #do nothing for a second
            time.sleep(1.0)
    except KeyboardInterrupt:
        pass
