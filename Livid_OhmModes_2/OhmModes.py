# amounra 0513 : http://www.aumhaa.com
from __future__ import with_statement


import Live
import time
import math
from itertools import chain
from _Framework.ButtonElement import ButtonElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ChannelStripComponent import ChannelStripComponent
from _Framework.ClipSlotComponent import ClipSlotComponent
from _Framework.CompoundComponent import CompoundComponent
from _Framework.ControlElement import ControlElement
from _Framework.ControlSurface import ControlSurface
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.DeviceComponent import DeviceComponent
from _Framework.DisplayDataSource import DisplayDataSource
from _Framework.EncoderElement import EncoderElement
from _Framework.InputControlElement import *
from VCM600.MixerComponent import MixerComponent
from _Framework.ModeSelectorComponent import ModeSelectorComponent
from _Framework.NotifyingControlElement import NotifyingControlElement
from _Framework.SceneComponent import SceneComponent
from _Framework.SessionComponent import SessionComponent
from _Framework.SessionZoomingComponent import DeprecatedSessionZoomingComponent as SessionZoomingComponent
from _Framework.SliderElement import SliderElement
from VCM600.TrackFilterComponent import TrackFilterComponent
from _Framework.TransportComponent import TransportComponent
from _Framework.ModesComponent import AddLayerMode, LayerMode, MultiEntryMode, ModesComponent, SetAttributeMode, ModeButtonBehaviour, CancellableBehaviour, AlternativeBehaviour, ReenterBehaviour, DynamicBehaviourMixin, ExcludingBehaviourMixin, ImmediateBehaviour, LatchingBehaviour, ModeButtonBehaviour
from _Framework.Layer import Layer
from _Framework.SubjectSlot import SubjectEvent, subject_slot, subject_slot_group
from _Framework.Task import *
from _Framework.M4LInterfaceComponent import M4LInterfaceComponent
from _Framework.ComboElement import ComboElement, DoublePressElement, MultiElement, DoublePressContext

from _Mono_Framework.MonoBridgeElement import MonoBridgeElement
from _Mono_Framework.MonoEncoderElement import MonoEncoderElement
from _Mono_Framework.MonoBridgeElement import MonoBridgeElement
from _Mono_Framework.DetailViewControllerComponent import DetailViewControllerComponent
from _Mono_Framework.MonoButtonElement import MonoButtonElement
from _Mono_Framework.TranslationComponent import TranslationComponent
from _Mono_Framework.LiveUtils import *
from _Mono_Framework.ModDevices import *
from _Mono_Framework.Mod import *

from _Mono_Framework.MonoDeviceComponent import MonoDeviceComponent
from _Mono_Framework.Debug import *
from _Generic.Devices import *
from Map import *

debug = initialize_debug()


session = None
mixer = None
switchxfader = (240, 0, 1, 97, 2, 15, 1, 247)
check_model = (240, 126, 127, 6, 1, 247)
KEYS = [[4, 0],
 [4, 1],
 [4, 2],
 [4, 3],
 [4, 4],
 [4, 5],
 [4, 6],
 [4, 7],
 [6, 0],
 [6, 1],
 [6, 2],
 [6, 3],
 [6, 4],
 [6, 5],
 [6, 6],
 [6, 7],
 [5, 0],
 [5, 1],
 [5, 2],
 [5, 3],
 [5, 4],
 [5, 5],
 [5, 6],
 [5, 7],
 [7, 0],
 [7, 1],
 [7, 2],
 [7, 3],
 [7, 4],
 [7, 5],
 [7, 6],
 [7, 7]]
TEMPO_TOP = 200.0
TEMPO_BOTTOM = 60.0
MIDI_NOTE_TYPE = 0
MIDI_CC_TYPE = 1
MIDI_PB_TYPE = 2
MIDI_MSG_TYPES = (MIDI_NOTE_TYPE, MIDI_CC_TYPE, MIDI_PB_TYPE)
MIDI_NOTE_ON_STATUS = 144
MIDI_NOTE_OFF_STATUS = 128
MIDI_CC_STATUS = 176
MIDI_PB_STATUS = 224

INC_DEC = [-1, 1]



class CancellableBehaviourWithRelease(CancellableBehaviour):


	def release_delayed(self, component, mode):
		component.pop_mode(mode)
	

	def update_button(self, component, mode, selected_mode):
		button = component.get_mode_button(mode)
		groups = component.get_mode_groups(mode)
		selected_groups = component.get_mode_groups(selected_mode)
		value = (mode == selected_mode or bool(groups & selected_groups))*10 or 3
		button.send_value(value, True)
	


class OctaveModeComponent(ModeSelectorComponent):


	def __init__(self, script, *a, **k):
		super(OctaveModeComponent, self).__init__(*a, **k)
		self._script = script
		self._set_protected_mode_index(3)
	

	def set_mode_buttons(self, buttons):
		for button in self._modes_buttons:
			button.remove_value_listener(self._mode_value)
		self._modes_buttons = []
		if (buttons != None):
			for button in buttons:
				assert isinstance(button, ButtonElement or MonoButtonElement)
				identify_sender = True
				button.add_value_listener(self._mode_value, identify_sender)
				self._modes_buttons.append(button)
			if (self._mode_index < 6):
				self._modes_buttons[1].turn_on()
			else:
				self._modes_buttons[1].turn_off()
			if (self._mode_index > 0):
				self._modes_buttons[0].turn_on()
			else:
				self._modes_buttons[0].turn_off()
	

	def set_mode(self, mode):
		assert isinstance(mode, int)
		mode = max(min(self._mode_index + INC_DEC[mode], 7), 0)
		if (self._mode_index != mode):
			self._mode_index = mode
			self.update()		
	

	def set_mode_toggle(self, button):
		assert ((button == None) or isinstance(button, ButtonElement or MonoButtonElement))
		if (self._mode_toggle != None):
			self._mode_toggle.remove_value_listener(self._toggle_value)
		self._mode_toggle = button
		if (self._mode_toggle != None):
			self._mode_toggle.add_value_listener(self._toggle_value)
	

	def number_of_modes(self):
		return 7
	

	def update(self):
		if(self.is_enabled() is True):
			for column in range(8):
				for row in range(3):
					self._script._grid[column][row + 4].set_identifier(int(PAGE1_KEYS_MAP[column][row]) + int(PAGE1_MODES_MAP[self._script._scale_mode._mode_index][column]) + int(self._script._octave_mode._mode_index * 12)) 
			if (self._mode_index < 6):
				self._modes_buttons[0].turn_on()
			else:
				self._modes_buttons[0].turn_off()
			if (self._mode_index > 0):
				self._modes_buttons[1].turn_on()
			else:
				self._modes_buttons[1].turn_off()
	


class ShiftModeComponent(ModeSelectorComponent):
	__module__ = __name__
	__doc__ = ' Special Class that uses two shift buttons and is lockable '


	def __init__(self, script, *a, **k):
		super(ShiftModeComponent, self).__init__(*a, **k)
		self._script = script
		self._mode_toggle1 = None
		self._mode_toggle2 = None
		self._mode_toggle3 = None
		self._set_protected_mode_index(0)
		self._last_mode = 0
	

	def set_mode_toggle(self, button1, button2, button3):
		assert ((button1 == None) or isinstance(button1, ButtonElement or MonoButtonElement))
		if (self._mode_toggle1 != None):
			self._mode_toggle1.remove_value_listener(self._toggle_value_left)
		self._mode_toggle1 = button1
		if (self._mode_toggle1 != None):
			self._mode_toggle1.add_value_listener(self._toggle_value_left)
		assert ((button2 == None) or isinstance(button2, ButtonElement or MonoButtonElement))
		if (self._mode_toggle2 != None):
			self._mode_toggle2.remove_value_listener(self._toggle_value_right)
		self._mode_toggle2 = button2
		if (self._mode_toggle2 != None):
			self._mode_toggle2.add_value_listener(self._toggle_value_right)
		assert ((button3 == None) or isinstance(button3, ButtonElement or MonoButtonElement))
		if (self._mode_toggle3 != None):
			self._mode_toggle3.remove_value_listener(self._toggle_value_mod)
		self._mode_toggle3 = button3
		if (self._mode_toggle3 != None):
			self._mode_toggle3.add_value_listener(self._toggle_value_mod)
		self._script.request_rebuild_midi_map()
	

	def set_mode_toggle1(self, button):
		self._toggle_value_left.subject = button
	

	def set_mode_toggle2(self, button):
		self._toggle_value_right.subject = button
	

	def set_mode_toggle3(self, button):
		self._toggle_value_mod.subject = button
	

	@subject_slot('value')
	def _toggle_value_left(self, value):
		if(value>0):
			if self._toggle_value_right.subject and self._toggle_value_right.subject.is_pressed():
				self._toggle_value(4)
			else:
				self._toggle_value(1)
	

	@subject_slot('value')
	def _toggle_value_right(self, value):
		if(value>0):
			if self._toggle_value_left.subject  and self._toggle_value_left.subject.is_pressed():
				self._toggle_value(4)
			else:
				self._toggle_value(2)
	

	@subject_slot('value')
	def _toggle_value_mod(self, value):
		if(value>0):
			self._toggle_value(3)
	

	def _toggle_value(self, value):
		if(value is self._mode_index):
			if value is 3:
				self.set_mode(self._last_mode)
			else:
				self.set_mode(0)
		elif not self._mode_index is 4:
			self.set_mode(value)
	

	def number_of_modes(self):
		return 5
	

	def update(self):
		self._script.deassign_matrix()
		if(self._mode_index is 0):
			self._toggle_value_left.subject and self._toggle_value_left.subject.turn_off()
			self._toggle_value_right.subject and self._toggle_value_right.subject.turn_off()
			self._script.schedule_message(1, self._script.assign_page_0)
			#self._script.assign_page_0()
		elif(self._mode_index is 1):
			self._toggle_value_left.subject and self._toggle_value_left.subject.turn_on()
			self._toggle_value_right.subject and self._toggle_value_right.subject.turn_off()
			self._script.schedule_message(1, self._script.assign_page_1)
			#self._script.assign_page_1()
		elif(self._mode_index is 2):
			self._toggle_value_left.subject and self._toggle_value_left.subject.turn_off()
			self._toggle_value_right.subject and self._toggle_value_right.subject.turn_on()
			self._script.schedule_message(1, self._script.assign_page_2)
			#self._script.assign_page_2()
		elif(self._mode_index is 3):
			self._toggle_value_left.subject and self._toggle_value_left.subject.turn_off()
			self._toggle_value_right.subject and self._toggle_value_right.subject.turn_off()
			self._script.schedule_message(1, self._script.assign_mod)
			#self._script.assign_mod()
		elif(self._mode_index is 4):
			self._toggle_value_left.subject and self._toggle_value_left.subject.turn_on()
			self._toggle_value_right.subject and self._toggle_value_right.subject.turn_on()
			self._script.schedule_message(1, self._script.assign_translation)
	

	def set_mode(self, mode):
		assert isinstance(mode, int)
		assert (mode in range(self.number_of_modes()))
		if (self._mode_index != mode):
			if mode != 3:
				self._last_mode = mode
			self._mode_index = mode
			self.update()
	


class SpecialMixerComponent(MixerComponent):
	' Special mixer class that uses return tracks alongside midi and audio tracks'
	__module__ = __name__


	def __init__(self, *a, **k):
		self._is_locked = False #added
		super(SpecialMixerComponent, self).__init__(*a, **k)
	

	def on_selected_track_changed(self):
		selected_track = self.song().view.selected_track
		if selected_track != None:
			if (self._selected_strip != None):
				if self._is_locked == False: #added
					self._selected_strip.set_track(selected_track)
			if self.is_enabled():
				if (self._next_track_button != None):
					if (selected_track != self.song().master_track):
						self._next_track_button.turn_on()
					else:
						self._next_track_button.turn_off()
				if (self._prev_track_button != None):
					if (selected_track != self.song().tracks[0]):
						self._prev_track_button.turn_on()
					else:
						self._prev_track_button.turn_off()		  
	

	def tracks_to_use(self):
		return tuple(self.song().visible_tracks) + tuple(self.song().return_tracks)
	


class ScaleModeComponent(ModeSelectorComponent):


	def __init__(self, script, *a, **k):
		super(ScaleModeComponent, self).__init__(*a, **k)
		self._script = script
		self._set_protected_mode_index(0)
	

	def set_mode_buttons(self, buttons):
		for button in self._modes_buttons:
			button.remove_value_listener(self._mode_value)
		self._modes_buttons = []
		if (buttons != None):
			for button in buttons:
				assert isinstance(button, ButtonElement or MonoButtonElement)
				identify_sender = True
				button.add_value_listener(self._mode_value, identify_sender)
				self._modes_buttons.append(button)
			for index in range(len(self._modes_buttons)):
				if (index == self._mode_index):
					self._modes_buttons[index].turn_on()
				else:
					self._modes_buttons[index].turn_off()
	

	def set_mode_toggle(self, button):
		assert ((button == None) or isinstance(button, ButtonElement or MonoButtonElement))
		if (self._mode_toggle != None):
			self._mode_toggle.remove_value_listener(self._toggle_value)
		self._mode_toggle = button
		if (self._mode_toggle != None):
			self._mode_toggle.add_value_listener(self._toggle_value)
	

	def number_of_modes(self):
		return 8
	

	def update(self):
		if(self.is_enabled() is True):
			for column in range(8):
				for row in range(3):
					self._script._grid[column][row + 4].set_identifier(int(PAGE1_KEYS_MAP[column][row]) + int(PAGE1_MODES_MAP[self._script._scale_mode._mode_index][column]) + int(self._script._octave_mode._mode_index * 12))
			for index in range(len(self._modes_buttons)):
				if (index == self._mode_index):
					self._modes_buttons[index].turn_on()
				else:
					self._modes_buttons[index].turn_off()
	


class OhmModes(ControlSurface):
	__module__ = __name__
	__doc__ = ' OhmModes controller script '


	def __init__(self, c_instance):
		super(OhmModes, self).__init__(c_instance)
		self._version_check = 'b996'
		self._host_name = 'Ohm'
		self._color_type = 'OhmRGB'
		self._rgb = 0
		self._timer = 0
		self._touched = 0
		self.flash_status = 1
		self._backlight = 127
		self._backlight_type = 'static'
		self._ohm = 127
		self._ohm_type = 'static'
		self._pad_translations = PAD_TRANSLATION
		self._device_selection_follows_track_selection = FOLLOW
		self._keys_octave = 5
		self._keys_scale = 0
		self._tempo_buttons = None
		with self.component_guard():
			self._setup_monobridge()
			self._setup_controls()
			self._setup_m4l_interface()
			self._setup_transport_control()
			self._setup_mixer_control()
			self._setup_session_control()
			self._setup_device_control()
			self._setup_crossfader()
			self._setup_translations()
			self._setup_mod()
			self._setup_modes()
			self._assign_page_constants()
			self._last_device = None
			self.song().view.add_selected_track_listener(self._update_selected_device)
			self.show_message('OhmModes Control Surface Loaded')
			self._send_midi(tuple(switchxfader))
		if FORCE_TYPE is True:
			self._rgb = FORCE_COLOR_TYPE
		else:
			self.schedule_message(10, self.query_ohm, None)
		self.log_message('<<<<<<<<<<<<<<<<<<<<<<<<< OhmModes ' + str(self._version_check) + ' log opened >>>>>>>>>>>>>>>>>>>>>>>>>')
		debug('DEBUG ON for OhmModes script.')
	

	def query_ohm(self):
		self._send_midi(tuple(check_model))
	

	def update_display(self):
		super(OhmModes, self).update_display()
		self._timer = (self._timer + 1) % 256
		self.flash()
		self.strobe()
	

	def _setup_monobridge(self):
		self._monobridge = MonoBridgeElement(self)
		self._monobridge.name = 'MonoBridge'
	

	def get_device_bank(self):
		return self._device._bank_index
	

	def _setup_controls(self):
		is_momentary = True
		self._fader = [ None for index in range(8) ]
		self._dial = [ None for index in range(16) ]
		self._button = [ None for index in range(8) ]
		self._menu = [ None for index in range(6) ]
		for index in range(8):
			self._fader[index] = MonoEncoderElement(MIDI_CC_TYPE, CHANNEL, OHM_FADERS[index], Live.MidiMap.MapMode.absolute, 'Fader_' + str(index), index, self)

		for index in range(8):
			self._button[index] = MonoButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, OHM_BUTTONS[index], 'Button_' + str(index), self)

		for index in range(16):
			self._dial[index] = MonoEncoderElement(MIDI_CC_TYPE, CHANNEL, OHM_DIALS[index], Live.MidiMap.MapMode.absolute, 'Encoder_' + str(index), index, self)

		self._knobs = []
		for index in range(12):
			self._knobs.append(self._dial[index])

		for index in range(6):
			self._menu[index] = MonoButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, OHM_MENU[index], 'Menu_' + str(index), self)

		self._crossfader = EncoderElement(MIDI_CC_TYPE, CHANNEL, CROSSFADER, Live.MidiMap.MapMode.absolute)
		self._crossfader.name = 'Crossfader'
		self._livid = MonoButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, LIVID, 'Livid_Button', self)
		self._shift_l = MonoButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, SHIFT_L, 'Page_Button_Left', self)
		self._shift_r = MonoButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, SHIFT_R, 'Page_Button_Right', self)
		self._matrix = ButtonMatrixElement()
		self._matrix.name = 'Matrix'
		self._grid = [ None for index in range(8) ]
		self._monomod = ButtonMatrixElement()
		self._monomod.name = 'Monomod'
		for column in range(8):
			self._grid[column] = [ None for index in range(8) ]
			for row in range(8):
				self._grid[column][row] = MonoButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, column * 8 + row, 'Grid_' + str(column) + '_' + str(row), self)

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

		self._dial_matrix = ButtonMatrixElement()
		for row in range(3):
			dial_row = []
			for column in range(4):
				dial_row.append(self._dial[column + (row*4)])

			self._dial_matrix.add_row(tuple(dial_row))

		self._menu_matrix = ButtonMatrixElement([self._menu])
	

	def _setup_m4l_interface(self):
		self._m4l_interface = M4LInterfaceComponent(controls=self.controls, component_guard=self.component_guard)
		self.get_control_names = self._m4l_interface.get_control_names
		self.get_control = self._m4l_interface.get_control
		self.grab_control = self._m4l_interface.grab_control
		self.release_control = self._m4l_interface.release_control
	

	def _setup_translations(self):
		controls = []
		for array in self._grid:
			for button in array:
				controls.append(button)
		if FADER_BANKING:
			controls = controls + self._dial
		if DIAL_BANKING:
			controls = controls + self._dial
		self._translations = TranslationComponent(controls, USER_CHANNEL)
		self._translations.layer = Layer(priority = 7, channel_selector_buttons = self._menu_matrix)
	

	def _setup_mod(self):
		self.monomodular = get_monomodular(self)
		self.monomodular.name = 'monomodular_switcher'
		self.modhandler = OhmModHandler(self)
		self.modhandler.name = 'ModHandler' 
		self.modhandler.layer = Layer(priority = 5, 
									grid = self._monomod,
									nav_up_button = self._menu[2],
									nav_down_button = self._menu[5],
									nav_left_button = self._menu[3],
									nav_right_button =  self._menu[4],
									shift_button = self._menu[1],
									alt_button = self._menu[0],
									parameter_controls = self._dial_matrix)
		self.modhandler.legacy_shift_mode = AddLayerMode(self.modhandler, Layer(priority = 6,
									channel_buttons = self._monomod.submatrix[:, 1:2],
									nav_matrix = self._monomod.submatrix[4:8, 2:6]))
		self.modhandler.shift_mode = AddLayerMode(self.modhandler, Layer(priority = 6, 
									device_selector_matrix = self._monomod.submatrix[:, :1],
									lock_button = self._livid,
									key_buttons = self._monomod.submatrix[:, 7:8]))
									
		self.modhandler.set_enabled(False)
		self.modhandler.set_mod_button(self._livid)
	

	def _setup_modes(self):
		self._shift_mode = ShiftModeComponent(self)
		self._shift_mode.name = 'Shift_Mode'
		#self._shift_mode.set_mode_toggle(self._shift_l, self._shift_r, self._livid)
		self._shift_mode.layer = Layer(priority = 4, mode_toggle1 = self._shift_l, mode_toggle2 = self._shift_r, mode_toggle3 = self._livid)
		self._shift_mode.set_enabled(True)
		self._scale_mode = ScaleModeComponent(self)
		self._scale_mode.name = 'Scale_Mode'
		self._octave_mode = OctaveModeComponent(self)
		self._octave_mode.name = 'Octave_Mode'
	

	def _setup_transport_control(self):
		self._transport = TransportComponent()
		self._transport.name = 'Transport'
		#self._transport.layer = Layer(priority = 4, play_button = self._menu[2], stop_button = self._menu[3])
	

	def _setup_mixer_control(self):
		global mixer
		is_momentary = True
		self._num_tracks = 7
		mixer = SpecialMixerComponent(7, 0, True, True)
		mixer.name = 'Mixer'
		self._mixer = mixer
		for index in range(7):
			mixer.channel_strip(index).set_volume_control(self._fader[index])

		for index in range(7):
			mixer.channel_strip(index).name = 'Mixer_ChannelStrip_' + str(index)
			mixer.track_eq(index).name = 'Mixer_EQ_' + str(index)
			mixer.channel_strip(index)._invert_mute_feedback = True

		self.song().view.selected_track = mixer.channel_strip(0)._track
	

	def _setup_session_control(self):
		global session
		is_momentary = True
		num_tracks = 7
		num_scenes = 5
		session = SessionComponent(num_tracks, num_scenes)
		session.name = 'Session'
		self._session = session
		session.set_offsets(0, 0)
		self._scene = [ None for index in range(6) ]
		for row in range(num_scenes):
			self._scene[row] = session.scene(row)
			self._scene[row].name = 'Scene_' + str(row)
			for column in range(num_tracks):
				clip_slot = self._scene[row].clip_slot(column)
				clip_slot.name = str(column) + '_Clip_Slot_' + str(row)

		session.set_mixer(self._mixer)
		session.set_show_highlight(True)
		self._session_zoom = SessionZoomingComponent(session)
		self._session_zoom.name = 'Session_Overview'
		self.set_highlighting_session_component(self._session)
	

	def _assign_session_colors(self):
		self.log_message('assign session colors')
		num_tracks = 7
		num_scenes = 5
		self._session.set_stop_clip_value(STOP_CLIP_COLOR[self._rgb])
		for row in range(num_scenes):
			for column in range(num_tracks):
				self._scene[row].clip_slot(column).set_triggered_to_play_value(CLIP_TRIGD_TO_PLAY_COLOR[self._rgb])
				self._scene[row].clip_slot(column).set_triggered_to_record_value(CLIP_TRIGD_TO_RECORD_COLOR[self._rgb])
				self._scene[row].clip_slot(column).set_stopped_value(CLIP_STOPPED_COLOR[self._rgb])
				self._scene[row].clip_slot(column).set_started_value(CLIP_STARTED_COLOR[self._rgb])
				self._scene[row].clip_slot(column).set_recording_value(CLIP_RECORDING_COLOR[self._rgb])

		self._session_zoom.set_stopped_value(ZOOM_STOPPED_COLOR[self._rgb])
		self._session_zoom.set_playing_value(ZOOM_PLAYING_COLOR[self._rgb])
		self._session_zoom.set_selected_value(ZOOM_SELECTED_COLOR[self._rgb])
		for row in range(8):
			for column in range(8):
				self._grid[column][row].set_force_next_value()

		self._session.on_scene_list_changed()
		self._shift_mode.update()
	

	def _setup_device_control(self):
		self._device = DeviceComponent()
		self._device.name = 'Device_Component'
		self.set_device_component(self._device)
		self._device_navigator = DetailViewControllerComponent()
		self._device_navigator.name = 'Device_Navigator'
		self._device_selection_follows_track_selection = FOLLOW
	

	def device_follows_track(self, val):
		self._device_selection_follows_track_selection = val == 1
		return self
	

	def _setup_crossfader(self):
		self._mixer.set_crossfader_control(self._crossfader)
	

	def disconnect(self):
		"""clean things up on disconnect"""
		self.song().view.remove_selected_track_listener(self._update_selected_device)
		self.log_message(time.strftime('%d.%m.%Y %H:%M:%S', time.localtime()) + '--------------= OhmModes log closed =--------------')
		super(OhmModes, self).disconnect()
		rebuild_sys()
	

	def _get_num_tracks(self):
		return self.num_tracks
	

	def flash(self):
		if(self.flash_status > 0):
			for control in self.controls:
				if isinstance(control, MonoButtonElement):
					control.flash(self._timer)
	

	def strobe(self):
		if self._backlight_type != 'static':
			if self._backlight_type is 'pulse':
				self._backlight = int(math.fabs(self._timer * 16 % 64 - 32) + 32)
			if self._backlight_type is 'up':
				self._backlight = int(self._timer * 8 % 64 + 16)
			if self._backlight_type is 'down':
				self._backlight = int(math.fabs(int(self._timer * 8 % 64 - 64)) + 16)
		self._send_midi(tuple([176, 27, int(self._backlight)]))
		if self._ohm_type != 'static':
			if self._ohm_type is 'pulse':
				self._ohm = int(math.fabs(self._timer * 16 % 64 - 32) + 32)
			if self._ohm_type is 'up':
				self._ohm = int(self._timer * 8 % 64 + 16)
			if self._ohm_type is 'down':
				self._ohm = int(math.fabs(int(self._timer * 8 % 64 - 64)) + 16)
		self._send_midi(tuple([176, 63, int(self._ohm)]))
		self._send_midi(tuple([176, 31, int(self._ohm)]))
	

	def deassign_matrix(self):
		with self.component_guard():
			self.modhandler.set_enabled(False)
			self._translations.set_enabled(False)
			#self.assign_alternate_mappings(0)
			self._scale_mode.set_mode_buttons(None)
			self._scale_mode.set_enabled(False)
			self._octave_mode.set_mode_buttons(None)
			self._octave_mode.set_enabled(False)
			self._session_zoom.set_enabled(False)
			self._session_zoom.set_nav_buttons(None, None, None, None)
			self._session.set_track_bank_buttons(None, None)
			self._session.set_scene_bank_buttons(None, None)
			self._transport.set_enabled(False)
			for column in range(4):
				self._mixer.track_eq(column)._gain_controls = None
				self._mixer.track_eq(column).set_enabled(False)

			for column in range(7):
				self._mixer.channel_strip(column).set_crossfade_toggle(None)
				self._mixer.channel_strip(column).set_mute_button(None)
				self._mixer.channel_strip(column).set_solo_button(None)
				self._mixer.channel_strip(column).set_arm_button(None)
				self._mixer.channel_strip(column).set_send_controls(None)
				self._mixer.channel_strip(column).set_pan_control(None)
				self._mixer.track_eq(column).set_enabled(False)
				for row in range(5):
					self._scene[row].clip_slot(column).set_launch_button(None)
			for column in range(8):
				self._button[column]._on_value = SELECT_COLOR[self._rgb]
				for row in range(8):
					#self._grid[column][row].set_channel(0)
					self._grid[column][row].release_parameter()
					self._grid[column][row].use_default_message()
					self._grid[column][row].set_enabled(True)
					self._grid[column][row].send_value(0, True)
					self._grid[column][row]._on_value = 127
					self._grid[column][row]._off_value = 0
					self._grid[column][row].force_next_send()
			for index in range(6):
				self._menu[index]._on_value = 127
				self._menu[index]._off_value = 0
			for index in range(16):
				self._dial[index].use_default_message()
				self._dial[index].release_parameter()
			self._device.set_parameter_controls(None)
			self._device.set_enabled(False)
			self._device_navigator.set_enabled(False)
			self._mixer.update()
			self._matrix.reset()
		self.request_rebuild_midi_map()
	

	def _assign_page_constants(self):
		with self.component_guard():
			self._session_zoom.set_zoom_button(self._grid[7][7])
			self._session_zoom.set_button_matrix(self._matrix)
			for column in range(7):
				self._mixer.channel_strip(column).set_select_button(self._button[column])
				self._mixer.channel_strip(column).set_volume_control(self._fader[column])

			self._mixer.master_strip().set_volume_control(self._fader[7])
			self._mixer.master_strip().set_select_button(self._button[7])
			self._mixer.set_prehear_volume_control(self._dial[15])
			self._transport.set_play_button(self._menu[0])
			self._menu[0].send_value(PLAY_COLOR[self._rgb], True)
			self._menu[0]._on_value = PLAY_COLOR[self._rgb]
			self._transport.set_stop_button(self._menu[1])
			self._menu[1]._off_value = STOP_COLOR[self._rgb]
			self._menu[1]._on_value = STOP_COLOR[self._rgb]
			self._menu[1].send_value(STOP_COLOR[self._rgb], True)
			self._device_navigator.set_device_nav_buttons(self._menu[3], self._menu[4])
	

	def assign_page_0(self):
		with self.component_guard():
			self._backlight_type = 'static'
			self._session_zoom.set_enabled(True)
			for column in range(7):	
				self._grid[column][5]._on_value = MUTE_COLOR[self._rgb]
				self._mixer.channel_strip(column).set_mute_button(self._grid[column][5])
				self._grid[column][6]._on_value = SOLO_COLOR[self._rgb]
				self._mixer.channel_strip(column).set_solo_button(self._grid[column][6])
				self._grid[column][7]._on_value = ARM_COLOR[self._rgb]
				self._mixer.channel_strip(column).set_arm_button(self._grid[column][7])
				self._mixer.channel_strip(column).set_pan_control(self._dial[column + 8])
				for row in range(5):
					self._scene[row].clip_slot(column).set_launch_button(self._grid[column][row])

			for column in range(4):
				self._mixer.channel_strip(column).set_send_controls(tuple([self._dial[column], self._dial[column + 4]]))

			for index in range(5):
				self._grid[7][index]._off_value = SCENE_LAUNCH_COLOR[self._rgb]
				self._scene[index].set_launch_button(self._grid[7][index])
				self._grid[7][index].set_force_next_value()
				self._grid[7][index].turn_off()

			for index in range(4):
				self._menu[2 + index]._on_value = NAV_BUTTON_COLOR[self._rgb]

			self._session.set_track_bank_buttons(self._menu[4], self._menu[3])
			self._session.set_scene_bank_buttons(self._menu[5], self._menu[2])
			self._menu[0]._on_value = PLAY_COLOR[self._rgb]
			self._menu[1]._off_value = STOP_COLOR[self._rgb]
			self._menu[1]._on_value = STOP_COLOR[self._rgb]
			self._transport.set_enabled(True)
			#self._mixer.update_all()
		self.request_rebuild_midi_map()
		#self.log_message('assign_page_0')
	

	def assign_page_1(self):
		with self.component_guard():
			self._backlight_type = 'pulse'
			self._session_zoom.set_enabled(False)
			for column in range(4):
				for row in range(4):
					self._grid[column][row].send_value(DRUM_COLOR[self._rgb], True)
					self._grid[column + 4][row].send_value(BASS_COLOR[self._rgb], True)
					self._grid[column][row].set_enabled(False)
					self._grid[column][row]._msg_channel = PAGE1_DRUM_CHANNEL
					self._grid[column][row].set_identifier(PAGE1_DRUM_MAP[column][row])
					self._grid[column + 4][row].set_enabled(False)
					self._grid[column + 4][row]._msg_channel = PAGE1_BASS_CHANNEL
					self._grid[column + 4][row].set_identifier(PAGE1_BASS_MAP[column][row])

			scale_mode_buttons = []
			for column in range(8):
				for row in range(3):
					self._grid[column][row + 4].set_enabled(False)
					self._grid[column][row + 4].send_value(KEYS_COLOR[self._rgb], True)
					self._grid[column][row + 4]._msg_channel = PAGE1_KEYS_CHANNEL
					self._grid[column][row + 4].set_identifier(int(PAGE1_KEYS_MAP[column][row]) + int(PAGE1_MODES_MAP[self._scale_mode._mode_index][column]) + int(self._octave_mode._mode_index * 12))

				for row in range(1):
					scale_mode_buttons.append(self._grid[column][7])

			self._scale_mode.set_mode_buttons(tuple(scale_mode_buttons))
			self._scale_mode.set_enabled(True)
			self._octave_mode.set_mode_buttons(tuple([self._menu[5], self._menu[2]]))
			self._octave_mode.set_enabled(True)
			for column in range(7):
				self._mixer.channel_strip(column).set_send_controls(tuple([self._dial[column + 8]]))
				self._mixer.channel_strip(column).set_arm_button(self._button[column])

			self._device.set_enabled(True)
			device_param_controls = []
			for index in range(8):
				device_param_controls.append(self._dial[index])

			self._device.set_parameter_controls(tuple(device_param_controls))
			self._menu[0]._on_value = PLAY_COLOR[self._rgb]
			for index in range(4):
				self._menu[2 + index]._on_value = DEVICE_NAV_COLOR[self._rgb]

			self._device_navigator.set_enabled(True)
			self._menu[0]._on_value = PLAY_COLOR[self._rgb]
			self._menu[1]._off_value = STOP_COLOR[self._rgb]
			self._menu[1]._on_value = STOP_COLOR[self._rgb]
			self._transport.set_enabled(True)
		self.request_rebuild_midi_map()
	

	def assign_page_2(self):
		with self.component_guard():
			self._backlight_type = 'up'
			self._session_zoom.set_enabled(True)
			for column in range(7):
				self._grid[column][5]._on_value = MUTE_COLOR[self._rgb]
				self._mixer.channel_strip(column).set_mute_button(self._grid[column][5])
				self._grid[column][6]._on_value = CROSSFADE_ASSIGN_COLOR[self._rgb]
				self._mixer.channel_strip(column).set_crossfade_toggle(self._grid[column][6])
				self._grid[column][7]._msg_channel = 2
				self._grid[column][7].set_identifier(column)
				self._grid[column][7].reset()
				self._grid[column][7].set_enabled(False)
				self._grid[column][7].send_value(4, True)
				for row in range(5):
					self._scene[row].clip_slot(column).set_launch_button(self._grid[column][row])

			for row in range(5):
				self._grid[7][row]._off_value = SCENE_LAUNCH_COLOR[self._rgb]
				self._scene[row].set_launch_button(self._grid[7][row])
				self._grid[7][row].set_force_next_value()
				self._grid[7][row].turn_off()

			for column in range(4):
				self._mixer.track_eq(column).set_gain_controls(tuple([self._dial[column + 8], self._dial[column + 4], self._dial[column]]))
				self._mixer.track_eq(column).set_enabled(True)

			for column in range(3):
				self._mixer.channel_strip(column + 4).set_pan_control(self._dial[column + 12])

			for index in range(4):
				self._menu[2 + index]._on_value = NAV_BUTTON_COLOR[self._rgb]

			self._session.set_track_bank_buttons(self._menu[4], self._menu[3])
			self._session.set_scene_bank_buttons(self._menu[5], self._menu[2])
			self._set_tempo_buttons([self._grid[7][5], self._grid[7][6]])
			self._menu[0]._on_value = PLAY_COLOR[self._rgb]
			self._menu[1]._off_value = STOP_COLOR[self._rgb]
			self._menu[1]._on_value = STOP_COLOR[self._rgb]
			self._transport.set_enabled(True)
			#self._mixer.update()
		self.request_rebuild_midi_map()
	

	def assign_mod(self):
		self.modhandler.set_enabled(True)
	

	def assign_translation(self):
		self._translations.set_enabled(True)
	

	def assign_alternate_mappings(self, chan):
		for column in range(8):
			for row in range(8):
				self._grid[column][row].set_channel(chan)
		for knob in self._dial:
			knob.set_channel(chan)
			knob.set_enabled(chan is 0)

		self.request_rebuild_midi_map()
	

	def _update_selected_device(self):
		if self._device_selection_follows_track_selection is True:
			self._update_device_selection()
	

	def handle_sysex(self, midi_bytes):
		#self.log_message('sysex: ' + str(midi_bytes))
		if len(midi_bytes) > 10:
			if midi_bytes[:11] == tuple([240,
			 126,
			 0,
			 6,
			 2,
			 0,
			 1,
			 97,
			 1,
			 0,
			 7]):
				self.log_message(str('>>>color detected'))
				self._rgb = 0
				for button in self._button:
					button._color_map = COLOR_MAP
				for column in self._grid:
					for button in column:
						button._color_map = COLOR_MAP
			elif midi_bytes[:11] == tuple([240,
			 126,
			 0,
			 6,
			 2,
			 0,
			 1,
			 97,
			 1,
			 0,
			 2]):
				self.log_message(str('>>>mono detected'))
				self._rgb = 1
				for button in self._button:
					button._color_map = [127 for index in range(0, 7)]
				for column in self._grid:
					for button in column:
						button._color_map = [127 for index in range(0, 7)]
		self._assign_session_colors()
	

	def to_encoder(self, num, val):
		rv = int(val * 127)
		self._device._parameter_controls[num].receive_value(rv)
		p = self._device._parameter_controls[num]._parameter_to_map_to
		newval = val * (p.max - p.min) + p.min
		p.value = newval
	

	def _set_tempo_buttons(self, buttons):
		if self._tempo_buttons != None:
			self._tempo_buttons[0].remove_value_listener(self._tempo_value)
			self._tempo_buttons[1].remove_value_listener(self._tempo_value)
		self._tempo_buttons = buttons
		if buttons != None:
			for button in buttons:
				 assert isinstance(button, MonoButtonElement)
			self._tempo_buttons[0].set_on_off_values(4, 0)
			self._tempo_buttons[0].add_value_listener(self._tempo_value, True)
			self._tempo_buttons[1].set_on_off_values(4, 0)
			self._tempo_buttons[1].add_value_listener(self._tempo_value, True)
			self._tempo_buttons[0].turn_on()
			self._tempo_buttons[1].turn_on()
	

	def _tempo_value(self, value, sender):
		if value > 0 and self._tempo_buttons.index(sender) == 0:
			self.song().tempo = round(min(self.song().tempo + 1, 999))
		elif value > 0 and self._tempo_buttons.index(sender) == 1:
			self.song().tempo = round(max(self.song().tempo - 1, 20))
	

	def generate_strip_string(self, display_string):
		NUM_CHARS_PER_DISPLAY_STRIP = 12
		if not display_string:
			return ' ' * NUM_CHARS_PER_DISPLAY_STRIP
		if len(display_string.strip()) > NUM_CHARS_PER_DISPLAY_STRIP - 1 and display_string.endswith('dB') and display_string.find('.') != -1:
			display_string = display_string[:-2]
		if len(display_string) > NUM_CHARS_PER_DISPLAY_STRIP - 1:
			for um in [' ',
			 'i',
			 'o',
			 'u',
			 'e',
			 'a']:
				while len(display_string) > NUM_CHARS_PER_DISPLAY_STRIP - 1 and display_string.rfind(um, 1) != -1:
					um_pos = display_string.rfind(um, 1)
					display_string = display_string[:um_pos] + display_string[um_pos + 1:]

		else:
			display_string = display_string.center(NUM_CHARS_PER_DISPLAY_STRIP - 1)
		ret = u''
		for i in range(NUM_CHARS_PER_DISPLAY_STRIP - 1):
			if ord(display_string[i]) > 127 or ord(display_string[i]) < 0:
				ret += ' '
			else:
				ret += display_string[i]

		ret += ' '
		return ret
	

	def notification_to_bridge(self, name, value, sender):
		if isinstance(sender, tuple([MonoButtonElement, MonoEncoderElement])):
			self._monobridge._send(sender.name, 'lcd_name', str(self.generate_strip_string(name)))
			self._monobridge._send(sender.name, 'lcd_value', str(self.generate_strip_string(value)))
	

	def touched(self):
		if self._touched is 0:
			self._monobridge._send('touch', 'on')
			self.schedule_message(2, self.check_touch)
		self._touched += 1
	

	def check_touch(self):
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
					clip_names.append(clip_slot._clip_slot)
					return clip_slot._clip_slot

		return clip_names
	


class OhmModHandler(ModHandler):


	def __init__(self, *a, **k):
		super(OhmModHandler, self).__init__(*a, **k)
		self._shift_mode = ModesComponent()
		self._color_type = 'RGB'
		self._shift_mode.add_mode('shift', tuple([self._enable_shift, self._disable_shift]), behaviour = CancellableBehaviourWithRelease())
		self.nav_box = self.register_component(NavigationBox(self, 16, 16, 8, 8, self.set_offset))
		self._mod_button = None
	

	def _enable_shift(self):
		self._shift_value(1)
	

	def _disable_shift(self):
		self._shift_value(0)
	

	def set_shift_button(self, button):
		self._shift_mode.set_mode_button('shift', button)
	

	def set_nav_matrix(self, matrix):
		self.nav_box.set_matrix(matrix)
	

	def _receive_grid(self, x, y, value, *a, **k):
		#self._receive_grid(x, y, value, *a, **k)
		legacy = self.active_mod().legacy
		if self._active_mod:
			if not self._grid_value.subject is None:
				if legacy:
					x = x - self.x_offset 
					y = y - self.y_offset 
				if x in range(8) and y in range(8):
					try:
						self._grid_value.subject.send_value(x, y, self._colors[value], True)
					except:
						pass
	

	def set_device_selector_matrix(self, matrix):
		self._device_selector.set_matrix(matrix)
	


	@subject_slot('value')
	def _grid_value(self, value, x, y, *a, **k):
		#self.log_message('_base_grid_value ' + str(x) + str(y) + str(value))
		if self.active_mod():
			if self.active_mod().legacy:
				x += self.x_offset
				y += self.y_offset
			self._active_mod.send('grid', x, y, value)
	

	@subject_slot('value')
	def _shift_value(self, value, *a, **k):
		self._is_shifted = not value is 0
		mod = self.active_mod()
		if mod:
			mod.send('shift', value)
		if self._is_shifted:
			self.shift_mode.enter_mode()
			if mod and mod.legacy:
				self.legacy_shift_mode.enter_mode()
		else:
			self.legacy_shift_mode.leave_mode()
			self.shift_mode.leave_mode()
		self.update()
	

	def set_mod_button(self, button):
		self._mod_button = button
	

	def update(self, *a, **k): 
		mod = self.active_mod()
		if self.is_enabled():
			if not mod is None:
				mod.restore()
			else:
				if not self._grid_value.subject is None:
					self._grid_value.subject.reset()
				if not self._keys_value.subject is None:
					self._keys_value.subject.reset()
			self._alt_value.subject and self._alt_value.subject.send_value(2 + int(self.is_alted())*7, True)
			if self._on_lock_value.subject:
				self._on_lock_value.subject.send_value(1 + (int(self.is_locked())*4), True)
			else:
				self._mod_button and self._mod_button.send_value(7 + (not self.active_mod() is None)*7, True)
			
		else:
			self._mod_button and self._mod_button.send_value((not self.active_mod() is None)*3, True)

	

