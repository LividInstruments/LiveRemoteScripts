# by amounra 0413 : http://www.aumhaa.com

import Live
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.ButtonElement import ButtonElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ModeSelectorComponent import ModeSelectorComponent
from _Framework.SubjectSlot import SubjectEvent, SubjectSlotGroup, subject_slot, subject_slot_group

from _Mono_Framework.MonoButtonElement import MonoButtonElement
from _Tools.re import *

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


	def __init__(self, script, prefix = 'p', *a, **k):
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
	

	@subject_slot_group('value')
	def _on_button_value(self, value, sender):
		if self.is_enabled():
			if value:
				self.select_device(self._buttons.index(sender))
	

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
		prefix = str(self._prefix)
		offset = self._offset
		preset = None
		for track in self.song().tracks:
			for device in self.enumerate_track_device(track):
				for index, entry in enumerate(self._device_registry):
					key = str(prefix + str(index + 1 + offset))
					if device.name.startswith(key):
						self._device_registry[index] = device
					elif device.name.startswith('*' +key) and device.can_have_chains and len(device.chains) and len(device.chains[0].devices):
						self._device_registry[index] = device.chains[0].devices[0]
		for return_track in self.song().return_tracks:
			for device in self.enumerate_track_device(return_track):
				for index, entry in enumerate(self._device_registry):
					key = str(prefix + str(index + 1 + offset))
					if device.name.startswith(key):
						self._device_registry[index] = device
					elif device.name.startswith('*' + key) and device.can_have_chains and len(device.chains) and len(device.chains[0].devices):
						self._device_registry[index] = device.chains[0].devices[0]
		for device in self.enumerate_track_device(self.song().master_track):
			for index, entry in enumerate(self._device_registry):
				key = str(prefix + str(index + 1 + offset) + ' ')
				if device.name.startswith(key):
					self._device_registry[index] = device
				elif device.name.startswith('*' + key) and device.can_have_chains and len(device.chains) and len(device.chains[0].devices):
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
	

	def _current_device_offsets(self, dict_entry):
		#self.log_message('finding current device offsets')
		selected_device = self._top_device()

		if not selected_device is None and hasattr(selected_device, 'name'):
			name = selected_device.name
			self.log_message('device name: ' + str(name.split(' ')))
			for item in name.split(' '):
				if len(str(item)) and str(item)[0]=='@':
					vals = item[1:].split(':')
					if len(vals) < 2:
						def_assignments = {'scale':'Auto', 'sequencer':False, 'split':False, 'offset':36, 'vertoffset':4, 'drumoffset':0}
						if vals[0] in def_assignments:
							vals.append([vals[0]])
					if vals[0] in dict_entry.keys():
						if vals[0] == 'scale' and vals[1] in SCALES.keys():
							dict_entry[vals[0]] = str(vals[1])
						elif vals[0] in ['sequencer', 'split']:
							if vals[1] in ['False', 'True']:
								dict_entry[vals[0]] = bool(['False', 'True'].index(vals[1]))
						elif vals[0] in ['offset', 'vertoffset', 'drumoffset']:
							dict_entry[vals[0]] = int(vals[1])
			#for key in dict_entry.keys():
			#	self.log_message('key: ' + str(key) + ' entry:' + str(dict_entry[key]))
		return dict_entry
	


