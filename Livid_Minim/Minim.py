# by amounra 0216 : http://www.aumhaa.com

from __future__ import with_statement
import Live
import time
import math
import logging
logger = logging.getLogger(__name__)

from itertools import izip, izip_longest, product

from ableton.v2.base import slicer, to_slice, liveobj_changed, group, flatten, listens
from ableton.v2.control_surface.elements.button import ButtonElement
from ableton.v2.control_surface.elements.button_matrix import ButtonMatrixElement
from ableton.v2.control_surface.components.channel_strip import ChannelStripComponent
from ableton.v2.control_surface.compound_component import CompoundComponent
from ableton.v2.control_surface.control_element import ControlElement
from ableton.v2.control_surface.control_surface import ControlSurface
from ableton.v2.control_surface.component import Component as ControlSurfaceComponent
from ableton.v2.control_surface.elements.encoder import EncoderElement
from ableton.v2.control_surface.input_control_element import *
from ableton.v2.control_surface.components.mixer import MixerComponent
from ableton.v2.control_surface.components.session import SessionComponent
from ableton.v2.control_surface.components.transport import TransportComponent
from ableton.v2.control_surface.components.session_navigation import SessionNavigationComponent
from ableton.v2.control_surface.mode import AddLayerMode, LayerMode, ModesComponent, ModeButtonBehaviour, DelayMode
from ableton.v2.control_surface.resource import PrioritizedResource
from ableton.v2.control_surface.skin import Skin
from ableton.v2.control_surface import DeviceBankRegistry
from ableton.v2.control_surface.components.device import DeviceComponent
from ableton.v2.control_surface.layer import Layer
from ableton.v2.control_surface.components.m4l_interface import M4LInterfaceComponent
from ableton.v2.control_surface.elements.combo import ComboElement, DoublePressElement, MultiElement, DoublePressContext
from ableton.v2.control_surface.components.background import BackgroundComponent
from ableton.v2.control_surface.components.session_ring import SessionRingComponent
from ableton.v2.base.slot import *
from ableton.v2.base.task import *

from Push.mode_behaviours import CancellableBehaviour
#from pushbase.instrument_component import InstrumentComponent, NoteLayout
from aumhaa.v2.control_surface.components.fixed_length_recorder import FixedLengthSessionRecordingComponent
from pushbase.auto_arm_component import AutoArmComponent
from pushbase.grid_resolution import GridResolution
from pushbase.playhead_element import PlayheadElement
from pushbase.percussion_instrument_finder_component import PercussionInstrumentFinderComponent, find_drum_group_device

from _Generic.Devices import *

from aumhaa.v2.control_surface import SendLividSysexMode, ShiftedBehaviour, LatchingShiftedBehaviour, DelayedExcludingMomentaryBehaviour
from aumhaa.v2.control_surface.mod import *
from aumhaa.v2.control_surface.instrument_consts import *
from aumhaa.v2.control_surface.components import DeviceNavigator, DeviceSelectorComponent
from aumhaa.v2.control_surface.components.mono_instrument import *
from aumhaa.v2.control_surface.elements import MonoBridgeElement, MonoButtonElement, CodecEncoderElement
from aumhaa.v2.livid import LividControlSurface
from aumhaa.v2.livid import LividSettings
from aumhaa.v2.base.debug import initialize_debug

debug = initialize_debug()

from Map import *

MIDI_NOTE_TYPE = 0
MIDI_CC_TYPE = 1
MIDI_PB_TYPE = 2
MIDI_MSG_TYPES = (MIDI_NOTE_TYPE, MIDI_CC_TYPE, MIDI_PB_TYPE)
MIDI_NOTE_ON_STATUS = 144
MIDI_NOTE_OFF_STATUS = 128
MIDI_CC_STATUS = 176
MIDI_PB_STATUS = 224


class MinimScaleComponent(CompoundComponent):



	def __init__(self, control_surface, *a, **k):
		super(MinimScaleComponent, self).__init__(*a, **k)
		self._control_surface = control_surface
		self._offset = 36
		self._vertoffset = 5
		self._scale = 'Major'
		self._channel = 0
		self.main_layer = LayerMode(self, Layer(priority = 0))
		self.split_layer = LayerMode(self, Layer(priority = 0))
		self.sequencer_layer = LayerMode(self, Layer(priority = 0))
		self.sequencer_shift_layer = LayerMode(self, Layer(priority = 0))
	

	def set_offset(self, val):
		self._offset = val
	

	def set_vertical_offset(self, val):
		self._vertoffset = val
	

	def set_scale_offset(self, val):
		self._scale = val
	

	def set_note_matrix(self, matrix):
		reset_matrix(self._on_note_matrix_value.subject)
		self._on_note_matrix_value.subject = matrix
		#self.update()
	

	def set_keypad_matrix(self, matrix):
		#debug('set keypad matrix: ' + str(matrix) + str(self.is_enabled()))
		reset_matrix(self._on_keypad_matrix_value.subject)
		self._on_keypad_matrix_value.subject = matrix
		if matrix:
			width = matrix.width()
			height = matrix.height()
			#CC_matrix = self._on_note_CC_matrix_value.subject
			vertoffset = self._vertoffset
			offset = self._offset
			scale = self._scale
			if scale is 'Auto':
				scale = DEFAULT_AUTO_SCALE
			scale_len = len(SCALES[scale])
			cur_chan = self._channel
			#shifted = self._parent.is_shifted()
			#current_note = self._note_sequencer._note_editor.editing_note
			for button, (x, y) in matrix.iterbuttons():
				if button:
					note_pos = x + (abs((height-1)-y)*vertoffset)
					note = offset + SCALES[scale][note_pos%scale_len] + (12*int(note_pos/scale_len))
					#if note is current_note:
					#	button.scale_color = 'MonoInstrument.Keys.SelectedNote'
					#else:
					button.scale_color = KEYCOLORS[(note%12 in WHITEKEYS) + (((note_pos%scale_len)==0)*2)]
					button.display_press = True
					button._last_flash = 0
					#if shifted:
					#	button.use_default_message()
					#	button.set_enabled(True)
					#else:
					button.set_identifier(note%127)
					button.descriptor = str(NOTENAMES[button._msg_identifier])
					button.set_enabled(False)
					button.set_channel(cur_chan)
					button.set_light(button.scale_color)
			#self._control_surface.release_controlled_track()
	

	@listens('value')
	def _on_note_matrix_value(self, value, x, y, *a, **k):
		debug('on_keys_matrix_value', x, y, value)
	

	@listens('value')
	def _on_note_CC_matrix_value(self, value, x, y, *a, **k):
		debug('on_note_CC_matrix_value', x, y, value)
	

	@listens('value')
	def _on_sequencer_matrix_value(self, value, x, y, *a, **k):
		debug('on_sequencer_matrix_value', x, y, value)
	

	@listens('value')
	def _on_keypad_matrix_value(self, value, x, y, *a, **k):
		debug('on_keypad_matrix_value', x, y, value)
		if value:
			matrix = self._on_keypad_matrix_value.subject
			width = matrix.width()
			height = matrix.height()
			vertoffset = self._vertoffset
			offset = self._offset
			scale = self._scale
			if scale is 'Auto':
				scale = DEFAULT_AUTO_SCALE
			scale_len = len(SCALES[scale])
			cur_chan = self._channel
			note_pos = x + (abs((height-1)-y)*vertoffset)
			note = offset + SCALES[scale][note_pos%scale_len] + (12*int(note_pos/scale_len))
			#self._note_sequencer._note_editor._set_editing_note(note)
			self.set_keypad_matrix(matrix)
	

	@listens('value')
	def _on_split_matrix_value(self, value, x, y, *a, **k):
		pass
	

	def set_note_CC_matrix(self, matrix):
		self._on_note_CC_matrix_value.subject = matrix
		#self.update()
	

	def update(self):
		super(MinimScaleComponent, self).update()
	


class MinimMonoInstrumentComponent(MonoInstrumentComponent):


	def __init__(self, *a, **k):
		super(MinimMonoInstrumentComponent, self).__init__(*a, **k)
	


class MinimTransportComponent(TransportComponent):


	def _update_stop_button_color(self):
		self._stop_button.color = 'Transport.StopOn' if self._play_toggle.is_toggled else 'Transport.StopOff'
	


class Minim(LividControlSurface):


	_sysex_id = 18
	_model_name = 'Minim'

	def __init__(self, c_instance, *a, **k):
		super(Minim, self).__init__(c_instance, *a, **k)
		self._shift_latching = LatchingShiftedBehaviour if SHIFT_LATCHING else ShiftedBehaviour
		self._skin = Skin(MinimColors)
		with self.component_guard():
			self._define_sysex()
			self._setup_monobridge()
			self._setup_controls()
			self._setup_background()
			self._setup_autoarm()
			self._setup_session()
			self._setup_transport()
			self._setup_instrument()
			self._setup_modes() 
			self._setup_m4l_interface()
		self.log_message('<<<<<<<<<<<<<<<<<<<<<<<<< Minim log opened >>>>>>>>>>>>>>>>>>>>>>>>>')
		self.show_message('Minim Control Surface Loaded')
		self._connection_routine.kill()
		self._background.set_enabled(True)
		self._initialize_hardware()
		self.schedule_message(2, self._initialize_script)
	

	def _initialize_hardware(self):
		debug('sending local control off')
		self.local_control_off.enter_mode()
	

	def _initialize_script(self):
		self._on_device_changed.subject = self._device_provider
		self._main_modes.set_enabled(True)
		self._main_modes.selected_mode = 'session'
		self.refresh_state()
		self._connection_routine.kill()
	

	def _setup_controls(self):
		is_momentary = True
		optimized = False
		resource = PrioritizedResource
		#self._fader = 
		self._pad = [[MonoButtonElement(is_momentary = is_momentary, msg_type = MIDI_NOTE_TYPE, channel = CHANNEL, identifier = MINIM_PADS[row][column], name = 'Pad_' + str(column) + '_' + str(row), script = self, skin = self._skin, color_map = COLOR_MAP, optimized_send_midi = optimized, resource_type = resource) for column in range(4)] for row in range(2)]
		self._button = [[MonoButtonElement(is_momentary = is_momentary, msg_type = MIDI_NOTE_TYPE, channel = CHANNEL, identifier = MINIM_BUTTONS[row][column], name = 'Button_' + str(column) + '_' + str(row), script = self, skin = self._skin, color_map = COLOR_MAP, optimized_send_midi = optimized, resource_type = resource) for column in range(4)] for row in range(2)]
		self._side_button = [MonoButtonElement(is_momentary = is_momentary, msg_type = MIDI_NOTE_TYPE, channel = CHANNEL, identifier = MINIM_SIDE_BUTTONS[index], name = 'Side_Button_' + str(index), script = self, skin = self._skin, color_map = COLOR_MAP, optimized_send_midi = optimized, resource_type = resource) for index in range(5)]		
		self._top_button = [MonoButtonElement(is_momentary = is_momentary, msg_type = MIDI_NOTE_TYPE, channel = CHANNEL, identifier = MINIM_TOP_BUTTONS[index], name = 'Top_Button_' + str(index), script = self, skin = self._skin, color_map = COLOR_MAP, optimized_send_midi = optimized, resource_type = resource) for index in range(2)]	
		self._bottom_button = MonoButtonElement(is_momentary = is_momentary, msg_type = MIDI_NOTE_TYPE, channel = CHANNEL, identifier = MINIM_BOTTOM_BUTTON, name = 'Bottom_Button', script = self, skin = self._skin, color_map = COLOR_MAP, optimized_send_midi = optimized, resource_type = resource)	


		self._matrix = ButtonMatrixElement(name = 'Pad_Matrix', rows = [self._button[:][0], self._pad[:][0], self._pad[:][1],self._button[:][1]])
		#self._pad_matrix = ButtonMatrixElement(name = 'Pad_Matrix', rows = self._pad)
		#self._button_matrix = ButtonMatrixElement(name = 'Button_Matrix', rows = self._button)
		self._top_button_matrix = ButtonMatrixElement(name = 'Button_Matrix', rows = [self._top_button])
	

	def _setup_background(self):
		self._background = BackgroundComponent()
		self._background.layer = Layer(priority = 3, matrix = self._matrix.submatrix[:,:], top_buttons = self._top_button_matrix.submatrix[:,:], bottom_button = self._bottom_button)
		self._background.set_enabled(False)
	

	def _define_sysex(self):
		self._livid_settings = LividSettings(model = 18, control_surface = self)
		self.local_control_off = SendLividSysexMode(livid_settings = self._livid_settings, call = 'set_local_control', message = [0])
	

	def _setup_autoarm(self):
		self._auto_arm = AutoArmComponent(name='Auto_Arm')
		self._auto_arm.can_auto_arm_track = self._can_auto_arm_track
		self._auto_arm._update_notification = lambda: None
	

	def _setup_transport(self):
		self._transport = MinimTransportComponent(name = 'Transport') 
		self._transport.layer = Layer(priority = 4, play_button = self._side_button[0], stop_button = self._side_button[1], record_button = self._side_button[2], overdub_button = self._side_button[3])
		self._transport.set_enabled(False)
	

	def _setup_session(self):
		self._session_ring = SessionRingComponent(name = 'Session_Ring', num_tracks = 4, num_scenes = 3)
		self._session = SessionComponent(name = 'Session', session_ring = self._session_ring, auto_name = True, enable_skinning = True)
		self._session.layer = Layer(priority = 4, clip_launch_buttons = self._matrix.submatrix[:,:3], stop_track_clip_buttons = self._matrix.submatrix[:,3])
		#self._session._stop_layer = Layer(priority = 5,  stop_track_clip_buttons = self._matrix.submatrix[:,2:])
		self._session_navigation = SessionNavigationComponent(name = 'Session_Navigation', session_ring = self._session_ring)
		self._session_navigation._horizontal_layer = AddLayerMode(self._session_navigation, Layer(priority = 4, left_button = self._top_button[0], right_button = self._top_button[1]))
		self._session_navigation._vertical_layer = AddLayerMode(self._session_navigation, Layer(priority = 4, up_button = self._top_button[0], down_button = self._top_button[1]))
		self._session_navigation.set_enabled(False)
		#self._session = SessionComponent(name = 'Session', session_ring = self._session_ring)
		#self._mixer = MinimMixerComponent(num_returns = 4, name = 'Mixer', tracks_provider = self._session_ring, invert_mute_feedback = True, auto_name = True)
		#self._mixer._mix_layer = AddLayerMode(self._mixer, Layer(priority = 4, volume_controls = self._encoder_matrix.submatrix[:8,3],
		#							pan_controls = self._encoder_matrix.submatrix[:8,2],
		#							send_controls = self._encoder_matrix.submatrix[:8, :2],
		#							))
		#self._mixer._solo_mute_layer = AddLayerMode(self._mixer, Layer(priority = 4, solo_buttons = self._button_matrix.submatrix[:8,2],
		#							mute_buttons = self._button_matrix.submatrix[:8,3],
		#							))
		#self._mixer._select_layer = AddLayerMode(self._mixer, Layer(priority = 4, track_select_buttons = self._code_keys))
		#self._mixer._sends_layer = AddLayerMode(self._mixer, Layer(priority = 4, send_controls = self._encoder_matrix.submatrix[:, :]))
		#self._mixer.set_enabled(False)
	

	def _setup_instrument(self):
		self._grid_resolution = GridResolution()

		self._c_instance.playhead.enabled = True
		self._playhead_element = PlayheadElement(self._c_instance.playhead)
		#self._playhead_element.reset()

		self._drum_group_finder = PercussionInstrumentFinderComponent(device_parent=self.song.view.selected_track)

		self._instrument = MinimMonoInstrumentComponent(name = 'InstrumentComponent', script = self, skin = self._skin, drum_group_finder = self._drum_group_finder, grid_resolution = self._grid_resolution, settings = DEFAULT_INSTRUMENT_SETTINGS, device_provider = self._device_provider, parent_task_group = self._task_group)
		self._instrument.layer = Layer(priority = 6, shift_button = self._side_button[3])

		self._instrument.keypad_options_layer = AddLayerMode(self._instrument, Layer(priority = 6, 
									scale_up_button = self._button[0][3], 
									scale_down_button = self._button[0][2],
									offset_up_button = self._button[0][1], 
									offset_down_button = self._button[0][0],
									vertical_offset_up_button = self._top_button[1],
									vertical_offset_down_button = self._top_button[0]))
		self._instrument.drumpad_options_layer = AddLayerMode(self._instrument, Layer(priority = 6, 
									scale_up_button = self._button[0][3],
									scale_down_button = self._button[0][2],
									drum_offset_up_button = self._button[0][1], 
									drum_offset_down_button = self._button[0][0],))

		self._instrument._keypad.main_layer = LayerMode(self._instrument._keypad, Layer(priority = 6, keypad_matrix = self._matrix.submatrix[:,1:3]))
		self._instrument._keypad.select_layer = LayerMode(self._instrument._keypad, Layer(priority = 6, keypad_select_matrix = self._matrix.submatrix[:, 1:3]))

		self._instrument._drumpad.main_layer = LayerMode(self._instrument._drumpad, Layer(priority = 6, drumpad_matrix = self._matrix.submatrix[:,1:3]))
		self._instrument._drumpad.select_layer = LayerMode(self._instrument._drumpad, Layer(priority = 6, drumpad_select_matrix = self._matrix.submatrix[:,1:3]))

		self._instrument._main_modes = ModesComponent(name = 'InstrumentModes')
		self._instrument._main_modes.add_mode('disabled', [])
		self._instrument._main_modes.add_mode('drumpad', [self._instrument._drumpad, self._instrument._drumpad.main_layer])
		self._instrument._main_modes.add_mode('drumpad_shifted', [self._instrument._drumpad, self._instrument._drumpad.select_layer, self._instrument.drumpad_options_layer])
		self._instrument._main_modes.add_mode('keypad', [self._instrument._keypad, self._instrument._keypad.main_layer])
		self._instrument._main_modes.add_mode('keypad_shifted', [self._instrument._keypad, self._instrument._keypad.select_layer, self._instrument.keypad_options_layer])
		self._instrument.register_component(self._instrument._main_modes)

		self._instrument.set_enabled(False)
		#self._instrument.audioloop_layer = LayerMode(self._instrument, Layer(priority = 6, loop_selector_matrix = self._base_grid))
	

	def _setup_shift_modes(self):
		self._main_shift_modes = ModesComponent(name = 'MainShiftModes')
		self._main_shift_modes.add_mode('disabled', [self.normal_encoder_sysex], cycle_mode_button_color = 'DefaultButton.Off')
		self._main_shift_modes.add_mode('enabled', [self.slow_encoder_sysex], cycle_mode_button_color = 'DefaultButton.On')  #, self._value_default
		self._main_shift_modes.layer = Layer(priority = 4, cycle_mode_button = self._livid)
		self._main_shift_modes.set_enabled(False)
		self._main_shift_modes.selected_mode = 'disabled'

		self._mod_shift_modes = ModesComponent(name = 'ModShiftModes')
		self._mod_shift_modes.layer = Layer(priority = 4, cycle_mode_button = self._livid)
		self._mod_shift_modes.set_enabled(False)
	

	def _setup_modes(self):
		self._main_modes = ModesComponent(name = 'MainModes')
		self._main_modes.add_mode('disabled', [])
		self._main_modes.add_mode('session_shifted', [self._session_navigation, self._session_navigation._vertical_layer], groups = ['shifted'], behaviour = self._shift_latching(color = 'Mode.Main'))
		self._main_modes.add_mode('session', [ self._session, self._session_navigation, self._session_navigation._horizontal_layer, self._transport], behaviour = self._shift_latching(color = 'Mode.Main'))
		self._main_modes.add_mode('instrument_shifted', [self._instrument], groups = ['shifted'], behaviour = self._shift_latching(color = 'Mode.Main'))
		self._main_modes.add_mode('instrument', [self._instrument, self._transport], behaviour = self._shift_latching(color = 'Mode.Main'))

		self._main_modes.layer = Layer(priority = 6, session_button = self._side_button[4], instrument_button = self._side_button[3])
		self._main_modes.set_enabled(False)
		self._main_modes.selected_mode = 'disabled'

		self._test.subject = self._main_modes
	


	@listens('selected_mode')
	def _test(self, *a):
		comps = [self._main_modes, self._instrument, self._instrument._main_modes, self._instrument._selected_session, self._session]
		debug('VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV')
		debug('main mode:', self._main_modes.selected_mode)
		debug('instrument mode:', self._instrument._main_modes.selected_mode)
		#debug('modswitcher mode:', self._modswitcher.selected_mode)
		#debug('instrument matrix mode:', self._instrument._matrix_modes.selected_mode)
		for comp in comps:
			debug(comp.name, 'is enabled:', comp.is_enabled())
		debug('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
	

	def _can_auto_arm_track(self, track):
		routing = track.current_input_routing
		return routing == 'Ext: All Ins' or routing == 'All Ins' or routing.startswith('Livid Minim Input')
	


	def _setup_m4l_interface(self):
		self._m4l_interface = M4LInterfaceComponent(controls=self.controls, component_guard=self.component_guard)
		self.get_control_names = self._m4l_interface.get_control_names
		self.get_control = self._m4l_interface.get_control
		self.grab_control = self._m4l_interface.grab_control
		self.release_control = self._m4l_interface.release_control
	

	@listens('device')
	def _on_device_changed(self):
		pass
	

	"""general functionality"""
	def disconnect(self):
		self.log_message('<<<<<<<<<<<<<<<<<<<<<<<<< Minim log closed >>>>>>>>>>>>>>>>>>>>>>>>>')
		super(Minim, self).disconnect()
	

