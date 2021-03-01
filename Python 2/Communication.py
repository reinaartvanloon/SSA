"""
Serial transmission library
Includes:
    -Creation of serial object
    -Serial receiver function
    -Serial transmitter function
Created by:
    Alejandro Rozene
"""

import serial                                                                   # module for serial communication
import serial.tools.list_ports 
import sys 
import numpy
import Audio
import time

class Comm:
        
    
    baudrate = 115200
    
    def __init__(self):       
        
        if float(serial.__version__)<3.0:
            sys.exit("Please update Pyserial")
        
        lstports = list( serial.tools.list_ports.comports() )                   # list ports               
        self.port_nr = ''                                                       # create an empty port number
        for n in lstports:
                if n.vid == 9025:
                    self.port_nr = n.device                                     # port name of the arduino prort
        if self.port_nr == '':
            sys.exit( "No device connected or recognized" )

        try:
            self.serialPort = serial.Serial (                                       # create serial object
                    self.port_nr, self.baudrate, timeout = 0 , rtscts = True )
            self.serialPort.close()
            print('Device recognized')
        except serial.SerialException:
            sys.exit( "No device connected or recognized" )  # if no ports are found, exit the program
        
            
        
    def write(self,audio_data):
        """Comm.write(processed_audio) takes an audio file from Audio.adapt()
            and writes to the serial port"""
        data = Audio.adapt(audio_data,150)
        self.serialPort.close()        
        for x in range(len(data)): 
            self.serialPort.open()            
            self.serialPort.write(data[x])            
            self.serialPort.close()
            printProgressBar (x, len(data), prefix = '', suffix = '',
                                  decimals = 1, length = 100, fill = '█',
                                  printEnd = "\r")
            
        
    def receive(self,*timeout):
        """Returns a list containing the available data from the 
            serial, received from the transmission"""
        if(timeout):
            try:
                self.serialPort.open()
                self.serialPort.close()
                print('Device recognized')
            except serial.SerialException:
                sys.exit( "No device connected or recognized" )
                      
            fs = 22050
            time.sleep(timeout[0])
            empty_sig = numpy.random.normal( size=int(float(timeout[0])*fs),                           
                                                 scale=Audio.stdofn)
            return empty_sig            
        
        # list for storing read values
        read_values = []
        # trigger for acknowledging transmission
        trigsig = 0
        # open the port (assert it was closed)
        try:
            self.serialPort.open()
        except serial.serialutil.SerialException:
            self.serialPort.close()
            self.serialPort.open()
        
        # loop until all data is received
        while 1: 
            # read serial and decode 
            readByte = self.serialPort.readline().decode("utf-8")
            # Byte found
            if readByte != '':
                # acknowledge loop on first iteration
                if trigsig == 0:
                    print('started')
                    trigsig = 1
                # store byte
                read_values.append(readByte)
                #print(readByte)
            # exit loop with end byte    
            if '.99' in readByte:
                print('done')
                self.serialPort.close()
                full_sig,noise_sig = Audio.decode_receive(read_values)
                return full_sig,noise_sig
                break

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '',
                      decimals = 1, length = 100, fill = '█',
                      printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()


class CommESP:
    
    baudrate = 115200
    
    def __init__(self):       
        lstports = list( serial.tools.list_ports.comports() )                   # list ports               
        self.port_nr = ''                                                       # create an empty port number
        for n in lstports:                                                      # find the port with arduino on its name    
                if n.description.startswith( "Silicon" ):                       
                    self.port_nr = n.device                                     # port name of the arduino prort
        if self.port_nr == '':
            sys.exit("No device connected or recognized")                       # if no ports are found, exit the program
        # alternative way of declaring
        # pp = [lstports[i].device for i in range(len(lstports)) if lstports[i].description.startswith("Arduino")]
        self.serialPort = serial.Serial (                                       # create serial object
                self.port_nr, self.baudrate, timeout = 0 , rtscts = True )        
        self.serialPort.close()                                                 # closing serial prevents "open" errors in future class instantiations
        
        
    def write(self,audio_data):
        """Comm.write(processed_audio) takes an audio file from Audio.adapt()
            and writes to the serial port"""
        self.serialPort.close()        
        for x in range(len(audio_data)): 
            self.serialPort.open()            
            self.serialPort.write(audio_data[x])            
            self.serialPort.close()
            
        
    def receive(self):
        """Returns a list containing the available data from the 
            serial, received from the transmission"""
        # list for storing read values
        read_values = []
        # trigger for acknowledging transmission
        trigsig = 0
        # open the port (assert it was closed)
        try:
            self.serialPort.open()
        except serial.serialutil.SerialException:
            self.serialPort.close()
            self.serialPort.open()
        
        # loop until all data is received
        while 1:
           
            try:
                readByte = self.serialPort.readline().decode("utf-8")            # read serial and decode
            except UnicodeDecodeError:
                pass
            # Byte found
            if readByte != '':
                print(readByte)
                # acknowledge loop on first iteration
                if trigsig == 0:
                    print('started')
                    trigsig = 1
                # store byte
                read_values.append(readByte)
                #print(readByte)
            # exit loop with end byte    
            if '.99' in readByte:
                print('done')
                self.serialPort.close()
                return read_values
                break
            
"""
Thanks to Greenstick from question 3173320 in stackoverflow
"""
    