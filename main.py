# -*- coding: utf-8 -*-
"""
Created on Wed Aug 27 11:13:37 2014

@author: nick
"""

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.factory import Factory
from kivy.uix.textinput import TextInput
from kivy.properties import NumericProperty, BooleanProperty, ObjectProperty
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.utils import Platform
from kivy.garden.graph import Graph, MeshLinePlot
from kivy.uix.tabbedpanel import TabbedPanel
import re
import os
import glob
import json

import powermeter as pm


class TabbedPanelItem(TabbedPanel):
     pass



class FloatInput(TextInput):

    pat = re.compile('[^0-9]')
    multiline = False
    halign = 'center'

    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        if '.' in self.text:
            s = re.sub(pat, '', substring)
        else:
            s = '.'.join([re.sub(pat, '', s) for s in substring.split('.', 1)])
        return super(FloatInput, self).insert_text(s, from_undo=from_undo)

class PowerMeterControl(TabbedPanel):
    power = NumericProperty(0)
    voltage = NumericProperty(0)
    wavelength = NumericProperty(780.0)
    connected = BooleanProperty(False)

    graph = Graph(xlabel='X', ylabel='Y', x_ticks_minor=5,
            x_ticks_major=25, y_ticks_major=1,
            y_grid_label=True, x_grid_label=True, padding=5,
            x_grid=True, y_grid=True, ymin=10, ymax=110)
    plot = ObjectProperty(None)

    powermeter = None

    iteration = 0
    #print connection
    def update(self, dt):
        self.voltage = float(self.powermeter.get_voltage())
        self.power = self.amp2power(self.voltage,self.wavelength,int(self.pm_range))
        #print self.powermeter.get_voltage()
      
       
        

        self.iteration += 1

    def update_range(self, value):
        self.pm_range = value
        if self.connected == True:
            self.powermeter.set_range(int(self.pm_range))
        

    def connect_to_powermeter(self, connection):
        if not self.connected:
            if Platform == 'android': #to get access to serial port on android
                os.system("su root chmod 777 " + connection) 
            self.data = self._read_cal_file()
            self.powermeter = pm.pmcommunication(connection)
            Clock.schedule_interval(self.update, 0.5)
            self.connected = True
            plot = MeshLinePlot(color=[1, 0, 0, 1])
            self.plot = plot
            self.ids.graph.add_plot(plot)
 
    def serial_ports_android(self):
        #Lists serial ports
        ports = glob.glob('/dev/ttyACM*')
        return ports
    
    
        """this section of the code deals with converting between the voltage value and the
    optical power at the wavelength of interest"""
    
    resistors = [1e6,110e3,10e3,1e3,100]    #sense resistor will fix later
    
    file_name = 's5106_interpolated.txt'    
    

    
    def _read_cal_file(self):
        f = open(self.file_name,'r')
        x = json.load(f)
        f.close()
        return x
        

    def volt2amp(self,voltage,range_number):
        self.amp = voltage/self.resistors[range_number]
        return self.amp
								
    
    def amp2power(self,voltage,wavelength,range_number):
        amp = self.volt2amp(voltage,range_number-1)
        xdata = self.data[0]
        ydata = self.data[1]
        i = xdata.index(int(wavelength))
        responsivity = ydata[i]
        power = amp/float(responsivity)
        return power
      
class PowermeterApp(App):
    def build(self):
        control = PowerMeterControl()
        return control
    
    def on_pause(self):
        return True
        
    def on_resume(self):
        pass


if __name__ == '__main__':
    PowermeterApp().run()
