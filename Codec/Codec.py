# by amounra 0214 : http://www.aumhaa.com

from __future__ import with_statement
import Live
import time
import math

""" All of the Framework files are listed below, but we are only using using some of them in this script (the rest are commented out) """
from _Framework.ButtonElement import ButtonElement # Class representing a button a the controller
from _Framework.ButtonMatrixElement import ButtonMatrixElement # Class representing a 2-dimensional set of buttons
from _Framework.ChannelStripComponent import ChannelStripComponent # Class attaching to the mixer of a given track
from _Framework.CompoundComponent import CompoundComponent # Base class for classes encompasing other components to form complex components
from _Framework.ControlElement import ControlElement # Base class for all classes representing control elements on a controller 
from _Framework.ControlSurface import ControlSurface # Central base class for scripts based on the new Framework
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent # Base class for all classes encapsulating functions in Live
#from _Framework.DeviceComponent import DeviceComponent # Class representing a device in Live
from _Framework.EncoderElement import EncoderElement # Class representing a continuous control on the controller
from _Framework.InputControlElement import * # Base class for all classes representing control elements on a controller
from _Framework.MixerComponent import MixerComponent # Class encompassing several channel strips to form a mixer
from _Framework.ModeSelectorComponent import ModeSelectorComponent # Class for switching between modes, handle several functions with few controls
from _Framework.NotifyingControlElement import NotifyingControlElement # Class representing control elements that can send values
from _Framework.SessionComponent import SessionComponent # Class encompassing several scene to cover a defined section of Live's session
from _Framework.TransportComponent import TransportComponent # Class encapsulating all functions in Live's transport section
from _Framework.ModesComponent import AddLayerMode, LayerMode, MultiEntryMode, ModesComponent, SetAttributeMode, ModeButtonBehaviour, CancellableBehaviour, AlternativeBehaviour, ReenterBehaviour, DynamicBehaviourMixin, ExcludingBehaviourMixin, ImmediateBehaviour, LatchingBehaviour, ModeButtonBehaviour
from _Framework.Layer import Layer
from _Framework.SubjectSlot import SubjectEvent, subject_slot, subject_slot_group
from _Framework.Task import *
from _Generic.Devices import *

from _Framework.M4LInterfaceComponent import M4LInterfaceComponent
from _Framework.ComboElement import ComboElement, DoublePressElement, MultiElement, DoublePressContext
from _Framework.BackgroundComponent import BackgroundComponent

"""Imports from _Mono_Framework"""
from _Mono_Framework.DetailViewControllerComponent import DetailViewControllerComponent
from _Mono_Framework.CodecEncoderElement import CodecEncoderElement
from _Mono_Framework.EncoderMatrixElement import NewEncoderMatrixElement as EncoderMatrixElement
from _Mono_Framework.DeviceSelectorComponent import NewDeviceSelectorComponent as DeviceSelectorComponent
from _Mono_Framework.MonoBridgeElement import MonoBridgeElement
from _Mono_Framework.MonoButtonElement import MonoButtonElement
from _Mono_Framework.MonoEncoderElement import MonoEncoderElement
from _Mono_Framework.Live8DeviceComponent import Live8DeviceComponent as DeviceComponent
from _Mono_Framework.LiveUtils import *
from _Mono_Framework.Mod import *
from _Mono_Framework.Debug import *

debug = initialize_debug()

from Map import *

def tracks_to_use(self):
	return tuple(self.song().visible_tracks) + tuple(self.song().return_tracks)
	
MixerComponent.tracks_to_use = tracks_to_use


""" Here we define some global variables """
factoryreset = (240,0,1,97,4,6,247)
btn_channels = (240, 0, 1, 97, 4, 19, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, 0, 247);
enc_channels = (240, 0, 1, 97, 4, 20, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, CHANNEL, 247);

SLOWENCODER = (240, 0, 1, 97, 4, 30, 00, 00, 247)
NORMALENCODER = (240, 0, 1, 97, 4, 30, 02, 00, 247)
FASTENCODER = (240, 0, 1, 97, 4, 30, 04, 00, 247)
SHOW_PLAYING_CLIP_DELAY = 5
ENCODER_SPEED = [NORMALENCODER, SLOWENCODER]

class CancellableBehaviourWithRelease(CancellableBehaviour):


	def release_delayed(self, component, mode):
		component.pop_mode(mode)
	

	def update_button(self, component, mode, selected_mode):
		button = component.get_mode_button(mode)
		groups = component.get_mode_groups(mode)
		selected_groups = component.get_mode_groups(selected_mode)
		value = (mode == selected_mode or bool(groups & selected_groups))*32 or 1
		button.send_value(value, True)
	

class ShiftCancellableBehaviourWithRelease(CancellableBehaviour):


	def release_delayed(self, component, mode):
		component.pop_mode(mode)
	

	def update_button(self, component, mode, selected_mode):
		pass
	


class CodecMonoButtonElement(MonoButtonElement):


	def __init__(self, *a, **k):
		super(CodecMonoButtonElement, self).__init__(*a, **k)
		self.set_color_map(tuple(COLOR_MAP))
	


class ShiftModeComponent(ModeSelectorComponent):


	def __init__(self, callback, script, *a, **k):
		super(ShiftModeComponent, self).__init__(*a, **k)
		assert hasattr(callback, '__call__')
		self._set_protected_mode_index(0)
		self._script = script
		self.update = callback
	

	def number_of_modes(self):
		return 4
	

	def set_mode_toggle(self, button):
		assert (button == None or isinstance(button, ButtonElement))
		if self._mode_toggle != None:
			self._mode_toggle.remove_value_listener(self._toggle_value)
		self._mode_toggle = button
		if self._mode_toggle != None:
			self._mode_toggle.add_value_listener(self._toggle_value)
	

	def set_mode_buttons(self, buttons):
		assert buttons != None
		assert isinstance(buttons, tuple)
		assert len(buttons) - 1 in range(16)
		for button in buttons:
			assert isinstance(button, ButtonElement)
			identify_sender = True
			button.add_value_listener(self._mode_value, identify_sender)
			self._modes_buttons.append(button)
	

	def _mode_value(self, *a, **k):
		if self.is_enabled():
			super(ShiftModeComponent, self)._mode_value(*a, **k)
	


class CodecDeviceComponent(DeviceComponent):
	__doc__ = ' Class representing a device in Live '


	def __init__(self, script, *a, **k):
		super(CodecDeviceComponent, self).__init__(*a, **k)
		self._script = script
		self._display_device_button = None
		self._prev_button = None
		self._next_button = None
		
	

	def _lock_value(self, value):
		if not self._script._shift_pressed and self.is_enabled():
			assert (self._lock_button != None)
			assert (value != None)
			assert isinstance(value, int)
			if not self._lock_button.is_momentary() or value is not 0:
				self._locked_to_device = not self._locked_to_device
				self.update()
	

	def set_lock_to_device(self, lock, device):
		#self._script.log_message(str(lock) + ' ' + str(device))
		assert isinstance(lock, type(False))
		if lock is True:
			if not self.is_locked():
				self.set_device(device)
			self._locked_to_device = not self._locked_to_device
			if self.is_enabled():
				if (self._lock_button != None):
					if self._locked_to_device:
						self._lock_button.turn_on()
					else:
						self._lock_button.turn_off()  
			self._script.schedule_message(2, self._lock_callback)
	

	def _bank_up_value(self, value):
		if (not self._script._shift_pressed) and self.is_enabled():
			super(CodecDeviceComponent, self)._bank_up_value(value)
	

	def _bank_down_value(self, value):
		if (not self._script._shift_pressed) and self.is_enabled():
			super(CodecDeviceComponent, self)._bank_down_value(value)
	

	def _on_off_value(self, value):
		if (not self._script._shift_pressed) and self.is_enabled():
			super(CodecDeviceComponent, self)._on_off_value(value)
	

	def _bank_value(self, value):
		if (not self._script._shift_pressed) and self.is_enabled():
			super(DeviceComponent, self)._bank_value(value)
	

	def display_device(self):
		if(self._device != None):
			track = self.find_track(self._device)
			if (self.song().view.selected_track is not track):
				self.song().view.selected_track = track
			self.song().view.select_device(self._device)
			if ((not self.application().view.is_view_visible('Detail')) or (not self.application().view.is_view_visible('Detail/DeviceChain'))):
				self.application().view.show_view('Detail')
				self.application().view.show_view('Detail/DeviceChain')
	

	def find_track(self, obj):
		if obj != None:
			if(type(obj.canonical_parent)==type(None)) or (type(obj.canonical_parent)==type(self.song())):
				return None
			elif(type(obj.canonical_parent) == type(self.song().tracks[0])):
				return obj.canonical_parent
			else:
				return self.find_track(obj.canonical_parent)
		else:
			return None
	

	def is_locked(self):
		return self._locked_to_device
	

	def set_display_device_button(self, button):
		if self._display_device_button != None:
			if self._display_device_button.value_has_listener(self._display_device_value):
				self._display_device_button.remove_value_listener(self._display_device_value)
		self._display_device_button = button
		self._display_device_button.add_value_listener(self._display_device_value)	
	

	def _display_device_value(self, value):
		if self.is_enabled():
			if value > 0 and self._device != None:
				self.display_device()
	

	def disconnect(self):
		if self._display_device_button != None:
			if self._display_device_button.value_has_listener(self._display_device_value):
				self._display_device_button.remove_value_listener(self._display_device_value)
		if self._prev_button != None:
			if self._prev_button.value_has_listener(self._nav_value):
				self._prev_button.remove_value_listener(self._nav_value)
		if self._next_button != None:
			if self._next_button.value_has_listener(self._nav_value):
				self._next_button.remove_value_listener(self._nav_value)
		super(CodecDeviceComponent, self).disconnect()
	

	def set_nav_buttons(self, prev_button, next_button):
		assert(prev_button == None or isinstance(prev_button, ButtonElement))
		assert(next_button == None or isinstance(next_button, ButtonElement))
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
	

	def _nav_value(self, value, sender):
		if self.is_enabled():
			if not self._script._shift_pressed:
				assert ((sender != None) and (sender in (self._prev_button, self._next_button)))
				if self.is_enabled() and not self.is_locked() and value != 0:		# and (not self._shift_pressed)):
					if ((not sender.is_momentary()) or (value != 0)):
						if self._script._device_component != self:
							self._script.set_device_component(self)
						direction = Live.Application.Application.View.NavDirection.left
						if (sender == self._next_button):
							direction = Live.Application.Application.View.NavDirection.right
						self.application().view.scroll_view(direction, 'Detail/DeviceChain', True)
						self.update()
	

	def update(self):
		super(CodecDeviceComponent, self).update()
		if self.is_enabled():
			if self._on_off_parameter() != None and self._on_off_button != None:
				self._on_off_button.send_value(self._on_off_parameter().value > 0)
			if self._lock_button != None:
				self._lock_button.send_value(self.is_locked())
			self._script.request_rebuild_midi_map()
	


class SpecialCodecDeviceComponent(CodecDeviceComponent):


	def __init__(self, *a, **k):
		super(SpecialCodecDeviceComponent, self).__init__(*a, **k)
	

	def _assign_parameters(self):
		assert self.is_enabled()
		assert (self._device != None)
		assert (self._parameter_controls != None)
		self._bank_name = ('Bank ' + str(self._bank_index + 1)) #added
		if (self._device.class_name in self._device_banks.keys()): #modified
			assert (self._device.class_name in self._device_best_banks.keys())
			banks = self._device_banks[self._device.class_name]
			for row in range(4):
				bank = None
				#if (not self._is_banking_enabled()):
				#	banks = self._device_best_banks[self._device.class_name]
				#	self._bank_name = 'Best of Parameters' #added
				if (len(banks) > (self._bank_index + row)):
					bank = banks[self._bank_index + row]
					if self._is_banking_enabled(): #added
						if self._device.class_name in self._device_bank_names.keys(): #added
							self._bank_name = self._device_bank_names[self._device.class_name][self._bank_index + row] #added *recheck
				#assert ((bank == None) or (len(bank) >= len(self._parameter_controls)))
				#self._script.log_message('device bank' + str(self._bank_name))
				for index in range(8):
					parameter = None
					if (bank != None):
						parameter = get_parameter_by_name(self._device, bank[index])
					if (parameter != None):
						self._parameter_controls[index + (row*8)].connect_to(parameter)
					else:
						self._parameter_controls[index  + (row*8)].release_parameter()
						self._parameter_controls[index + (row*8)].send_value(0, True);
		else:
			parameters = self._device_parameters_to_map()
			num_controls = len(self._parameter_controls)
			index = (self._bank_index * num_controls)
			for control in self._parameter_controls:
				if (index < len(parameters)):
					control.connect_to(parameters[index])
				else:
					control.release_parameter()
				index += 1
	


class CodecResetSendsComponent(ControlSurfaceComponent):
	' Special Component to reset all track sends to zero for the first four returns '
	__module__ = __name__


	def __init__(self, script, *a, **k):
		super(CodecResetSendsComponent, self).__init__(*a, **k)
		self._script = script
		self._buttons = [[None for index in range(4)] for index in range(8)]
	

	def disconnect(self):
		if (self._buttons != None):
			for column in self._buttons:
				for button in column:
					if (button != None):
						button.remove_value_listener(self.reset_send)
		self._buttons = []
	

	def on_enabled_changed(self):
		self.update()
	

	def set_buttons(self, buttons):
		for column in buttons:
			for button in column:
				assert isinstance(button, ButtonElement) or (button == None)
		#assert(for button in buttons(isinstance(button, ButtonElement) or (button == None)))
		for column in self._buttons:
			for button in column:
				if (button != None):
					button.remove_value_listener(self.reset_send)
		self._buttons = buttons
		for column in self._buttons:
			for button in column:
				if (button != None):
					button.add_value_listener(self.reset_send, identify_sender = True)
	

	def update(self):
		#debug_print('update is abstract. Forgot to override it?')
		pass
	

	def reset_send(self, value, sender):
		if self.is_enabled() and not self._script._shift_pressed:
			assert (self._buttons != None)
			assert isinstance(value, int)
			tracks = self.tracks_to_use()
			returns = self.returns_to_use()
			if ((value is not 0) or (not sender.is_momentary())):
				for column in range(8):
					for row in range(4):
						if sender is self._buttons[column][row]:
							if (row < len(returns)):
								for track in tracks:
									track.mixer_device.sends[row].value = 0
								for track in returns:
									track.mixer_device.sends[row].value = 0
							break
	

	def tracks_to_use(self):
		return self.song().tracks
	

	def returns_to_use(self):
		return self.song().return_tracks
	


class CodecDeviceSelectorComponent(ModeSelectorComponent):
	__module__ = __name__
	__doc__ = ' Class for selecting a device based on a prefix added to its name'


	def __init__(self, script, prefix, devices, *a, **k):
		super(CodecDeviceSelectorComponent, self).__init__(*a, **k)
		self._script = script
		self._mode_index = 0
		self._number_of_modes = 0
		self._prefix = prefix
	

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
				self._number_of_modes = len(self._modes_buttons)
			for index in range(len(self._modes_buttons)):
				if (index == self._mode_index):
					self._modes_buttons[index].turn_on()
				else:
					self._modes_buttons[index].turn_off()
	

	def set_mode_toggle(self, button):
		assert ((button == None) or isinstance(button, ButtonElement))
		if (self._mode_toggle != None):
			self._mode_toggle.remove_value_listener(self._toggle_value)
		self._mode_toggle = button
		if (self._mode_toggle != None):
			self._mode_toggle.add_value_listener(self._toggle_value)
	

	def number_of_modes(self):
		return self._number_of_modes
	

	def update(self):
		if self.is_enabled():
			for button in range(len(self._modes_buttons)):
				if(button is self._mode_index):
					self._modes_buttons[button].turn_on()
				else:
					self._modes_buttons[button].turn_off()
	

	def set_mode(self, mode):
		if self.is_enabled():
			assert isinstance(mode, int)
			assert (mode in range(self.number_of_modes()))
			if (self._mode_index != mode):
				self._mode_index = mode
				keys = (str('c' + str(self._mode_index + 1)), str('p' + str(self._mode_index + 1)))
				preset = None
				for key in keys:
					if preset == None:
						for track_type in (self.song().tracks, self.song().return_tracks, [self.song().master_track]):
							for track in track_type:
								for device in track.devices:
									if(match(key, str(device.name)) != None):
										preset = device
										break
									elif device.can_have_chains:
										for chain in device.chains:
											for chain_device in chain.devices:
												if(match(key, str(chain_device.name)) != None):
													preset = chain_device
													break
				if(preset != None):
					#self._selected_device.set_device(preset)
					self._script._device_component.set_device(preset)
					self._script.request_rebuild_midi_map()
				self.update()
	

	def set_preset(self, preset):
		pass
	

	def on_enabled_changed(self):
		self.update()	
	


class CodecDeviceNavigatorComponent(ControlSurfaceComponent):
	__module__ = __name__
	__doc__ = ' Component that can toggle the device chain- and clip view of the selected track '


	def __init__(self, *a, **k):
		super(CodecDeviceNavigatorComponent, self).__init__(*a, **k)
		self._device_clip_toggle_button = None
		self._detail_toggle_button = None
		self._left_button = None
		self._right_button = None
		self._shift_button = None
		self._shift_pressed = False
		self._show_playing_clip_ticks_delay = -1
		self.application().view.add_is_view_visible_listener('Detail', self._detail_view_visibility_changed)
		self._register_timer_callback(self._on_timer)
		return None
	

	def disconnect(self):
		self._unregister_timer_callback(self._on_timer)
		self.application().view.remove_is_view_visible_listener('Detail', self._detail_view_visibility_changed)
		if self._device_clip_toggle_button != None:
			self._device_clip_toggle_button.remove_value_listener(self._device_clip_toggle_value)
			self._device_clip_toggle_button = None
		if self._detail_toggle_button != None:
			self._detail_toggle_button.remove_value_listener(self._detail_toggle_value)
			self._detail_toggle_button = None
		if self._left_button != None:
			self._left_button.remove_value_listener(self._nav_value)
			self._left_button = None
		if self._right_button != None:
			self._right_button.remove_value_listener(self._nav_value)
			self._right_button = None
		if self._shift_button != None:
			self._shift_button.remove_value_listener(self._shift_value)
			self._shift_button = None
		return None
	

	def set_device_clip_toggle_button(self, button):
		if not(button == None or isinstance(button, ButtonElement)):
			isinstance(button, ButtonElement)
			raise AssertionError
		if self._device_clip_toggle_button != button:
			if self._device_clip_toggle_button != None:
				self._device_clip_toggle_button.remove_value_listener(self._device_clip_toggle_value)
			self._device_clip_toggle_button = button
			if self._device_clip_toggle_button != None:
				self._device_clip_toggle_button.add_value_listener(self._device_clip_toggle_value)
			self._rebuild_callback()
			self.update()
		return None
	

	def set_detail_toggle_button(self, button):
		if not(button == None or isinstance(button, ButtonElement)):
			isinstance(button, ButtonElement)
			raise AssertionError
		if self._detail_toggle_button != button:
			if self._detail_toggle_button != None:
				self._detail_toggle_button.remove_value_listener(self._detail_toggle_value)
			self._detail_toggle_button = button
			if self._detail_toggle_button != None:
				self._detail_toggle_button.add_value_listener(self._detail_toggle_value)
			self._rebuild_callback()
			self.update()
		return None
	

	def set_device_nav_buttons(self, device, left_button, right_button):
		
		assert(left_button == None or isinstance(left_button, ButtonElement))
		assert(right_button == None or isinstance(right_button, ButtonElement))
		identify_sender = True
		if self._left_button != None:
			self._left_button.remove_value_listener(self._nav_value)
		self._left_button = left_button
		if self._left_button != None:
			self._left_button.add_value_listener(self._nav_value, identify_sender)
		if self._right_button != None:
			self._right_button.remove_value_listener(self._nav_value)
		self._right_button = right_button
		if self._right_button != None:
			self._right_button.add_value_listener(self._nav_value, identify_sender)
		#self._rebuild_callback()
		self.update()
		return None
	

	def set_shift_button(self, button):
		if not(button == None or isinstance(button, ButtonElement) and button.is_momentary()):
			isinstance(button, ButtonElement)
			raise AssertionError
		if self._shift_button != button:
			if self._shift_button != None:
				self._shift_button.remove_value_listener(self._shift_value)
			self._shift_button = button
			if self._shift_button != None:
				self._shift_button.add_value_listener(self._shift_value)
			self._rebuild_callback()
			self.update()
		return None
	

	def on_enabled_changed(self):
		self.update()
	

	def update(self):
		if self.is_enabled():
			self.is_enabled()
			if not self._shift_pressed:
				self._shift_pressed
				if self._left_button != None:
					self._left_button.turn_off()
				if self._right_button != None:
					self._right_button.turn_off()
				if self._device_clip_toggle_button != None:
					self._device_clip_toggle_button.turn_off()
				self._detail_view_visibility_changed()
			else:
				self._shift_pressed
		else:
			self.is_enabled()
		return None
	

	def _detail_view_visibility_changed(self):
		if self.is_enabled() and not self._shift_pressed and self._detail_toggle_button != None:
			if self.application().view.is_view_visible('Detail'):
				self.application().view.is_view_visible('Detail')
				self._detail_toggle_button.turn_on()
			else:
				self.application().view.is_view_visible('Detail')
				self._detail_toggle_button.turn_off()
		else:
			self.is_enabled()
		return None
	

	def _device_clip_toggle_value(self, value):
		if not self._device_clip_toggle_button != None:
			raise AssertionError
		if not value in range(128):
			raise AssertionError
		if self.is_enabled() and not self._shift_pressed:
			not self._shift_pressed
			button_is_momentary = self._device_clip_toggle_button.is_momentary()
			if not button_is_momentary or value != 0:
				not button_is_momentary
				if not self.application().view.is_view_visible('Detail'):
					self.application().view.is_view_visible('Detail')
					self.application().view.show_view('Detail')
				else:
					self.application().view.is_view_visible('Detail')
				if not self.application().view.is_view_visible('Detail/DeviceChain'):
					self.application().view.is_view_visible('Detail/DeviceChain')
					self.application().view.show_view('Detail/DeviceChain')
				else:
					self.application().view.is_view_visible('Detail/DeviceChain')
					self.application().view.show_view('Detail/Clip')
			if button_is_momentary and value != 0:
				self._show_playing_clip_ticks_delay = SHOW_PLAYING_CLIP_DELAY
			else:
				button_is_momentary
				self._show_playing_clip_ticks_delay = -1
		else:
			self.is_enabled()
		return None
	

	def _detail_toggle_value(self, value):
		assert (self._detail_toggle_button != None)
		assert (value in range(128))
		if (self.is_enabled() and (not self._shift_pressed)):
			if ((not self._detail_toggle_button.is_momentary()) or (value != 0)):
				if (not self.application().view.is_view_visible('Detail')):
					self.application().view.show_view('Detail')
				else:
					self.application().view.hide_view('Detail')		
	

	def _shift_value(self, value):
		if not self._shift_button != None:
			raise AssertionError
		if not value in range(128):
			raise AssertionError
		self._shift_pressed = value != 0
		self.update()
		return None
	

	def _nav_value(self, value, sender):
		assert ((sender != None) and (sender in (self._left_button,
												 self._right_button)))
		if (self.is_enabled() and (not self._shift_pressed)):
			if ((not sender.is_momentary()) or (value != 0)):
				modifier_pressed = True
				if ((not self.application().view.is_view_visible('Detail')) or (not self.application().view.is_view_visible('Detail/DeviceChain'))):
					self.application().view.show_view('Detail')
					self.application().view.show_view('Detail/DeviceChain')
				else:
					direction = Live.Application.Application.View.NavDirection.left
					if (sender == self._right_button):
						direction = Live.Application.Application.View.NavDirection.right
					self.application().view.scroll_view(direction, 'Detail/DeviceChain', (not modifier_pressed))
	

	def _on_timer(self):
		if (self.is_enabled() and (not self._shift_pressed)):
			if (self._show_playing_clip_ticks_delay > -1):
				if (self._show_playing_clip_ticks_delay == 0):
					song = self.song()
					playing_slot_index = song.view.selected_track.playing_slot_index
					if (playing_slot_index > -1):
						song.view.selected_scene = song.scenes[playing_slot_index]
						if song.view.highlighted_clip_slot.has_clip:
							self.application().view.show_view('Detail/Clip')
				self._show_playing_clip_ticks_delay -= 1
	


class Codec(ControlSurface):
	__module__ = __name__
	__doc__ = " MonoCode controller script "


	def __init__(self, c_instance, *a, **k):
		super(Codec, self).__init__(c_instance, *a, **k)
		self._monomod_version = 'b996'
		self._host_name = 'Codec'
		self._linked_script = None
		self._last_device = None
		self._device_list = [None, None, None, None]
		self._device_select_buttons = None
		self._last_device_component = None
		self._timer = 0
		self._touched = 0
		self._locked = False
		self.flash_status = 1
		self._shift_button = None
		self._use_device_selector = USE_DEVICE_SELECTOR
		self._device_selection_follows_track_selection=FOLLOW
		self._leds_last = 0
		self._shift_pressed = False
		self._shift_doublepressed = False
		self._alt_enabled = False
		with self.component_guard():
			self._setup_controls()
			self._setup_monobridge()
			self._setup_device_controls()
			self._setup_special_device_control() 
			self._device.append(self._special_device)			#necessary for device browsing to work with special device
			self._setup_device_chooser()
			self._setup_mixer_controls()
			self._setup_mod()
			self._setup_device_selector()
			self._setup_modes() 
			self._setup_send_reset()
			self._setup_default_buttons()
			self._setup_m4l_interface()
			self._initialize_code()
		self.log_message('<<<<<<<<<<<<<<<<<<<<<<<<< Codec ' + str(self._monomod_version) + ' log opened >>>>>>>>>>>>>>>>>>>>>>>>>')
		self.show_message('Codec Control Surface Loaded')
		self.request_rebuild_midi_map()
	

	"""script initialization methods"""
	def _initialize_code(self):
		if FACTORY_RESET:
			self._send_midi(factoryreset)
			self._send_midi(btn_channels)
			self._send_midi(enc_channels)	
	

	def _setup_monobridge(self):
		self._monobridge = MonoBridgeElement(self)
		self._monobridge.name = 'MonoBridge'
	

	def _setup_controls(self):
		is_momentary = True
		self._livid = DoublePressElement(CodecMonoButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, LIVID, 'Livid_Button', self))
		self._dial = [None for index in range(8)]
		for column in range(8):
			self._dial[column] = [None for index in range(4)]
			for row in range(4):
				self._dial[column][row] = CodecEncoderElement(MIDI_CC_TYPE, CHANNEL, CODE_DIALS[row][column], Live.MidiMap.MapMode.absolute, 'Dial_' + str(column) + '_' +	str(row), (column + (row*8)), self)	
				
		self._button = [None for index in range(8)]
		for column in range(8):
			self._button[column] = [None for index in range(4)]
			for row in range(4):
				self._button[column][row] = CodecMonoButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, CODE_BUTTONS[row][column], 'Button_' + str(column) + '_' + str(row), self) 
		

		self._column_button = [None for index in range(8)]
		for index in range(8):
			self._column_button[index] = CodecMonoButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, CODE_COLUMN_BUTTONS[index], 'Column_Button_' + str(index), self)		
			
		self._row_button = [None for index in range(4)]
		for index in range(4):
			self._row_button[index] = CodecMonoButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, CODE_ROW_BUTTONS[index], 'Row_Button_' + str(index), self)		

		self._code_keys = ButtonMatrixElement([self._column_button])
		self._code_buttons = ButtonMatrixElement([self._row_button])

		self._encoder_matrix = EncoderMatrixElement(self)
		self._encoder_matrix.name = 'Encoder_Matrix'
		for row in range(4):
			dial_row = tuple([self._dial[column][row] for column in range(8)])
			self._encoder_matrix.add_row(dial_row)

		self._button_matrix = ButtonMatrixElement()
		self._button_matrix.name = 'Button_Matrix'
		for row in range(4):
			button_row = [self._button[column][row] for column in range(8)]
			self._button_matrix.add_row(tuple(button_row))
	

	def _setup_modes(self):
		#self.set_shift_button(self._livid)
		self._main_mode = ShiftModeComponent(self._mode_update, self) 
		self._main_mode.name = 'Shift_Mode'
		self._main_mode.set_mode_buttons(tuple([self._row_button[0], self._row_button[1], self._row_button[2], self._row_button[3]]))
		#self._on_shift_doublepress_value.subject = self._livid.double_press
		self._shift_mode = ModesComponent()
		self._shift_mode.add_mode('shift', tuple([self._enable_shift, self._disable_shift]), behaviour = ShiftCancellableBehaviourWithRelease())
		self._shift_mode.set_mode_button('shift', self._livid)
		self._alt_mode = ModesComponent()
		self._alt_mode.add_mode('alt', tuple([self._enable_alt, self._disable_alt]), behaviour = CancellableBehaviourWithRelease())
	

	def _setup_transport_control(self):
		self._transport = TransportComponent() 
		self._transport.name = 'Transport'
	

	def _setup_mod(self):
		self.monomodular = get_monomodular(self)
		self.monomodular.name = 'monomodular_switcher'
		self.modhandler = CodecModHandler(self)
		self.modhandler.name = 'ModHandler'
		self.modhandler.layer = Layer( code_grid = self._button_matrix, code_encoder_grid = self._encoder_matrix, )# shift_button = self._shift_button))  parameter_controls = self._encoder_matrix,
		self.modhandler.set_enabled(False)
		self.modhandler.code_buttons_layer = AddLayerMode(self.modhandler, Layer(code_buttons = self._code_buttons, priority = 3))
		self.modhandler.keys_layer = AddLayerMode(self.modhandler, Layer(key_buttons = self._code_keys, priority = 3))
		self.modhandler.code_keys_layer = AddLayerMode(self.modhandler, Layer(code_keys = self._code_keys, priority = 3))
		self.modhandler.alt_layer = AddLayerMode(self.modhandler, Layer(lock_button = self._livid))
	

	def _setup_mixer_controls(self):
		is_momentary = True
		self._num_tracks = (8)
		self._session = SessionComponent(self._num_tracks, 0)
		self._session.name = 'Session'
		self._mixer = MixerComponent(self._num_tracks, 0, False, False)
		self._mixer.name = 'Mixer'
		self._mixer._next_track_value = self._mixer_next_track_value(self._mixer)
		self._mixer._prev_track_value = self._mixer_prev_track_value(self._mixer)
		self._mixer.set_track_offset(0)
		for index in range(8):
			self._mixer.channel_strip(index).name = 'Mixer_ChannelStrip_' + str(index)
			self._mixer.channel_strip(index)._invert_mute_feedback = True
			self._mixer.channel_strip(index)._mute_value = self._channelstrip_mute_value(self._mixer.channel_strip(index))
			self._mixer.channel_strip(index)._solo_value = self._channelstrip_solo_value(self._mixer.channel_strip(index))
			#self._mixer.channel_strip(index).select_layer = AddLayerMode(self._mixer.channel_strip(index), Layer(select_button = self._column_button[index], priority = 4))
			#self._mixer.channel_strip(index).set_select_button(self._column_button[index])
		self.song().view.selected_track = self._mixer.channel_strip(0)._track
		self._session.set_mixer(self._mixer)
	

	def _setup_device_controls(self):
		self._device = [None for index in range(4)]
		for index in range(4):
			self._device[index] = CodecDeviceComponent(self)
			self._device[index].name = 'CodecDevice_Component_' + str(index)
			device_param_controls = []
			for control in range(8):
				device_param_controls.append(self._dial[control][index])
			self._device[index].set_on_off_button(self._button[1][index])
			self._device[index].set_lock_button(self._button[2][index])
			self._device[index].set_bank_nav_buttons(self._button[4][index], self._button[5][index])
			self._device[index].set_nav_buttons(self._button[6][index], self._button[7][index])
			self._device[index].set_parameter_controls(tuple(device_param_controls))
		self.set_device_component(self._device[0])
		self._last_device_component = self._device[0]
	

	def _setup_special_device_control(self):
		self._special_device = SpecialCodecDeviceComponent(self)
		self._special_device.name = 'SpecialCodecDeviceComponent'
		self._special_device.set_on_off_button(self._button[1][0])
		self._special_device.set_lock_button(self._button[2][0])
		self._special_device.set_bank_nav_buttons(self._button[4][0], self._button[5][0])
		self._special_device.set_nav_buttons(self._button[6][0], self._button[7][0])
		#self._special_device._current_bank_details = self._make_current_bank_details(self._device)
		device_param_controls = []
		for row in range(4):
			for column in range(8):
				device_param_controls.append(self._dial[column][row])
		self._special_device.set_parameter_controls(tuple(device_param_controls))
		self._on_device_changed.subject = self.song()
	

	def _setup_device_chooser(self):
		self._selected_device = self._device[0]
		self._last_selected_device = self._device[0]
		self._device_select_buttons = [self._button[0][index] for index in range(4)]
		for button in self._device_select_buttons:
			button.add_value_listener(self._device_select_value, True)
	

	def _setup_device_selector(self):
		self._device_selector = DeviceSelectorComponent(self)
		self._device_selector.name = 'Device_Selector'
		self._device_selector.set_buttons(self._column_button)
		self._device_selector.set_enabled(False)
		#self._device_selector.layer = Layer(matrix = self._code_keys)
		#self._device_selector.layer.priority = 2
	

	def _setup_send_reset(self):
		self._send_reset = CodecResetSendsComponent(self)
		self._send_reset.set_buttons(self._button)
	

	def _setup_default_buttons(self):
		self._value_default = ParameterDefaultComponent(self)
		buttons = []
		dials = []
		for column in self._button:
			for button in column:
				buttons.append(button)
		for column in self._dial:
			for dial in column:
				dials.append(dial)
		self._value_default.set_buttons(buttons)
		self._value_default.set_dials(dials)
	

	def _setup_m4l_interface(self):
		self._m4l_interface = M4LInterfaceComponent(controls=self.controls, component_guard=self.component_guard)
		self.get_control_names = self._m4l_interface.get_control_names
		self.get_control = self._m4l_interface.get_control
		self.grab_control = self._m4l_interface.grab_control
		self.release_control = self._m4l_interface.release_control
	

	"""multiple device support"""
	def _device_select_value(self, value, sender):
		#self.log_message('device_select_value ' + str(value) + ' ' + str(self._device_select_buttons.index(sender)))
		if not self._shift_pressed:
			if sender.is_momentary or value > 0:
				if self._main_mode._mode_index == 2:
					self.set_device_component(self._device[self._device_select_buttons.index(sender)])
					self._last_device_component = self._device_component
					if self._device_component != None and isinstance(self._device_component._device, Live.Device.Device):
						if self._device_component.find_track(self._device_component._device) == self.song().view.selected_track:
							self._device_component.display_device()
	

	def _shift_value(self, value):
		debug('shift value:', value)
		if self.modhandler.is_enabled() and self._alt_enabled:
			self.modhandler.set_lock(not self.modhandler.is_locked())
			if not self.modhandler.is_locked():
				self.modhandler.select_appointed_device()
				self._main_mode.update()
		else:
			self._shift_pressed = value > 0
			#self.log_message('shift_pressed ' + str(self._shift_pressed))
			self._send_midi(ENCODER_SPEED[int(self._shift_pressed)])
			self._main_mode.set_enabled(not self._shift_pressed)
			self.update_modhandler_controls()
			if self._shift_pressed:
				self._alt_mode.pop_mode('alt')
				self._alt_mode.set_mode_button('alt', None)
			self.modhandler._shift_value(value)
		self._update_shift_button()
	

	def _update_shift_button(self):
		if self._livid != None:
			self._livid.send_value((self._shift_pressed > 0) or (self.modhandler.is_locked()*16), True)
	

	def _enable_alt(self):
		self._alt_enabled = True
		self._main_mode.set_enabled(False)
		for index in range(8):
			self._mixer.channel_strip(index).set_select_button(None)
		self.update_modhandler_controls()
		if self.modhandler.is_enabled():
			self.modhandler._alt_value(1)
		self._device_selector.set_enabled(True)
	

	def _disable_alt(self):
		self._alt_enabled = False
		self._main_mode.set_enabled(True)
		if self.modhandler.is_enabled():
			self.modhandler._alt_value(0)
		self._device_selector.set_enabled(False)
		self._mode_update()
	

	def _enable_shift(self):
		self._shift_value(1)
	

	def _disable_shift(self):
		self._shift_value(0)
	

	@subject_slot('value')
	def _on_shift_doublepress_value(self, value):
		#if not self.modhandler.is_enabled() and not self.modhandler.active_mod() is None:
		#	self._main_mode.set_mode(3)
		#	self.schedule_message(1, self._on_shift_doublepress_value, 1)

		if self.modhandler.is_enabled():
			self.modhandler.set_lock(not self.modhandler.is_locked())
			if not self.modhandler.is_locked():
				self.modhandler.select_appointed_device()
				self._main_mode.update()
		self._update_shift_button()
		#self.log_message('modlock: ' + str(self.modhandler.is_locked()))
	

	def update_modhandler_controls(self):
		handler = self.modhandler
		if handler.is_enabled():
			alt = self._alt_enabled
			if self._shift_pressed:
				if alt:
					handler.set_mod_nav_buttons([self._code_buttons[0], self._code_buttons[1]])
					handler.code_keys_layer.leave_mode()
				else:
					handler.keys_layer.leave_mode()
					handler.code_keys_layer.enter_mode()
					handler.code_buttons_layer.enter_mode()
					handler.set_mod_nav_buttons([None, None])
			else:
				if alt:
					handler.set_mod_nav_buttons([self._code_buttons[0], self._code_buttons[1]])
					handler.keys_layer.leave_mode()
				else:
					handler.code_keys_layer.leave_mode()
					handler.keys_layer.enter_mode()
					handler.set_mod_nav_buttons([None, None])
					handler.code_buttons_layer.leave_mode()
			handler.update()
	


	"""Mode Functions"""
	def _mode_update(self):
		#self.log_message('_mode_update: enabled = ' + str(self._main_mode.is_enabled()))
		if self._main_mode.is_enabled():
			with self.component_guard():
				self._deassign_all()
				self._alt_mode.set_mode_button('alt', None)
				if(self._main_mode._mode_index is 0):
					self._assign_volume()
				elif(self._main_mode._mode_index is 1):
					self._assign_sends()
				elif(self._main_mode._mode_index is 2):
					self._assign_devices()
				elif(self._main_mode._mode_index is 3):
					self._assign_special_device()
			self.schedule_message(3, self._assign_alt_button, self._main_mode._mode_index+1)
			self._update_mode_buttons()
			self._update_shift_button()
			self.request_rebuild_midi_map()
	

	def _assign_alt_button(self, mode):
		if self._main_mode._mode_index is (mode-1):
			button = self._row_button[mode-1]
			self._alt_mode.set_mode_button('alt', button)
			if button.is_pressed():
				self._alt_mode.selected_mode = 'alt'
	

	def _update_mode_buttons(self):
		if self._main_mode.is_enabled():
			if not self._main_mode._modes_buttons is None:
				for button in self._main_mode._modes_buttons:
					if self._main_mode._modes_buttons.index(button) == self._main_mode._mode_index:
						button.turn_on()
					else:
						button.turn_off()
	

	def _deassign_all(self):
		#self._alt_mode.pop_mode('alt')
		with self.component_guard():
			self.modhandler.set_enabled(False)
			if not self.modhandler._keys_value.subject is None:
				self.modhandler.keys_layer.leave_mode()
			if not self.modhandler._code_keys_value.subject is None:
				self.modhandler.code_keys_layer.leave_mode()
			if not self.modhandler._code_buttons_value.subject is None:
				self.modhandler.code_buttons_layer.leave_mode()
			#self._assign_alternate_mappings(0)
			for index in range(8):
				self._mixer.channel_strip(index).set_volume_control(None)
				self._mixer.channel_strip(index).set_pan_control(None)
				self._mixer.channel_strip(index).set_send_controls(tuple([None, None, None, None]))
			for index in range(4):
				self._device[index].set_on_off_button(None)
				self._device[index].set_lock_button(None)
				self._device[index].set_bank_nav_buttons(None, None)
				self._device[index].set_nav_buttons(None, None)
				self._device[index].set_enabled(False)
				self._device[index]._parameter_controls = None
			self._special_device.set_enabled(False)
			#self._special_device._parameter_controls = None
			self._deassign_buttons()
		self.request_rebuild_midi_map()
		for control in self.controls:
			if isinstance(control, (MonoButtonElement, CodecEncoderElement)):
				control.release_parameter()
				control.reset(True)

	

	def _deassign_buttons(self):
		for index in range(8):
			self._mixer.channel_strip(index).set_select_button(None)
			self._mixer.channel_strip(index).set_solo_button(None)
			self._mixer.channel_strip(index).set_mute_button(None)
		self._mixer.set_select_buttons(None, None)
		self._send_reset.set_enabled(False)
		for index in range(8):
			self._mixer.channel_strip(index).set_select_button(None)
	

	def _assign_volume(self):
		for index in range(8):
			self._mixer.channel_strip(index).set_volume_control(self._dial[index][3])
			self._mixer.channel_strip(index).set_pan_control(self._dial[index][2])
			self._mixer.channel_strip(index).set_send_controls(tuple([self._dial[index][0], self._dial[index][1]]))
			self._mixer.channel_strip(index).set_solo_button(self._button[index][2])
			self._mixer.channel_strip(index).set_mute_button(self._button[index][3])
		self._mixer.set_select_buttons(self._button[7][0], self._button[6][0])
		for index in range(8):
			self._mixer.channel_strip(index).set_select_button(self._column_button[index])
			#self._mixer.channel_strip(index).select_layer.enter_mode()
	

	def _assign_sends(self):
		for index in range(8):
			self._mixer.channel_strip(index).set_send_controls(tuple([self._dial[index][0], self._dial[index][1], self._dial[index][2], self._dial[index][3]]))
			self._send_reset.set_enabled(True)
			self._mixer.channel_strip(index).set_select_button(self._column_button[index])
			#self._mixer.channel_strip(index).select_layer.enter_mode()	
	

	def _assign_devices(self):
		self.set_device_component(self._last_device_component)
		self._device_select_value(1, self._device_select_buttons[self._device.index(self._device_component)])
		for index in range(4):
			device_param_controls = []
			for control in range(8):
				device_param_controls.append(self._dial[control][index])
			self._device[index].set_on_off_button(self._button[1][index])
			self._device[index].set_lock_button(self._button[2][index])
			self._device[index].set_bank_nav_buttons(self._button[4][index], self._button[5][index])
			self._device[index].set_nav_buttons(self._button[6][index], self._button[7][index])
			self._device[index].set_parameter_controls(tuple(device_param_controls))
			self._device[index].set_enabled(True)
		for index in range(8):
			self._mixer.channel_strip(index).set_select_button(self._column_button[index])
			#self._mixer.channel_strip(index).select_layer.enter_mode()
	

	def _assign_special_device(self):
		if not self.modhandler.active_mod() is None:
			self.modhandler.set_enabled(True)
			self.update_modhandler_controls()
			#self.log_message('enabled mod')
		else:
			self.set_device_component(self._special_device)

			#device_param_controls = []
			#for row in range(4):
			#	for column in range(8):
			#		device_param_controls.append(self._dial[column][row])
			#self._special_device.set_parameter_controls(tuple(device_param_controls))

			self._special_device.set_enabled(True)
			if not self._alt_mode.selected_mode is 'alt':
				for index in range(8):
					self._mixer.channel_strip(index).set_select_button(self._column_button[index])
				#self._mixer.channel_strip(index).select_layer.enter_mode()
			#self.log_message('disabled mod')
	

	def _assign_alternate_mappings(self, chan):
		for column in self._dial:
			for control in column:
				control.set_channel(chan)
				control.set_enabled(chan is 0)
		for column in self._button:
			for control in column:
				control.set_channel(chan)
				control.set_enabled(chan is 0)
		for control in self._column_button:
			control.set_channel(chan)
			control.set_enabled(chan is 0)
		for control in self._row_button:
			control.set_channel(chan)
			control.set_enabled(chan is 0)
	

	@subject_slot('appointed_device')
	def _on_device_changed(self):
		#self.log_message('_on_device_changed')
		if self._main_mode._mode_index is 3 and not self.modhandler.is_locked():
			self.schedule_message(4, self._mode_update)
	


	"""general functionality"""
	def disconnect(self):
		"""clean things up on disconnect"""
		for button in self._device_select_buttons:
			if button.value_has_listener(self._device_select_value):
				button.remove_value_listener(self._device_select_value)
		if self._session._is_linked():
			self._session._unlink()
		self.log_message('<<<<<<<<<<<<<<<<<<<<<<<<< Codec log closed >>>>>>>>>>>>>>>>>>>>>>>>>')
		super(Codec, self).disconnect()
		rebuild_sys()
	

	def update_display(self):
		super(Codec, self).update_display()
		self._timer = (self._timer + 1) % 256
		self.modhandler.send_ring_leds()
		self.flash()
	

	def flash(self):
		if(self.flash_status > 0):
			for control in self.controls:
				if isinstance(control, MonoButtonElement):
					control.flash(self._timer)
	

	def handle_sysex(self, *a):
		pass
	


	"""m4l bridge"""
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
		assert (len(ret) == NUM_CHARS_PER_DISPLAY_STRIP)
		return ret
	

	def notification_to_bridge(self, name, value, sender):
		if(isinstance(sender, CodecEncoderElement)):
			self._monobridge._send(sender.name, 'lcd_name', str(self.generate_strip_string(name)))
			self._monobridge._send(sender.name, 'lcd_value', str(self.generate_strip_string(value)))
	

	def touched(self):
		if self._touched is 0:
			self._monobridge._send('touch', 'on')
			self.schedule_message(2, self.check_touch)
		self._touched +=1
	

	def check_touch(self):
		if self._touched > 5:
			self._touched = 5
		elif self._touched > 0:
			self._touched -= 1
		if self._touched is 0:
			self._monobridge._send('touch', 'off')
		else:
			self.schedule_message(2, self.check_touch)
	

	def restart_monomodular(self):
		#self.log_message('restart monomodular')
		self.modhandler.disconnect()
		with self.component_guard():
			self._setup_mod()
	

	def connect_script_instances(self, instanciated_scripts):
		#self.log_message('connect script instances')
		pass
	


	"""overrides"""
	def allow_updates(self, allow_updates):
		for component in self.components:
			component.set_allow_update(int(allow_updates!=0))
	

	def set_device_component(self, device_component):
		if self._device_component != None:
			self._device_component._lock_callback = None
		self._device_component = device_component
		self._c_instance.update_locks()
		#self._device_component._lock_callback = self._toggle_lock	#old:  self._device_component.set_lock_callback(self._toggle_lock)
		if device_component is not None:
			self._device_component._lock_callback = self._toggle_lock
			if self._device_selection_follows_track_selection:
				self.schedule_message(1, self._update_device_selection)
			if self._device_select_buttons != None:
				for button in self._device_select_buttons:
					button.send_value(self._device_select_buttons.index(button) == self._device.index(self._device_component))
	

	def _get_num_tracks(self):
		return self.num_tracks
	

	def _channelstrip_mute_value(self, channelstrip):
		def _mute_value(value):
			if not self._shift_pressed:
				#self.log_message('shift not pressed')
				ChannelStripComponent._mute_value(channelstrip, value)
		return _mute_value
		
	

	def _channelstrip_solo_value(self, channelstrip):
		def _solo_value(value):
			if not self._shift_pressed:
				ChannelStripComponent._solo_value(channelstrip, value)
		return _solo_value
		
	

	def _mixer_next_track_value(self, mixer):
		def _next_track_value(value):
			if not self._shift_pressed:
				MixerComponent._next_track_value(mixer, value)
		return _next_track_value
		
	

	def _mixer_prev_track_value(self, mixer):
		def _prev_track_value(value):
			if not self._shift_pressed:
				MixerComponent._prev_track_value(mixer, value)
		return _prev_track_value
		
	

	def _make_current_bank_details(self, device_component):
		def _current_bank_details():
			if not self._is_mod(device_component.device()) is None:
				if self.modhandler.active_mod() and self.modhandler.active_mod()._param_component._device_parent != None:
					bank_name = self.modhandler.active_mod()._param_component._bank_name
					bank = [param._parameter for param in self.modhandler.active_mod()._param_component._params]
					if self.modhandler._shift_value.subject and self.modhandler._shift_value.subject.is_pressed():
						bank = bank[8:]
					#self.log_message('current mod bank details: ' + str(bank_name) + ' ' + str(bank))
					return (bank_name, bank)
				else:
					return DeviceComponent._current_bank_details(device_component)
			else:
				return DeviceComponent._current_bank_details(device_component)
		return _current_bank_details
		
	


class ParameterDefaultComponent(ControlSurfaceComponent):
	__module__ = __name__
	__doc__ = " MonoCode controller script "


	def __init__(self, script):
		"""everything except the '_on_selected_track_changed' override and 'disconnect' runs from here"""
		ControlSurfaceComponent.__init__(self)
		self._script = script
		self._buttons = []
		self._dials = []
	

	def set_buttons(self, buttons):
		for button in self._buttons:
			if button.value_has_listener(self._value_to_default):
				button.remove_value_listener(self._value_to_default)
		self._buttons = buttons
		for button in self._buttons:
			button.add_value_listener(self._value_to_default, True)
	

	def set_dials(self, dials):
		assert(len(dials) == len(self._buttons))
		self._dials = dials
	

	def _value_to_default(self, value, sender):
		if value > 0 and self._script._shift_pressed:
			dial = self._dials[self._buttons.index(sender)]
			if dial != None:
				if dial.mapped_parameter() != None:
					if hasattr(dial.mapped_parameter(), 'default_value'):
						dial.mapped_parameter().value = dial.mapped_parameter().default_value
	

	def update(self):
		pass
	

	def disconnect(self):
		for button in self._buttons:
			if button.value_has_listener(self._value_to_default):
				button.remove_value_listener(self._value_to_default)
	


class CodecModHandler(ModHandler):


	def __init__(self, *a, **k):
		#super(CodecModHandler, self).__init__(*a, **k)
		self._local = True
		self._last_sent_leds = 1
		self._code_grid = None
		self._code_encoder_grid = None
		self._code_keys = None
		self._code_buttons = None
		addresses = {'code_grid': {'obj':Grid('code_grid', 8, 4), 'method':self._receive_code_grid},
					'code_encoder_grid': {'obj':RingedGrid('code_encoder_grid', 8, 4), 'method':self._receive_code_encoder_grid},
					'code_key': {'obj':  Array('code_key', 8), 'method': self._receive_code_key},
					'code_button': {'obj':  Array('code_button', 4), 'method': self._receive_code_button}}
		super(CodecModHandler, self).__init__(addresses = addresses, *a, **k)
		self._color_type = 'Monochrome'
		self.nav_box = self.register_component(NavigationBox(self, 16, 16, 2, 2, self.set_offset))

		self._colors = range(128)
	

		#'code_encoder_grid_relative': {'obj':StoredElement(_name = 'code_encoder_grid_relative'), 'method':self._receive_code_encoder_grid_relative},
		#'code_encoder_grid_local': {'obj':StoredElement(_name = 'code_encoder_grid_local'), 'method':self._receive_code_encoder_grid_local},

	def _receive_code_grid(self, x, y, value, *a, **k):
		#self.log_message('_receive_code_grid: %(x)s %(y)s %(value)s ' % {'x':x, 'y':y, 'value':value})
		if self.is_enabled() and self._active_mod and not self._active_mod.legacy and not self._code_grid_value.subject is None and x < 8 and y < 4:
			self._code_grid_value.subject.send_value(x, y, self._colors[value], True)
	

	def _receive_code_encoder_grid(self, x, y, *a, **k):
		#self.log_message('_receive_code_encoder_grid: %(x)s %(y)s %(k)s' % {'x':x, 'y':y, 'k':k})
		if self.is_enabled() and self._active_mod and not self._code_encoder_grid_value.subject is None and x < 8 and y < 4:
			keys = k.keys()
			if 'value' in keys:
				if self._local:
					self._code_encoder_grid_value.subject.send_value(x, y, k['value'], True)
				else:
					self._code_encoder_grid_value.subject.get_button(x, y)._ring_value = k['value']
			if 'mode' in keys:
				self._code_encoder_grid_value.subject.get_button(x, y).set_mode(k['mode'])
			if 'green' in keys:
				self._code_encoder_grid_value.subject.get_button(x, y).set_green(k['green'])
			if 'custom' in keys:
				self._code_encoder_grid_value.subject.get_button(x, y).set_custom(k['custom'])
			if 'local' in keys:
				self._receive_code_encoder_grid_local(k['local'])
			if 'relative' in keys:
				self._receive_code_encoder_grid_relative(k['relative'])
	

	def _receive_code_encoder_grid_relative(self, value, *a):
		#self.log_message('_receive_code_encoder_grid_relative: %(v)s' % {'v':value})
		if self.is_enabled() and self._active_mod:
			value and self._script._send_midi(tuple([240, 0, 1, 97, 4, 17, 127, 127, 127, 127, 127, 127, 127, 127, 247])) or self._script._send_midi(tuple([240, 0, 1, 97, 4, 17, 0, 0, 0, 0, 0, 0, 0, 0, 247]))
	

	def _receive_code_encoder_grid_local(self, value, *a):
		#self.log_message('_receive_code_encoder_grid_local: %(v)s' % {'v':value})
		if self.is_enabled() and self._active_mod:
			self.clear_rings()
			self._local = bool(value)
			value and self._script._send_midi(tuple([240, 0, 1, 97, 4, 8, 72, 247])) or self._script._send_midi(tuple([240, 0, 1, 97, 4, 8, 64, 247]))
	

	def _receive_code_button(self, num, value, *a):
		#self._script.log_message('receive code_button' + str(num) + str(value))
		if self.is_enabled() and self._active_mod:
			if not self._code_buttons_value.subject is None:
				self._code_buttons_value.subject.send_value(num, 0, self._colors[value], True)
	

	def _receive_code_key(self, num, value, *a):
		if self.is_enabled() and self._active_mod and not self._active_mod.legacy:
			if not self._code_keys_value.subject is None:
				self._code_keys_value.subject.send_value(num, 0, self._colors[value], True)
	

	def _receive_grid(self, x, y, value, *a, **k):
		if self.is_enabled() and self._active_mod and self._active_mod.legacy:
			if not self._code_grid_value.subject is None:
				if (x - self.x_offset) in range(8) and (y - self.y_offset) in range(4):
					self._code_grid_value.subject.send_value(x - self.x_offset, y - self.y_offset, self._colors[value], True)
	

	def set_code_grid(self, grid):
		self._code_grid = grid
		self._code_grid_value.subject = self._code_grid
	

	def set_code_encoder_grid(self, grid):
		self._code_encoder_grid = grid
		self._code_encoder_grid_value.subject = self._code_encoder_grid
		self.set_parameter_controls(grid)
		#self.log_message('parameter controls are: ' + str(self._parameter_controls))
	

	def set_code_keys(self, keys):
		self._code_keys = keys
		self._code_keys_value.subject = self._code_keys
	

	def set_code_buttons(self, buttons):
		#self.log_message('set code buttons ' + str(buttons))
		self._code_buttons = buttons
		self._code_buttons_value.subject = self._code_buttons
	

	@subject_slot('value')
	def _alt_value(self, value, *a, **k):
		self._is_alted = not value is 0
		mod = self.active_mod()
		if mod:
			mod.send('alt', value)
		self.update()
	

	@subject_slot('value')
	def _code_keys_value(self, value, x, y, *a, **k):
		#self.log_message('_code_keys_value: %(x)s %(y)s %(value)s ' % {'x':x, 'y':y, 'value':value})
		if self._active_mod:
			self._active_mod.send('code_key', x, int(value>0))
	

	@subject_slot('value')
	def _code_buttons_value(self, value, x, y, *a, **k):
		#self.log_message('_code_buttons_value: %(x)s %(y)s %(value)s ' % {'x':x, 'y':y, 'value':value})
		if self._active_mod:
			self._active_mod.send('code_button', x, int(value>0))
	

	@subject_slot('value')
	def _code_grid_value(self, value, x, y, *a, **k):
		#self.log_message('_code_grid_value: %(x)s %(y)s %(value)s ' % {'x':x, 'y':y, 'value':value})
		if self._active_mod:
			if self._active_mod.legacy:
				self._active_mod.send('grid', x + self.x_offset, y + self.y_offset, int(value>0))
			else:
				self._active_mod.send('code_grid', x, y, int(value>0))
	

	@subject_slot('value')
	def _code_encoder_grid_value(self, value, x, y, *a, **k):
		#self.log_message('_code_encoder_grid_value: %(x)s %(y)s %(value)s ' % {'x':x, 'y':y, 'value':value})
		if self._active_mod:
			self._active_mod.send('code_encoder_grid', x, y, int(value>0))
	

	def update(self, *a, **k):
		mod = self.active_mod()
		#self.log_message('modhandler update: ' + str(mod))
		if self.is_enabled() and not mod is None:
			mod.restore()
		else:
			#self._script.log_message('disabling modhandler')
			self._script._send_midi(tuple([240, 0, 1, 97, 4, 17, 0, 0, 0, 0, 0, 0, 0, 0, 247]))
			self._script._send_midi(tuple([240, 0, 1, 97, 4, 8, 72, 247]))
			if not self._code_grid_value.subject is None:
				self._code_grid_value.subject.reset()
			if not self._code_encoder_grid_value.subject is None:
				self._code_encoder_grid_value.subject.reset()
			if not self._keys_value.subject is None:
				self._keys_value.subject.reset()
	

	def send_ring_leds(self):
		if self.is_enabled() and self._active_mod and not self._local and self._code_encoder_grid_value:
			leds = [240, 0, 1, 97, 4, 31]
			for encoder, coords in self._code_encoder_grid.xiterbuttons():
				bytes = encoder._get_ring()
				leds.append(bytes[0])
				leds.append(int(bytes[1]) + int(bytes[2]))
			leds.append(247)
			if not leds==self._last_sent_leds:
				self._script._send_midi(tuple(leds))
				self._last_sent_leds = leds
	

	def clear_rings(self):
		self._last_sent_leds = 1
	



#
#