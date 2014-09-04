# by amounra 0714 : http://www.aumhaa.com

import Live 
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent 
from _Framework.SubjectSlot import SubjectEvent, subject_slot, subject_slot_group
from _Mono_Framework.Debug import *

debug = initialize_debug()

class ResetSendsComponent(ControlSurfaceComponent):
	' Special Component to reset all track sends to zero for the first four returns '
	__module__ = __name__


	def __init__(self, script, *a, **k):
		super(ResetSendsComponent, self).__init__(*a, **k)
		self._script = script
	

	def set_buttons(self, buttons):
		self._on_button_value.subject = buttons
		if buttons:
			for button, _ in buttons.iterbuttons():
				button and button.set_light('ResetSendsColor')
	

	def update(self):
		pass
	
	
	@subject_slot('value')
	def _on_button_value(self, value, x, y, *a, **k):
		if value:
			self._on_button_value.subject and self.reset_send(x)
	

	def reset_send(self, send_number):
		if send_number < len(self.returns_to_use()):
			for track in self.tracks_to_use():
				track.mixer_device.sends[send_number].value = 0
			for track in self.returns_to_use():
				track.mixer_device.sends[send_number].value = 0
	

	def tracks_to_use(self):
		return self.song().tracks
	

	def returns_to_use(self):
		return self.song().return_tracks
	

