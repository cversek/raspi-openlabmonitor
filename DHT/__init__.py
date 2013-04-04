from lib import DHTLibrary
from dht22_class import DHT22
DEFAULT_PINMODE = "BCM" #use Broadcom SoC's numbering scheme, this best matches Adafruit's Pi Cobbler pinout

def setup(pinmode = DEFAULT_PINMODE):
    DHTLibrary.setup(pinmode=pinmode)
