# by amounra 0513: http://www.aumhaa.com

from __future__ import with_statement
import sys
import os
import copy
import Live
import contextlib
from _Tools.re import *
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ControlSurface import ControlSurface
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.ControlElement import ControlElement
from _Framework.CompoundComponent import CompoundComponent # Base class for classes encompasing other components to form complex components
from _Framework.Task import *
from _Framework.SubjectSlot import SubjectEvent, subject_slot, subject_slot_group
from _Framework.Signal import Signal
from _Framework.NotifyingControlElement import NotifyingControlElement
from _Framework.Util import in_range
from _Framework.Debug import debug_print
from _Framework.Disconnectable import Disconnectable
from _Framework.InputControlElement import InputSignal

from _Mono_Framework.DeviceSelectorComponent import NewDeviceSelectorComponent as DeviceSelectorComponent
from _Mono_Framework.MonoParamComponent import MonoParamComponent
from _Mono_Framework.MonoDeviceComponent import NewMonoDeviceComponent as MonoDeviceComponent
from _Mono_Framework.ModDevices import *

DEBUG = True

INITIAL_SCROLLING_DELAY = 5
INTERVAL_SCROLLING_DELAY = 1

CS_LIST_KEY = 'control_surfaces'

def debug():
	return DEBUG


def hascontrol(handler, control):
	return control in handler._controls.keys()


def unpack_values(values):
	values = [int(i) for i in str(values).split('^')]
	if len(values)<2:
		return values[0]
	else:
		return values
	


def unpack_items(values):
	to_convert = str(values).split('^')
	converted = []
	for i in to_convert:
		try:
			converted.append(int(i))
		except:
			converted.append(str(i))
	#if len(converted)<2:
	#	return converted[0]
	#else:
	return converted


def enumerate_track_device(track):
	devices = []
	if hasattr(track, 'devices'):
		for device in track.devices:
			devices.append(device)
			if device.can_have_chains:
				for chain in device.chains:
					for chain_device in enumerate_track_device(chain):
						devices.append(chain_device)
	return devices


def get_monomodular(host):
		if isinstance(__builtins__, dict):
			if not 'monomodular' in __builtins__.keys() or not isinstance(__builtins__['monomodular'], ModRouter):
				__builtins__['monomodular'] = ModRouter()
		else:
			if not hasattr(__builtins__, 'monomodular') or not isinstance(__builtins__['monomodular'], ModRouter):
				setattr(__builtins__, 'monomodular', ModRouter())
		monomodular = __builtins__['monomodular']
		if not monomodular.has_host():
			monomodular.set_host(host)
		return monomodular


def get_control_surfaces():
	if isinstance(__builtins__, dict):
		if CS_LIST_KEY not in __builtins__.keys():
			__builtins__[CS_LIST_KEY] = []
		return __builtins__[CS_LIST_KEY]
	else:
		if not hasattr(__builtins__, CS_LIST_KEY):
			setattr(__builtins__, CS_LIST_KEY, [])
		return getattr(__builtins__, CS_LIST_KEY)


def return_empty():
	return []


class SpecialInputSignal(Signal):


	def __init__(self, sender = None, *a, **k):
		super(SpecialInputSignal, self).__init__(sender=sender, *a, **k)
		self._input_control = sender
	

	@contextlib.contextmanager
	def _listeners_update(self):
		old_count = self.count
		yield
		diff_count = self.count - old_count
		self._input_control._input_signal_listener_count += diff_count
		listener_count = self._input_control._input_signal_listener_count
	

	def connect(self, *a, **k):
		with self._listeners_update():
			super(SpecialInputSignal, self).connect(*a, **k)
	

	def disconnect(self, *a, **k):
		with self._listeners_update():
			super(SpecialInputSignal, self).disconnect(*a, **k)
	

	def disconnect_all(self, *a, **k):
		with self._listeners_update():
			super(SpecialInputSignal, self).disconnect_all(*a, **k)
	


class ElementTranslation(object):


	def __init__(self, name, script):
		self._script = script
		self._name = name
		self._targets = {}
		self._last_received = None
	

	def set_enabled(self, name, enabled):
		try:
			self._targets[name]['Enabled'] = enabled > 0
			if enabled and not self._last_received is None:
				target = self._targets[name]
				value_list = [i for i in target['Arguments']] + [j for j in self._last_received]
				try:
					getattr(target['Target'], method)(*value_list)
				except:
					pass
		except:
			pass
	

	def is_enabled(self, name):
		try:
			return self._targets[name]['Enabled']
		except:
			return False
	

	def target(self, name):
		try:
			return self._targets[name]['Target']
		except:
			return None
	

	def add_target(self, name, target, *args, **k):
		self._targets[name] = {'Target':target, 'Arguments':args, 'Enabled':True}
	

	def receive(self, method, *values):
		#self._script.log_message(str(self._name) + ' receive: ' + str(method) + ' ' + str(values))
		for entry in self._targets.keys():
			target = self._targets[entry]
			if target['Enabled'] == True:
				value_list = [i for i in target['Arguments']] + [j for j in values]
				try:
					getattr(target['Target'], method)(*value_list)
				except:
					pass
		self._last_received = values
	


class StoredElement(object):


	def __init__(self, active_handlers = return_empty, *a, **attributes):
		self._active_handlers = active_handlers
		self._value = 0
		for name, attribute in attributes.iteritems():
			setattr(self, name, attribute)
	

	def value(self, value):
		self._value = value
		self.update_element()
	

	def update_element(self):
		for handler in self._active_handlers():
			handler.receive_address(self._name, self._value)
	

	def restore(self):
		self.update_element()
	


class Grid(object):


	def __init__(self, name, width, height, active_handlers = return_empty, *a, **k):
		self._active_handlers = active_handlers
		self._name = name
		self._width = width
		self._height = height
		self._cell = [[StoredElement(active_handlers, _name = self._name + '_' + str(x) + '_' + str(y), _x = x, _y = y , *a, **k) for y in range(height)] for x in range(width)]
	

	def restore(self):
		for column in self._cell:
			for element in column:
				self.update_element(element)
	

	def update_element(self, element):
		for handler in self._active_handlers():
			handler.receive_address(self._name, element._x, element._y, element._value)
	

	def value(self, x, y, value, *a):
		element = self._cell[x][y]
		element._value = value
		self.update_element(element)
	

	def row(self, row, value, *a):
		for column in range(len(self._cell)):
			self.value(column, row, value)
	

	def column(self, column, value, *a):
		for row in range(len(self._cell[column])):
			self.value(column, row, value)
	

	def clear(self, value, *a):
		self.all(0)
	

	def all(self, value, *a):
		for column in range(len(self._cell)):
			for row in range(len(self._cell[column])):
				self.value(column, row, value)
	

	def batch_row(self, row, *values):
		width = len(self._cell)
		for index in range(len(values)):
			self.value(index%width, row + int(index/width), values[index])
	

	def batch_column(self, column, *values):
		for row in range(len(self._cell[column])):
			if values[row]:
				self.value(column, row, values[row])
	

	def batch_all(self, *values):
		for column in range(len(self._cell)):
			for row in range(len(self._cell[column])):
				if values[column + (row*self._width)]:
					self.value(column, row, values[column + (row*len(self._cell))])
	

	def mask(self, x, y, value, *a):
		element = self._cell[x][y]
		if value > -1:
			for handler in self._active_handlers():
				handler.receive_address(self._name, element._x, element._y, value)
		else:
			self.update_element(element)
	

	def mask_row(self, row, value, *a):
		for column in range(len(self._cell[row])):
			self.mask(column, row, value)
	

	def mask_column(self, column, value, *a):
		for row in range(len(self._cell)):
			self.mask(column, row, value)
	

	def mask_all(self, value, *a):
		for column in range(len(self._cell)):
			for row in range(len(self._cell[column])):
				self.mask(column, row, value)
	

	def batch_mask_row(self, row, *values):
		width = len(self._cell)
		for index in range(len(values)):
			self.mask(index%width, row + int(index/width), values[index])
	

	def batch_mask_column(self, column, *values):
		for row in range(len(self._cell[column])):
			if values[row]:
				self.mask(column, row, values[row])
	

	def batch_mask_all(self, *values):
		for column in range(len(self._cell)):
			for row in range(len(self._cell[column])):
				if values[column + (row*len(self._cell))]:
					self.mask(column, row, values[column + (row*self._width)])
	


class Array(object):


	def __init__(self, name, size, active_handlers = return_empty, *a, **k):
		self._active_handlers = active_handlers
		self._name = name
		self._cell = [StoredElement(self._name + '_' + str(num), _num = num, *a, **k) for num in range(size)]
	

	def restore(self):
		for element in self._cell:
			self.update_element(element)
	

	def update_element(self, element):
		for handler in self._active_handlers():
			handler.receive_address(self._name, element._num, element._value)
	

	def value(self, num, value):
		element = self._cell[num]
		element._value = value
		self.update_element(element)
	

	def all(self, value):
		for num in range(len(self.cell)):
			self.value(num, value)
	

	def mask(self, num, value):
		control = self.cell[num]
		if value > 0:
			for handler in self._active_handlers():
				handler.receive_address(self.name, element._num, value)
		else:
			self._update_element(element)
	

	def mask_all(self, value):
		for num in range(len(self.cell)):
			self.mask(num, value)
	


class RadioArray(Array):


	def value(self, num):
		for element in self._cell:
			element._value = int(element is self._cell[num])
			self.update_element(element)
	


class RingedStoredElement(StoredElement):


	def __init__(self, active_handlers = return_empty, *a, **attributes):
		self._green = 0
		self._mode = 0
		self._custom = [0, 0, 0, 0, 0, 0, 0, 0, 0]
		super(RingedStoredElement, self).__init__(active_handlers, *a, **attributes)
	

	def mode(self, value):
		self._mode = value
		self.update_element()
	

	def green(self, value):
		self._green = value
		self.update_element()
	

	def custom(self, *values):
		self._custom = values
		self.update_element()
	

	def update_element(self):
		for handler in self._active_handlers():
			handler.receive_address(self._name, value = self._value)
			handler.receive_address(self._name, green = self._green)
			handler.receive_address(self._name, mode = self._mode)
			handler.receive_address(self._name, custom = self._custom)	
	


class RingedGrid(Grid):


	def __init__(self, name, width, height, active_handlers = return_empty, *a, **k):
		self._active_handlers = active_handlers
		self._name = name
		self._width = width
		self._height = height
		self._relative = False
		self._local = True
		self._cell = [[RingedStoredElement(active_handlers, _name = self._name + '_' + str(x) + '_' + str(y), _x = x, _y = y , *a, **k) for y in range(height)] for x in range(width)]
	

	def green(self, x, y, value):
		element = self._cell[x][y]
		element._green = value
		self.update_element(element)
	

	def led(self, x, y, value):
		element = self._cell[x][y]
		element._led = value
		self.update_element(element)
	

	def mode(self, x, y, value):
		element = self._cell[x][y]
		element._mode = value
		self.update_element(element)
	

	def custom(self, x, y, *values):
		element = self._cell[x][y]
		element._custom = values
		self.update_element(element)
	

	def relative(self, value):
		#if not self._relative == value:
		self._relative = bool(value)
		self.restore()
	

	def local(self, value):
		#if not self._local == bool(value):
		self._local = bool(value)
		self.restore()
	

	def restore(self):
		for handler in self._active_handlers():
			handler.receive_address(str(self._name+'_relative'), self._relative)
			handler.receive_address(str(self._name+'_local'), self._local)
		super(RingedGrid, self).restore()
	

	def update_element(self, element):
		for handler in self._active_handlers():
			handler.receive_address(self._name, element._x, element._y, value = element._value, green = element._green, mode = element._mode, custom = element._custom)
	


class ModHandler(CompoundComponent):


	def __init__(self, script, addresses = None, device_selector = None, *a, **k):
		super(ModHandler, self).__init__(*a, **k)
		self._script = script
		self._device_selector = device_selector if not device_selector is None else DeviceSelectorComponent(script)
		self._color_type = 'RGB'
		self.log_message = script.log_message
		self.modrouter = script.monomodular
		self._active_mod = None
		self._parameter_controls = None
		self._device_component = None
		self._colors = range(128)
		self._is_enabled = False
		self._is_connected = False
		self._is_locked = False
		self._is_alted = False
		self._is_shifted = False
		self._is_shiftlocked = False
		self._receive_methods = {}
		self._addresses =  {'grid': {'obj':Grid('grid', 16, 16), 'method':self._receive_grid},
							'key': {'obj':Array('key', 8), 'method':self._receive_key},
							'shift': {'obj':StoredElement(_name = 'shift'), 'method':self._receive_shift},
							'alt': {'obj':StoredElement(_name = 'alt'), 'method':self._receive_alt},
							'channel': {'obj':RadioArray('channel', 16), 'method':self._receive_channel}}
		self._addresses.update(addresses or {})
		self._grid = None
		self._mod_nav_buttons = None
		self.x_offset = 0
		self.y_offset = 0
		self._scroll_up_ticks_delay = -1
		self._scroll_down_ticks_delay = -1
		self._scroll_right_ticks_delay = -1
		self._scroll_left_ticks_delay = -1
		self.navbox_selected = 3
		self.navbox_unselected = 5
		self._initialize_receive_methods()
		self.modrouter.register_handler(self)
		self._register_timer_callback(self._on_timer)
		self._on_device_changed.subject = self.song()
		self.modrouter._task_group.add(sequence(delay(5), self.select_appointed_device))
	

	def disconnect(self, *a, **k):
		self._active_mod = None
		#self._unregister_timer_callback(self._on_timer)
		super(ModHandler, self).disconnect(*a, **k)
	

	def _initialize_receive_methods(self):
		addresses = self._addresses
		for address, Dict in addresses.iteritems():
			if not address in self._receive_methods.keys():
				self._receive_methods[address] = Dict['method']
	

	def _register_addresses(self, client):
		addresses = self._addresses
		for address, Dict in addresses.iteritems():
			if not address in client._addresses.keys():
				client._addresses[address] = copy.deepcopy(Dict['obj'])
				client._addresses[address]._active_handlers = client.active_handlers
	

	def receive_address(self, address_name, *a, **k):
		#self.log_message('receive_address ' + str(address_name) + str(a))
		if address_name in self._receive_methods.keys():
			self._receive_methods[address_name](*a, **k)
	

	def update(self, *a, **k):
		if self._active_mod:
			self._active_mod.restore()
	


	def select_mod(self, mod):
		self._active_mod = mod
		self._colors = range(128)
		for mod in self.modrouter._mods:
			if self in mod._active_handlers:
				mod._active_handlers.remove(self)
		if not self._active_mod is None:
			self._active_mod._active_handlers.append(self)
			if self._color_type in self._active_mod._color_maps.keys():
				self._colors = self._active_mod._color_maps[self._color_type]
			self._active_mod.restore()
		self.update()
	

	def active_mod(self, *a, **k):
		return self._active_mod
	


	@subject_slot('appointed_device')
	def _on_device_changed(self):
		#self.log_message('modhandler on_device_changed')
		if not self.is_locked():	# or self.active_mod() is None:   #not sure why this was here?  
			self.modrouter._task_group.add(sequence(delay(2), self.select_appointed_device))
	

	def select_appointed_device(self, *a):
		#self.log_message('select_appointed_device' + str(a))
		self.select_mod(self.modrouter.is_mod(self.song().appointed_device))
	


	def set_parameter_controls(self, controls):
		self._parameter_controls = None
		if not controls is None:
			self._parameter_controls = [control for control, _ in controls.iterbuttons()]
		if not self._active_mod is None:
			self._active_mod._param_component.update()
	

	def set_device_component(self, device_component):
		self._device_component = device_component
	

	def update_device(self):
		#self.log_message('update device')
		#self.update_parameter_controls()
		#if self.is_enabled() and not self._device_component is None:
		#	self.update_device()
		pass
	


	def set_mod_nav_buttons(self, buttons):
		self._mod_nav_buttons = buttons
		self._on_mod_nav_button_value.replace_subjects(buttons)
		self._update_mod_nav_buttons()
	

	@subject_slot_group('value')
	def _on_mod_nav_button_value(self, value, sender):
		if value and not self._mod_nav_buttons is None:
			direction = self._mod_nav_buttons.index(sender)
			if direction:
				self.nav_mod_up()
			else:
				self.nav_mod_down()
	

	def _update_mod_nav_buttons(self):
		if not self._mod_nav_buttons is None:
			for button in self._mod_nav_buttons:
				if not button is None:
					button.turn_on()
	

	def nav_mod_down(self):
		new_mod = self.modrouter.get_previous_mod(self.active_mod())
		self.log_message('new_mod: ' + str(new_mod))
		if isinstance(new_mod, ModClient):
			device = new_mod.linked_device()
			self.log_message('device: ' + str(device))
			if isinstance(device, Live.Device.Device):
				self.song().view.select_device(device)
				self.log_message('selected: ' + str(device))
				self.select_mod(new_mod)
	

	def nav_mod_up(self):
		new_mod = self.modrouter.get_next_mod(self.active_mod())
		self.log_message('new_mod: ' + str(new_mod))
		if isinstance(new_mod, ModClient):
			device = new_mod.linked_device()
			if isinstance(device, Live.Device.Device):
				self.song().view.select_device(device)
				self.select_mod(new_mod)
	

	def show_mod_in_live(self):
		if isinstance(self.active_mod(), Live.Device.Device):
			self.song().view.select_device(self.active_mod().linked_device())
	


	def set_grid(self, grid):
		#self.log_message('set grid:' + str(grid))
		self._grid = grid
		self._grid_value.subject = grid
		if not self._grid is None:
			for button, _ in grid.iterbuttons():
				if not button == None:
					button.use_default_message()
					button.set_enabled(True)
		self.update()
	

	def _receive_grid(self, address):
		pass
	

	@subject_slot('value')
	def _grid_value(self, value, x, y, *a, **k):
		#self.log_message('_base_grid_value ' + str(x) + str(y) + str(value))
		if self.active_mod():
			if self._active_mod.legacy:
				if self.is_shifted():
					if value > 0 and x in range(6, 8) and y in range(2,4):
						self.set_offset((x - 6) * 8,  (y - 2) * 8)
						self.update()
				else:
					self._active_mod.send('grid', x + self.x_offset, y + self.y_offset, value)
			else:
				self._active_mod.send('grid', x, y, value)
	


	def set_key_buttons(self, keys):
		self._keys_value.subject = keys
		if self.active_mod():
			self.active_mod()._addresses['key'].restore()
	

	def _receive_key(self, x, value):
		#self.log_message('_receive_key: %s %s' % (x, value))
		if not self._keys_value.subject is None:
			self._keys_value.subject.send_value(x, 0, self._colors[value], True)
	

	@subject_slot('value')
	def _keys_value(self, value, x, y, *a, **k):
		if self._active_mod:
			self._active_mod.send('key', x, value)
	


	def set_channel_buttons(self, buttons):
		self._channel_value.subject = buttons
		if self.active_mod():
			self.active_mod()._addresses['channel'].restore()
	

	def _receive_channel(self, x, value):
		#self.log_message('_receive_channel: %s %s' % (x, value))
		if not self._channel_value.subject is None and x < self._channel_value.subject.width():
			self._channel_value.subject.send_value(x, 0, self._colors[value], True)
	

	@subject_slot('value')
	def _channel_value(self, value, x, y, *a, **k):
		#self.log_message('_channel_value: %s %s' % (x, value))
		if value and self._active_mod:
			self._active_mod.send('channel', x)
	


	def set_shift_button(self, button):
		self._shift_value.subject = button
		if button:
			button.send_value(self.is_shifted())
	

	def is_shifted(self):
		return self._is_shifted
	

	def _receive_shift(self, value):
		if not self._shift_value.subject is None:
			self._shift_value.subject.send_value(value)
	

	@subject_slot('value')
	def _shift_value(self, value, *a, **k):
		self._is_shifted = not value is 0
		if self.active_mod():
			self._active_mod.send('shift', value)
		self.update()
	


	def set_alt_button(self, button):
		self._alt_value.subject = button
		if button:
			button.send_value(self.is_alted())
	
	
	def is_alted(self):
		return self._is_alted
	

	def _receive_alt(self, value):
		if not self._alt_value.subject is None:
			self._alt_value.subject.send_value(value)
	

	@subject_slot('value')
	def _alt_value(self, value, *a, **k):
		self._is_alted = not value is 0
		if self._active_mod:
			self._active_mod.send('alt', value)
			self.update_device()
		self.update()
	


	def set_lock_button(self, button):
		self._on_lock_value.subject = button
		if button:
			button.send_value(self.is_locked()*8)
	

	def is_locked(self):
		return self._is_locked
	

	def set_lock(self, value):
		self._is_locked = value > 0
		if not self._on_lock_value.subject is None:
			self._on_lock_value.subject.send_value(self.is_locked()*8)
	

	@subject_slot('value')
	def _on_lock_value(self, value):
		if value>0:
			self.set_lock(not self.is_locked())
		self.update()
	


	def set_shiftlock_button(self, button):
		self._on_shiftlock_value.subject = button
	

	def is_shiftlocked(self):
		return self._is_shiftlocked
	

	@subject_slot('value')
	def _on_shiftlock_value(self, value):
		#self.log_message('shiftlock value ' + str(value))
		if value>0:
			self._is_shiftlocked = not self.is_shiftlocked()
			if not self._on_shiftlock_value.subject is None:
				self._on_shiftlock_value.subject.send_value(self.is_shiftlocked())
			self.update()
	


	def set_offset(self, x, y):
		self.x_offset = max(0, min(x, 8))
		self.y_offset = max(0, min(y, 8))
		if self._active_mod and self._active_mod.legacy:
			self._active_mod.send('offset', self.x_offset, self.y_offset)
			self._display_nav_box()
	

	def _display_nav_box(self):
		pass
	

	def set_nav_buttons(self, buttons):
		assert buttons is None or len(buttons)==4
		if buttons is None:
			buttons = [None for index in range(4)]
		self.set_nav_up_button(buttons[0])
		self.set_nav_down_button(buttons[1])
		self.set_nav_left_button(buttons[2])
		self.set_nav_right_button(buttons[3])
	

	def set_nav_up_button(self, button):
		self._on_nav_up_value.subject = button
	

	def set_nav_down_button(self, button):
		self._on_nav_down_value.subject = button
	

	def set_nav_left_button(self, button):
		self._on_nav_left_value.subject = button
	

	def set_nav_right_button(self, button):
		self._on_nav_right_value.subject = button
	

	@subject_slot('value')
	def _on_nav_up_value(self, value):
		if value:
			self._scroll_up_ticks_delay = INITIAL_SCROLLING_DELAY
			if (not self._is_scrolling()):
				self.set_offset(self.x_offset, self.y_offset - 1)
				self.update()
		else:
			self._scroll_up_ticks_delay = -1
	

	@subject_slot('value')
	def _on_nav_down_value(self, value):
		if value:
			self._scroll_down_ticks_delay = INITIAL_SCROLLING_DELAY
			if (not self._is_scrolling()):
				self.set_offset(self.x_offset, self.y_offset + 1)
				self.update()
		else:
			self._scroll_down_ticks_delay = -1
	

	@subject_slot('value')
	def _on_nav_left_value(self, value):
		if value:
			self._scroll_left_ticks_delay = INITIAL_SCROLLING_DELAY
			if (not self._is_scrolling()):
				self.set_offset(self.x_offset - 1, self.y_offset)
				self.update()
		else:
			self._scroll_left_ticks_delay = -1
	

	@subject_slot('value')
	def _on_nav_right_value(self, value):
		if value:
			self._scroll_right_ticks_delay = INITIAL_SCROLLING_DELAY
			if (not self._is_scrolling()):
				self.set_offset(self.x_offset + 1, self.y_offset)
				self.update()
		else:
			self._scroll_right_ticks_delay = -1
	

	def _update_nav_buttons(self):
		self._on_nav_up_value.subject and self._on_nav_up_value.subject.send_value(int(self.y_offset > 0), True)
		self._on_nav_down_value.subject and self._on_nav_down_value.subject.send_value(int(self.y_offset < 8), True)
		self._on_nav_left_value.subject and self._on_nav_left_value.subject.send_value(int(self.x_offset > 0), True)
		self._on_nav_right_value.subject and self._on_nav_right_value.subject.send_value(int(self.x_offset < 8), True)
	

	def _is_scrolling(self):
		return (0 in (self._scroll_up_ticks_delay, self._scroll_down_ticks_delay, self._scroll_right_ticks_delay, self._scroll_left_ticks_delay))
	

	def _on_timer(self):
		if self.is_enabled():
			scroll_delays = [self._scroll_up_ticks_delay,
							 self._scroll_down_ticks_delay,
							 self._scroll_right_ticks_delay,
							 self._scroll_left_ticks_delay]
			if (scroll_delays.count(-1) < 4):
				x_increment = 0
				y_increment = 0
				if (self._scroll_right_ticks_delay > -1):
					if self._is_scrolling():
						x_increment += 1
						self._scroll_right_ticks_delay = INTERVAL_SCROLLING_DELAY
					self._scroll_right_ticks_delay -= 1
				if (self._scroll_left_ticks_delay > -1):
					if self._is_scrolling():
						x_increment -= 1
						self._scroll_left_ticks_delay = INTERVAL_SCROLLING_DELAY
					self._scroll_left_ticks_delay -= 1
				if (self._scroll_down_ticks_delay > -1):
					if self._is_scrolling():
						y_increment += 1
						self._scroll_down_ticks_delay = INTERVAL_SCROLLING_DELAY
					self._scroll_down_ticks_delay -= 1
				if (self._scroll_up_ticks_delay > -1):
					if self._is_scrolling():
						y_increment -= 1
						self._scroll_up_ticks_delay = INTERVAL_SCROLLING_DELAY
					self._scroll_up_ticks_delay -= 1
				new_x_offset = max(0, (self.x_offset + x_increment))
				new_y_offset = max(0, (self.y_offset + y_increment))
				if ((new_x_offset != self.x_offset) or (new_y_offset != self.y_offset)):
					self.set_offset(new_x_offset, new_y_offset)
					self.update()
	





class ModClient(NotifyingControlElement):


	__subject_events__ = (SubjectEvent(name='value', signal=InputSignal, override=True),)
	_input_signal_listener_count = 0

	def __init__(self, parent, device, name, *a, **k):
		super(ModClient, self).__init__(*a, **k)
		self.name = name
		self.device = device
		self._device_parent = None
		self._parent = parent
		self.log_message = parent.log_message
		self._active_handlers = []
		self._addresses = {}
		self._translations = {}
		self._translation_groups = {}
		self._color_maps = {}
		self.legacy = False
		self.register_addresses()
		self._param_component = MonoDeviceComponent(self, MOD_BANK_DICT, MOD_TYPES)
	

	def register_addresses(self):
		for handler in self._parent._handlers:
			handler._register_addresses(self)
			self.send('register_handler', handler.name)
	

	def addresses(self):
		return self._addresses
	

	def translations(self):
		return self._translations
	

	def active_handlers(self):
		return self._active_handlers
	

	def receive(self, address_name, method = 'value', values = 0, *a, **k):
		if address_name in self._addresses.keys():
			address = self._addresses[address_name]
			value_list = unpack_items(values)
			#self.log_message('address: ' + str(address) + ' value_list: ' + str(value_list))
			try:
				#with self._parent._host.component_guard():
				getattr(address, method)(*value_list)
			except:
				if debug():
					self.log_message('receive method exception %(a)s %(m)s %(vl)s' % {'a':address_name, 'm':method, 'vl':values})
	

	def distribute(self, function_name, values = 0, *a, **k):
		if hasattr(self, function_name):
			value_list = unpack_items(values)
			#self.log_message('distribute: ' + str(function_name) + ' ' + str(values) + ' ' + str(value_list))
			try:
				getattr(self, function_name)(*value_list)
			except:
				if debug():
					self.log_message('distribute method exception %(fn)s %(vl)s' % {'fn':function_name, 'vl':value_list})
	

	def receive_translation(self, translation_name, method = 'value', *values):
		#value_list = unpack_items(values)
		#self.log_message('receive_translation: ' + str(translation_name) + ' ' + str(method) + ' ' + str(values))
		try:
			self._translations[translation_name].receive(method, *values)
		except:
			if debug():
				self.log_message('receive_translation method exception %(n)s %(m)s %(vl)s' % {'n':translation_name, 'm':method, 'vl':values})
	

	def trans(self, translation_name, method = 'value', *values):
		#value_list = unpack_items(values)
		#self.log_message('receive_translation: ' + str(translation_name) + 'is avail: ' + str(translation_name in self._translations.keys()) + ' ' + str(method) + ' ' + str(values))# + ' ' + str(value_list))
		try:
			self._translations[translation_name].receive(method, *values)
		except:
			if debug():
				self.log_message('receive_translation method exception %(n)s %(m)s %(vl)s' % {'n':translation_name, 'm':method, 'vl':values})
	

	def send(self, control_name, *a):
		#with self._parent._host.component_guard():
		self.notify_value(control_name, *a)
	

	def is_active(self):
		return (len(self._active_host) > 0)
	

	def set_enabled(self, val):
		self._enabled = val!=0
	

	def is_connected(self):
		return self._connected
	

	def disconnect(self):
		self._active_handler = []
		if self._device_parent != None:
			if self._device_parent.devices_has_listener(self._device_listener):
				self._device_parent.remove_devices_listener(self._device_listener)
		self.send('disconnect')
		super(ModClient, self).disconnect()
		self._enabled = True
	

	def reset(self):
		pass
	

	def restore(self):
		for address_name, address in self._addresses.iteritems():
			address.restore()
		self._param_component.update()
	

	def _connect_to(self, device):
		self._connected = True
		self.device = device
		if self._device_parent != None:
			if self._device_parent.devices_has_listener(self._device_listener):
				self._device_parent.remove_devices_listener(self._device_listener)
		self._device_parent = device.canonical_parent
		if not self._device_parent.devices_has_listener(self._device_listener):
			self._device_parent.add_devices_listener(self._device_listener)
		for handler in self._active_handler:
			handler.update()
	

	def _disconnect_client(self, reconnect = False):
		if self._device_parent != None:
			if self._device_parent.devices_has_listener(self._device_listener):
				self._device_parent.remove_devices_listener(self._device_listener)
		self._connected = False
		self.device = None
		for handler in self._active_handler:
			handler.set_mod(None)
	

	def _device_listener(self):
		if self.device == None:
			self._disconnect_client()
	

	def linked_device(self):
		return self.device
	

	def script_wants_forwarding(self):
		return True
	

	def add_translation(self, name, target, group=None, *args, **k):
		#self.log_message('name: ' + str(name) + ' target: ' + str(target) + ' args: ' + str(args))
		if target in self._addresses.keys():
			if not name in self._translations.keys():
				self._translations[name] = ElementTranslation(name, self)
			#self.log_message('adding new target')
			self._translations[name].add_target(target, self._addresses[target], *args)
			if not group is None:
				if not group in self._translation_groups.keys():
					self._translation_groups[group] = []
				self._translation_groups[group].append([name, target])
				#self.log_message('added to group ' + str(group) + ' : ' + str(self._translation_groups[group]))
	

	def enable_translation(self, name, target, enabled = True):
		if name in self._translations.keys():
			self._translations[name].set_enabled(target, enabled)
	

	def enable_translation_group(self, group, enabled = True):
		if group in self._translation_groups.keys():
			for pair in self._translation_groups[group]:
				#self.log_message('enabling for ' + str(pair))
				self.enable_translation(pair[0], pair[1], enabled)
	

	def receive_device(self, command, *args):
		#self.log_message('receive_device ' + str(command) +str(args))
		try:
			getattr(self._param_component, command)(*args)
		except:
			self.log_message('receive_device exception: %(c)s %(a)s' % {'c':command, 'a':args})
	

	def update_device(self):
		for handler in self.active_handlers():
			handler.update_device()
	

	def set_legacy(self, value):
		#self.log_message('set_legacy: ' + str(value))
		self.legacy = value > 0
	

	def select_device_from_key(self, key):
		key = str(key)
		preset = None
		for track in self._parent.song().tracks:
			for device in enumerate_track_device(track):
				if(match(key, str(device.name)) != None):
					preset = device
					break
		for return_track in self._parent.song().return_tracks:
			for device in enumerate_track_device(return_track):
				if(match(key, str(device.name)) != None):
					preset = device
					break
		for device in enumerate_track_device(self._parent.song().master_track):
			if(match(key, str(device.name)) != None):
				preset = device
				break
		if preset != None:
			self._parent.song().view.select_device(preset)
	

	def fill_color_map(self, color_type = None, *color_map):
		#self.log_message('fill color map: ' + str(color_type) + ' ' + str(color_map))
		if not color_type is None:
			self._color_maps[color_type] = [color_map[index%(len(color_map))] for index in range(128)]
			self._color_maps[color_type][0:0] = [0]
			for handler in self.active_handlers():
				if handler._color_type is color_type:
					handler._colors = self._color_maps[color_type]
				handler.update()
	

	def set_color_map(self, color_type, *color_map):
		#self.log_message('set color map: ' + str(color_type) + ' ' + str(color_map))
		if color_type:
			for index in xrange(color_map):
				self._color_maps[color_type][index] = color_map[index]
			for handler in self.active_handlers():
				if handler._color_type is color_type:
					handler._colors = self._color_maps[color_type]
				handler.update()
	


class ModRouter(CompoundComponent):


	def __init__(self, *a, **k):
		super(ModRouter, self).__init__(*a, **k)
		self._host = None
		self._handlers = []
		self._mods = []
		self.log_message = self._log_message
		return None
	

	def set_host(self, host):
		assert isinstance(host, ControlSurface)
		self._host = host
		#self._host._get_tasks().add(repeat(self.timer))
		self._task_group = host._task_group
		self._host.log_message('host registered: ' + str(host))
		self.log_message = host.log_message
		#self._host._register_component(self)
	

	def has_host(self):
		#from _Framework.ControlSurface import ControlSurface
		#result = False
		#if hasattr(self._host, '_task_group'):
		#	result = self._host._task_group.find(self.timer)
		#return result
		return not self._host is None
	

	def _log_message(self, *a, **k):
		pass
	

	def register_handler(self, handler):
		if handler not in self._handlers:
			self._handlers.append(handler)
		for mod in self._mods:
			mod.register_addresses()
			mod.send('disconnect')
	

	def unregister_handler(self, cs, handler):
		self.log_message('unregistering handler ' + str(cs) + ' ' + str(handler))
		for mod in self._mods:
			mod.send('disconnect')
		for index in range(len(self._handlers)):
			if self._handlers[index] is handler:
				self._host = None
				self._task_group = None
				self.log_message('deleting from handlers: ' + str(self._handlers[index]))
				del self._handlers[index]
				for surface in get_control_surfaces():
					if not surface is cs:
						if hasattr(surface, 'monomodular'):
							self.log_message('reconnecting router to ' + str(surface))
							self.set_host(surface)
							break
				self._log_message = self._log_message
				break

	

	def devices(self):
		return [mod.device for mod in self._mods]
	

	def get_mod(self, device):
		#self.log_message('getting mod...')
		mod = None
		for mod_device in self._mods:
			if mod_device.device == device:
				mod = mod_device
		return mod
	

	def get_next_mod(self, active_mod):
		if not active_mod is None:
			return self._mods[(self._mods.index(active_mod) +1) % len(self._mods)]
		elif not len(self._mods) is 0:
			return self._mods[0]
		else:
			return None
	

	def get_previous_mod(self, active_mod):
		if not active_mod is None:
			return self._mods[(self._mods.index(active_mod) + len(self._mods) -1) % len(self._mods)]
		elif not len(self._mods) is 0:
			return self._mods[-1]
		else:
			return active_mod
	

	def add_mod(self, device):
		if not device in self.devices():
			with self._host.component_guard():
				self._mods.append( ModClient(self, device, 'modClient'+str(len(self._mods))) )
		ret = self.get_mod(device)
		#self.log_message('add mod device: ' + str(device.name) + ' ' + str(ret))
		return ret
	

	def timer(self, *a, **k):
		pass
	

	def update(self):
		pass
	

	def disconnect(self):
		for surface in get_control_surfaces():
			if hasattr(surface, 'monomodular'):
				self.log_message('deleting monomodular for ' + str(surface))
				del surface.monomodular
		old_host = self._host
		self._host = None
		self._handlers = []
		if hasattr(__builtins__, 'monomodular') or 'monomodular' in __builtins__.keys():
			self.log_message('deleting monomodular from builtins')
			del __builtins__['monomodular']
		for surface in get_control_surfaces():
			if not surface is old_host:
				if hasattr(surface, 'restart_monomodular'):
					surface.schedule_message(2, surface.restart_monomodular)
		for mod in self._mods:
			mod.disconnect()
		self._mods = []
		self.log_message('monomodular is disconnecting....')
		self.log_message = self._log_message
		super(ModRouter, self).disconnect()
	

	def is_mod(self, device):
		mod_device = None
		if isinstance(device, Live.Device.Device):
			try:
				if device.can_have_chains and not device.can_have_drum_pads and len(device.view.selected_chain.devices)>0:
					device = device.view.selected_chain.devices[0]
			except:
				pass
		self.log_message('is_mod ' + str(device))
		if not device is None:
			for mod in self._mods:
				self.log_message('mod in mods: ' + str(mod.device))
				if mod.device == device:
					mod_device = mod
					break
		return mod_device
	



