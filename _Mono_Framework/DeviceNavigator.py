import Live
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.SubjectSlot import subject_slot, subject_slot_group
from _Mono_Framework.Debug import *

debug = initialize_debug()

class DeviceNavigator(ControlSurfaceComponent):
	__module__ = __name__
	__doc__ = ' Component that can navigate devices and chains '


	def __init__(self, device_component, mixer, script):
		super(DeviceNavigator, self).__init__()
		self._device = device_component
		self._mixer = mixer
		self._script = script
		self._on_device_changed.subject = self.song()
		self._device_color_on = 4
		self._device_color_off = 0
		self._chain_color_on = 5
		self._chain_color_off = 0
		self._level_color_on = 3
		self._level_color_off = 0
	

	def deassign_all(self):
		self.set_nav_buttons(None, None)
		self.set_layer_buttons(None, None)
		self.set_chain_nav_buttons(None, None)
	

	def set_nav_buttons(self, prev_button, next_button):
		#debug('set nav: ' + str(prev_button) + ' ' + str(next_button))
		identify_sender = True
		if self._prev_button != None:
			if self._prev_button.value_has_listener(self._nav_value):
				self._prev_button.remove_value_listener(self._nav_value)
		self._prev_button = prev_button
		if self._prev_button != None:
			self._prev_button.add_value_listener(self._nav_value, identify_sender)
		if self._next_button != None:
			if self._next_button.value_has_listener(self._nav_value):
				self._next_button.remove_value_listener(self._nav_value)
		self._next_button = next_button
		if self._next_button != None:
			self._next_button.add_value_listener(self._nav_value, identify_sender)
		self.update()
		return None
	

	def set_prev_button(self, button):
		self._on_prev_value.subject = button
		self._on_device_changed()
	

	def set_next_button(self, button):
		self._on_next_value.subject = button
		self._on_device_changed()
	

	def set_prev_chain_button(self, button):
		self._on_prev_chain_value.subject = button
		self._on_device_changed()
	

	def set_next_chain_button(self, button):
		self._on_next_chain_value.subject = button
		self._on_device_changed()
	

	def set_enter_button(self, button):
		self._on_enter_value.subject = button
		self._on_device_changed()
	

	def set_exit_button(self, button):
		self._on_exit_value.subject = button
		self._on_device_changed()
	

	def set_device_select_dial(self, dial):
		self._on_device_select_dial_value.subject = dial
	

	def _find_track(self, obj):
		if(type(obj.canonical_parent) == type(self.song().tracks[0])):
			return obj.canonical_parent
		elif(type(obj.canonical_parent)==type(None)) or (type(obj.canonical_parent)==type(self.song())):
			return None
		else:
			return self.find_track(obj.canonical_parent)
	

	def _get_track(self):
			track = self._mixer._selected_strip._track
			if self._device._device and isinstance(self._device._device.canonical_parent, Live.Chain.Chain):
				track = self._device._device.canonical_parent
			return track
	

	@subject_slot('value')
	def _on_prev_value(self, value):
		if value:
			track = self._get_track()
			if track and self._device._device and self._device._device in track.devices:
				if isinstance(track, Live.Chain.Chain) and [device for device in track.devices].index(self._device._device) is 0:
					self._on_exit_value(1)
				else:
					device = track.devices[min(len(track.devices)-1, max(0, [item for item in track.devices].index(self._device._device)-1))]
					self._script.set_appointed_device(device)
					self.song().view.select_device(device)
	

	@subject_slot('value')
	def _on_next_value(self, value):
		if value:
			track = self._get_track()
			if track and self._device._device and self._device._device in track.devices:
				if self._device._device.can_have_chains and [device for device in track.devices].index(self._device._device) == (len(track.devices)-1):
					self._on_enter_value(1)
				else:
					device = track.devices[min(len(track.devices)-1, max(0, [item for item in track.devices].index(self._device._device)+1))]
					self._script.set_appointed_device(device)
					self.song().view.select_device(device)
	

	@subject_slot('value')
	def _on_device_select_dial_value(self, value):
		#debug('_on_scene_bank_dial_value', value)
		if value > 64:
			self._on_prev_value(1)
		else:
			self._on_next_value(1)
	

	@subject_slot('value')
	def _on_prev_chain_value(self, value):
		if value:
			track = self._mixer.selected_strip()._track
			if track and self._device._device and isinstance(self._device._device.canonical_parent, Live.Chain.Chain):
				parent_chain = self._device._device.canonical_parent
				parent = parent_chain.canonical_parent
				new_chain_index = min(len(parent.chains)-1, max(0, [item for item in parent.chains].index(parent_chain)-1))
				device = parent.chains[new_chain_index].devices[0] if len(parent.chains[new_chain_index].devices) else None
				if device:
					self._script.set_appointed_device(device)
					self.song().view.select_device(device)
	

	@subject_slot('value')
	def _on_next_chain_value(self, value):
		if value:
			track = self._mixer.selected_strip()._track
			if track and self._device._device and isinstance(self._device._device.canonical_parent, Live.Chain.Chain):
				parent_chain = self._device._device.canonical_parent
				parent = parent_chain.canonical_parent
				new_chain_index = min(len(parent.chains)-1, max(0, [item for item in parent.chains].index(parent_chain)+1))
				device = parent.chains[new_chain_index].devices[0] if len(parent.chains[new_chain_index].devices) else None
				if device:
					self._script.set_appointed_device(device)
					self.song().view.select_device(device)
	

	@subject_slot('value')
	def _on_enter_value(self, value):
		#debug('enter: ' + str(value) + ' ; ' + str(self._device._device.can_have_chains) + ' ' + str(len(self._device._device.chains)))
		if value:
			if self._device._device and self._device._device.can_have_chains and len(self._device._device.chains):
				device = self._device._device.chains[0].devices[0]
				self._script.set_appointed_device(device)
				self.song().view.select_device(device)
	

	@subject_slot('value')
	def _on_exit_value(self, value):
		#debug('exit: ' + str(value) + ' ; ' + str(self._device._device.canonical_parent) + ' ' + str(isinstance(self._device._device.canonical_parent, Live.Chain.Chain)))
		if value:
			if self._device._device and self._device._device.canonical_parent and isinstance(self._device._device.canonical_parent, Live.Chain.Chain):
				device = self._device._device.canonical_parent.canonical_parent
				self._script.set_appointed_device(device)
				self.song().view.select_device(device)
	

	@subject_slot('appointed_device')
	def _on_device_changed(self, *a, **k):
		self._script.schedule_message(1, self.update)
	

	def update(self):
		#debug('updating device navigator')
		track = self._get_track()
		if track != None:
			if not self._on_prev_value.subject is None:
				if self._device._device and len(track.devices)>0 and self._device._device in track.devices and [t for t in track.devices].index(self._device._device)>0:
					self._on_prev_value.subject.send_value(self._device_color_on, True)
				else:
					self._on_prev_value.subject.send_value(self._device_color_off, True)
			if not self._on_next_value.subject is None:
				if self._device._device and len(track.devices)>0 and self._device._device in track.devices and [t for t in track.devices].index(self._device._device)<(len(track.devices)-1):
					self._on_next_value.subject.send_value(self._device_color_on, True)
				else:
					self._on_next_value.subject.send_value(self._device_color_off, True)
			if not self._on_prev_chain_value.subject is None:
				if self._device._device and isinstance(self._device._device.canonical_parent, Live.Chain.Chain):
					parent_chain = self._device._device.canonical_parent
					parent = parent_chain.canonical_parent
					if len(parent.chains)>0 and parent_chain in parent.chains and [c for c in parent.chains].index(parent_chain)>0:
						self._on_prev_chain_value.subject.turn_on()
					else:
						self._on_prev_chain_value.subject.turn_off()
			if not self._on_next_chain_value.subject is None:
				if self._device._device and isinstance(self._device._device.canonical_parent, Live.Chain.Chain):
					parent_chain = self._device._device.canonical_parent
					parent = parent_chain.canonical_parent
					if len(parent.chains)>0 and parent_chain in parent.chains and [c for c in parent.chains].index(parent_chain)<(len(parent.chains)-1):
						self._on_next_chain_value.subject.turn_on()
					else:
						self._on_next_chain_value.subject.turn_off()
			if not self._on_enter_value.subject is None:
				if self._device._device and self._device._device.can_have_chains and len(self._device._device.chains):
					self._on_enter_value.subject.turn_on()
				else:
					self._on_enter_value.subject.turn_off()
			if not self._on_exit_value.subject is None:
				if self._device._device and self._device._device.canonical_parent and isinstance(self._device._device.canonical_parent, Live.Chain.Chain):
					self._on_exit_value.subject.turn_on()
				else:
					self._on_exit_value.subject.turn_off()
	

	def disconnect(self):
		super(DeviceNavigator, self).disconnect()
	

