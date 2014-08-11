# by amounra 0413 : http://www.aumhaa.com

from __future__ import with_statement
import Live
import time
import math

""" _Framework files """
from _Framework.ButtonElement import ButtonElement # Class representing a button a the controller
from _Framework.ButtonMatrixElement import ButtonMatrixElement # Class representing a 2-dimensional set of buttons
from _Framework.ChannelStripComponent import ChannelStripComponent # Class attaching to the mixer of a given track
from _Framework.ClipSlotComponent import ClipSlotComponent # Class representing a ClipSlot within Live
from _Framework.CompoundComponent import CompoundComponent # Base class for classes encompasing other components to form complex components
from _Framework.ControlElement import ControlElement # Base class for all classes representing control elements on a controller 
from _Framework.ControlSurface import ControlSurface # Central base class for scripts based on the new Framework
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent # Base class for all classes encapsulating functions in Live
from _Framework.EncoderElement import EncoderElement # Class representing a continuous control on the controller
from _Framework.InputControlElement import * # Base class for all classes representing control elements on a controller
from VCM600.MixerComponent import MixerComponent # Class encompassing several channel strips to form a mixer
from _Framework.ModeSelectorComponent import ModeSelectorComponent # Class for switching between modes, handle several functions with few controls
from _Framework.NotifyingControlElement import NotifyingControlElement # Class representing control elements that can send values
from _Framework.SceneComponent import SceneComponent # Class representing a scene in Live
from _Framework.SessionComponent import SessionComponent # Class encompassing several scene to cover a defined section of Live's session
from _Framework.SessionZoomingComponent import DeprecatedSessionZoomingComponent as SessionZoomingComponent# Class using a matrix of buttons to choose blocks of clips in the session


""" Here we define some global variables """


class Tweaker(ControlSurface):
	__module__ = __name__
	__doc__ = " MonOhmod companion controller script "


	def __init__(self, c_instance):
		"""everything except the '_on_selected_track_changed' override and 'disconnect' runs from here"""
		ControlSurface.__init__(self, c_instance)
		with self.component_guard():
			self._update_linked_device_selection = None
			self._tweaker_version = '0.4'
			self.log_message("--------------= Tweaker Mixer " + str(self._tweaker_version) + " log opened =--------------") 
			self._update_linked_device_selection = None
			self._setup_mixer_control()
			self._setup_session_control()
	

	"""script initialization methods"""
	def _setup_controls(self):
		is_momentary = True
		self._grid = [None for index in range(8)]
		for column in range(8):
			self._grid[column] = [FlashingButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, column + (row * 8), 'Grid_' + str(column) + '_' + str(row), self) for row in range(4)]
		self._button = [FlashingButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, TWEAKER_BUTTONS[index], 'Button_' + str(index), self) for index in range(len(TWEAKER_BUTTONS))]
		self._nav = [FlashingButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, TWEAKER_NAVS[index], 'Nav_' + str(index), self) for index in range(len(TWEAKER_NAVS))]
		self._encoder_buttons = [FlashingButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, TWEAKER_ENCODER_BUTTONS[index], 'Encoder_Button_' + str(index), self) for index in range(len(TWEAKER_ENCODER_BUTTONS))]
		self._dial = [EncoderElement(MIDI_CC_TYPE, CHANNEL, TWEAKER_DIALS[index], Live.MidiMap.MapMode.absolute) for index in range(len(TWEAKER_DIALS))]
		self._fader = [EncoderElement(MIDI_CC_TYPE, CHANNEL, TWEAKER_FADERS[index], Live.MidiMap.MapMode.absolute) for index in range(len(TWEAKER_FADERS))]
		self._crossfader = EncoderElement(MIDI_CC_TYPE, CHANNEL, CROSSFADER, Live.MidiMap.MapMode.absolute)
		self._encoder = [EncoderElement(MIDI_CC_TYPE, CHANNEL, TWEAKER_ENCODERS[index], Live.MidiMap.MapMode.absolute) for index in range(len(TWEAKER_ENCODERS))]
		self._pad = [FlashingButtonElement(not is_momentary, MIDI_CC_TYPE, CHANNEL, TWEAKER_PADS[index], 'Pad_' + str(index), self) for index in range(len(TWEAKER_PADS))]
		self._matrix = ButtonMatrixElement()
		self._matrix.name = 'Matrix'
		for row in range(4):
			button_row = []
			for column in range(7):
				button_row.append(self._grid[column][row])
			self._matrix.add_row(tuple(button_row)) 	
	

	def _setup_transport_control(self):
		self._transport = TransportComponent() 
		self._transport.name = 'Transport'
	

	def _setup_mixer_control(self):
		is_momentary = True
		self._num_tracks = (2) #A mixer is one-dimensional; 
		self._mixer = MixerComponent(2, 0, False, True)
		self._mixer.name = 'Mixer'
		self._mixer.tracks_to_use = self._mixer_tracks_to_use(self._mixer)
		self._mixer.set_track_offset(0) #Sets start point for mixer strip (offset from left)
	

	def _setup_session_control(self):
		is_momentary = True
		num_tracks = 2
		num_scenes = 3 
		self._session = SessionComponent(num_tracks, num_scenes)
		self._session.name = "Session"
		self._session.set_offsets(0, 0)
		self._session.set_mixer(self._mixer)
		self.set_highlighting_session_component(self._session)
	

	"""general functionality"""
	
	def allow_updates(self, allow_updates):
		for component in self.components:
			component.set_allow_update(int(allow_updates!=0))
	

	def disconnect(self):
		"""clean things up on disconnect"""
		if self._session._is_linked():
			self._session._unlink()
		self.log_message("--------------= Tweaker Mixer " + str(self._tweaker_version) + " log closed =--------------") #Create entry in log file
		ControlSurface.disconnect(self)
		return None
	

	def connect_script_instances(self, instanciated_scripts):
		link = False
		for s in instanciated_scripts:
			if '_tweaker_version' in dir(s):
				if s._tweaker_version == self._tweaker_version:
					link = True
			if not s is self:
				s._linked_session = self._session
					#break	
		if link is True:
			if not self._session._is_linked():
				#self._session.set_offsets(0, 0)
				self._session._link()
	

	def _mixer_tracks_to_use(self, mixer):
		def tracks_to_use():
			return tuple(self.song().visible_tracks) + tuple(self.song().return_tracks)
		return tracks_to_use

#	a