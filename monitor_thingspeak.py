""" Object-oriented interface for reading thermistor sensors temperature values
    using a voltage divider circuit.
"""
################################################################################
import time
import numpy as np
import RPi.GPIO as GPIO
from thermistor import Thermistor
from mcp3008adc import MCP3008ADC  #ADC for sampling
import DHT

TIME_DELAY = 60.0 #seconds
################################################################################
#see example at http://australianrobotics.com.au/news/how-to-talk-to-thingspeak-with-python-a-memory-cpu-monitor
import httplib, urllib
HEADERS = {"Content-type": "application/x-www-form-urlencoded","Accept":"text/plain"}
URL     = "api.thingspeak.com:80"

class ThingspeakChannel(object):
    def __init__(self, api_write_key):
        self.api_write_key = api_write_key
        
    def post(self, **fields):
        """ Post data to the channel.
            Arguments should be specified as 'field%d', e.g.
               obj.post(field1='1.0', field2='2.0')
        """
        #TODO check that the fields are labelled correctly
        
        #insert the API key
        fields['key'] = self.api_write_key
        #format the post parameters
        params = urllib.urlencode(fields)
        conn = httplib.HTTPConnection(URL)
        conn.request("POST","/update",params, HEADERS)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        return response, data

################################################################################
# Main
################################################################################
if __name__ == "__main__":
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
    #configure thermistor
    therm = Thermistor(A=A,
                       B=B,
                       C=C,
                       R_25C=R_25C,
                       R_std=R_STD,
                       adc=adc,
                       adc_channel = ADC_CHANNEL
                       )
    #setup the DHT library
    DHT_PIN = 4
    DHT.setup(pinmode='BCM')
    dht = DHT.DHT22(DHT_PIN)
                       
                       
    #setup thingspeak channel
    api_write_key = open('.API_WRITE_KEY.secret').read().strip()
    thingspeak_channel = ThingspeakChannel(api_write_key)
    
    #read thermistor in a loop
    try:
        while True:
            try:
                H_room, T_room = dht.read() #WARNING, this may occasionally throw an IOError
                T_soil = therm.read_temperature()
                print "---"
                print "timestamp: %s" % time.time()
                print "room_temperature: %0.2f" % T_room
                print "room_humidity: %0.2f" % H_room
                print "soil_temperature: %0.2f" % T_soil
                #upload to thingspeak
                thingspeak_channel.post(field1=T_room,
                                        field2=H_room,
                                        field3=T_soil,
                                       )
                #do nothing for a second
                time.sleep(TIME_DELAY)
            except IOError:
                print "#IOError - skipping this measurement"
    except KeyboardInterrupt:
        pass
