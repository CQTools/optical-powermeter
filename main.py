# -*- coding: utf-8 -*-
"""
Created on Wed Aug 27 11:13:37 2014

@author: nick
"""

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.properties import NumericProperty, BooleanProperty, ObjectProperty
from kivy.clock import Clock
from kivy.garden.graph import Graph, MeshLinePlot
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
import re
import os
import glob
import serial

import powermeter as pm



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

class PowerMeterControl(Widget):
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
        self.power = self.powermeter.amp2power(self.wavelength,int(self.pm_range))
        #print self.powermeter.get_voltage()
      
       
        

        self.iteration += 1

#
#    def count_calls(fn):
#        def _counting(*args, **kwargs):
#            _counting.calls += 1
#            return fn(*args, **kwargs)
#        _counting.calls = 0
#    return _counting
#
#    @count_calls
    def update_range(self, value):
        self.pm_range = value
        if self.connected == True:
            self.powermeter.set_range(int(self.pm_range))
        

    def connect_to_powermeter(self, connection):
        if not self.connected:
            #os.system("su root chmod 777 " + connection) #comment this line when debugging on linux
            self.powermeter = pm.pmcommunication(connection)
            Clock.schedule_interval(self.update, 0.2)
            self.connected = True
            plot = MeshLinePlot(color=[1, 0, 0, 1])
            self.plot = plot
            self.ids.graph.add_plot(plot)
 
    def serial_ports_android(self):
        #Lists serial ports
        ports = glob.glob('/dev/ttyACM*')
        return ports
    
      
class PowermeterApp(App):
    def build(self):
        control = PowerMeterControl()
        return control


if __name__ == '__main__':
    PowermeterApp().run()
