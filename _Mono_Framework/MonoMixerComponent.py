# by amounra 0814 : http://www.aumhaa.com

import Live

from _Framework.SubjectSlot import subject_slot, subject_slot_group
from _Framework.MixerComponent import MixerComponent as MixerComponentBase
from _Framework.ChannelStripComponent import ChannelStripComponent as ChannelStripComponentBase
from _Framework.InputControlElement import ParameterSlot
from _Framework.TrackArmState import TrackArmState
from _Framework.DeviceComponent import DeviceComponent
from _Framework.Util import nop
from _Generic.Devices import *

from Debug import *

debug = initialize_debug()

EQ_DEVICES = {'Eq8': {'Gains': [ '%i Gain A' % (index + 1) for index in range(8) ]},
 'FilterEQ3': {'Gains': ['GainHi', 'GainMid', 'GainLo'],
			   'Cuts': ['LowOn', 'MidOn', 'HighOn']}}

TRACK_FOLD_DELAY = 0.5


def release_control(control):
	if control != None:
		control.release_parameter()



class MixerComponent(MixerComponentBase):


	def __init__(self, num_tracks, num_returns, invert_mute_feedback, auto_name):
		super(MixerComponent,self).__init__(num_tracks, num_returns, invert_mute_feedback, auto_name)
	

	def _create_strip(self):
		return ChannelStripComponent()
	

	def set_next_track_button(self, next_button):
		if next_button is not self._next_track_button:
			self._next_track_button = next_button
			self._next_track_button_slot.subject = next_button
			self.on_selected_track_changed()
	

	def set_previous_track_button(self, prev_button):
		if prev_button is not self._prev_track_button:
			self._prev_track_button = prev_button
			self._prev_track_button_slot.subject = prev_button
			self.on_selected_track_changed()
	

	def set_track_select_dial(self, dial):
		self._on_track_select_dial_value.subject = dial
	

	def select_next_track(self):
		if self.is_enabled():
			selected_track = self.song().view.selected_track
			all_tracks = tuple(self.song().visible_tracks) + tuple(self.song().return_tracks) + (self.song().master_track,)
			assert(selected_track in all_tracks)
			if selected_track != all_tracks[-1]:
				index = list(all_tracks).index(selected_track)
				self.song().view.selected_track = all_tracks[index + 1]
	

	def select_prev_track(self):
		if self.is_enabled():
			selected_track = self.song().view.selected_track
			all_tracks = tuple(self.song().visible_tracks) + tuple(self.song().return_tracks) + (self.song().master_track,)
			assert(selected_track in all_tracks)
			if selected_track != all_tracks[0]:
				index = list(all_tracks).index(selected_track)
				self.song().view.selected_track = all_tracks[index - 1]
	

	def set_send_controls(self, controls):
		self._send_controls = controls
		for index, channel_strip in enumerate(self._channel_strips):
			if self.send_index is None:
				channel_strip.set_send_controls([None])
			else:
				send_controls = [ controls.get_button(index, i) for i in xrange(2) ] if controls else [None]
				skipped_sends = [ None for _ in xrange(self.send_index) ]
				channel_strip.set_send_controls(skipped_sends + send_controls)
	

	def set_send_controls(self, controls):
		self._send_controls = controls
		if controls:
			for index in range(len(self._channel_strips)):
				send_controls = [controls.get_button(index, row) for row in range(controls.height())]
				if self.send_index > controls.height:
					send_controls = send_controls + [None for _ in range(self.send_index - controls.height)]
				self._channel_strips[index].set_send_controls(send_controls)
		else:
			for strip in self._channel_strips:
				if self.send_index is None:
					strip.set_send_controls([None])
				else:
					strip.set_send_controls([None for _ in range(self.send_index)])
	

	def set_return_controls(self, controls):
		for strip, control in map(None, self._return_strips, controls or []):
			#debug('strip and control:', strip, control)
			strip.set_volume_control(control)
	

	def set_stop_clip_buttons(self, buttons):
		for strip, button in map(None, self._channel_strips, buttons or []):
			strip.set_stop_button(button)
			#debug('set stop button:', button)
	

	def set_arming_track_select_buttons(self, buttons):
		for strip, button in map(None, self._channel_strips, buttons or []):
			strip.set_arming_select_button(button)
	

	def set_eq_gain_controls(self, controls):
		self._eq_controls = controls
		if controls:
			for index in range(len(self._channel_strips)):
				eq_controls = [controls.get_button(index, row) for row in range(controls.height())]
				self._channel_strips[index].set_eq_gain_controls(eq_controls)
		else:
			for strip in self._channel_strips:
				strip.set_eq_gain_controls(None)
	

	def set_parameter_controls(self, controls):
		self._parameter_controls = controls
		if controls:
			for index in range(len(self._channel_strips)):
				parameter_controls = [controls.get_button(index, row) for row in range(controls.height())]
				self._channel_strips[index].set_parameter_controls(parameter_controls)
		else:
			for strip in self._channel_strips:
				strip.set_parameter_controls(None)
	

	def tracks_to_use(self):
		return tuple(self.song().visible_tracks) + tuple(self.song().return_tracks)
	

	@subject_slot('value')
	def _on_track_select_dial_value(self, value):
		debug('_on_track_select_dial_value', value)
		if value > 64:
			self.select_prev_track()
		else:
			self.select_next_track()
	



class ChannelStripComponent(ChannelStripComponentBase):


	def __init__(self, *a, **k):
		super(ChannelStripComponent, self).__init__(*a, **k)
		self._device_component = DeviceComponent()
		self._device_component._show_msg_callback = lambda message: None
		self._on_selected_track_changed.subject = self.song().view
		self._fold_task = self._tasks.add(Task.sequence(Task.wait(TRACK_FOLD_DELAY), Task.run(self._do_fold_track))).kill()
		#self._cue_volume_slot = self.register_disconnectable(ParameterSlot())
		self._track_state = self.register_disconnectable(TrackArmState())
		self._on_arm_state_changed.subject = self._track_state
		self._eq_gain_controls = None
		self._eq_device = None
		self._record_button_value = 0
		self._arming_select_button = None
	

	def set_track(self, track):
		assert(isinstance(track, (type(None), Live.Track.Track)))
		self._on_devices_changed.subject = track
		self._update_device_selection()
		self._detect_eq(track)
		super(ChannelStripComponent,self).set_track(track)
	

	def on_selected_track_changed(self):
		if self.is_enabled():
			if self._select_button != None:
				if self._track != None or self.empty_color == None:
					if self.song().view.selected_track == self._track:
						self._select_button.set_light('Mixer.SelectedOn')
					else:
						self._select_button.set_light('Mixer.SelectedOff')
				else:
					self._select_button.set_light(self.empty_color)
			self._update_track_button()
		self._update_device_selection()
	

	def update(self, *a, **k):
		super(ChannelStripComponent, self).update()
		self._update_device_selection()
	

	def set_invert_mute_feedback(self, invert_feedback):
		assert(isinstance(invert_feedback, type(False)))
		self._invert_mute_feedback = invert_feedback
		self.update()
	

	def set_eq_gain_controls(self, controls):
		for control in list(self._eq_gain_controls or []):
			release_control(control)
		self._eq_gain_controls = controls
		self.update()
	

	def set_parameter_controls(self, controls):
		self._device_component and self._device_component.set_parameter_controls(controls)
	

	def set_device_component(self, device_component):
		self._device_component = device_component
		self._update_device_selection
	

	def set_arming_select_button(self, button):
		self._arming_select_button = button
		self._arming_select_value.subject = button
		button and button.set_on_off_values('DefaultButton.On', 'DefaultButton.Off')
		self._update_track_button()
	

	def set_stop_button(self, button):
		#debug('setting stop button:', button)
		self._on_stop_value.subject = button
		button and button.set_light('Mixer.StopClip')
	

	@subject_slot('arm')
	def _on_arm_state_changed(self):
		if self.is_enabled() and self._track:
			self._update_track_button()
	

	@subject_slot('value')
	def _on_stop_value(self, value):
		if self._track:
			self._track.stop_all_clips()
	

	@subject_slot('value')
	def _arming_select_value(self, value):
		if value and self.song().view.selected_track == self._track:
			self._do_toggle_arm(exclusive=self.song().exclusive_arm)
		else:
			if self.song().view.selected_track != self._track:
				self.song().view.selected_track = self._track
		if value and self._track.is_foldable and self._select_button.is_momentary():
			self._fold_task.restart()
		else:
			self._fold_task.kill()
	

	@subject_slot('selected_track')
	def _on_selected_track_changed(self):
		self.on_selected_track_changed()
	

	@subject_slot('devices')
	def _on_devices_changed(self):
		debug(self.name, 'on devices changed')
		self._update_device_selection()
		self._detect_eq(self._track)
		self.update()
	

	def _update_device_selection(self):
		track = self._track
		device_to_select = None
		if track and device_to_select == None and len(track.devices) > 0:
			device_to_select = track.devices[0]
		self._device_component and self._device_component.set_device(device_to_select)
	

	def _detect_eq(self, track = None):
		self._eq_device = None
		if not track is None:
			for index in range(len(track.devices)):
				device = track.devices[-1 * (index + 1)]
				if device.class_name in EQ_DEVICES.keys():
					self._eq_device = device
					break
	

	def _on_mute_changed(self):
		if self.is_enabled() and self._mute_button != None:
			if self._track != None or self.empty_color == None:
				if self._track in chain(self.song().tracks, self.song().return_tracks) and self._track.mute != self._invert_mute_feedback:
					self._mute_button.set_light('Mixer.MuteOn')
				else:
					self._mute_button.set_light('Mixer.MuteOff')
			else:
				self._mute_button.set_light(self.empty_color)
	

	def _on_solo_changed(self):
		if self.is_enabled() and self._solo_button != None:
			if self._track != None or self.empty_color == None:
				if self._track in chain(self.song().tracks, self.song().return_tracks) and self._track.solo:
					self._solo_button.set_light('Mixer.SoloOn')
				else:
					self._solo_button.set_light('Mixer.SoloOff')
			else:
				self._solo_button.set_light(self.empty_color)
	

	def _on_arm_changed(self):
		if self.is_enabled() and self._arm_button != None:
			if self._track != None or self.empty_color == None:
				if self._track in self.song().tracks and self._track.can_be_armed and self._track.arm:
					self._arm_button.set_light('Mixer.ArmUnselected')
				else:
					self._arm_button.set_light('Mixer.ArmOff')
			else:
				self._arm_button.set_light(self.empty_color)
		self._update_track_button()
	

	def _all_controls(self):
		return [self._pan_control, self._volume_control] + list(self._send_controls or []) + list(self._eq_gain_controls or [])
	

	def _connect_parameters(self):
		#super(ChannelStripComponent, self)._connect_parameters()
		if self._pan_control != None:
			self._pan_control.connect_to(self._track.mixer_device.panning)
		if self._volume_control != None:
			self._volume_control.connect_to(self._track.mixer_device.volume)
		if self._send_controls != None:
			index = 0
			for send_control in self._send_controls:
				if send_control != None:
					if index < len(self._track.mixer_device.sends):
						send_control.connect_to(self._track.mixer_device.sends[index])
					else:
						send_control.release_parameter()
						send_control.send_value(0, True)
						self._empty_control_slots.register_slot(send_control, nop, 'value')
				index += 1
		if not self._eq_device is None:
			device_dict = EQ_DEVICES[self._eq_device.class_name]
			if self._eq_gain_controls != None:
				gain_names = device_dict['Gains']
				index = 0
				for eq_gain_control in self._eq_gain_controls:
					if eq_gain_control != None:
						if len(gain_names) > index:
							parameter = get_parameter_by_name(self._eq_device, gain_names[index])
							if parameter != None:
								eq_gain_control.connect_to(parameter)
							else:
								eq_gain_control.release_parameter()
								self._empty_control_slots.register_slot(eq_gain_control, nop, 'value')
						else:
							eq_gain_control.release_parameter()
							self._empty_control_slots.register_slot(eq_gain_control, nop, 'value')
					index += 1
	

	def _disconnect_parameters(self):
		for control in self._all_controls():
			control and control.send_value(0, True)
		super(ChannelStripComponent, self)._disconnect_parameters()
	

	def _update_track_button(self):
		if self.is_enabled():
			if self._arming_select_button != None:
				if self._track == None:
					self._arming_select_button.set_light(self.empty_color)
				elif self._track.can_be_armed and (self._track.arm or self._track.implicit_arm):
					if self._track == self.song().view.selected_track:
						if self._track.arm:
							self._arming_select_button.set_light('Mixer.ArmSelected')
						else:
							self._arming_select_button.set_light('Mixer.ArmSelectedImplicit')
					else:
						self._arming_select_button.set_light('Mixer.ArmUnselected')
				elif self._track == self.song().view.selected_track:
					self._arming_select_button.turn_on()
				else:
					self._arming_select_button.turn_off()
	

	def _do_toggle_arm(self, exclusive = False):
		if self._track.can_be_armed:
			self._track.arm = not self._track.arm
			if exclusive and (self._track.implicit_arm or self._track.arm):
				for track in self.song().tracks:
					if track.can_be_armed and track != self._track:
						track.arm = False
	

	def _do_fold_track(self):
		if self.is_enabled() and self._track != None and self._track.is_foldable:
			self._track.fold_state = not self._track.fold_state
	

	def _do_select_track(self, track):
		pass
	

