# http://julienbayle.net

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
from _Framework.MixerComponent import MixerComponent # Class encompassing several channel strips to form a mixer
from _Framework.ModeSelectorComponent import ModeSelectorComponent # Class for switching between modes, handle several functions with few controls
from _Framework.NotifyingControlElement import NotifyingControlElement # Class representing control elements that can send values
from _Framework.SceneComponent import SceneComponent # Class representing a scene in Live
from _Framework.SessionComponent import SessionComponent # Class encompassing several scene to cover a defined section of Live's session
from _Framework.SessionZoomingComponent import SessionZoomingComponent # Class using a matrix of buttons to choose blocks of clips in the session
from _Framework.SliderElement import SliderElement # Class representing a slider on the controller
from _Framework.TrackEQComponent import TrackEQComponent # Class representing a track's EQ, it attaches to the last EQ device in the track
from _Framework.TrackFilterComponent import TrackFilterComponent # Class representing a track's filter, attaches to the last filter in the track
from _Framework.TransportComponent import TransportComponent # Class encapsulating all functions in Live's transport section


""" Here we define some global variables """
CHANNEL = 0
CODE_ENC = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32]
CODE_ENCBTN = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32]
CODE_BTN = [33,34,35,36,37,38,39,40,41,42,43,44,45]
CODE_ENCRING = [33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64]

class LividCodeM4L(ControlSurface):
	__module__ = __name__
	__doc__ = " LividCodeM4L controller script "

	def __init__(self, c_instance):
		super(LividCodeM4L, self).__init__(c_instance)
		with self.component_guard():
			self._host_name = 'LividCode'
			self._color_type = 'Code'
			self.log_message("--------------= LividCodeM4L log START =--------------") 
			self._setup_controls()
			
	"""script initialization methods"""
	
	def _setup_controls(self):
		is_momentary = True
		self._encoder = [None for index in range(32)]	
		self._encoder_button = [None for index in range(32)]
		self._button = [None for index in range(13)]
		for index in range(32):
			self._encoder[index] = EncoderElement(MIDI_CC_TYPE, CHANNEL,  CODE_ENC[index], Live.MidiMap.MapMode.absolute)
			self._encoder[index].name = 'enc[' + str(index) + ']'
		for index in range(32):
			self._encoder_button[index] = ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, CODE_ENCBTN[index])
			self._encoder_button[index].name = 'encbtn[' + str(index) + ']'
		for index in range(13):
			self._button[index] = ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, CODE_BTN[index])
			self._button[index].name = 'btn[' + str(index) + ']'
		for index in range(32):
			self._encoder[index] = EncoderElement(MIDI_CC_TYPE, CHANNEL,  CODE_ENCRING[index], Live.MidiMap.MapMode.absolute)
			self._encoder[index].name = 'encring[' + str(index) + ']'

	def receive_value(self, value):
		self._value = value
		self.log_message("rx: "+value)

	"""LividCodeM4L script disconnection"""
	def disconnect(self):
		self.log_message("--------------= LividCodeM4L log END =--------------")
		ControlSurface.disconnect(self)
		return None