# by amounra 0413 : http://www.aumhaa.com

import Live
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.ButtonElement import ButtonElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ModeSelectorComponent import ModeSelectorComponent
from _Framework.SubjectSlot import SubjectEvent, SubjectSlotGroup, subject_slot, subject_slot_group

from _Mono_Framework.MonoButtonElement import MonoButtonElement
#from re import *
import re

from _Mono_Framework.Debug import *

debug = initialize_debug()

DEVICE_COLORS = {'midi_effect':2,
				'audio_effect':5,
				'instrument':3,
				'Operator':4,
				'DrumGroupDevice':6,
				'MxDeviceMidiEffect':2,
				'MxDeviceInstrument':3,
				'MxDeviceAudioEffect':5,
				'InstrumentGroupDevice':3,
				'MidiEffectGroupDevice':2,
				'AudioEffectGroupDevice':5}

SELECTED_COLORSHIFT = 7

class DeviceSelectorComponent(ModeSelectorComponent):


	def __init__(self, script, *a, **k):
		super(DeviceSelectorComponent, self).__init__(*a, **k)
		self._script = script
		self._mode_index = 0
		self._number_of_modes = 0
		self._offset = 0
		self._buttons = None
		self._last_preset = 0
		self._device_colors = DEVICE_COLORS
		self._selected_colorshift = SELECTED_COLORSHIFT
	

	def set_offset(self, offset = 0):
		assert isinstance(offset, int)
		self._offset = offset
		self.update()
	

	def assign_buttons(self, buttons, offset = 0):
		assert isinstance(offset, int)
		self._offset = offset
		if(buttons != None):
			for button in buttons:
				assert isinstance(button, MonoButtonElement)
			self._buttons = buttons
		self.update()
	

	def set_mode_buttons(self, buttons):
		for button in self._modes_buttons:
			button.remove_value_listener(self._mode_value)
		self._modes_buttons = []
		if (buttons != None):
			for button in buttons:
				assert isinstance(button, ButtonElement or MonoButtonElement)
				identify_sender = True
				button.add_value_listener(self._mode_value, identify_sender)
				self._modes_buttons.append(button)
				self._number_of_modes = len(self._modes_buttons) + self._offset
			for index in range(len(self._modes_buttons)):
				if (index + self._offset) == self._last_preset:
					self._modes_buttons[index].turn_on()
				else:
					self._modes_buttons[index].turn_off()
	

	def set_mode_toggle(self, button):
		assert ((button == None) or isinstance(button, ButtonElement or MonoButtonElement))
		if (self._mode_toggle != None):
			self._mode_toggle.remove_value_listener(self._toggle_value)
		self._mode_toggle = button
		if (self._mode_toggle != None):
			self._mode_toggle.add_value_listener(self._toggle_value)
	

	def number_of_modes(self):
		return self._number_of_modes
	
		
	def update(self):
		if(self.is_enabled() is False):
			self.set_mode_buttons(None)
		elif(self.is_enabled() is True):
			if(len(self._modes_buttons) is 0):
				self.set_mode_buttons(self._buttons)
				#self.set_mode_buttons(tuple(self._script._grid[index][5] for index in range(8)))
				#self.set_mode_buttons(self._modes_buttons
		key = str('p'+ str(self._mode_index + 1 + self._offset))
		preset = None

		for track in range(len(self.song().tracks)):
			#self._script.log_message(self.enumerate_track_device(self.song().tracks[track]))
			for device in self.enumerate_track_device(self.song().tracks[track]):
				if(match(key, str(device.name)) != None):
					preset = device
		for return_track in range(len(self.song().return_tracks)):
			for device in self.enumerate_track_device(self.song().return_tracks[return_track]):
				if(match(key, str(device)) != None):
					preset = device
		for device in self.enumerate_track_device(self.song().master_track.devices):
			if(match(key, str(device)) != None):
				preset = device
		if(preset != None):
			#self._script._device.set_device(preset)
			self._script.set_appointed_device(preset)
			self._last_preset = self._mode_index + self._offset
		#self._script._device._update()	
		for index in range(len(self._modes_buttons)):
			button = self._modes_buttons[button]
			if isinstance(button, ButtonElement):
				if (index + self._offset) == self._last_preset:
					self._modes_buttons[button].turn_on()
				else:
					self._modes_buttons[button].turn_off()
	

	def enumerate_track_device(self, track):
		devices = []
		if hasattr(track, 'devices'):
			for device in track.devices:
				devices.append(device)
				if device.can_have_chains:
					for chain in device.chains:
						for chain_device in self.enumerate_track_device(chain):
							devices.append(chain_device)
		return devices
	

	def on_enabled_changed(self):
		if(self.is_enabled() is False):
			self.set_mode_buttons(None)
		elif(self.is_enabled() is True):
			if(len(self._modes_buttons) is 0):
				self.set_mode_buttons(self._buttons)
				#self.set_mode_buttons(tuple(self._script._grid[index][5] for index in range(8)))
		for button in range(len(self._modes_buttons)):
			if (button + self._offset) == self._last_preset:
				self._modes_buttons[button].turn_on()
			else:
				self._modes_buttons[button].turn_off()
	


class NewDeviceSelectorComponent(ControlSurfaceComponent):


	def __init__(self, script, prefix = '@d', *a, **k):
		super(NewDeviceSelectorComponent, self).__init__(*a, **k)
		self.log_message = script.log_message
		self._script = script
		self._prefix = prefix
		self._offset = 0
		self._buttons = []
		self._device_registry = []
		self._watched_device = None
		self._device_colors = DEVICE_COLORS
		self._selected_colorshift = SELECTED_COLORSHIFT
		self._device_listener.subject = self.song()
		self._device_listener()
	

	def disconnect(self, *a, **k):
		super(NewDeviceSelectorComponent, self).disconnect()
	

	def set_offset(self, offset):
		self._offset = offset
		self.update()
	

	def set_matrix(self, matrix):
		buttons = []
		if not matrix is None:
			for button, address in matrix.iterbuttons():
				#self._script.log_message('button is: ' + str(button))
				if not button is None:
					button.use_default_message()
					button.set_enabled(True)
					buttons.append(button)
		self.set_buttons(buttons)
	

	def set_buttons(self, buttons):
		self._buttons = buttons or []
		self._on_button_value.replace_subjects(self._buttons)
		self.update()
	

	def set_assign_button(self, button):
		debug('set assign button:', button)
		self._on_assign_button_value.subject = button
		self._update_assign_button()
	

	@subject_slot('value')
	def _on_assign_button_value(self, value):
		debug('device_selector._on_assign_button_value', value)
		self._update_assign_button()
	

	def _update_assign_button(self):
		button = self._on_assign_button_value.subject
		if button:
			button.is_pressed() and button.set_light('DeviceSelector.AssignOn') or button.set_light('DeviceSelector.AssignOff')
	

	@subject_slot_group('value')
	def _on_button_value(self, value, sender):
		if self.is_enabled():
			if value:
				if self._on_assign_button_value.subject and self._on_assign_button_value.subject.is_pressed():
					self.assign_device(self._buttons.index(sender))
				else:
					self.select_device(self._buttons.index(sender))
	

	def assign_device(self, index):
		device = self.song().appointed_device
		if not device is None and hasattr(device, 'name'):
			prefix = str(self._prefix)+':'
			offset = self._offset
			key =  prefix + str(index + 1 + offset)
			name = device.name.split(' ')
			if key in name:
				name.remove(key)
			else:
				old_entry = self._device_registry[index]
				if old_entry and hasattr(old_entry, 'name'):
					old_name = old_entry.name.split(' ')
					if key in old_name:
						old_name.remove(key)
						old_entry.name = ' '.join(old_name)
				for sub in name:
					sub.startswith(prefix) and name.remove(sub)
				name.insert(0, key)
			device.name = ' '.join(name)
			self.scan_all()
			self.update()
	

	def select_device(self, index):
		if self.is_enabled():
			preset = None
			if index < len(self._device_registry):
				preset = self._device_registry[index] 
			if not preset is None and isinstance(preset, Live.Device.Device):
				self.song().view.select_device(preset)
				self._script.set_appointed_device(preset)
				try:
					self._script.monomodular.is_mod(preset) and self._script.modhandler.select_mod(self._script.monomodular.is_mod(preset))
				except:
					pass
			self.update()
	

	def scan_all(self):
		debug('scan all--------------------------------')
		self._device_registry = [None for index in range(len(self._buttons))]
		prefix = str(self._prefix)+':'
		offset = self._offset
		preset = None
		for track in self.song().tracks:
			for device in self.enumerate_track_device(track):
				for index, entry in enumerate(self._device_registry):
					key = str(prefix + str(index + 1 + offset))
					if device.name.startswith(key+' ') or device.name == key:
						self._device_registry[index] = device
					elif (device.name.startswith('*' +key+' ') or device.name == ('*' +key)) and device.can_have_chains and len(device.chains) and len(device.chains[0].devices):
						self._device_registry[index] = device.chains[0].devices[0]
		for return_track in self.song().return_tracks:
			for device in self.enumerate_track_device(return_track):
				for index, entry in enumerate(self._device_registry):
					key = str(prefix + str(index + 1 + offset))
					if device.name.startswith(key+' ') or device.name == key:
						self._device_registry[index] = device
					elif (device.name.startswith('*' +key+' ') or device.name == ('*' +key))  and device.can_have_chains and len(device.chains) and len(device.chains[0].devices):
						self._device_registry[index] = device.chains[0].devices[0]
		for device in self.enumerate_track_device(self.song().master_track):
			for index, entry in enumerate(self._device_registry):
				key = str(prefix + str(index + 1 + offset))
				if device.name.startswith(key+' ') or device.name == key:
					self._device_registry[index] = device
				elif (device.name.startswith('*' +key+' ') or device.name == ('*' +key))  and device.can_have_chains and len(device.chains) and len(device.chains[0].devices):
					self._device_registry[index] = device.chains[0].devices[0]
		self.update()
		#debug('device registry: ' + str(self._device_registry))
	

	def enumerate_track_device(self, track):
		devices = []
		if hasattr(track, 'devices'):
			for device in track.devices:
				devices.append(device)
				if device.can_have_chains:
					for chain in device.chains:
						for chain_device in self.enumerate_track_device(chain):
							devices.append(chain_device)
		return devices
	

	@subject_slot('appointed_device')
	def _device_listener(self, *a, **k):
		#debug('device_listener')
		self._on_name_changed.subject = self.song().appointed_device
		self._watched_device = self.song().appointed_device
		if self.is_enabled():
			self.update()
	

	@subject_slot('name')
	def _on_name_changed(self):
		#debug('on name changed')
		if self._watched_device == self.song().appointed_device:
			self.scan_all()
	

	def on_enabled_changed(self):
		if self.is_enabled():
			self.update()
	

	def update(self):
		if self.is_enabled():
			if len(self._device_registry) != len(self._buttons):
				self.scan_all()
			name = 'None'
			dev = self.song().appointed_device
			offset = self._offset
			if self._buttons:
				for index in range(len(self._buttons)):
					preset = self._device_registry[index]
					button = self._buttons[index]
					if isinstance(button, ButtonElement):
						if isinstance(preset, Live.Device.Device) and hasattr(preset, 'name'):
							name = preset.name
							dev_type = preset.type
							dev_class = preset.class_name
							val = (dev_class in self._device_colors and self._device_colors[dev_class]) or (dev_type in self._device_colors and self._device_colors[dev_type]) or 7
							selected_shift = (dev == preset)*self._selected_colorshift
							button.send_value(val + selected_shift)
						else:
							button.send_value(0)
	

