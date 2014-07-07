# amounra 0513 : http://www.aumhaa.com


from __future__ import with_statement
import Live
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
from _Framework.DeviceComponent import DeviceComponent # Class representing a device in Live
from _Framework.EncoderElement import EncoderElement # Class representing a continuous control on the controller
from _Framework.InputControlElement import * # Base class for all classes representing control elements on a controller
from _Framework.MixerComponent import MixerComponent # Class encompassing several channel strips to form a mixer
from _Framework.ModeSelectorComponent import ModeSelectorComponent # Class for switching between modes, handle several functions with few controls
from _Framework.NotifyingControlElement import NotifyingControlElement # Class representing control elements that can send values
from _Framework.SceneComponent import SceneComponent # Class representing a scene in Live
from _Framework.SessionComponent import SessionComponent # Class encompassing several scene to cover a defined section of Live's session
from _Framework.SessionZoomingComponent import DeprecatedSessionZoomingComponent as SessionZoomingComponent # Class using a matrix of buttons to choose blocks of clips in the session
from _Framework.SliderElement import SliderElement # Class representing a slider on the controller
from VCM600.TrackEQComponent import TrackEQComponent # Class representing a track's EQ, it attaches to the last EQ device in the track
from VCM600.TrackFilterComponent import TrackFilterComponent # Class representing a track's filter, attaches to the last filter in the track
from _Framework.TransportComponent import TransportComponent # Class encapsulating all functions in Live's transport section
from _Framework.M4LInterfaceComponent import M4LInterfaceComponent

"""Custom files, overrides, and files from other scripts"""
from _Mono_Framework.MonoButtonElement import MonoButtonElement
from _Mono_Framework.MonoEncoderElement import MonoEncoderElement
from _Mono_Framework.MonoBridgeElement import MonoBridgeElement
from _Mono_Framework.Debug import *
from Map import *


""" Here we define some global variables """
switchxfader = (240, 00, 01, 97, 02, 15, 01, 247)
switchxfaderrgb = (240, 00, 01, 97, 07, 15, 01, 247)
assigncolors = (240, 00, 01, 97, 07, 34, 00, 07, 03, 06, 05, 01, 02, 04, 247)
assign_default_colors = (240, 00, 01, 97, 07, 34, 00, 07, 06, 05, 01, 04, 03, 02, 247)
check_model = (240, 126, 127, 6, 1, 247)

""" Here we add an override to the MixerComponent to include return channels in our mixer """

class AliasMixerComponent(MixerComponent):


	def tracks_to_use(self):
		return tuple(self.song().visible_tracks) + tuple(self.song().return_tracks)
	


class Alias(ControlSurface):
	__module__ = __name__
	__doc__ = " Alias 8 controller script "


	def __init__(self, c_instance):
		super(Alias, self).__init__(c_instance)
		with self.component_guard():
			self._host_name = 'Alias'
			self._color_type = 'OhmRGB'
			self.log_message("--------------= Alias log opened =--------------") 
			self._rgb = 0
			self._timer = 0
			self.flash_status = 1
			self._clutch_device_selection = False
			self._touched = 0
			self._update_linked_device_selection = None
			self._setup_monobridge()
			self._setup_controls()
			self._setup_m4l_interface()
			self._setup_mixer_control()
			self._setup_session_control()
			self._setup_mixer_nav() 
	

	"""script initialization methods"""
	def _setup_monobridge(self):
		self._monobridge = MonoBridgeElement(self)
		self._monobridge.name = 'MonoBridge'
	

	def _setup_controls(self):
		is_momentary = True
		self._fader = [MonoEncoderElement(MIDI_CC_TYPE, CHANNEL, ALIAS_FADERS[index], Live.MidiMap.MapMode.absolute, 'Fader_' + str(index), index, self) for index in range(9)]
		self._button = [MonoButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, ALIAS_BUTTONS[index], 'Button_' + str(index), self) for index in range(16)]
		self._dial = [MonoEncoderElement(MIDI_CC_TYPE, CHANNEL, ALIAS_DIALS[index], Live.MidiMap.MapMode.absolute, 'Dial_' + str(index), index + 8, self) for index in range(16)]
		self._encoder = MonoEncoderElement(MIDI_CC_TYPE, CHANNEL, ALIAS_ENCODER, Live.MidiMap.MapMode.absolute, 'Encoder', 0, self)
	

	def _setup_m4l_interface(self):
		self._m4l_interface = M4LInterfaceComponent(controls=self.controls, component_guard=self.component_guard)
		self.get_control_names = self._m4l_interface.get_control_names
		self.get_control = self._m4l_interface.get_control
		self.grab_control = self._m4l_interface.grab_control
		self.release_control = self._m4l_interface.release_control
	

	def _setup_mixer_control(self):
		is_momentary = True
		self._num_tracks = (8) #A mixer is one-dimensional; 
		self._mixer = AliasMixerComponent(8, 0, False, False)
		self._mixer.name = 'Mixer'
		self._mixer.set_track_offset(0) #Sets start point for mixer strip (offset from left)
		for index in range(8):
			self._mixer.channel_strip(index).set_volume_control(self._fader[index])
			self._mixer.channel_strip(index).set_send_controls(tuple([self._dial[index], self._dial[index+8]]))
			self._mixer.channel_strip(index).set_mute_button(self._button[index])
			self._button[index].set_on_off_values(MUTE_TOG, 0)
			self._mixer.channel_strip(index)._invert_mute_feedback = True
			self._mixer.channel_strip(index).set_arm_button(self._button[index+8])
			self._button[index+8].set_on_off_values(REC_TOG, 0)
			self._mixer.channel_strip(index).name = 'Mixer_ChannelStrip_' + str(index)
		self._mixer.master_strip().set_volume_control(self._fader[8])
		self.song().view.selected_track = self._mixer.channel_strip(0)._track 
	

	def _setup_session_control(self):
		self._session = SessionComponent(8, 1)
		self._session.set_mixer(self._mixer)
		self.set_highlighting_session_component(self._session)
	

	def _setup_mixer_nav(self):
		if not self._encoder.value_has_listener(self._nav_change):
			self._encoder.add_value_listener(self._nav_change)	
	


	"""shift/zoom methods"""
	def _nav_change(self, value):
		self._session.set_offsets(int((float(value)/float(127))*max(8, len(self._mixer.tracks_to_use())-8)), self._session._scene_offset)
	


	"""called on timer"""
	def update_display(self):
		ControlSurface.update_display(self)
		self._timer = (self._timer + 1) % 256
		self.flash()
	

	def flash(self):
		if(self.flash_status > 0):
			for control in self.controls:
				if isinstance(control, MonoButtonElement):
					control.flash(self._timer)
	


	"""m4l bridge"""
	def generate_strip_string(self, display_string):
		NUM_CHARS_PER_DISPLAY_STRIP = 12
		if (not display_string):
			return (' ' * NUM_CHARS_PER_DISPLAY_STRIP)
		if ((len(display_string.strip()) > (NUM_CHARS_PER_DISPLAY_STRIP - 1)) and (display_string.endswith('dB') and (display_string.find('.') != -1))):
			display_string = display_string[:-2]
		if (len(display_string) > (NUM_CHARS_PER_DISPLAY_STRIP - 1)):
			for um in [' ',
			 'i',
			 'o',
			 'u',
			 'e',
			 'a']:
				while ((len(display_string) > (NUM_CHARS_PER_DISPLAY_STRIP - 1)) and (display_string.rfind(um, 1) != -1)):
					um_pos = display_string.rfind(um, 1)
					display_string = (display_string[:um_pos] + display_string[(um_pos + 1):])
		else:
			display_string = display_string.center((NUM_CHARS_PER_DISPLAY_STRIP - 1))
		ret = u''
		for i in range((NUM_CHARS_PER_DISPLAY_STRIP - 1)):
			if ((ord(display_string[i]) > 127) or (ord(display_string[i]) < 0)):
				ret += ' '
			else:
				ret += display_string[i]

		ret += ' '
		ret = ret.replace(' ', '_')
		assert (len(ret) == NUM_CHARS_PER_DISPLAY_STRIP)
		return ret
	

	def notification_to_bridge(self, name, value, sender):
		if isinstance(sender, MonoEncoderElement):
			self._monobridge._send(sender.name, 'lcd_name', str(self.generate_strip_string(name)))
			self._monobridge._send(sender.name, 'lcd_value', str(self.generate_strip_string(value)))
	

	def touched(self):
		if self._touched is 0:
			self._monobridge._send('touch', 'on')
			self.schedule_message(2, self.check_touch)
		self._touched +=1
	

	def check_touch(self):
		if self._touched > 5:
			self._touched = 5
		elif self._touched > 0:
			self._touched -= 1
		if self._touched is 0:
			self._monobridge._send('touch', 'off')
		else:
			self.schedule_message(2, self.check_touch)
	


	"""general functionality"""
	def allow_updates(self, allow_updates):
		for component in self.components:
			component.set_allow_update(int(allow_updates!=0))
	

	def disconnect(self):
		if self._encoder.value_has_listener(self._nav_change):
			self._encoder.remove_value_listener(self._nav_change)
		self.log_message("--------------= Alias log closed =--------------")
		super(Alias, self).disconnect()
		rebuild_sys()
	

	def handle_sysex(self, midi_bytes):
		pass
	

	def device_follows_track(self, val):
		self._device_selection_follows_track_selection = (val == 1)
		return self
	

	def assign_alternate_mappings(self):
		pass
	

	def _get_num_tracks(self):
		return self.num_tracks
	

	def _on_device_changed(self, device):
		#self.log_message('new device ' + str(type(device)))
		if self._update_linked_device_selection != None:
			self._update_linked_device_selection(device)
	

	def _on_session_offset_changes(self):
		if self._r_function_mode._mode_index in range(0,3):
			self._mem[int(self._r_function_mode._mode_index)] = self._session2.track_offset()
	

	def connect_script_instances(self, instanciated_scripts):
		pass
	



#	a