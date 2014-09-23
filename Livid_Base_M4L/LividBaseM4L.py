# http://lividinstruments.com

from __future__ import with_statement
import Live
import math

""" _Framework files """
from _Framework.ButtonElement import ButtonElement # Class representing a button a the controller
from _Framework.ButtonMatrixElement import ButtonMatrixElement # Class representing a 2-dimensional set of buttons
from _Framework.ChannelStripComponent import ChannelStripComponent # Class attaching to the mixer of a given track
#from _Framework.ClipSlotComponent import ClipSlotComponent # Class representing a ClipSlot within Live
from _Framework.CompoundComponent import CompoundComponent # Base class for classes encompasing other components to form complex components
from _Framework.ControlElement import ControlElement # Base class for all classes representing control elements on a controller 
from _Framework.ControlSurface import ControlSurface # Central base class for scripts based on the new Framework
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent # Base class for all classes encapsulating functions in Live
from _Framework.DeviceComponent import DeviceComponent # Class representing a device in Live
from _Framework.EncoderElement import EncoderElement # Class representing a continuous control on the controller
from _Framework.InputControlElement import * # Base class for all classes representing control elements on a controller
from VCM600.MixerComponent import MixerComponent # Class encompassing several channel strips to form a mixer
from _Framework.ModeSelectorComponent import ModeSelectorComponent # Class for switching between modes, handle several functions with few controls
from _Framework.NotifyingControlElement import NotifyingControlElement # Class representing control elements that can send values
from _Framework.SceneComponent import SceneComponent # Class representing a scene in Live
from _Framework.SessionComponent import SessionComponent # Class encompassing several scene to cover a defined section of Live's session
from _Framework.SessionZoomingComponent import DeprecatedSessionZoomingComponent as SessionZoomingComponent # Class using a matrix of buttons to choose blocks of clips in the session
from _Framework.SliderElement import SliderElement # Class representing a slider on the controller
from VCM600.TrackEQComponent import TrackEQComponent # Class representing a track's EQ, it attaches to the last EQ device in the track
from VCM600.TrackFilterComponent import TrackFilterComponent # Class representing a track's filter, attaches to the last filter in the track
from _Framework.TransportComponent import TransportComponent # Class encapsulating all functions in Live's transport section


""" Here we define some global variables """
CHANNEL = 0   #main channel (0 - 15)
BASE_PADS = [60, 61, 62, 63, 64, 65, 66, 67, 52, 53, 54, 55, 56, 57, 58, 59, 44, 45, 46, 47, 48, 49, 50, 51, 36, 37, 38, 39, 40, 41, 42, 43]  #there are 32 of these
BASE_TOUCHSTRIPS = [1, 2, 3, 4, 5, 6, 7, 8, 9]    #there are 9 of these
BASE_TOUCHPADS = [10, 11, 12, 13, 14, 15, 16, 17] #there are 8 of these
BASE_BUTTONS = [18, 19, 20, 21, 22, 23, 24, 25]   #there are 8 of these
BASE_RUNNERS = [68, 69, 70, 71, 72, 73, 74, 75]   #there are 8 of these top LEDS
BASE_SIDES = [26,27,28,29,30,31,32,33]   #there are 8 of these side LEDS
BASE_LCDS = [34, 35]

class LividBaseM4L(ControlSurface):
  __module__ = __name__
  __doc__ = " LividBaseM4L controller script "

  def __init__(self, c_instance):
    super(LividBaseM4L, self).__init__(c_instance)
    with self.component_guard():
      self._host_name = 'LividBaseM4L'
      self._color_type = 'Base'
      self.log_message("--------------= LividBaseM4L log BEGIN SCRIPT =--------------")
      self._setup_controls()
      
  """script initialization methods"""
  
  def _setup_controls(self):
    is_momentary = True
    self._tfader = [None for index in range(9)]
    self._tfader_touch = [None for index in range(9)]
    self._pad = [None for index in range(32)]
    self._pad_cc = [None for index in range(32)]
    self._button = [None for index in range(8)]
    self._tbutton = [None for index in range(8)]
    self._runnerled = [None for index in range(8)]
    self._sideled = [None for index in range(8)]
    self._lcd = [None for index in range(2)]
    for index in range(9):
      self._tfader[index] = EncoderElement(MIDI_CC_TYPE, CHANNEL, BASE_TOUCHSTRIPS[index], Live.MidiMap.MapMode.absolute)
      self._tfader[index].name = 'fader[' + str(index) + ']'
    for index in range(9):
      self._tfader_touch[index] = ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, BASE_TOUCHSTRIPS[index])
      self._tfader_touch[index].name = 'fadertouch[' + str(index) + ']'
    for index in range(32):
      self._pad[index] = ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, BASE_PADS[index])
      self._pad[index].name = 'pad[' + str(index) + ']'
    for index in range(32):
      self._pad_cc[index] = EncoderElement(MIDI_CC_TYPE, CHANNEL, BASE_PADS[index], Live.MidiMap.MapMode.absolute)
      self._pad_cc[index].name = 'padcc[' + str(index) + ']'
    for index in range(8):
      self._button[index] = ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, BASE_BUTTONS[index])
      self._button[index].name = 'btn[' + str(index) + ']'
    for index in range(8):
      self._tbutton[index] = ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, BASE_TOUCHPADS[index])
      self._tbutton[index].name = 'topbtn[' + str(index) + ']'   
    for index in range(8):
      self._runnerled[index] = ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, BASE_RUNNERS[index])
      self._runnerled[index].name = 'runnerled[' + str(index) + ']'
    for index in range(8):
      self._sideled[index] = ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, BASE_SIDES[index])
      self._sideled[index].name = 'sideled[' + str(index) + ']'
    for index in range(2):
      self._lcd[index] = ButtonElement(is_momentary, MIDI_CC_TYPE, CHANNEL, BASE_LCDS[index])
      self._lcd[index].name = 'lcd[' + str(index) + ']'
    
  def receive_value(self, value):
    self._value = value
    
  def slider_color(self, value):
    for index in range(9):
      self._send_midi((191,index+10,value))
      
  def aslider_color(self, sli, value):
    self._send_midi((191,sli+10,value))

    
  """LividBaseM4L script disconnection"""
  def disconnect(self):
    self.log_message("--------------= LividBaseM4L log END =--------------")
    ControlSurface.disconnect(self)
    return None