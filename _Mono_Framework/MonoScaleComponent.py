"""
MonoScaleComponent.py

Created by amounra on 2013-07-18.
Copyright (c) 2013 __aumhaa__. All rights reserved.
"""

import Live

from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.CompoundComponent import CompoundComponent
from _Framework.ModeSelectorComponent import ModeSelectorComponent
from _Framework.SubjectSlot import subject_slot, subject_slot_group
from _Framework.ButtonElement import ButtonElement
from _Framework.DisplayDataSource import DisplayDataSource
from _Framework.ModesComponent import DisplayingModesComponent, ModesComponent
from _Framework.Util import forward_property
from _Framework.SessionComponent import SessionComponent

from Push.Colors import Basic, Rgb, Pulse, Blink, BiLed

INITIAL_SCROLLING_DELAY = 5
INTERVAL_SCROLLING_DELAY = 1

DISPLAY_NAMES = ['SplitMode', 'Vertical Offset', 'Scale Type', 'Root Note']

_NOTENAMES = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
NOTENAMES = [(_NOTENAMES[index%12] + ' ' + str(int(index/12))) for index in range(128)]
SCALENAMES = None
SCALEABBREVS = None

#from Map import *

CHANNELS = ['Ch. 2', 'Ch. 3', 'Ch. 4', 'Ch. 5', 'Ch. 6', 'Ch. 7', 'Ch. 8', 'Ch. 9', 'Ch. 10', 'Ch. 11', 'Ch. 12', 'Ch. 13', 'Ch. 14', 'Ch. 15', 'Ch. 16']
MODES = ['chromatic', 'drumpad', 'scale', 'user']

DEFAULT_MIDI_ASSIGNMENTS = {'mode':'chromatic', 'offset':36, 'vertoffset':12, 'scale':'Chromatic', 'drumoffset':0, 'split':False}

"""The scale modes and drumpads use the following note maps"""

NOTES = [24, 25, 26, 27, 28, 29, 30, 31, 16, 17, 18, 19, 20, 21, 22, 23, 8, 9, 10, 11, 12, 13, 14, 15, 0, 1, 2, 3, 4, 5, 6, 7]
#DRUMNOTES = [48, 49, 50, 51, 64, 65, 66, 67, 44, 45, 46, 47, 60, 61, 62, 63, 40, 41, 42, 43, 56, 57, 58, 59, 36, 37, 38, 39, 52, 53, 54, 55]
DRUMNOTES = [12, 13, 14, 15, 28, 29, 30, 31, 8, 9, 10, 11, 24, 25, 26, 27, 4, 5, 6, 7, 20, 21, 22, 23, 0, 1, 2, 3, 16, 17, 18, 19]
SCALENOTES = [36, 38, 40, 41, 43, 45, 47, 48, 24, 26, 28, 29, 31, 33, 35, 36, 12, 14, 16, 17, 19, 21, 23, 24, 0, 2, 4, 5, 7, 9, 11, 12]
WHITEKEYS = [0, 2, 4, 5, 7, 9, 11, 12]

"""These are the scales we have available.  You can freely add your own scales to this """
SCALES = 	{'Mod':[0,1,2,3,4,5,6,7,8,9,10,11],
			'Session':[0,1,2,3,4,5,6,7,8,9,10,11],
			'Auto':[0,1,2,3,4,5,6,7,8,9,10,11],
			'Chromatic':[0,1,2,3,4,5,6,7,8,9,10,11],
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

SCALEABBREVS = {'Session':'-S','Auto':'-A','Chromatic':'12','DrumPad':'-D','Major':'M-','Minor':'m-','Dorian':'II','Mixolydian':'V',
			'Lydian':'IV','Phrygian':'IH','Locrian':'VH','Diminished':'d-','Whole-half':'Wh','Whole Tone':'WT','Minor Blues':'mB',
			'Minor Pentatonic':'mP','Major Pentatonic':'MP','Harmonic Minor':'mH','Melodic Minor':'mM','Dominant Sus':'D+','Super Locrian':'SL',
			'Neopolitan Minor':'mN','Neopolitan Major':'MN','Enigmatic Minor':'mE','Enigmatic':'ME','Composite':'Cp','Bebop Locrian':'lB',
			'Bebop Dominant':'DB','Bebop Major':'MB','Bhairav':'Bv','Hungarian Minor':'mH','Minor Gypsy':'mG','Persian':'Pr',
			'Hirojoshi':'Hr','In-Sen':'IS','Iwato':'Iw','Kumoi':'Km','Pelog':'Pg','Spanish':'Sp'}


"""Any scale names in this array will automatically use SplitMode when chosen, regardless of the SplitSwitch for the individual MIDI Channel"""
SPLIT_SCALES = []

"""It is possible to create a custom list of scales to be used by the script.  For instance, the list below would include major, minor, auto, drumpad, and chromatic scales, in that order."""
#SCALENAMES = ['Major', 'Minor', 'Auto', 'DrumPad', 'Chromatic']

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

OFFSET_SHIFT_IS_MOMENTARY = True

class SplitModeSelector(ModeSelectorComponent):


	def __init__(self, callback):
		super(SplitModeSelector, self).__init__()
		self._report_mode = callback
		self._modes_buttons = []
		self._set_protected_mode_index(0)
	

	def number_of_modes(self):
		return 2
	

	def set_mode_toggle(self, button):
		assert(button == None or isinstance(button, ButtonElement))
		if self._mode_toggle != None:
			self._mode_toggle.remove_value_listener(self._toggle_value)
		self._mode_toggle = button
		if self._mode_toggle != None:
			self._mode_toggle.add_value_listener(self._toggle_value)
		self.update()
	

	def _mode_value(self, value, sender):
		if self._is_enabled:
			super(SplitModeSelector, self)._mode_value(value, sender)
			self._report_mode(self._mode_index)
	

	def _toggle_value(self, value):
		if self._is_enabled:
			super(SplitModeSelector, self)._toggle_value(value)
			self._report_mode(self._mode_index)
	

	def update(self):
		if self._is_enabled:
			if len(self._modes_buttons) > 0:
				for index in range(len(self._modes_buttons)):
					if self._mode_index == index:
						self._modes_buttons[index].turn_on()
					else:
						self._modes_buttons[index].turn_off()
			if not self._mode_toggle is None:
				if self._mode_index > 0:
					self._mode_toggle.turn_on()
				else:
					self._mode_toggle.turn_off()
	


class ScaleModeComponent(ModeSelectorComponent):
	__module__ = __name__
	__doc__ = ' Class for switching between modes, handle several functions with few controls '


	def __init__(self, script):
		super(ScaleModeComponent, self).__init__()
		self._script = script
		self._set_protected_mode_index(0)
	

	def set_mode_buttons(self, buttons):
		for button in self._modes_buttons:
			button.remove_value_listener(self._mode_value)
		self._modes_buttons = []
		if (buttons != None):
			for button in buttons:
				assert isinstance(button, MonoButtonElement)
				identify_sender = True
				button.add_value_listener(self._mode_value, identify_sender)
				self._modes_buttons.append(button)
			for index in range(len(self._modes_buttons)):
				if (index == self._mode_index):
					self._modes_buttons[index].turn_on()
				else:
					self._modes_buttons[index].turn_off()
	

	def set_mode_toggle(self, button):
		assert ((button == None) or isinstance(button, MonoButtonElement))
		if (self._mode_toggle != None):
			self._mode_toggle.remove_value_listener(self._toggle_value)
		self._mode_toggle = button
		if (self._mode_toggle != None):
			self._mode_toggle.add_value_listener(self._toggle_value)
	

	def number_of_modes(self):
		return 8
	

	def update(self):
		if self.is_enabled():
			scales = SCALES.keys()
			self._script._offsets['scale'] = scales[self._mode_index%len(scales)]
			for index in range(len(self._modes_buttons)):
				if (index == self._mode_index):
					self._modes_buttons[index].turn_on()
				else:
					self._modes_buttons[index].turn_off()
	


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
		self._scroll_up_button = None
		self._scroll_down_button = None
		self._shift_button = None
		self._shift_is_momentary = True
		self._register_timer_callback(self._on_timer)
	

	def disconnect(self):
		if (self._scroll_up_button != None):
			self._scroll_up_button.remove_value_listener(self._scroll_up_value)
			self._scroll_up_button = None
		if (self._scroll_down_button != None):
			self._scroll_down_button.remove_value_listener(self._scroll_down_value)
			self._scroll_down_button = None
	

	def on_enabled_changed(self):
		self._scroll_up_ticks_delay = -1
		self._scroll_down_ticks_delay = -1
		self.update()
	

	def set_offset_change_buttons(self, up_button, down_button):
		assert ((up_button == None) or isinstance(up_button, ButtonElement))
		assert ((down_button == None) or isinstance(down_button, ButtonElement))
		do_update = False
		if (up_button is not self._scroll_up_button):
			do_update = True
			if (self._scroll_up_button != None):
				self._scroll_up_button.remove_value_listener(self._scroll_up_value)
			self._scroll_up_button = up_button
			if (self._scroll_up_button != None):
				self._scroll_up_button.add_value_listener(self._scroll_up_value)
		if (down_button is not self._scroll_down_button):
			do_update = True
			if (self._scroll_down_button != None):
				self._scroll_down_button.remove_value_listener(self._scroll_down_value)
			self._scroll_down_button = down_button
			if (self._scroll_down_button != None):
				self._scroll_down_button.add_value_listener(self._scroll_down_value)
		if do_update:
			self.update()
	

	def _scroll_up_value(self, value):
		assert (value in range(128))
		#assert (self._scroll_up_button != None)
		if self.is_enabled():
			button_is_momentary = True
			if not self._scroll_up_button is None:
				button_is_momentary = self._scroll_up_button.is_momentary()
			if button_is_momentary:
				if (value != 0):
					self._scroll_up_ticks_delay = INITIAL_SCROLLING_DELAY
				else:
					self._scroll_up_ticks_delay = -1
			if ((not self._is_scrolling()) and ((value is not 0) or (not button_is_momentary))):
				self._offset = max(self._minimum, min(self._maximum, self._offset + (1 + (self._shifted * self._shifted_value))))
				self.update()
				self._report_change(self._offset)
	

	def _scroll_down_value(self, value):
		assert (value in range(128))
		#assert (self._scroll_down_button != None)
		if self.is_enabled():
			button_is_momentary = True
			if not self._scroll_down_button is None:
				button_is_momentary = self._scroll_down_button.is_momentary()
			if button_is_momentary:
				if (value != 0):
					self._scroll_down_ticks_delay = INITIAL_SCROLLING_DELAY
				else:
					self._scroll_down_ticks_delay = -1
			if ((not self._is_scrolling()) and ((value is not 0) or (not button_is_momentary))):
				self._offset = max(self._minimum, min(self._maximum, self._offset - (1 + (self._shifted * self._shifted_value))))
				self.update()
				self._report_change(self._offset)
	

	def set_shift_button(self, shift_button):
		if self._shift_button != None:
			if self._shift_button.value_has_listener(self._shift_value):
				self._shift_button.remove_value_listener(self._shift_value)
		self._shift_button = shift_button
		if self._shift_button != None:
			self._shift_button.add_value_listener(self._shift_value)
			self.update()
	

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
							 self._scroll_down_ticks_delay]
			if (scroll_delays.count(-1) < 2):
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
				new_offset = max(self._minimum, min(self._maximum, self._offset + offset_increment))
				if new_offset != self._offset:
					self._offset =  new_offset
					self.update()
					self._report_change(self._offset)
	

	def _is_scrolling(self):
		return (0 in (self._scroll_up_ticks_delay,
					  self._scroll_down_ticks_delay))
	

	def update(self):
		if (self._scroll_down_button != None):
			if (self._offset > self._minimum):
				self._scroll_down_button.turn_on()
			else:
				self._scroll_down_button.turn_off()
		if (self._scroll_up_button != None):
			if (self._offset < self._maximum):
				self._scroll_up_button.turn_on()
			else:
				self._scroll_up_button.turn_off()	
		if (self._shift_button != None):
			if (self._shifted):
				self._shift_button.turn_on()
			else:
				self._shift_button.turn_off()
	

	def deassign_all(self):
		self.set_offset_change_buttons(None, None)
		self.set_shift_button(None)
		self.on_enabled_changed()
	


class ScaleSessionComponent(SessionComponent):


	def __init__(self, num_tracks, num_scenes, script):
		super(ScaleSessionComponent, self).__init__(num_tracks, num_scenes)
		self._shifted = False
		self._script = script
	

	def deassign_all(self):
		self._shifted = False
		self.set_scene_bank_buttons(None, None)
		self.set_track_bank_buttons(None, None)
		self.set_stop_all_clips_button(None)
		self.set_stop_track_clip_buttons(None)
		self.set_select_buttons(None, None)
		for scene in self._scenes:
			scene.set_launch_button(None)
			for slot in scene._clip_slots:
				slot.set_launch_button(None)
	

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
	


class MonoScaleComponent(CompoundComponent):


	def __init__(self, script, *a, **k):
		super(MonoScaleComponent, self).__init__(*a, **k)
		self._script = script
		self._matrix = None
		self._setup_selected_session_control()
		self._touchstrip = None

		self._display = MonoScaleDisplayComponent(self)
		self._display.set_enabled(False)

		self._scales_modes = self.register_component(ModesComponent())
		self._scales_modes.add_mode('disabled', None)
		self._scales_modes.add_mode('enabled', self._display, 'DefaultButton.On')
		self._scales_modes.selected_mode = 'disabled'

		self._offsets = [{'offset':DEFAULT_OFFSET, 'vertoffset':DEFAULT_VERTOFFSET, 'drumoffset':DEFAULT_DRUMOFFSET, 'scale':DEFAULT_SCALE, 'split':DEFAULT_SPLIT} for index in range(16)]

		self._split_mode_selector = SplitModeSelector(self._split_mode_value)

		self._vertical_offset_component = ScrollingOffsetComponent(self._vertical_offset_value)

		self._offset_component = ScrollingOffsetComponent(self._offset_value)
		self._offset_component._shifted_value = 11
		self._shift_is_momentary = OFFSET_SHIFT_IS_MOMENTARY

		self._scale_offset_component = ScrollingOffsetComponent(self._scale_offset_value)
		self._scale_offset_component._minimum = 0
		self._scale_offset_component._maximum = len(SCALES.keys())-1


	

	display_layer = forward_property('_display')('layer')

	def _setup_selected_session_control(self):
		self._selected_session = ScaleSessionComponent(1, 32, self)
		self._selected_session.name = "SelectedSession"
		self._selected_session.set_offsets(0, 0)	 
		#self._selected_session.set_stop_clip_value(STOP_CLIP)
		self._selected_scene = [None for index in range(32)]
		for row in range(32):
			self._selected_scene[row] = self._selected_session.scene(row)
			self._selected_scene[row].name = 'SelectedScene_' + str(row)
			clip_slot = self._selected_scene[row].clip_slot(0)
			clip_slot.name = 'Selected_Clip_Slot_' + str(row)
			#clip_slot.set_triggered_to_play_value(CLIP_TRG_PLAY)
			#clip_slot.set_triggered_to_record_value(CLIP_TRG_REC)
			#clip_slot.set_stopped_value(CLIP_STOP)
			#clip_slot.set_started_value(CLIP_STARTED)
			#clip_slot.set_recording_value(CLIP_RECORDING)
	

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
	

	def set_scales_toggle_button(self, button):
		assert(button is None or button.is_momentary())
		self._scales_modes.set_toggle_button(button)
	

	def set_button_matrix(self, matrix):
		if not matrix is self._matrix_value.subject:
			if self._matrix_value.subject:
				for button in self._matrix_value.subject:
					button.set_enabled(True)
					button.use_default_message()
			self._matrix_value.subject = matrix
		if self._matrix_value.subject:
			self._script.schedule_message(1, self.update)
	

	@subject_slot('value')
	def _matrix_value(self, value, x, y, *a, **k):
		self._script.log_message('monoscale grid in: ' + str(x) + ' ' + str(y) + ' ' + str(value))
		#pass
	

	def set_octave_up_button(self, button):
		self._octave_up_value.subject = button
		if button:
			button.turn_on()
	

	@subject_slot('value')
	def _octave_up_value(self, value):
		if value:
			self._offset_component.set_enabled(True)
			self._offset_component._shifted = True
			self._offset_component._scroll_up_value(1)
			self._offset_component._shifted = False
			self._offset_component.set_enabled(False)
	

	def set_octave_down_button(self, button):
		self._octave_down_value.subject = button
		if button:
			button.turn_on()
	

	@subject_slot('value')
	def _octave_down_value(self, value):
		if value:
			self._offset_component.set_enabled(True)
			self._offset_component._shifted = True
			self._offset_component._scroll_down_value(1)
			self._offset_component._shifted = False
			self._offset_component.set_enabled(False)
	

	def update(self):
		if not self.is_enabled():
			self._selected_session.deassign_all()
			self._script.set_highlighting_session_component(self._script._session)
			self._script._session._do_show_highlight()
	

	def _detect_instrument_type(self, track):
		scale = DEFAULT_AUTO_SCALE
		for device in track.devices:
			if isinstance(device, Live.Device.Device):
				self._script.log_message('device: ' + str(device.class_name))
				if device.class_name == 'DrumGroupDevice':
					scale = 'DrumPad'
					break
		return scale
	

	def _offset_value(self, offset):
		cur_track = self._script._mixer._selected_strip._track
		if cur_track.has_midi_input:
			cur_chan = cur_track.current_input_sub_routing
			if cur_chan in CHANNELS:
				cur_chan = (CHANNELS.index(cur_chan))+1
				scale = self._offsets[cur_chan]['scale']
				if scale is 'Auto':
					scale = self._detect_instrument_type(cur_track)
				if scale is 'DrumPad':
					old_offset = self._offsets[cur_chan]['drumoffset']
					self._offsets[cur_chan]['drumoffset'] = offset
					self._script.show_message('New drum root is ' + str(self._offsets[cur_chan]['drumoffset']))
					self._display.set_value_string(str(self._offsets[cur_chan]['drumoffset']), 3)
				else:
					self._offsets[cur_chan]['offset'] = offset
					self._script.show_message('New root is Note# ' + str(self._offsets[cur_chan]['offset']) + ', ' + str(NOTENAMES[self._offsets[cur_chan]['offset']]))
					self._display.set_value_string(str(self._offsets[cur_chan]['offset']) + ', ' + str(NOTENAMES[self._offsets[cur_chan]['offset']]), 3)
				self._assign_midi_layer()
	

	def _vertical_offset_value(self, offset):
		cur_track = self._script._mixer._selected_strip._track
		if cur_track.has_midi_input:
			cur_chan = cur_track.current_input_sub_routing
			if cur_chan in CHANNELS:
				cur_chan = (CHANNELS.index(cur_chan))+1
				self._offsets[cur_chan]['vertoffset'] = offset
				self._script.show_message('New vertical offset is ' + str(self._offsets[cur_chan]['vertoffset']))
				self._display.set_value_string(str(self._offsets[cur_chan]['vertoffset']), 1)
				self._assign_midi_layer()
	

	def _scale_offset_value(self, offset):
		cur_track = self._script._mixer._selected_strip._track
		if cur_track.has_midi_input:
			cur_chan = cur_track.current_input_sub_routing
			if cur_chan in CHANNELS:
				cur_chan = (CHANNELS.index(cur_chan))+1
				self._offsets[cur_chan]['scale'] = SCALENAMES[offset]
				self._script.show_message('New scale is ' + str(self._offsets[cur_chan]['scale']))
				self._display.set_value_string(str(self._offsets[cur_chan]['scale']), 2)
				if len(SCALES[self._offsets[cur_chan]['scale']])>8:
					self._offsets[cur_chan]['vert_offset'] = 8
				self._assign_midi_layer()
	

	def _split_mode_value(self, mode):
		cur_track = self._script._mixer._selected_strip._track
		if cur_track.has_midi_input:
			cur_chan = cur_track.current_input_sub_routing
			if cur_chan in CHANNELS:
				cur_chan = (CHANNELS.index(cur_chan))+1
				self._offsets[cur_chan]['split'] = bool(mode)
				self._display.set_value_string(str(bool(mode)), 0)
				self._assign_midi_layer()
	

	def _assign_midi_layer(self):
		cur_track = self._script.song().view.selected_track
		is_midi = False
		matrix = self._matrix_value.subject
		if cur_track.has_midi_input and not matrix is None:
			is_midi = True
			cur_chan = cur_track.current_input_sub_routing
			#self._script.log_message('cur_chan ' + str(cur_chan) + str(type(cur_chan)) + str(len(cur_chan)))
			if cur_chan in CHANNELS:
				cur_chan = (CHANNELS.index(cur_chan))+1
				offset, vertoffset, scale, split = self._offsets[cur_chan]['offset'], self._offsets[cur_chan]['vertoffset'], self._offsets[cur_chan]['scale'], self._offsets[cur_chan]['split']
				if scale is 'Auto':
					scale = self._detect_instrument_type(cur_track)
					#self._script.log_message('auto found: ' + str(scale))
				self._split_mode_selector._mode_index = int(self._offsets[cur_chan]['split'])
				self._split_mode_selector.update()
				self._vertical_offset_component._offset = self._offsets[cur_chan]['vertoffset']	
				self._vertical_offset_component.update()
				self._scale_offset_component._offset = SCALENAMES.index(self._offsets[cur_chan]['scale'])
				self._scale_offset_component.update()
				if scale is 'DrumPad':
					self._offset_component._offset = self._offsets[cur_chan]['drumoffset']
				else:
					self._offset_component._offset = self._offsets[cur_chan]['offset']	
				self._offset_component.update()
				if scale is 'Session':
					is_midi = False
				elif scale is 'Mod':
					is_midi = True
				elif scale in SPLIT_SCALES or split:
					#self._send_midi(SPLITBUTTONMODE)
					scale_len = len(SCALES[scale])
					for row in range(8):
						for column in range(4):
							button = matrix.get_button(column, row)
							if scale is 'DrumPad':
								button.set_identifier((DRUMNOTES[column + (row*8)] + (self._offsets[cur_chan]['drumoffset']*4))%127)
								button.scale_color = DRUMCOLORS[row<4]
								button.send_value(button.scale_color)
								self._offset_component._shifted_value = 3
							else:
								note_pos = column + (abs(7-row)*int(vertoffset))
								note =	offset + SCALES[scale][note_pos%scale_len] + (12*int(note_pos/scale_len))
								button.set_identifier(note%127)
								button.scale_color = KEYCOLORS[(note%12 in WHITEKEYS) + (((note_pos%scale_len)==0)*2)]
								button.send_value(button.scale_color)
								self._offset_component._shifted_value = 11
							button.set_enabled(False)
							button.set_channel(cur_chan)
							#self._selected_session.deassign_all()
							matrix = self._matrix_value.subject
							matrix.get_button(column + 4, row).use_default_message()
							matrix.get_button(column + 4, row).set_enabled(True)
							self._selected_scene[column+(row*4)].clip_slot(0).set_launch_button(matrix.get_button(column + 4, row))
					#self._selected_session.set_scene_bank_buttons(self._button[5], self._button[4])
					self._script.set_highlighting_session_component(self._selected_session)
					self._selected_session._do_show_highlight()
				else:
					#self._send_midi(MIDIBUTTONMODE)
					scale_len = len(SCALES[scale])
					for row in range(8):
						for column in range(8):
							button = matrix.get_button(column, row)
							if scale is 'DrumPad':
								button.set_identifier((DRUMNOTES[column + (row*8)] + (self._offsets[cur_chan]['drumoffset']*4))%127)
								button.scale_color = DRUMCOLORS[(column<4)+((row<4)*2)]
								button.send_value(button.scale_color)
								self._offset_component._shifted_value = 3
							else:
								note_pos = column + (abs(7-row)*vertoffset)
								note =	offset + SCALES[scale][note_pos%scale_len] + (12*int(note_pos/scale_len))
								button.set_identifier(note%127)
								button.scale_color = KEYCOLORS[(note%12 in WHITEKEYS) + (((note_pos%scale_len)==0)*2)]
								button.send_value(button.scale_color)
								self._offset_component._shifted_value = 11
							button.set_enabled(False)
							button.set_channel(cur_chan)
					self._selected_session.deassign_all()
					self._script.set_highlighting_session_component(self._script._session)
					self._script._session._do_show_highlight()
				#if not self._touchstrip is None:
				#	self._touchstrip.set_channel(cur_chan)
				self._display.set_value_string(str(bool(self._split_mode_selector._mode_index)), 0)
				self._display.set_value_string(str(self._offsets[cur_chan]['vertoffset']), 1)
				self._display.set_value_string(str(self._offsets[cur_chan]['scale']), 2)
				self._display.set_value_string(str(self._offsets[cur_chan]['offset']) + ', ' + str(NOTENAMES[self._offsets[cur_chan]['offset']]), 3)
			else:
				is_midi = False
			self._script.set_feedback_channels([])
		return is_midi	
	

	def _assign_midi_shift_layer(self):
		cur_track = self._script._mixer._selected_strip._track
		is_midi = False
		if cur_track.has_midi_input:
			#self._send_midi(LIVEBUTTONMODE)
			#if AUTO_ARM_SELECTED:
			#	if not cur_track.arm:
			#		self.schedule_message(1, self._arm_current_track, cur_track)
			is_midi = True
			cur_chan = cur_track.current_input_sub_routing
			if cur_chan in CHANNELS:
				cur_chan = (CHANNELS.index(cur_chan))+1
				scale = self._offsets[cur_chan]['scale']
				if scale is 'Auto':
					scale = self._detect_instrument_type(cur_track)
					#self.log_message('auto found: ' + str(scale))
				if scale is 'Session':
					is_midi = False
				elif scale is 'Mod':
					is_midi = True
				else:
					"""for button in self._touchpad[0:1]:
						button.set_on_off_values(SPLITMODE, 0)
					for button in self._touchpad[1:2]:
						button.set_on_off_values(OVERDUB, 0)
					self._transport.set_overdub_button(self._touchpad[1])
					self._split_mode_selector._mode_index = int(self._offsets[cur_chan]['split'])
					self._split_mode_selector.set_enabled(True)
					if not self._offsets[cur_chan]['scale'] is 'DrumPad':
						for button in self._touchpad[2:4]:
							button.set_on_off_values(VERTOFFSET, 0)
						self._vertical_offset_component._offset = self._offsets[cur_chan]['vertoffset']		
						self._vertical_offset_component.set_offset_change_buttons(self._touchpad[3], self._touchpad[2])
					for button in self._touchpad[4:6]:
						button.set_on_off_values(SCALEOFFSET, 0)
					self._scale_offset_component._offset = SCALENAMES.index(self._offsets[cur_chan]['scale'])
					self._scale_offset_component.set_offset_change_buttons(self._touchpad[5], self._touchpad[4])
					for button in self._touchpad[6:8]:
						button.set_on_off_values(OFFSET, 0)
					if scale is 'Auto':
						scale = self._detect_instrument_type(cur_track)
					if scale is 'DrumPad':
						self._offset_component._offset = self._offsets[cur_chan]['drumoffset']
					else:
						self._offset_component._offset = self._offsets[cur_chan]['offset']		
					self._offset_component.set_offset_change_buttons(self._touchpad[7], self._touchpad[6])"""
					is_midi = True
		return is_midi
	

	def update(self):
		if self.is_enabled() and self._button_matrix:
			self.
			cur_track = self._mixer._selected_strip._track
			is_midi = False
			scale, offset, vertoffset = ' ', ' ', ' '

			if cur_track.has_midi_input:
				if AUTO_ARM_SELECTED:
					if not cur_track.arm:
						self.schedule_message(1, self._arm_current_track, cur_track)
				is_midi = True
				cur_chan = cur_track.current_input_sub_routing
				#self.log_message('cur_chan ' + str(cur_chan) + str(type(cur_chan)) + str(len(cur_chan)))
				if len(cur_chan) == 0:
					cur_chan = 'All Channels'
				if cur_chan in CHANNELS:
					cur_chan = (CHANNELS.index(cur_chan)%15)+1

					offsets = self._current_device_offsets(self._offsets[cur_chan])

					offset, vertoffset, scale, split, sequencer = offsets['offset'], offsets['vertoffset'], offsets['scale'], offsets['split'], offsets['sequencer']
					if scale == 'Auto':
						scale = self._detect_instrument_type(cur_track)
						#self.log_message('auto found: ' + str(scale))
					elif scale in SPLIT_SCALES or split:
						#self._send_midi(SPLITBUTTONMODE)
						scale_len = len(SCALES[scale])
						if scale is 'DrumPad':
							for row in range(4):
								for column in range(4):
								#if scale is 'DrumPad':
									self._pad[column + (row*8)].set_identifier((DRUMNOTES[column + (row*8)] + (self._offsets[cur_chan]['drumoffset']*4))%127)
									self._pad[column + (row*8)].scale_color = DRUMCOLORS[0]
									#self._pad[column + (row*8)].send_value(DRUMCOLORS[column<4], True)
									self._pad[column + (row*8)].display_press = True
									self._pad[column + (row*8)].press_flash(0, True)
									self._pad_CC[column + (row*8)].set_identifier((DRUMNOTES[column + (row*8)] + (self._offsets[cur_chan]['drumoffset']*4))%127)
									#self._drumgroup.set_drum_matrix(self._drumpad_grid)
									self._offset_component._shifted_value = 3
									self._pad[column + (row*8)].set_enabled(False)
									self._pad[column + (row*8)].set_channel(cur_chan)
									self._pad[column + (row*8)]._descriptor = str(NOTENAMES[self._pad[column + (row*8)]._msg_identifier])
									if not sequencer:
										self._selected_scene[column+(row*4)].clip_slot(0).set_launch_button(self._pad[column + 4 + (row*8)])
						else:
							current_note = self._note_sequencer._note_editor.editing_note
							for row in range(2, 4):
								for column in range(8):
									note_pos = column + (abs(3-row)*int(vertoffset))
									note =	offset + SCALES[scale][note_pos%scale_len] + (12*int(note_pos/scale_len))
									self._pad[column + (row*8)].set_identifier(note%127)
									self._pad[column + (row*8)].scale_color = KEYCOLORS[(note%12 in WHITEKEYS) + (((note_pos%scale_len)==0)*2)]
									if note is current_note and sequencer:
										self._pad[column + (row*8)].scale_color = SELECTED_NOTE
									#self._pad[column + (row*8)].send_value(self._pad[column + (row*8)].scale_color, True)
									self._pad[column + (row*8)].display_press = True
									self._pad[column + (row*8)].press_flash(0, True)
									self._pad_CC[column + (row*8)].set_identifier(note%127)
									self._offset_component._shifted_value = 11
									self._pad[column + (row*8)].set_enabled(False)
									self._pad[column + (row*8)].set_channel(cur_chan)
									self._pad[column + (row*8)]._descriptor = str(NOTENAMES[self._pad[column + (row*8)]._msg_identifier])
									self._pad_CC[column + (row*8)].set_enabled(False)
									self._pad_CC[column + (row*8)].set_channel(cur_chan)
									#self._selected_session.deassign_all()
									if not sequencer:
										self._selected_scene[column+((row-2)*4)].clip_slot(0).set_launch_button(self._pad[column + ((row-2)*8)])
						#self._selected_session.set_scene_bank_buttons(self._button[5], self._button[4])
						if sequencer:
							self.set_feedback_channels(range(cur_chan, cur_chan+1))

							if scale is 'DrumPad':
								self.set_pad_translations(make_pad_translations(cur_chan))
								self._step_sequencer.set_playhead(self._playhead_element)
								self._step_sequencer._drum_group.set_select_button(self._button[self._layer])
								self._step_sequencer.set_button_matrix(self._base_grid.submatrix[4:8, :4])
								self._step_sequencer.set_drum_matrix(self._base_grid.submatrix[:4, :4])
								vals = [-1, -1, -1, -1, 0, 1, 2, 3, -1, -1, -1, -1, 4, 5, 6, 7, -1, -1, -1, -1, 8, 9, 10, 11, -1, -1, -1, -1, 12, 13, 14, 15]
								for x, pad in enumerate(self._pad):
									pad.display_press = False
									if vals[x]>-1:
										pad.set_channel(cur_chan)
										pad.set_identifier(vals[x])
									else:
										pad.set_identifier(vals[x+4]+16)
										pad.set_channel(cur_chan)


							else:
								#self.log_message('assign stuff to note sequencer')
								self._note_sequencer.set_playhead(self._playhead_element)
								self._note_sequencer.set_button_matrix(self._base_grid.submatrix[:8, :2])
								#vals = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, -1, 4, 5, 6, 7, -1, -1, -1, -1, 8, 9, 10, 11, -1, -1, -1, -1, 12, 13, 14, 15]
								for x, pad in enumerate(self._pad):
									pad.display_press = False
									if x<16:
										pad.set_channel(cur_chan)
										pad.set_identifier(x)
								self._on_note_matrix_pressed.subject = self._base_grid

							self.reset_controlled_track()

						else:
							self.set_highlighting_session_component(self._selected_session)
							self._selected_session._do_show_highlight()
					else:
						self._send_midi(MIDIBUTTONMODE)
						scale_len = len(SCALES[scale])
						for row in range(4):
							for column in range(8):
								if scale is 'DrumPad':
									self._pad[column + (row*8)].set_identifier((DRUMNOTES[column + (row*8)] + (self._offsets[cur_chan]['drumoffset']*4))%127)
									self._pad[column + (row*8)].scale_color = DRUMCOLORS[column<4]
									#self._pad[column + (row*8)].send_value(DRUMCOLORS[column<4], True)
									self._pad[column + (row*8)].display_press = True
									self._pad[column + (row*8)].press_flash(0, True)
									self._pad[column + (row*8)]._descriptor = str(NOTENAMES[self._pad[column + (row*8)]._msg_identifier])
									self._pad_CC[column + (row*8)].set_identifier((DRUMNOTES[column + (row*8)] + (self._offsets[cur_chan]['drumoffset']*4))%127)
									self._offset_component._shifted_value = 3
								else:
									note_pos = column + (abs(3-row)*vertoffset)
									note =	offset + SCALES[scale][note_pos%scale_len] + (12*int(note_pos/scale_len))
									self._pad[column + (row*8)].set_identifier(note%127)
									self._pad[column + (row*8)].scale_color = KEYCOLORS[(note%12 in WHITEKEYS) + (((note_pos%scale_len)==0)*2)]
									#self._pad[column + (row*8)].send_value(self._pad[column + (row*8)].scale_color, True)
									self._pad[column + (row*8)].display_press = True
									self._pad[column + (row*8)].press_flash(0, True)
									self._pad[column + (row*8)]._descriptor = str(NOTENAMES[self._pad[column + (row*8)]._msg_identifier])
									self._pad_CC[column + (row*8)].set_identifier(note%127)
									self._offset_component._shifted_value = 11
								self._pad[column + (row*8)].set_enabled(False)
								self._pad[column + (row*8)].set_channel(cur_chan)
								self._pad_CC[column + (row*8)].set_enabled(False)
								self._pad_CC[column + (row*8)].set_channel(cur_chan)
						#self._session.set_scene_bank_buttons(self._button[5], self._button[4])
						#self._session.set_track_bank_buttons(self._button[6], self._button[7])
					if self.pad_held():
						for index in range(len(self._last_pad_stream)):
							self._stream_pads[index].press_flash(self._last_pad_stream[index])
				else:
					is_midi = False

				#return is_midi	
	
	def assign_keypad(self, grid, scale):
		if grid and scale in SCALES:
			scale_len = len(SCALES[scale])
			height = grid.height()

			offset, vertoffset = offsets['offset'], offsets['vertoffset']

			for button, (x, y) in grid.iterbuttons():

				note_pos = x + (abs(height-y)*vertoffset)
				note = offset + SCALES[scale][note_pos%scale_len] + (12*int(note_pos/scale_len))
				button.set_identifier(note%127)
				button.scale_color = KEYCOLORS[(note%12 in WHITEKEYS) + (((note_pos%scale_len)==0)*2)]
				button.send_value(button.scale_color, True)

				#button.display_press = True
				#button.press_flash(0, True)
				#button._descriptor = str(NOTENAMES[self._pad[column + (row*8)]._msg_identifier])
				#button_CC.set_identifier(note%127)

				self._offset_component._shifted_value = 11
	

	def assign_drumpad(self, grid):
		if grid:
			height = grid.height()
			width = grid.width()
			offset, vertoffset = offsets['offset'], offsets['vertoffset']
			if (width, height) is (4, 4):
				self.set_feedback_channels(range(cur_chan, cur_chan+1))

				self.set_pad_translations(make_pad_translations(cur_chan))
				self._step_sequencer.set_playhead(self._playhead_element)
				#self._step_sequencer._drum_group.set_select_button(self._button[self._layer])
				#self._step_sequencer.set_button_matrix(self._base_grid.submatrix[4:8, :4])
				self._step_sequencer.set_drum_matrix(grid)
				for button, (x, y) in grid:

					button.set_identifier(vals[x+4]+16)
					button.set_channel(cur_chan)

					#pad.display_press = False

			else:
				for button, (x, y) in grid.iterbuttons():
					button.set_identifier((DRUMNOTES[column + (row*8)] + (self._offsets[cur_chan]['drumoffset']*4))%127)
					button.scale_color = DRUMCOLORS[column<4]
					button.send_value(DRUMCOLORS[column<4], True)

					#button.display_press = True
					#button.press_flash(0, True)
					#button._descriptor = str(NOTENAMES[self._pad[column + (row*8)]._msg_identifier])
					#button_CC.set_identifier((DRUMNOTES[column + (row*8)] + (self._offsets[cur_chan]['drumoffset']*4))%127)

					self._offset_component._shifted_value = 3
	




	@subject_slot('value')
	def on_selected_track_changed(self):
		track = self._script._mixer.selected_strip()._track
		track_list = []
		for t in self._script._mixer.tracks_to_use():
			track_list.append(t)
		if track in track_list:
			self._selected_session._track_offset = track_list.index(track)
		self._selected_session._reassign_tracks()
		self._selected_session._reassign_scenes()
		self.update()
	





