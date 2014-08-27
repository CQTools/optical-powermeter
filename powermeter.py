# -*- coding: utf-8 -*-
"""
Created on Mon Aug 25 19:12:31 2014

@author: nick
"""

import serial
import json

class pmcommunication(object):
# Module for communicating with the power meter    
    baudrate = 115200
    
    def __init__(self, port):
        self.serial = self._open_port(port)
        self.data = self._read_cal_file() #reads in calibration file once stored as object data
        
    def _open_port(self, port):
        ser = serial.Serial(port, self.baudrate, timeout=5)
        ser.readline()
        ser.timeout = 1
        return ser
    
    def _serial_write(self, string):
        self.serial.write(string + '\n')
    
    def _serial_read(self):
        msg_string = self.serial.readline()
        # Remove any linefeeds etc
        msg_string = msg_string.rstrip()
        return msg_string
    
    def reset(self):
        self._serial_write('*RST')
        return self._serial_read()
        
    def get_voltage(self):
        self._serial_write('VOLT?')
        return self._serial_read()
    
    
    def set_range(self,value):
        self._serial_write('RANGE'+ str(value))
        self.pm_range = value -1
        return pm_range
    
    def serial_number(self):
        self._serial_write('*IDN?')
        return self._serial_read()

    """this section of the code deals with converting between the voltage value and the
    optical power at the wavelength of interest"""
    
    resistors = [1e6,110e3,10e3,1e3,100]    #sense resistor will fix later
    
    file_name = ('s5106_interpolated.txt')    
    

    
    def _read_cal_file(self):
        f = open(self.file_name,'r')
        x = json.load(f)
        f.close()
        return x
        

    def volt2amp(self,voltage,range_number):
        self.amp = voltage/self.resistors[int(range_number)]
        return self.amp
								
    
    def amp2power(self,wavelength):
        voltage = float(self.get_voltage())
        amp = self.volt2amp(voltage,4)
        xdata = self.data[0]
        ydata = self.data[1]
        i = xdata.index(int(wavelength))
        responsivity = ydata[i]
        power = amp/float(responsivity)
        return power
    
    
       
      
    
    
    