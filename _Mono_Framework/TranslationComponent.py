from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.CompoundComponent import CompoundComponent
from _Framework.SubjectSlot import SubjectEvent, subject_slot, subject_slot_group

from Debug import *

debug = initialize_debug()

class TranslationComponent(CompoundComponent):


	def __init__(self, controls = [], user_channel_offset = 1, channel = 0, *a, **k):
		super(TranslationComponent, self).__init__()
		self._controls = controls
		self._user_channel_offset = user_channel_offset
		self._channel = channel or 0
		self._color = 0
	

	def set_controls(self, controls):
		self._controls = controls
	

	def add_control(self, control):
		if control:
			self._controls.append(control)
	

	def set_channel_selector_buttons(self, buttons):
		self._on_channel_seletor_button_value.subject = buttons
		self.update_channel_selector_buttons()
	

	def set_channel_selector_control(self, control):
		if self._on_channel_selector_control_value.subject:
			self._on_channel_selector_control_value.subject.send_value(0)
		self._on_channel_selector_control_value.subject = control
		self.update_channel_selector_control()
	

	def update_channel_selector_control(self):
		control = self._on_channel_selector_control_value.subject
		if control:
			chan_range = 14 - self._user_channel_offset
			value =  ((self._channel-self._user_channel_offset)*127)/chan_range
			control.send_value(  int(value)  )
	

	def update_channel_selector_buttons(self):
		buttons = self._on_channel_seletor_button_value.subject
		if buttons:
			for button, coords in buttons.iterbuttons():
				if button:
					channel = self._channel - self._user_channel_offset
					selected = coords[0] + (coords[1]*buttons.width())
					if channel == selected:
						button.turn_on()
					else:
						button.turn_off()
	

	@subject_slot('value')
	def _on_channel_selector_control_value(self, value, *a, **k):
		chan_range = 14 - self._user_channel_offset
		channel = int((value*chan_range)/127)+self._user_channel_offset
		if channel != self._channel:
			self._channel = channel
			self.update()
	

	@subject_slot('value')
	def _on_channel_seletor_button_value(self, value, x, y, *a, **k):
		if value:
			x = x + (y*self._on_channel_seletor_button_value.subject.width())
			self._channel = min(x+self._user_channel_offset, 14)
		self.update()
	

	def update(self):
		if self.is_enabled():
			for control in self._controls:
				if control:
					control.clear_send_cache()
					control.release_parameter()
					try:
						control.set_light('Translation.Channel_'+str(self._channel)+'.'+str(control.name))
					except:
						control.send_value(self._color, True)
					control.set_channel(self._channel)
					control.set_enabled(False)
		else:
			for control in self._controls:
				control and control.use_default_message() and control.set_enabled(True)
		self.update_channel_selector_buttons()
		self.update_channel_selector_control()
	
