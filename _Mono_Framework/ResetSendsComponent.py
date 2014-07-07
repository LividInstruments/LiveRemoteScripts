# by amounra 0413 : http://www.aumhaa.com

import Live 
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent 
from _Framework.ButtonElement import ButtonElement
from _Mono_Framework.MonoButtonElement import MonoButtonElement

class ResetSendsComponent(ControlSurfaceComponent):
	' Special Component to reset all track sends to zero for the first four returns '
	__module__ = __name__


	def __init__(self, script, *a, **k):
		super(ResetSendsComponent, self).__init__(*a, **k)
		self._script = script
		self._buttons = [None, None, None, None]
	

	def disconnect(self):
		if (self._buttons != None):
			for button in self._buttons:
				if (button != None):
					button.remove_value_listener(self.reset_send)
		self._buttons = []
	

	def on_enabled_changed(self):
		self.update()
	

	def set_buttons(self, buttons):
		assert isinstance(buttons, tuple)
		assert (len(buttons) is 4)
		for button in buttons:
			assert isinstance(button, ButtonElement) or (button == None)
		for button in self._buttons:
			if (button != None):
				button.remove_value_listener(self.reset_send)
		self._buttons = []
		for button in buttons:
			if (button != None):
				button.add_value_listener(self.reset_send, identify_sender = True)
			self._buttons.append(button)
	

	def update(self):
		#debug_print('update is abstract. Forgot to override it?')
		pass
	

	"""this method is used in CNTRLR, it resets all sends on a track instead of all sends related to a return"""
	"""def reset_send(self, value, sender):
		assert (self._buttons != None)
		assert isinstance(value, int)
		tracks = self.tracks_to_use()
		#returns = self.returns_to_use()
		if ((not value is 0) or (not sender.is_momentary())):
			for index in range(len(self._script._mixer.channel_strip(self._buttons.index(sender))._send_controls)):
				if self._script._mixer.channel_strip(self._buttons.index(sender))._send_controls[index].mapped_parameter()!=None:
					self._script._mixer.channel_strip(self._buttons.index(sender))._send_controls[index].mapped_parameter().value = 0
	"""
	

	def reset_send(self, value, sender):
		assert (self._buttons != None)
		assert isinstance(value, int)
		tracks = self.tracks_to_use()
		returns = self.returns_to_use()
		if ((value is not 0) or (not sender.is_momentary())):
			for index in range(4):
				if (index < len(returns)):
					if sender is self._buttons[index]:
						for track in tracks:
							track.mixer_device.sends[index].value = 0
						for track in returns:
							track.mixer_device.sends[index].value = 0
	

	def tracks_to_use(self):
		return self.song().tracks
	

	def returns_to_use(self):
		return self.song().return_tracks
	



