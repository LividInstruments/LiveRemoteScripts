# by amounra :  http://www.aumhaa.com
from __future__ import with_statement
import contextlib
from _Framework.SubjectSlot import SubjectEvent
from _Framework.Signal import Signal
from _Framework.NotifyingControlElement import NotifyingControlElement
from _Framework.Util import in_range
from _Framework.Debug import debug_print
from _Framework.Disconnectable import Disconnectable
from _Framework.InputControlElement import InputSignal
from MonoDeviceComponent import MonoDeviceComponent
from ModDevices import *


wheel_parameter = {0: 'value', 1: 'mode', 2:'green', 3:'white', 4:'custom'}
LOGO = [[], [], [], [], [], [], [], [], 
				[[1, 1], [2, 1], [3, 1], [4, 1]], 
		[[0, 1]], 
				[[1, 1], [2, 1]], 
				[[1, 1], [2, 1], [3, 1]], 
		[[0, 1]], 
				[[1, 1], [2, 1], [3, 1], [4, 1]],
						[[2, 1], [3, 1], [4, 1]],
		[],
						[[2, 2], [3, 2]],
				[[1, 2],				 [4, 2]],
		[[0, 2],						 [4, 2]], 
		[[0, 2],				 [3, 2], [4, 2]],
				[[1, 2], [2, 2], [3, 2]],
		[],
				[[1, 3], [2, 3], [3, 3], [4, 3]],	 
		[[0, 3], [1, 3]], 
				[[1, 3], [2, 3]], 
						[[2, 3], [3, 3]],
		[[0, 3], [1, 3], [2, 3], [3, 3], [4, 3]],
		[],
						[[2, 4], [3, 4]],
				[[1, 4],				 [4, 4]], 
		[[0, 4],						 [4, 4]],
		[[0, 4], 				 [3, 4], [4, 4]], 
				[[1, 4], [2, 4], [3, 4]],
		[],
				[[1, 5], [2, 5], [3, 5], [4, 5]], 
		[[0, 5]],
				[[1, 5], [2, 5]], 
				[[1, 5], [2, 5], [3, 5]], 
		[[0, 5]],
				[[1, 5], [2, 5], [3, 5], [4, 5]], 
						[[2, 5], [3, 5], [4, 5]], 
		[],
						[[2, 6],[3, 6]], 
				[[1, 6], 				[4, 6]], 
		[[0, 6], 						 [4, 6]], 
		[[0, 6],				 [3, 6], [4, 6]], 
				[[1, 6], [2, 6], [3, 6]], 
		[],
		[[0, 1], [1, 1], [2, 1], [3, 1], [4, 1]], 
		[[0, 1], 				 	      [4, 1]], 
		[[0, 1], 				 		  [4, 1]], 
				[[1, 1], [2, 1], [3, 1], [4, 1]],
						[[2, 1], [3, 1], [4, 1]], 
		[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]


def unpack_values(values):
	return [int(i) for i in str(values).split('^')]



class MonoClient(NotifyingControlElement):
	__module__ = __name__
	__doc__ = ' Class representing a single mod in a Monomodular hosted environment '


	__subject_events__ = (SubjectEvent(name='value', signal=InputSignal, override=True),)
	_input_signal_listener_count = 0

	def __init__(self, script, number, *a, **k):
		super(MonoClient, self).__init__(script, number, *a, **k)
		self._host = script
		self._is_monolink = False
		self._active_host = []
		self._number  = number
		self._channel = 0
		self._connected = False
		self._enabled = True
		self.device = None
		self._device_parent = None
		self._device_component = None
		self._swing = 0
		self._mute = 0
		self._autoselect_enabled = 0
		self._offset = [0, 0]
		self._color_maps = []
		self._report_offset = False
		self._local_ring_control = 1
		self._c_local_ring_control = 1
		self._controls = [{},{}]
		self._create_grid()
		self._create_keys()
		self._create_wheels()
		self._create_c_grid()
		self._create_c_keys()
		self._create_c_wheels()
		self._create_c_knobs()
		self._absolute_mode = 1
		self._c_absolute_mode = 1
		self._parameters = []
		self._mod_dial = None
		self._mod_vol = 127
		self._mod_color = 0
		self._device_component = MonoDeviceComponent(self, MOD_BANK_DICT, MOD_TYPES)
		self._banner_state = 0
		self._monomodular = 0
	

	def is_active(self):
		return (len(self._active_host) > 0)
	

	def set_enabled(self, val):
		self._enabled = val!=0
	

	def _banner(self):
		if not self.is_connected() and len(self._active_host)>0:
			if self._banner_state < 54:
				self.receive_grid_all(0)
				for index in range(16):
					for y in range(len(LOGO[self._banner_state + index])):
						self.receive_grid(index, LOGO[self._banner_state + index][y][0], LOGO[self._banner_state + index][y][1])
				self._banner_state += 1
				self._host.schedule_message(1, self._banner)
			else:
				self._banner_state = 0		
	

	def script_wants_forwarding(self):
		return True
	

	def is_connected(self):
		return self._connected
	

	def disconnect(self):
		#self._device_component.disconnect()
		self._active_host = []
		if self._device_parent != None:
			if self._device_parent.devices_has_listener(self._device_listener):
				self._device_parent.remove_devices_listener(self._device_listener)
		super(MonoClient, self).disconnect()
		self._enabled = True
		self._c_local_ring_control = 1
		self._local_ring_control = 1
		self._c_absolute_mode = 1
		self._absolute_mode = 1

	

	def reset(self):
		pass
	

	def _connect_to(self, device):
		#self._host.log_message('client ' + str(self._number) + ' connect_to'  + str(device.name))
		self._connected = True
		self.device = device
		if self._device_parent != None:
			if self._device_parent.devices_has_listener(self._device_listener):
				self._device_parent.remove_devices_listener(self._device_listener)
		self._device_parent = device.canonical_parent
		if not self._device_parent.devices_has_listener(self._device_listener):
			self._device_parent.add_devices_listener(self._device_listener)
		#self._mute = 0
		#self._send('toggle_mute', self._mute)
		for host in self._active_host:
			host.update()
		for host in self._host._hosts:
			if hasattr(host, '_notify_new_connection'):
				host._notify_new_connection(device)
			
	

	def _disconnect_client(self, reconnect = False):
		#self._host.log_message('disconnect client ' + str(self._number))
		self._create_grid()
		self._create_keys()
		self._create_wheels()
		self._create_c_grid()
		self._create_c_keys()
		self._create_c_wheels()
		self._create_c_knobs()
		self.set_local_ring_control(1)
		self.set_absolute_mode(1)
		self.set_c_local_ring_control(1)
		self.set_c_absolute_mode(1)
		self._mod_vol = 127
		self._mod_color = 0
		self._monomodular = 0
		self._swing = 0
		self._report_offset = False
		if self._device_parent != None:
			if self._device_parent.devices_has_listener(self._device_listener):
				self._device_parent.remove_devices_listener(self._device_listener)
		if reconnect == True:
			self._send('reconnect')
		if not self._device_component is None:
			self._device_component.disconnect_client()
		self._connected = False
		self.device = None
		for host in self._active_host:
			host.update()
			if not host.is_enabled() and 'display_mod_colors' in dir(host):
				host.display_mod_colors()
	

	def _device_listener(self):
		#self._host.log_message('device_listener' + str(self.device))
		if self.device == None:
			self._disconnect_client()
	

	def linked_device(self):
		return self.device
	


	"""initiation methods"""
	def _create_grid(self):
		self._grid = [None for index in range(16)]
		for column in range(16):
			self._grid[column] = [None for index in range(16)]
			for row in range(16):
				self._grid[column][row] = 0
	

	def _create_keys(self):
		self._key = [None for index in range(8)]
		for index in range(8):
			self._key[index] = 0
	

	def _create_wheels(self):
		self._wheel = [[] for index in range(9)]
		for column in range(9):
			self._wheel[column] = [[] for index in range(5)]
			for row in range(5):
				self._wheel[column][row] = {'log': 0, 'value': 0, 'mode':0, 'white': 0, 'green': 0, 'custom':'00000000', 'pn':' ', 'pv': '0'}
	


	"""send methods (to m4l from host)"""
	def _send(self, args1 = None, args2 = None, args3 = None, args4 = None):
		if self._enabled is True:
			self.notify_value(args1, args2, args3, args4)
	

	def _send_key(self, index, value):
		self._send('key', index, value)
	

	def _send_grid(self, column, row, value):
		self._send('grid', column, row, value)
	

	def _send_offset(self, x, y):
		self._offset = [x, y]
		if(self._report_offset is True):
			self._send('offset', x, y)	
	


	"""receive methods (from m4l)"""
	def receive_key(self, index, value=0):
		if self._key[index] != value:
			self._key[index] = value
			for host in self._active_host:
				host._send_key(index, value)
	

	def receive_grid(self, column, row, value=0):
		if self._grid[column][row] != value:
			self._grid[column][row] = value
			for host in self._active_host:
				host._send_grid(column, row, value)
	

	def receive_grid_row(self, row, value=0):
		g_len = len(self._grid)
		for column in xrange(g_len):
			self._grid[column][row] = value
		for host in self._active_host:
			for column in xrange(g_len):
				host._send_grid(column, row, value)
	

	def receive_grid_column(self, column, value=0):
		g_len = len(self._grid[column])
		for row in xrange(g_len):
			self._grid[column][row] = value
		for host in self._active_host:
			for row in xrange(g_len):
				host._send_grid(column, row, value)
	

	def receive_grid_all(self, value=0):
		for column in xrange(len(self._grid)):
			for row in xrange(len(self._grid[column])):
				self._grid[column][row] = value
				#if self.is_active():
				for host in self._active_host:
				#for column in range(len(self._grid)):
					#for row in range(len(self._grid[column])):
					host._send_grid(column, row, value)
	

	def receive_mask_key(self, num, value=-1):
		#if self.is_active():
		if value > -1:
			for host in self._active_host:
				host._send_key(num, value)
		else:
			for host in self._active_host:
				host._send_key(num, int(self._key[num]))
	

	def receive_mask_grid(self, column, row, value=-1):
		if value > -1:
			for host in self._active_host:
				host._send_grid(column, row, value)
		else:
			for host in self._active_host:
				host._send_grid(column, row, int(self._grid[column][row]))
	

	def receive_mask_column(self, column, value=-1):
		if value > -1:
			for host in self._active_host:
				for index in xrange(16):
					host._send_grid(column, index, value)
		else:
			for host in self._active_host:
				for index in xrange(16):
					host._send_grid(column, index, self._grid[column][index])
	

	def receive_mask_row(self, row, value=-1):
		hosts = self._active_host
		if value > -1:
			for index in xrange(16):
				for host in hosts:
					host._send_grid(index, row, value)
		else:
			for host in self._active_host:
				for index in xrange(16):
					host._send_grid(index, row, self._grid[index][row])
	

	def receive_mask_all(self, value=-1):
		if value > -1:
			for host in self._active_host:
				for column in xrange(16):
					for row in xrange(16):
						host._send_grid(column, row, value)
		else:
			for host in self._active_host:
				for column in xrange(16):
					for row in xrange(16):
						host._send_grid(column, row, self._grid[index][row])
	

	def receive_hotline(self, client, func = None, arguments = None):
		#self._host.log_message(str(client) + ' ' + str(func) + ' ' + str(arguments))
		if(client == 'all') and (func != None):
			for index in xrange(16):
				self._host._client[index]._send('hotline', func, arguments)
		elif(client in xrange(16)) and (func != None):
			self._host._client[client]._send('hotline', func, arguments)
	

	def receive_autoselect_enabled(self, val=0):
		self._autoselect_enabled = val
	

	def receive_swing(self, swing=0):	
		self._swing = swing
		self._send('swing', swing)
	

	def report_swing(self, swing=0):
		self._send('report_swing', swing)
	

	def toggle_mute(self):
		self._mute = abs(self._mute-1)
		self._send('toggle_mute', self._mute)
	

	def set_mute(self, val=0):
		self._mute = val
	

	def receive_channel(self, channel=0):
		if channel in range(16):
			self._channel = channel
	

	def autoselect_enabled(self=0):
		return self._autoselect_enabled > 0
	

	def _autoselect(self):
		if self.autoselect_enabled():
			if self.device != None:
				for host in self._active_host:
					host.set_appointed_device(self.device)
	

	def _set_channel(self, channel):
		self._send('channel', channel)
		self._channel = channel	
	

	def set_report_offset(self, val=0):
		self._report_offset = (val == 1)
		self._send_offset(self._offset[0], self._offset[1])
	

	def set_monomodular(self, val=0):
		self._monomodular = val
	

	def set_color_map(self, color_type, color_map):
		for host in self._host._hosts:
			#self._host.log_message(str(host._host_name) + str(host_name))
			if str(host._script._color_type) == str(color_type):
				#new_map = [color_map[i] for i in range(len(color_map))]
				#self._host.log_message('mapping ' + str(host_name) + ' to ' + str(self._number))
				new_map = color_map.split('*')
				for index in xrange(len(new_map)):
					new_map[index] = int(new_map[index])
				#self._host.log_message(str(host_name) + str(new_map))
				host._color_maps[self._number] = new_map
				if host._active_client is self:
					host._select_client(self._number)
				#self._host.log_message(str(host_name) + ' ' + str(color_map.split('*')))
	

	def linked_device(self):
		return self.device
	


	"""CNTRL:R specific methods"""
	def _create_c_grid(self):
		self._c_grid = [None for index in range(4)]
		for column in range(4):
			self._c_grid[column] = [None for index in range(4)]
			for row in range(4):
				self._c_grid[column][row] = 0
	

	def _create_c_keys(self):
		self._c_key = [None for index in range(32)]
		for index in range(32):
			self._c_key[index] = 0
	

	def _create_c_knobs(self):
		self._knob = [None for index in range(24)]
		for index in range(24):
			self._knob[index] = 0
	

	def _create_c_wheels(self):
		self._c_wheel = [[] for index in range(4)]
		for column in range(4):
			self._c_wheel[column] = [[] for index in range(3)]
			for row in range(3):
				self._c_wheel[column][row] = {'log': 0, 'value': 0, 'mode':0, 'white': 0, 'green': 0, 'custom':'00000000', 'pn':' ', 'pv': '0'}
	

	def _send_c_knob(self, index, value=0):
		self._send('c_knob', index, value)
	

	def _send_c_key(self, index, value=0):
		self._send('c_key', index, value)
	

	def _send_c_grid(self, column, row, value=0):
		self._send('c_grid', column, row, value)
	

	def _send_c_dial(self, column, row, value=0):
		self._send('c_dial', column, row, value)
	

	def _send_c_dial_button(self, column, row, value=0):
		if row > 0:
			self._send('c_dial_button', column, row-1, value)
	

	def receive_c_key(self, index, value=0):
		if self._c_key[index] != value:
			self._c_key[index] = value
			for host in self._active_host:
				host._send_c_key(index, value)
	

	def receive_c_grid(self, column, row, value=0):
		if self._c_grid[column][row] != value:
			self._c_grid[column][row] = value
			for host in self._active_host:
				host._send_c_grid(column, row, value)
	

	def receive_c_grid_row(self, row, value=0):
		g_len = len(self._c_grid)
		for column in xrange(g_len):
			self._c_grid[column][row] = value
		for host in self._active_host:
			for column in xrange(g_len):
				host._send_c_grid(column, row, value)
	

	def receive_c_grid_column(self, column, value=0):
		g_len = len(self._c_grid[0])
		for row in xrange(g_len):
			self._c_grid[column][row] = value
		for host in self._active_host:
			for row in xrange(g_len):
				host._send_c_grid(column, row, value)
	

	def receive_c_grid_all(self, value=0):
		g_len = len(self._c_grid)
		g_ht = len(self._c_grid[0])
		for column in xrange(g_len):
			for row in xrange(g_ht):
				self._c_grid[column][row] = value
		for host in self._active_host:
			for column in xrange(g_len):
				for row in xrange(g_ht):
					host._send_c_grid(column, row, value)
	

	def receive_mask_c_key(self, num, value=-1):
		if value > -1:
			for host in self._active_host:
				host._send_c_key(num, value)
		else:
			for host in self._active_host:
				host._send_c_key(num, int(self._c_key[num]))
	

	def receive_mask_c_grid(self, column, row, value=-1):
		if value > -1:
			for host in self._active_host:
				host._send_c_grid(column, row, value)
		else:
			for host in self._active_host:
				host._send_c_grid(column, row, int(self._c_grid[column][row]))
	

	def receive_mask_c_column(self, column, value=-1):
		if value > -1:
			for host in self._active_host:
				for index in xrange(4):
					host._send_c_grid(column, index, value)
		else:
			for host in self._active_host:
				for index in xrange(4):
					host._send_c_grid(column, index, self._c_grid[column][index])
	

	def receive_mask_c_row(self, row, value=-1):
		if value > -1:
			for host in self._active_host:
				for index in xrange(4):
					host._send_c_grid(index, row, value)
		else:
			for host in self._active_host:
				for index in xrange(4):
					host._send_c_grid(index, row, self._c_grid[index][row])
	

	def receive_mask_c_all(self, value=-1):
		if value > -1:
			for host in self._active_host:
				for column in xrange(4):
					for row in xrange(4):
						host._send_c_grid(column, row, value)
		else:
			for host in self._active_host:
				for column in xrange(4):
					for row in xrange(4):
						host._send_c_grid(column, row, self._c_grid[index][row])
	

	def receive_c_wheel(self, number, parameter, value):
		column = number%4
		row = int(number/4)
		if self._c_wheel[column]:
			if self._c_wheel[column][row]:
				wheel = self._c_wheel[column][row]
		 		wheel[parameter] = value
				if parameter!='white':
					for host in self._active_host:
						host._send_c_wheel(column, row, wheel, parameter)
				elif row > 0:
					for host in self._active_host:
						host._send_c_wheel(column, row, wheel, parameter)
	

	def _send_c_dial(self, column, row, value):
		self._send('c_dial', column, row, value)
	

	def _send_c_dial_button(self, column, row, value):
		if row > 0:
			self._send('c_dial_button', column, row-1, value)
	

	def set_c_absolute_mode(self, val=1):
		#self._host.log_message('client set absolute mode ' + str(val))
		self._c_absolute_mode = val
		if self._enabled:
			for host in self._active_host:
				if 'set_c_absolute_mode' in dir(host):
					host.set_c_absolute_mode(self._c_absolute_mode)
	

	def set_c_local_ring_control(self, val = 0):
		self._c_local_ring_control = val
		if self._enabled:
			for host in self._active_host:
				if 'set_c_local_ring_control' in dir(host):
					host.set_c_local_ring_control(self._c_local_ring_control)
	

	def receive_mod_color(self, val=0):
		#self._host.log_message('mod color' + str(val))
		if val != 1:
			self._mod_color = val
			for host in self._active_host:
				if '_display_mod_colors' in dir(host):
					host._display_mod_colors()
	

	def _mod_dial_parameter(self):
		param = None
		if not self.device == None:
			for parameter in self.device.parameters:
				if (parameter.original_name == 'moddial'):
					param = parameter
					break
		return param
	

	def send_midi(self, Type, num, val):
		self._host.send_midi(Type, num, val)
	


	"""Codec specific methods"""
	def _send_dial(self, column, row, value=0):
		self._send('dial', column, row, value)
	

	def _send_dial_button(self, column, row, value=0):
		if column < 8 and row < 4:
			self._send('dial_button', column, row, value)
		elif row is 4:
			self._send('column_button', column, value)
		else:
			self._send('row_button', row, value)	
	

	def receive_wheel(self, number, parameter, value):
		column = number%9
		row = int(number/9)
		if self._wheel[column]:
			if self._wheel[column][row]:
				self._wheel[column][row][parameter] = value
				#if self.is_active():
				if parameter!='white':
					for host in self._active_host:
						host._send_wheel(column, row, self._wheel[column][row], parameter)
				elif row > -1:
					for host in self._active_host:
						host._send_wheel(column, row, self._wheel[column][row], parameter)
	

	def set_local_ring_control(self, val = 1):
		#self._host.log_message('client set local ring ' + str(val))
		self._local_ring_control = val
		if self._enabled:
			for host in self._active_host:
				if 'set_local_ring_control' in dir(host):
					host.set_local_ring_control(self._local_ring_control)
	

	def set_absolute_mode(self, val = 1):
		#self._host.log_message('client set absolute mode ' + str(val))
		self._absolute_mode = val
		if self._enabled:
			for host in self._active_host:
				if 'set_absolute_mode' in dir(host):
					host.set_absolute_mode(self._absolute_mode)
	


	"""MonoDevice integration"""
	def receive_device(self, command, args0 = None, args1 = None, args2 = None):
		if command in dir(self._device_component):
			getattr(self._device_component, command)(args0, args1, args2)
	


