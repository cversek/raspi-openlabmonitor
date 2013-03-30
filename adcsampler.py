################################################################################
import os,sys,time
from collections import OrderedDict
import numpy as np
from mcp3008adc import MCP3008ADC

ADCS = {'mcp3008': MCP3008ADC}

    
DEFAULT_OUTPUT_FILE = "./data.csv"
DEFAULT_VERBOSE     = True
DEFAULT_BUFFSIZE    = 1
################################################################################
class Application:
    def __init__(self, adc, channels, modes, delay, output_file, 
                 buff_size = DEFAULT_BUFFSIZE,
                 store_error = False,
                 csv_delimiter = ",",
                 csv_newline   = "\n",
                 verbose       = False,
                 ):
        self.adc       = adc
        self.channels  = channels
        self.modes     = modes
        self.buffer    = []
        self.delay       = delay
        self.output_file = output_file
        self.buff_size   = buff_size
        self.store_error = store_error
        self.csv_delimiter   = csv_delimiter
        self.csv_newline     = csv_newline
        self.verbose   = verbose
        
        
    def sample(self, samp_size = 1, samp_num = None):
        adc = self.adc
        channels     = self.channels
        modes        = self.modes
        num_chans    = len(channels)
        chan_indices = range(num_chans) 
        buff_size    = self.buff_size
        delay        = self.delay
        #collect metadata and write it to the file header
        metadata = OrderedDict()
        metadata['start_timestamp'] = t0 = time.time()
        metadata['adc_model']       = adc.MODEL
        metadata['adc_bit_res']     = adc.BIT_RESOLUTION
        metadata['adc_vref']        = adc.vref     
        metadata['channels']        = channels
        metadata['modes']           = modes
        metadata['samp_size']       = samp_size
        metadata['samp_num']        = samp_num
        metadata['delay']           = delay
        metadata['store_error']     = self.store_error
        self.write_header(metadata)
        if self.verbose:
            print "Starting aquistion with the following settings:"
            for key,val in metadata.items():
                print "\t%s = %r" % (key,val)
            print "Beginning to sample"
        #begin sampling
        try:
            i = 0
            while i < samp_num or samp_num is None:
                t1 = time.time()
                subsamps = [[] for chan in range(num_chans)]
                for j in range(samp_size):
                    for index,chan,mode in zip(chan_indices,channels,modes):
                        subsamp = adc.read(chan, mode = mode)
                        subsamps[index].append(subsamp)
                t2 = time.time()
                t_samp = (t1+t2)/2.0 - t0
                t_err  = (t2-t1)/2.0
                record = [t_samp, t_err]
                #convert subsample to array for processing
                subsamps = np.array(subsamps)
                sample = subsamps.mean(axis=1)  #average columnwise
                if self.store_error:
                    err = subsamps.std(axis=1)  #std.dev. columnwise
                    for s,e in zip(sample,err):
                        record += [s,e]
                else:
                    record += list(sample)
                self.buffer.append(record)
                i += 1
                if i % buff_size == 0:
                    if self.verbose:
                        print "%d samples collected, flushing buffer..." % i
                    self.flush_buffer()
                #do nothing for a while
                time.sleep(delay)
        except KeyboardInterrupt:
            return i
        finally:
            self.close()
            
    def write_header(self, metadata):
        self.output_file.write("#<METADATA>")
        self.output_file.write(self.csv_newline)
        for key, val in metadata.items():
            self.output_file.write("#%s = %r" % (key,val))
            self.output_file.write(self.csv_newline)
        self.output_file.write("#</METADATA>")
        self.output_file.write(self.csv_newline)
        #column descriptor
        line = ["#t_samp (s)", "t_err(s)"]
        for chan in self.channels:
            line += ["chan%d" % chan]
            if self.store_error:
                line += ["chan%d_err" % chan]
        self.output_file.write(self.csv_delimiter.join(line))
        self.output_file.write(self.csv_newline)
        self.output_file.flush()
            
            
    def flush_buffer(self):
        for record in self.buffer:
            line = self.csv_delimiter.join(map(str,record))
            self.output_file.write(line)
            self.output_file.write(self.csv_newline)
        self.output_file.flush()
        self.buffer = []
        
    def close(self):
        self.flush_buffer()
        self.output_file.close()
        
        

################################################################################
# MAIN
################################################################################
import RPi.GPIO as GPIO
#TODO these pin settings should be configurable from the commandline
ADC_SPI_TYPE = "software"
SPICLK  = 18
SPIMISO = 23
SPIMOSI = 24
SPICS   = 25
PINMODE = GPIO.BCM  #configure the pin order as Broadcom SoC channels

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--adc", 
                        help = "the type of adc chip to sample from",
                        default = "mcp3008",
                       )
    parser.add_argument("-c", "--channels", 
                        help = "channels to sample separated by ','",
                        default = "0",
                       )
    parser.add_argument("-m", "--modes", 
                        help = "modes for each channel 's' (single-end) or 'd' (differential) separated by ','",
                        default = "s",
                       )
    parser.add_argument("-d", "--delay", 
                        help = "delay between samples in seconds",
                        default = 1.0,
                       )
    parser.add_argument("-s", "--samp_size", 
                        help = "number of subsamples to average for each recorded sample",
                        default = 1,
                       )
    parser.add_argument("-n", "--samp_num", 
                        help = "number of samples to collect",
                        default = None,
                       )
    parser.add_argument("-b", "--buff_size", 
                        help = "number of samples to hold in memory before writing to disk",
                        default = DEFAULT_BUFFSIZE,
                       )
    parser.add_argument("-e", "--store_error", 
                        help = "store the errors of the samples (std. dev. of subsamples)",
                        action="store_true",
                        default = False,
                       )
    parser.add_argument("-o", "--output_file", 
                        help = "file to store samples",
                        default = DEFAULT_OUTPUT_FILE,
                       )                      
    parser.add_argument("-v", "--verbose", 
                        help="increase output verbosity",
                        action="store_true",
                        default = DEFAULT_VERBOSE,
                       )
    args = parser.parse_args()
    #check the adc argument and configure the acquisition
    adc_class = ADCS[args.adc]
    adc = adc_class()
    adc_spi_type = ADC_SPI_TYPE #TODO add hardware support handling
    if adc_spi_type == "software":
        adc.setup_software_spi(clockpin = SPICLK,
                               misopin  = SPIMISO,
                               mosipin  = SPIMOSI,
                               cspin    = SPICS,
                               pinmode  = PINMODE
                              )
    else:
        raise NotImplemented #TODO
    #check the channels argument
    channels = args.channels
    channels = map(int,channels.split(','))
    #check the modes argument
    modes    = args.modes.split(',')
    assert len(modes) <= len(channels)
    #fill in missing modes as single-ended
    if modes == ['']:
        modes = ['s']*len(channels)
    else:  
        for m in modes:
            assert m in ['s','d']
        modes = modes + ['s']*(len(channels) - len(modes))
    #check delay argument
    delay = float(args.delay)
    #check samp_size argument
    samp_size = int(args.samp_size)
    assert samp_size > 0
    #check samp_num argument
    samp_num = None
    if not args.samp_num is None:
        samp_num = int(args.samp_num)
        assert samp_num > 0
    #check buff_size argument
    buff_size = int(args.buff_size)
    assert buff_size > 0   
    #check output file argument
    output_file = None
    output_mode = None
    if os.path.isfile(args.output_file):
        print "-"*20
        res = ""
        while not res in ['A','a','O','o','Q','q']:
            res = raw_input("Output file '%s' already exists, (A)ppend/(O)verwrite/(Q)uit?: " % args.output_file)
            if res in ['A','a']:
                output_file = open(args.output_file,'a')
                output_mode = "append"
            elif res in ['O','o']:
                output_file = open(args.output_file,'w')
                output_mode = "overwrite"
            elif res in ['Q','q']:
                sys.exit(0)
    else:
        output_file = open(args.output_file,'w')
        output_mode = 'create'
                     
    if args.verbose:
        print "Writing (mode=\"%s\") output file: %s" % (output_mode,args.output_file)
        
    #configure the application
    app = Application(adc         = adc,
                      channels    = channels,
                      modes       = modes,
                      delay       = delay,
                      buff_size   = buff_size,
                      output_file = output_file,
                      store_error = args.store_error,
                      verbose     = args.verbose,
                      )
    
    #start acquisition
    app.sample(samp_size = samp_size, 
               samp_num  = samp_num,
              )
    
