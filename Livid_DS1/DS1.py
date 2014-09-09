# by amounra 0714 : http://www.aumhaa.com

from __future__ import with_statement
import Live
import math
import sys
from _Tools.re import *
from itertools import imap, chain, starmap

""" _Framework files """
from _Framework.ButtonElement import ButtonElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ChannelStripComponent import ChannelStripComponent
from _Framework.ClipSlotComponent import ClipSlotComponent
from _Framework.CompoundComponent import CompoundComponent
from _Framework.ControlElement import ControlElement, ControlElementClient
from _Framework.ControlSurface import ControlSurface
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.DisplayDataSource import DisplayDataSource
from _Framework.DeviceComponent import DeviceComponent
from _Framework.EncoderElement import EncoderElement
from _Framework.InputControlElement import *
from _Framework.MixerComponent import MixerComponent
from _Framework.ModeSelectorComponent import ModeSelectorComponent
from _Framework.NotifyingControlElement import NotifyingControlElement
from _Framework.SceneComponent import SceneComponent
from _Framework.SessionComponent import SessionComponent
from _Framework.SessionZoomingComponent import DeprecatedSessionZoomingComponent as SessionZoomingComponent
from _Framework.SliderElement import SliderElement
from _Framework.TransportComponent import TransportComponent
from _Framework.PhysicalDisplayElement import *
from _Framework.SubjectSlot import subject_slot, subject_slot_group
from _Framework.Layer import Layer
from _Framework.Skin import Skin
from _Framework.M4LInterfaceComponent import M4LInterfaceComponent
from _Framework.ComboElement import ComboElement, DoublePressElement, MultiElement, DoublePressContext
from _Framework.ModesComponent import Mode, DisableMode, EnablingModesComponent, DelayMode, AddLayerMode, LayerMode, MultiEntryMode, ModesComponent, SetAttributeMode, ModeButtonBehaviour, CancellableBehaviour, AlternativeBehaviour, ReenterBehaviour, DynamicBehaviourMixin, ExcludingBehaviourMixin, ImmediateBehaviour, LatchingBehaviour, ModeButtonBehaviour
from _Framework.ClipCreator import ClipCreator
from _Framework.Resource import PrioritizedResource
from _Framework.Util import mixin

"""Custom files, overrides, and files from other scripts"""

from _Mono_Framework.MonoBridgeElement import MonoBridgeElement
from _Mono_Framework.MonoDeviceComponent import MonoDeviceComponent

from _Mono_Framework.MonoButtonElement import *
from _Mono_Framework.MonoEncoderElement import MonoEncoderElement
from _Mono_Framework.DeviceNavigator import DeviceNavigator
from _Mono_Framework.TranslationComponent import TranslationComponent
from _Mono_Framework.LividUtilities import LividSettings
from _Mono_Framework.MonoModes import SendLividSysexMode
from _Mono_Framework.Debug import *


from Map import *

import _Mono_Framework.modRemixNet as RemixNet
import _Mono_Framework.modOSC


from Push.AutoArmComponent import AutoArmComponent
from Push.SessionRecordingComponent import *
from Push.ViewControlComponent import ViewControlComponent
from Push.DrumGroupComponent import DrumGroupComponent
from Push.StepSeqComponent import StepSeqComponent
from Push.PlayheadElement import PlayheadElement
from Push.PlayheadComponent import PlayheadComponent
from Push.GridResolution import GridResolution
from Push.ConfigurableButtonElement import ConfigurableButtonElement
from Push.LoopSelectorComponent import LoopSelectorComponent
from Push.Actions import CreateInstrumentTrackComponent, CreateDefaultTrackComponent, CaptureAndInsertSceneComponent, DuplicateDetailClipComponent, DuplicateLoopComponent, SelectComponent, DeleteComponent, DeleteSelectedClipComponent, DeleteSelectedSceneComponent, CreateDeviceComponent
from Push.SkinDefault import make_default_skin


ENCODER_SPEED = [0, 0, 1, 0, 2, 0, 3, 0, 4, 0, 5, 0, 6, 0, 7, 0, 8, 0, 9, 0, 10, 0, 11, 0, 12, 0, 13, 0, 14, 0, 15, 0, 16, 0, 17, 0, 18, 0, 19, 0, 20, 0, 21, 0, 22, 0, 23, 0, 24, 0, 127, 1, 26, 0, 127, 1, 127, 1]



MIDI_NOTE_TYPE = 0
MIDI_CC_TYPE = 1
MIDI_PB_TYPE = 2
MIDI_MSG_TYPES = (MIDI_NOTE_TYPE, MIDI_CC_TYPE, MIDI_PB_TYPE)
MIDI_NOTE_ON_STATUS = 144
MIDI_NOTE_OFF_STATUS = 128
MIDI_CC_STATUS = 176
MIDI_PB_STATUS = 224


def is_device(device):
	return (not device is None and isinstance(device, Live.Device.Device) and hasattr(device, 'name'))


def make_pad_translations(chan):
	return tuple((x%4, int(x/4), x+16, chan) for x in range(16))


def return_empty():
	return []


debug = initialize_debug()


class DS1TransportComponent(TransportComponent):


	def set_record_button(self, button, *a, **k):
		button and button.set_on_off_values('Transport.RecordOn', 'Transport.RecordOff')
		super(DS1TransportComponent, self).set_record_button(button, *a, **k)
	

	def set_play_button(self, button, *a, **k):
		button and button.set_on_off_values('Transport.PlayOn', 'Transport.PlayOff')
		super(DS1TransportComponent, self).set_play_button(button, *a, **k)
	

	def set_stop_button(self, button, *a, **k):
		button and button.set_on_off_values('Transport.StopOn', 'Transport.StopOn')
		super(DS1TransportComponent, self).set_stop_button(button, *a, **k)
	

	def set_seek_backward_button(self, button, *a, **k):
		button and button.set_on_off_values('Transport.SeekBackwardOn', 'Transport.SeekBackwardOff')
		super(DS1TransportComponent, self).set_seek_backward_button(button, *a, **k)
	

	def set_loop_button(self, button, *a, **k):
		button and button.set_on_off_values('Transport.LoopOn', 'Transport.LoopOff')
		super(DS1TransportComponent, self).set_loop_button(button, *a, **k)
	


class DS1MixerComponent(MixerComponent):


	def __init__(self, script, *a, **k):
		super(DS1MixerComponent,self).__init__( *a, **k)
		self._script = script
	

	def _create_strip(self):
		return DS1ChannelStripComponent()
	

	def set_next_track_button(self, next_button):
		if next_button is not self._next_track_button:
			self._next_track_button = next_button
			self._next_track_button_slot.subject = next_button
			self.on_selected_track_changed()
	

	def set_previous_track_button(self, prev_button):
		if prev_button is not self._prev_track_button:
			self._prev_track_button = prev_button
			self._prev_track_button_slot.subject = prev_button
			self.on_selected_track_changed()
	

	def set_return_controls(self, controls):
		for strip, control in map(None, self._return_strips, controls or []):
			strip.set_volume_control(control)
	

	def tracks_to_use(self):
		return tuple(self.song().visible_tracks) + tuple(self.song().return_tracks)
	


class DS1SessionComponent(SessionComponent):


	def set_track_select_dial(self, dial):
		self._on_track_select_dial_value.subject = dial
	

	@subject_slot('value')
	def _on_track_select_dial_value(self, value):
		debug('_on_track_select_dial_value', value)
		if value > 64:
			self._bank_left()
		else:
			self._bank_right()
	


class DS1ChannelStripComponent(ChannelStripComponent):


	def __init__(self, *a, **k):
		super(DS1ChannelStripComponent, self).__init__(*a, **k)
		self._device_component = DeviceComponent()
	

	def set_track(self, *a, **k):
		super(DS1ChannelStripComponent, self).set_track(*a, **k)
		new_track = self._track or None
		self._update_device_selection.subject = self._track
	

	def set_stop_button(self, button):
		self._on_stop_value.subject = button
	

	@subject_slot('value')
	def _on_stop_value(self, value):
		if self._track:
			self._track.stop_all_clips()
	

	def set_invert_mute_feedback(self, invert_feedback):
		assert(isinstance(invert_feedback, type(False)))
		self._invert_mute_feedback = invert_feedback
		self.update()
	

	def _on_mute_changed(self):
		if self.is_enabled() and self._mute_button != None:
			if self._track != None or self.empty_color == None:
				if self._track in chain(self.song().tracks, self.song().return_tracks) and self._track.mute == self._invert_mute_feedback:
					self._mute_button.turn_on()
				else:
					self._mute_button.turn_off()
			else:
				self._mute_button.set_light(self.empty_color)
	

	def set_parameter_controls(self, controls):
		self._device_component and self._device_component.set_parameter_controls(controls)
	

	def set_device_component(self, device_component):
		self._device_component = device_component
		self._update_device_selection
	

	def on_selected_track_changed(self, *a, **k):
		super(DS1ChannelStripComponent, self).on_selected_track_changed(*a, **k)
		self._update_device_selection()
	

	@subject_slot('devices')
	def _update_device_selection(self):
		track = self._track
		device_to_select = None
		if track and device_to_select == None and len(track.devices) > 0:
			device_to_select = track.devices[0]
		self._device_component and self._device_component.set_device(device_to_select)
	

	def update(self, *a, **k):
		super(DS1ChannelStripComponent, self).update()
		self._update_device_selection()
	


class ToggleModeBehaviour(ModeButtonBehaviour):


	def press_immediate(self, component, mode):
		debug('selected_mode:', component.selected_mode, 'mode:', mode,)
		self.cycle_mode(-1)
	


class ToggledModesComponent(ModesComponent):


	@subject_slot('value')
	def _on_toggle_value(self, value):
		#debug('mode is:', self.selected_mode)
		if value:
			self.cycle_mode(-1)
			self._on_toggle_value.subject and self._on_toggle_value.subject.set_light('ModeButtons.'+self.selected_mode)
	


class DS1(ControlSurface):
	__module__ = __name__
	__doc__ = " DS1 controller script "


	def __init__(self, c_instance):
		super(DS1, self).__init__(c_instance)
		self._connected = False
		self._host_name = 'DS1'
		self.oscServer = None
		self._rgb = 0
		self._timer = 0
		self.flash_status = 1
		self._touched = 0
		self._update_linked_device_selection = None
		self._skin = Skin(DS1Colors)
		with self.component_guard():
			self._setup_monobridge()
			self._setup_controls()
			self._define_sysex()
			self._setup_mixer_control()
			self._setup_session_control()
			self._setup_transport_control()
			self._setup_device_control()
			self._setup_session_recording_component()
			#self._setup_translations()
			self._setup_main_modes()
			self._setup_m4l_interface()
			#self._device.add_device_listener(self._on_new_device_set)
		self.log_message("<<<<<<<<<<<<<<<<<= DS1 log opened =>>>>>>>>>>>>>>>>>>>>>") 
		self.schedule_message(3, self._initialize_hardware)
	

	"""script initialization methods"""
	def _initialize_hardware(self):
		self.encoder_absolute_mode.enter_mode()
		self.encoder_speed_sysex.enter_mode()
	

	def _check_connection(self):
		if not self._connected:
			self._send_midi(QUERYSURFACE)
			self.schedule_message(100, self._check_connection)
	

	def _setup_monobridge(self):
		self._monobridge = MonoBridgeElement(self)
		self._monobridge.name = 'MonoBridge'
	

	def _setup_controls(self):
		is_momentary = True
		self._fader = [MonoEncoderElement(MIDI_CC_TYPE, CHANNEL, DS1_FADERS[index], Live.MidiMap.MapMode.absolute, 'Fader_' + str(index), index, self) for index in range(8)]
		for fader in self._fader:
			fader._mapping_feedback_delay = -1
		self._dial = [[MonoEncoderElement(MIDI_CC_TYPE, CHANNEL, DS1_DIALS[x][y], Live.MidiMap.MapMode.absolute, 'Dial_' + str(x) + '_' + str(y), x + (y*5), self) for x in range(8)] for y in range(5)]
		for row in self._dial:
			for dial in row:
				dial._mapping_feedback_delay = -1
		self._side_dial = [MonoEncoderElement(MIDI_CC_TYPE, CHANNEL, DS1_SIDE_DIALS[x], Live.MidiMap.MapMode.absolute, 'Side_Dial_' + str(x), x, self) for x in range(4)]
		for dial in self._side_dial:
			dial._mapping_feedback_delay = -1
		self._encoder = [MonoEncoderElement(MIDI_CC_TYPE, CHANNEL, DS1_ENCODERS[x], Live.MidiMap.MapMode.absolute, 'Side_Dial_' + str(x), x, self) for x in range(4)]
		for encoder in self._encoder:
			encoder._mapping_feedback_delay = -1
		self._encoder_button = [MonoButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, DS1_ENCODER_BUTTONS[index], 'EncoderButton_' + str(index), self, skin = self._skin) for index in range(4)]
		self._master_fader = MonoEncoderElement(MIDI_CC_TYPE, CHANNEL, DS1_MASTER, Live.MidiMap.MapMode.absolute, 'MasterFader', 0, self)
		self._button = [MonoButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, DS1_BUTTONS[index], 'Button_' + str(index), self, skin = self._skin) for index in range(16)]
		self._grid = [[MonoButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, DS1_GRID[x][y], 'Button_' + str(x) + '_' + str(y), self, skin = self._skin) for x in range(3)] for y in range(3)]
		self._dummy = [MonoEncoderElement(MIDI_CC_TYPE, CHANNEL, 120+x, Live.MidiMap.MapMode.absolute, 'Dummy_Dial_' + str(x), x, self) for x in range(5)]

		self._fader_matrix = ButtonMatrixElement(name = 'FaderMatrix', rows = [self._fader])
		self._top_buttons = ButtonMatrixElement(name = 'TopButtonMatrix', rows = [self._button[:8]])
		self._bottom_buttons = ButtonMatrixElement(name = 'BottomButtonMatrix', rows = [self._button[8:]])
		self._dial_matrix = ButtonMatrixElement(name = 'DialMatrix', rows = self._dial)
		self._side_dial_matrix = ButtonMatrixElement(name = 'SideDialMatrix', rows = [self._side_dial])
		self._encoder_matrix = ButtonMatrixElement(name = 'EncoderMatrix', rows = [self._encoder])
		self._encoder_button_matrix = ButtonMatrixElement(name = 'EncoderButtonMatrix', rows = [self._encoder_button])
		self._grid_matrix = ButtonMatrixElement(name = 'GridMatrix', rows = self._grid)
		self._selected_parameter_controls = ButtonMatrixElement(name = 'SelectedParameterControls', rows = [self._dummy + self._encoder[:1] + self._encoder[2:]])


	

	def _define_sysex(self):
		self._livid_settings = LividSettings(model = 16, control_surface = self)
		self.encoder_speed_sysex = SendLividSysexMode(livid_settings = self._livid_settings, call = 'set_encoder_mapping', message = ENCODER_SPEED)
		self.encoder_absolute_mode = SendLividSysexMode(livid_settings = self._livid_settings, call = 'set_encoder_encosion_mode', message = [0])

	

	def _setup_autoarm(self):
		self._auto_arm = AutoArmComponent(name='Auto_Arm')
		self._auto_arm.can_auto_arm_track = self._can_auto_arm_track
	

	def _setup_mixer_control(self):
		self._num_tracks = (8)
		self._mixer = DS1MixerComponent(script = self, num_tracks = 8, num_returns = 4, invert_mute_feedback = True, autoname = True)
		self._mixer.name = 'Mixer'
		self._mixer.set_track_offset(0)
		self._mixer.master_strip().set_volume_control(self._master_fader)
		self._mixer.set_prehear_volume_control(self._side_dial[3])
		self._mixer.layer = Layer(volume_controls = self._fader_matrix)
		self._strip = [self._mixer.channel_strip(index) for index in range(8)]
		for index in range(8):
			self._strip[index].layer = Layer(parameter_controls = self._dial_matrix.submatrix[index:index+1, :])
		self._mixer.selected_strip().layer = Layer(parameter_controls = self._selected_parameter_controls)
		self._mixer.master_strip().layer = Layer(parameter_controls = self._side_dial_matrix.submatrix[:3, :])
		self._mixer.main_layer = AddLayerMode(self._mixer, Layer(solo_buttons = self._bottom_buttons, mute_buttons = self._top_buttons))
		self._mixer.select_layer = AddLayerMode(self._mixer, Layer(arm_buttons = self._bottom_buttons, track_select_buttons = self._top_buttons))
		self.song().view.selected_track = self._mixer.channel_strip(0)._track 
		self._mixer.set_enabled(True)
	

	def _setup_session_control(self):
		self._session = DS1SessionComponent(num_tracks = 8, num_scenes = 1, auto_name = True, enable_skinning = True)
		self._session.set_offsets(0, 0)	 
		self._session.set_mixer(self._mixer)
		self._session.layer = Layer(track_select_dial = ComboElement(self._encoder[1], modifiers = [self._encoder_button[1]]), scene_bank_up_button = self._grid[0][1], scene_bank_down_button = self._grid[0][2], scene_launch_buttons = self._grid_matrix.submatrix[1:2, 1:2])
		self._session.clips_layer = AddLayerMode(self._session, Layer(clip_launch_buttons = self._top_buttons, stop_track_clip_buttons = self._bottom_buttons))
		self.set_highlighting_session_component(self._session)
		self._session._do_show_highlight()
	

	def _setup_transport_control(self):
		self._transport = DS1TransportComponent()
		self._transport.name = 'Transport'
		self._transport.layer = Layer(stop_button = self._grid[1][0], play_button = self._grid[0][0], record_button = self._grid[2][0], loop_button = self._grid[2][1], seek_backward_button = self._grid[1][2])
		self._transport.set_enabled(True)
	

	def _setup_device_control(self):
		self._device = DeviceComponent()
		self._device.name = 'Device_Component'
		self.set_device_component(self._device)
		self._device_navigator = DeviceNavigator(self._device, self._mixer, self)
		self._device_navigator.name = 'Device_Navigator'
		self._device_selection_follows_track_selection = FOLLOW 
		self._device.device_name_data_source().set_update_callback(self._on_device_name_changed)
	

	def _setup_session_recording_component(self):
		self._clip_creator = ClipCreator()
		self._clip_creator.name = 'ClipCreator'
		self._recorder = SessionRecordingComponent(self._clip_creator, ViewControlComponent())
		self._recorder.set_enabled(True)
	

	def _setup_m4l_interface(self):
		self._m4l_interface = M4LInterfaceComponent(controls=self.controls, component_guard=self.component_guard, priority = 10)
		self._m4l_interface.name = "M4LInterface"
		self.get_control_names = self._m4l_interface.get_control_names
		self.get_control = self._m4l_interface.get_control
		self.grab_control = self._m4l_interface.grab_control
		self.release_control = self._m4l_interface.release_control
	

	def _setup_translations(self):
		controls = []
		for control in self.controls:
			controls.append(control)
		self._translations = TranslationComponent(controls, 10)
		self._translations.name = 'TranslationComponent'
		self._translations.set_enabled(False)
	

	def _setup_OSC_layer(self):
		self._OSC_id = 0
		if hasattr(__builtins__, 'control_surfaces') or (isinstance(__builtins__, dict) and 'control_surfaces' in __builtins__.keys()):
			for cs in __builtins__['control_surfaces']:
				if cs is self:
					break
				elif isinstance(cs, DS1):
					self._OSC_id += 1

		self._prefix = '/Live/DS1/'+str(self._OSC_id)
		self._outPrt = OSC_OUTPORT
		if not self.oscServer is None:
			self.oscServer.shutdown()
		self.oscServer = RemixNet.OSCServer('localhost', self._outPrt, 'localhost', 10001)
	

	def _setup_main_modes(self):
		self._main_modes = ToggledModesComponent(name = 'MainModes')
		self._main_modes.add_mode('Main', [self._mixer.main_layer],)
		self._main_modes.add_mode('Select', [self._mixer.select_layer],)
		self._main_modes.add_mode('Clips', [self._session.clips_layer],)
		self._main_modes.layer = Layer(priority = 4, toggle_button = self._grid[2][2])
		self._main_modes.selected_mode = 'Main'
		self._main_modes.set_enabled(True)
	

	def _notify_descriptors(self):
		if OSC_TRANSMIT:
			for pad in self._pad:
				self.oscServer.sendOSC(self._prefix+'/'+pad.name+'/lcd_name/', str(self.generate_strip_string(pad._descriptor)))
			for touchpad in self._touchpad:
				self.oscServer.sendOSC(self._prefix+'/'+touchpad.name+'/lcd_name/', str(self.generate_strip_string(touchpad._descriptor)))
			for button in self._button:
				self.oscServer.sendOSC(self._prefix+'/'+button.name+'/lcd_name/', str(self.generate_strip_string(button._descriptor)))
	

	def _get_devices(self, track):

		def dig(container_device):
			contained_devices = []
			if container_device.can_have_chains:
				for chain in container_device.chains:
					for chain_device in chain.devices:
						for item in dig(chain_device):
							contained_devices.append(item)
			else:
				contained_devices.append(container_device)
			return contained_devices
		

		devices = []
		for device in track.devices:
			for item in dig(device):
				devices.append(item)
				#self.log_message('appending ' + str(item))
		return devices
	

	"""called on timer"""
	def update_display(self):
		super(DS1, self).update_display()
		self._timer = (self._timer + 1) % 256
		self.flash()
	

	def flash(self):
		if(self.flash_status > 0):
			for control in self.controls:
				if isinstance(control, MonoButtonElement):
					control.flash(self._timer)
	

	"""m4l bridge"""
	def _on_device_name_changed(self):
		name = self._device.device_name_data_source().display_string()
		self._monobridge._send('Device_Name', 'lcd_name', str(self.generate_strip_string('Device')))
		self._monobridge._send('Device_Name', 'lcd_value', str(self.generate_strip_string(name)))
		self.touched()
		if OSC_TRANSMIT:
			self.oscServer.sendOSC(self._prefix+'/glob/device/', str(self.generate_strip_string(name)))
	

	def _on_device_bank_changed(self):
		name = 'No Bank'
		if is_device(self._device._device):
			name, _ = self._device._current_bank_details()
		self._monobridge._send('Device_Bank', 'lcd_name', str(self.generate_strip_string('Bank')))
		self._monobridge._send('Device_Bank', 'lcd_value', str(self.generate_strip_string(name)))
		self.touched()
	

	def _on_device_chain_changed(self):
		name = " "
		if is_device(self._device._device) and self._device._device.canonical_parent and isinstance(self._device._device.canonical_parent, Live.Chain.Chain):
			name = self._device._device.canonical_parent.name
		self._monobridge._send('Device_Chain', 'lcd_name', str(self.generate_strip_string('Chain')))
		self._monobridge._send('Device_Chain', 'lcd_value', str(self.generate_strip_string(name)))
		self.touched()
	

	def generate_strip_string(self, display_string):
		NUM_CHARS_PER_DISPLAY_STRIP = 12
		if (not display_string):
			return (' ' * NUM_CHARS_PER_DISPLAY_STRIP)
		else:
			display_string = str(display_string)
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
		#self.log_message('monobridge:' + str(name) + str(value))
		if isinstance(sender, MonoEncoderElement):
			if OSC_TRANSMIT:
				self.oscServer.sendOSC(self._prefix+'/'+sender.name+'/lcd_name/', str(self.generate_strip_string(name)))
				self.oscServer.sendOSC(self._prefix+'/'+sender.name+'/lcd_value/', str(self.generate_strip_string(value)))
			self._monobridge._send(sender.name, 'lcd_name', str(self.generate_strip_string(name)))
			self._monobridge._send(sender.name, 'lcd_value', str(self.generate_strip_string(value)))
		else:
			self._monobridge._send(name, 'lcd_name', str(self.generate_strip_string(name)))
			self._monobridge._send(name, 'lcd_value', str(self.generate_strip_string(value)))
			if OSC_TRANSMIT:
				self.oscServer.sendOSC(self._prefix+'/'+name+'/lcd_name/', str(self.generate_strip_string(name)))
				self.oscServer.sendOSC(self._prefix+'/'+name+'/lcd_value/', str(self.generate_strip_string(value)))
	

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
	def disconnect(self):
		if not self.oscServer is None:
			self.oscServer.shutdown()
		self.oscServer = None
		self.log_message("--------------= DS1 log closed =--------------")
		super(DS1, self).disconnect()
	

	def _can_auto_arm_track(self, track):
		routing = track.current_input_routing
		return routing == 'Ext: All Ins' or routing == 'All Ins' or routing.startswith('DS1 Input')
		#self._main_modes.selected_mode in ['Sends', 'Device'] and
	

	def _on_selected_track_changed(self):
		super(DS1, self)._on_selected_track_changed()
	

	def handle_sysex(self, midi_bytes):
		#self.log_message('sysex: ' + str(midi_bytes))
		if len(midi_bytes) > 14:
			if midi_bytes[3:10] == tuple([6, 2, 0, 1, 97, 1, 0]):
				if not self._connected:
					self._connected = True
					self._initialize_hardware()
	


#	a