# by amounra 0915 : http://www.aumhaa.com

import Live
from ableton.v2.control_surface.component import Component
from ableton.v2.base.slot import listens, listens_group

from aumhaa.v2.base.debug import initialize_debug

debug = initialize_debug()

class DeviceNavigator(Component):
	__module__ = __name__
	__doc__ = ' Component that can navigate devices and chains '


	def __init__(self, device_provider, mixer, script, name = None):
		super(DeviceNavigator, self).__init__()
		if name:
			self.name = name
		self._device = device_provider
		self._mixer = mixer
		self._script = script
		self._on_device_changed.subject = self.song
		self._device_color_on = 'DefaultButton.On'
		self._device_color_off = 'DefaultButton.Off'
		self._chain_color_on = 'DefaultButton.On'
		self._chain_color_off = 'DefaultButton.Off'
		self._level_color_on = 'DefaultButton.On'
		self._level_color_off = 'DefaultButton.Off'
	

	def deassign_all(self):
		self.set_nav_buttons(None, None)
		self.set_layer_buttons(None, None)
		self.set_chain_nav_buttons(None, None)
	

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
		if(type(obj.canonical_parent) == type(self.song.tracks[0])):
			return obj.canonical_parent
		elif(type(obj.canonical_parent)==type(None)) or (type(obj.canonical_parent)==type(self.song)):
			return None
		else:
			return self.find_track(obj.canonical_parent)
	

	def _get_track(self):
			track = self._mixer._selected_strip._track
			if self._device.device and isinstance(self._device.device.canonical_parent, Live.Chain.Chain):
				track = self._device.device.canonical_parent
			return track
	

	@listens('value')
	def _on_prev_value(self, value):
		if value:
			track = self._get_track()
			if track and self._device.device and self._device.device in track.devices:
				if isinstance(track, Live.Chain.Chain) and [device for device in track.devices].index(self._device.device) is 0:
					self._on_exit_value(1)
				else:
					device = track.devices[min(len(track.devices)-1, max(0, [item for item in track.devices].index(self._device.device)-1))]
					#temp #self._script.set_appointed_device(device)
					self.song.view.select_device(device)
	

	@listens('value')
	def _on_next_value(self, value):
		if value:
			track = self._get_track()
			if track and self._device.device and self._device.device in track.devices:
				if self._device.device.can_have_chains and [device for device in track.devices].index(self._device.device) == (len(track.devices)-1):
					self._on_enter_value(1)
				else:
					device = track.devices[min(len(track.devices)-1, max(0, [item for item in track.devices].index(self._device.device)+1))]
					#self._script.set_appointed_device(device)
					self.song.view.select_device(device)
	

	@listens('value')
	def _on_device_select_dial_value(self, value):
		#debug('_on_scene_bank_dial_value', value)
		if value > 64:
			self._on_prev_value(1)
		else:
			self._on_next_value(1)
	

	@listens('value')
	def _on_prev_chain_value(self, value):
		if value:
			track = self._mixer.selected_strip()._track
			if track and self._device.device and isinstance(self._device.device.canonical_parent, Live.Chain.Chain):
				parent_chain = self._device.device.canonical_parent
				parent = parent_chain.canonical_parent
				new_chain_index = min(len(parent.chains)-1, max(0, [item for item in parent.chains].index(parent_chain)-1))
				device = parent.chains[new_chain_index].devices[0] if len(parent.chains[new_chain_index].devices) else None
				if device:
					#self._script.set_appointed_device(device)
					self.song.view.select_device(device)
	

	@listens('value')
	def _on_next_chain_value(self, value):
		if value:
			track = self._mixer.selected_strip()._track
			if track and self._device.device and isinstance(self._device.device.canonical_parent, Live.Chain.Chain):
				parent_chain = self._device.device.canonical_parent
				parent = parent_chain.canonical_parent
				new_chain_index = min(len(parent.chains)-1, max(0, [item for item in parent.chains].index(parent_chain)+1))
				device = parent.chains[new_chain_index].devices[0] if len(parent.chains[new_chain_index].devices) else None
				if device:
					#self._script.set_appointed_device(device)
					self.song.view.select_device(device)
	

	@listens('value')
	def _on_enter_value(self, value):
		#debug('enter: ' + str(value) + ' ; ' + str(self._device.device.can_have_chains) + ' ' + str(len(self._device.device.chains)))
		if value:
			if self._device.device and self._device.device.can_have_chains and len(self._device.device.chains):
				device = self._device.device.chains[0].devices[0]
				#self._script.set_appointed_device(device)
				self.song.view.select_device(device)
	

	@listens('value')
	def _on_exit_value(self, value):
		#debug('exit: ' + str(value) + ' ; ' + str(self._device.device.canonical_parent) + ' ' + str(isinstance(self._device.device.canonical_parent, Live.Chain.Chain)))
		if value:
			if self._device.device and self._device.device.canonical_parent and isinstance(self._device.device.canonical_parent, Live.Chain.Chain):
				device = self._device.device.canonical_parent.canonical_parent
				#self._script.set_appointed_device(device)
				self.song.view.select_device(device)
	

	@listens('appointed_device')
	def _on_device_changed(self, *a, **k):
		self._script.schedule_message(1, self.update)
	

	def update(self):
		#debug('updating device navigator')
		track = self._get_track()
		if track != None:
			if not self._on_prev_value.subject is None:
				if self._device.device and len(track.devices)>0 and self._device.device in track.devices and [t for t in track.devices].index(self._device.device)>0:
					self._on_prev_value.subject.set_light(self._device_color_on)
				else:
					self._on_prev_value.subject.set_light(self._device_color_off)
			if not self._on_next_value.subject is None:
				if self._device.device and len(track.devices)>0 and self._device.device in track.devices and [t for t in track.devices].index(self._device.device)<(len(track.devices)-1):
					self._on_next_value.subject.set_light(self._device_color_on)
				else:
					self._on_next_value.subject.set_light(self._device_color_off)
			if not self._on_prev_chain_value.subject is None:
				if self._device.device and isinstance(self._device.device.canonical_parent, Live.Chain.Chain):
					parent_chain = self._device.device.canonical_parent
					parent = parent_chain.canonical_parent
					if len(parent.chains)>0 and parent_chain in parent.chains and [c for c in parent.chains].index(parent_chain)>0:
						self._on_prev_chain_value.subject.set_light(self._chain_color_on)
					else:
						self._on_prev_chain_value.subject.set_light(self._chain_color_off)
			if not self._on_next_chain_value.subject is None:
				if self._device.device and isinstance(self._device.device.canonical_parent, Live.Chain.Chain):
					parent_chain = self._device.device.canonical_parent
					parent = parent_chain.canonical_parent
					if len(parent.chains)>0 and parent_chain in parent.chains and [c for c in parent.chains].index(parent_chain)<(len(parent.chains)-1):
						self._on_next_chain_value.subject.set_light(self._chain_color_on)
					else:
						self._on_next_chain_value.subject.set_light(self._chain_color_off)
			if not self._on_enter_value.subject is None:
				if self._device.device and self._device.device.can_have_chains and len(self._device.device.chains):
					self._on_enter_value.subject.set_light(self._level_color_on)
				else:
					self._on_enter_value.subject.set_light(self._level_color_off)
			if not self._on_exit_value.subject is None:
				if self._device.device and self._device.device.canonical_parent and isinstance(self._device.device.canonical_parent, Live.Chain.Chain):
					self._on_exit_value.subject.set_light(self._level_color_on)
				else:
					self._on_exit_value.subject.set_light(self._level_color_off)
	

	def disconnect(self):
		super(DeviceNavigator, self).disconnect()
	

