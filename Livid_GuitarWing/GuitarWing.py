# by amounra 0613 : http://www.aumhaa.com




from __future__ import with_statement
import Live
import math
import sys
from _Tools.re import *
from itertools import imap, chain, starmap

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
from _Framework.MixerComponent import MixerComponent # Class encompassing several channel strips to form a mixer
from _Framework.ModeSelectorComponent import ModeSelectorComponent # Class for switching between modes, handle several functions with few controls
from _Framework.NotifyingControlElement import NotifyingControlElement # Class representing control elements that can send values
from _Framework.SceneComponent import SceneComponent # Class representing a scene in Live
from _Framework.SessionComponent import SessionComponent # Class encompassing several scene to cover a defined section of Live's session
from _Framework.SessionZoomingComponent import SessionZoomingComponent # Class using a matrix of buttons to choose blocks of clips in the session
from _Framework.SliderElement import SliderElement # Class representing a slider on the controller
from _Framework.TrackEQComponent import TrackEQComponent # Class representing a track's EQ, it attaches to the last EQ device in the track
from _Framework.TrackFilterComponent import TrackFilterComponent # Class representing a track's filter, attaches to the last filter in the track
from _Framework.TransportComponent import TransportComponent # Class encapsulating all functions in Live's transport section
from _Framework.PhysicalDisplayElement import PhysicalDisplayElement
from _Framework.SubjectSlot import subject_slot, subject_slot_group
from _Framework.Layer import Layer


#This stuff is changing from Push...  to _Framework...  between 9.1.1 and 9.2
from Push.M4LInterfaceComponent import M4LInterfaceComponent
from Push.ComboElement import ComboElement, DoublePressElement, MultiElement, DoublePressContext
from Push.ClipCreator import ClipCreator
from Push.Skin import *

"""Custom files, overrides, and files from other scripts"""
from _Mono_Framework.MonoButtonElement import *
from _Mono_Framework.MonoEncoderElement import MonoEncoderElement
from _Mono_Framework.MonoBridgeElement import MonoBridgeElement
from _Mono_Framework.MonoDeviceComponent import MonoDeviceComponent
from _Mono_Framework.ModDevices import *
from _Mono_Framework.Mod import *

"""to be included from Monomodular"""
import sys
import _Mono_Framework.modRemixNet as RemixNet
import _Mono_Framework.modOSC

from Map import *

MIDI_NOTE_TYPE = 0
MIDI_CC_TYPE = 1
MIDI_PB_TYPE = 2
MIDI_MSG_TYPES = (MIDI_NOTE_TYPE, MIDI_CC_TYPE, MIDI_PB_TYPE)
MIDI_NOTE_ON_STATUS = 144
MIDI_NOTE_OFF_STATUS = 128
MIDI_CC_STATUS = 176
MIDI_PB_STATUS = 224

def is_device(device):
	return (not device is None and isinstance(device, Live.Device.Device) and hasattr(device, 'name'))


def make_pad_translations(chan):
	return tuple((x%4, int(x/4), x+16, chan) for x in range(16))


"""
class GuitarWingSessionRecordingComponent(SessionRecordingComponent):


	def __init__(self, *a, **k):
		self._length_value = 1
		super(GuitarWingSessionRecordingComponent, self).__init__(*a, **k)
		self._length_buttons = []
	

	def _get_selected_length(self):
		song = self.song()
		length = 2.0 ** (LENGTH_VALUES[self._length_value])
		quant = LAUNCH_QUANTIZATION[(LENGTH_VALUES[self._length_value])]
		#if self._length_value > 1:
		length = length * song.signature_numerator / song.signature_denominator
		return (length, quant)
	

	def set_length_buttons(self, buttons):
		if buttons != self._length_buttons:
			for button in self._length_buttons:
				if button.value_has_listener(self._on_length_button):
					button.remove_value_listener(self._on_length_button)
			if buttons == None:
				buttons = []
			self._length_buttons = buttons
			for button in self._length_buttons:
				button.add_value_listener(self._on_length_button, True)
			self.update_length_buttons()
	

	def _on_length_button(self, value, sender):
		if value > 0:
			self._length_value = self._length_buttons.index(sender)
			self.update_length_buttons()
	

	def update(self, *a, **k):
		super(GuitarWingSessionRecordingComponent, self).update(*a, **k)
		if self.is_enabled():
			self.update_length_buttons()
	
"""

class GuitarWingSessionComponent(SessionComponent):


	def __init__(self, num_tracks, num_scenes, script):
		super(GuitarWingSessionComponent, self).__init__(num_tracks, num_scenes)
		self._shifted = False
		self._script = script
	

	def deassign_all(self):
		self._shifted = False
		self.set_scene_bank_buttons(None, None)
		self.set_track_bank_buttons(None, None)
		self.set_stop_all_clips_button(None)
		self.set_stop_track_clip_buttons(None)
		self.set_select_buttons(None, None)
		for scene in self._scenes:
			scene.set_launch_button(None)
			for slot in scene._clip_slots:
				slot.set_launch_button(None)
	

	def _bank_up_value(self, value):
		assert (value in range(128))
		assert (self._bank_up_button != None)
		if self.is_enabled():
			button_is_momentary = self._bank_up_button.is_momentary()
			if button_is_momentary:
				if (value != 0):
					self._scroll_up_ticks_delay = INITIAL_SCROLLING_DELAY
				else:
					self._scroll_up_ticks_delay = -1
			if ((not self._is_scrolling()) and ((value is not 0) or (not button_is_momentary))):
				self.set_offsets(self._track_offset, (self._scene_offset + (1+(self._shifted*3))))
	

	def _bank_down_value(self, value):
		assert (value in range(128))
		assert (self._bank_down_button != None)
		if self.is_enabled():
			button_is_momentary = self._bank_down_button.is_momentary()
			if button_is_momentary:
				if (value != 0):
					self._scroll_down_ticks_delay = INITIAL_SCROLLING_DELAY
				else:
					self._scroll_down_ticks_delay = -1
			if ((not self._is_scrolling()) and ((value is not 0) or (not button_is_momentary))):
				self.set_offsets(self._track_offset, max(0, self._scene_offset - (1+(self._shifted*3))))
	

	def _bank_right_value(self, value):
		assert (value in range(128))
		assert (self._bank_right_button != None)
		if self.is_enabled():
			button_is_momentary = self._bank_right_button.is_momentary()
			if button_is_momentary:
				if (value != 0):
					self._scroll_right_ticks_delay = INITIAL_SCROLLING_DELAY
				else:
					self._scroll_right_ticks_delay = -1
			if ((not self._is_scrolling()) and ((value is not 0) or (not button_is_momentary))):
				self.set_offsets((self._track_offset + (1+(self._shifted*7))), self._scene_offset)
	

	def _bank_left_value(self, value):
		assert isinstance(value, int)
		assert (self._bank_left_button != None)
		if self.is_enabled():
			button_is_momentary = self._bank_left_button.is_momentary()
			if button_is_momentary:
				if (value != 0):
					self._scroll_left_ticks_delay = INITIAL_SCROLLING_DELAY
				else:
					self._scroll_left_ticks_delay = -1
			if ((not self._is_scrolling()) and ((value is not 0) or (not button_is_momentary))):
				self.set_offsets(max(0, (self._track_offset - (1+(self._shifted*7)))), self._scene_offset)
	


class GuitarWingDeviceComponent(DeviceComponent):


	def __init__(self, script, *a, **k):
		super(GuitarWingDeviceComponent, self).__init__(*a, **k)
		self._script = script
	

	def deassign_all(self):
		self.set_parameter_controls(None)
		self.set_bank_nav_buttons(None, None)
		self.set_bank_buttons(None)
	

	def set_parameter_controls(self, controls):
		assert (controls is None) or isinstance(controls, tuple)
		if self._device != None and self._parameter_controls != None:
			for control in self._parameter_controls:
				control.release_parameter()
		if not controls is None:
			for control in controls:
				assert (control != None)
				assert isinstance(control, EncoderElement)
		self._parameter_controls = controls
		self.update()
		return None
	

	def _is_banking_enabled(self):
		return True
	

	def _on_device_bank_changed(self, *a, **k):
		super(GuitarWingDeviceComponent, self)._on_device_bank_changed(*a, **k)
		self._script._on_device_bank_changed()
	


class DeviceNavigator(ControlSurfaceComponent):
	__module__ = __name__
	__doc__ = ' Component that can toggle the device chain- and clip view of the selected track '


	def __init__(self, device_component, mixer, script):
		super(DeviceNavigator, self).__init__()
		self._prev_button = None
		self._next_button = None
		self._enter_button = None
		self._exit_button = None
		self._chain_prev_button = None
		self._chain_next_button = None
		self._device = device_component
		self._mixer = mixer
		self._script = script
		return None
	

	def deassign_all(self):
		self.set_nav_buttons(None, None)
		self.set_layer_buttons(None, None)
		self.set_chain_nav_buttons(None, None)
	

	def set_nav_buttons(self, prev_button, next_button):
		#self._script.log_message('set nav: ' + str(prev_button) + ' ' + str(next_button))
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
	

	def set_chain_nav_buttons(self, chain_prev_button, chain_next_button):
		#self._script.log_message('set nav: ' + str(prev_button) + ' ' + str(next_button))
		identify_sender = True
		if self._chain_prev_button != None:
			if self._chain_prev_button.value_has_listener(self._chain_nav_value):
				self._chain_prev_button.remove_value_listener(self._chain_nav_value)
		self._chain_prev_button = chain_prev_button
		if self._chain_prev_button != None:
			self._chain_prev_button.add_value_listener(self._chain_nav_value, identify_sender)
		if self._chain_next_button != None:
			if self._chain_next_button.value_has_listener(self._chain_nav_value):
				self._chain_next_button.remove_value_listener(self._chain_nav_value)
		self._chain_next_button = chain_next_button
		if self._chain_next_button != None:
			self._chain_next_button.add_value_listener(self._chain_nav_value, identify_sender)
		self.update()
		return None
	

	def set_layer_buttons(self, enter_button, exit_button):
		#self._script.log_message('set nav: ' + str(prev_button) + ' ' + str(next_button))
		identify_sender = True
		if self._enter_button != None:
			if self._enter_button.value_has_listener(self._enter_value):
				self._enter_button.remove_value_listener(self._enter_value)
		self._enter_button = enter_button
		if self._enter_button != None:
			self._enter_button.add_value_listener(self._enter_value)
		if self._exit_button != None:
			if self._exit_button.value_has_listener(self._exit_value):
				self._exit_button.remove_value_listener(self._exit_value)
		self._exit_button = exit_button
		if self._exit_button != None:
			self._exit_button.add_value_listener(self._exit_value)
		self.update()
		return None
	

	def update(self):
		track = self._mixer.selected_strip()._track
		if self._device._device and isinstance(self._device._device.canonical_parent, Live.Chain.Chain):
			track = self._device._device.canonical_parent
		if track != None:
			if not self._prev_button is None:
				if self._device._device and len(track.devices)>0 and self._device._device in track.devices and [t for t in track.devices].index(self._device._device)>0:
					self._prev_button.turn_on()
				else:
					self._prev_button.turn_off()
			if not self._next_button is None:
				if self._device._device and len(track.devices)>0 and self._device._device in track.devices and [t for t in track.devices].index(self._device._device)<(len(track.devices)-1):
					self._next_button.turn_on()
				else:
					self._next_button.turn_off()
			if not self._chain_prev_button is None:
				if self._device._device and isinstance(self._device._device.canonical_parent, Live.Chain.Chain):
					parent_chain = self._device._device.canonical_parent
					parent = parent_chain.canonical_parent
					if len(parent.chains)>0 and parent_chain in parent.chains and [c for c in parent.chains].index(parent_chain)>0:
						self._chain_prev_button.turn_on()
					else:
						self._chain_prev_button.turn_off()
			if not self._chain_next_button is None:
				if self._device._device and isinstance(self._device._device.canonical_parent, Live.Chain.Chain):
					parent_chain = self._device._device.canonical_parent
					parent = parent_chain.canonical_parent
					if len(parent.chains)>0 and parent_chain in parent.chains and [c for c in parent.chains].index(parent_chain)<(len(parent.chains)-1):
						self._chain_next_button.turn_on()
					else:
						self._chain_next_button.turn_off()
			if not self._enter_button is None:
				if self._device._device and self._device._device.can_have_chains and len(self._device._device.chains):
					self._enter_button.turn_on()
				else:
					self._enter_button.turn_off()
			if not self._exit_button is None:
				if self._device._device and self._device._device.canonical_parent and isinstance(self._device._device.canonical_parent, Live.Chain.Chain):
					self._exit_button.turn_on()
				else:
					self._exit_button.turn_off()
	

	def _nav_value(self, value, sender):
		if self.is_enabled():
			if ((not sender.is_momentary()) or (value != 0)):
				track = self._mixer.selected_strip()._track
				if self._device._device and isinstance(self._device._device.canonical_parent, Live.Chain.Chain):
					track = self._device._device.canonical_parent
				if track != None:
					if(sender == self._prev_button):
						#self._script.log_message('prev button')
						if self._device._device and self._device._device in track.devices:
							device = track.devices[min(len(track.devices)-1, max(0, [item for item in track.devices].index(self._device._device)-1))]
							self._script.set_appointed_device(device)
							self.song().view.select_device(device)
					elif(sender == self._next_button):
						if self._device._device and self._device._device in track.devices:
							#self._script.log_message('next button')
							device = track.devices[min(len(track.devices)-1, max(0, [item for item in track.devices].index(self._device._device)+1))]
							self._script.set_appointed_device(device)
							self.song().view.select_device(device)	
	

	def _chain_nav_value(self, value, sender):
		if self.is_enabled():
			if ((not sender.is_momentary()) or (value != 0)):
				track = self._mixer.selected_strip()._track
				if track != None:
					if(sender == self._chain_prev_button):
						#self._script.log_message('prev button')
						if self._device._device and isinstance(self._device._device.canonical_parent, Live.Chain.Chain):
							parent_chain = self._device._device.canonical_parent
							parent = parent_chain.canonical_parent
							device = parent.chains[min(len(parent.chains)-1, max(0, [item for item in parent.chains].index(parent_chain)-1))].devices[0]
							self._script.set_appointed_device(device)
							self.song().view.select_device(device)
					elif(sender == self._chain_next_button):
						if self._device._device and isinstance(self._device._device.canonical_parent, Live.Chain.Chain):
							parent_chain = self._device._device.canonical_parent
							parent = parent_chain.canonical_parent
							device = parent.chains[min(len(parent.chains)-1, max(0, [item for item in parent.chains].index(parent_chain)+1))].devices[0]
							self._script.set_appointed_device(device)
							self.song().view.select_device(device)
	

	def _enter_value(self, value):
		#self._script.log_message('enter: ' + str(value) + ' ; ' + str(self._device._device.can_have_chains) + ' ' + str(len(self._device._device.chains)))
		if value:
			if self._device._device and self._device._device.can_have_chains and len(self._device._device.chains):
				device = self._device._device.chains[0].devices[0]
				self._script.set_appointed_device(device)
				self.song().view.select_device(device)
	

	def _exit_value(self, value):
		#self._script.log_message('exit: ' + str(value) + ' ; ' + str(self._device._device.canonical_parent) + ' ' + str(isinstance(self._device._device.canonical_parent, Live.Chain.Chain)))
		if value:
			if self._device._device and self._device._device.canonical_parent and isinstance(self._device._device.canonical_parent, Live.Chain.Chain):
				device = self._device._device.canonical_parent.canonical_parent
				self._script.set_appointed_device(device)
				self.song().view.select_device(device)
	

	def disconnect(self):
		if self._prev_button != None:
			if self._prev_button.value_has_listener(self._nav_value):
				self._prev_button.remove_value_listener(self._nav_value)
		if self._next_button != None:
			if self._next_button.value_has_listener(self._nav_value):
				self._next_button.remove_value_listener(self._nav_value)	
	

	def _find_track(self, obj):
		if(type(obj.canonical_parent) == type(self.song().tracks[0])):
			return obj.canonical_parent
		elif(type(obj.canonical_parent)==type(None)) or (type(obj.canonical_parent)==type(self.song())):
			return None
		else:
			return self.find_track(obj.canonical_parent)
	

	def on_enabled_changed(self):
		pass
	


class ScrollingOffsetComponent(ControlSurfaceComponent):
	__module__ = __name__
	__doc__ = ' Class for handling held buttons for continued value changes '


	def __init__(self, callback):
		super(ScrollingOffsetComponent, self).__init__()
		self._report_change = callback
		self._offset = 0
		self._maximum = 127
		self._minimum = 0
		self._shifted = False
		self._shifted_value = 11
		self._scroll_up_ticks_delay = -1
		self._scroll_down_ticks_delay = -1	
		self._scroll_up_button = None
		self._scroll_down_button = None
		self._shift_button = None
		self._shift_is_momentary = True
		self._register_timer_callback(self._on_timer)
	

	def disconnect(self):
		if (self._scroll_up_button != None):
			self._scroll_up_button.remove_value_listener(self._scroll_up_value)
			self._scroll_up_button = None
		if (self._scroll_down_button != None):
			self._scroll_down_button.remove_value_listener(self._scroll_down_value)
			self._scroll_down_button = None
	

	def on_enabled_changed(self):
		self._scroll_up_ticks_delay = -1
		self._scroll_down_ticks_delay = -1
		self.update()
	

	def set_offset_change_buttons(self, up_button, down_button):
		assert ((up_button == None) or isinstance(up_button, ButtonElement))
		assert ((down_button == None) or isinstance(down_button, ButtonElement))
		do_update = False
		if (up_button is not self._scroll_up_button):
			do_update = True
			if (self._scroll_up_button != None):
				self._scroll_up_button.remove_value_listener(self._scroll_up_value)
			self._scroll_up_button = up_button
			if (self._scroll_up_button != None):
				self._scroll_up_button.add_value_listener(self._scroll_up_value)
		if (down_button is not self._scroll_down_button):
			do_update = True
			if (self._scroll_down_button != None):
				self._scroll_down_button.remove_value_listener(self._scroll_down_value)
			self._scroll_down_button = down_button
			if (self._scroll_down_button != None):
				self._scroll_down_button.add_value_listener(self._scroll_down_value)
		if do_update:
			self.update()
	

	def _scroll_up_value(self, value):
		assert (value in range(128))
		assert (self._scroll_up_button != None)
		if self.is_enabled():
			button_is_momentary = self._scroll_up_button.is_momentary()
			if button_is_momentary:
				if (value != 0):
					self._scroll_up_ticks_delay = INITIAL_SCROLLING_DELAY
				else:
					self._scroll_up_ticks_delay = -1
			if ((not self._is_scrolling()) and ((value is not 0) or (not button_is_momentary))):
				self._offset = max(self._minimum, min(self._maximum, self._offset + (1 + (self._shifted * self._shifted_value))))
				self.update()
				self._report_change(self._offset)
	

	def _scroll_down_value(self, value):
		assert (value in range(128))
		assert (self._scroll_down_button != None)
		if self.is_enabled():
			button_is_momentary = self._scroll_down_button.is_momentary()
			if button_is_momentary:
				if (value != 0):
					self._scroll_down_ticks_delay = INITIAL_SCROLLING_DELAY
				else:
					self._scroll_down_ticks_delay = -1
			if ((not self._is_scrolling()) and ((value is not 0) or (not button_is_momentary))):
				self._offset = max(self._minimum, min(self._maximum, self._offset - (1 + (self._shifted * self._shifted_value))))
				self.update()
				self._report_change(self._offset)
	

	def set_shift_button(self, shift_button):
		if self._shift_button != None:
			if self._shift_button.value_has_listener(self._shift_value):
				self._shift_button.remove_value_listener(self._shift_value)
		self._shift_button = shift_button
		if self._shift_button != None:
			self._shift_button.add_value_listener(self._shift_value)
			self.update()
	

	def _shift_value(self, value):
		if self._shift_is_momentary:
			self._shifted = (value > 0)
			self.update()
		else:
			if value > 0:
				self._shifted = not self._shifted
				self.update()
	

	def _on_timer(self):
		if self.is_enabled():
			scroll_delays = [self._scroll_up_ticks_delay,
							 self._scroll_down_ticks_delay]
			if (scroll_delays.count(-1) < 2):
				offset_increment = 0
				if (self._scroll_down_ticks_delay > -1):
					if self._is_scrolling():
						offset_increment -= 1
						self._scroll_down_ticks_delay = INTERVAL_SCROLLING_DELAY
					self._scroll_down_ticks_delay -= 1
				if (self._scroll_up_ticks_delay > -1):
					if self._is_scrolling():
						offset_increment += 1
						self._scroll_up_ticks_delay = INTERVAL_SCROLLING_DELAY
					self._scroll_up_ticks_delay -= 1
				new_offset = max(self._minimum, min(self._maximum, self._offset + offset_increment))
				if new_offset != self._offset:
					self._offset =	new_offset
					self.update()
					self._report_change(self._offset)
	

	def _is_scrolling(self):
		return (0 in (self._scroll_up_ticks_delay,
					  self._scroll_down_ticks_delay))
	

	def update(self):
		if (self._scroll_down_button != None):
			if (self._offset > self._minimum):
				self._scroll_down_button.turn_on(True)
			else:
				self._scroll_down_button.turn_off(True)
		if (self._scroll_up_button != None):
			if (self._offset < self._maximum):
				self._scroll_up_button.turn_on(True)
			else:
				self._scroll_up_button.turn_off(True)	
		if (self._shift_button != None):
			if (self._shifted):
				self._shift_button.turn_on(True)
			else:
				self._shift_button.turn_off(True)
	

	def deassign_all(self):
		self.set_offset_change_buttons(None, None)
		self.set_shift_button(None)
		self.on_enabled_changed()
	


class GuitarWing(ControlSurface):
	__module__ = __name__
	__doc__ = " GuitarWing controller script "


	def __init__(self, c_instance):
		super(GuitarWing, self).__init__(c_instance)
		self._connected = False
		self._host_name = 'GuitarWing'
		self._color_type = 'OhmRGB'
		self.oscServer = None
		self.log_message("<<<<<<<<<<<<<<<<<= GuitarWing log opened =>>>>>>>>>>>>>>>>>>>>>") 
		self._timer = 0
		self._current_nav_buttons = []
		self.flash_status = 1
		self._clutch_device_selection = False
		self._touched = 0
		with self.component_guard():
			self._setup_monobridge()
			self._setup_controls()
			self._setup_m4l_interface()
			#self._setup_OSC_layer()
			self._setup_device_control()
			self._setup_transport_control()
			#self._setup_selected_session_control()
			#self._setup_mixer_control()
			#self._setup_session_control()
			#self._setup_step_sequencer()
			#self._device.add_device_listener(self._on_new_device_set)
			self._device.set_parameter_controls(tuple([self._fader[0], self._fader[1], self._fader[2], self._accel[2]]))  #, self._fader_button[0], self._fader_button[1], self._fader_button[2], self._padCC[4]]))
			for index in range(4):
				self._pad[index].set_identifier(36+index)
				self._pad[index].set_channel(CHANNEL)
				self._pad[index].set_enabled(False)
			self._transport.set_stop_button(self._button[6])
			self._transport.set_loop_button(self._button[7])
			self._transport.set_seek_backward_button(self._button[8])
			self._transport.set_record_button(self._button[9])
			self._on_select_track_down_value.subject = self._button[0]
			self._on_select_track_up_value.subject = self._button[1]
	

	@subject_slot('value')
	def _on_select_track_up_value(self, value):
		if value:
			pass
	

	@subject_slot('value')
	def _on_select_track_down_value(self, value):
		if value:
			pass
	

	"""def _install_mapping(self, midi_map_handle, control, parameter, feedback_delay, feedback_map):
		assert(self._in_build_midi_map)
		assert(control != None and parameter != None)
		assert(isinstance(parameter, Live.DeviceParameter.DeviceParameter))
		assert(isinstance(control, InputControlElement))
		assert(isinstance(feedback_delay, int))
		assert(isinstance(feedback_map, tuple))
		success = False
		feedback_rule = None
		if control.message_type is MIDI_NOTE_TYPE:
			feedback_rule = Live.MidiMap.CCFeedbackRule()
			feedback_rule.note_no = control.message_identifier()
			feedback_rule.vel_map = feedback_map
		elif control.message_type() is MIDI_CC_TYPE:
			feedback_rule = Live.MidiMap.CCFeedbackRule()
			feedback_rule.cc_no = control.message_identifier()
			feedback_rule.cc_value_map = feedback_map
		elif control.message_type() is MIDI_PB_TYPE:
			feedback_rule = Live.MidiMap.PitchBendFeedbackRule()
			feedback_rule.value_pair_map = feedback_map
		assert(feedback_rule != None)
		feedback_rule.channel = control.message_channel()
		feedback_rule.delay_in_ms = feedback_delay
		if control.message_type() is MIDI_NOTE_TYPE:
			success = Live.MidiMap.map_midi_note_with_feedback_map(midi_map_handle, parameter, control.message_channel(), control.message_identifier(), feedback_rule)
		elif control.message_type() is MIDI_CC_TYPE:
			success = Live.MidiMap.map_midi_cc_with_feedback_map(midi_map_handle, parameter, control.message_channel(), control.message_identifier(), control.message_map_mode(), feedback_rule, not control.needs_takeover(), control.mapping_sensitivity)
		elif control.message_type() is MIDI_PB_TYPE:
			success = Live.MidiMap.map_midi_pitchbend_with_feedback_map(midi_map_handle, parameter, control.message_channel(), feedback_rule, not control.needs_takeover())
		success and Live.MidiMap.send_feedback_for_parameter(midi_map_handle, parameter)
		return success
		"""
	

	def _setup_monobridge(self):
		self._monobridge = MonoBridgeElement(self)
		self._monobridge.name = 'MonoBridge'
	

	def _setup_controls(self):
		is_momentary = True
		self._button = [MonoButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, BUTTONS[index], 'Button_' + str(index), self) for index in range(10)]

		self._fader = [MonoEncoderElement(MIDI_CC_TYPE, CHANNEL, SLIDERS[index], Live.MidiMap.MapMode.absolute, 'Fader_' + str(index), index, self) for index in range(3)]
		#self._fader_button = [MonoButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, index, 'Fader_Button_' + str(index), self) for index in range(3)]
		self._fader_button = [MonoEncoderElement(MIDI_NOTE_TYPE, CHANNEL, SLIDERS[index], Live.MidiMap.MapMode.absolute, 'Fader_Button_' + str(index), index, self) for index in range(3)]

		self._pad =  [MonoButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, PADS[index], 'Pad_' + str(index), self) for index in range(5)]
		self._padCC = [MonoEncoderElement(MIDI_CC_TYPE, CHANNEL, PADS[index], Live.MidiMap.MapMode.absolute, 'PadCC_' + str(index), index, self) for index in range(5)]

		self._accel = [MonoEncoderElement(MIDI_CC_TYPE, CHANNEL, ACCELS[index], Live.MidiMap.MapMode.absolute, 'Accel_' + str(index), index, self) for index in range(3)]
	

	def _setup_mixer_control(self):
		is_momentary = True
		self._num_tracks = (8) #A mixer is one-dimensional; 
		self._mixer = GuitarWingMixerComponent(self, 8, 4, False, False)
		self._mixer.name = 'Mixer'
		self._mixer.set_track_offset(0) #Sets start point for mixer strip (offset from left)
		for index in range(8):
			self._mixer.channel_strip(index)._invert_mute_feedback = True
			self._mixer.channel_strip(index).name = 'Mixer_ChannelStrip_' + str(index)
		for index in range(4):
			self._mixer.return_strip(index).name = 'Mixer_ReturnStrip_' + str(index)
		self._mixer.selected_strip().name = 'Mixer_SelectedStrip'
		self.song().view.selected_track = self._mixer.channel_strip(0)._track 
	

	def _setup_session_control(self):
		self._session = GuitarWingSessionComponent(8, 4, self)
		self._session.name = "Session"
		self._session.set_offsets(0, 0)	 
		self._session.set_stop_clip_value(STOP_CLIP)
		self._scene = [None for index in range(4)]
		for row in range(4):
			self._scene[row] = self._session.scene(row)
			self._scene[row].name = 'Scene_' + str(row)
			for column in range(8):
				clip_slot = self._scene[row].clip_slot(column)
				clip_slot.name = str(column) + '_Clip_Slot_' + str(row)
				clip_slot.set_triggered_to_play_value(CLIP_TRG_PLAY)
				clip_slot.set_triggered_to_record_value(CLIP_TRG_REC)
				clip_slot.set_stopped_value(CLIP_STOP)
				clip_slot.set_started_value(CLIP_STARTED)
				clip_slot.set_recording_value(CLIP_RECORDING)
		self._session.set_mixer(self._mixer)
		self._session.set_track_banking_increment(TRACK_BANKING_INCREMENT)
		self.set_highlighting_session_component(self._session)
		self._session._do_show_highlight()
	

	def _setup_transport_control(self):
		self._transport = TransportComponent()
	

	def _setup_selected_session_control(self):
		self._selected_session = GuitarWingSessionComponent(1, 16, self)
		self._selected_session.name = "SelectedSession"
		self._selected_session.set_offsets(0, 0)	 
		self._selected_session.set_stop_clip_value(STOP_CLIP)
		self._selected_scene = [None for index in range(16)]
		for row in range(16):
			self._selected_scene[row] = self._selected_session.scene(row)
			self._selected_scene[row].name = 'SelectedScene_' + str(row)
			clip_slot = self._selected_scene[row].clip_slot(0)
			clip_slot.name = 'Selected_Clip_Slot_' + str(row)
			clip_slot.set_triggered_to_play_value(CLIP_TRG_PLAY)
			clip_slot.set_triggered_to_record_value(CLIP_TRG_REC)
			clip_slot.set_stopped_value(CLIP_STOP)
			clip_slot.set_started_value(CLIP_STARTED)
			clip_slot.set_recording_value(CLIP_RECORDING)
	

	def _setup_device_control(self):
		self._device = GuitarWingDeviceComponent(self)  #, MOD_BANK_DICT, MOD_TYPES)
		self._device.name = 'Device_Component'

		self.set_device_component(self._device)
		self._device.set_enabled(True)
	

	def _setup_m4l_interface(self):
		self._m4l_interface = M4LInterfaceComponent(controls=self.controls, component_guard=self.component_guard)
		self.get_control_names = self._m4l_interface.get_control_names
		self.get_control = self._m4l_interface.get_control
		self.grab_control = self._m4l_interface.grab_control
		self.release_control = self._m4l_interface.release_control
	

	def _setup_mod(self):
		if isinstance(__builtins__, dict):
			if not 'monomodular' in __builtins__.keys() or not isinstance(__builtins__['monomodular'], ModRouter):
				__builtins__['monomodular'] = ModRouter()
		else:
			if not hasattr(__builtins__, 'monomodular') or not isinstance(__builtins__['monomodular'], ModRouter):
				setattr(__builtins__, 'monomodular', ModRouter())
		self.monomodular = __builtins__['monomodular']
		if not self.monomodular.has_host():
			self.monomodular.set_host(self)
		self.monomodular.name = 'monomodular_switcher'
		self.modhandler = GuitarWingModHandler(script = self)
		self.modhandler.name = 'ModHandler'
		# self.log_message('mod is: ' + str(self.monomodular) + ' ' + str(__builtins__['monomodular']))
	

	def _setup_OSC_layer(self):
		self._OSC_id = 0
		if hasattr(__builtins__, 'control_surfaces') or (isinstance(__builtins__, dict) and 'control_surfaces' in __builtins__.keys()):
			for cs in __builtins__['control_surfaces']:
				if cs is self:
					break
				elif isinstance(cs, GuitarWing):
					self._OSC_id += 1

		self._prefix = '/Live/GuitarWing/'+str(self._OSC_id)
		self._outPrt = OSC_OUTPORT
		if not self.oscServer is None:
			self.oscServer.shutdown()
		self.oscServer = RemixNet.OSCServer('localhost', self._outPrt, 'localhost', 10001)
	

	def _deassign_all(self):
		self.modhandler._fader_color_override = False
		self._send_midi(tuple([240, 0, 1, 97, 12, 50, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 247]))
		self._send_midi(tuple([191, 122, 64]))		#turn local OFF for CapFaders
		#for index in range(8):
		#	self._send_midi(tuple([191, index+10, 125]))
		#self._send_midi(tuple([191, 18, 105]))
		self._current_nav_buttons = []
		with self.component_guard():

			self.release_controlled_track()

			self._step_sequencer.set_loop_selector_matrix(None)
			self._step_sequencer.set_quantization_buttons(None)
			self._step_sequencer.set_follow_button(None)
			self._step_sequencer.set_button_matrix(None)
			self._step_sequencer.set_drum_matrix(None)
			self._step_sequencer.set_drum_bank_up_button(None)
			self._step_sequencer.set_drum_bank_down_button(None)
			self._step_sequencer.set_mute_button(None)
			self._step_sequencer.set_solo_button(None)
			self._step_sequencer.set_playhead(None)

			self._on_note_matrix_pressed.subject = None
			self._note_sequencer.set_loop_selector_matrix(None)
			self._note_sequencer.set_quantization_buttons(None)
			self._note_sequencer.set_follow_button(None)
			self._note_sequencer.set_button_matrix(None)
			self._note_sequencer.set_playhead(None)

			self._drumgroup.set_drum_matrix(None)
			self.modhandler._assign_keys(None)
			self.modhandler._assign_base_grid(None)
			self.modhandler._assign_base_grid_CC(None)
			self.modhandler.set_shift_button(None)
			self.modhandler.set_device_component(None)
			self._transport.set_overdub_button(None)
			self._recorder.set_new_button(None)
			self._recorder.set_record_button(None)
			self._recorder.set_length_button(None)
			self._recorder.set_length_buttons(None)
			self._offset_component.deassign_all()
			self._vertical_offset_component.deassign_all()
			self._scale_offset_component.deassign_all()
			self._device_navigator.deassign_all()
			self._device.deassign_all()
			self._mixer.deassign_all()
			self._selected_session.deassign_all()
			self._session.deassign_all()
			self.set_highlighting_session_component(self._session)
			self._session._do_show_highlight()
			self._user_mode_selector.set_enabled(False)
			self._midi_mode_selector.set_enabled(False)
			self._split_mode_selector.set_enabled(False)
			self._sequencer_mode_selector.set_enabled(False)

			for pad in self._touchpad:
				pad.set_on_off_values(127, 0)
				pad.release_parameter()
				pad.use_default_message()
				pad.reset(True)
				pad.set_enabled(True)
				pad._descriptor = '_'
			for pad in self._pad:
				pad.display_press = False
				pad.set_on_off_values(127, 0)
				pad.release_parameter()
				pad.use_default_message()
				pad.reset(True)
				pad.set_enabled(True)
				pad._descriptor = '_'
				pad.set_force_next_value()
			for pad in self._pad_CC:
				pad.release_parameter()
				pad.use_default_message()
				pad.set_enabled(True)
			for button in self._button[4:8]:
				button.set_on_off_values(127, 0)
				button.release_parameter()
				button.use_default_message()
				button.reset(True)
				button.set_enabled(True)
				button._descriptor = '_'
			for fader in self._fader[0:8]:
				fader.release_parameter()
				fader.use_default_message()
				fader.send_value(0, True)
				fader.set_enabled(True)
			for runner in self._runner:
				runner.release_parameter()
				runner.reset(True)
				#fader.force_next_send()
		#self.request_rebuild_midi_map()
	

	def _notify_descriptors(self):
		if OSC_TRANSMIT:
			for pad in self._pad:
				self.oscServer.sendOSC(self._prefix+'/'+pad.name+'/lcd_name/', str(self.generate_strip_string(pad._descriptor)))
			for touchpad in self._touchpad:
				self.oscServer.sendOSC(self._prefix+'/'+touchpad.name+'/lcd_name/', str(self.generate_strip_string(touchpad._descriptor)))
			for button in self._button:
				self.oscServer.sendOSC(self._prefix+'/'+button.name+'/lcd_name/', str(self.generate_strip_string(button._descriptor)))
	

	def _set_device_attribute(self, device, attribute, value, force = False):
		if not device is None and hasattr(device, 'name'):
			name = device.name.split(' ')
			for index in range(len(name)):
				if len(str(name[index])) and str(name[index][0])=='@':
					vals = name[index][1:].split(':')
					if vals[0] == attribute:
						#vals[1] = value
						name[index] = str('@'+str(attribute)+':'+str(value))
						device.name = ' '.join(name)
	

	def _top_device(self):
		selected_device = self._device._device
		if not selected_device is None and hasattr(selected_device, 'canonical_parent'):
			while not isinstance(selected_device.canonical_parent, Live.Track.Track):
				selected_device = selected_device.canonical_parent
		return selected_device
	

	def _detect_instrument_type(self, track):
		scale = DEFAULT_AUTO_SCALE
		#for device in self._get_devices(track):
		if self._assign_mod():
			scale = 'Mod'
		else:
			for device in track.devices:
				if isinstance(device, Live.Device.Device):
					#self.log_message('device: ' + str(device.class_name))
					if device.class_name == 'DrumGroupDevice':
						scale = 'DrumPad'
						self._step_sequencer.set_drum_group_device(device)
						break
		return scale
	

	def _get_devices(self, track):

		def dig(container_device):
			contained_devices = []
			if container_device.can_have_chains:
				for chain in container_device.chains:
					for chain_device in chain.devices:
						for item in dig(chain_device):
							contained_devices.append(item)
			else:
				contained_devices.append(container_device)
			return contained_devices
		

		devices = []
		for device in track.devices:
			for item in dig(device):
				devices.append(item)
				#self.log_message('appending ' + str(item))
		return devices
	

	@subject_slot('value')
	def _on_duplicate_button_value(self, value):
		#self.log_message('duplicate button value: ' + str(value))
		track = self._mixer.selected_strip()._track
		#track_index = [t for t in self._mixer.tracks_to_use()].index(self._mixer.selected_strip()._track)
		#self._session.selected_scene.clip_slot(track_index)._do_duplicate_clipslot()
		if not value is 0 and not track is None:
			try:
				track.duplicate_clip_slot([s for s in self.song().scenes].index(self.song().view.selected_scene))
				#self._session.selected_scene.clip_slot(track_index)._do_duplicate_clipslot()
			except:
				self.log_message('couldnt duplicate')
				self.log_message('because: ' + str([s for s in self.song().scenes].index(self.song().view.selected_scene)))
	

	@subject_slot('value')
	def _on_new_button_value(self, value):
		#self.log_message('new button value: ' +str(value))
		song = self.song()
		view = song.view
		try:
			selected_track = view.selected_track
			selected_scene_index = list(song.scenes).index(view.selected_scene)
			selected_track.stop_all_clips(False)
			self._jump_to_next_slot(selected_track, selected_scene_index)
		except:
			self.log_message('couldnt create new')
			#self._view_selected_clip_detail()
	

	def _jump_to_next_slot(self, track, start_index):
		song = self.song()
		new_scene_index = self._next_empty_slot(track, start_index)
		song.view.selected_scene = song.scenes[new_scene_index]
	

	def _next_empty_slot(self, track, scene_index):
		song = self.song()
		scene_count = len(song.scenes)
		while track.clip_slots[scene_index].has_clip:
			scene_index += 1
			if scene_index == scene_count:
				song.create_scene(scene_count)
		return scene_index
	

	"""called on timer"""
	def update_display(self):
		super(GuitarWing, self).update_display()
		self._timer = (self._timer + 1) % 256
		self.flash()
	

	def flash(self):
		if(self.flash_status > 0):
			for control in self.controls:
				if isinstance(control, MonoButtonElement):
					control.flash(self._timer)
	

	"""m4l bridge"""
	def _on_device_name_changed(self):
		name = self._device.device_name_data_source().display_string()
		self._monobridge._send('Device_Name', 'lcd_name', str(self.generate_strip_string('Device')))
		self._monobridge._send('Device_Name', 'lcd_value', str(self.generate_strip_string(name)))
		self.touched()
		if OSC_TRANSMIT:
			self.oscServer.sendOSC(self._prefix+'/glob/device/', str(self.generate_strip_string(name)))
	

	def _on_device_bank_changed(self):
		name = 'No Bank'
		if is_device(self._device._device):
			name, _ = self._device._current_bank_details()
		self._monobridge._send('Device_Bank', 'lcd_name', str(self.generate_strip_string('Bank')))
		self._monobridge._send('Device_Bank', 'lcd_value', str(self.generate_strip_string(name)))
		self.touched()
	

	def _on_device_chain_changed(self):
		name = " "
		if is_device(self._device._device) and self._device._device.canonical_parent and isinstance(self._device._device.canonical_parent, Live.Chain.Chain):
			name = self._device._device.canonical_parent.name
		self._monobridge._send('Device_Chain', 'lcd_name', str(self.generate_strip_string('Chain')))
		self._monobridge._send('Device_Chain', 'lcd_value', str(self.generate_strip_string(name)))
		self.touched()
	

	def generate_strip_string(self, display_string):
		NUM_CHARS_PER_DISPLAY_STRIP = 12
		if (not display_string):
			return (' ' * NUM_CHARS_PER_DISPLAY_STRIP)
		else:
			display_string = str(display_string)
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
	

	def notification_to_bridge(self, name, value, sender):
		#self.log_message('monobridge:' + str(name) + str(value))
		if isinstance(sender, MonoEncoderElement):
			if OSC_TRANSMIT:
				self.oscServer.sendOSC(self._prefix+'/'+sender.name+'/lcd_name/', str(self.generate_strip_string(name)))
				self.oscServer.sendOSC(self._prefix+'/'+sender.name+'/lcd_value/', str(self.generate_strip_string(value)))
			self._monobridge._send(sender.name, 'lcd_name', str(self.generate_strip_string(name)))
			self._monobridge._send(sender.name, 'lcd_value', str(self.generate_strip_string(value)))
		else:
			self._monobridge._send(name, 'lcd_name', str(self.generate_strip_string(name)))
			self._monobridge._send(name, 'lcd_value', str(self.generate_strip_string(value)))
			if OSC_TRANSMIT:
				self.oscServer.sendOSC(self._prefix+'/'+name+'/lcd_name/', str(self.generate_strip_string(name)))
				self.oscServer.sendOSC(self._prefix+'/'+name+'/lcd_value/', str(self.generate_strip_string(value)))
	

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
		
	

	"""general functionality"""
	def disconnect(self):
		if not self.oscServer is None:
			self.oscServer.shutdown()
		self.oscServer = None
		self.log_message("--------------= GuitarWing log closed =--------------")
		super(GuitarWing, self).disconnect()
	

	"""some cheap overrides"""

	def set_highlighting_session_component(self, session_component):
		self._highlighting_session_component = session_component
		self._highlighting_session_component.set_highlighting_callback(self._set_session_highlight)
	

	def handle_sysex(self, midi_bytes):
		#self.log_message('sysex: ' + str(midi_bytes))
		if len(midi_bytes) > 14:
			if midi_bytes[:6] == tuple([240, 0, 1, 97, 12, 64]):
				self._register_pad_pressed(midi_bytes[6:14])
			elif midi_bytes[3:10] == tuple([6, 2, 0, 1, 97, 1, 0]):
				if not self._connected:
					self._connected = True
					self._initialize_hardware()
	




#	a