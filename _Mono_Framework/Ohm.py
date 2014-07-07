# http://www.aumhaa.com
# by amounra 0313

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

"""Imports from _Mono_Framework"""

from _Mono_Framework.MonoBridgeElement import MonoBridgeElement
from _Mono_Framework.MonoButtonElement import MonoButtonElement
from _Mono_Framework.MonoEncoderElement import MonoEncoderElement
from _Mono_Framework.DeviceSelectorComponent import DeviceSelectorComponent
from _Mono_Framework.ResetSendsComponent import ResetSendsComponent
from _Mono_Framework.DetailViewControllerComponent import DetailViewControllerComponent
from _Mono_Framework.MonomodComponent import MonomodComponent
from _Mono_Framework.LiveUtils import *

"""Custom files, overrides, and files from other scripts"""
from _Generic.Devices import *
from Map import *

""" Here we define some global variables """

switchxfader = (240, 00, 01, 97, 02, 15, 01, 247)
switchxfaderrgb = (240, 00, 01, 97, 07, 15, 01, 247)
assigncolors = (240, 00, 01, 97, 07, 34, 00, 07, 03, 06, 05, 01, 02, 04, 247)
assign_default_colors = (240, 00, 01, 97, 07, 34, 00, 07, 06, 05, 01, 04, 03, 02, 247)
check_model = (240, 126, 127, 6, 1, 247)

class FunctionModeComponent(ModeSelectorComponent):


	def __init__(self, script, callback, *a, **k):
		super(FunctionModeComponent, self).__init__(*a, **k)
		assert hasattr(callback, '__call__')
		self._script = script
		self.update = callback
		self._set_protected_mode_index(0)
	

	def number_of_modes(self):
		return 6
	

	def set_mode_buttons(self, buttons):
		for button in self._modes_buttons:
			button.remove_value_listener(self._mode_value)
		self._modes_buttons = []
		if (buttons != None):
			for button in buttons:
				assert isinstance(button, ButtonElement)
				identify_sender = True
				button.add_value_listener(self._mode_value, identify_sender)
				self._modes_buttons.append(button)
			for index in range(len(self._modes_buttons)):
				if (index == self._mode_index):
					self._modes_buttons[index].turn_on()
				else:
					self._modes_buttons[index].turn_off()
	

	def set_mode_toggle(self, button):
		assert ((button == None) or isinstance(button, ButtonElement))
		if (self._mode_toggle != None):
			self._mode_toggle.remove_value_listener(self._toggle_value)
		self._mode_toggle = button
		if (self._mode_toggle != None):
			self._mode_toggle.add_value_listener(self._toggle_value)
	


class MonomodModeComponent(ModeSelectorComponent):


	def __init__(self, script, callback, *a, **k):
		super(MonomodModeComponent, self).__init__(*a, **k)
		assert hasattr(callback, '__call__')
		self._script = script
		self.update = callback
		self._set_protected_mode_index(0)
	

	def number_of_modes(self):
		return 2
	

	def set_mode_toggle(self, button):
		assert ((button == None) or isinstance(button, ButtonElement))
		if (self._mode_toggle != None):
			self._mode_toggle.remove_value_listener(self._toggle_value)
		self._mode_toggle = button
		if (self._mode_toggle != None):
			self._mode_toggle.add_value_listener(self._toggle_value)
	


class ShiftModeComponent(ModeSelectorComponent):


	def __init__(self, script, callback, *a, **k):
		super(ShiftModeComponent, self).__init__(*a, **k)
		assert hasattr(callback, '__call__')
		self._script = script
		self.update = callback
		self._mode_toggle1 = None
		self._mode_toggle2 = None
		self._toggle1_value = 0
		self._toggle2_value = 0
		self._mode_index = 0
		self._last_mode = 0
		self._set_protected_mode_index(0)
	

	def set_mode_toggle(self, button1, button2):
		assert ((button1 == None) or isinstance(button1, ButtonElement))
		if (self._mode_toggle1 != None):
			self._mode_toggle1.remove_value_listener(self._toggle_value_left)
		self._mode_toggle1 = button1
		if (self._mode_toggle1 != None):
			self._mode_toggle1.add_value_listener(self._toggle_value_left)
		assert ((button2 == None) or isinstance(button2, ButtonElement))
		if (self._mode_toggle2 != None):
			self._mode_toggle2.remove_value_listener(self._toggle_value_right)
		self._mode_toggle2 = button2
		if (self._mode_toggle2 != None):
			self._mode_toggle2.add_value_listener(self._toggle_value_right)
	

	def _toggle_value_left(self, value):
		self._toggle1_value = value
		self._toggle_value(value, 'left')
	

	def _toggle_value_right(self, value):
		self._toggle2_value = value
		self._toggle_value(value, 'right')
	
	
	def _toggle_value(self, value, side):
		assert (self._mode_toggle1 != None)
		assert (self._mode_toggle2 != None)
		assert isinstance(value, int)
		if((value > 0) and ((side is 'left' and self._toggle2_value > 0) or (side is 'right' and self._toggle1_value > 0))):
			if(self._last_mode is 0):
				self._last_mode = 1
				self.set_mode(4) #self.set_mode(self._last_mode)
			else:
				self._last_mode = 0
				#self.set_mode(self._last_mode)
				if(side is 'left'):
					self.set_mode(2)
				if(side is 'right'):
					self.set_mode(3)
		#elif((value > 0) and ((side is 'left' and self._toggle2_value > 0) or (side is 'right' and self._toggle1_value > 0))):	
		elif(value is 0) and (self._toggle1_value is 0) and (self._toggle2_value is 0):
			self.set_mode(self._last_mode)
		elif(value > 0 and self._last_mode is 1):
			self.set_mode(4)
		else:
			if (side is 'left' and value > 0):
				self.set_mode(2)
			elif (side is 'right' and value > 0):
				self.set_mode(3)
	

	def number_of_modes(self):
		return 5
	


class MonOhm(ControlSurface):
	__module__ = __name__
	__doc__ = " Monomodular control script for Ohm64 and OhmRGB "


	def __init__(self, *a, **k):
		super(MonOhm, self).__init__(*a, **k)
		self._monomod_version = 'b995'
		self._codec_version = 'b995'
		self._cntrlr_version = 'b995'
		self._cntrlr = None
		self._host_name = 'MonOhm'
		self._color_type = 'OhmRGB'
		self._update_linked_device_selection = None
		self._link_mixer = LINK_MIXER
		self.hosts = []
		self._bright = True
		self._rgb = 0
		self._timer = 0
		self.flash_status = 1
		self._is_split = True
		self._clutch_device_selection = False
		self._touched = 0
		self._backlight = 127
		self._backlight_type = 'static'
		self._ohm = 127
		self._ohm_type = 'static'
		self._pad_translations = PAD_TRANSLATION
		self._update_linked_device_selection = None
		self._use_pedal = USE_PEDAL
		self._disable_master = DISABLE_MASTER_VOLUME
		self._mem = [4, 8, 12]
		self._mixers = []
		self._sessions = []
		self._zooms = []
		self._function_modes = []
		with self.component_guard():
			self.log_message("<<<<<<<<<<<<<<<<<<<<= MonOhm " + str(self._monomod_version) + " log opened =>>>>>>>>>>>>>>>>>>>") 
			self.log_message("<<<<<<<<<<<<<<<<<<<<= Map file for " + str(MAP_VERSION) + " =>>>>>>>>>>>>>>>>>>>") 
			self._setup_monobridge()
			self._setup_controls()
			self._setup_transport_control() 
			self._setup_mixer_control()
			self._setup_session_control()
			self._setup_device_control()
			self._setup_crossfader()
			self._setup_device_selector()
			self._setup_monomod()
			self._setup_modes() 
			self.song().view.add_selected_track_listener(self._update_selected_device)
			if FORCE_TYPE is True:
				self._rgb = FORCE_COLOR_TYPE
			else:
				self.schedule_message(10, self.query_ohm, None)
		self.show_message('MonOhm Control Surface Loaded')
		self._send_midi(tuple(switchxfader))
		#self._send_midi(tuple(assigncolors))

	

	"""script initialization methods"""
	def query_ohm(self):
		#self.log_message('querying ohm64')
		self._send_midi(tuple(check_model))
	

	def _setup_monobridge(self):
		self._monobridge = MonoBridgeElement(self)
		self._monobridge.name = 'MonoBridge'
	

	def _setup_controls(self):
		is_momentary = True
		self._fader = [None for index in range(8)]
		self._dial = [None for index in range(16)]
		self._button = [None for index in range(8)]
		self._menu = [None for index in range(6)]
		for index in range(8):
			self._fader[index] = MonoEncoderElement(MIDI_CC_TYPE, CHANNEL, OHM_FADERS[index], Live.MidiMap.MapMode.absolute, 'Fader_' + str(index), index, self)
		for index in range(8):
			self._button[index] = MonoButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, OHM_BUTTONS[index], 'Button_' + str(index), self)
		for index in range(16):
			self._dial[index] = MonoEncoderElement(MIDI_CC_TYPE, CHANNEL, OHM_DIALS[index], Live.MidiMap.MapMode.absolute, 'Dial_' + str(index), index + 8, self)
		for index in range(6):
			self._menu[index] = MonoButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, OHM_MENU[index], 'Menu_' + str(index), self)	
		self._crossfader = MonoEncoderElement(MIDI_CC_TYPE, CHANNEL, CROSSFADER, Live.MidiMap.MapMode.absolute, "Crossfader", 24, self)
		self._livid = MonoButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, LIVID, 'Livid_Button', self)
		self._shift_l = MonoButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, SHIFT_L, 'Shift_Button_Left', self)
		self._shift_r = MonoButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, SHIFT_R, 'Shift_Button_Right', self)
		self._matrix = ButtonMatrixElement()
		self._matrix.name = 'Matrix'
		self._monomod = ButtonMatrixElement()
		self._monomod.name = 'Monomod'
		self._grid = [None for index in range(8)]
		for column in range(8):
			self._grid[column] = [None for index in range(8)]
			for row in range(8):
				self._grid[column][row] = MonoButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, (column * 8) + row, 'Grid_' + str(column) + '_' + str(row), self)
		for row in range(5):
			button_row = []
			for column in range(7):
				button_row.append(self._grid[column][row])
			self._matrix.add_row(tuple(button_row)) 
		for row in range(8):
			button_row = []
			for column in range(8):
				button_row.append(self._grid[column][row])
			self._monomod.add_row(tuple(button_row))
		self._dummy_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 15, 125)
		self._dummy_button.name = 'Dummy1'
		self._dummy_button2 = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 15, 126)
		self._dummy_button2.name = 'Dummy2'
		self._dummy_button3 = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 15, 127)
		self._dummy_button2.name = 'Dummy3'
		self._pedal = [None for index in range(8)]
		if self._use_pedal is True:
			for index in range(8):
					self._pedal[index] = EncoderElement(MIDI_CC_TYPE, 0, 25+index, Live.MidiMap.MapMode.absolute)
					self._pedal[index].name = 'Pedal_'+str(index)
					self._pedal[index]._report = False
	

	def _setup_transport_control(self):
		self._transport = TransportComponent() 
		self._transport.name = 'Transport'
	

	def _setup_mixer_control(self):
		is_momentary = True
		self._num_tracks = (4) #A mixer is one-dimensional; 
		self._mixer = MixerComponent(8, 0, False, True)
		self._mixer.name = 'Left_Mixer'
		self._mixer.set_track_offset(0) #Sets start point for mixer strip (offset from left)
		for index in range(4):
			self._mixer.channel_strip(index).set_volume_control(self._fader[index])
		for index in range(8):
			self._mixer.channel_strip(index)._on_cf_assign_changed = self.mixer_on_cf_assign_changed(self._mixer.channel_strip(index))
			self._mixer.channel_strip(index).name = 'Mixer_ChannelStrip_' + str(index)
			self._mixer.track_filter(index).name = 'Mixer_TrackFilter_' + str(index)
			self._mixer.channel_strip(index)._invert_mute_feedback = True
		self.song().view.selected_track = self._mixer.channel_strip(0)._track #set the selected strip to the first track, so that we don't, for example, try to assign a button to arm the master track, which would cause an assertion error
		self._mixer2 = MixerComponent(4, 4, False, False)
		self._mixer2.name = 'Right_Mixer'
		self._mixer2.set_track_offset(4)
		for index in range(4):
			self._mixer2.channel_strip(index)._on_cf_assign_changed = self.mixer_on_cf_assign_changed(self._mixer2.channel_strip(index))
			self._mixer2.channel_strip(index).name = 'Mixer2_ChannelStrip_' + str(index)
			self._mixer2.return_strip(index)._on_cf_assign_changed = self.mixer_on_cf_assign_changed(self._mixer2.return_strip(index))
			self._mixer2.return_strip(index).name = 'Mixer2_ReturnStrip_' + str(index)
			self._mixer2.channel_strip(index).set_volume_control(self._fader[index + 4]) 
			self._mixer2.channel_strip(index)._invert_mute_feedback = True
			self._mixer2.return_strip(index)._invert_mute_feedback = True
		self._mixers = [self._mixer, self._mixer2]
		self._send_reset = ResetSendsComponent(self)
		self._send_reset.name = 'Sends_Reset'
		self._mixer._reassign_tracks()
		self._mixer2._reassign_tracks()
	

	def _setup_session_control(self):
		is_momentary = True
		num_tracks = 4
		num_scenes = 5 
		self._session = SessionComponent(num_tracks, num_scenes)
		self._session.name = "Left_Session"
		self._session.set_offsets(0, 0)	 
		self._session.set_stop_track_clip_value(STOP_CLIP[self._rgb])
		self._scene = [None for index in range(5)]
		for row in range(num_scenes):
			self._scene[row] = self._session.scene(row)
			self._scene[row].name = 'L_Scene_' + str(row)
			for column in range(num_tracks):
				clip_slot = self._scene[row].clip_slot(column)
				clip_slot.name = str(column) + '_Clip_Slot_L_' + str(row)
				clip_slot.set_triggered_to_play_value(CLIP_TRG_PLAY[self._rgb])
				clip_slot.set_triggered_to_record_value(CLIP_TRG_REC[self._rgb])
				clip_slot.set_stopped_value(CLIP_STOP[self._rgb])
				clip_slot.set_started_value(CLIP_STARTED[self._rgb])
				clip_slot.set_recording_value(CLIP_RECORDING[self._rgb])
		self._session.set_mixer(self._mixer)
		self._session_zoom = SessionZoomingComponent(self._session)	 
		self._session_zoom.name = 'L_Session_Overview'
		self._session_zoom.set_stopped_value(ZOOM_STOPPED[self._rgb])
		self._session_zoom.set_playing_value(ZOOM_PLAYING[self._rgb])
		self._session_zoom.set_selected_value(ZOOM_SELECTED[self._rgb])
		self._session_zoom._zoom_button = (self._dummy_button)
		self._session_zoom.set_enabled(True) 
		self._session2 = SessionComponent(num_tracks, num_scenes)
		self._session2.name = 'Right_Session'
		self._session2.set_offsets(4, 0)
		self._session2.set_stop_track_clip_value(STOP_CLIP[self._rgb])
		self._scene2 = [None for index in range(5)]
		for row in range(num_scenes):
			self._scene2[row] = self._session2.scene(row)
			self._scene2[row].name = 'R_Scene_' + str(row)
			for column in range(num_tracks):
				clip_slot = self._scene2[row].clip_slot(column)
				clip_slot.name = str(column) + '_Clip_Slot_R_' + str(row)
				clip_slot.set_triggered_to_play_value(CLIP_TRG_PLAY[self._rgb])
				clip_slot.set_triggered_to_record_value(CLIP_TRG_REC[self._rgb])
				clip_slot.set_stopped_value(CLIP_STOP[self._rgb])
				clip_slot.set_started_value(CLIP_STARTED[self._rgb])
				clip_slot.set_recording_value(CLIP_RECORDING[self._rgb])
		self._session2.set_mixer(self._mixer2)
		self._session2.add_offset_listener(self._on_session_offset_changes)
		self._session_zoom2 = SessionZoomingComponent(self._session2)	   
		self._session_zoom2.name = 'R_Session_Overview'
		self._session_zoom2.set_stopped_value(ZOOM_STOPPED[self._rgb])
		self._session_zoom2.set_playing_value(ZOOM_PLAYING[self._rgb])
		self._session_zoom2.set_selected_value(ZOOM_SELECTED[self._rgb])
		self._session_zoom.set_enabled(True) 
		self._session_zoom2._zoom_button = (self._dummy_button2)
		self._session_main = SessionComponent(8, num_scenes)
		self._session_main.name = 'Main_Session'
		self._session_main.set_stop_track_clip_value(STOP_CLIP[self._rgb])
		self._scene_main = [None for index in range(5)]
		for row in range(num_scenes):
			self._scene_main[row] = self._session_main.scene(row)
			self._scene_main[row].name = 'M_Scene_' + str(row)
			for column in range(8):
				clip_slot = self._scene_main[row].clip_slot(column)
				clip_slot.name = str(column) + '_Clip_Slot_M_' + str(row)
				clip_slot.set_triggered_to_play_value(CLIP_TRG_PLAY[self._rgb])
				clip_slot.set_triggered_to_record_value(CLIP_TRG_REC[self._rgb])
				clip_slot.set_stopped_value(CLIP_STOP[self._rgb])
				clip_slot.set_started_value(CLIP_STARTED[self._rgb])
				clip_slot.set_recording_value(CLIP_RECORDING[self._rgb])
		self._session_main.set_mixer(self._mixer)
		self._session_zoom_main = SessionZoomingComponent(self._session_main)
		self._session_zoom_main.name = 'M_Session_Overview'
		self._session_zoom_main.set_stopped_value(ZOOM_STOPPED[self._rgb])
		self._session_zoom_main.set_playing_value(ZOOM_PLAYING[self._rgb])
		self._session_zoom_main.set_selected_value(ZOOM_SELECTED[self._rgb])
		self._session_zoom_main.set_enabled(True)
		self._session_zoom_main._zoom_button = (self._dummy_button3)
		self._sessions = [self._session, self._session2, self._session_main]
		self._zooms = [self._session_zoom, self._session_zoom2, self._session_zoom_main]
	

	def _assign_session_colors(self):
		num_tracks = 4
		num_scenes = 5 
		self._session.set_stop_track_clip_value(STOP_ALL[self._rgb])
		self._session2.set_stop_track_clip_value(STOP_ALL[self._rgb])
		self._session_main.set_stop_track_clip_value(STOP_ALL[self._rgb])
		for row in range(num_scenes): 
			for column in range(num_tracks):
				self._scene[row].clip_slot(column).set_triggered_to_play_value(CLIP_TRG_PLAY[self._rgb])
				self._scene[row].clip_slot(column).set_triggered_to_record_value(CLIP_TRG_REC[self._rgb])
				self._scene[row].clip_slot(column).set_stopped_value(CLIP_STOP[self._rgb])
				self._scene[row].clip_slot(column).set_started_value(CLIP_STARTED[self._rgb])
				self._scene[row].clip_slot(column).set_recording_value(CLIP_RECORDING[self._rgb])	
				self._scene2[row].clip_slot(column).set_triggered_to_play_value(CLIP_TRG_PLAY[self._rgb])
				self._scene2[row].clip_slot(column).set_triggered_to_record_value(CLIP_TRG_REC[self._rgb])
				self._scene2[row].clip_slot(column).set_stopped_value(CLIP_STOP[self._rgb])
				self._scene2[row].clip_slot(column).set_started_value(CLIP_STARTED[self._rgb])
				self._scene2[row].clip_slot(column).set_recording_value(CLIP_RECORDING[self._rgb])	
		for row in range(num_scenes): 
			for column in range(8):
				self._scene_main[row].clip_slot(column).set_triggered_to_play_value(CLIP_TRG_PLAY[self._rgb])
				self._scene_main[row].clip_slot(column).set_triggered_to_record_value(CLIP_TRG_REC[self._rgb])
				self._scene_main[row].clip_slot(column).set_stopped_value(CLIP_STOP[self._rgb])
				self._scene_main[row].clip_slot(column).set_started_value(CLIP_STARTED[self._rgb])
				self._scene_main[row].clip_slot(column).set_recording_value(CLIP_RECORDING[self._rgb])		
		self._session_zoom.set_stopped_value(ZOOM_STOPPED[self._rgb])
		self._session_zoom.set_playing_value(ZOOM_PLAYING[self._rgb])
		self._session_zoom.set_selected_value(ZOOM_SELECTED[self._rgb])
		self._session_zoom2.set_stopped_value(ZOOM_STOPPED[self._rgb])
		self._session_zoom2.set_playing_value(ZOOM_PLAYING[self._rgb])
		self._session_zoom2.set_selected_value(ZOOM_SELECTED[self._rgb])
		self._session_zoom_main.set_stopped_value(ZOOM_STOPPED[self._rgb])
		self._session_zoom_main.set_playing_value(ZOOM_PLAYING[self._rgb])
		self._session_zoom_main.set_selected_value(ZOOM_SELECTED[self._rgb])
		self.refresh_state()
	

	def _setup_device_control(self):
		self._device = DeviceComponent()
		self._device.name = 'Device_Component'
		self._device.set_device = self.device_set_device(self._device)
		self._device._is_banking_enabled = self.device_is_banking_enabled(self._device)
		self.set_device_component(self._device)
		#self.bank = DeviceCallbackComponent(self._device, 1)
		#self.bank.name = 'Device_Bank'
		#self.device_instance = DeviceCallbackComponent(self._device, 2)
		#self.device_instance.name = 'Device_Instance'
		self._device_navigator = DetailViewControllerComponent()
		self._device_navigator.name = 'Device_Navigator'
		self._device_selection_follows_track_selection = FOLLOW
		self._device.set_parameter_controls(tuple([self._dial[index] for index in range(8)]))
		self._device.set_enabled(False)
	

	def _setup_crossfader(self):
		self._mixer.set_crossfader_control(self._crossfader)
	

	def _setup_device_selector(self):
		self._device_selector = DeviceSelectorComponent(self)
		self._device_selector.name = 'Device_Selector'
	

	def _setup_monomod(self):
		self._host = MonomodComponent(self)
		self._host.name = 'Monomod_Host'
		self._host._host_name = 'MonOhm'
		self.hosts = [self._host]
	

	def _setup_modes(self):
		self._monomod_mode = MonomodModeComponent(self, self.monomod_mode_update)
		self._monomod_mode.name = 'Monomod_Mode'
		self._monomod_mode.set_mode_toggle(self._livid)
		self._shift_mode = ShiftModeComponent(self, self.shift_update) 
		self._shift_mode.name = 'Shift_Mode'
		self._shift_mode.set_mode_toggle(self._shift_l, self._shift_r)
		self._l_function_mode = FunctionModeComponent(self, self.l_function_update)
		self._l_function_mode.name = 'Left_Function_Mode'
		self._r_function_mode = FunctionModeComponent(self, self.r_function_update)
		self._r_function_mode.name = 'Right_Function_Mode'
		self._m_function_mode = FunctionModeComponent(self, self.m_function_update)
		self._m_function_mode.name = 'Main_Function_Mode'
		self._function_modes = [self._l_function_mode, self._r_function_mode, self._m_function_mode]
	


	"""shift/zoom methods"""
	def deassign_matrix(self):
		for session in self._sessions:
			session.set_stop_track_clip_buttons(None)
			session.set_track_bank_buttons(None, None)
			session.set_scene_bank_buttons(None, None)
		for zoom in self._zooms:
			zoom.set_button_matrix(None)
			zoom.set_nav_buttons(None, None, None, None)
		for column in range(4):
			self._mixer2.channel_strip(column).set_select_button(None)
			self._mixer2.return_strip(column).set_mute_button(None)
			self._mixer2.return_strip(column).set_solo_button(None)
			self._mixer2.return_strip(column).set_arm_button(None)
			self._mixer2.return_strip(column).set_crossfade_toggle(None)
			self._mixer2.return_strip(column).set_select_button(None)			#shouldn't this be somewhere else?
			self._mixer2.channel_strip(column).set_crossfade_toggle(None)
			self._mixer2.channel_strip(column).set_mute_button(None)
			self._mixer2.channel_strip(column).set_solo_button(None)
			self._mixer2.channel_strip(column).set_arm_button(None)
			for row in range(5):
				self._scene[row].clip_slot(column).set_launch_button(None)
				self._scene2[row].clip_slot(column).set_launch_button(None)
		for index in range(5):
			self._scene[index].set_launch_button(None)
			self._scene2[index].set_launch_button(None)
			self._scene_main[index].set_launch_button(None)
		for column in range(8):
			self._button[column].set_on_off_values(127, 0)
			self._mixer.channel_strip(column).set_select_button(None)
			self._mixer.channel_strip(column).set_crossfade_toggle(None)
			self._mixer.channel_strip(column).set_mute_button(None)
			self._mixer.channel_strip(column).set_solo_button(None)
			self._mixer.channel_strip(column).set_arm_button(None)
			for row in range(5):
				self._scene_main[row].clip_slot(column).set_launch_button(None)
			for row in range(8):
				self._grid[column][row].set_channel(0)
				self._grid[column][row].release_parameter()
				self._grid[column][row].use_default_message()
				self._grid[column][row].set_enabled(True)
				self._grid[column][row].set_on_off_values(127, 0)
				self._grid[column][row].send_value(0, True)
		self._send_reset.set_buttons(tuple(None for index in range(4)))
	

	def zoom_off(self):
		for column in range(4):
			self._grid[column][5].set_on_value(MUTE[self._rgb])
			self._mixer.channel_strip(column).set_mute_button(self._grid[column][5])
			self._grid[column][6].set_on_value(SOLO[self._rgb])
			self._mixer.channel_strip(column).set_solo_button(self._grid[column][6])
			self._grid[column][7].set_on_value(ARM[self._rgb])
			self._mixer.channel_strip(column).set_arm_button(self._grid[column][7])
			for row in range(5):
				self._scene[row].clip_slot(column).set_launch_button(self._grid[column][row])
			if(self._r_function_mode._mode_index in range(0,3)):
				self._grid[column + 4][5].set_on_value(MUTE[self._rgb])
				self._mixer2.channel_strip(column).set_mute_button(self._grid[column + 4][5])
				self._grid[column + 4][6].set_on_value(SOLO[self._rgb])
				self._mixer2.channel_strip(column).set_solo_button(self._grid[column + 4][6])
				self._grid[column + 4][7].set_on_value(ARM[self._rgb])
				self._mixer2.channel_strip(column).set_arm_button(self._grid[column + 4][7])
				for row in range(5):
					self._scene2[row].clip_slot(column).set_launch_button(self._grid[column + 4][row])
			elif(self._r_function_mode._mode_index is 3):
				self._grid[column + 4][5].set_on_value(MUTE[self._rgb])
				self._mixer2.return_strip(column).set_mute_button(self._grid[column + 4][5])
				self._grid[column + 4][6].set_on_value(SOLO[self._rgb])
				self._mixer2.return_strip(column).set_solo_button(self._grid[column + 4][6])
				#self._mixer2.return_strip(column).set_crossfade_toggle(self._grid[column + 4][7])
				for row in range(5):
					self._grid[column + 4][row].send_value(USER1_COLOR[self._rgb], True)
					self._grid[column + 4][row].set_channel(RIGHT_USER1_CHANNEL)
					self._grid[column + 4][row].set_identifier(RIGHT_USER1_MAP[column][row])
					self._grid[column + 4][row].set_enabled(False)	 #this has to happen for translate to work
		if(self._r_function_mode._mode_index is 0):
			for index in range(4):
				self._grid[index + 4][7].send_value(SEND_RESET[self._rgb], True)
			self._send_reset.set_buttons(tuple(self._grid[index + 4][7] for index in range(4)))
	

	def zoom_off_m(self):
		self.deassign_right_controls()
		for column in range(8):
			self._grid[column][5].set_on_value(MUTE[self._rgb])
			self._mixer.channel_strip(column).set_mute_button(self._grid[column][5])
			self._grid[column][6].set_on_value(SOLO[self._rgb])
			self._mixer.channel_strip(column).set_solo_button(self._grid[column][6])
			self._grid[column][7].set_on_value(ARM[self._rgb])
			self._mixer.channel_strip(column).set_arm_button(self._grid[column][7])
			for row in range(5):
				self._scene_main[row].clip_slot(column).set_launch_button(self._grid[column][row])
	

	def zoom_left(self):
		track_stop_buttons = []
		track_stop_buttons2 = []
		for index in range(4):
			self._grid[index][6].set_on_value(CROSSFADE_TOGGLE[self._rgb])
			self._mixer.channel_strip(index).set_crossfade_toggle(self._grid[index][6])
			self._grid[index + 4][6].set_on_value(CROSSFADE_TOGGLE[self._rgb])
			self._mixer2.channel_strip(index).set_crossfade_toggle(self._grid[index + 4][6])
			self._grid[index][7].set_on_value(TRACK_STOP[self._rgb])
			track_stop_buttons.append(self._grid[index][7])
			self._grid[index + 4][7].set_on_value(TRACK_STOP[self._rgb])
			track_stop_buttons2.append(self._grid[index + 4][7])
		for index in range(5):
			self._grid[7][index].set_off_value(SCENE_LAUNCH[self._rgb])
			self._scene[index].set_launch_button(self._grid[7][index])
		self._session.set_stop_track_clip_buttons(tuple(track_stop_buttons))
		self._session2.set_stop_track_clip_buttons(tuple(track_stop_buttons2))
		self._session_zoom.set_button_matrix(self._matrix)
		self._grid[0][5].set_on_value(RECORD[self._rgb])
		self._transport.set_record_button(self._grid[0][5])
		self._grid[1][5].set_on_value(OVERDUB[self._rgb])
		self._transport.set_overdub_button(self._grid[1][5])
		self._grid[2][5].set_on_value(LOOP[self._rgb])
		self._transport.set_loop_button(self._grid[2][5])
		self._grid[3][5].set_on_value(STOP_ALL[self._rgb])	
		self._session.set_stop_all_clips_button(self._grid[3][5])
		for index in range(4):
			self._grid[index + 4][5].send_value(SEND_RESET[self._rgb], True)
		self._send_reset.set_buttons(tuple(self._grid[index + 4][5] for index in range(4)))
		for index in range(4):
			self._button[index + 4].set_off_value(DEVICE_SELECT[self._rgb])
		self._device_selector.assign_buttons(tuple(self._button[index + 4] for index in range(4)), 4)
	
	
	def zoom_right(self):
		track_stop_buttons = []
		track_stop_buttons2 = []
		for index in range(4):
			self._grid[index][6].set_on_value(CROSSFADE_TOGGLE[self._rgb])
			self._mixer.channel_strip(index).set_crossfade_toggle(self._grid[index][6])
			self._grid[index][7].set_off_value(TRACK_STOP[self._rgb])
			track_stop_buttons.append(self._grid[index][7])
		for index in range(5):
			self._grid[7][index].set_off_value(SCENE_LAUNCH[self._rgb])
			self._scene2[index].set_launch_button(self._grid[7][index])
		self._session.set_stop_track_clip_buttons(tuple(track_stop_buttons))
		if(self._r_function_mode._mode_index < 3):
			for index in range(4):
				self._grid[index + 4][6].set_on_value(CROSSFADE_TOGGLE[self._rgb])
				self._mixer2.channel_strip(index).set_crossfade_toggle(self._grid[index + 4][6])
				self._grid[index + 4][7].set_off_value(TRACK_STOP[self._rgb])
				track_stop_buttons2.append(self._grid[index + 4][7])
			self._session2.set_stop_track_clip_buttons(tuple(track_stop_buttons2))
		else:
			for index in range(4):
				self._grid[index + 4][6].set_on_value(CROSSFADE_TOGGLE[self._rgb])
				self._mixer2.return_strip(index).set_crossfade_toggle(self._grid[index + 4][6])
		self._session_zoom2.set_button_matrix(self._matrix)
		self._grid[0][5].set_on_value(RECORD[self._rgb])
		self._transport.set_record_button(self._grid[0][5])
		self._grid[1][5].set_on_value(OVERDUB[self._rgb])
		self._transport.set_overdub_button(self._grid[1][5])
		self._grid[2][5].set_on_value(LOOP[self._rgb])
		self._transport.set_loop_button(self._grid[2][5])
		self._grid[3][5].set_on_value(STOP_ALL[self._rgb])
		self._session.set_stop_all_clips_button(self._grid[3][5])
		for index in range(4):
			self._grid[index + 4][5].send_value(SEND_RESET[self._rgb], True)
		self._send_reset.set_buttons(tuple(self._grid[index + 4][5] for index in range(4)))
		for index in range(4):
			self._button[index]._off_value = DEVICE_SELECT[self._rgb]
		self._device_selector.assign_buttons(tuple(self._button[index] for index in range(4)), 0)

	

	def zoom_main(self):
		track_stop_buttons = []
		for index in range(8):
			self._grid[index][6].set_on_value(CROSSFADE_TOGGLE[self._rgb])
			self._mixer.channel_strip(index).set_crossfade_toggle(self._grid[index][6])
			self._grid[index][7].set_on_value(TRACK_STOP[self._rgb])
			track_stop_buttons.append(self._grid[index][7])
		for index in range(5):
			self._grid[7][index].set_on_value(SCENE_LAUNCH[self._rgb])
			self._scene_main[index].set_launch_button(self._grid[7][index])
		self._session_main.set_stop_track_clip_buttons(tuple(track_stop_buttons))
		self._session_zoom_main.set_button_matrix(self._matrix)
		self._grid[0][5].set_on_value(RECORD[self._rgb])
		self._transport.set_record_button(self._grid[0][5])
		self._grid[1][5].set_on_value(OVERDUB[self._rgb])
		self._transport.set_overdub_button(self._grid[1][5])
		self._grid[2][5].set_on_value(LOOP[self._rgb])
		self._transport.set_loop_button(self._grid[2][5])
		self._grid[3][5].set_on_value(STOP_ALL[self._rgb])	
		self._session.set_stop_all_clips_button(self._grid[3][5])
		for index in range(4):
			self._grid[index + 4][5].send_value(SEND_RESET[self._rgb], True)
		self._send_reset.set_buttons(tuple(self._grid[index + 4][5] for index in range(4)))
		for index in range(4):
			self._button[index + 4].set_off_value(DEVICE_SELECT[self._rgb])
		self._device_selector.assign_buttons(tuple(self._button[index + 4] for index in range(4)), 4)

	


	"""function mode callbacks"""
	def l_function_update(self):
		mode = self._l_function_mode._mode_index
		if(self._l_function_mode.is_enabled() is False):
			self._l_function_mode.set_mode_buttons(None)
		elif(self._l_function_mode.is_enabled() is True):
			if(len(self._l_function_mode._modes_buttons) is 0):
				for index in range(4):
					self._mixer.channel_strip(index).set_select_button(None)
				buttons = []
				for index in range(4):
					buttons.append(self._button[index]) 
				self._l_function_mode.set_mode_buttons(tuple(buttons))
			if(self._shift_mode._mode_index is 2):
				for index in range(4):
					if(mode != index):
						self._button[index].turn_off()
					else:
						self._button[index].turn_on()
		if(mode is 0):
			self.assign_left_device_dials()
			self.show_message('Mixer Split:Left Side Dials in Device(Top) and Selected Send(Bottom) Mode')
		elif(mode is 1):
			self.assign_left_send_dials()
			self.show_message('Mixer Split:Left Side Dials in Channel Send Mode (Sends 1-3)')
		elif(mode is 2):
			self.assign_left_filter_dials()
			self.show_message('Mixer Split:Left Side Dials in Filter(Top) and Pan(Bottom) Mode')
		elif(mode is 3):
			self.assign_left_user_dials()
			self.show_message('Mixer Split:Left Side Dials in User Map Mode')
	

	def r_function_update(self):
		mode = self._r_function_mode._mode_index
		if(self._r_function_mode.is_enabled() is False):
			self._r_function_mode.set_mode_buttons(None)
			self.set_highlighting_session_component(self._session2)
			self._session2._do_show_highlight()
			#self._session._highlighting_callback(self._session._track_offset, self._session._scene_offset, 4, 5, 1)
		elif(self._r_function_mode.is_enabled() is True):
			if(len(self._r_function_mode._modes_buttons) is 0):
				for index in range(4):
					self._mixer2.channel_strip(index).set_select_button(None)
				buttons = []
				for index in range(4):
					buttons.append(self._button[index + 4]) 
				self._r_function_mode.set_mode_buttons(tuple(buttons))
			if(self._shift_mode._mode_index is 3):
				for index in range(4):
					if(mode != index):
						self._button[index + 4].turn_off()
					else:
						self._button[index + 4].turn_on()
		if(mode is 3):
			self.assign_right_return_controls()
			self.show_message('Mixer Split:Right Side Faders = Returns 1-4, Dials = Returns Pan')
		else:   ##(mode in range(0, 3):
			self.assign_right_volume_controls()
			self._session2.set_offsets(int(self._mem[mode]), self._session2._scene_offset)
			self.show_message('Mixer Split:Right Side Faders = Channel Mixer, Dials = Returns, Track Offset' + str(RIGHT_MODE_OFFSETS[mode]))
			self._ohm_type = OHM_TYPE[mode]
			self._ohm = OHM_VALUE[mode]
	

	def m_function_update(self):
		mode = self._m_function_mode._mode_index
		if(self._m_function_mode.is_enabled() is False):
			self._m_function_mode.set_mode_buttons(None)
			#self._session.set_show_highlight(False)
			#self._session2.set_show_highlight(False)
			self.set_highlighting_session_component(self._session_main)
			self._session_main._do_show_highlight()
			#self._session_main._highlighting_callback(self._session_main._track_offset, self._session_main._scene_offset, 8, 5, 1)
		elif(self._m_function_mode.is_enabled() is True):
			if(len(self._m_function_mode._modes_buttons) is 0):
				for index in range(8):
					self._mixer.channel_strip(index).set_select_button(None)
				buttons = []
				for index in range(4):
					buttons.append(self._button[index]) 
				self._m_function_mode.set_mode_buttons(tuple(buttons))
			if(self._shift_mode._mode_index is 4):
				for index in range(4):
					if(mode != index):
						self._button[index].turn_off()
					else:
						self._button[index].turn_on()
		if(mode is 0):
			self.assign_main_controls1()
			self.show_message('Mixer Linked:Dials in Device(Top) and Selected Send(Bottom) Mode')
		elif(mode is 1):
			self.assign_main_controls2()
			self.show_message('Mixer Linked:Dials in Channel Send Mode (Sends 1-3)')
		elif(mode is 2):
			self.assign_main_controls3()
			self.show_message('Mixer Linked:Left Dials in Filter(Top) and Pan(Bottom) Mode')
		elif(mode is 3):
			self.assign_main_controls4()
			self.show_message('Mixer Linked:Dials in User Map Mode')
	

	def shift_update(self):
		self._clutch_device_selection = True
		self.allow_updates(False)
		self.deassign_channel_select_buttons()
		self.deassign_matrix()
		self.deassign_menu()
		if(self._cntrlr != None):
			self._cntrlr._monohm_shift(self._shift_mode._mode_index)
		if(self._monomod_mode._mode_index is 0):		#if monomod is not on
			if(self._shift_mode._mode_index is 0):							#if no shift is pressed
				self._shift_mode._mode_toggle1.turn_off()
				self._shift_mode._mode_toggle2.turn_off()
				if(self.split_mixer() is False):
					self.set_split_mixer(True)
				for zoom in self._zooms:
					zoom._on_zoom_value(0)
				self.zoom_off()
				self._device_selector.set_enabled(False)
				for mode in self._function_modes:
					mode.set_enabled(False)
				self.assign_channel_select_buttons()
				#self._recalculate_selected_channel()
				#self.assign_transport_to_menu()
				self.assign_session_nav_to_menu()
				self.l_function_update()
				self.r_function_update()
				self.set_highlighting_session_component(self._session)
				self._session._do_show_highlight()
			elif(self._shift_mode._mode_index is 1):						#if no shift is pressed, but mixer is linked
				self._shift_mode._mode_toggle1.turn_on()
				self._shift_mode._mode_toggle2.turn_on()
				if(self.split_mixer() is True):
					self.set_split_mixer(False)
				for zoom in self._zooms:
					zoom._on_zoom_value(0)
				self.zoom_off_m()
				self._device_selector.set_enabled(False)
				for mode in self._function_modes:
					mode.set_enabled(False)
				self.assign_main_channel_select_buttons()
				self.assign_session_main_nav_to_menu()
				self.m_function_update()
				self.set_highlighting_session_component(self._session_main)
				self._session_main._do_show_highlight()
			elif(self._shift_mode._mode_index > 1):						#if a shift is pressed
				self.assign_device_nav_to_menu()
				self.deassign_channel_select_buttons()
				if(self._shift_mode._mode_index is 2):					#if shift left
					self._shift_mode._mode_toggle1.turn_on()
					self.zoom_left()
					#self._session_zoom._zoom_value(1)
					self._session_zoom._on_zoom_value(1)
					self._session.set_enabled(True) #this is a workaround so that the stop buttons still function
					self._l_function_mode.set_enabled(True)
					self.set_highlighting_session_component(self._session)
					self._session._do_show_highlight()
				elif(self._shift_mode._mode_index is 3):				#if shift right
					self._shift_mode._mode_toggle2.turn_on()
					self.zoom_right()
					self._session_zoom2._on_zoom_value(1)
					self._session2.set_enabled(True)  #this is a workaround so that the stop buttons still function
					self._r_function_mode.set_enabled(True)
					self.assign_shift_controls()
					if(self._r_function_mode._mode_index < 4):
						self.set_highlighting_session_component(self._session2)
						self._session2._do_show_highlight()
				elif(self._shift_mode._mode_index is 4):				#if either shift pressed while mixer is linked
					self._shift_mode._mode_toggle1.turn_on()
					self._shift_mode._mode_toggle2.turn_on()
					self.zoom_main()
					self._session_zoom_main._on_zoom_value(1)
					self._session_main.set_enabled(True) #this is a workaround so that the stop buttons still function
					self._m_function_mode.set_enabled(True)
					self.assign_shift_controls()
					self.set_highlighting_session_component(self._session_main)
					self._session_main._do_show_highlight()
				self._device_selector.set_enabled(True)
		else:
			if(self._shift_mode._mode_index is 0):							#if no shift is pressed
				self._shift_mode._mode_toggle1.turn_off()
				self._shift_mode._mode_toggle2.turn_off()
				if(self.split_mixer() is False):
					self.set_split_mixer_monomod(True)
				self._device_selector.set_enabled(False)
				for mode in self._function_modes:
					mode.set_enabled(False)
				self.l_function_update()
				self.r_function_update()
				self.assign_channel_select_buttons()
				#self._recalculate_selected_channel()
			elif(self._shift_mode._mode_index is 1):						#if no shift is pressed, but mixer is linked
				self._shift_mode._mode_toggle1.turn_on()
				self._shift_mode._mode_toggle2.turn_on()
				if(self.split_mixer() is True):
					self.set_split_mixer(False)
				self._device_selector.set_enabled(False)
				for mode in self._function_modes:
					mode.set_enabled(False)
				self.m_function_update()
				self.assign_main_channel_select_buttons()
			elif(self._shift_mode._mode_index > 1):						#if a shift is pressed
				self.deassign_channel_select_buttons()
				self.assign_monomod_shift_to_menu()
				if(self._shift_mode._mode_index is 2):					#if shift left
					self._shift_mode._mode_toggle1.turn_on()
					for index in range(4):
						self._button[index + 4]._off_value = DEVICE_SELECT[self._rgb]
					self._device_selector.assign_buttons(tuple(self._button[index + 4] for index in range(4)), 4)
					self._l_function_mode.set_enabled(True)
					self._session.set_show_highlight(True)
				elif(self._shift_mode._mode_index is 3):				#if shift right
					self._shift_mode._mode_toggle2.turn_on()
					for index in range(4):
						self._button[index]._off_value = DEVICE_SELECT[self._rgb]
					self._device_selector.assign_buttons(tuple(self._button[index] for index in range(4)), 0)
					self._r_function_mode.set_enabled(True)
					self.assign_shift_controls()
					if(self._r_function_mode._mode_index < 4):
						self.set_highlighting_session_component(self._session2)
						self._session2._do_show_highlight()
				elif(self._shift_mode._mode_index is 4):				#if either shift pressed while mixer is linked
					self._shift_mode._mode_toggle1.turn_on()
					self._shift_mode._mode_toggle2.turn_on()
					for index in range(4):
						self._button[index + 4]._off_value = DEVICE_SELECT[self._rgb]
					self._device_selector.assign_buttons(tuple(self._button[index + 4] for index in range(4)), 4)
					self._m_function_mode.set_enabled(True)
					self.assign_shift_controls()
					self._session_main.set_show_highlight(True)
				self._device_selector.set_enabled(True)
			if self._shift_mode._mode_index > 1:
				self._host._shift_value(1)
			else:
				self._host._shift_value(0)
		self.allow_updates(True)
		self._clutch_device_selection = False
		#self._request_rebuild_midi_map()
		if(self._shift_mode._mode_index < 2):
			self._monobridge._send('touch', 'off')
		else:
			self._monobridge._send('touch', 'on')
	

	def monomod_mode_update(self):
		if(self._monomod_mode._mode_index == 0):
			self._host.set_enabled(False)
			self._host._set_button_matrix(None)
			self._host._set_nav_buttons(None)
			self._host._set_lock_button(None)
			self._host._set_alt_button(None)
			self._livid.turn_off()
			self._shift_mode.update()
			#self._session._reassign_scenes()
			
		elif(self._monomod_mode._mode_index == 1):
			self._livid.turn_on()
			#self.deassign_matrix()			#moved to set_mode so that the matrix doesn't clear AFTER it has been loaded by monomod
			if(self._host._active_client == None):
				self.assign_alternate_mappings()
			else:
				self.deassign_matrix()
				self.deassign_menu()
				self._monomod.reset()
				self._host._set_button_matrix(self._monomod)
				self._host._set_nav_buttons([self._menu[0], self._menu[3], self._menu[4], self._menu[5]])
				self._host._set_lock_button(self._menu[1])
				self._host._set_alt_button(self._menu[2])
				self._host.set_enabled(True)
				self._shift_mode.update()
			#self.show_message('Monomod grid enabled')
	


	"""left control management methods"""
	def deassign_left_dials(self):
		for index in range(12):
			self._dial[index].use_default_message()
			self._dial[index].release_parameter()
			self._dial[index].set_enabled(True)
		if(self._device._parameter_controls != None):
			for control in self._device._parameter_controls:
				control.release_parameter()
			self._device._parameter_controls = None
		self._device.set_enabled(False)
		self._mixer.selected_strip().set_send_controls(None)
		for track in range(4):
			self._mixer.channel_strip(track).set_send_controls(None)
			self._mixer.channel_strip(track).set_pan_control(None)
	

	def assign_left_device_dials(self):
		self.log_message('assign left device dials')
		self._backlight_type = BACKLIGHT_TYPE[0]
		self._backlight = BACKLIGHT_VALUE[0]
		self.deassign_left_dials()
		self._device.set_enabled(True)
		self._device.set_parameter_controls(tuple(self._dial[0:8]))
		self._mixer.selected_strip().set_send_controls(tuple(self._dial[8:12]))
	

	def assign_left_send_dials(self):
		self._backlight_type = BACKLIGHT_TYPE[1]
		self._backlight = BACKLIGHT_VALUE[1]
		self.deassign_left_dials()
		for track in range(4):
			channel_strip_send_controls = []
			for control in range(3):
				channel_strip_send_controls.append(self._dial[track + (control * 4)])
			self._mixer.channel_strip(track).set_send_controls(tuple(channel_strip_send_controls))
	

	def assign_left_filter_dials(self):
		self._backlight_type = BACKLIGHT_TYPE[2]
		self._backlight = BACKLIGHT_VALUE[2]
		self.deassign_left_dials()
		for index in range(4):
			self._mixer.track_filter(index).set_filter_controls(self._dial[index], self._dial[index + 4])
		for track in range(4):
			self._mixer.channel_strip(track).set_pan_control(self._dial[track + 8])
	

	def assign_left_user_dials(self):
		self._backlight_type = BACKLIGHT_TYPE[3]
		self._backlight = BACKLIGHT_VALUE[3]
		self.deassign_left_dials()
		for index in range(12):
			self._dial[index].set_channel(L_USER_DIAL_CHAN)
			self._dial[index].set_identifier(L_USER_DIAL_MAP[index])
			self._dial[index].set_enabled(False)
	


	"""right control management methods"""
	def deassign_right_controls(self):
		self._mixer.master_strip().set_volume_control(None)
		self._mixer.set_prehear_volume_control(None)
		for index in range(4):
			self._mixer.channel_strip(index + 4).set_volume_control(None)
			self._mixer2.channel_strip(index).set_volume_control(None)
			self._mixer2.return_strip(index).set_volume_control(None)
			self._mixer2.return_strip(index).set_pan_control(None)
			self._mixer2.selected_strip().set_send_controls(None)
			self._mixer2.return_strip(0).set_send_controls(tuple([None, None]))
			self._mixer2.return_strip(1).set_send_controls(tuple([None, None]))
			self._dial[index + 12].use_default_message()
			self._fader[index + 4].use_default_message()
			self._dial[index + 12].release_parameter()
			self._fader[index + 4].release_parameter()
			self._fader[index + 4].set_enabled(True)
			self._dial[index + 12].set_enabled(True)
	

	def assign_right_volume_controls(self):
		#self._ohm_type = OHM_TYPE[0]
		#self._ohm = OHM_VALUE[0]
		self.deassign_right_controls()
		for index in range(4):
			if(self._mixer2.channel_strip(index)):
				self._mixer2.channel_strip(index).set_volume_control(self._fader[index + 4])
		for index in range(4):
			if(self._mixer2.return_strip(index)):
				self._mixer2.return_strip(index).set_volume_control(self._dial[index + 12])
	

	def assign_right_return_controls(self):
		self._ohm_type = OHM_TYPE[3]
		self._ohm = OHM_VALUE[3]
		self.deassign_right_controls()
		#need to turn off session2 and session_zoom2 here, and in all subsequent right side modes
		#self._session_main._highlighting_callback(len(self.song.song.tracks), self._session2._scene_offset, 4, 5, 1)
		self._session2.set_show_highlight(False)
		for index in range(4):
			if(self._mixer2.return_strip(index)):
				self._mixer2.return_strip(index).set_volume_control(self._fader[index + 4])
				self._mixer2.return_strip(index).set_pan_control(self._dial[index + 12])
	


	"""main control management methods"""
	def assign_main_controls1(self):
		self.deassign_right_controls()
		self.deassign_left_dials()
		for column in range(8):
			self._mixer.channel_strip(column).set_volume_control(self._fader[column])
		self.assign_left_device_dials()
		for index in range(4):
			self._mixer2.return_strip(index).set_volume_control(self._dial[index + 12])
	

	def assign_main_controls2(self):
		self.deassign_right_controls()
		self.deassign_left_dials()
		for column in range(8):
			self._mixer.channel_strip(column).set_volume_control(self._fader[column])
		self.assign_left_send_dials()
		for index in range(4):
			self._mixer2.return_strip(index).set_volume_control(self._dial[index + 12])
	

	def assign_main_controls3(self):
		self.deassign_right_controls()
		self.deassign_left_dials()
		for column in range(8):
			self._mixer.channel_strip(column).set_volume_control(self._fader[column])
		self.assign_left_filter_dials()
		for index in range(4):
			self._mixer2.return_strip(index).set_volume_control(self._dial[index + 12])
	

	def assign_main_controls4(self):
		self.deassign_right_controls()
		self.deassign_left_dials()
		for column in range(8):
			self._mixer.channel_strip(column).set_volume_control(self._fader[column])
		self.assign_left_user_dials()
		for index in range(4):
			self._mixer2.return_strip(index).set_volume_control(self._dial[index + 12])
	


	"""menu button management methods"""
	def deassign_menu(self):
		for index in range(6):
			self._menu[index].set_on_off_values(127, 0)
		self._device.set_lock_button(None)
		self._device.set_on_off_button(None)
		self._device_navigator.set_device_nav_buttons(None, None)	
		self._device.set_bank_nav_buttons(None, None)
		self._transport.set_play_button(None)	
		self._transport.set_record_button(None) 
		self._transport.set_stop_button(None)
		self._transport.set_loop_button(None)	
		self._transport.set_overdub_button(None)	
		self._session.set_stop_all_clips_button(None)
		self._transport.set_play_button(None)	
		self._transport.set_stop_button(None)
		self._session_main.set_track_bank_buttons(None, None)
		self._session_main.set_scene_bank_buttons(None, None)
	

	def assign_device_nav_to_menu(self):
		self._menu[2].set_on_value(DEVICE_LOCK[self._rgb])
		self._device.set_lock_button(self._menu[2])
		self._menu[1].set_on_value(DEVICE_ON[self._rgb])
		self._device.set_on_off_button(self._menu[1])
		for index in range(2):
			self._menu[index + 4].set_on_value(DEVICE_NAV[self._rgb])
			self._menu[index * 3].set_on_value(DEVICE_BANK[self._rgb])
		self._device_navigator.set_device_nav_buttons(self._menu[4], self._menu[5]) 
		self._device.set_bank_nav_buttons(self._menu[0], self._menu[3])
	

	def assign_transport_to_menu(self):
		self._menu[0].set_on_off_values(PLAY_ON[self._rgb], PLAY[self._rgb])
		self._transport.set_play_button(self._menu[0])	
		self._menu[2].set_on_value(RECORD[self._rgb])
		self._transport.set_record_button(self._menu[2])
		self._menu[1].set_on_value(STOP[self._rgb])
		self._transport.set_stop_button(self._menu[1])
		self._menu[3].set_on_value(LOOP[self._rgb])
		self._transport.set_loop_button(self._menu[3])	
		self._menu[5].set_on_value(OVERDUB[self._rgb])
		self._transport.set_overdub_button(self._menu[5])
		self._menu[4].set_on_value(STOP_ALL[self._rgb])
		self._session.set_stop_all_clips_button(self._menu[4])
	

	def assign_session_nav_to_menu(self):
		self._menu[1].set_on_off_values(PLAY_ON[self._rgb], PLAY[self._rgb])
		self._transport.set_play_button(self._menu[1])	
		self._menu[2].set_on_off_values(STOP[self._rgb], STOP[self._rgb])	
		self._transport.set_stop_button(self._menu[2])
		for index in range(2):
			self._menu[index + 4].set_on_value(SESSION_NAV[self._rgb])
			self._menu[index * 3].set_on_value(SESSION_NAV[self._rgb])
		self._session.set_track_bank_buttons(self._menu[5], self._menu[4])
		self._session.set_scene_bank_buttons(self._menu[3], self._menu[0])
	

	def assign_monomod_shift_to_menu(self):
		self._menu[1].set_on_off_values(PLAY_ON[self._rgb], PLAY[self._rgb])
		self._transport.set_play_button(self._menu[1])
		self._menu[2].set_on_off_values(STOP[self._rgb], STOP[self._rgb])		
		self._transport.set_stop_button(self._menu[2])
		for index in range(2):
			self._menu[index + 4].set_on_value(DEVICE_NAV[self._rgb])
			self._menu[index * 3].set_on_value(DEVICE_BANK[self._rgb])
		self._device_navigator.set_device_nav_buttons(self._menu[4], self._menu[5]) 
		self._device.set_bank_nav_buttons(self._menu[0], self._menu[3])
	

	def assign_session_bank_to_menu(self):
		self._menu[1].set_on_off_values(PLAY_ON[self._rgb], PLAY[self._rgb])
		self._transport.set_play_button(self._menu[0])	
		self._menu[2].set_on_off_values(STOP[self._rgb], STOP[self._rgb])	
		self._transport.set_stop_button(self._menu[1])
		for index in range(2):
			self._menu[index + 4].set_on_value(BANK_BUTTONS[self._rgb])
			self._menu[index * 3].set_on_value(BANK_BUTTONS[self._rgb])
		self._session.set_track_bank_buttons(self._menu[5], self._menu[4])
		self._session.set_scene_bank_buttons(self._menu[3], self._menu[0])
	

	def assign_session2_bank_to_menu(self):
		self._menu[1].set_on_off_values(PLAY_ON[self._rgb], PLAY[self._rgb])
		self._transport.set_play_button(self._menu[0])
		self._menu[2].set_on_off_values(STOP[self._rgb], STOP[self._rgb])
		self._transport.set_stop_button(self._menu[1])
		for index in range(2):
			self._menu[index + 4].set_on_value(BANK_BUTTONS[self._rgb])
			self._menu[index * 3].set_on_value(BANK_BUTTONS[self._rgb])
		self._session2.set_track_bank_buttons(self._menu[5], self._menu[4])
		self._session2.set_scene_bank_buttons(self._menu[3], self._menu[0])
	

	def assign_session_main_nav_to_menu(self):
		self._menu[1].set_on_off_values(PLAY_ON[self._rgb], PLAY[self._rgb])
		self._transport.set_play_button(self._menu[1])	
		self._menu[2].set_on_off_values(STOP[self._rgb], STOP[self._rgb])
		self._transport.set_stop_button(self._menu[2])
		for index in range(2):
			self._menu[index + 4].set_on_value(BANK_BUTTONS[self._rgb])
			self._menu[index * 3].set_on_value(BANK_BUTTONS[self._rgb])
		self._session_main.set_track_bank_buttons(self._menu[5], self._menu[4])
		self._session_main.set_scene_bank_buttons(self._menu[3], self._menu[0])
	


	"""channel selection management methods"""
	def deassign_channel_select_buttons(self):
		for index in range(8):
			if(self._mixer.channel_strip(index)):
				self._mixer.channel_strip(index).set_select_button(None)
			self._button[index].release_parameter()
		for index in range(4):
			self._mixer2.channel_strip(index).set_select_button(None)
			self._mixer2.return_strip(index).set_select_button(None)
			self._mixer2.master_strip().set_select_button(None)
			self._button[index + 4].release_parameter()
	

	def assign_channel_select_buttons(self):
		for index in range(4):
			#if(self._mixer.channel_strip(index)):
			self._button[index].set_on_off_values(127, 0)
			self._mixer.channel_strip(index).set_select_button(self._button[index])
		if(self._r_function_mode._mode_index < 3):
			for index in range(4):
				#if(self._mixer2.channel_strip(index)):
				self._button[index].set_on_off_values(127, 0)
				self._mixer2.channel_strip(index).set_select_button(self._button[index + 4])	
		#elif(self._r_function_mode._mode_index < 3):
		else:
			for index in range(4):
				#if(self._mixer2.return_strip(index)):
				self._button[index].set_on_off_values(1, 0)
				self._mixer2.return_strip(index).set_select_button(self._button[index + 4])
	

	def assign_return_select_buttons(self):
		for index in range(4):
			self._button[index + 4].set_off_value(0)
			if(self._mixer.channel_strip(index)):
				self._button[index + 4].set_on_value(1)
				self._mixer.channel_strip(index).set_select_button(self._button[index + 4])
	

	def assign_l_channel_select_buttons(self):
		self._mixer.set_select_buttons(None, None)
		self._session.set_select_buttons(None, None)
		for index in range(4):
			self._button[index].set_off_value(0)
			if(self._mixer.channel_strip(index)):
				self._mixer.channel_strip(index).set_select_button(self._button[index])
	

	def assign_r_channel_select_buttons(self):
		self._mixer2.set_select_buttons(None, None)
		self._session2.set_select_buttons(None, None)
		for index in range(4):
			self._button[index + 4].set_off_value(0)
			if(self._mixer2.channel_strip(index)):
				self._mixer2.channel_strip(index).set_select_button(self._button[index + 4])
	

	def assign_main_channel_select_buttons(self):
		for index in range(8):
			self._button[index].set_off_value(0)
			if(self._mixer.channel_strip(index)):
				self._button[index].set_on_value(127)
				self._mixer.channel_strip(index).set_select_button(self._button[index])
	

	def assign_shift_controls(self):
		if self._disable_master is False:
			self.deassign_right_controls()
			self._mixer.master_strip().set_volume_control(self._fader[7])
			self._mixer.set_prehear_volume_control(self._dial[15])	
			self._mixer2.return_strip(0).set_send_controls(tuple([None, self._fader[4]]))
			self._mixer2.return_strip(1).set_send_controls(tuple([self._fader[5], None]))
	


	"""called on timer"""
	def update_display(self):
		ControlSurface.update_display(self)
		self._timer = (self._timer + 1) % 256
		self.flash()
		self.strobe()
	

	def flash(self):
		if(self.flash_status > 0):
			for control in self.controls:
				if isinstance(control, MonoButtonElement):
					control.flash(self._timer)
	

	def strobe(self):
		if(self._backlight_type != 'static'):
			if(self._backlight_type is 'pulse'):
				self._backlight = int(math.fabs(((self._timer * 8) % 64) -32) +32)
			if(self._backlight_type is 'up'):
				self._backlight = int(((self._timer * 4) % 64) + 16)
			if(self._backlight_type is 'down'):
				self._backlight = int(math.fabs(int(((self._timer * 4) % 64) - 64)) + 16)
		if(self._rgb == 1):
			self._send_midi(tuple([176, 27, int(self._backlight)]))
		else:
			self._send_midi(tuple([176, 118, int(self._backlight)]))
		if(self._ohm_type != 'static'):
			if(self._ohm_type is 'pulse'):
				self._ohm = int(math.fabs(((self._timer * 8) % 64) -32) +32)
			if(self._ohm_type is 'up'):
				self._ohm = int(((self._timer * 4) % 64) + 16)
			if(self._ohm_type is 'down'):
				self._ohm = int(math.fabs(int(((self._timer * 4) % 64) - 64)) + 16)
		if(self._rgb == 1):
			self._send_midi(tuple([176, 63, int(self._ohm)]))
			self._send_midi(tuple([176, 31, int(self._ohm)]))	
		else:
			self._send_midi(tuple([176, 119, int(self._ohm)]))
	


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
		if(isinstance(sender, MonoEncoderElement)):
			self._monobridge._send(sender.name, 'lcd_name', str(self.generate_strip_string(name)))
			self._monobridge._send(sender.name, 'lcd_value', str(self.generate_strip_string(value)))
	

	def touched(self):
		if(self._shift_mode._mode_index < 2):
			if self._touched is 0:
				self._monobridge._send('touch', 'on')
				self.schedule_message(2, self.check_touch)
			self._touched +=1
	

	def check_touch(self):
		if(self._shift_mode._mode_index < 2):
			if self._touched > 5:
				self._touched = 5
			elif self._touched > 0:
				self._touched -= 1
			if self._touched is 0:
				self._monobridge._send('touch', 'off')
			else:
				self.schedule_message(2, self.check_touch)
	

	def get_clip_names(self):
		clip_names = []
		for scene in self._session._scenes:
			for clip_slot in scene._clip_slots:
				if clip_slot.has_clip() is True:
					clip_names.append(clip_slot._clip_slot)##.clip.name)
					return clip_slot._clip_slot
					##self.log_message(str(clip_slot._clip_slot.clip.name))
		return clip_names
	


	"""midi functionality"""
	def to_encoder(self, num, val):
		rv=int(val*127)
		self._device._parameter_controls[num].receive_value(rv)
		p = self._device._parameter_controls[num]._parameter_to_map_to
		newval = (val * (p.max - p.min)) + p.min
		p.value = newval
	

	def handle_sysex(self, midi_bytes):
		assert(isinstance (midi_bytes, tuple))
		#self.log_message(str('sysex') + str(midi_bytes))
		if len(midi_bytes) > 10:
			if midi_bytes[:11] == tuple([240, 126, 0, 6, 2, 0, 1, 97, 1, 0, 7]):
				self.show_message(str('Ohm64 RGB detected...setting color map'))
				self.log_message(str('Ohm64 RGB detected...setting color map'))
				self._rgb = 0
				self._host._host_name = 'OhmRGB'
				self._color_type = 'OhmRGB'
				for button in self._button:
					button._color_map = COLOR_MAP
				for column in self._grid:
					for button in column:
						button._color_map = COLOR_MAP
			elif midi_bytes[:11] == tuple([240, 126, 0, 6, 2, 0, 1, 97, 1, 0, 2]):
				self.show_message(str('Ohm64 Monochrome detected...setting color map'))
				self.log_message(str('Ohm64 Monochrome detected...setting color map'))
				self._rgb = 1
				self._host._host_name = 'Ohm64'
				self._color_type = 'Monochrome'
				for button in self._button:
					button._color_map = [127 for index in range(0, 7)]
				for column in self._grid:
					for button in column:
						button._color_map = [127 for index in range(0, 7)]
				self._assign_session_colors()
	

	def receive_external_midi(self, midi_bytes):
		#self.log_message('receive_external_midi' + str(midi_bytes))
		assert (midi_bytes != None)
		assert isinstance(midi_bytes, tuple)
		with self.component_guard():
			if (len(midi_bytes) is 3):
				msg_type = (midi_bytes[0] & 240)
				forwarding_key = [midi_bytes[0]]
				self.log_message(str(self._forwarding_registry))
				if (msg_type is not MIDI_PB_TYPE):
					forwarding_key.append(midi_bytes[1])
				recipient = self._forwarding_registry[tuple(forwarding_key)]
				self.log_message('receive_midi recipient ' + str(recipient))
				if (recipient != None):
					recipient.receive_value(midi_bytes[2])
			else:
				self.handle_sysex(midi_bytes)

	


	"""general functionality"""
	

	def set_highlighting_session_component(self, session_component):
		self._highlighting_session_component = session_component
		self._highlighting_session_component.set_highlighting_callback(self._set_session_highlight)
	

	def allow_updates(self, allow_updates):
		for component in self.components:
			component.set_allow_update(int(allow_updates!=0))
	

	def disconnect(self):
		"""clean things up on disconnect"""
		"""for s in self._control_surfaces():
			self.log_message('monohm disconnect finds ' + str(s))
			if '_version_check' in dir(s):
				if s._version_check == 'b994':
					s.disconnect()"""
		self._update_linked_device_selection = None
		if self._session._is_linked():
			self._session._unlink()
		if self._cntrlr != None:
			self._cntrlr._monohm = None
		self._cntrlr = None
		if self.song().view.selected_track_has_listener(self._update_selected_device):
			self.song().view.remove_selected_track_listener(self._update_selected_device)
		if self._session2.offset_has_listener(self._on_session_offset_changes):
			self._session2.remove_offset_listener(self._on_session_offset_changes)
		#self._disconnect_notifier.set_mode(0)
		self.log_message("--------------= MonOhm " + str(self._monomod_version) + " log closed =--------------") #Create entry in log file
		ControlSurface.disconnect(self)
		return None
		
	

	def device_follows_track(self, val):
		self._device_selection_follows_track_selection = (val == 1)
		return self
	

	def _update_selected_device(self):
		if(self._clutch_device_selection == False):
			if self._device_selection_follows_track_selection is True:
				track = self.song().view.selected_track
				device_to_select = track.view.selected_device
				if device_to_select == None and len(track.devices) > 0:
					device_to_select = track.devices[0]
				if device_to_select != None:
					self.song().view.select_device(device_to_select)
				#self._device.set_device(device_to_select)
				self.set_appointed_device(device_to_select)
				#self._device_selector.set_enabled(True)
				self.request_rebuild_midi_map()
		return None 
	

	def assign_alternate_mappings(self):
		for column in range(8):
			for row in range(8):
				self._grid[column][row].set_identifier(OHM_MAP_ID[column][row])
				self._grid[column][row].set_identifier(OHM_MAP_CHANNEL[column][row])
				self._grid[column][row].send_value(OHM_MAP_VALUE[column][row])
				self._grid[column][row].set_enabled(False)
	

	def get_session_offsets(self):
		if(self._is_split is True):
			return [self._session.track_offset(), self._session.scene_offset(), self._session2.track_offset(), self._session2.scene_offset()]
		elif(self._is_split is False):
			return [self._session_main.track_offset(), self._session_main.scene_offset(), (self._session_main.track_offset()) + 4, self._session_main.scene_offset()]
	

	def set_split_mixer(self, is_split):
		assert isinstance(is_split, type(False))
		if(is_split!=self._is_split):
			if(is_split is True):
				self._mixer._track_offset = self._session._track_offset
			else:
				self._mixer._track_offset = self._session_main._track_offset
			self._is_split = is_split
			self._session_main.set_enabled(not is_split)
			self._session.set_enabled(is_split)
			self._session2.set_enabled(is_split)
			self._mixer._reassign_tracks()
	

	def set_split_mixer_monomod(self, is_split):
		assert isinstance(is_split, type(False))
		if(is_split!=self._is_split):
			if(is_split is True):
				self._mixer._track_offset = self._session._track_offset
			else:
				self._mixer._track_offset = self._session_main._track_offset
			self._is_split = is_split
			self._mixer._reassign_tracks()
	

	def split_mixer(self):
		return self._is_split
	

	def _get_num_tracks(self):
		return self.num_tracks
	

	def _recalculate_selected_channel(self):
		selected = False
		for index in range(4):
			if self.song().view.selected_track == self._mixer.channel_strip(index)._track:
				selected = True
			elif self.song().view.selected_track == self._mixer2.channel_strip(index)._track:
				selected = True
		if selected is False:
			self.song().view.selected_track = self._mixer2.channel_strip(0)._track
	

	def _on_device_changed(self, device):
		#self.log_message('new device ' + str(type(device)))
		if self._update_linked_device_selection != None:
			self._update_linked_device_selection(device)
	

	def mixer_on_cf_assign_changed(self, channel_strip):
		def _on_cf_assign_changed():
			if (channel_strip.is_enabled() and (channel_strip._crossfade_toggle != None)):
				if (channel_strip._track != None) and (channel_strip._track in (channel_strip.song().tracks + channel_strip.song().return_tracks)):
					if channel_strip._track.mixer_device.crossfade_assign == 1: #modified
						channel_strip._crossfade_toggle.turn_off()
					elif channel_strip._track.mixer_device.crossfade_assign == 0:
						channel_strip._crossfade_toggle.send_value(1)
					else:
						channel_strip._crossfade_toggle.send_value(2)
		return _on_cf_assign_changed
		
	

	def device_is_banking_enabled(self, device):
		def _is_banking_enabled():
			return True
		return _is_banking_enabled
		
	

	def _on_session_offset_changes(self):
		if self._r_function_mode._mode_index in range(0,3):
			self._mem[int(self._r_function_mode._mode_index)] = self._session2.track_offset()
	

	def connect_script_instances(self, instanciated_scripts):
		link = False
		for s in instanciated_scripts:
			if '_monomod_version' in dir(s):
				if s._monomod_version == self._monomod_version:
					if '_link_mixer' in dir(s):
						if s._link_mixer is True:
							link = True
		if link is True:
			if not self._session._is_linked():
				self._session.set_offsets(LINK_OFFSET[0], LINK_OFFSET[1])
				self._session._link()
		"""for s in self._control_surfaces():
			self.log_message('monohm finds ' + str(s))
			if '_version_check' in dir(s):
				if s._version_check == 'b994':
					if s._awake == False:
						s.connect_script_instances(instanciated_scripts)"""
	

	def device_set_device(self, device_component):
		def _set_device(device):
			DeviceComponent.set_device(device_component, device)
			self._on_device_changed(device) 
		return _set_device
	

	def _on_device_changed(self, device):
		#self.log_message('new device ' + str(type(device)))
		if self._update_linked_device_selection != None:
			self._update_linked_device_selection(device)
	



#	a