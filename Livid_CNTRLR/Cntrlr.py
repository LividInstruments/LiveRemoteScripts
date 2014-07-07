# by amounra 0513 : http://www.aumhaa.com

from __future__ import with_statement
import Live
import time
import math
import sys

""" _Framework files """
from _Framework.ButtonElement import ButtonElement # Class representing a button a the controller
from _Framework.ButtonMatrixElement import ButtonMatrixElement # Class representing a 2-dimensional set of buttons
from _Framework.ChannelStripComponent import ChannelStripComponent # Class attaching to the mixer of a given track
from _Framework.ClipSlotComponent import ClipSlotComponent # Class representing a ClipSlot within Live
from _Framework.CompoundComponent import CompoundComponent # Base class for classes encompasing other components to form complex components
from _Framework.ControlElement import ControlElement # Base class for all classes representing control elements on a controller 
from _Framework.ControlSurface import ControlSurface # Central base class for scripts based on the new Framework
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent # Base class for all classes encapsulating functions in Live
from _Framework.DeviceComponent import DeviceComponent # Class representing a device in Live
from _Framework.EncoderElement import EncoderElement # Class representing a continuous control on the controller
from _Framework.InputControlElement import * # Base class for all classes representing control elements on a controller
from VCM600.MixerComponent import MixerComponent # Class encompassing several channel strips to form a mixer
from _Framework.ModeSelectorComponent import ModeSelectorComponent # Class for switching between modes, handle several functions with few controls
from _Framework.NotifyingControlElement import NotifyingControlElement # Class representing control elements that can send values
from _Framework.SceneComponent import SceneComponent # Class representing a scene in Live
from _Framework.SessionComponent import SessionComponent # Class encompassing several scene to cover a defined section of Live's session
from _Framework.SessionZoomingComponent import DeprecatedSessionZoomingComponent as SessionZoomingComponent # Class using a matrix of buttons to choose blocks of clips in the session
from _Framework.SliderElement import SliderElement # Class representing a slider on the controller
from VCM600.TrackEQComponent import TrackEQComponent # Class representing a track's EQ, it attaches to the last EQ device in the track
from VCM600.TrackFilterComponent import TrackFilterComponent # Class representing a track's filter, attaches to the last filter in the track
from _Framework.TransportComponent import TransportComponent # Class encapsulating all functions in Live's transport section
from _Framework.M4LInterfaceComponent import M4LInterfaceComponent

"""Imports from the Monomodular Framework"""
from _Mono_Framework.CodecEncoderElement import CodecEncoderElement
from _Mono_Framework.EncoderMatrixElement import EncoderMatrixElement
from _Mono_Framework.MonoChopperComponent import MonoChopperComponent
from _Mono_Framework.MonoBridgeElement import MonoBridgeElement
from _Mono_Framework.MonoButtonElement import MonoButtonElement
from _Mono_Framework.MonoEncoderElement import MonoEncoderElement
from _Mono_Framework.ResetSendsComponent import ResetSendsComponent
from _Mono_Framework.DetailViewControllerComponent import DetailViewControllerComponent
from _Mono_Framework.DeviceSelectorComponent import DeviceSelectorComponent
from _Mono_Framework.MonomodComponent import MonomodComponent
from _Mono_Framework.MonoDeviceComponent import MonoDeviceComponent
from _Mono_Framework.SwitchboardElement import SwitchboardElement
from _Mono_Framework.MonoClient import MonoClient
from _Mono_Framework.Debug import *
from _Mono_Framework.LiveUtils import *

"""Custom files, overrides, and files from other scripts"""

from _Generic.Devices import *
from MonoDeviceComponent import MonoDeviceComponent
from ModDevices import *
from Map import *



""" Here we define some global variables """
switchxfader = (240, 00, 01, 97, 02, 15, 01, 247)
switchxfaderrgb = (240, 00, 01, 97, 07, 15, 01, 247)
assigncolors = (240, 00, 01, 97, 07, 34, 00, 07, 03, 06, 05, 01, 02, 04, 247)
assign_default_colors = (240, 00, 01, 97, 07, 34, 00, 07, 06, 05, 01, 04, 03, 02, 247)
check_model = (240, 126, 127, 6, 1, 247)


factoryreset = (240,0,1,97,8,6,247)
btn_channels = (240, 0, 1, 97, 8, 19, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, 0, 247);
enc_channels = (240, 0, 1, 97, 8, 20, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, 247);
SLOWENCODER = (240, 0, 1, 97, 8, 30, 69, 00, 247)
NORMALENCODER = (240, 0, 1, 97, 8, 30, 00, 00, 247)
FASTENCODER = (240, 0, 1, 97, 8, 30, 04, 00, 247)


class ShiftModeComponent(ModeSelectorComponent):


	def __init__(self, script, callback, *a, **k):
		super(ShiftModeComponent, self).__init__(*a, **k)
		self._script = script
		self.update = callback
		self._modes_buttons = []
		self._last_mode = 0
		self._set_protected_mode_index(0)
	

	def set_mode_buttons(self, buttons):
		for button in self._modes_buttons:
			button.remove_value_listener(self._mode_value)
		self._modes_buttons = []
		if (buttons != None):
			for button in buttons:
				assert isinstance(button, ButtonElement or FlashingButtonElement)
				identify_sender = True
				button.add_value_listener(self._mode_value, identify_sender)
				self._modes_buttons.append(button)
	

	def number_of_modes(self):
		return 5
	

	def set_mode(self, mode):
		assert isinstance(mode, int)
		mode += 1
		assert (mode in range(self.number_of_modes()))
		if (self._mode_index != mode):
			self._mode_index = mode
			self.update()
		elif (self._mode_index != 0):
			self._mode_index = 0
			self.update()
	

	def _mode_value(self, value, sender):
		assert (len(self._modes_buttons) > 0)
		assert isinstance(value, int)
		assert isinstance(sender, ButtonElement)
		assert (self._modes_buttons.count(sender) == 1)
		if ((value is not 0) or (not sender.is_momentary())):
			self.set_mode(self._modes_buttons.index(sender))
	


class MonomodModeComponent(ModeSelectorComponent):
	__module__ = __name__
	__doc__ = ' Class for switching between modes, handle several functions with few controls '


	def __init__(self, script, *a, **k):
		super(MonomodModeComponent, self).__init__(*a, **k)
		self._script = script
		self._set_protected_mode_index(0)
	

	def set_mode_buttons(self, buttons):
		for button in self._modes_buttons:
			button.remove_value_listener(self._mode_value)
		self._modes_buttons = []
		if (buttons != None):
			for button in buttons:
				assert isinstance(button, ButtonElement)
				identify_sender = True
				button.add_value_listener(self._mode_value, identify_sender)
				self._modes_buttons.append(button)
			for index in range(len(self._modes_buttons)):
				if (index == self._mode_index):
					self._modes_buttons[index].turn_on()
				else:
					self._modes_buttons[index].turn_off()
	

	def set_mode_toggle(self, button):
		assert ((button == None) or isinstance(button, ButtonElement or FlashingButtonElement))
		if (self._mode_toggle != None):
			self._mode_toggle.remove_value_listener(self._toggle_value)
		self._mode_toggle = button
		if (self._mode_toggle != None):
			self._mode_toggle.add_value_listener(self._toggle_value)
	

	def number_of_modes(self):
		return 2
	


class CntrlrDetailViewControllerComponent(DetailViewControllerComponent):


	def __init__(self, script, *a, **k):
		super(CntrlrDetailViewControllerComponent, self).__init__(*a, **k)
		self._script = script
	

	def _nav_value(self, value, sender):
		super(CntrlrDetailViewControllerComponent, self)._nav_value(value, sender)
		if (self.is_enabled() and (not self._shift_pressed)):
			if ((not sender.is_momentary()) or (value != 0)):
				modifier_pressed = True
				if not ((not self.application().view.is_view_visible('Detail')) or (not self.application().view.is_view_visible('Detail/DeviceChain'))):
					self._script._update_selected_device()
	


class CntrlrSwitchboardElement(SwitchboardElement):


	def __init__(self, *a, **k):
		super(CntrlrSwitchboardComponent, self).__init__(*a, **k)
	


class CntrlrMonoDevice(MonoDeviceComponent):


	def __init__(self, *a, **k):
		super(CntrlrMonoDevice, self).__init__(*a, **k)
	


class CntrlrMonoClient(MonoClient):


	def __init__(self, *a, **k):
		super(CntrlrMonoClient, self).__init__(*a, **k)
		self._raw = False
		self._device_component = CntrlrMonoDevice(self, MOD_BANK_DICT, MOD_TYPES)
	

	def _banner(self):
		pass
	

	def disconnect_client(self, *a, **k):
		super(CntrlrMonoClient, self).disconnect_client(*a, **k)
		if not self._mod_dial == None:
			if self._mod_dial._parameter is self._mod_dial_parameter:
				self._mod_dial.release_parameter()
	

	def _send_c_key(self, index, value, *a, **k):
		self._send('key', index, value)
		if self._raw is True:
			control = self._host._host._keys[index]
			if control != None:
				self._send('raw', control._msg_type + control._original_channel, control._original_identifier, value)
	

	def _send_c_grid(self, column, row, value, *a, **k):
		self._send('grid', column, row, value)
		if self._raw is True:
			control = self._host._host._grid.get_button(column, row)
			if control != None:
				self._send('raw', control._msg_type + control._original_channel, control._original_identifier, value)
	

	def _send_c_dial(self, column, row, value, *a, **k):
		self._send('dial', column, row, value)
		if self._raw is True:
			control = self._host._host._dial_matrix.get_dial(column, row)
			if control != None:
				self._send('raw', control._msg_type + control._original_channel, control._original_identifier, value)
	

	def _send_c_dial_button(self, column, row, value, *a, **k):
		if row > 0:
			self._send('dial_button', column, row-1, value)
			if self._raw is True:
				control = self._host._host._dial_button_matrix.get_button(column, row)
				if control != None:
					self._send('raw', control._msg_type + control._original_channel, control._original_identifier, value)
	

	def _send_key(self, *a):
		pass
	

	def _send_grid(self, *a):
		pass
	

	def _send_dial(self, *a):
		pass
	

	def _send_dial_button(self, *a):
		pass
	

	"""receive methods (from m4l)"""
	def receive_key(self, *a, **k):
		super(CntrlrMonoClient, self).receive_c_key(*a, **k)
	

	def receive_grid(self, *a, **k):
		super(CntrlrMonoClient, self).receive_c_grid(*a, **k)
	

	def receive_grid_row(self, *a, **k):
		super(CntrlrMonoClient, self).receive_c_grid_row(*a, **k)
	

	def receive_grid_column(self, *a, **k):
		super(CntrlrMonoClient, self).receive_c_grid_column(*a, **k)
	

	def receive_grid_all(self, *a, **k):
		super(CntrlrMonoClient, self).receive_c_grid_all(*a, **k)
	

	def receive_mask_key(self, *a, **k):
		super(CntrlrMonoClient, self).receive_mask_c_key(*a, **k)
	

	def receive_mask_grid(self, *a, **k):
		super(CntrlrMonoClient, self).receive_mask_c_grid(*a, **k)
	

	def receive_mask_column(self, *a, **k):
		super(CntrlrMonoClient, self).receive_mask_c_column(*a, **k)
	

	def receive_mask_row(self, row, value):
		super(CntrlrMonoClient, self).receive_mask_c_row(*a, **k)
	

	def receive_mask_all(self, *a, **k):
		super(CntrlrMonoClient, self).receive_mask_c_all(*a, **k)
	

	def receive_wheel(self, *a, **k):
		super(CntrlrMonoClient, self).receive_c_wheel(*a, **k)
	

	def set_local_ring_control(self, *a, **k):
		super(CntrlrMonoClient, self).set_c_local_ring_control(*a, **k)
	

	def set_absolute_mode(self, *a, **k):
		super(CntrlrMonoClient, self).set_c_absolute_mode(*a, **k)
	

	def receive_mod_color(self, val):
		if val != 1:
			self._mod_color = val
			self._host.shift_update()
	

	"""raw data integration"""
	def set_raw_enabled(self, value):
		self._raw = value > 0
		#self._host.log_message('raw enabled' + str(self._raw))
		if(self._raw is True):
			self._update_controls_dictionary()
	

	def receive_raw(self, Type, Identifier, value):
		#self._host.log_message('recieve raw' + str(Type) + str(Identifier) + str(value))
		if self._controls[Type]:
			if Identifier in self._controls[Type]:
				self._controls[Type][Identifier](value)
	

	def _update_controls_dictionary(self):
		if self._host._host != None:
			self._controls = [{}, {}]
			if self._control_defs['grid'] != None:
				for column in range(self._control_defs['grid'].width()):
					for row in range(self._control_defs['grid'].height()):
						button = self._control_defs['grid'].get_button(column, row)
						if button != None:
							self._controls[0][button._original_identifier]=self._make_grid_call(column, row)
			if self._control_defs['keys'] != None:
				for index in range(len(self._control_defs['keys'])):
					key = self._control_defs['keys'][index]
					if key != None:
						self._controls[0][key._original_identifier]=self._make_key_call(index)
			if self._control_defs['dials'] != None:
				for index in range(12):
					column = index%4
					row = int(index/4)
					dial = self._control_defs['dials'].get_dial(column, row)
					if dial != None:
						self._controls[1][dial._original_identifier]=self._make_dial_call(index)
			if self._control_defs['buttons'] != None:
				for index in range(8):
					column = index%4
					row = int(index/4)+1
					button = self._control_defs['buttons'].get_button(column, row)
					if button != None:
						self._controls[0][button._original_identifier]=self._make_dial_button_call(index+4)
	

	def _make_grid_call(self, column, row):
		def recieve_grid(value):
			#self._host.log_message('receive grid' + str(value) + str(column) + str(row))
			self.receive_c_grid(column, row, value)
		return recieve_grid
		
	

	def _make_key_call(self, number):
		def receive_key(value):
			#self._host.log_message('receive key' + str(number) + str(value))
			self.receive_c_key(number, value)
		return receive_key
		
	

	def _make_dial_call(self, number):
		def receive_c_wheel(value):
			self.receive_wheel(number, 'value', value)
		return receive_wheel
		
	

	def _make_dial_button_call(self, number):
		def receive_c_wheel(value):
			self.receive_wheel(number, 'white', value)
		return receive_wheel
		
	


class CntrlrMonomodComponent(MonomodComponent):


	def __init__(self, *a, **k):
		super(CntrlrMonomodComponent, self).__init__(*a, **k)
	

	def _send_grid(self, *a):
		pass
	

	def _send_key(self, *a):
		pass
	


	def disconnect(self, *a, **k):
		self._release_mod_dials()
		super(CntrlrMonomodComponent, self).disconnect(*a, **k)
	

	def connect_to_clients(self, *a, **k):
		super(CntrlrMonomodComponent, self).connect_to_clients(*a, **k)
		for index in range(4):
			self._client[index]._mod_dial = (self._script._encoder[index])		#assign it a modDial so that we can control its modVolume from the unshifted CNTRLR
	

	def _select_client(self, *a, **k):
		super(CntrlrMonomodComponent, self)._select_client(*a, **k)		
		self._script.set_local_ring_control(self._active_client._c_local_ring_control)
		self._script.set_absolute_mode(self._active_client._c_absolute_mode)
		self._active_client._device_component.update()
	

	def on_enabled_changed(self, *a, **k):
		super(CntrlrMonomodComponent, self).on_enabled_changed(*a, **k)
		if self._active_client != None:
			if self.is_enabled():
				self._active_client._device_component.update()
				self._script.set_absolute_mode(self._active_client._c_absolute_mode)
				self._script.set_local_ring_control(self._active_client._c_local_ring_control)
			else:
				for control in self._parameter_controls:
					control.release_parameter()
				self._script.set_absolute_mode(1)
				self._script.set_local_ring_control(1)
	


	def _set_button_matrix(self, grid):
		assert isinstance(grid, (ButtonMatrixElement, type(None)))
		if grid != self._grid:
			if self._grid != None:
				self._grid.remove_value_listener(self._matrix_value)
			self._grid = grid
			if self._grid != None:
				self._grid.add_value_listener(self._matrix_value)
			self.update()
		return None
	

	def _matrix_value(self, value, x, y, is_momentary):	   #to be sent to client from controller
		assert (self._grid != None)
		assert (value in range(128))
		assert isinstance(is_momentary, type(False))
		if (self.is_enabled()):
			self._active_client._send_c_grid(x + self._x, y + self._y, value)
	

	def _update_grid(self):
		if self.is_enabled() and self._grid != None:
			for column in range(4):
				for row in range(4):
					self._send_c_grid(column, row, self._active_client._c_grid[column][row])
	


	def _alt_value(self, value):
		if self._shift_pressed == 0:
			self._alt_pressed = value != 0
			self._active_client._send('alt', int(self._alt_pressed))
			self.update()
	


	def _set_key_buttons(self, buttons):
		assert (buttons == None) or (isinstance(buttons, tuple))
		for key in self._keys:
			if key.value_has_listener(self._key_value):
				key.remove_value_listener(self._key_value)
		self._keys = []
		if buttons != None:
			assert len(buttons) == 32
			for button in buttons:
				assert isinstance(button, MonoButtonElement)
				self._keys.append(button)
				button.add_value_listener(self._key_value, True)
	

	def _key_value(self, value, sender):
		if self.is_enabled():
			self._active_client._send_c_key(self._keys.index(sender), int(value!=0))
	

	def _update_keys(self):
		for index in range(32):
			self._send_c_key(index, self._active_client._c_key[index])
	
	


	def _set_knobs(self, knobs):
		assert (knobs == None) or (isinstance(knobs, tuple))
		for knob in self._knobs:
			if knob.has_value_listener(self._knob_value):
				knob.remove_value_listener(self._knob_value)
		self._knobs = []
		if knobs != None:
			assert len(knobs) == 24
			for knob in knobs:
				assert isinstance(knob, EncoderElement)
				self._knobs.append(knob)
				knob.add_value_listener(self._knob_value, True)
	

	def _knob_value(self, value, sender):
		if self.is_enabled():
			self._active_client._send_c_knob(self._knobs.index(sender), value)
	


	def _dial_matrix_value(self, value, x, y):
		if self.is_enabled() and self._active_client != None:
			if self._script._absolute_mode == 0:
				value = RELATIVE[int(value == 1)]
			self._active_client._send_c_dial(x, y, value)
	

	def _dial_button_matrix_value(self, value, x, y, force):
		if (self.is_enabled()) and (self._active_client != None):
			self._active_client._send_c_dial_button(x, y, value)
	

	def _reset_encoder(self, coord):
		self._dial_matrix.get_dial(coord[0], coord[1])._reset_to_center()
	


	"""CNTRLR specific methods"""
	def _send_c_grid(self, column, row, value):		#to be sent to controller from client
		if self.is_enabled() and self._grid != None:
			if column in range(self._x, self._x + 4):
				if row in range(self._y, self._y + 4):
					self._grid.get_button(column - self._x, row - self._y).send_value(int(self._colors[value]))

	

	def _send_c_key(self, index, value):
		if self.is_enabled():
			#if (self._shift_pressed > 0) or (self._locked > 0):
			#	self._grid.get_button(index, 7).send_value(int(self._colors[value]))
			if  self._keys != None and len(self._keys) > index:
				self._keys[index].send_value(int(self._colors[value]))
	

	def _send_c_wheel(self, column, row, wheel, parameter=None):		#to be sent to controller from client
		if self.is_enabled() and wheel != None: 
			if column < 4 and row < 3:
				dial = self._dial_matrix.get_dial(column, row)
				if(parameter=='value'):
					dial._ring_value = int(wheel['value'])
				dial._ring_mode = int(wheel['mode'])
				dial._ring_green = int(wheel['green']!=0)
				dial._ring_log = int(wheel['log'])
				if(parameter=='custom'):
					dial._ring_custom = dial._calculate_custom(str(wheel['custom']))
			self._dial_button_matrix.send_value(column, row, wheel['white'])
			if(self._script._absolute_mode > 0) and (not self._active_client._device_component.is_enabled()):
				dial.send_value(wheel['log'], True)
	

	def _update_c_wheel(self):
		if self._dial_button_matrix != None:
			for column in range(4):
				for row in range(3):
					self._send_c_wheel(column, row, self._active_client._c_wheel[column][row])
					if not self._active_client._device_component.is_enabled():
						self._send_to_lcd(column, row, self._active_client._c_wheel[column][row])
						#self._script.log_message('dial value update' +str(column) + str(row) + str(self._active_client._wheel[column][row]['value']))
	

	def set_c_local_ring_control(self, val = 1):
		self._c_local_ring_control = (val!=0)
		self._script.set_local_ring_control(self._c_local_ring_control)
	

	def set_c_absolute_mode(self, val=1):
		self._c_absolute_mode = (val!=0)
		self._script.set_absolute_mode(self._c_absolute_mode)
	


	def _release_mod_dials(self):
		if not self._client is None:
			for index in range(4):										#for each of our 4 clients:
				if not self._client[index]._mod_dial == None:								#if the client has a modDial assigned to it
					self._client[index]._mod_dial.release_parameter()						#remove the modDial's parameter assignment
	

	def _assign_mod_dials(self):
		if not self._client is None:
			for index in range(4):					#recursion to contain all available clients
				param = self._client[index]._mod_dial_parameter()	#param is a local variable, and we assign its value to the mod_dial_parameter (this is handled by each individual client module)
				#self._script.log_message('mod dial param ' + str(param))
				if not self._client[index]._mod_dial == None:					#if the client has been assigned a mod dial (which it should have been in setup_mod() )
					if not param == None:										#if the param variable was properly assigned in the client module
						self._client[index]._mod_dial.connect_to(param)			#connect the physical control to the parameter (this should be the moddial parameter in the m4l patch)
					else:
						self._client[index]._mod_dial.release_parameter()		#if the param was None, release the physical control from any assignments
			self._script.request_rebuild_midi_map()
	

	def _display_mod_colors(self):
		if not self._client is None:
			for index in range(4):							#set up a recursion of 4
				self._script._shift_mode._modes_buttons[index].send_value(self._client[index]._mod_color)		#update the modLEDs to display the color assigned to its contained mod
			if self._is_enabled:
				self._script._shift_mode._modes_buttons[self._client.index(self._active_client)].send_value(8)
		else:
			for index in range(4):
				self._script._shift_mode._modes_buttons[index].send_value(0)
	



class Cntrlr(ControlSurface):
	__module__ = __name__
	__doc__ = " Monomodular controller script for Livid CNTRLR "


	def __init__(self, *a, **k):
		super(Cntrlr, self).__init__(*a, **k)
		"""MonoComponent specific variables - best not change these unless you know what you're doing"""
		self._version_check = 'b994'
		self._host_name = 'Cntrlr'
		self._color_type = 'OhmRGB'
		self._hosts = []
		self.hosts = []
		self._client = [None for index in range(4)]
		self._active_client = None
		self._rgb = 0 									##will change which color scheme is used, 0 is Livid 1 is AumHaa 2 is Monochrome(deprecated)
		self._timer = 0									#used for flashing states, and is incremented by each call from self._update_display()
		self._touched = 0								#used by the LCD patch to determine the last time a control was changed
		self._local_ring_control = True					#used by CodecEncoderElement to determine whether individual ring LEDs are addressable
		self.set_local_ring_control(1)					#initialize the local_control state of the encoder rings
		self._absolute_mode = 1							#used by CodecEncoderElement to determine whether inc/dec or absolute changes are sent from CNTRLR
		self.flash_status = 1							#used to determine whether button LED's use flashing states or not
		self._device_selection_follows_track_selection = FOLLOW
		with self.component_guard():
			"""Initialization methods - comments included in the corresponding method"""
			self._setup_monobridge()
			self._setup_controls()
			self._setup_m4l_interface()
			self._setup_transport_control() 
			self._setup_mixer_control()
			self._setup_session_control()
			self._assign_session_colors()
			self._setup_device_control()
			self._setup_device_selector()
			self._setup_mod()
			self._setup_switchboard()
			self._setup_chopper()
			self._setup_modes() 
		self.schedule_message(1, self._open_log)
		self.song().view.add_selected_track_listener(self._update_selected_device)		#Add a listener so that when the track content changes our device selection will aslo be updated
	

	"""script initialization methods"""

	def _open_log(self):
		self.log_message("<<<<<<<<<<<<<<<<<<<<= " + str(self._host_name) + " " + str(self._version_check) + " log opened =>>>>>>>>>>>>>>>>>>>") 
		self.show_message(str(self._host_name) + ' Control Surface Loaded')
	

	"""monobridge is used to send parameter names and values to the m4l LCD patch"""
	def _setup_monobridge(self):
		self._monobridge = MonoBridgeElement(self)
		self._monobridge.name = 'MonoBridge'
	

	"""it is valuable to set up all of our controls at the beginning of our script so that """
	"""don't make the mistake of double assignments of identifiers, which is not tolerated by """
	"""the components they are assigned to.  Each control element will also be named, so that it """
	"""can be accessed via m4l if we need to listen to it or send messages to it"""
	def _setup_controls(self):
		is_momentary = True		#this variable will be used when sending arguments to the __init__ function of the modules we are creating instances of
		"""since we have several controls of each type, we'll first need to set up some arrays to hold each collection of controls"""
		"""initially, we set each one to None as a placeholder.  We could, in fact, create them at the same time as creating these functions in
			the following manner:
				self._fader = [MonoEncoderElement(MIDI_CC_TYPE, CHANNEL, CNTRLR_FADERS[index], Live.MidiMap.MapMode.absolute, 'Fader_' + str(index), index, self) for index in range(8)]
			Instead, we'll name them later so that the script is a little more readable."""
		
		self._fader = [None for index in range(8)]
		self._dial_left = [None for index in range(12)]
		self._dial_right = [None for index in range(12)]
		self._encoder = [None for index in range(12)]	
		self._encoder_button = [None for index in range(12)]	
		self._grid = [None for index in range(16)]
		self._button = [None for index in range(32)]
		
		"""Now that we have our arrays, we can fill them with the controltypes that we'll be using."""
		for index in range(8):
			self._fader[index] = MonoEncoderElement(MIDI_CC_TYPE, CHANNEL, CNTRLR_FADERS[index], Live.MidiMap.MapMode.absolute, 'Fader_' + str(index), index, self)
		self._knobs = []
		for index in range(12):
			self._dial_left[index] = MonoEncoderElement(MIDI_CC_TYPE, CHANNEL, CNTRLR_KNOBS_LEFT[index], Live.MidiMap.MapMode.absolute, 'Dial_Left_' + str(index), CNTRLR_KNOBS_LEFT[index], self)
			self._knobs.append(self._dial_left[index])
		for index in range(12):
			self._dial_right[index] = MonoEncoderElement(MIDI_CC_TYPE, CHANNEL, CNTRLR_KNOBS_RIGHT[index], Live.MidiMap.MapMode.absolute, 'Dial_Right_' + str(index), CNTRLR_KNOBS_RIGHT[index], self)
			self._knobs.append(self._dial_right[index])
		for index in range(12):
			self._encoder[index] = CodecEncoderElement(MIDI_CC_TYPE, CHANNEL, CNTRLR_DIALS[index], Live.MidiMap.MapMode.absolute, 'Encoder_' + str(index), CNTRLR_DIALS[index], self)
		for index in range(12):
			self._encoder_button[index] = MonoButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, CNTRLR_DIAL_BUTTONS[index], 'Encoder_Button_' + str(index), self)
		for index in range(16):
			self._grid[index] = MonoButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, CNTRLR_GRID[index], 'Grid' + str(index), self)
		for index in range(32):
			self._button[index] = MonoButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, CNTRLR_BUTTONS[index], 'Button_' + str(index), self)
		
		"""We'll also need to assign some of our controls to ButtonMatrixElements so that we can use them with the Session Zoom and the Mod components"""
		"""We use the same formula here:  first we create the holders:"""
		self._matrix = ButtonMatrixElement()				#this is a standard _Framework object used by many of the other scripts
		self._matrix.name = 'Matrix'
		self._dial_matrix = EncoderMatrixElement(self)		#this is a special Mono object, used specifically for the mod components
		self._dial_matrix.name = 'Dial_Matrix'
		self._dial_button_matrix = ButtonMatrixElement()	#this is a special Mono object, used specifically for the mod components
		self._dial_button_matrix.name = 'Dial_Button_Matrix'
		
		"""And then we fill the with the control elements that are assigned to them"""
		for row in range(4):		#we have 4 rows, and 4 columns, forming the 4x4 grid in the center of the controller
			button_row = []			#since the matrix is two dimensional, first we create the outer array,
			for column in range(4):
				button_row.append(self._grid[(row*4) + column])		#then we create the inner array.  The process is the same for the other controls here.
			self._matrix.add_row(tuple(button_row)) 				#add_row() is a method of the ButtonMatrixElement.  You can look in its parent module to see how it works
		for row in range(3):
			dial_row = []
			for column in range(4):
				dial_row.append(self._encoder[(row*4) + column])
			self._dial_matrix.add_row(tuple(dial_row))
		for row in range(3):
			dial_button_row = []
			for column in range(4):
				dial_button_row.append(self._encoder_button[(row*4) + column])
			self._dial_button_matrix.add_row(tuple(dial_button_row))
		self._key_matrix = ButtonMatrixElement()
		button_row = []						#since we only use one row for the chopper, we can define a 1 dimensional button matrix for this one.   
		for column in range(16):			#We use the ButtonMatrixObject because it takes care of setting up callbacks for all the buttons easily when we need them later
			button_row.append(self._button[16 + column])
		self._key_matrix.add_row(tuple(button_row))
	

	def _setup_m4l_interface(self):
		self._m4l_interface = M4LInterfaceComponent(controls=self.controls, component_guard=self.component_guard)
		self.get_control_names = self._m4l_interface.get_control_names
		self.get_control = self._m4l_interface.get_control
		self.grab_control = self._m4l_interface.grab_control
		self.release_control = self._m4l_interface.release_control
	

	"""the transport component allows us to assign controls to transport functions in Live"""
	def _setup_transport_control(self):
		self._transport = TransportComponent() 
		self._transport.name = 'Transport'
	

	"""the mixer component corresponds and moves with our selection in Live, and allows us to assign physical controls"""
	"""to Live's mixer functions without having to make all the links ourselves"""
	def _setup_mixer_control(self):
		is_momentary = True
		self._num_tracks = (4) 								#A mixer is one-dimensional; 
		self._mixer = MixerComponent(4, 2)		#These values represent the (Number_of_tracks, Number_of_returns, EQ_component, Filter_component)
		self._mixer.name = 'Mixer'							#We name everything that we might want to access in m4l
		self._mixer.set_track_offset(0) 					#Sets start point for mixer strip (offset from left)
		for index in range(4):								
			self._mixer.channel_strip(index).set_volume_control(self._fader[index])		#Since we gave our mixer 4 tracks above, we'll now assign our fader controls to it						
			self._mixer.channel_strip(index).name = 'Mixer_ChannelStrip_' + str(index)	#We also name the individual channel_strip so we can access it
			self._mixer.track_eq(index).name = 'Mixer_EQ_' + str(index)					#We also name the individual EQ_component so we can access it
			self._mixer.channel_strip(index)._invert_mute_feedback = True				#This makes it so that when a track is muted, the corresponding button is turned off
		self.song().view.selected_track = self._mixer.channel_strip(0)._track 			#set the selected strip to the first track, so that we don't, for example, try to assign a button to arm the master track, which would cause an assertion error
		self._send_reset = ResetSendsComponent(self)		#This creates a custom MonoComponent that allows us to reset all the sends on a track to zero with a single button
		self._send_reset.name = 'Sends_Reset'				#We name it so that we can access it from m4l
	

	"""the session component represents a grid of buttons that can be used to fire, stop, and navigate clips in the session view"""
	def _setup_session_control(self):
		is_momentary = True
		num_tracks = 4															#we are working with a 4x4 grid,	
		num_scenes = 4 															#so the height and width are both set to 4
		self._session = SessionComponent(num_tracks, num_scenes)				#we create our SessionComponent with the variables we set above it
		self._session.name = "Session"											#we name it so we can access it in m4l
		self._session.set_offsets(0, 0)											#we set the initial offset to the far left, top of the session grid
		self._session.set_stop_clip_value(STOP_CLIP[self._rgb])			#we assign the colors that will be displayed when the stop_clip button is pressed. This value comes from CNTRLR_Map.py, which is imported in the header of our script
		self._scene = [None for index in range(4)]								#we create an array to hold the Scene subcomponents so that we can get to them if we need them.
		for row in range(num_scenes):											#now we'll fill the array with different objects that were created when we called the SessionComponent() module
			self._scene[row] = self._session.scene(row)							#each session row is a SceneComponent
			self._scene[row].name = 'Scene_' + str(row)							#name it so we can access it in m4l
			for column in range(num_tracks):									#now we'll create holders and names for the contents of each scene
				clip_slot = self._scene[row].clip_slot(column)					#we use our assignment of the scene above to gain access to the individual clipslots.  Here, we are just assigning 'clip_slot' each time as a local variable so we can manipulated it's properties
				clip_slot.name = str(column) + '_Clip_Slot' + str(row)			#name it so that we can acces it in m4l
				clip_slot.set_triggered_to_play_value(CLIP_TRG_PLAY[self._rgb])	#set its triggered to play color
				clip_slot.set_triggered_to_record_value(CLIP_TRG_REC[self._rgb])#set its triggered to record color
				clip_slot.set_stopped_value(CLIP_STOP[self._rgb])				#set its stop color
				clip_slot.set_started_value(CLIP_STARTED[self._rgb])			#set its started color
				clip_slot.set_recording_value(CLIP_RECORDING[self._rgb])		#set its recording value
		self.set_highlighting_session_component(self._session)
		self._session.set_mixer(self._mixer)									#now we link the MixerComponent we created in _setup_mixer_control() to our session component so that they will follow each other when either is navigated
		self._session_zoom = SessionZoomingComponent(self._session)	 			#this creates the ZoomingComponent that allows navigation when the shift button is pressed
		self._session_zoom.name = 'Session_Overview'							#name it so we can access it in m4l
		self._session_zoom.set_stopped_value(ZOOM_STOPPED[self._rgb])			#set the zooms stopped color
		self._session_zoom.set_playing_value(ZOOM_PLAYING[self._rgb])			#set the zooms playing color
		self._session_zoom.set_selected_value(ZOOM_SELECTED[self._rgb])			#set the zooms selected color
		self._session_zoom.set_button_matrix(self._matrix)						#assign the ButtonMatrixElement that we created in _setup_controls() to the zooming component so that we can control it
		self._session_zoom.set_zoom_button(self._button[31])					#assign a shift button so that we can switch states between the SessionComponent and the SessionZoomingComponent
	

	"""this section is used so that we can reassign the color properties of each state.  Legacy, from the OhmModes script, to support either RGB or Monochrome"""
	def _assign_session_colors(self):
		num_tracks = 4
		num_scenes = 4 
		self._session.set_stop_clip_value(STOP_ALL[self._rgb])
		for row in range(num_scenes): 
			for column in range(num_tracks):
				self._scene[row].clip_slot(column).set_triggered_to_play_value(CLIP_TRG_PLAY[self._rgb])
				self._scene[row].clip_slot(column).set_triggered_to_record_value(CLIP_TRG_REC[self._rgb])
				self._scene[row].clip_slot(column).set_stopped_value(CLIP_STOP[self._rgb])
				self._scene[row].clip_slot(column).set_started_value(CLIP_STARTED[self._rgb])
				self._scene[row].clip_slot(column).set_recording_value(CLIP_RECORDING[self._rgb])		
		self._session_zoom.set_stopped_value(ZOOM_STOPPED[self._rgb])
		self._session_zoom.set_playing_value(ZOOM_PLAYING[self._rgb])
		self._session_zoom.set_selected_value(ZOOM_SELECTED[self._rgb])
		self.refresh_state()
	

	"""the device component allows us to assign encoders to the selected device in Live"""
	def _setup_device_control(self):
		self._device = DeviceComponent()			#create the device component
		self._device.name = 'Device_Component'		#name it so we can access it in m4l
		self._device._is_banking_enabled = self.device_is_banking_enabled(self._device)  #we do this to defeat some undesirable behavior in the DeviceComponent which defeats banking if no controls are assigned
		#self._device.set_device = self._device_set_device(self._device)
		self._device.update = self._device_update(self._device)
		self._device.set_parameter_controls(tuple([self._encoder[index+4] for index in range(8)]))		#set its controls to the bottom 8 encoders;  we use [index+4] to offset past the first 4 encoders
		self.set_device_component(self._device)		#assign our component to the control_surface main script;  this allows special updating, like being able to lock the devicecomponent to the currently selected device
		self._device_navigator = CntrlrDetailViewControllerComponent(self)		#this is a special component taken out of the APC scripts; its used to move from one device to another with the controller
		self._device_navigator.name = 'Device_Navigator'					#name it so that we can access it in m4l
		self._device_selection_follows_track_selection = FOLLOW				#_device_selection_follows_track_selection is a property of the main ControlSurface script, and does what it says it does.  The FOLLOW variable is taken from CNTRLR_Map.py
	

	"""the device selector component allows the user to set buttons that will automatically select a device based on its name"""
	"""its not used in the stock CNTRLR script, but it could easily be assigned to any buttons using the correct syntax"""
	"""for more information, check out the documentation for the MonOhm script"""
	def _setup_device_selector(self):
		self._device_selector = DeviceSelectorComponent(self)
		self._device_selector.name = 'Device_Selector'
	

	"""this section sets up the host environment that allows the controller to access different mods from the modButtons"""
	def _setup_mod(self):
		self._host = CntrlrMonomodComponent(self)						#the MonomodComponent is the bridge between the CNTRLR's controls and the client patches that connect to m4l
		self._host.name = 'Cntrlr_Host'						#name it so we can access it
		self.hosts = [self._host]								#since some CNTRLR's can have more than one grid to access its clients, we create an array to hold all of the hosts that are included in this script.  The CNTRLR only holds one.
		self._hosts = [self._host]								#this is redundant, and needs to be fixed
		self._host._set_parameter_controls(self._encoder)
		for index in range(4):									#now we create our clients that will be connected to the actual m4l mods
			self._client[index] = CntrlrMonoClient(self, index)		#create an instance, and pass it its index
			self._client[index].name = 'Client_' + str(index)	#name it so we can access it
			self._client[index]._mod_dial = (self._encoder[index])		#assign it a modDial so that we can control its modVolume from the unshifted CNTRLR
			self._client[index]._device_component = MonoDeviceComponent(self._client[index], MOD_BANK_DICT, MOD_TYPES)
			self._client[index]._control_defs = {'dials':self._dial_matrix, 'buttons':self._dial_button_matrix, 'grid':self._matrix, 'keys':self._button, 'knobs':self._knobs}  #assign controls that raw data will be addressed at
		self._active_client = self._client[0]					#select the first client as our active client
		self._active_client._is_active = True					#initialize its active state, used by MonomodComponent to determine its status when sending it messages
		self._host.connect_to_clients(self)						#connect our MonomodComponent to our clients now that they are set up and ready to go.
	

	"""the switchboard allows us to manage connections and disconnections between our clients and any mods that are currently installed in our Live project"""
	def _setup_switchboard(self):
		self._switchboard = SwitchboardElement(self, self._client)			#here we are passing the main script and the array of client modules we created above to create an instance of the switchboard controlelement
		self._switchboard.name = 'Switchboard'								#name it so we can access it in m4l
	

	"""the clipchopper component is a custom component we can access by switching modes"""
	def _setup_chopper(self):
		self._chopper = MonoChopperComponent(self, self._mixer)		#create the chopper module, and pass it our mixer so that we can use it to navigate which clip is being manipulated
		self._chopper.name = 'Chopper'					#name it so we can access it via m4l
		self._chopper._set_button_matrix(self._key_matrix)	#set its controls to the ButtonMatrixElement we created in _setup_controls()
	

	"""since there are many different configurations possible with the modButtons, we'll need to create a ModeSelectorComponent"""
	"""to manage the different states of our controller"""
	def _setup_modes(self):
		self._shift_mode = ShiftModeComponent(self, self.shift_update)			#here we call a new component by passing this module and its shift_update method
		self._shift_mode.name = 'Mod_Mode'										#name it so we can access it
		self._shift_mode.set_mode_buttons([self._encoder_button[index] for index in range(4)])		#set the mode buttons that we will use to change states
	


	"""cntrlr modes"""
	"""here we set up some methods that will be used to update the control assignments when we change between different modes"""
	
	"""this method is called everytime we change modes.  If we make any assignments in the other mode assignment methods, we"""
	"""have to be sure to remove them in this function.  This creates a 'blank slate' for all the CNTRLRs control elements"""
	def deassign_live_controls(self):
		#for index in range(4):
		#	if self._encoder[index].value_has_listener(self._client[index]._mod_dial_value):
		#		self._encoder[index].remove_value_listener(self._client[index]._mod_dial_value)


		"""THIS SECTION IS MISSING FROM THE ORIGINAL SCRIPT AND NEEDS TO BE FIXED...THE ASSIGNMENTS WERE MADE AT __init__"""
		for index in range(4):								
			self._mixer.channel_strip(index).set_volume_control(None)		#Since we gave our mixer 4 tracks above, we'll now assign our fader controls to it						
		for index in range(2):
			self._mixer.return_strip(index).set_volume_control(None)	#assign the right faders to control the volume of our return strips
		self._mixer.master_strip().set_volume_control(None)					#assign the far right fader to control our master channel strip
		self._mixer.set_prehear_volume_control(None)							#assign the remaining fader to control our prehear volume of the the master channel strip


		for index in range(4):											#for the left side of the mixer
			self._mixer.channel_strip(index).set_solo_button(None)		#remove the solo button assignments
			self._mixer.channel_strip(index).set_arm_button(None)		#remove the arm button assignments
			self._mixer.channel_strip(index).set_mute_button(None)		#remove the mute button assignments
			self._mixer.channel_strip(index).set_select_button(None)	#remove the select button assignments
		for column in range(4):	
			for row in range(4):
				self._scene[row].clip_slot(column).set_launch_button(None)	#remove the clip launch assignments
		self._send_reset.set_buttons(tuple([None for index in range(4)]))	#remove the send_reset button assignments - this has to be sent as a tuple
		self._session.set_stop_track_clip_buttons(None)						#remove the clip_stop button assignments
		self._transport.set_play_button(None)								#remove the play button assignment
		self._transport.set_record_button(None)								#remove the record button assignment
		self._transport.set_stop_button(None)								#remove the stop button assignment
		for index in range(16):
			self._grid[index].set_on_off_values(127, 0)						#reset the on/off values of the grid buttons
			self._grid[index].reset()										#turn the buttons LEDs off
		for index in range(32):
			self._button[index].set_on_off_values(127, 0)					#reset the on/off values for the key buttons
			self._button[index].reset()										#turn the buttons LEDs off
			self._button[index].release_parameter()							#remove the parameter assignment that was assigned to the keys
		for client in self._client:											#for each of our 4 clients:
			if not client._mod_dial == None:								#if the client has a modDial assigned to it
				client._mod_dial.release_parameter()						#remove the modDial's parameter assignment
		#self._device.set_parameter_controls(tuple([self._encoder[index+4] for index in range(8)]))			#assign the encoders from the device component controls - we are doing this here b
		self._device_navigator.set_device_nav_buttons(None, None) 			#remove the assignment of the device nav buttons
		self._device_navigator.set_enabled(False)							#turn off the device navigator
		self._device.set_on_off_button(None)								#remove the assignment of the on/off button from the device component
		self._device.set_lock_button(None)									#remove the assignment of the lock button from the device component	
		self._device.set_bank_nav_buttons(None, None) 						#remove the assignment of the navigation buttons from the device component
		self._device.set_enabled(False)										#turn off the device component
		self._session.set_track_bank_buttons(None, None)					#set the track bank buttons for the Session navigation controls
		self._session.set_scene_bank_buttons(None, None)					#set the scnee bank buttons for the Session navigation controls
		self._session.set_enabled(False)									#turn off the session component
		self._session_zoom.set_enabled(False)								#turn off the zoom component
		for index in range(16):
			self._grid[index].clear_send_cache()							#set the last_sent value of the grid to -1, so that the next value it receives will always be transmitted to the CNTRLR
		for index in range(32):
			self._button[index].clear_send_cache()							#set the last_sent value of the keys to -1, so that the next value it receives will always be transmitted to the CNTRLR
		for index in range(12):
			self._device._parameter_controls = None
			self._encoder[index].release_parameter()
			self._encoder[index].send_value(0, True)						#turn off all the encoder rings.  We send it the second argument, True, so that it is forced to update regardless of its last_sent property
			self._encoder[index].clear_send_cache()							#set the last_sent value of the encoder rings to -1, so that the next value it receives will always be transmitted to the CNTRLR
		for index in range(8):
			self._encoder_button[index+4].send_value(0, True)				#turn off all the encoder LEDs.  We send it the second argument, True, so that it is forced to update regardless of its last_sent property
			self._encoder_button[index+4].clear_send_cache()				#set the last_sent value of the encoder LEDs to -1, so that the next value it receives will always be transmitted to the CNTRLR
		self._session_zoom.set_zoom_button(None)							#remove the assignment of the shift button from the ZoomingComponent
		self._host._release_mod_dials()
		self.request_rebuild_midi_map()										#now that we've finished deassigning all of our controls, we tell the main script to rebuild its MIDI map and update the values in Live
	

	"""this assigns the CNTRLR's controls on the main mode the CNTRLR script boots up in"""
	"""if you're trying to customize your layout, this is probably where you want to concentrate"""
	def assign_live_controls(self):
		"""the following lines update all of the controls' last_sent properties, so that they forward the next value they receive regardless of whether or not it is the same as the last it recieved"""
		"""we also reset the encoder rings and buttons, since the device component will not update them if it is not locked to a device in Live"""
		for index in range(16):
			self._grid[index].clear_send_cache()
		for index in range(32):
			self._button[index].clear_send_cache()
		for index in range(8):
			self._encoder_button[index+4].send_value(0, True)
			self._encoder_button[index+4].clear_send_cache()
		for index in range(8):
			self._encoder[index+4].send_value(0, True)
		for index in range(12):
			self._encoder[index].clear_send_cache()

		"""here we assign the top encoders to the mod_dial, if it exists, in any connected mods"""
		self.schedule_message(4, self._assign_mod_dials)

		"""here we assign the left side of our mixer's buttons on the lower 32 keys"""
		for index in range(4):															#we set up a recursive loop to assign all four of our track channel strips' controls
			self._button[index].set_on_value(SOLO[self._rgb])							#set the solo color from the Map.py
			self._mixer.channel_strip(index).set_solo_button(self._button[index])		#assign the solo buttons to our mixer channel strips
			self._button[index+4].set_on_value(ARM[self._rgb])							#set the arm color from the Map.py
			self._mixer.channel_strip(index).set_arm_button(self._button[index+4])		#assign the arm buttons to our mixer channel strips
			self._button[index+16].set_on_value(MUTE[self._rgb])						#set the mute color from the Map.py
			self._mixer.channel_strip(index).set_mute_button(self._button[index+16])	#assign the mute buttons to our mixer channel strips
			self._button[index+20].set_on_value(SELECT[self._rgb])						#set the select color from the Map.py
			self._mixer.channel_strip(index).set_select_button(self._button[index+20])	#assign the select buttons to our mixer channel strips
		self._send_reset.set_buttons(tuple(self._button[index + 8] for index in range(4)))			#this is yet another way to quickly assign multiple elements conveniently in-place.  We are creating a recursion inside an assignment.  The tuple() method creates an immutable array.  It can't be modified until it gets where it's going and is unpacked.
		self._session.set_stop_track_clip_buttons(tuple(self._button[index+24] for index in range(4)))	#these last two lines assign the send_reset buttons and the stop_clip buttons for each track
		for index in range(4):
			self._button[index+8].send_value(SEND_RESET[self._rgb], True)				#now we are going to send a message to turn the LEDs on for the send_reset buttons
			self._button[index + 24].set_on_off_values(STOP_CLIP[self._rgb], STOP_CLIP[self._rgb])	#this assigns the custom colors defined in the Map.py file to the stop_clip buttons.  They have seperate on/off values, but we assign them both the same value so we can always identify them
			self._button[index+24].send_value(STOP_CLIP[self._rgb], True)				#finally, we send the on/off colors out to turn the LEDs on for the stop clip buttons
		self._button[28].set_on_off_values(PLAY_ON[self._rgb], PLAY[self._rgb])			#assing the on/off colors for play.  These are two seperate values, dependant upon whether play is engaged or not
		self._transport.set_play_button(self._button[28])								#set the transports play control to the corresponding button on the CNTRLR
		self._button[30].set_on_off_values(RECORD_ON[self._rgb], RECORD[self._rgb])		#set the on/off colors for the transport record buttons
		self._transport.set_record_button(self._button[30])								#assign the correct button for the transport record control
		self._button[29].set_on_value(STOP[self._rgb])									#set the on value for the Stop button
		self._transport.set_stop_button(self._button[29])								#assign the correct button for the transport stop control
		self._button[29].send_value(STOP_OFF[self._rgb], True)							#turn on the LED for the stop button
		for index in range(4):															#set up a for loop to generate an index for assigning the session nav buttons' colors
			self._button[index + 12].set_on_off_values(SESSION_NAV[self._rgb], SESSION_NAV_OFF[self._rgb])	#assign the colors from Map.py to the session nav buttons
		self._session.set_track_bank_buttons(self._button[15], self._button[14])		#set the track bank buttons for the Session navigation controls
		self._session.set_scene_bank_buttons(self._button[13], self._button[12])		#set the scnee bank buttons for the Session navigation controls

		"""this section assigns the grid to the clip launch functionality of the SessionComponent"""
		for column in range(4):															#we need to set up a double recursion so that we can generate the indexes needed to assign the grid buttons
			for row in range(4):														#the first recursion passes the column index, the second the row index
				self._scene[row].clip_slot(column).set_launch_button(self._grid[(row*4)+column])	#we use the indexes to grab the first the scene and then the clip we assigned above, and then we use them again to define the button held in the grid array that we want to assign to the clip slot from the session component

		"""this section assigns the faders and knobs"""
		for index in range(4):								
			self._mixer.channel_strip(index).set_volume_control(self._fader[index])		#Since we gave our mixer 4 tracks above, we'll now assign our fader controls to it						
		for index in range(2):
			self._mixer.return_strip(index).set_volume_control(self._fader[index+4])	#assign the right faders to control the volume of our return strips
		self._mixer.master_strip().set_volume_control(self._fader[7])					#assign the far right fader to control our master channel strip
		self._mixer.set_prehear_volume_control(self._fader[6])							#assign the remaining fader to control our prehear volume of the the master channel strip
		for track in range(4):															#we set up a recursive loop to assign all four of our track channel strips' controls
			channel_strip_send_controls = []											#the channelstripcomponent requires that we pass the send controls in an array, so we create a local variable, channel_strip_send_controls, to hold them
			for control in range(2):													#since we are going to assign two controls to the sends, we create a recursion
				channel_strip_send_controls.append(self._dial_left[track + (control * 4)])		#then use the append __builtin__ method to add them to the array
			self._mixer.channel_strip(track).set_send_controls(tuple(channel_strip_send_controls))	#now that we have an array containing the send controls, we pass it to the channelstrip component with its set_send_controls() method
			self._mixer.channel_strip(track).set_pan_control(self._dial_left[track + 8])		#now we set the pan control to the bottom 
			self._mixer.track_eq(track).set_gain_controls(tuple([self._dial_right[track+8], self._dial_right[track+4], self._dial_right[track]]))	#here's another way of doing the same thing, but instead of creating the array before hand, we define it in-place.  Its probably bad coding to mix styles like this, but I'll leave it for those of you trying to figure this stuff out
			self._mixer.track_eq(track).set_enabled(True)								#turn the eq component on

		"""this section assigns the encoders and encoder buttons"""
		self._device.set_parameter_controls(tuple([self._encoder[index+4] for index in range(8)]))			#assign the encoders from the device component controls - we are doing this here b
		self._encoder_button[7].set_on_value(DEVICE_LOCK[self._rgb])					#set the on color for the Device lock encoder button
		self._device.set_lock_button(self._encoder_button[7])							#assign encoder button 7 to the device lock control
		self._encoder_button[4].set_on_value(DEVICE_ON[self._rgb])						#set the on color for the Device on/off encoder button 
		self._device.set_on_off_button(self._encoder_button[4])							#assing encoder button 4 to the device on/off control
		for index in range(2):															#setup a recursion to generate indexes so that we can reference the correct controls to assing to the device_navigator functions
			self._encoder_button[index + 8].set_on_value(DEVICE_NAV[self._rgb])			#assign the on color for the device navigator
			self._encoder_button[index + 10].set_on_value(DEVICE_BANK[self._rgb])		#assign the on color for the device bank controls
		self._device_navigator.set_device_nav_buttons(self._encoder_button[10], self._encoder_button[11]) 	#set the device navigators controls to encoder buttons 10 and 11
		self._device.set_bank_nav_buttons(self._encoder_button[8], self._encoder_button[9]) 	#set the device components bank nav controls to encoder buttons 8 and 9
		self._session_zoom.set_zoom_button(self._button[31])							#assign the lower right key button to the shift function of the Zoom component

		"""now we turn on and update some of the components we've just made assignments to"""
		self._device.set_enabled(True)													#enable the Device Component
		self._device_navigator.set_enabled(True)										#enable the Device Navigator
		self._session.set_enabled(True)													#enable the Session Component
		self._session_zoom.set_enabled(True)											#enable the Session Zoom
		self._device.update()															#tell the Device component to update its assingments so that it will detect the currently selected device parameters and display them on the encoder rings
		self._session.update()															#tell the Session component to update so that the grid will display the currently selected session region
	

	"""this assigns the CNTRLR's controls on for 4th empty modSlot"""
	"""these assignments mirror the main section; commenting is restricted to the differences"""
	def assign_chopper_controls(self):
		"""the following lines update all of the controls' last_sent properties, so that they forward the next value they receive regardless of whether or not it is the same as the last it recieved"""
		"""we also reset the encoder rings and buttons, since the device component will not update them if it is not locked to a device in Live"""
		for index in range(16):
			self._grid[index].clear_send_cache()
		for index in range(32):
			self._button[index].clear_send_cache()
		for index in range(8):
			self._encoder_button[index+4].send_value(0, True)
			self._encoder_button[index+4].clear_send_cache()
		for index in range(12):
			self._encoder[index].send_value(0, True)
			self._encoder[index].clear_send_cache()

		"""here we assign the top encoders to the mod_dial, if it exists, in any connected mods"""
		self.schedule_message(4, self._assign_mod_dials)

		"""the following lines differ from the assignments in self.assign_live_controls()"""
		"""the assignments merely moving certain elements from their original positions"""
		for index in range(4):
			self._button[index].set_on_value(MUTE[self._rgb])
			self._mixer.channel_strip(index).set_mute_button(self._button[index])
			self._button[index+4].set_on_value(SELECT[self._rgb])
			self._mixer.channel_strip(index).set_select_button(self._button[index+4])
		self._session.set_stop_track_clip_buttons(tuple(self._button[index+8] for index in range(4)))
		for index in range(4):
			self._button[index + 8].set_on_off_values(STOP_CLIP[self._rgb], STOP_CLIP[self._rgb])
			self._button[index+8].send_value(STOP_CLIP[self._rgb], True)
		for index in range(4):
			self._button[index + 12].set_on_off_values(SESSION_NAV[self._rgb], SESSION_NAV_OFF[self._rgb])
		self._session.set_scene_bank_buttons(self._button[13], self._button[12])
		self._session.set_track_bank_buttons(self._button[15], self._button[14])

		"""the rest of this method mirrors self._assign_live_controls, comments can be found there"""
		for index in range(2):
			self._mixer.return_strip(index).set_volume_control(self._fader[index+4])
		self._mixer.master_strip().set_volume_control(self._fader[7])
		self._mixer.set_prehear_volume_control(self._fader[6])
		for track in range(4):
			channel_strip_send_controls = []
			for control in range(2):
				channel_strip_send_controls.append(self._dial_left[track + (control * 4)])
			self._mixer.channel_strip(track).set_send_controls(tuple(channel_strip_send_controls))
			self._mixer.channel_strip(track).set_pan_control(self._dial_left[track + 8])
			gain_controls = []
			self._mixer.track_eq(track).set_gain_controls(tuple([self._dial_right[track+8], self._dial_right[track+4], self._dial_right[track]]))
			self._mixer.track_eq(track).set_enabled(True)	
		for column in range(4):
			for row in range(4):
				self._scene[row].clip_slot(column).set_launch_button(self._grid[(row*4)+column])
		self._encoder_button[7].set_on_value(DEVICE_LOCK[self._rgb])
		self._device.set_lock_button(self._encoder_button[7])
		self._encoder_button[4].set_on_value(DEVICE_ON[self._rgb])
		self._device.set_on_off_button(self._encoder_button[4])
		for index in range(2):
			self._encoder_button[index + 8].set_on_value(DEVICE_NAV[self._rgb])
			self._encoder_button[index + 10].set_on_value(DEVICE_BANK[self._rgb])
		self._device_navigator.set_device_nav_buttons(self._encoder_button[10], self._encoder_button[11]) 
		self._device.set_bank_nav_buttons(self._encoder_button[8], self._encoder_button[9]) 
		self._device.set_enabled(True)
		self._device_navigator.set_enabled(True)
		self._session.set_enabled(True)
		self._session_zoom.set_enabled(True)
		self._device.update()
		self._session.update()	
		self.request_rebuild_midi_map()
	


	"""function mode callbacks"""
	def display_mod_colors(self):
		for index in range(4):							#set up a recursion of 4
			self._shift_mode._modes_buttons[index].send_value(self._client[index]._mod_color)		#update the modLEDs to display the color assigned to its contained mod
	

	"""this method changes modes when we press a modButton.  It is also called from Monomod when it needs to update the modDial assignments"""
	def shift_update(self):
		#self.log_message('shift_update')
		self.assign_alternate_mappings(0)				#first, we remove any channel reassingments we might have made by assigning alternate mappings, but to channel 0 (the original channel)
		self._chopper.set_enabled(False)				#disable the chopper, we will enable it later if we are in chopper mode
		for index in range(4):							#set up a recursion of 4
			self._shift_mode._modes_buttons[index].send_value(self._client[index]._mod_color)		#update the modLEDs to display the color assigned to its contained mod
		if self._shift_mode._mode_index is 0:			#if the shift mode is 0, meaning we've selecte the main script mode:
			self._host._set_dial_matrix(None, None)		#deassign the Monomod Components dial matrix 
			#self._host._set_knobs(None)
			self._host._set_button_matrix(None)			#deassign the Monomod Component's button matrix
			self._host._set_key_buttons(None)			#deassign the Monomod Component's key matrix
			self._host.set_enabled(False)				#disable the Monomod Component
			self.set_local_ring_control(1)				#send sysex to the CNTRLR to put it in local ring mode
			self.assign_live_controls()					#assign our top level control assignments
		elif CHOPPER_ENABLE and not self._host._client[3].is_connected() and self._shift_mode._mode_index == 4:		#if the fourth mod button has been pressed and there is no mod installed
			self.deassign_live_controls()				#deassign the top level assignments
			for index in range(4):						#set up a recursion of 4
				if self._shift_mode._mode_index == (index + 1):			#for each recursion, if the recursion number is the same as the shift_mode_index +1
					self._shift_mode._modes_buttons[index].send_value(1)		#turn on the LED below the modButton
			self.schedule_message(4, self._assign_mod_dials)			
			self._host._set_dial_matrix(None, None)		#deassign the Monomod Components dial matrix 
			self._host._set_button_matrix(None)			#deassign the Monomod Component's button matrix
			self._host._set_key_buttons(None)			#deassign the Monomod Component's key matrix
			self._host.set_enabled(False)				#disable the Monomod Component
			self.set_local_ring_control(1)				#send sysex to the CNTRLR to put it in local ring mode
			self.assign_chopper_controls()				#assign the controls for the Chopper Component
			self._chopper.set_enabled(True)				#turn the Chopper Component on
		else:											#otherwise, if we are in modMode
			self.deassign_live_controls()				#remove all of our assignments from the controls and refresh their caches
			self.assign_mixer_controls()
			self._host.set_enabled(True)				#turn on the Monomod Component
			self._host._set_dial_matrix(self._dial_matrix, self._dial_button_matrix)	#assign the encoders to it
			#self._host._set_knobs(tuple(self._knobs))
			self._host._set_button_matrix(self._matrix)									#assign the 4x4 to it
			self._host._set_key_buttons(tuple(self._button))							#assign the lower buttons to it
			self._host._select_client(self._shift_mode._mode_index-1)					#select the client corresponding to the button we pressed
			self._host.display_active_client()											#tell Monomod Component to update the LEDs on the CNTRLR corresponding to the client that is selected
			for index in range(4):														#set up a recursion for each of our modButtons
				if self._shift_mode._mode_index == (index + 1):							#if the button is the mode we've chosen
					self._shift_mode._modes_buttons[index].send_value(1)				#turn the LED white
			if not self._host._active_client.is_connected():							#if there is not a mod in the currently selected modSlot
				self.assign_alternate_mappings(self._shift_mode._mode_index)			#assign a different MIDI channel that the controls translated to when entering Live
	

	def assign_mixer_controls(self):
		for index in range(4):								
			self._mixer.channel_strip(index).set_volume_control(self._fader[index])		#Since we gave our mixer 4 tracks above, we'll now assign our fader controls to it						
		for index in range(2):
			self._mixer.return_strip(index).set_volume_control(self._fader[index+4])	#assign the right faders to control the volume of our return strips
		self._mixer.master_strip().set_volume_control(self._fader[7])					#assign the far right fader to control our master channel strip
		self._mixer.set_prehear_volume_control(self._fader[6])							#assign the remaining fader to control our prehear volume of the the master channel strip
	

	"""assign alternate mappings to the controls when a modSlot is selected that doesn't contain a mod"""
	def assign_alternate_mappings(self, chan):
		chan = min(16, max(chan, 0))
		for index in range(8):
			self._encoder_button[index + 4].set_channel(chan)		#set the contols channel to the methods second argument
			self._encoder_button[index + 4].set_enabled(chan is 0)	#if the channel is not 0, we need to disable the control so that it 
			self._encoder_button[index + 4].force_next_send()
		for encoder in self._encoder:								#is forwarded to Live, but not used by the script for internal processing
			encoder.set_channel(chan)
			encoder.set_enabled(chan is 0)
			encoder.force_next_send()
		for button in self._button:
			button.set_channel(chan)
			button.set_enabled(chan is 0)
			button.force_next_send()
		for cell in self._grid:
			cell.set_channel(chan)
			cell.set_enabled(chan is 0)
			cell.force_next_send()
		if FADER_BANKING:
			for fader in self._fader:
				fader.release_parameter()
				fader.set_channel(chan)
				fader.set_enabled(chan is 0)
				fader.force_next_send()
		if DIAL_BANKING:
			for dial in self._dial_right:
				dial.release_parameter()
				dial.set_channel(chan)
				dial.set_enabled(chan is 0)
				dial.force_next_send()
			for dial in self._dial_left:
				dial.release_parameter()
				dial.set_channel(chan)
				dial.set_enabled(chan is 0)
				dial.force_next_send()
		self.request_rebuild_midi_map()
			
	

	"""reassign the original channel and identifier to all the controls that can be remapped through assign_alternate_mappings"""
	def assign_original_mappings(self):
		for index in range(8):
			self._encoder_button[index + 4].set_channel(self._encoder_button[index + 4]._original_channel)
			self._encoder_button[index + 4].set_enabled(True)
			self._encoder_button[index + 4].force_next_send()
		for encoder in self._encoder:
			encoder.set_channel(encoder._original_channel)
			encoder.set_enabled(True)
			encoder.force_next_send()
		for button in self._button:
			button.set_channel(button._original_channel)
			button.set_enabled(True)
			button.force_next_send()
		for cell in self._grid:
			cell.set_channel(cell._original_channel)
			cell.set_enabled(True)
			cell.force_next_send()	
		if FADER_BANKING:
			for fader in self._fader:
				fader.set_channel(fader._original_channel)
				fader.set_enabled(True)
				fader.force_next_send()
		if DIAL_BANKING:
			for dial in self._dial_right:
				dial.set_channel(dial._original_channel)
				dial.set_enabled(True)
				dial.force_next_send()
			for dial in self._dial_left:
				dial.set_channel(dial._original_channel)
				dial.set_enabled(True)
				dial.force_next_send()
		self.request_rebuild_midi_map()
	

	"""called on timer"""
	def update_display(self):
		super(Cntrlr, self).update_display()		#since we are overriding this from the inherited method, we need to call the original routine as well
		self._timer = (self._timer + 1) % 256	#each 100/60ms, increase the self._timer property by one.  Start over at 0 when we hit 256
		if(self._local_ring_control is False):	#if local rings are turned off, then we need to send the new values if they've changed
			self.send_ring_leds()			
		self.flash()							#call the flash method below
	

	"""this method recurses through all the controls, causing them to flash depending on their stored values"""
	def flash(self):
		if(self.flash_status > 0):
			for control in self.controls:
				if isinstance(control, MonoButtonElement):
					control.flash(self._timer)		
	


	"""m4l bridge"""

	"""this is a method taken and modified from the MackieControl scripts"""
	"""it takes a display string and modifies it to be a specified length"""
	def generate_strip_string(self, display_string):
		NUM_CHARS_PER_DISPLAY_STRIP = 12
		if (not display_string):
			return (' ' * NUM_CHARS_PER_DISPLAY_STRIP)
		if ((len(display_string.strip()) > (NUM_CHARS_PER_DISPLAY_STRIP - 1)) and (display_string.endswith('dB') and (display_string.find('.') != -1))):
			display_string = display_string[:-2]
		if (len(display_string) > (NUM_CHARS_PER_DISPLAY_STRIP - 1)):
			for um in [' ',
			 'i',
			 'o',
			 'u',
			 'e',
			 'a']:
				while ((len(display_string) > (NUM_CHARS_PER_DISPLAY_STRIP - 1)) and (display_string.rfind(um, 1) != -1)):
					um_pos = display_string.rfind(um, 1)
					display_string = (display_string[:um_pos] + display_string[(um_pos + 1):])
		else:
			display_string = display_string.center((NUM_CHARS_PER_DISPLAY_STRIP - 1))
		ret = u''
		for i in range((NUM_CHARS_PER_DISPLAY_STRIP - 1)):
			if ((ord(display_string[i]) > 127) or (ord(display_string[i]) < 0)):
				ret += ' '
			else:
				ret += display_string[i]

		ret += ' '
		ret = ret.replace(' ', '_')
		assert (len(ret) == NUM_CHARS_PER_DISPLAY_STRIP)
		return ret
	

	"""this method forwards display information from control elements to the LCD patch"""
	def notification_to_bridge(self, name, value, sender):
		if(isinstance(sender, (MonoEncoderElement, CodecEncoderElement))):
			pn = str(self.generate_strip_string(name))
			pv = str(self.generate_strip_string(value))
			self._monobridge._send(sender.name, 'lcd_name', pn)
			self._monobridge._send(sender.name, 'lcd_value', pv)
	

	"""this method regulates parameter values from being sent on updates if the control has not actually been changed"""
	def touched(self):
		if self._touched is 0:
			self._monobridge._send('touch', 'on')
			self.schedule_message(2, self.check_touch)
		self._touched +=1
	

	"""this method is called by the LCD patch to determine whether any controls have been changed"""
	def check_touch(self):
		if self._touched > 5:
			self._touched = 5
		elif self._touched > 0:
			self._touched -= 1
		if self._touched is 0:
			self._monobridge._send('touch', 'off')
		else:
			self.schedule_message(2, self.check_touch)
	

	"""this is an unnused method.  It provides a way to retrieve all the clip names belonging to the current session views clips"""
	def get_clip_names(self):
		clip_names = []
		for scene in self._session._scenes:
			for clip_slot in scene._clip_slots:
				if clip_slot.has_clip() is True:
					clip_names.append(clip_slot._clip_slot)##.clip.name)
					return clip_slot._clip_slot
		return clip_names
	


	"""midi functionality"""
	
	"""this method needs to be here so that Live knows what to do (nothing, in this case) when it receives sysex from the CNTRLR"""
	def handle_sysex(self, midi_bytes):
		pass
	

	"""this method can be linked to from m4l, and provides a way to update the parameter value of an assigned DeviceComponent parameter control"""
	def to_encoder(self, num, val):
		rv=int(val*127)
		self._device._parameter_controls[num].receive_value(rv)
		p = self._device._parameter_controls[num]._parameter_to_map_to
		newval = (val * (p.max - p.min)) + p.min
		p.value = newval
	

	"""this method sets the instance variable for local ring control, and sends the appropriate sysex string to change states on the CNTRLR"""
	def set_local_ring_control(self, val = 1):
		self._local_ring_control = (val!=0)
		if(self._local_ring_control is True):
			self._send_midi(tuple([240, 0, 1, 97, 8, 32, 0, 247]))
		else:
			self._send_midi(tuple([240, 0, 1, 97, 8, 32, 1, 247]))
	

	"""this method sets the instance variable for absolute encoder changes, and sends the appropriate sysex string to change states on the CNTRLR"""			
	def set_absolute_mode(self, val = 1):
		self._absolute_mode = (val!=0)
		if self._absolute_mode is True:
			self._send_midi(tuple([240, 0, 1, 97, 8, 17, 0, 0, 0, 0, 0, 0, 0, 0, 247]))
		else:
			self._send_midi(tuple([240, 0, 1, 97, 8, 17, 127, 127, 127, 127, 127, 127, 127, 127, 247]))
	

	"""this method is used to update the individual elements of the encoder rings when the CNTRLR is in local ring control mode"""
	def send_ring_leds(self):
		if self._host._is_enabled == True:
			leds = [240, 0, 1, 97, 8, 31]
			for index in range(12):
				wheel = self._encoder[index]
				bytes = wheel._get_ring()
				leds.append(bytes[0])
				leds.append(int(bytes[1]) + int(bytes[2]))
			leds.append(247)
			self._send_midi(tuple(leds))
	

	def _release_mod_dials(self):
		if not self._client is None:
			for client in self._client:										#for each of our 4 clients:
				if not client._mod_dial == None:								#if the client has a modDial assigned to it
					client._mod_dial.release_parameter()						#remove the modDial's parameter assignment
	

	def _assign_mod_dials(self):
		if not self._client is None:
			for client in self._client:					#recursion to contain all available clients
				param = client._mod_dial_parameter()	#param is a local variable, and we assign its value to the mod_dial_parameter (this is handled by each individual client module)
				if not client._mod_dial == None:					#if the client has been assigned a mod dial (which it should have been in setup_mod() )
					if not param == None:										#if the param variable was properly assigned in the client module
						client._mod_dial.connect_to(param)			#connect the physical control to the parameter (this should be the moddial parameter in the m4l patch)
					else:
						client._mod_dial.release_parameter()		#if the param was None, release the physical control from any assignments
			self.request_rebuild_midi_map()
	


	"""general functionality"""
	
	"""this method is called by Live when it needs to disconnect.  It's very important that any observers that were set up in the script are removed here"""
	def disconnect(self):
		"""clean things up on disconnect"""
		if self.song().view.selected_track_has_listener(self._update_selected_device):
			self.song().view.remove_selected_track_listener(self._update_selected_device)
		self._hosts = []
		self.log_message("<<<<<<<<<<<<<<<<<<<<<<<<< " + str(self._host_name) + " log closed >>>>>>>>>>>>>>>>>>>>>>>>>") #Create entry in log file
		super(Cntrlr, self).disconnect()
		rebuild_sys()
	

	"""this provides a hook that can be called from m4l to change the DeviceComponent's behavior"""
	def device_follows_track(self, val):
		self._device_selection_follows_track_selection = (val == 1)
		return self
	

	"""this is a customizationo of the inherited behavior of ControlSurface"""
	def _update_selected_device(self):
		if self._device_selection_follows_track_selection is True:
			track = self.song().view.selected_track
			device_to_select = track.view.selected_device
			if device_to_select == None and len(track.devices) > 0:
				device_to_select = track.devices[0]
			if device_to_select != None:
				self.song().view.select_device(device_to_select)
			#self._device.set_device(device_to_select)
			self.set_appointed_device(device_to_select)
			#self._device_selector.set_enabled(True)
		self.request_rebuild_midi_map()
		return None 
	

	"""this provides a hook to get the current tracks length from other modules"""
	def _get_num_tracks(self):
		return self.num_tracks
	


	"""device component methods and overrides"""

	"""this closure replaces the default DeviceComponent update() method without requiring us to build an override class"""
	"""it calls the _update_selected_device method of this script in addition to its normal routine"""
	"""it also ensures a rebuilt midi_map; for some reason the Abe's pulled that part out of the post 8.22 scripts, and under certain circumstances"""
	"""things don't work as expected anymore."""
	def _device_update(self, device):
		def _update():
			#for client in self._client:
			#	if (device._device != None) and (client.device == device._device):
			#		device._bank_index = max(client._device_component._cntrl_offset, device._bank_index)
			DeviceComponent.update(device)
			self.request_rebuild_midi_map()
		return _update
		
	

	def _device_set_device(self, device_component):
		def set_device(device):
			is_monodevice = False
			for client in self._client:
				if (device != None) and (client.device == device):
					is_monodevice = client
			if is_monodevice != False:
				#device = client._device_component._device
				self.log_message('is monodevice' + str(device.name))
				assert ((device == None) or isinstance(device, Live.Device.Device))
				if ((not device_component._locked_to_device) and (device != device_component._device)):
					if (device_component._device != None):
						device_component._device.remove_name_listener(device_component._on_device_name_changed)
						device_component._device.remove_parameters_listener(device_component._on_parameters_changed)
						parameter = device_component._on_off_parameter()
						if (parameter != None):
							parameter.remove_value_listener(device_component._on_on_off_changed)
						if (device_component._parameter_controls != None):
							for control in device_component._parameter_controls:
								control.release_parameter()
					device_component._device = device
					if (device_component._device != None):
						device_component._bank_index = 0
						device_component._device.add_name_listener(self._on_device_name_changed)
						device_component._device.add_parameters_listener(self._on_parameters_changed)
						parameter = device_component._on_off_parameter()
						if (parameter != None):
							parameter.add_value_listener(device_component._on_on_off_changed)
					for key in device_component._device_bank_registry.keys():
						if (key == device_component._device):
							device_component._bank_index = device_component._device_bank_registry.get(key, 0)
							del device_component._device_bank_registry[key]
							break
					device_component._bank_name = '<No Bank>' #added
					device_component._bank_index = max(is_monodevice._cntrl_offset, device_component._bank_index)
					device_component._on_device_name_changed()
					device_component.update()	 
			else:
				DeviceComponent.set_device(device_component, device)
		return set_device
		
	

	"""this closure replaces the default ChannelStripComponent _on_cf_assign_changed() method without requiring us to build an override class"""
	"""it allows us to change different colors to its assigned controls based on the crossfade assignment, which the default _Framework doesn't support"""
	def mixer_on_cf_assign_changed(self, channel_strip):
		def _on_cf_assign_changed():
			if (channel_strip.is_enabled() and (channel_strip._crossfade_toggle != None)):
				if (channel_strip._track != None) and (channel_strip._track in (channel_strip.song().tracks + channel_strip.song().return_tracks)):
					if channel_strip._track.mixer_device.crossfade_assign == 1: #modified
						channel_strip._crossfade_toggle.turn_off()
					elif channel_strip._track.mixer_device.crossfade_assign == 0:
						channel_strip._crossfade_toggle.send_value(1)
					else:
						channel_strip._crossfade_toggle.send_value(2)
		return _on_cf_assign_changed
		
	

	"""a closure fix for banking when we deassign the bank buttons and still want to change bank indexes"""
	def device_is_banking_enabled(self, device):
		def _is_banking_enabled():
			return True
		return _is_banking_enabled
		
	

#	a