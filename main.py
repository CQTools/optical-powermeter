# -*- coding: utf-8 -*-
"""
Created on Wed Aug 27 11:13:37 2014

@author: nick
"""

from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.properties import NumericProperty, BooleanProperty, ObjectProperty, BoundedNumericProperty,ListProperty, StringProperty
from kivy.clock import Clock
from kivy.utils import platform
from kivy.graphics import Mesh, Color, Rectangle
from kivy.garden.graph import Graph, MeshLinePlot
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.utils import get_color_from_hex as rgb
import re
import os
import glob
import json

import powermeter as pm

from kivy.core.window import Window
#Window.clearcolor = (1, 1, 1, 1)


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
    power = StringProperty('0.0')
    max_power = NumericProperty(0.0)
    voltage = NumericProperty(0)
    tick_color = ListProperty([0,1,0,1])
    wavelength = BoundedNumericProperty(780.0,min=340.0,max=1180,errorhandler=lambda x: 1180 if x > 1180 else 340)
    connected = BooleanProperty(False)
    #canvas.add(Color(1., 1., 0))
    #canvas.add(Rectangle(size=(50, 50)))
    graph_theme = {
                'label_options': {
                'color': rgb('444444'),
                'bold': True},
                'background_color': rgb('f8f8f2'),
                'tick_color': '[1,0,0,1]',
                'border_color': (0,0,0,1),
                'draw_border':True}

    graph = Graph(**graph_theme)


    plot = ObjectProperty(None)

    powermeter = None

    iteration = 0
    #print connection
    def update(self, dt):
        self.voltage = float(self.powermeter.get_voltage())
        self.power = 'f'#self.amp2power(self.voltage,self.wavelength,int(self.pm_range))
        self.power_max()
        #print self.powermeter.get_voltage()
        self.plot.points.append((self.iteration, self.iteration*0.001))
        print self.plot.points
        self.iteration += 1
        if self.iteration > 150:
            self.iteration = 0
            self.plot.points = []
       

    def update_range(self, value):
        self.pm_range = value
        if self.connected == True:
            self.powermeter.set_range(int(self.pm_range))
        

    def connect_to_powermeter(self, connection):
        if not self.connected:
            if platform == 'android': #to get access to serial port on android
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
    
    resistors = [1e6,110e3,10e3,1e3,100]    #sense resistors adjust to what is on the board
    
    file_name = 's5106_interpolated.cal'    #detector calibration file
    

    
    def _read_cal_file(self): # read in calibration file for sensor
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
    
    def format_power(self,power):
        fpower = power*1000
                
        return fpower
    
    def power_max(self):
        if self.max_power < self.power:
            self.max_power = self.power
        return self.max_power
      
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
