# by amounra 0513 : http://www.aumhaa.com

"""This is a collection of subclasses used to override MonoFramework elements during testing....they basically just remove 
the arguments from the specialty Mono Subclasses and pass the class over to the original Super that it was subclassing"""



from _Framework.ButtonElement import ButtonElement

from _Mono_Framework.MonomodComponent import MonomodComponent


class MonoButtonElement(ButtonElement):

	def __init__(self, is_momentary, msg_type, channel, identifier, name, cs, *a, **k):
		super(MonoButtonElement, self).__init__(is_momentary, msg_type, channel, identifier, *a, **k)
		#self.set_color_map(tuple([1, 1, 1, 1, 1, 1, 1]))
		self._script = cs
		self.name = name
	


class AumPCMonomodComponent(MonomodComponent):


	def __init__(self, *a, **k):
		super(AumPCMonomodComponent, self).__init__(*a, **k)
	

	def _set_shift_button(self, shift):
		self._script.log_message('set shift button ' + str(shift))
		super(AumPCMonomodComponent, self)._set_shift_button(shift)

	def _shift_value(self, value):
		self._shift_pressed = value != 0
		self._script.log_message('monomod shift value is ' + str(self._shift_pressed) + str(self.is_enabled()))
		self.update()
	

	def _update_grid(self, *a, **k):
		super(AumPCMonomodComponent, self)._update_grid(*a, **k)
		self._script.log_message('mod update grid')
	

	"""def _send_grid(self, column, row, value):
		super(AumPCMonomodComponent, self)._send_grid(column, row, value)
		self._script.log_message('send grid: ' + str(column) + ' ' + str(row) + ' ' + str(value))"""
	
