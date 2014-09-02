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
LAUNCH_GRID = [0,1,2,3,4,5,6,7,16,17,18,19,20,21,22,23,32,33,34,35,36,37,38,39,48,49,50,51,52,53,54,55,64,65,66,67,68,69,70,71,80,81,82,83,84,85,86,87,96,97,98,99,100,101,102,103,112,113,114,115,116,117,118,119]  #there are 64 of these
LAUNCH_SIDE = [8,24,40,56,72,88,104,120]    #there are 8 of these
LAUNCH_TOP = [104,105,106,107,108,109,110,111] #there are 8 of these

class LaunchpadM4L(ControlSurface):
  __module__ = __name__
  __doc__ = " LaunchpadM4L controller script "

  def __init__(self, c_instance):
    super(LaunchpadM4L, self).__init__(c_instance)
    with self.component_guard():
      self._host_name = 'LaunchpadM4L'
      self._color_type = 'Launchpad'
      self.log_message("--------------= LaunchpadM4L log BEGIN SCRIPT =--------------")
      self._setup_controls()
      
  """script initialization methods"""
  
  def _setup_controls(self):
    is_momentary = True
    self._grid = [None for index in range(64)]
    self._side = [None for index in range(8)]
    self._top = [None for index in range(8)]
    
    for index in range(64):
      self._grid[index] = ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, LAUNCH_GRID[index])
      self._grid[index].name = 'grid[' + str(index) + ']'
    for index in range(8):
      self._side[index] = ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, LAUNCH_SIDE[index])
      self._side[index].name = 'side[' + str(index) + ']'
    for index in range(8):
      self._top[index] = ButtonElement(is_momentary, MIDI_CC_TYPE, CHANNEL, LAUNCH_TOP[index])
      self._top[index].name = 'top[' + str(index) + ']'
    
  def receive_value(self, value):
    self._value = value
    

    
  """LividBaseM4L script disconnection"""
  def disconnect(self):
    self.log_message("--------------= LaunchpadM4L log END =--------------")
    ControlSurface.disconnect(self)
    return None