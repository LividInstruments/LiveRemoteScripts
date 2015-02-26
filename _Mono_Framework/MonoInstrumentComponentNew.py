"""
MonoInstrumentComponent.py

Created by amounra on 2014-07-18.
Copyright (c) 2014 __aumhaa__. All rights reserved.
"""

import Live
from itertools import imap, chain, starmap, ifilter

from _Framework.ControlSurface import *
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.CompoundComponent import CompoundComponent
from _Framework.ModeSelectorComponent import ModeSelectorComponent
from _Framework.SubjectSlot import subject_slot, subject_slot_group
from _Framework.ButtonElement import ButtonElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.DisplayDataSource import DisplayDataSource
from _Framework.ModesComponent import DisplayingModesComponent, ModesComponent
from _Framework.Util import forward_property, find_if, first, in_range, product
from _Framework.SessionComponent import SessionComponent
from _Framework.ClipCreator import ClipCreator
from _Framework.ModesComponent import AddLayerMode, LayerMode, MultiEntryMode, ModesComponent, SetAttributeMode, ModeButtonBehaviour, CancellableBehaviour, AlternativeBehaviour, ReenterBehaviour, DynamicBehaviourMixin, ExcludingBehaviourMixin, ImmediateBehaviour, LatchingBehaviour, ModeButtonBehaviour
from _Framework.Layer import Layer

from Push.SessionRecordingComponent import *
from Push.ViewControlComponent import ViewControlComponent
#from Push.DrumGroupComponent import DrumGroupComponent
from Push.StepSeqComponent import StepSeqComponent, DrumGroupFinderComponent
from Push.GridResolution import GridResolution
from Push.ConfigurableButtonElement import ConfigurableButtonElement
from Push.LoopSelectorComponent import LoopSelectorComponent
from Push.Actions import CreateInstrumentTrackComponent, CreateDefaultTrackComponent, CaptureAndInsertSceneComponent, DuplicateDetailClipComponent, DuplicateLoopComponent, SelectComponent, DeleteComponent, DeleteSelectedClipComponent, DeleteSelectedSceneComponent, CreateDeviceComponent
from Push.SkinDefault import make_default_skin

from _Mono_Framework.OriginalDrumGroupComponent import DrumGroupComponent
from _Mono_Framework.Debug import *

debug = initialize_debug()

INITIAL_SCROLLING_DELAY = 5
INTERVAL_SCROLLING_DELAY = 1

DISPLAY_NAMES = ['SplitMode', 'Vertical Offset', 'Scale Type', 'Root Note']

_NOTENAMES = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
NOTENAMES = [(_NOTENAMES[index%12] + ' ' + str(int(index/12))) for index in range(128)]
SCALENAMES = None
SCALEABBREVS = None

#from Map import *

CHANNELS = ['Ch. 2', 'Ch. 3', 'Ch. 4', 'Ch. 5', 'Ch. 6', 'Ch. 7', 'Ch. 8', 'Ch. 9', 'Ch. 10', 'Ch. 11', 'Ch. 12', 'Ch. 13', 'Ch. 14']
DEFAULT_MIDI_ASSIGNMENTS = {'mode':'chromatic', 'offset':36, 'vertoffset':12, 'scale':'Chromatic', 'drumoffset':0, 'split':False, 'sequencer':False}

"""The scale modes and drumpads use the following note maps"""
DRUMNOTES = [12, 13, 14, 15, 28, 29, 30, 31, 8, 9, 10, 11, 24, 25, 26, 27, 4, 5, 6, 7, 20, 21, 22, 23, 0, 1, 2, 3, 16, 17, 18, 19]
WHITEKEYS = [0, 2, 4, 5, 7, 9, 11, 12]
KEYCOLORS = ['MonoInstrument.Keys.BlackValue', 'MonoInstrument.Keys.WhiteValue', 'MonoInstrument.Keys.RootBlackValue', 'MonoInstrument.Keys.RootWhiteValue']
DRUMCOLORS = ['MonoInstrument.Drums.EvenValue', 'MonoInstrument.Drums.OddValue']

"""These are the scales we have available.  You can freely add your own scales to this """
SCALES = 	{'Mod':[0,1,2,3,4,5,6,7,8,9,10,11],
			'Session':[0,1,2,3,4,5,6,7,8,9,10,11],
			'Keys':[0,2,4,5,7,9,11,12,1,3,3,6,8,10,10,13],
			'Auto':[0,1,2,3,4,5,6,7,8,9,10,11],
			'Chromatic':[0,1,2,3,4,5,6,7,8,9,10,11],
			'DrumRack':[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],
			'DrumPad':[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],
			'Major':[0,2,4,5,7,9,11],
			'Minor':[0,2,3,5,7,8,10],
			'Dorian':[0,2,3,5,7,9,10],
			'Mixolydian':[0,2,4,5,7,9,10],
			'Lydian':[0,2,4,6,7,9,11],
			'Phrygian':[0,1,3,5,7,8,10],
			'Locrian':[0,1,3,4,7,8,10],
			'Diminished':[0,1,3,4,6,7,9,10],
			'Whole-half':[0,2,3,5,6,8,9,11],
			'Whole_Tone':[0,2,4,6,8,10],
			'Minor_Blues':[0,3,5,6,7,10],
			'Minor_Pentatonic':[0,3,5,7,10],
			'Major_Pentatonic':[0,2,4,7,9],
			'Harmonic_Minor':[0,2,3,5,7,8,11],
			'Melodic_Minor':[0,2,3,5,7,9,11],
			'Dominant_Sus':[0,2,5,7,9,10],
			'Super_Locrian':[0,1,3,4,6,8,10],
			'Neopolitan_Minor':[0,1,3,5,7,8,11],
			'Neopolitan_Major':[0,1,3,5,7,9,11],
			'Enigmatic_Minor':[0,1,3,6,7,10,11],
			'Enigmatic':[0,1,4,6,8,10,11],
			'Composite':[0,1,4,6,7,8,11],
			'Bebop_Locrian':[0,2,3,5,6,8,10,11],
			'Bebop_Dominant':[0,2,4,5,7,9,10,11],
			'Bebop_Major':[0,2,4,5,7,8,9,11],
			'Bhairav':[0,1,4,5,7,8,11],
			'Hungarian_Minor':[0,2,3,6,7,8,11],
			'Minor_Gypsy':[0,1,4,5,7,8,10],
			'Persian':[0,1,4,5,6,8,11],
			'Hirojoshi':[0,2,3,7,8],
			'In-Sen':[0,1,5,7,10],
			'Iwato':[0,1,5,6,10],
			'Kumoi':[0,2,3,7,9],
			'Pelog':[0,1,3,4,7,8],
			'Spanish':[0,1,3,4,5,6,8,10]
			}

SCALEABBREVS = {'Auto':'-A','Keys':'-K','Chromatic':'12','DrumPad':'-D','DrumRack':'D-','Major':'M-','Minor':'m-','Dorian':'II','Mixolydian':'V',
			'Lydian':'IV','Phrygian':'IH','Locrian':'VH','Diminished':'d-','Whole-half':'Wh','Whole_Tone':'WT','Minor_Blues':'mB',
			'Minor_Pentatonic':'mP','Major_Pentatonic':'MP','Harmonic_Minor':'mH','Melodic_Minor':'mM','Dominant_Sus':'D+','Super_Locrian':'SL',
			'Neopolitan_Minor':'mN','Neopolitan_Major':'MN','Enigmatic_Minor':'mE','Enigmatic':'ME','Composite':'Cp','Bebop_Locrian':'lB',
			'Bebop_Dominant':'DB','Bebop_Major':'MB','Bhairav':'Bv','Hungarian_Minor':'mH','Minor_Gypsy':'mG','Persian':'Pr',
			'Hirojoshi':'Hr','In-Sen':'IS','Iwato':'Iw','Kumoi':'Km','Pelog':'Pg','Spanish':'Sp'}


"""Any scale names in this array will automatically use SplitMode when chosen, regardless of the SplitSwitch for the individual MIDI Channel"""
SPLIT_SCALES = []

"""This is the default scale used by Auto when something other than a drumrack is detected for the selected track"""
DEFAULT_AUTO_SCALE = 'Major'

"""This is the default Vertical Offset for any scale other than DrumPad """
DEFAULT_VERTOFFSET = 4

"""This is the default NoteOffset, aka RootNote, used for scales other than DrumPad"""
DEFAULT_OFFSET = 48

"""This is the default NoteOffset, aka RootNote, used for the DrumPad scale;  it is a multiple of 4, so an offset of 4 is actually a RootNote of 16"""
DEFAULT_DRUMOFFSET = 9

"""This is the default Scale used for all MIDI Channels"""
DEFAULT_SCALE = 'Auto'

"""This is the default SplitMode used for all MIDI Channels"""
DEFAULT_SPLIT = False


if SCALENAMES is None:
	SCALENAMES = [scale for scale in sorted(SCALES.iterkeys())]

if SCALEABBREVS is None:
	SCALEABBREVS = []

"""It is possible to create a custom list of scales to be used by the script.  For instance, the list below would include major, minor, auto, drumpad, and chromatic scales, in that order."""
#SCALENAMES = ['Keys', 'Major', 'Minor', 'Auto', 'DrumPad', 'Chromatic']

OFFSET_SHIFT_IS_MOMENTARY = True


def song():
	return Live.Application.get_application().get_document()


def detect_instrument_type(track):
	scale = DEFAULT_AUTO_SCALE
	for device in track.devices:
		if isinstance(device, Live.Device.Device):
			#debug('device: ' + str(device.class_name))
			if device.class_name == 'DrumGroupDevice':
				scale = 'DrumPad'
				#self._step_sequencer.set_drum_group_device(device)
				break
	return scale
	


def make_pad_translations(chan):
	return tuple((x%4, int(x/4), x+16, chan) for x in range(16))


def reset_matrix(matrix):
	if matrix:
		for button, (x, y) in matrix.iterbuttons():
			if button:
				button.descriptor = None
				button.display_press = False
				button._force_forwarding = False
				button.set_force_next_value()
				button.use_default_message()
				button.set_enabled(True)


def new_reset_matrix(matrix):
	if matrix:
		for element in matrix:
			button = element._control_element
			if button:
				button.descriptor = None
				button.display_press = False
				button._force_forwarding = False
				button.set_force_next_value()
				button.use_default_message()
				button.set_enabled(True)

def _add_to_mode(mode, add):
	return mode + add



class CancellableBehaviourWithRelease(CancellableBehaviour):


	def release_delayed(self, component, mode):
		component.pop_mode(mode)
	

	def update_button(self, component, mode, selected_mode):
		button = component.get_mode_button(mode)
		groups = component.get_mode_groups(mode)
		selected_groups = component.get_mode_groups(selected_mode)
		value = (mode == selected_mode or bool(groups & selected_groups))*32 or 1
		button.send_value(value, True)
	


class ShiftCancellableBehaviourWithRelease(CancellableBehaviour):


	def release_delayed(self, component, mode):
		component.pop_mode(mode)
	

	def update_button(self, component, mode, selected_mode):
		pass
	


class SplitModeSelector(ModeSelectorComponent):


	def __init__(self, callback):
		super(SplitModeSelector, self).__init__()
		self._on_value = 127
		self._report_mode = callback
		self._modes_buttons = []
		self._set_protected_mode_index(0)
	

	def number_of_modes(self):
		return 2
	

	def set_mode_toggle(self, button):
		debug('setting mode toggle...')
		if not self._mode_toggle is None:
			self._mode_toggle.descriptor = None
		self._mode_toggle = button
		if not self._mode_toggle is None:
			self._mode_toggle.descriptor = 'SplitMode'
		self._toggle_value.subject = button
		self.update()
	

	def _mode_value(self, value, sender):
		if self._is_enabled:
			super(SplitModeSelector, self)._mode_value(value, sender)
			self._report_mode(self._mode_index)
	

	@subject_slot('value')
	def _toggle_value(self, value):
		if self._is_enabled and value:
			super(SplitModeSelector, self)._toggle_value(value)
			self._report_mode(self._mode_index)
	

	def update(self):
		if self._is_enabled:
			if len(self._modes_buttons) > 0:
				for index in range(len(self._modes_buttons)):
					if self._mode_index == index:
						self._modes_buttons[index].set_light(self._on_value)
					else:
						self._modes_buttons[index].turn_off()
			if not self._toggle_value.subject is None:
				if self._mode_index > 0:
					self._toggle_value.subject.set_light(self._on_value)
				else:
					self._toggle_value.subject.turn_off()
	


class ScrollingOffsetComponent(ControlSurfaceComponent):
	__module__ = __name__
	__doc__ = ' Class for handling held buttons for continued value changes '


	def __init__(self, callback):
		super(ScrollingOffsetComponent, self).__init__()
		self._report_change = callback
		self._offset = 0
		self._maximum = 127
		self._minimum = 0
		self._shifted = False
		self._shifted_value = 11
		self._scroll_up_ticks_delay = -1
		self._scroll_down_ticks_delay = -1
		self._scroll_octave_up_ticks_delay = -1
		self._scroll_octave_down_ticks_delay = -1	
		self._shift_is_momentary = True
		self._on_value = 127
		self._register_timer_callback(self._on_timer)
		#self._tasks.add(self._on_timer)
	

	def disconnect(self):
		self._scroll_up_value.subject = None
		self._scroll_down_value.subject = None
		self._scroll_octave_up_value.subject = None
		self._scroll_octave_down_value.subject = None
		super(ScrollingOffsetComponent, self).disconnect()
	

	def on_enabled_changed(self):
		self._scroll_up_ticks_delay = -1
		self._scroll_down_ticks_delay = -1
		self._scroll_octave_up_ticks_delay = -1
		self._scroll_octave_down_ticks_delay = -1
		self.update()
	

	def set_offset_change_buttons(self, up_button, down_button):
		assert ((up_button == None) or isinstance(up_button, ButtonElement))
		assert ((down_button == None) or isinstance(down_button, ButtonElement))
		self.set_up_button(up_button)
		self.set_down_button(down_button)
	

	def set_up_button(self, button):
		self._scroll_up_value.subject = button
		self.update()
	

	def set_down_button(self, button):
		self._scroll_down_value.subject = button
		self.update()
	

	def set_octave_up_button(self, button):
		self._scroll_octave_up_value.subject = button
		self.update()
	

	def set_octave_down_button(self, button):
		self._scroll_octave_down_value.subject = button
		self.update()
	

	def set_shift_button(self, shift_button):
		self._shift_value.subject = shift_button
		self.update()
	

	@subject_slot('value')
	def _scroll_up_value(self, value):
		if self.is_enabled():
			button_is_momentary = True
			if self._scroll_up_value.subject:
				button_is_momentary = self._scroll_up_value.subject.is_momentary()
			if button_is_momentary:
				if (value != 0):
					self._scroll_up_ticks_delay = INITIAL_SCROLLING_DELAY
				else:
					self._scroll_up_ticks_delay = -1
			if ((not self._is_scrolling()) and ((value is not 0) or (not button_is_momentary))):
				self._offset = max(self._minimum, min(self._maximum, self._offset + (1 + (self._shifted * (self._shifted_value-1)))))
				self.update()
				self._report_change(self._offset)
	

	@subject_slot('value')
	def _scroll_down_value(self, value):
		if self.is_enabled():
			button_is_momentary = True
			if self._scroll_down_value.subject:
				button_is_momentary = self._scroll_down_value.subject.is_momentary()
			if button_is_momentary:
				if (value != 0):
					self._scroll_down_ticks_delay = INITIAL_SCROLLING_DELAY
				else:
					self._scroll_down_ticks_delay = -1
			if ((not self._is_scrolling()) and ((value is not 0) or (not button_is_momentary))):
				self._offset = max(self._minimum, min(self._maximum, self._offset - (1 + (self._shifted * (self._shifted_value-1)))))
				self.update()
				self._report_change(self._offset)
	

	@subject_slot('value')
	def _scroll_octave_up_value(self, value):
		if self.is_enabled():
			button_is_momentary = True
			if self._scroll_octave_up_value.subject:
				button_is_momentary = self._scroll_octave_up_value.subject.is_momentary()
			if button_is_momentary:
				if (value != 0):
					self._scroll_octave_up_ticks_delay = INITIAL_SCROLLING_DELAY
				else:
					self._scroll_octave_up_ticks_delay = -1
			if ((not self._is_scrolling()) and ((value is not 0) or (not button_is_momentary))):
				self._offset = max(self._minimum, min(self._maximum, self._offset +  self._shifted_value))
				self.update()
				self._report_change(self._offset)
	

	@subject_slot('value')
	def _scroll_octave_down_value(self, value):
		if self.is_enabled():
			button_is_momentary = True
			if self._scroll_octave_down_value.subject:
				button_is_momentary = self._scroll_octave_down_value.subject.is_momentary()
			if button_is_momentary:
				if (value != 0):
					self._scroll_octave_down_ticks_delay = INITIAL_SCROLLING_DELAY
				else:
					self._scroll_octave_down_ticks_delay = -1
			if ((not self._is_scrolling()) and ((value is not 0) or (not button_is_momentary))):
				self._offset = max(self._minimum, min(self._maximum, self._offset - self._shifted_value))
				self.update()
				self._report_change(self._offset)
	

	@subject_slot('value')
	def _shift_value(self, value):
		if self._shift_is_momentary:
			self._shifted = (value > 0)
			self.update()
		else:
			if value > 0:
				self._shifted = not self._shifted
				self.update()
		
	

	def _on_timer(self):
		if self.is_enabled():
			scroll_delays = [self._scroll_up_ticks_delay,
							self._scroll_down_ticks_delay, 
							self._scroll_octave_up_ticks_delay,
							self._scroll_octave_down_ticks_delay]
			if (scroll_delays.count(-1) < 4):
				offset_increment = 0
				if (self._scroll_down_ticks_delay > -1):
					if self._is_scrolling():
						offset_increment -= 1
						self._scroll_down_ticks_delay = INTERVAL_SCROLLING_DELAY
					self._scroll_down_ticks_delay -= 1
				if (self._scroll_up_ticks_delay > -1):
					if self._is_scrolling():
						offset_increment += 1
						self._scroll_up_ticks_delay = INTERVAL_SCROLLING_DELAY
					self._scroll_up_ticks_delay -= 1
				if (self._scroll_octave_down_ticks_delay > -1):
					if self._is_scrolling():
						offset_increment -= self._shifted_value
						self._scroll_octave_down_ticks_delay = INTERVAL_SCROLLING_DELAY
					self._scroll_octave_down_ticks_delay -= 1
				if (self._scroll_octave_up_ticks_delay > -1):
					if self._is_scrolling():
						offset_increment += self._shifted_value
						self._scroll_octave_up_ticks_delay = INTERVAL_SCROLLING_DELAY
					self._scroll_octave_up_ticks_delay -= 1
				new_offset = max(self._minimum, min(self._maximum, self._offset + offset_increment))
				if new_offset != self._offset:
					self._offset =  new_offset
					self.update()
					self._report_change(self._offset)
	

	def _is_scrolling(self):
		return (0 in (self._scroll_up_ticks_delay,
					  self._scroll_down_ticks_delay,
					  self._scroll_octave_up_ticks_delay,
					  self._scroll_octave_down_ticks_delay))
	

	def set_offset(self, value):
		self._offset = value
		self._report_change(value)
	

	def update(self):
		if self._scroll_down_value.subject:
			if self._offset > self._minimum:
				self._scroll_down_value.subject.set_light(self._on_value)
			else:
				self._scroll_down_value.subject.turn_off()
		if self._scroll_up_value.subject != None:
			if self._offset < self._maximum:
				self._scroll_up_value.subject.set_light(self._on_value)
			else:
				self._scroll_up_value.subject.turn_off()
		if self._scroll_octave_down_value.subject:
			if self._offset > self._minimum:
				self._scroll_octave_down_value.subject.set_light(self._on_value)
			else:
				self._scroll_octave_down_value.subject.turn_off()
		if self._scroll_octave_up_value.subject != None:
			if self._offset < self._maximum:
				self._scroll_octave_up_value.subject.set_light(self._on_value)
			else:
				self._scroll_octave_up_value.subject.turn_off()
		if self._shift_value.subject:
			if self._shifted:
				self._shift_value.subject.turn_on()
			else:
				self._shift_value.subject.turn_off()
	


class ScaleSessionComponent(SessionComponent):


	def __init__(self, num_tracks, num_scenes, script, *a, **k):
		super(ScaleSessionComponent, self).__init__(num_tracks, num_scenes, *a, **k)
		self._shifted = False
		self._script = script
	

	def _bank_up_value(self, value):
		assert (value in range(128))
		assert (self._bank_up_button != None)
		if self.is_enabled():
			button_is_momentary = self._bank_up_button.is_momentary()
			if button_is_momentary:
				if (value != 0):
					self._scroll_up_ticks_delay = INITIAL_SCROLLING_DELAY
				else:
					self._scroll_up_ticks_delay = -1
			if ((not self._is_scrolling()) and ((value is not 0) or (not button_is_momentary))):
				self.set_offsets(self._track_offset, (self._scene_offset + (1+(self._shifted*3))))
	

	def _bank_down_value(self, value):
		assert (value in range(128))
		assert (self._bank_down_button != None)
		if self.is_enabled():
			button_is_momentary = self._bank_down_button.is_momentary()
			if button_is_momentary:
				if (value != 0):
					self._scroll_down_ticks_delay = INITIAL_SCROLLING_DELAY
				else:
					self._scroll_down_ticks_delay = -1
			if ((not self._is_scrolling()) and ((value is not 0) or (not button_is_momentary))):
				self.set_offsets(self._track_offset, max(0, self._scene_offset - (1+(self._shifted*3))))
	

	def _bank_right_value(self, value):
		assert (value in range(128))
		assert (self._bank_right_button != None)
		if self.is_enabled():
			button_is_momentary = self._bank_right_button.is_momentary()
			if button_is_momentary:
				if (value != 0):
					self._scroll_right_ticks_delay = INITIAL_SCROLLING_DELAY
				else:
					self._scroll_right_ticks_delay = -1
			if ((not self._is_scrolling()) and ((value is not 0) or (not button_is_momentary))):
				self.set_offsets((self._track_offset + (1+(self._shifted*7))), self._scene_offset)
	

	def _bank_left_value(self, value):
		assert isinstance(value, int)
		assert (self._bank_left_button != None)
		if self.is_enabled():
			button_is_momentary = self._bank_left_button.is_momentary()
			if button_is_momentary:
				if (value != 0):
					self._scroll_left_ticks_delay = INITIAL_SCROLLING_DELAY
				else:
					self._scroll_left_ticks_delay = -1
			if ((not self._is_scrolling()) and ((value is not 0) or (not button_is_momentary))):
				self.set_offsets(max(0, (self._track_offset - (1+(self._shifted*7)))), self._scene_offset)
	

	def set_clip_launch_buttons(self, buttons):
		if buttons:
			width = buttons.width()
			height = buttons.height()
			for button, (x, y) in buttons.iterbuttons():
				if button:
					button.display_press = False
					#button.press_flash(0, True)
					button.set_off_value(0)
					button.clear_send_cache()
					button.turn_off()
					index = x + (y*width)
					scene = self.scene(index)
					slot = scene.clip_slot(0)
					slot.set_launch_button(button)


		else:
			for x, y in product(xrange(self._num_tracks), xrange(self._num_scenes)):
				scene = self.scene(y)
				slot = scene.clip_slot(x)
				slot.set_launch_button(None)
		self._reassign_tracks()
		self._reassign_scenes()
		self.update()
	

	def update_current_track(self):
		track = self.song().view.selected_track
		track_list = []
		for t in self.song().tracks:
			track_list.append(t)
		if track in track_list:
			self._track_offset = track_list.index(track)
		#debug('new track offset: ' + str(self._selected_session._track_offset))
		self._reassign_tracks()
		self._reassign_scenes()
		self.update()
	


class MonoScaleDisplayComponent(ControlSurfaceComponent):


	def __init__(self, parent, *a, **k):
		super(MonoScaleDisplayComponent, self).__init__(*a, **k)
		self.num_segments = 4
		self._parent = parent
		self._name_display_line = None
		self._value_display_line = None
		self._name_data_sources = [ DisplayDataSource(DISPLAY_NAMES[index]) for index in xrange(4) ]
		self._value_data_sources = [ DisplayDataSource() for _ in range(self.num_segments) ]
	

	def set_controls(self, controls):
		if(controls):
			controls[0].set_on_off_values('DefaultMatrix.On', 'DefaultMatrix.Off')
			controls[2].set_on_off_values('Session.SceneSelected', 'Scales.Unselected')
			controls[3].set_on_off_values('Session.SceneSelected', 'Scales.Unselected')
			controls[4].set_on_off_values('Scales.FixedOn', 'Scales.FixedOff')
			controls[5].set_on_off_values('Scales.FixedOn', 'Scales.FixedOff')
			controls[6].set_on_off_values('Mixer.ArmSelected', 'Mixer.ArmUnselected')
			controls[7].set_on_off_values('Mixer.ArmSelected', 'Mixer.ArmUnselected')
		if controls is None:
			controls = [None for index in range(8)]
		self._parent._split_mode_selector.set_mode_toggle(controls[0])
		self._parent._vertical_offset_component.set_offset_change_buttons(controls[3], controls[2])
		self._parent._scale_offset_component.set_offset_change_buttons(controls[5], controls[4])
		self._parent._offset_component.set_offset_change_buttons(controls[7], controls[6])
	

	def set_name_display_line(self, display_line):
		self._name_display_line = display_line
		if self._name_display_line:
			self._name_display_line.set_data_sources(self._name_data_sources)
	

	def set_value_display_line(self, display_line):
		self._value_display_line = display_line
		if self._value_display_line:
			self._value_display_line.set_data_sources(self._value_data_sources)
	

	def set_value_string(self, value, source = 0):
		if source in range(len(self._value_data_sources)):
			self._value_data_sources[source].set_display_string(str(value))
	

	def update(self):
		pass
	


class MonoInstrumentComponent(CompoundComponent):


	def __init__(self, script, skin, grid_resolution, scalenames = SCALENAMES, *a, **k):
		super(MonoInstrumentComponent, self).__init__(*a, **k)
		self._scalenames = scalenames
		self._script = script
		self._skin = skin
		self._grid_resolution = grid_resolution
		self.keypad_shift_layer = AddLayerMode(self, Layer(priority = 0))
		self.drumpad_shift_layer = AddLayerMode(self, Layer(priority = 0))
		self.audioloop_layer = LayerMode(self, Layer(priority = 0))
		self._cur_chan = 0

		self._setup_selected_session_control()

		self._setup_shift_mode()

		self._display = MonoScaleDisplayComponent(self)
		self._display.set_enabled(False)

		self._scales_modes = self.register_component(ModesComponent())
		self._scales_modes.add_mode('disabled', None)
		self._scales_modes.add_mode('enabled', self._display, 'DefaultButton.On')
		self._scales_modes.selected_mode = 'disabled'

		self._split_mode_component = SplitModeSelector(self._split_mode_value)
		self._split_mode_component._on_value = 'MonoInstrument.SplitModeOnValue'
		self.set_split_button = self._split_mode_component.set_mode_toggle

		self._sequencer_mode_component = SplitModeSelector(self._sequencer_mode_value)
		self._sequencer_mode_component._on_value = 'MonoInstrument.SequencerModeOnValue'
		self.set_sequencer_button = self._sequencer_mode_component.set_mode_toggle

		self._offsets = [{'offset':DEFAULT_OFFSET, 'vertoffset':DEFAULT_VERTOFFSET, 'drumoffset':DEFAULT_DRUMOFFSET, 'scale':DEFAULT_SCALE, 'split':DEFAULT_SPLIT, 'sequencer':False} for index in range(16)]

		self._vertical_offset_component = ScrollingOffsetComponent(self._vertical_offset_value)
		self._vertical_offset_component._on_value = 'MonoInstrument.VerticalOffsetOnValue'
		self.set_vertical_offset_up_button = self._vertical_offset_component.set_up_button
		self.set_vertical_offset_down_button = self._vertical_offset_component.set_down_button

		self._offset_component = ScrollingOffsetComponent(self._offset_value)
		self._offset_component._shifted_value = 12
		self._offset_component._maximum = 112
		self._offset_component._on_value = 'MonoInstrument.OffsetOnValue'
		self.set_offset_up_button = self._offset_component.set_up_button
		self.set_offset_down_button = self._offset_component.set_down_button
		self.set_octave_up_button = self._offset_component.set_octave_up_button
		self.set_octave_down_button = self._offset_component.set_octave_down_button

		self._drum_offset_component = ScrollingOffsetComponent(self._drum_offset_value)
		self._drum_offset_component._shifted_value = 16
		self._drum_offset_component._maximum = 28
		self._drum_offset_component._on_value = 'MonoInstrument.DrumOffsetOnValue'
		self.set_drum_offset_up_button = self._drum_offset_component.set_up_button
		self.set_drum_offset_down_button = self._drum_offset_component.set_down_button
		self.set_drum_octave_up_button = self._drum_offset_component.set_octave_up_button
		self.set_drum_octave_down_button = self._offset_component.set_octave_down_button

		self._scale_offset_component = ScrollingOffsetComponent(self._scale_offset_value)
		self._scale_offset_component._minimum = 0
		self._scale_offset_component._maximum = len(self._scalenames)-1
		self._scale_offset_component._on_value = 'MonoInstrument.ScaleOffsetOnValue'
		self.set_scale_up_button = self._scale_offset_component.set_up_button
		self.set_scale_down_button = self._scale_offset_component.set_down_button

		self._keypad = MonoScaleComponent(parent = self, control_surface = script, skin = skin, grid_resolution = grid_resolution)

		self._drumpad = MonoDrumpadComponent(parent = self, control_surface = script, skin = skin, grid_resolution = grid_resolution)
		self.set_drumpad_mute_button = self._drumpad.set_mute_button
		self.set_drumpad_solo_button = self._drumpad.set_solo_button

		self._audio_loop = LoopSelectorComponent(follow_detail_clip=True, measure_length=1.0, name='Loop_Selector')

		self.set_loop_selector_matrix = self._audio_loop.set_loop_selector_matrix

		self._main_modes = ModesComponent()

		self.register_components(self._main_modes, self._audio_loop, self._vertical_offset_component, self._offset_component, self._scale_offset_component, self._drum_offset_component)
		# self._keypad, self._drumpad, 

		self._setup_modes()

		self._drum_group_finder = DrumGroupFinderComponent()
		self._on_drum_group_changed.subject = self._drum_group_finder

		self.on_selected_track_changed()
	

	display_layer = forward_property('_display')('layer')

	def _setup_selected_session_control(self):
		self._selected_session = ScaleSessionComponent(1, 32, self, enable_skinning = True)
		self._selected_session.name = "SelectedSession"
		self._selected_session.set_offsets(0, 0)
		#for row in range(32):
		#	clip_slot = self._selected_session.scene(row).clip_slot(0)
	

	def _setup_shift_mode(self):
		self._shifted = False
		self._shift_mode = ModesComponent()
		self._shift_mode.add_mode('shift', tuple([self._enable_shift, self._disable_shift]), behaviour = ShiftCancellableBehaviourWithRelease())
	

	@subject_slot('drum_group')
	def _on_drum_group_changed(self):
		drum_device = self._drum_group_finder.drum_group
		self._drumpad._step_sequencer.set_drum_group_device(drum_device)
	

	def set_touchstrip(self, control):
		#if control is None and not self._touchstrip is None:
		#	self._touchstrip.use_default_message()
		self._touchstrip = control
		if control:
			control.reset()
	

	def set_name_display_line(self, display_line):
		self._name_display_line = display_line
	

	def set_value_display_line(self, display_line):
		self._value_display_line = display_line
	

	def _set_display_line(self, line, sources):
		if line:
			line.set_num_segments(len(sources))
			for segment in xrange(len(sources)):
				line.segment(segment).set_data_source(sources[segment])
	

	def set_shift_button(self, button):
		self._on_shift_value.subject = button
		self._shifted = 0
		self._shift_mode.set_mode_button('shift', None)
		self._drumpad._step_sequencer._drum_group._select_button = button  #drum_group uses is_pressed() to determine an action
	

	def set_shift_mode_button(self, button):
		self._on_shift_value.subject = None
		self._shifted = 0
		self._shift_mode.set_mode_button('shift', button)
		self._drumpad._step_sequencer._drum_group._select_button = button  #drum_group uses is_pressed() to determine an action
	

	def is_shifted(self):
		#return self._on_shift_value.subject and self._on_shift_value.subject.is_pressed()
		return self._shifted
	

	@subject_slot('value')
	def _on_shift_value(self, value):
		self._shifted = value
		self.update()
		self._drumpad._step_sequencer._drum_group._on_select_value(value)
	

	def _enable_shift(self):
		self._on_shift_value(1)
	

	def _disable_shift(self):
		self._on_shift_value(0)
	

	def set_octave_enable_button(self, button):
		#debug('octave toggle button:', button)
		self._on_octave_enable_value.subject = button
	

	@subject_slot('value')
	def _on_octave_enable_value(self, value):
		self._offset_component._shift_value(value)
		self._drum_offset_component._shift_value(value)
	

	def _offset_value(self, offset):
		cur_track = self.song().view.selected_track
		if cur_track.has_midi_input:
			cur_chan = self._get_current_channel(cur_track)
			if cur_chan in range(17):
				self._offsets[cur_chan]['offset'] = offset
				self._set_device_attribute(self._top_device(), 'offset', offset)
				self._script.show_message('New root is Note# ' + str(self._offsets[cur_chan]['offset']) + ', ' + str(NOTENAMES[self._offsets[cur_chan]['offset']]))
				self._display.set_value_string(str(self._offsets[cur_chan]['offset']) + ', ' + str(NOTENAMES[self._offsets[cur_chan]['offset']]), 3)
				self._keypad.set_offset(offset)
				self.update()
	

	def _drum_offset_value(self, offset):
		cur_track = self.song().view.selected_track
		if cur_track.has_midi_input:
			cur_chan = self._get_current_channel(cur_track)
			if cur_chan in range(17):
				self._offsets[cur_chan]['drumoffset'] = offset
				self._set_device_attribute(self._top_device(), 'drumoffset', offset)
				self._script.show_message('New drum root is ' + str(self._offsets[cur_chan]['drumoffset']))
				self._display.set_value_string(str(self._offsets[cur_chan]['drumoffset']), 3)
				self._drumpad.set_offset(offset)
				self.update()
	

	def _vertical_offset_value(self, offset):
		cur_track = self.song().view.selected_track
		if cur_track.has_midi_input:
			cur_chan = self._get_current_channel(cur_track)
			if cur_chan in range(17):
				self._offsets[cur_chan]['vertoffset'] = offset
				self._set_device_attribute(self._top_device(), 'vertoffset', offset)
				self._script.show_message('New vertical offset is ' + str(self._offsets[cur_chan]['vertoffset']))
				self._display.set_value_string(str(self._offsets[cur_chan]['vertoffset']), 1)
				self._keypad.set_vertical_offset(offset)
				self.update()
	

	def _scale_offset_value(self, offset):
		cur_track = self.song().view.selected_track
		if cur_track.has_midi_input:
			cur_chan = self._get_current_channel(cur_track)
			if cur_chan in range(17):
				self._offsets[cur_chan]['scale'] = self._scalenames[offset]
				self._set_device_attribute(self._top_device(), 'scale', self._scalenames[offset])
				self._script.show_message('New scale is ' + str(self._offsets[cur_chan]['scale']))
				self._display.set_value_string(str(self._offsets[cur_chan]['scale']), 2)
				if len(SCALES[self._offsets[cur_chan]['scale']])>8:
					self._offsets[cur_chan]['vert_offset'] = 8
					self._keypad._vertoffset = 8
				self._keypad.set_scale_offset(self._scalenames[offset])
				self._drumpad._explicit_drumpad = self._scalenames[offset] is 'DrumPad'
				self.update()
	

	def _split_mode_value(self, mode):
		cur_track = self.song().view.selected_track
		if cur_track.has_midi_input:
			cur_chan = self._get_current_channel(cur_track)
			if cur_chan in range(17):
				self._offsets[cur_chan]['split'] = bool(mode)
				self._set_device_attribute(self._top_device(), 'split', bool(mode))
				self._display.set_value_string(str(bool(mode)), 0)
				if mode > 0 and self._sequencer_mode_component._mode_index > 0:
					self._sequencer_mode_component.set_mode(0)
					self._sequencer_mode_value(0)
				else:
					self.update()
	

	def _sequencer_mode_value(self, mode):
		cur_track = self.song().view.selected_track
		if cur_track.has_midi_input:
			cur_chan = self._get_current_channel(cur_track)
			if cur_chan in range(17):
				self._offsets[cur_chan]['sequencer'] = bool(mode)
				self._set_device_attribute(self._top_device(), 'sequencer', bool(mode))
				self._display.set_value_string(str(bool(mode)), 0)
				if mode > 0 and self._split_mode_component._mode_index > 0:
					self._split_mode_component.set_mode(0)
					self._split_mode_value(0)
				else:
					self.update()
	

	def on_selected_track_changed(self):
		debug('instrument track changed, updating')
		self._selected_session.update_current_track()
		self.update_settings()
		#make sure other components are ready, namely drumpad selector
		self._script.schedule_message(1, self.update)
	

	def update_settings(self):
		cur_track = self.song().view.selected_track
		if cur_track.has_midi_input:
			cur_chan = self._get_current_channel(cur_track)
			if cur_chan in range(17):
				offsets = self._current_device_offsets(self._offsets[cur_chan])
				offset, vertoffset, scale, split, sequencer, drumoffset = offsets['offset'], offsets['vertoffset'], offsets['scale'], offsets['split'], offsets['sequencer'], offsets['drumoffset']
				self._offset_component.set_offset(offset)
				self._scale_offset_component.set_offset(self._scalenames.index(scale))
				self._vertical_offset_component.set_offset(vertoffset)
				self._drum_offset_component.set_offset(drumoffset)
				self._split_mode_component._set_protected_mode_index(int(split))
				self._sequencer_mode_component._set_protected_mode_index(int(sequencer))
				self._cur_chan = cur_chan
				self._drumpad._channel = cur_chan
				self._keypad._channel = cur_chan
				self._drumpad._explicit_drumpad = scale is 'DrumPad'
	

	def update(self):
		super(MonoInstrumentComponent, self).update()
		if self.is_enabled():
			new_mode = 'disabled'
			self._main_modes._mode_stack.release_all()
			cur_track = self.song().view.selected_track
			if cur_track.has_audio_input and cur_track in self.song().visible_tracks:
				new_mode = 'audioloop'
			elif cur_track.has_midi_input:
				cur_chan = self._get_current_channel(cur_track)
				offsets = self._current_device_offsets(self._offsets[cur_chan])
				scale, split, sequencer = offsets['scale'], offsets['split'], offsets['sequencer']
				if scale == 'Auto':
					scale = detect_instrument_type(cur_track)
				new_mode = ['keypad', 'drumpad'][int(scale in ['DrumPad', 'DrumRack'])]
				if split:
					new_mode += '_split'
				elif sequencer:
					new_mode +=  '_sequencer'
				if self.is_shifted():
					new_mode += '_shifted'
				self._script.set_feedback_channels(range(14, 15))
			if new_mode in self._main_modes._mode_map or new_mode is None:
				self._main_modes.selected_mode = new_mode
			else:
				self._main_modes.selected_mode = 'disabled'
			debug('monoInstrument mode is:', self._main_modes.selected_mode)
	

	def _setup_modes(self):
		self._main_modes.add_mode('disabled', [])
		self._main_modes.add_mode('drumpad', [self._drumpad.main_layer])
		self._main_modes.add_mode('drumpad_split', [self._drumpad.split_layer])
		self._main_modes.add_mode('drumpad_sequencer', [self._drumpad.sequencer_layer])
		self._main_modes.add_mode('drumpad_shifted', [self._drumpad.main_layer, self.drumpad_shift_layer])
		self._main_modes.add_mode('drumpad_split_shifted', [self._drumpad.split_layer, self.drumpad_shift_layer])
		self._main_modes.add_mode('drumpad_sequencer_shifted', [self._drumpad.sequencer_shift_layer, self.drumpad_shift_layer])
		self._main_modes.add_mode('keypad', [self._keypad.main_layer])
		self._main_modes.add_mode('keypad_split', [self._keypad.split_layer])
		self._main_modes.add_mode('keypad_sequencer', [self._keypad.sequencer_layer])
		self._main_modes.add_mode('keypad_shifted', [self.keypad_shift_layer])
		self._main_modes.add_mode('keypad_split_shifted', [self._keypad.split_layer, self.keypad_shift_layer])
		self._main_modes.add_mode('keypad_sequencer_shifted', [self._keypad.sequencer_shift_layer, self.keypad_shift_layer])
		self._main_modes.add_mode('audioloop', [self.audioloop_layer])
		#self._main_modes.register_component(self._main_modes)
	

	def _top_device(self, selected_device = None):
		if selected_device is None:
			selected_device = self.song().appointed_device
		if not selected_device is None and hasattr(selected_device, 'canonical_parent'):
			while not isinstance(selected_device.canonical_parent, Live.Track.Track):
				selected_device = selected_device.canonical_parent
		return selected_device
	

	def _set_device_attribute(self, device, attribute, value, force = False):
		if not device is None and hasattr(device, 'name'):
			name = device.name.split(' ')
			for index in range(len(name)):
				if len(str(name[index])) and str(name[index][0])=='@':
					vals = name[index][1:].split(':')
					if vals[0] == attribute:
						#vals[1] = value
						name[index] = str('@'+str(attribute)+':'+str(value))
						device.name = ' '.join(name)
	

	def _remove_device_attribute(self, device, attribute, force = False):
		if not device is None and hasattr(device, 'name'):
			name = device.name.split(' ')
			for index in range(len(name)):
				if len(str(name[index])) and str(name[index][0])=='@':
					vals = name[index][1:].split(':')
					if vals[0] == attribute:
						name.remove(vals[0])
						device.name = ' '.join(name)
	

	def _current_device_offsets(self, dict_entry, device = None):
		#debug('finding current device offsets')
		if device is None:
			device = self.song().appointed_device
		selected_device = self._top_device(device)
		if not selected_device is None and hasattr(selected_device, 'name'):
			name = selected_device.name
			#debug('device name: ' + str(name.split(' ')))
			for item in name.split(' '):
				if len(str(item)) and str(item)[0]=='@':
					vals = item[1:].split(':')
					if len(vals) < 2:
						def_assignments = {'scale':'Auto', 'sequencer':False, 'split':False, 'offset':36, 'vertoffset':4, 'drumoffset':0}
						if vals[0] in def_assignments:
							vals.append([vals[0]])
					if vals[0] in dict_entry.keys():
						if vals[0] == 'scale' and vals[1] in SCALES.keys():
							dict_entry[vals[0]] = str(vals[1])
						elif vals[0] in ['sequencer', 'split']:
							if vals[1] in ['False', 'True']:
								dict_entry[vals[0]] = bool(['False', 'True'].index(vals[1]))
						elif vals[0] in ['offset', 'vertoffset', 'drumoffset']:
							dict_entry[vals[0]] = int(vals[1])
			#for key in dict_entry.keys():
			#	debug('key: ' + str(key) + ' entry:' + str(dict_entry[key]))
		return dict_entry
	

	def _get_current_channel(self, cur_track = None):
		if cur_track is None:
			cur_track = self.song().view.selected_track
		cur_chan = cur_track.current_input_sub_routing
		if len(cur_chan) == 0:
			cur_chan = 'All Channels'
		if cur_chan == 'All Channels':
			cur_chan = 1
		if cur_chan in CHANNELS:
			cur_chan = (CHANNELS.index(cur_chan)%15)+1
		else:
			cur_chan = 14
		return cur_chan
	


class MonoScaleComponent(CompoundComponent):


	def __init__(self, parent, control_surface, skin, grid_resolution, *a, **k):
		super(MonoScaleComponent, self).__init__(*a, **k)
		self._parent = parent
		self._control_surface = control_surface
		self._skin = skin
		self._grid_resolution = grid_resolution
		self._offset = 0
		self._vertoffset = 0
		self._scale = 'Major'
		self._channel = 0
		self.main_layer = LayerMode(self, Layer(priority = 0))
		self.split_layer = LayerMode(self, Layer(priority = 0))
		self.sequencer_layer = LayerMode(self, Layer(priority = 0))
		self.sequencer_shift_layer = LayerMode(self, Layer(priority = 0))
		self._note_sequencer = StepSeqComponent(ClipCreator(), skin, grid_resolution, name='Note_Sequencer')
		self._note_sequencer._playhead_component._notes=tuple(range(16))
		self._note_sequencer._playhead_component._triplet_notes=tuple(chain(*starmap(range, ((0, 6), (8, 14)))))
		#self.set_playhead = self._note_sequencer.set_playhead
		self.set_loop_selector_matrix = self._note_sequencer.set_loop_selector_matrix 
		self.set_quantization_buttons = self._note_sequencer.set_quantization_buttons
		#self.set_follow_button = self._note_sequencer.set_follow_button
		self.register_component(self._note_sequencer)

	

	def set_follow_button(self, button):
		if not self._note_sequencer._loop_selector._follow_button is None:
			self._note_sequencer._loop_selector._follow_button.descriptor = None
		if button:
			button.descriptor = 'LoopSelector.Follow'
		self._note_sequencer.set_follow_button(button)
	

	def set_playhead(self, playhead):
		#debug('keys set playhead: ' + str(playhead))
		self._note_sequencer.set_playhead(playhead)
	

	def set_offset(self, val):
		self._offset = val
	

	def set_vertical_offset(self, val):
		self._vertoffset = val
		#self._on_keypad_matrix_value.subject and self.set_keypad_matrix(self._on_keypad_matrix_value.subject)
	

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
			shifted = self._parent.is_shifted()
			current_note = self._note_sequencer._note_editor.editing_note
			for button, (x, y) in matrix.iterbuttons():
				if button:
					note_pos = x + (abs((height-1)-y)*vertoffset)
					note = offset + SCALES[scale][note_pos%scale_len] + (12*int(note_pos/scale_len))
					if note is current_note:
						button.scale_color = 'MonoInstrument.Keys.SelectedNote'
					else:
						button.scale_color = KEYCOLORS[(note%12 in WHITEKEYS) + (((note_pos%scale_len)==0)*2)]
					button.display_press = True
					button._last_flash = 0
					if shifted:
						button.use_default_message()
						button.set_enabled(True)
					else:
						button.set_identifier(note%127)
						button.descriptor = str(NOTENAMES[button._msg_identifier])
						button.set_enabled(False)
						button.set_channel(cur_chan)
					button.set_light(button.scale_color)
			self._control_surface.release_controlled_track()
	

	def set_sequencer_matrix(self, matrix):
		#debug('set keys sequencer matrix: ' + str(matrix))
		reset_matrix(self._note_sequencer._note_editor_matrix)
		self._on_sequencer_matrix_value.subject = matrix
		if matrix:
			cur_chan = self._channel
			width = matrix.width()
			height = matrix.height()
			for button, (x, y) in matrix.iterbuttons():
				if button:
					button.display_press = False
					#button.set_channel(0)
					#button.set_on_off_values('Sequencer.On', 'Sequencer.Off')
					button.set_identifier(x + (y*width))
			#self._control_surface.set_feedback_channels(range(14, 15))
		self._note_sequencer.set_button_matrix(matrix)
		#debug('playhead color is:', self._note_sequencer.playhead_color, int(self._skin[self._note_sequencer.playhead_color]))
	

	def set_split_matrix(self, matrix):
		self._on_split_matrix_value.subject = matrix
		self._parent._selected_session.set_clip_launch_buttons(matrix)
		self._control_surface.schedule_message(1, self._parent._selected_session.update)
	

	@subject_slot('value')
	def _on_note_matrix_value(self, value, x, y, *a, **k):
		debug('on_keys_matrix_value', x, y, value)
		
	

	@subject_slot('value')
	def _on_note_CC_matrix_value(self, value, x, y, *a, **k):
		debug('on_note_CC_matrix_value', x, y, value)
		
	

	@subject_slot('value')
	def _on_sequencer_matrix_value(self, value, x, y, *a, **k):
		debug('on_sequencer_matrix_value', x, y, value)

		#if y>1 and value:
		#	self._note_sequencer._note_editor.editing_note = self._base_grid.get_button(x, y)._stored_note
		#	self._assign_midi_shift_layer()
	

	@subject_slot('value')
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
			self._note_sequencer._note_editor._set_editing_note(note)
			self.set_keypad_matrix(matrix)
	

	@subject_slot('value')
	def _on_split_matrix_value(self, value, x, y, *a, **k):
		pass
	

	def set_note_CC_matrix(self, matrix):
		self._on_note_CC_matrix_value.subject = matrix
		#self.update()
	

	def update(self):
		super(MonoScaleComponent, self).update()
	


class MonoDrumpadComponent(CompoundComponent):


	def __init__(self, parent, control_surface, skin, grid_resolution, *a, **k):
		super(MonoDrumpadComponent, self).__init__(*a, **k)
		self._parent = parent
		self._control_surface = control_surface
		self._skin = skin
		self._grid_resolution = grid_resolution
		self._offset = 0
		self._channel = 1
		self._explicit_drumpad = False
		self.main_layer = LayerMode(self, Layer(priority = 0))
		self.split_layer = LayerMode(self, Layer(priority = 0))
		self.sequencer_layer = LayerMode(self, Layer(priority = 0))
		self.sequencer_shift_layer = LayerMode(self, Layer(priority = 0))
		self._step_sequencer = StepSeqComponent(ClipCreator(), skin, grid_resolution, name='Drum_Sequencer')
		self._step_sequencer._note_editor._visible_steps = self._visible_steps
		#self._step_sequencer._drum_group._update_pad_led = self._drum_group_update_pad_led
		#self._step_sequencer._drum_group._update_control_from_script = self._update_control_from_script
		self._step_sequencer._playhead_component._notes=tuple(range(16))
		self._step_sequencer._playhead_component._triplet_notes=tuple(chain(*starmap(range, ((0, 3), (4, 7), (8, 11), (12, 15)))))
		self.set_playhead = self._step_sequencer.set_playhead
		self.set_loop_selector_matrix = self._step_sequencer.set_loop_selector_matrix 
		self.set_quantization_buttons = self._step_sequencer.set_quantization_buttons
		#self.set_follow_button = self._step_sequencer.set_follow_button
		self.register_component(self._step_sequencer)
	

	def set_follow_button(self, button):
		if not self._step_sequencer._loop_selector._follow_button is None:
			self._step_sequencer._loop_selector._follow_button.descriptor = None
		if button:
			button.descriptor = 'LoopSelector.Follow'
		self._step_sequencer.set_follow_button(button)
	

	"""Push only supports full rows of 8 buttons for playhead display....this is a hack"""
	def _visible_steps(self):
		first_time = self._step_sequencer._note_editor.page_length * self._step_sequencer._note_editor._page_index
		steps_per_page = self._step_sequencer._note_editor._get_step_count()
		step_length = self._step_sequencer._note_editor._get_step_length()
		indices = range(steps_per_page)
		if self._step_sequencer._note_editor._is_triplet_quantization():
			indices = filter(lambda k: k % 4 != 3, indices)
		return [ (self._step_sequencer._note_editor._time_step(first_time + k * step_length), index) for k, index in enumerate(indices) ]
	

	def _drum_group_update_pad_led(self, pad, button, soloed_pads):
		if self._on_drumpad_matrix_value.subject:
			DrumGroupComponent._update_pad_led(self._step_sequencer._drum_group, pad, button, soloed_pads)
			#debug('updating leds:' + str(button.name))
			#button.turn_off()
			button.color = 'DefaultButton.Off'
	

	"""def _update_control_from_script(self):
		takeover_drums = self._step_sequencer._drum_group._takeover_drums or self._step_sequencer._drum_group._selected_pads
		profile = 'default' if takeover_drums else 'drums'
		if self._step_sequencer._drum_group.drum_matrix:
			#for button, _ in self._step_sequencer._drum_group.drum_matrix.iterbuttons():
			for button, _ in ifilter(first, self._step_sequencer._drum_group.drum_matrix.iterbuttons()):
				if button:
					translation_channel = self._parent._get_current_channel()
					button.set_channel(translation_channel)
					button.set_enabled(takeover_drums)
					#debug('button name: ' + str(button.name) + ' ch: ' + str(translation_channel) + ' takeover drums is' + str(takeover_drums))
					button.sensitivity_profile = profile"""
	

	def set_offset(self, offset):
		self._offset = offset
		self._step_sequencer._drum_group and self._step_sequencer._drum_group._set_position(offset)
	

	def set_note_matrix(self, matrix):
		reset_matrix(self._on_note_matrix_value.subject)
		self._on_note_matrix_value.subject = matrix
		#self.update()
	

	def set_note_CC_matrix(self, matrix):
		reset_matrix(self._on_note_CC_matrix_value.subject)
		self._on_note_CC_matrix_value.subject = matrix
		#self.update()
	

	def set_sequencer_matrix(self, matrix):
		reset_matrix(self._step_sequencer._note_editor_matrix)
		self._on_sequencer_matrix_value.subject = matrix
		if matrix:
			cur_chan = self._channel
			#self._step_sequencer._drum_group.set_select_button(self._button[self._layer])
			width = matrix.width()
			for button, (x, y) in matrix.iterbuttons():
				if button:
					button.display_press = False
					button.set_identifier(x+(y*width))
					#button.set_channel(14)
					#debug('button assignments: ' + str(button.message_identifier()) + ' ' + str(button.message_channel()))
		self._step_sequencer.set_button_matrix(matrix)
	

	def set_split_matrix(self, matrix):
		self._on_split_matrix_value.subject = matrix
		self._parent._selected_session.set_clip_launch_buttons(matrix)
		#self._control_surface.schedule_message(1, self._parent._selected_session.update)
	

	def set_drumpad_matrix(self, matrix):
		#debug('set drumpad matrix: ' + str(matrix))
		new_reset_matrix(self._step_sequencer._drum_group.drum_matrix)
		reset_matrix(self._on_drumpad_matrix_value.subject)
		self._on_drumpad_matrix_value.subject = matrix
		if matrix:
			cur_chan = self._channel
			height = matrix.height()
			width = matrix.width()
			self.set_pad_translations(make_pad_translations(cur_chan))
			if width > 3 and height > 3 and not self._parent._drum_group_finder.drum_group is None and not self._explicit_drumpad:
				#debug('setting Live drum matrix')
				self.set_pad_translations(make_pad_translations(cur_chan))
				for button, (x, y) in matrix.iterbuttons():
					if button:
						button.display_press = False
						if x < 4 and y < 4:
							button.set_identifier(x + (y*4) + 16)
							button.set_channel(cur_chan)
						else:
							button.use_default_message()
							button.set_enabled(True)
							button.reset()
				#self._control_surface.set_feedback_channels(range(cur_chan, cur_chan+1) + [14])
				self._control_surface.reset_controlled_track()
				self._step_sequencer.set_drum_matrix(matrix.submatrix[:4, :4])
			else:
				#self._step_sequencer._drum_group.mute_button and self._step_sequencer._drum_group.mute_button.send_value(0, True)
				#self._step_sequencer._drum_group.solo_button and self._step_sequencer._drum_group.solo_button.send_value(0, True)
				offset = self._offset
				current_note = self._step_sequencer._note_editor.editing_note
				shifted = self._parent.is_shifted()
				#debug('setting normal drum matrix')
				for button, (x, y) in matrix.iterbuttons():
					if button and x < 8 and y < 4:
						note = (DRUMNOTES[x + (y*8)] + (offset*4))%128
						button.set_identifier(note)
						if note is current_note:
							button.scale_color = 'MonoInstrument.Drums.SelectedNote'
						else:
							button.scale_color = DRUMCOLORS[int((note-4)/16)%2]
						button.display_press = True
						button._last_flash = 0
						button.descriptor = str(NOTENAMES[button._msg_identifier])
						if shifted:
							button.use_default_message()
							button.set_enabled(True)
						else:
							button.set_enabled(False)
							button.set_channel(cur_chan)
						button.set_light(button.scale_color)
				self._step_sequencer.set_drum_matrix(None)
				#self._control_surface.set_feedback_channels(range(14, 15))
				self._control_surface.release_controlled_track()
		else:
			self._step_sequencer.set_drum_matrix(None)
	

	def set_mute_button(self, button):
		self._step_sequencer.set_mute_button(button)
		if button:
			button.send_value(2, True)
	

	def set_solo_button(self, button):
		self._step_sequencer.set_solo_button(button)
		if button:
			button.send_value(3, True)
	

	def set_quantization_buttons(self, button):
		#we do this so we can override a full grid for the extra button at the end
		if button and isinstance(button, ButtonMatrixElement):
			debug('button is matrix')
			for but, (x, y) in button.iterbuttons():
				debug('button ' + str(x) + str(y) + ' is: ' + str(but))
			button = button.get_button(0, 0)
		self._step_sequencer.set_follow_button(button)
	

	@subject_slot('value')
	def _on_note_matrix_value(self, value, x, y, *a, **k):
		debug('on_drum_matrix_value', x, y, value)
	

	@subject_slot('value')
	def _on_note_CC_matrix_value(self, value, x, y, *a, **k):
		debug('on_note_CC_matrix_value', x, y, value)
		
	

	@subject_slot('value')
	def _on_sequencer_matrix_value(self, value, x, y, *a, **k):
		debug('on_sequencer_matrix_value', x, y, value)
	

	@subject_slot('value')
	def _on_drumpad_matrix_value(self, value, x, y, *a, **k):
		debug('on_drumpad_matrix_value', x, y, value)
		if value:
			matrix = self._on_drumpad_matrix_value.subject
			width = matrix.width()
			height = matrix.height()
			offset = self._offset
			cur_chan = self._channel
			note = (DRUMNOTES[x + (y*8)] + (offset*4))%127
			self._step_sequencer._note_editor._set_editing_note(note)
			if self._step_sequencer._drum_group._drum_group_device:
				self._step_sequencer._drum_group._drum_group_device.view.selected_drum_pad = self._step_sequencer._drum_group._drum_group_device.drum_pads[note]
			#self.set_drumpad_matrix(matrix)
	

	@subject_slot('value')
	def _on_split_matrix_value(self, value, x, y, *a, **k):
		pass
	

	def set_pad_translations(self, pad_translations):
		if not pad_translations == self._control_surface._pad_translations:
			self._control_surface._pad_translations = None
			#self.log_message('setting translations: ' + str(pad_translations))
			self._control_surface.set_pad_translations(pad_translations)
	

	def update(self):
		super(MonoDrumpadComponent, self).update()
	
