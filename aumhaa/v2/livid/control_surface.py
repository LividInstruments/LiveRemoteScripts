# by amounra 0216 : http://www.aumhaa.com

from __future__ import absolute_import, print_function
import Live
import math
import sys

import logging
logger = logging.getLogger(__name__)

from ableton.v2.control_surface.profile import profile
from ableton.v2.control_surface.control_surface import *
from ableton.v2.control_surface.input_control_element import InputControlElement, MIDI_CC_TYPE, MIDI_NOTE_TYPE, MIDI_PB_TYPE, MIDI_SYSEX_TYPE

from aumhaa.v2.control_surface.elements import MonoButtonElement

class LividControlSurface(ControlSurface):


	_rgb = 0
	_color_type = 'OhmRGB'
	_timer = 0
	_touched = 0
	flash_status = 1

	def __init__(self, *a, **k):
		self.log_message = logger.info
		super(LividControlSurface, self).__init__(*a, **k)
	

	def set_appointed_device(self, device):
		self.song.appointed_device = device
	

	def flash(self):
		if(self.flash_status > 0):
			for control in self.controls:
				if isinstance(control, MonoButtonElement):
					control.flash(self._timer)
	

	def update_display(self):
		super(LividControlSurface, self).update_display()
		self._timer = (self._timer + 1) % 256
		self.flash()
	

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
		
	

	def process_midi_bytes(self, midi_bytes, midi_processor):
		if midi.is_sysex(midi_bytes):
			result = self.get_registry_entry_for_sysex_midi_message(midi_bytes)
			if result is not None:
				identifier, recipient = result
				midi_processor(recipient, midi_bytes[len(identifier):-1])
			else:
				try:
					self.handle_sysex(midi_bytes)
				except:
					pass
		else:
			recipient = self.get_recipient_for_nonsysex_midi_message(midi_bytes)
			if recipient is not None:
				midi_processor(recipient, midi.extract_value(midi_bytes))
			else:
				logger.warning('Got unknown message: ' + midi.pretty_print_bytes(midi_bytes))
	




