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
	


from _Framework.SubjectSlot import subject_slot, subject_slot_group

class DescriptiveSubjectSlot(SubjectSlot):


	def connect(self):
		super(DescriptiveSubjectSlot, self).connect()
		self._notify_descriptor()
	

	def disconnect(self):
		super(DescriptiveSubjectSlot, self).disconnect()
		self._notify_descriptor()
	

	def soft_disconnect(self):
		super(DescriptiveSubjectSlot, self).soft_disconnect()
		self._notify_descriptor()
	

	def _notify_descriptor(self):
		debug('connecting:', self._subject, 'to', self._listener)
		if hasattr(self._subject, '_descriptor'):
			if self._subject:
				self._subject._descriptor = self._listener
	



def make_register_slot(original):
	def register_slot(*a, **k):
		debug('REGISTER SLOT:', *a, **k)
		if a and isinstance(a[0], SubjectSlot):
			slot = a[0]
			slot.connect = DescriptiveSubjectSlot.connect
			slot.disconnect = DescriptiveSubjectSlot.disconnect
			slot.soft_disconnect = DescriptiveSubjectSlot.soft_disconnect
			slot.notify_descriptor = DescriptiveSubjectSlot.notify_descriptor
		else:
			slot = DescriptiveSubjectSlot(*a, **k)
		original.register_disconnectable(slot)
		return slot
	return register_slot
	

"""def _setup_descriptors(self):
	debug('setup descriptors...')
	for component in self.components:
		if hasattr(component, '_registered_disconnectables'):
			debug('------------name:', component.name if hasattr(component, 'name') else component)
			for item in component._registered_disconnectables:
				item.register_slot = make_register_slot(item)
				debug('item:', item._listener if hasattr(item, '_listener') else item)"""

