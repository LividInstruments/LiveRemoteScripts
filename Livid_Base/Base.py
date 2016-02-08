# by amounra 0613 : http://www.aumhaa.com

from __future__ import with_statement
import Live
import math
import sys
import re
#from re import *
from itertools import imap, chain, starmap

""" _Framework files """
from _Framework.Dependency import inject
from _Framework.ButtonElement import ButtonElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ClipSlotComponent import ClipSlotComponent
from _Framework.CompoundComponent import CompoundComponent
from _Framework.ControlElement import ControlElement, ControlElementClient
from _Framework.ControlSurface import ControlSurface, OptimizedControlSurface
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.DisplayDataSource import DisplayDataSource
from _Framework.DeviceComponent import DeviceComponent
from _Framework.EncoderElement import EncoderElement
from _Framework.InputControlElement import *
from _Framework.ModeSelectorComponent import ModeSelectorComponent
from _Framework.NotifyingControlElement import NotifyingControlElement
from _Framework.SceneComponent import SceneComponent
from _Framework.SessionComponent import SessionComponent
from _Framework.SliderElement import SliderElement
from _Framework.SubjectSlot import *
from _Framework.TransportComponent import TransportComponent
from _Framework.PhysicalDisplayElement import *
from _Framework.SubjectSlot import subject_slot, subject_slot_group
from _Framework.Layer import Layer
from _Framework.Skin import Skin
from _Framework.M4LInterfaceComponent import M4LInterfaceComponent
from _Framework.ComboElement import ComboElement, DoublePressElement, MultiElement, DoublePressContext
from _Framework.ModesComponent import Mode, CompoundMode, DisableMode, EnablingModesComponent, DelayMode, AddLayerMode, LayerMode, MultiEntryMode, ModesComponent, SetAttributeMode, ModeButtonBehaviour, CancellableBehaviour, AlternativeBehaviour, ReenterBehaviour, DynamicBehaviourMixin, ExcludingBehaviourMixin, ImmediateBehaviour, LatchingBehaviour, ModeButtonBehaviour
from _Framework.ClipCreator import ClipCreator
from _Framework.Resource import PrioritizedResource
from _Framework.Util import mixin
from _Framework.BackgroundComponent import BackgroundComponent
from _Framework.SessionRecordingComponent import *
from _Framework.ViewControlComponent import ViewControlComponent
from _Framework.DrumGroupComponent import DrumGroupComponent


"""Custom files, overrides, and files from other scripts"""
from _Mono_Framework.MonoButtonElement import *
from _Mono_Framework.LividUtilities import LividSettings
from _Mono_Framework.MonoEncoderElement import MonoEncoderElement
from _Mono_Framework.MonoBridgeElement import MonoBridgeElement
from _Mono_Framework.MonoDeviceComponent import MonoDeviceComponent
from _Mono_Framework.MonoMixerComponent import MixerComponent
from _Mono_Framework.DeviceNavigator import DeviceNavigator
from _Mono_Framework.TranslationComponent import TranslationComponent
from _Mono_Framework.MonoM4LInterfaceComponent import MonoM4LInterfaceComponent
from _Mono_Framework.MonoModes import SendLividSysexMode, MomentaryBehaviour, ExcludingMomentaryBehaviour, DelayedExcludingMomentaryBehaviour, CancellableBehaviourWithRelease, ShiftedBehaviour, LatchingShiftedBehaviour, FlashingBehaviour
from _Mono_Framework.ModDevices import *
from _Mono_Framework.Mod import *
from _Mono_Framework.Debug import *
from _Mono_Framework.LividColors import *
from _Mono_Framework.MonoInstrumentComponent import *
from _Mono_Framework.OSCDisplay import OSCDisplay

import _Mono_Framework.modRemixNet as RemixNet
import _Mono_Framework.modOSC

from _Mono_Framework._deprecated.AutoArmComponent import AutoArmComponent
from _Mono_Framework._deprecated.GridResolution import GridResolution
from _Mono_Framework._deprecated.SessionRecordingComponent import FixedLengthSessionRecordingComponent

debug = initialize_debug()

DIRS = [47, 48, 50, 49]
_NOTENAMES = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
NOTENAMES = [(_NOTENAMES[index%12] + ' ' + str(int(index/12))) for index in range(128)]

from Map import *

if OSC_TRANSMIT:
	from _Mono_Framework.MonoButtonElement import DescriptiveMonoButtonElement as MonoButtonElement
	from _Mono_Framework.MonoBridgeElement import OSCMonoBridgeElement as MonoBridgeElement

MODE_DATA = {'Clips': 'L', 
			'Clips_shifted': 'L', 
			'Sends': 'S',
			'Sends_shifted': 'S',
			'Device': 'D',
			'Device_shifted': 'D',
			'User': 'U',
			'User_shifted': 'U',
			'Mod': 'M',
			'Select': 'C'}

_base_translations = {' ':42, '0': 0, '1': 1,'2': 2, '3': 3,'4': 4,'5': 5,'6': 6,'7': 7,'8': 8,'9': 9,'A': 10,'B': 11,'C': 12,'D': 13,'E': 14,'F': 15,'G': 16,'H': 17,'I': 18,'J': 19,'K': 20,'L': 21,'M': 22,'N': 23,'O': 24,'P': 25,'Q': 26,'R': 27,'S': 28,'T': 29,'U': 30,'V': 31,'W': 32,'X': 33,'Y': 34,'Z': 35,'a': 10,'b': 11,'c': 12,'d': 13,'e': 14,'f': 15,'g': 16,'h': 17,'i': 18,'j': 19,'k': 20,'l': 21,'m': 22,'n': 23,'o': 24,'p': 25,'q': 26,'r': 27,'s': 28,'t': 29,'u': 30,'v': 31,'w': 32,'x': 33,'y': 34,'z': 35,'_': 39, '-': 42, '?': 127}


FADER_COLORS = [96, 124, 108, 120, 116, 100, 104, 112]

MIDIBUTTONMODE = (240, 0, 1, 97, 12, 66, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 247)
USERBUTTONMODE = (240, 0, 1, 97, 12, 66, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 247)
LIVEBUTTONMODE = (240, 0, 1, 97, 12, 66, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 247)
SPLITVERTICAL = (240, 0, 1, 97, 12, 66, 5, 5, 5, 5, 1, 1, 1, 1, 5, 5, 5, 5, 1, 1, 1, 1, 5, 5, 5, 5, 1, 1, 1, 1, 5, 5, 5, 5, 1, 1, 1, 1, 247)
SPLITHORIZONTAL = (240, 0, 1, 97, 12, 66, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 247)
SPLITVERTICALATON = (240, 0, 1, 97, 12, 66,  5, 5, 5, 5, 3, 3, 3, 3, 5, 5, 5, 5, 3, 3, 3, 3, 5, 5, 5, 5, 3, 3, 3, 3, 5, 5, 5, 5, 3, 3, 3, 3, 247)
SPLITHORIZONTALATON = (240, 0, 1, 97, 12, 66, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,247)

ATOFFBUTTONMODE = (240, 0, 1, 97, 12, 10, 36, 0, 37, 0, 38, 0, 39, 0, 40, 0, 41, 0, 42, 0, 43, 0, 44, 0, 45, 0, 46, 0, 47, 0, 48, 0, 49, 0, 50, 0, 51, 0, 52, 0, 53, 0, 54, 0, 55, 0, 56, 0, 57, 0, 58, 0, 59, 0, 60, 2, 61, 0, 62, 0, 63, 0, 64, 0, 65, 0, 66, 0, 67, 0, 247)
ATONBUTTONMODE = (240, 0, 1, 97, 12, 10, 36, 2, 37, 2, 38, 2, 39, 2, 40, 2, 41, 2, 42, 2, 43, 2, 44, 2, 45, 2, 46, 2, 47, 2, 48, 2, 49, 2, 50, 2, 51, 2, 52, 2, 53, 2, 54, 2, 55, 2, 56, 2, 57, 2, 58, 2, 59, 2, 60, 2, 61, 2, 62, 2, 63, 2, 64, 2, 65, 2, 66, 2, 67, 2, 247)

CLIPS_FADER_COLORS = tuple([240, 0, 1, 97, 12, 61, 7, 7, 7, 7, 7, 7, 7, 7, 2, 247])
SENDS_FADER_COLORS = tuple([240, 0, 1, 97, 12, 61, 5, 5, 5, 5, 4, 4, 4, 4, 2, 247])
DEVICE_FADER_COLORS = tuple([240, 0, 1, 97, 12, 61, 6, 6, 6, 6, 6, 6, 6, 6, 2, 247])
USER_FADER_COLORS =tuple([240, 0, 1, 97, 12, 61, 1, 1, 1, 1, 1, 1, 1, 1, 2, 247])
MOD_FADER_COLORS = tuple([240, 0, 1, 97, 12, 61, 7, 7, 7, 7, 7, 7, 7, 7, 2, 247])

STREAMINGON = (240, 0, 1, 97, 12, 62, 127, 247)
STREAMINGOFF = (240, 0, 1, 97, 12, 62, 0, 247)
LINKFUNCBUTTONS = (240, 0, 1, 97, 12, 68, 1, 247)
DISABLECAPFADERNOTES = (240, 0, 1, 97, 12, 69, 1, 247)
QUERYSURFACE = (240, 126, 127, 6, 1, 247)

ATOFF = [36, 0, 37, 0, 38, 0, 39, 0, 40, 0, 41, 0, 42, 0, 43, 0, 44, 0, 45, 0, 46, 0, 47, 0, 48, 0, 49, 0, 50, 0, 51, 0, 52, 0, 53, 0, 54, 0, 55, 0, 56, 0, 57, 0, 58, 0, 59, 0, 60, 2, 61, 0, 62, 0, 63, 0, 64, 0, 65, 0, 66, 0, 67, 0]
ATON = [36, 2, 37, 2, 38, 2, 39, 2, 40, 2, 41, 2, 42, 2, 43, 2, 44, 2, 45, 2, 46, 2, 47, 2, 48, 2, 49, 2, 50, 2, 51, 2, 52, 2, 53, 2, 54, 2, 55, 2, 56, 2, 57, 2, 58, 2, 59, 2, 60, 2, 61, 2, 62, 2, 63, 2, 64, 2, 65, 2, 66, 2, 67, 2]

STREAMINGON = [127]
STREAMINGOFF = [0]
MIDIBUTTONMODE = [1 for index in range(32)]
USERBUTTONMODE = [3 for index in range(32)]
LIVEBUTTONMODE = [5 for index in range(32)]
SPLITVERTICAL = [5, 5, 5, 5, 1, 1, 1, 1, 5, 5, 5, 5, 1, 1, 1, 1, 5, 5, 5, 5, 1, 1, 1, 1, 5, 5, 5, 5, 1, 1, 1, 1]
SPLITHORIZONTAL = [1 for index in range(16)] + [5 for index in range(16)]
SPLITVERTICALATON = [5, 5, 5, 5, 3, 3, 3, 3, 5, 5, 5, 5, 3, 3, 3, 3, 5, 5, 5, 5, 3, 3, 3, 3, 5, 5, 5, 5, 3, 3, 3, 3,]
SPLITHORIZONTALATON = [3 for index in range(16)] + [5 for index in range(16)]
CLIPS_FADER_COLORS = [7, 7, 7, 7, 7, 7, 7, 7, 2]
SENDS_FADER_COLORS = [5, 5, 5, 5, 4, 4, 4, 4, 2]
DEVICE_FADER_COLORS = [6, 6, 6, 6, 6, 6, 6, 6, 2]
USER_FADER_COLORS = [1, 1, 1, 1, 1, 1, 1, 1, 2]
MOD_FADER_COLORS = [7, 7, 7, 7, 7, 7, 7, 7, 2]


MIDI_NOTE_TYPE = 0
MIDI_CC_TYPE = 1
MIDI_PB_TYPE = 2
MIDI_MSG_TYPES = (MIDI_NOTE_TYPE, MIDI_CC_TYPE, MIDI_PB_TYPE)
MIDI_NOTE_ON_STATUS = 144
MIDI_NOTE_OFF_STATUS = 128
MIDI_CC_STATUS = 176
MIDI_PB_STATUS = 224

_Q = Live.Song.Quantization
LAUNCH_QUANTIZATION = (_Q.q_quarter,
 _Q.q_half,
 _Q.q_bar,
 _Q.q_2_bars,
 _Q.q_4_bars,
 _Q.q_8_bars,
 _Q.q_8_bars,
 _Q.q_8_bars)

def is_device(device):
	return (not device is None and isinstance(device, Live.Device.Device) and hasattr(device, 'name'))


def make_pad_translations(chan):
	return tuple((x%4, int(x/4), x+16, chan) for x in range(16))


def return_empty():
	return []


def make_default_skin():
	return Skin(BaseColors)



class BasePhysicalDisplayElement(PhysicalDisplayElement):


	def __init__(self, *a, **k):
		super(BasePhysicalDisplayElement, self).__init__(*a, **k)
		self._last_sent_messages = []
		self._message_clear_all = [tuple([176, 16, 127]), tuple([176, 17, 127])]
	

	def display_message(self, message, *a, **k):
		#debug('display_message', message)
		if not self._block_messages:
			message = str(message) + '  '
			self._message_to_send = [tuple([176, 34, self._translate_char(message[0])]), tuple([176, 35, self._translate_char(message[1])])]
			self._request_send_message()
	

	def update(self):
		self._message_to_send = len(self._logical_segments) > 0 and not self._block_messages and None
		self._request_send_message()
	

	def clear_send_cache(self):
		self._last_sent_messages = []
		self._request_send_message()
	

	def reset(self):
		super(PhysicalDisplayElement, self).reset()
		if not self._block_messages:
			self._message_to_send = self._message_clear_all != None and self._message_clear_all
		self._request_send_message()
	

	def set_translation_table(self, translation_table):
		assert('?' in translation_table.keys())
		self._translation_table = translation_table
	

	def _send_message(self):
		if not self._block_messages:
			if self._message_to_send is None:
				self._message_to_send = self._build_message(map(first, self._central_resource.owners))
			self.send_midi(self._message_to_send)
	

	def send_midi(self, messages):
		if messages != self._last_sent_messages:
			for message in  messages:
				#debug('sending message:', message)
				ControlElement.send_midi(self, message)
			self._last_sent_message = messages
	

	def _build_display_message(self, display):
		message = str(display.display_string) + ' '
		return message[0]
	

	def _build_message(self, displays):
		messages = []
		if len(displays) is 1:
			message = self._translate_string(' ' + str(displays[0].display_string))
			#debug('message len:', len(message), 'message:', message)
			messages = [tuple([176, 34, message[-2]]), tuple([176, 35, message[-1]])]
		elif len(displays):
			for i in range(2):
				messages.append(tuple([176, 34 + i, self._translate_char(self._build_display_message(displays[i]))]))
		#debug('messages to send:', messages)
		return messages
	


class BaseDisplayingModesComponent(ModesComponent):


	def __init__(self, *a, **k):
		super(BaseDisplayingModesComponent, self).__init__(*a, **k)
		self._mode_data_string = {}
		self._data_source = DisplayDataSource()
	

	def add_mode(self, name, mode_or_component, display_string = '', *a, **k):
		super(BaseDisplayingModesComponent, self).add_mode(name, mode_or_component, *a, **k)
		self._mode_data_string[name] = display_string
	

	def update(self, *a, **k):
		super(BaseDisplayingModesComponent, self).update(*a, **k)
		self._update_data_sources(self.selected_mode)
	

	def _do_enter_mode(self, name, *a, **k):
		super(BaseDisplayingModesComponent, self)._do_enter_mode(name, *a, **k)
		self._update_data_sources(name)
	

	def _update_data_sources(self, selected, *a, **k):
		if self.is_enabled():
			#debug('setting data string to:', self._mode_data_string[selected])
			self._data_source.set_display_string(self._mode_data_string[selected])
	

	def set_display(self, display, *a, **k):
		if display:
			display.set_data_sources([self._data_source])
	


class BaseDisplayingTranslationComponent(TranslationComponent):


	def __init__(self, *a, **k):
		super(BaseDisplayingTranslationComponent, self).__init__(*a, **k)
		self._data_source = DisplayDataSource()
	

	def update(self):
		super(BaseDisplayingTranslationComponent, self).update()
		self._update_data_sources()
	

	def _update_data_sources(self):
		if self.is_enabled():
			self._data_source.set_display_string('U' + str(min(9, max(1, (self._channel-self._user_channel_offset+1)))))
	

	def set_display(self, display, *a, **k):
		if display:
			display.set_data_sources([self._data_source])
	


class BaseDeviceComponent(DeviceComponent):


	def update(self):
		super(BaseDeviceComponent, self).update()
		if self.is_enabled() and self._device != None:
			self._device_bank_registry.set_device_bank(self._device, self._bank_index)
			if self._parameter_controls != None:
				old_bank_name = self._bank_name
				self._assign_parameters()
				if self._bank_name != old_bank_name:
					self._show_msg_callback(self._device.name + ' Bank: ' + self._bank_name)
		elif self._parameter_controls != None:
			self._release_parameters(self._parameter_controls)
			for control in self._parameter_controls:
				if control:
					control.send_value(0, True)
		if self.is_enabled():
			self._update_on_off_button()
			self._update_lock_button()
			self._update_device_bank_buttons()
			self._update_device_bank_nav_buttons()
	


class BaseSessionRecordingComponent(FixedLengthSessionRecordingComponent):


	def __init__(self, *a, **k):
		self._length_value = 1
		super(BaseSessionRecordingComponent, self).__init__(*a, **k)
		self._length_buttons = []
	

	def set_length_button(self, button):
		if self._on_length_value.subject:
			self._on_length_value.subject.descriptor = None
		if button:
			button.descriptor = 'Recorder.FixedLength'
		super(BaseSessionRecordingComponent, self).set_length_button(button)
	

	def _get_selected_length(self):
		song = self.song()
		length = 2.0 ** (LENGTH_VALUES[self._length_value])
		quant = LAUNCH_QUANTIZATION[(LENGTH_VALUES[self._length_value])]
		#if self._length_value > 1:
		length = length * song.signature_numerator / song.signature_denominator
		return (length, quant)
	

	def set_length_buttons(self, buttons):
		self._on_length_buttons_value.subject = buttons
		self.update_length_buttons()
	

	@subject_slot('value')
	def _on_length_buttons_value(self, value, x, y, *a, **k):
		if value > 0:
			self._length_value = x
			self.update_length_buttons()
	

	def update(self, *a, **k):
		super(BaseSessionRecordingComponent, self).update(*a, **k)
		if self.is_enabled():
			self.update_length_buttons()
	

	def update_length_buttons(self):
		buttons = self._on_length_buttons_value.subject
		if buttons:
			for button, (x, y) in buttons.iterbuttons():
				if button:
					if x == self._length_value:
						button.turn_on()
					else:
						button.turn_off()
	


class BlockingMonoButtonElement(MonoButtonElement):


	def __init__(self, *a, **k):
		super(BlockingMonoButtonElement, self).__init__(*a, **k)
		self.display_press = False
		self._last_flash = 0
		self.scale_color = 0
	


class BaseClipSlotComponent(ClipSlotComponent):


	@subject_slot('name')
	def _on_clip_name_changed(self):
		debug('clipname changed')
		if OSC_TRANSMIT:
			self.update()
	

	def _update_clip_property_slots(self):
		clip = self._clip_slot.clip if self._clip_slot else None
		self._on_clip_color_changed.subject = clip
		self._on_clip_name_changed.subject = clip
		self._on_clip_playing_state_changed.subject = clip
		self._on_recording_state_changed.subject = clip
	

	def report_clip_name(self):
		button = self._launch_button_value.subject
		if button and self._clip_slot != None:
			clip_name = '' if not self.has_clip() else self._clip_slot.clip.name
			button.descriptor = str(clip_name)
			button._last_reported_descriptor = None
	

	def set_launch_button(self, button):
		if self._launch_button_value.subject:
			self._launch_button_value.subject.descriptor = ''
		self._launch_button_value.subject = button
		self.update()
	

	def update(self):
		#super(BaseClipSlotComponent, self).update()
		self._has_fired_slot = False
		button = self._launch_button_value.subject
		self.report_clip_name()
		if self._allow_updates:
			if self.is_enabled() and button != None:
				value_to_send = self._feedback_value()
				if value_to_send in (None, -1):
					button.set_light('Session.Empty')
				elif in_range(value_to_send, 0, 128):
					button.send_value(value_to_send)
				else:
					button.set_light(value_to_send)
		else:
			self._update_requests += 1
	


class BaseSceneComponent(SceneComponent):


	clip_slot_component_type = BaseClipSlotComponent


class BaseSessionComponent(SessionComponent):


	scene_component_type = BaseSceneComponent

	def __init__(self, num_tracks, num_scenes, *a, **k):
		super(BaseSessionComponent, self).__init__(num_tracks, num_scenes, *a, **k)
	

	def set_clip_launch_buttons(self, buttons):
		assert(not buttons or (buttons.width() <= self._num_tracks and buttons.height() <= self._num_scenes))
		if buttons:
			for button, (x, y) in buttons.iterbuttons():
				if button:
					button.set_off_value(0)
				scene = self.scene(y)
				slot = scene.clip_slot(x)
				slot.set_launch_button(button)

		else:
			for x, y in product(xrange(self._num_tracks), xrange(self._num_scenes)):
				scene = self.scene(y)
				slot = scene.clip_slot(x)
				slot.set_launch_button(None)
	

	def set_scene_launch_buttons(self, buttons):
		assert(not buttons or (buttons.height() == self._num_scenes and buttons.width() == 1))
		if buttons:
			for button, (_, x) in buttons.iterbuttons():
				scene = self.scene(x)
				scene.set_launch_button(button)
				if button:
					button.send_value(7, True)

		else:
			for x in xrange(self._num_scenes):
				scene = self.scene(x)
				scene.set_launch_button(None)
	


class BaseFaderArray(Array):


	def __init__(self, name, size, active_handlers = return_empty):
		self._active_handlers = active_handlers
		self._name = name
		self._cell = [StoredElement(self._name + '_' + str(num), _num = num, _mode = 1, _value = 7) for num in range(size)]
	

	def value(self, num, value = 0):
		element = self._cell[num]
		element._value = value % 8
		self.update_element(element)
	

	def mode(self, num, mode = 0):
		element = self._cell[num]
		element._mode = mode % 4
		self.update_element(element)
	

	def update_element(self, element):	
		for handler in self._active_handlers():
			handler.receive_address(self._name, element._num, (FADER_COLORS[element._value]) + element._mode )
	


class StoredControlElement(StoredElement):


	def __init__(self, *a, **k):
		self._id = -1
		self._channel = -1
		super(StoredControlElement, self).__init__(*a, **k)
	

	def id(self, id):
		self._id = id
		self.update_element()
	

	def channel(self, channel):
		self._channel = channel
		self.udpate_element()
	


class BaseGrid(Grid):


	def __init__(self, name, width, height, active_handlers = return_empty, *a, **k):
		super(BaseGrid, self).__init__(name, width, height, active_handlers = return_empty, *a, **k)
		self._cell = [[StoredControlElement(active_handlers, _name = self._name + '_' + str(x) + '_' + str(y), _x = x, _y = y, _identifier = -1, _channel = -1) for y in range(height)] for x in range(width)]
	

	def identifier(self, x, y, identifier = -1):
		element = self._cell[x][y]
		element._identifier = min(127, max(-1, identifier))

		self.update_element(element)
	

	def channel(self, x, y, channel = -1):
		element = self._cell[x][y]
		element._channel = min(15, max(-1, channel))
		self.update_element(element)
	

	def update_element(self, element):
		for handler in self._active_handlers():
			handler.receive_address(self._name, element._x, element._y, value = element._value, identifier = element._identifier, channel = element._channel)
	


class BaseModHandler(ModHandler):


	def __init__(self, *a, **k):
		self._base_grid = None
		self._base_grid_CC = None
		self._fader_color_override = False
		addresses = {'base_grid': {'obj': BaseGrid('base_grid', 8, 4), 'method':self._receive_base_grid},
					'base_fader': {'obj': BaseFaderArray('base_fader', 8), 'method':self._receive_base_fader}}
		super(BaseModHandler, self).__init__(addresses = addresses, *a, **k)
		self._is_shifted = False
		self.nav_box = self.register_component(NavigationBox(self, 16, 16, 8, 4, self.set_offset))
	

	def _receive_base_grid(self, x, y, value = -1, identifier = -1, channel = -1, *a, **k):
		#debug('_receive_base_grid:', x, y, value, identifier, channel)
		mod = self.active_mod()
		if mod and not mod.legacy and self._base_grid_value.subject:
			value > -1 and self._base_grid_value.subject.send_value(x, y, value, True)
			button = self._base_grid_value.subject.get_button(x, y)
			if button:
				new_identifier = identifier if identifier > -1 else button._original_identifier
				new_channel = channel if channel > -1 else button._original_channel
				button._msg_identifier != new_identifier and button.set_identifier(new_identifier)
				button._msg_channel != new_channel and button.set_channel(new_channel)
				button.set_enabled((channel, identifier) == (-1, -1))
	

	def _receive_base_fader(self, num, value):
		#self.log_message('_receive_base_fader: %s %s' % (num, value))
		if self.is_enabled():
			self._script._send_midi((191, num+10, value))
	

	def _receive_shift(self, value):
		pass
	

	def _receive_grid(self, x, y, *a, **k):
		#debug('receive grid', x, y, k.items())
		mod = self.active_mod()
		if mod and mod.legacy:
			x = x - self.x_offset
			y = y - self.y_offset
			if x in range(8) and y in range(4):
				self._receive_base_grid(x, y, *a, **k)
	

	def _receive_grid(self, x, y, value = -1, identifier = False, channel = False, *a, **k):
		#debug('receive grid', x, y, value)
		mod = self.active_mod()
		if mod and mod.legacy and self._base_grid_value.subject:
			x = x - self.x_offset
			y = y - self.y_offset
			if x in range(8) and y in range(4):
				value > -1 and self._base_grid_value.subject.send_value(x, y, value, True)
				if identifier or channel:
					button = self._base_grid_value.subject.get_button(x, y)
					if button:
						identifier and button.set_identifier(identifier if identifier > -1 else button._original_identifier)
						channel and button.set_channel(channel if channel > -1 else button._original_channel)
						button.set_enabled(button._msg_identifier == button._original_identifier and button._msg_channel == button._original_channel)
	

	def set_base_grid(self, grid):
		#debug('set base grid:', grid,)
		old_grid = self._base_grid_value.subject
		if old_grid:
			for button, _ in old_grid.iterbuttons():
				button and button.use_default_message() 
		self._base_grid = grid
		self._base_grid_value.subject = self._base_grid
	

	def set_base_grid_CC(self, grid):
		self._base_grid_CC = grid
		self._base_grid_CC_value.subject = self._base_grid_CC
	

	def set_background_buttons(self, buttons):
		if buttons:
			for button, _ in buttons.iterbuttons():
				button and button.turn_off()
	

	def set_key_buttons(self, buttons, *a, **k):
		self._keys_value.subject and self._keys_value.subject.reset()
		super(BaseModHandler, self).set_key_buttons(buttons, *a, **k)
	

	@subject_slot('value')
	def _keys_value(self, value, x, y, *a, **k):
		self.active_mod() and self.active_mod().send('key', x, value)
	

	@subject_slot('value')
	def _base_grid_value(self, value, x, y, *a, **k):
		#debug('_base_grid_value ', x, y, value)
		mod = self.active_mod()
		if mod:
			if mod.legacy:
				mod.send('grid', x + self.x_offset, y + self.y_offset, value)
			else:
				mod.send('base_grid', x, y, value)
		
	

	@subject_slot('value')
	def _base_grid_CC_value(self, value, x, y, *a, **k):
		#debug('_base_grid_CC_value', x, y, value)
		mod = self.active_mod()
		if mod:
			if mod.legacy:
				mod.send('grid_CC', x + self.x_offset , y + self.y_offset, value)
			else:
				mod.send('base_grid_CC', x, y, value)
	

	@subject_slot('value')
	def _shift_value(self, value, *a, **k):
		self._is_shifted = not value is 0
		mod = self.active_mod()
		if mod:
			mod.send('shift', value)
		if self._is_shifted:
			self.shift_layer.enter_mode()
			if mod and mod.legacy:
				self.legacy_shift_layer.enter_mode()
		else:
			self.legacy_shift_layer.leave_mode()
			self.shift_layer.leave_mode()
		self.update()
	

	@subject_slot('appointed_device')
	def _on_device_changed(self):
		super(BaseModHandler, self)._on_device_changed()
		self._script._on_device_changed()
	

	def select_mod(self, *a, **k):
		super(BaseModHandler, self).select_mod(*a, **k)
		self._script._on_device_changed()
	
		
	def update(self, *a, **k):
		mod = self.active_mod()
		if mod:
			mod.restore()
		else:
			if not self._base_grid_value.subject is None:
				self._base_grid_value.subject.reset()
			if not self._keys_value.subject is None:
				self._keys_value.subject.reset()
		self.update_buttons()
		#self.update_device()
	


class BaseMonoInstrumentComponent(MonoInstrumentComponent):


	def __init__(self, *a, **k):
		self._base_display = None
		self._keys_offset_data = DisplayDataSource('')
		self._drum_offset_data = DisplayDataSource('')
		self._vertical_offset_data = DisplayDataSource('')
		self._scale_offset_data = DisplayDataSource('')
		super(BaseMonoInstrumentComponent, self).__init__(*a, **k)
	

	def set_shift_button(self, button):
		self._shifted = 0
		self._drumpad._step_sequencer._drum_group._select_button = button  #drum_group uses is_pressed() to determine an action
	

	def set_base_display(self, display):
		self._base_display = display
	

	def _offset_value(self, offset):
		super(BaseMonoInstrumentComponent, self)._offset_value(offset)
		self._keys_offset_data.set_display_string(str(NOTENAMES[offset]))
		self._script._monobridge._send('display2', 'offset', str(NOTENAMES[offset]))
		self._base_display and self._base_display.set_data_sources([self._keys_offset_data])
	

	def _drum_offset_value(self, offset):
		super(BaseMonoInstrumentComponent, self)._drum_offset_value(offset)
		self._drum_offset_data.set_display_string(str(offset))
		self._script._monobridge._send('display2', 'drum_offset', str(offset))
		self._base_display and self._base_display.set_data_sources([self._drum_offset_data])
	

	def _vertical_offset_value(self, offset):
		super(BaseMonoInstrumentComponent, self)._vertical_offset_value(offset)	
		self._vertical_offset_data.set_display_string(str(offset))
		self._script._monobridge._send('display1', 'vert_offset', str(offset))
		self._base_display and self._base_display.set_data_sources([self._vertical_offset_data])	
	

	def _scale_offset_value(self, offset):
		super(BaseMonoInstrumentComponent, self)._scale_offset_value(offset)
		self._scale_offset_data.set_display_string(str(SCALEABBREVS[self._scalenames[offset]]))
		self._script._monobridge._send('display3', 'scale_offset', str(SCALEABBREVS[self._scalenames[offset]]))
		self._base_display and self._base_display.set_data_sources([self._scale_offset_data])
	


class Base(ControlSurface):
	__module__ = __name__
	__doc__ = " Base controller script "


	def __init__(self, c_instance):
		super(Base, self).__init__(c_instance)
		self._connected = False
		self._host_name = 'Base'
		self._color_type = 'OhmRGB'
		self.monomodular = None
		self.oscDisplay = None
		self._rgb = 0
		self._timer = 0
		self._current_nav_buttons = []
		self.flash_status = 1
		self._touched = 0
		self._last_pad_stream = [0 for i in range(0, 32)]
		self._shift_latching = LatchingShiftedBehaviour if SHIFT_LATCHING else ShiftedBehaviour
		self._skin = Skin(BaseColors)
		with self.component_guard():
			self._setup_OSC_layer()
			self._setup_monobridge()
			self._setup_controls()
			self._setup_background()
			self._define_sysex()
			self._setup_display()
			self._setup_autoarm()
			self._setup_mixer_control()
			self._setup_session_control()
			self._setup_transport_control()
			self._setup_device_control()
			self._setup_session_recording_component()
			self._setup_translations()
			self._setup_instrument()
			self._setup_mod()
			self._setup_modswitcher()
			self._setup_main_modes()
			self._setup_m4l_interface()
			self._on_device_changed.subject = self.song()
			self.set_feedback_channels(range(14, 15))
		self.log_message("<<<<<<<<<<<<<<<<<= Base log opened =>>>>>>>>>>>>>>>>>>>>>")
		self.schedule_message(3, self._check_connection)
	

	def set_appointed_device(self, device):
		self.song().appointed_device = device
	

	def set_feedback_channels(self, channels, *a, **k):
		super(Base, self).set_feedback_channels(channels, *a, **k)
	

	"""script initialization methods"""
	def _initialize_hardware(self):
		self._livid_settings.send('set_streaming_enabled', STREAMINGON)
		self._livid_settings.send('set_function_button_leds_linked', [1])
		self._livid_settings.send('set_capacitive_fader_note_output_enabled', [1])
		self._livid_settings.send('set_pad_pressure_output_type', ATON if AFTERTOUCH is True else ATOFF)
		self._send_midi((191, 122, 64))
		self._main_modes.selected_mode = 'Clips'
	

	def _check_connection(self):
		if not self._connected:
			#self._send_midi(QUERYSURFACE)
			self._livid_settings.query_surface()
			self.schedule_message(100, self._check_connection)
	

	def port_settings_changed(self):
		debug('port settings changed!')
		self._connected = False
		self._check_connection()
	

	def _setup_monobridge(self):
		self._monobridge = MonoBridgeElement(self, osc_display = self.oscDisplay)
		self._monobridge.name = 'MonoBridge'
	

	def pad_held(self):
		return (sum(self._last_pad_stream)>0)
	

	def _setup_controls(self):
		is_momentary = True
		self._fader = [MonoEncoderElement(MIDI_CC_TYPE, CHANNEL, BASE_TOUCHSTRIPS[index], Live.MidiMap.MapMode.absolute, 'Fader_' + str(index), index, self, mapping_feedback_delay = -1, monobridge = self._monobridge) for index in range(9)]
		self._fader_matrix = ButtonMatrixElement(name = 'FaderMatrix', rows = [self._fader[:8]])
		self._button = [MonoButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, BASE_BUTTONS[index], name = 'Button_' + str(index), script = self, skin = self._skin, monobridge = self._monobridge) for index in range(8)]
		self._pad = [BlockingMonoButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, BASE_PADS[index], name = 'Pad_' + str(index), script = self, skin = self._skin, monobridge = self._monobridge) for index in range(32)]
		self._pad_doublepress = [DoublePressElement(pad) for pad in self._pad]
		self._pad_CC = [MonoEncoderElement(MIDI_CC_TYPE, CHANNEL, BASE_PADS[index], Live.MidiMap.MapMode.absolute, 'Pad_CC_' + str(index), index, self, monobridge = self._monobridge) for index in range(32)]
		self._touchpad = [MonoButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, BASE_TOUCHPADS[index], name = 'TouchPad_' + str(index), script = self, resource_type = PrioritizedResource, skin = self._skin, monobridge = self._monobridge) for index in range(8)]
		self._touchpad_matrix = ButtonMatrixElement(name = 'TouchPadMatrix', rows = [self._touchpad],)
		self._touchpad_multi = MultiElement(self._touchpad[0], self._touchpad[1], self._touchpad[2], self._touchpad[3], self._touchpad[4], self._touchpad[5], self._touchpad[6], self._touchpad[7],)
		self._runner = [MonoButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, BASE_RUNNERS[index], name = 'Runner_' + str(index), script = self, skin = self._skin) for index in range(8)]
		self._runner_matrix = ButtonMatrixElement(name = 'RunnerMatrix', rows = [self._runner])
		self._stream_pads = [self._pad[index%8 + (abs((index/8)-3)*8)] for index in range(32)]
		self._mode_buttons = ButtonMatrixElement( name = 'mode_buttons' , rows = [self._button[0:4]])
		self._nav_buttons = ButtonMatrixElement( name = 'nav_buttons', rows = [self._button[4:8]] )
		self._base_grid = ButtonMatrixElement(name = 'BaseGrid', rows = [self._pad[(index*8):(index*8)+8] for index in range(4)] )
		self._base_grid_CC = ButtonMatrixElement(name = 'BaseGridCC', rows = [self._pad_CC[(index*8):(index*8)+8] for index in range(4)] )
		self._keys = ButtonMatrixElement(name = 'Keys', rows = [self._touchpad[0:8]])
		self._keys_display = ButtonMatrixElement(name = 'KeysDisplay', rows = [self._runner[0:8]])
		self._base_doublepress_grid = ButtonMatrixElement(name = 'doublepress_matrix', rows = [[self._pad_doublepress[column+(row*8)] for column in range(8)] for row in range(4)])
		self._drumpad_grid = ButtonMatrixElement(name = 'DrumPadGrid', rows = [self._pad[(index*8):(index*8)+4] for index in range(4)])

		self._up_button = self._nav_buttons[UDLR[0]]
		self._dn_button = self._nav_buttons[UDLR[1]]
		self._lt_button = self._nav_buttons[UDLR[2]]
		self._rt_button = self._nav_buttons[UDLR[3]]

		for control in self.controls:
			hasattr(control, 'report_descriptor') and control.report_descriptor('', True)

		#self._on_nav_button_value.subject = self._nav_buttons
	

	def _setup_background(self):
		self._background = BackgroundComponent(name = 'Background')
		self._background.layer = Layer(priority = 0, matrix = self._base_grid, matrix_CC = self._base_grid_CC, touchpads = self._touchpad_matrix, faders = self._fader_matrix, runners = self._runner_matrix)
	

	def _define_sysex(self):
		self._livid_settings = LividSettings(model = 12, control_surface = self)

		self.clips_layer_sysex = SendLividSysexMode(livid_settings = self._livid_settings, call = 'set_fader_led_colors', message = CLIPS_FADER_COLORS)
		self.sends_layer_sysex = SendLividSysexMode(livid_settings = self._livid_settings, call = 'set_fader_led_colors', message = SENDS_FADER_COLORS)
		self.device_layer_sysex = SendLividSysexMode(livid_settings = self._livid_settings, call = 'set_fader_led_colors', message = DEVICE_FADER_COLORS)
		self.user_layer_sysex = SendLividSysexMode(livid_settings = self._livid_settings, call = 'set_fader_led_colors', message = USER_FADER_COLORS)
		self.mod_layer_sysex = SendLividSysexMode(livid_settings = self._livid_settings, call = 'set_fader_led_colors', message = USER_FADER_COLORS)

		self.midi_mode_sysex = SendLividSysexMode(livid_settings = self._livid_settings, call = 'set_pad_output_type', message = USERBUTTONMODE if AFTERTOUCH else MIDIBUTTONMODE)
		self.user_mode_sysex = SendLividSysexMode(livid_settings = self._livid_settings, call = 'set_pad_output_type', message = USERBUTTONMODE)
		self.live_mode_sysex = SendLividSysexMode(livid_settings = self._livid_settings, call = 'set_pad_output_type', message = LIVEBUTTONMODE)
		self.splitvertical_mode_sysex = SendLividSysexMode(livid_settings = self._livid_settings, call = 'set_pad_output_type', message = SPLITVERTICALATON if AFTERTOUCH else SPLITVERTICAL)
		self.splithorizontal_mode_sysex = SendLividSysexMode(livid_settings = self._livid_settings, call = 'set_pad_output_type', message = SPLITHORIZONTALATON if AFTERTOUCH else SPLITHORIZONTAL)

		self.atoff_mode_sysex = SendLividSysexMode(livid_settings = self._livid_settings, call = 'set_pad_pressure_output_type', message = ATOFFBUTTONMODE)
		self.aton_mode_sysex = SendLividSysexMode(livid_settings = self._livid_settings, call = 'set_pad_pressure_output_type', message = ATONBUTTONMODE)
	

	def _setup_display(self):
		self._display = BasePhysicalDisplayElement(width_in_chars = 2)
		self._display.name = 'Display'
		self._display.set_message_parts(header = [176, 34,], tail = [])
		self._display.set_clear_all_message((176, 34, 127, 176, 35, 127))
		self._display.set_translation_table(_base_translations)
	
	
	def _setup_autoarm(self):
		self._auto_arm = AutoArmComponent(name='Auto_Arm')
		self._auto_arm.can_auto_arm_track = self._can_auto_arm_track
	

	def _setup_mixer_control(self):
		is_momentary = True
		self._num_tracks = (8)
		self._mixer = MixerComponent(num_tracks = 8, num_returns = 4, invert_mute_feedback = True, auto_name = True)
		self._mixer.name = 'Mixer'
		self._mixer.set_track_offset(0)
		self._mixer.master_strip().set_volume_control(self._fader[8])
		self._mixer.volume_layer = AddLayerMode(self._mixer, Layer(priority = 4, volume_controls = self._fader_matrix))
		self._mixer.select_layer = AddLayerMode(self._mixer, Layer(priority = 4, track_select_buttons = self._touchpad_matrix))
		selected_strip = self._mixer.selected_strip()
		selected_strip.set_invert_mute_feedback(True)
		self._mixer.selected_channel_controls_layer = AddLayerMode(selected_strip, Layer(priority = 9, arm_button = self._button[6], solo_button = self._button[5], mute_button = self._button[4], stop_button = self._button[7]))
		self._mixer.selected_sends_layer = AddLayerMode(selected_strip, Layer(priority = 4, send_controls = self._fader_matrix.submatrix[:4, :]))
		self._mixer.returns_layer = AddLayerMode(self._mixer, Layer(priority = 4, return_controls = self._fader_matrix.submatrix[4:, :]))
		self._mixer.channel_controls_layer = AddLayerMode(self._mixer, Layer(priority = 6, mute_buttons = self._base_grid.submatrix[:, :1],
																		solo_buttons = self._base_grid.submatrix[:, 1:2],
																		arm_buttons = self._base_grid.submatrix[:, 2:3],
																		stop_clip_buttons = self._base_grid.submatrix[:, 3:4]))
		self._mixer.navigation_layer = AddLayerMode(self._mixer, Layer(priority = 6, previous_track_button = self._button[6], next_track_button = self._button[7]))
		self.song().view.selected_track = self._mixer.channel_strip(0)._track 
		self._mixer.set_enabled(True)
	

	def _setup_session_control(self):
		self._session = BaseSessionComponent(8, 4, enable_skinning = True)
		self._session.name = "Session"
		self._session._enable_skinning()
		self._session.set_offsets(0, 0)	 
		self._scene = [None for index in range(4)]
		for row in range(4):
			self._scene[row] = self._session.scene(row)
			self._scene[row].name = 'Scene_' + str(row)
			for column in range(8):
				clip_slot = self._scene[row].clip_slot(column)
				clip_slot.name = str(column) + '_Clip_Slot_' + str(row)
				clip_slot._cs = self
		self._session.set_mixer(self._mixer)
		self._session.cliplaunch_layer = AddLayerMode(self._session, Layer(priority = 4, clip_launch_buttons = self._base_grid))
		self._session.overlay_cliplaunch_layer = AddLayerMode(self._session, Layer(priority = 9, clip_launch_buttons = self._base_grid.submatrix[:7, :], scene_launch_buttons = self._base_grid.submatrix[7:, :]))
		self._session.navigation_layer = AddLayerMode(self._session, Layer(priority = 6, scene_bank_up_button = self._button[4], scene_bank_down_button = self._button[5], track_bank_left_button = self._button[6], track_bank_right_button = self._button[7]))
		self.set_highlighting_session_component(self._session)
		self._session._do_show_highlight()
	

	def _setup_transport_control(self):
		self._transport = TransportComponent()
		self._transport.name = 'Transport'
		self._transport.overdub_layer = AddLayerMode(self._transport, Layer(priority = 5, overdub_button = self._button[4]))
	

	def _setup_device_control(self):
		self._device_selection_follows_track_selection = True 
		self._device = BaseDeviceComponent()
		self._device.name = 'Device_Component'
		self._device.parameters_layer = AddLayerMode(self._device, Layer(priority = 4, parameter_controls = self._fader_matrix.submatrix[:8][:]))
		self._device.nav_layer = AddLayerMode(self._device, Layer(priority = 5, bank_prev_button = self._button[6], bank_next_button = self._button[7]))
		self.set_device_component(self._device)
		self._device_navigator = DeviceNavigator(self._device, self._mixer, self)
		self._device_navigator.name = 'Device_Navigator'
		self._device_navigator._device_color_on = 'DeviceNavigator.DeviceNavOn'
		self._device_navigator._device_color_off = 'DeviceNavigator.DeviceNavOff'
		self._device_navigator._chain_color_on = 'DeviceNavigator.ChainNavOn'
		self._device_navigator._chain_color_off = 'DeviceNavigator.ChainNavOff'
		self._device_navigator._level_color_on = 'DeviceNavigator.LevelNavOn'
		self._device_navigator._level_color_off = 'DeviceNavigator.LevelNavOff'
		self._device_navigator.main_layer = AddLayerMode(self._device_navigator, Layer(priority = 6, prev_button = self._button[4], next_button = self._button[5]))
		self._device_navigator.alt_layer = AddLayerMode(self._device_navigator, Layer(priority = 6, prev_chain_button = self._button[4], next_chain_button = self._button[5], enter_button = self._button[7], exit_button = self._button[6]))
		self._device.device_name_data_source().set_update_callback(self._on_device_name_changed)
	

	def _setup_session_recording_component(self):
		self._clip_creator = ClipCreator()
		self._clip_creator.name = 'ClipCreator'
		self._recorder = BaseSessionRecordingComponent(self._clip_creator, ViewControlComponent())
		self._recorder.main_layer = LayerMode(self._recorder, Layer(priority = 5, new_button = self._button[5], record_button = self._button[6], length_button = self._button[7]))
		self._recorder.alt_layer = LayerMode(self._recorder, Layer(priority = 5, length_buttons = self._nav_buttons.submatrix[1:4][:]))
		self._recorder.set_enabled(True)
	

	def _setup_m4l_interface(self):
		self._m4l_interface = MonoM4LInterfaceComponent(controls=self.controls, component_guard=self.component_guard, priority = 10)
		self._m4l_interface.name = "M4LInterface"
		self.get_control_names = self._m4l_interface.get_control_names
		self.get_control = self._m4l_interface.get_control
		self.grab_control = self._m4l_interface.grab_control
		self.release_control = self._m4l_interface.release_control
	

	def _setup_translations(self):
		controls = []
		for button, _ in self._base_grid.iterbuttons():
			controls.append(button)
		for button, _ in self._base_grid_CC.iterbuttons():
			controls.append(button)
		for fader, _ in self._fader_matrix.iterbuttons():
			controls.append(fader)
		if CAP_BUTTON_TRANSLATIONS:
			for button, _ in self._touchpad_matrix.iterbuttons():
				controls.append(button)
		self._translations = BaseDisplayingTranslationComponent(controls, USER_OFFSET)
		self._translations.name = 'TranslationComponent'
		self._translations._channel = USER_OFFSET
		self._translations.layer = Layer(priority = 10, channel_selector_buttons = self._nav_buttons, display = self._display)
		self._translations.set_enabled(False)
	

	def _setup_mod(self):
		self.monomodular = get_monomodular(self)
		self.monomodular.name = 'monomodular_switcher'
		self.modhandler = BaseModHandler(script = self) #detect_mod = self._on_new_device_set)
		self.modhandler.name = 'ModHandler'
		self.modhandler.layer = Layer(priority = 6, base_grid = self._base_grid, 
													base_grid_CC = self._base_grid_CC,
													parameter_controls = self._fader_matrix,
													alt_button = self._button[6],
													lock_button = self._button[7],
													key_buttons = self._runner_matrix,)
		self.modhandler.alt_layer = AddLayerMode(self.modhandler, Layer(priority = 6,
													device_selector_matrix = self._touchpad_matrix,))
		self.modhandler.legacy_shift_layer = AddLayerMode(self.modhandler, Layer(priority = 6,
													channel_buttons = self._base_grid.submatrix[:6, :1],
													nav_matrix = self._base_grid.submatrix[6:8, :],))
		self.modhandler.shift_layer = AddLayerMode(self.modhandler, Layer(priority = 6,
													key_buttons = self._touchpad_matrix,
													background_buttons = self._runner_matrix))
		self.modhandler._device_selector._selection_layer = AddLayerMode(self.modhandler._device_selector, Layer(priority = 6,
													matrix = self._mode_buttons))
		self.modhandler.set_enabled(False)
	

	def _setup_instrument(self):
		self._grid_resolution = self.register_disconnectable(GridResolution())
		self._c_instance.playhead.enabled = True
		self._playhead_element = PlayheadElement(self._c_instance.playhead)

		self._playhead_element.reset()
		self._skin = make_default_skin()

		quantgrid = ButtonMatrixElement([self._base_grid._orig_buttons[2][4:8], self._base_grid._orig_buttons[3][4:7]])

		self._instrument = BaseMonoInstrumentComponent(self, self._skin, grid_resolution = self._grid_resolution, scalenames = SCALENAMES if SCALENAMES else None)
		self._instrument.name = 'InstrumentModes'
		self._instrument.layer = Layer(priority = 6, base_display = self._display)
		self._instrument.audioloop_layer = LayerMode(self._instrument, Layer(priority = 6, loop_selector_matrix = self._base_grid))
		self._instrument.octave_toggle = AddLayerMode(self._instrument, Layer(octave_enable_button = self._button[4]))
		self._instrument.keypad_shift_layer = AddLayerMode(self._instrument, Layer(priority = 6, 
									base_display = self._display,
									scale_up_button = self._touchpad[7], 
									scale_down_button = self._touchpad[6],
									offset_up_button = self._touchpad[5], 
									offset_down_button = self._touchpad[4],
									vertical_offset_up_button = self._touchpad[3],
									vertical_offset_down_button = self._touchpad[2],
									split_button = self._touchpad[0], 
									sequencer_button = self._touchpad[1]))
		self._instrument.drumpad_shift_layer = AddLayerMode(self._instrument, Layer(priority = 6, 
									base_display = self._display,
									scale_up_button = self._touchpad[7],
									scale_down_button = self._touchpad[6],
									drum_offset_up_button = self._touchpad[5], 
									drum_offset_down_button = self._touchpad[4],
									drumpad_mute_button = self._touchpad[3],
									drumpad_solo_button = self._touchpad[2],
									split_button = self._touchpad[0], 
									sequencer_button = self._touchpad[1]))
		self._instrument._keypad.main_layer = LayerMode(self._instrument._keypad, Layer(priority = 6, keypad_matrix = self._base_grid))
		self._instrument._keypad.sequencer_layer = LayerMode(self._instrument._keypad, Layer(priority = 6, playhead = self._playhead_element, keypad_matrix = self._base_grid.submatrix[:, 2:4], sequencer_matrix = self._base_grid.submatrix[:, :2]))
		self._instrument._keypad.split_layer = LayerMode(self._instrument._keypad, Layer(priority = 6, keypad_matrix = self._base_grid.submatrix[:, 2:4], split_matrix = self._base_grid.submatrix[:, :2]))
		self._instrument._keypad.sequencer_shift_layer = LayerMode(self._instrument._keypad, Layer(priority = 6, keypad_matrix = self._base_grid.submatrix[:, 2:4], loop_selector_matrix = self._base_grid.submatrix[:, :1], quantization_buttons = self._base_grid.submatrix[:7, 1:2], follow_button = self._pad[15]))
		self._instrument._drumpad.main_layer = LayerMode(self._instrument._drumpad, Layer(priority = 6, drumpad_matrix = self._base_grid))
		self._instrument._drumpad.sequencer_layer = LayerMode(self._instrument._drumpad, Layer(priority = 6, playhead = self._playhead_element, drumpad_matrix = self._base_grid.submatrix[:4, :], sequencer_matrix = self._base_grid.submatrix[4:8, :]))
		self._instrument._drumpad.split_layer = LayerMode(self._instrument._drumpad, Layer(priority = 6, drumpad_matrix = self._base_grid.submatrix[:4, :], split_matrix = self._base_grid.submatrix[4:8, :]))
		self._instrument._drumpad.sequencer_shift_layer = LayerMode(self._instrument._drumpad, Layer(priority = 6, drumpad_matrix = self._base_grid.submatrix[:4, :4], loop_selector_matrix = self._base_grid.submatrix[4:8, :2], quantization_buttons = quantgrid, follow_button = self._pad[31]))
		self._instrument.set_enabled(False)

		self._instrument._main_modes = ModesComponent(name = 'InstrumentModes')
		self._instrument._main_modes.add_mode('disabled', [])
		self._instrument._main_modes.add_mode('drumpad', [self._instrument._drumpad.main_layer, self.midi_mode_sysex])
		self._instrument._main_modes.add_mode('drumpad_split', [self._instrument._drumpad.split_layer, self.splitvertical_mode_sysex])
		self._instrument._main_modes.add_mode('drumpad_sequencer', [self._instrument._drumpad.sequencer_layer, self.splitvertical_mode_sysex])
		self._instrument._main_modes.add_mode('drumpad_shifted', [self._instrument._drumpad.main_layer, self._instrument.drumpad_shift_layer, self.midi_mode_sysex])
		self._instrument._main_modes.add_mode('drumpad_split_shifted', [self._instrument._drumpad.split_layer, self._instrument.drumpad_shift_layer])
		self._instrument._main_modes.add_mode('drumpad_sequencer_shifted', [self._instrument._drumpad.sequencer_shift_layer, self._instrument.drumpad_shift_layer, self.splitvertical_mode_sysex])
		self._instrument._main_modes.add_mode('keypad', [self._instrument._keypad.main_layer, self.midi_mode_sysex])
		self._instrument._main_modes.add_mode('keypad_split', [self._instrument._keypad.split_layer, self.splithorizontal_mode_sysex])
		self._instrument._main_modes.add_mode('keypad_sequencer', [self._instrument._keypad.sequencer_layer, self.splithorizontal_mode_sysex], )
		self._instrument._main_modes.add_mode('keypad_shifted', [self._instrument._keypad.main_layer, self._instrument.keypad_shift_layer, self.midi_mode_sysex])
		self._instrument._main_modes.add_mode('keypad_split_shifted', [self._instrument._keypad.split_layer, self._instrument.keypad_shift_layer])
		self._instrument._main_modes.add_mode('keypad_sequencer_shifted', [self._instrument._keypad.sequencer_shift_layer, self._instrument.keypad_shift_layer, self.splithorizontal_mode_sysex])
		self._instrument._main_modes.add_mode('audioloop', [self._instrument.audioloop_layer, self.live_mode_sysex])
		self._instrument.register_component(self._instrument._main_modes)
		self._instrument.set_enabled(False)
	

	def _setup_OSC_layer(self):
		self.oscDisplay = OSCDisplay(prefix = '/Live/0', model_name = 'Base', model = Base, outport = OSC_OUTPORT)
		self.oscDisplay.set_enabled(OSC_TRANSMIT)
	

	def _setup_modswitcher(self):
		self._modswitcher = BaseDisplayingModesComponent(name = 'ModSwitcher')
		self._modswitcher.add_mode('mod', [self.modhandler, self.user_mode_sysex], display_string = MODE_DATA['Mod'])
		self._modswitcher.add_mode('instrument', [self._instrument, self.device_layer_sysex])
		#self._modswitcher.selected_mode = 'instrument'
		self._modswitcher.set_enabled(False)
	

	def _setup_main_modes(self):
		for index in range(4):
			self._button[index]._last_reported_descriptor = ['MainModes.Clip', 'MainModes.Send', 'MainModes.Device', 'MainModes.User'][index]
		self._main_modes = BaseDisplayingModesComponent(name = 'MainModes')
		self._main_modes.add_mode('disabled', [self._background])
		self._main_modes.add_mode('Clips_shifted', [self._set_nav_colors, self._mixer.volume_layer, self._mixer.select_layer, self._mixer.channel_controls_layer, self.clips_layer_sysex, self.live_mode_sysex], groups = ['shifted'], behaviour = self._shift_latching(color = 'MainModes.Clip'), display_string = MODE_DATA['Clips_shifted'])
		self._main_modes.add_mode('Clips', [self._set_nav_colors, self._mixer.volume_layer, self._mixer.select_layer,  self._session.cliplaunch_layer, self._session.navigation_layer, self.clips_layer_sysex, self.live_mode_sysex, self.refresh_OSC ], behaviour = self._shift_latching(color = 'MainModes.Clip'), display_string = MODE_DATA['Clips'])
		self._main_modes.add_mode('Sends_shifted', [self._set_fixed_length_colors, self.sends_layer_sysex, self._instrument, self._recorder.alt_layer, self._instrument.octave_toggle, tuple([self._send_instrument_shifted, self._send_instrument_unshifted]),], groups = ['shifted'], behaviour = self._shift_latching(color = 'MainModes.Sends'), display_string = MODE_DATA['Sends_shifted'])
		self._main_modes.add_mode('Sends', [self._set_clip_creator_colors, self.sends_layer_sysex, self._instrument, self._mixer.select_layer, self._mixer.selected_sends_layer, self._mixer.returns_layer,  self._transport.overdub_layer, self._recorder.main_layer,], behaviour = self._shift_latching(color = 'MainModes.Sends'), display_string = MODE_DATA['Sends'])
		self._main_modes.add_mode('Device_shifted', [self._set_device_shift_nav_colors, self.device_layer_sysex, self._modswitcher, tuple([self._send_instrument_shifted, self._send_instrument_unshifted]), self._device, self._device.parameters_layer, self._device_navigator.alt_layer,  ], groups = ['shifted'], behaviour = self._shift_latching(color = 'MainModes.Device'), display_string = MODE_DATA['Device_shifted'])
		self._main_modes.add_mode('Device', [self._set_device_nav_colors, self.device_layer_sysex, self._modswitcher, self._mixer.select_layer, self._mixer.select_layer, self._device, self._device.parameters_layer, self._device.nav_layer, self._device_navigator.main_layer,], behaviour = self._shift_latching(color = 'MainModes.Device'), display_string = MODE_DATA['Device'])
		self._main_modes.add_mode('User_shifted', [self._set_user_page_colors, self._translations, self._mixer.select_layer, self.user_layer_sysex, self.user_mode_sysex ], groups = ['shifted'], behaviour = self._shift_latching(color = 'MainModes.User'), display_string = MODE_DATA['User'])
		self._main_modes.add_mode('User', [self._set_user_page_colors, self._translations, self._mixer.select_layer, self.user_layer_sysex, self.user_mode_sysex], behaviour = self._shift_latching(color = 'MainModes.User'), display_string = MODE_DATA['User'])
		self._main_modes.add_mode('Select', [self.modhandler._device_selector._selection_layer, self._mixer.select_layer, self._mixer.volume_layer, self._mixer.selected_channel_controls_layer, self._session.overlay_cliplaunch_layer, self.clips_layer_sysex], behaviour = DelayedExcludingMomentaryBehaviour(excluded_groups = ['shifted']), display_string = MODE_DATA['Select'])
		self._main_modes.layer = Layer(priority = 4, Clips_button=self._button[0], Sends_button=self._button[1], Device_button=self._button[2], User_button=self._button[3], Select_button=self._touchpad_multi, display = self._display)
		self._main_modes.selected_mode = 'disabled'
	

	def _send_fader_colors(self):
		mode = self._main_modes.selected_mode
		if mode.startswith('Sends'):
			self.sends_layer_sysex.enter_mode()
		elif mode.startswith('Device'):
			self.device_layer_sysex.enter_mode()
	

	def _send_instrument_shifted(self):
		self._instrument.is_enabled() and self._instrument._on_shift_value(1)
		self.modhandler.is_enabled() and self.modhandler._shift_value(1)
	

	def _send_instrument_unshifted(self):
		self._instrument.is_enabled() and self._instrument._on_shift_value(0)
		self.modhandler.is_enabled() and self.modhandler._shift_value(0)
	

	def _set_nav_colors(self):
		for button in self._button[4:8]:
			button.set_on_off_values('Session.NavigationButtonOn', 'DefaultButton.Off')
	

	def _set_clip_creator_colors(self):
		self._button[4].set_on_off_values('Transport.OverdubOn', 'Transport.OverdubOff')
		self._button[5].set_on_off_values('Recorder.NewOn', 'Recorder.NewOff')
		self._button[6].set_on_off_values('Recorder.RecordOn', 'Recorder.RecordOff')
		self._button[7].set_on_off_values('Recorder.FixedOn', 'Recorder.FixedOff')
	

	def _set_fixed_length_colors(self):
		self._button[4].set_on_off_values('Sequencer.OctaveOn', 'Sequencer.OctaveOff')
		self._button[5].set_on_off_values('Recorder.FixedAssigned', 'Recorder.FixedNotAssigned')
		self._button[6].set_on_off_values('Recorder.FixedAssigned', 'Recorder.FixedNotAssigned')
		self._button[7].set_on_off_values('Recorder.FixedAssigned', 'Recorder.FixedNotAssigned')
	

	def _set_device_nav_colors(self):
		self._button[4].set_on_off_values('Device.NavOn', 'Device.NavOff')
		self._button[5].set_on_off_values('Device.NavOn', 'Device.NavOff')
		self._button[6].set_on_off_values('Device.BankOn', 'Device.BankOff')
		self._button[7].set_on_off_values('Device.BankOn', 'Device.BankOff')
	

	def _set_device_shift_nav_colors(self):
		self._button[4].set_on_off_values('Device.ChainNavOn', 'Device.ChainNavOff')
		self._button[5].set_on_off_values('Device.ChainNavOn', 'Device.ChainNavOff')
		self._button[6].set_on_off_values('Device.ContainNavOn', 'Device.ContainNavOff')
		self._button[7].set_on_off_values('Device.ContainNavOn', 'Device.ContainNavOff')
	

	def _set_user_page_colors(self):
		for button in self._button[4:8]:
			button.set_on_off_values('DefaultButton.On', 'DefaultButton.Off')
	

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
	

	def _register_pad_pressed(self, bytes):
		assert(len(bytes) is 8)
		decoded = []
		for i in range(0, 8):
			bin = bytes[i]
			for index in range(0, 4):
				decoded.append(bin & 1)
				bin = bin>>1
		self._last_pad_stream = decoded
		for index in range(len(decoded)):
			button = self._stream_pads[index]
			value = decoded[index]
			if button.display_press and (not value is button._last_flash):
				if value:
					button.set_light('MonoInstrument.PressFlash')
				else:
					button.set_light(button.scale_color)
				button._last_flash = value
	

	@subject_slot('value')
	def _on_nav_button_value(self, value, x, y, is_momentary):
		button = self._nav_buttons.get_button(x, y)
		if button in self._current_nav_buttons:
			if value > 0:
				self._send_midi((176, 35, DIRS[self._current_nav_buttons.index(button)]))
			else:
				self._display_mode()
	

	def update_display(self):
		super(Base, self).update_display()
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
			self.oscDisplay.sendOSC('glob/device', str(self.generate_strip_string(name)))
	

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
		self._livid_settings.send('set_streaming_enabled', STREAMINGOFF)
		self.log_message("--------------= Base log closed =--------------")
		super(Base, self).disconnect()
		#rebuild_sys()
	

	def _can_auto_arm_track(self, track):
		routing = track.current_input_routing
		return routing == 'Ext: All Ins' or routing == 'All Ins' or routing.startswith('Base Input')
		#self._main_modes.selected_mode in ['Sends', 'Device'] and
	

	@subject_slot('appointed_device')
	def _on_device_changed(self):
		self.schedule_message(1, self._update_modswitcher)
		#pass
	

	def _on_selected_track_changed(self):
		super(Base, self)._on_selected_track_changed()
		self.schedule_message(1, self._update_modswitcher)
	

	def _update_modswitcher(self):
		debug('update modswitcher', self.modhandler.active_mod())
		if self.modhandler.active_mod():
			self._modswitcher.selected_mode = 'mod'
		else:
			self._modswitcher.selected_mode = 'instrument'
	

	def reset_controlled_track(self, track = None, *a):
		if not track:
			track = self.song().view.selected_track
		self.set_controlled_track(track)
	

	def set_controlled_track(self, track = None, *a):
		dtrack = track.name if track and hasattr(track, 'name') else track
		debug('set_controlled_track:', dtrack)
		if isinstance(track, Live.Track.Track):
			super(Base, self).set_controlled_track(track)
		else:
			self.release_controlled_track()
	

	def restart_monomodular(self):
		#self.log_message('restart monomodular')
		self.modhandler.disconnect()
		with self.component_guard():
			self._setup_mod()
	

	def send_fader_color(self, num, value):
		self._send_midi((191, num+10, value))
	

	"""some cheap overrides"""
	def set_highlighting_session_component(self, session_component):
		self._highlighting_session_component = session_component
		if not session_component is None:
			self._highlighting_session_component.set_highlighting_callback(self._set_session_highlight)
	

	def handle_sysex(self, midi_bytes):
		#debug('sysex: ', str(midi_bytes))
		if len(midi_bytes) > 14:
			if midi_bytes[:6] == tuple([240, 0, 1, 97, 12, 64]):
				self._register_pad_pressed(midi_bytes[6:14])
			elif midi_bytes[:6] == tuple([240, 0, 1, 97, 17, 64]):
				self._register_pad_pressed(midi_bytes[6:14])
			elif midi_bytes[3:10] == tuple([6, 2, 0, 1, 97, 1, 0]):
				if not self._connected:
					self._connected = True
					self._livid_settings.set_model(midi_bytes[11])
					self._initialize_hardware()
	

	def display_message(self, message, *a, **k):
		debug('display_message', message)
		self._display.display_message(message)
	

	def refresh_OSC(self):
		if OSC_TRANSMIT:
			for control in self.controls:
				if isinstance(control, MonoEncoderElement):
					control.forward_parameter_value()
				elif isinstance(control, MonoButtonElement):
					control.report_descriptor(control._last_reported_descriptor, True)
			for index in range(4):
				self._button[index].report_descriptor(['MainModes.Clip', 'MainModes.Send', 'MainModes.Device', 'MainModes.User'][index], True)
			self._on_device_name_changed()
			self._on_device_bank_changed()
			self._on_device_chain_changed()
			
	

#	a