# by amounra 0216 : http://www.aumhaa.com
from __future__ import absolute_import
import Live
from itertools import izip, izip_longest, product
from ableton.v2.base import listens, listens_group, Subject, SlotManager, liveobj_valid, nop, clamp
import ableton.v2.base.task as Task
from ableton.v2.control_surface.components import ChannelStripComponent as ChannelStripComponentBase, DeviceComponent, MixerComponent as MixerComponentBase
from ableton.v2.control_surface import ParameterSlot, CompoundComponent
#from _Framework.TrackArmState import TrackArmState

from _Generic.Devices import *

from aumhaa.v2.base.debug import *

debug = initialize_debug()

EQ_DEVICES = {'Eq8': {'Gains': [ '%i Gain A' % (index + 1) for index in range(8) ]},
 'FilterEQ3': {'Gains': ['GainHi', 'GainMid', 'GainLo'],
			   'Cuts': ['LowOn', 'MidOn', 'HighOn']}}

TRACK_FOLD_DELAY = 0.5


def release_control(control):
	if control != None:
		control.release_parameter()


class TrackArmState(Subject, SlotManager):
	__events__ = ('arm',)


	def __init__(self, track = None, *a, **k):
		super(TrackArmState, self).__init__(*a, **k)
		self.set_track(track)
	

	def set_track(self, track):
		self._track = track
		self._arm = track and track.can_be_armed and (track.arm or track.implicit_arm)
		subject = track if track and track.can_be_armed else None
		self._on_explicit_arm_changed.subject = subject
		self._on_implicit_arm_changed.subject = subject
	

	@listens('arm')
	def _on_explicit_arm_changed(self):
		self._on_arm_changed()
	

	@listens('implicit_arm')
	def _on_implicit_arm_changed(self):
		self._on_arm_changed()
	

	def _on_arm_changed(self):
		if not self._track.arm:
			new_state = self._track.implicit_arm
			self._arm = self._arm != new_state and new_state
			self.notify_arm()
	

	def _get_arm(self):
		return self._arm if self._track.can_be_armed else False
	

	def _set_arm(self, new_state):
		if self._track.can_be_armed:
			self._track.arm = new_state
			if not new_state:
				self._track.implicit_arm = False
		self._arm = new_state
	

	arm = property(_get_arm, _set_arm)


def turn_button_on_off(button, on = True):
	if button != None:
		if on:
			button.turn_on()
		else:
			button.turn_off()



class MonoChannelStripComponent(ChannelStripComponentBase):


	_mute_on_color = 'DefaultButton.On'
	_mute_off_color = 'DefaultButton.Off'
	_solo_on_color = 'DefaultButton.On'
	_solo_off_color = 'DefaultButton.Off'
	_arm_on_color = 'DefaultButton.On'
	_arm_off_color = 'DefaultButton.Off'
	_selected_on_color = 'DefaultButton.On'
	_selected_off_color = 'DefaultButton.Off'

	def __init__(self, *a, **k):
		super(MonoChannelStripComponent, self).__init__(*a, **k)
		self._ChannelStripComponent__on_selected_track_changed.subject = None
		self._ChannelStripComponent__on_selected_track_changed = self.__on_selected_track_changed
		self.__on_selected_track_changed.subject = self.song.view
		self.__on_selected_track_changed()
	

	@listens('selected_track')
	def __on_selected_track_changed(self):
		if liveobj_valid(self._track) or self.empty_color == None:
			if self.song.view.selected_track == self._track:
				self.select_button.color = self._selected_on_color
			else:
				self.select_button.color = self._selected_off_color
		else:
			self.select_button.color = self.empty_color
	

	def _on_mute_changed(self):
		if self.is_enabled() and self._mute_button != None:
			if liveobj_valid(self._track) or self.empty_color == None:
				if self._track in chain(self.song.tracks, self.song.return_tracks) and self._track.mute != self._invert_mute_feedback:
					self._mute_button.set_light(self._mute_on_color)
				else:
					self._mute_button.set_light(self._mute_off_color)
			else:
				self._mute_button.set_light(self.empty_color)
	

	def _on_solo_changed(self):
		if self.is_enabled() and self._solo_button != None:
			if liveobj_valid(self._track) or self.empty_color == None:
				if self._track in chain(self.song.tracks, self.song.return_tracks) and self._track.solo:
					self._solo_button.set_light(self._solo_on_color)
				else:
					self._solo_button.set_light(self._solo_off_color)
			else:
				self._solo_button.set_light(self.empty_color)
	

	def _on_arm_changed(self):
		if self.is_enabled() and self._arm_button != None:
			if liveobj_valid(self._track) or self.empty_color == None:
				if self._track in self.song.tracks and self._track.can_be_armed and self._track.arm:
					self._arm_button.set_light(self._arm_on_color)
				else:
					self._arm_button.set_light(self._arm_off_color)
			else:
				self._arm_button.set_light(self.empty_color)
	

	def set_stop_button(self, button):
		#debug('setting stop button:', button)
		self._on_stop_value.subject = button
		button and button.set_light('Mixer.StopClip')
	

	@listens('value')
	def _on_stop_value(self, value):
		if self._track:
			self._track.stop_all_clips()
	



class MonoMixerComponent(MixerComponentBase):


	def __init__(self, num_returns = 4, enable_skinning = False, *a, **k):
		self._return_strips = []
		self._return_controls = None
		super(MonoMixerComponent, self).__init__(*a, **k)
		for index in range(num_returns):
			self._return_strips.append(self._create_strip())
			self.register_components(self._return_strips[index])
		enable_skinning and self._assign_skin_colors()
		self._reassign_tracks()
	

	def _create_strip(self):
		return MonoChannelStripComponent()
	

	def _assign_skin_colors(self):
		for strip in self._channel_strips + self._return_strips + [self._master_strip, self._selected_strip]:
			strip._mute_on_color = 'Mixer.MuteOn'
			strip._mute_off_color = 'Mixer.MuteOff'
			strip._solo_on_color = 'Mixer.SoloOn'
			strip._solo_off_color = 'Mixer.SoloOff'
			strip._arm_on_color = 'Mixer.ArmUnselected'
			strip._arm_off_color = 'Mixer.ArmOff'
			strip._selected_on_color = 'Mixer.SelectedOn'
			strip._selected_off_color = 'Mixer.SelectedOff'
	

	def return_strip(self, index):
		assert(index in range(len(self._return_strips)))
		return self._return_strips[index]
	

	def _reassign_tracks(self):
		super(MonoMixerComponent, self)._reassign_tracks()
		for track, channel_strip in izip(self.song.return_tracks, self._return_strips):
			channel_strip.set_track(track)
	

	def set_send_controls(self, controls):
		self._send_controls and self._send_controls.reset()
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
		self._return_controls = controls
		for channel_strip, control in izip_longest(self._return_strips, controls or []):
			if channel_strip:
				channel_strip.set_volume_control(control)
				channel_strip.update()
	

	def set_stop_clip_buttons(self, buttons):
		for strip, button in map(None, self._channel_strips, buttons or []):
			strip.set_stop_button(button)
	



class OldMixerComponentBase(CompoundComponent):
	""" Class encompassing several channel strips to form a mixer """


	def __init__(self, num_tracks = 0, num_returns = 0, invert_mute_feedback = False, auto_name = False, *a, **k):
		assert(num_tracks >= 0)
		assert(num_returns >= 0)
		super(MixerComponentBase, self).__init__(*a, **k)
		self._track_offset = -1
		self._send_index = 0
		self._bank_up_button = None
		self._bank_down_button = None
		self._next_track_button = None
		self._prev_track_button = None
		self._prehear_volume_control = None
		self._crossfader_control = None
		self._send_controls = None
		self._channel_strips = []
		self._return_strips = []
		self._offset_can_start_after_tracks = False
		for index in range(num_tracks):
			strip = self._create_strip()
			self._channel_strips.append(strip)
			self.register_components(self._channel_strips[index])
			if invert_mute_feedback:
				strip.set_invert_mute_feedback(True)

		for index in range(num_returns):
			self._return_strips.append(self._create_strip())
			self.register_components(self._return_strips[index])

		self._master_strip = self._create_strip()
		self.register_components(self._master_strip)
		self._master_strip.set_track(self.song.master_track)
		self._selected_strip = self._create_strip()
		self.register_components(self._selected_strip)
		self.on_selected_track_changed()
		self.set_track_offset(0)
		auto_name and self._auto_name()
		self._on_return_tracks_changed.subject = self.song
		self._on_return_tracks_changed()


		def make_button_slot(name):
			return self.register_slot(None, getattr(self, '_%s_value' % name), 'value')
		
		self._bank_up_button_slot = make_button_slot('bank_up')
		self._bank_down_button_slot = make_button_slot('bank_down')
		self._next_track_button_slot = make_button_slot('next_track')
		self._prev_track_button_slot = make_button_slot('prev_track')
	

	def disconnect(self):
		super(MixerComponentBase, self).disconnect()
		release_control(self._prehear_volume_control)
		release_control(self._crossfader_control)
		self._bank_up_button = None
		self._bank_down_button = None
		self._next_track_button = None
		self._prev_track_button = None
		self._prehear_volume_control = None
		self._crossfader_control = None
	

	def _get_send_index(self):
		return self._send_index
	

	def _set_send_index(self, index):
		if 0 <= index < self.num_sends or index is None:
			if self._send_index != index:
				self._send_index = index
				self.set_send_controls(self._send_controls)
				self.on_send_index_changed()
		else:
			raise IndexError

	send_index = property(_get_send_index, _set_send_index)
	

	def on_send_index_changed(self):
		pass
	

	@property
	def num_sends(self):
		return len(self.song.return_tracks)
	

	def channel_strip(self, index):
		assert(index in range(len(self._channel_strips)))
		return self._channel_strips[index]
	

	def return_strip(self, index):
		assert(index in range(len(self._return_strips)))
		return self._return_strips[index]
	

	def master_strip(self):
		return self._master_strip
	

	def selected_strip(self):
		return self._selected_strip
	

	def set_prehear_volume_control(self, control):
		release_control(self._prehear_volume_control)
		self._prehear_volume_control = control
		self.update()
	

	def set_crossfader_control(self, control):
		release_control(self._crossfader_control)
		self._crossfader_control = control
		self.update()
	

	def set_volume_controls(self, controls):
		for strip, control in map(None, self._channel_strips, controls or []):
			strip.set_volume_control(control)
	

	def set_pan_controls(self, controls):
		for strip, control in map(None, self._channel_strips, controls or []):
			strip.set_pan_control(control)
	

	def set_send_controls(self, controls):
		self._send_controls = controls
		for strip, control in map(None, self._channel_strips, controls or []):
			if self._send_index is None:
				strip.set_send_controls(None)
			else:
				strip.set_send_controls((None,) * self._send_index + (control,))
	

	def set_arm_buttons(self, buttons):
		for strip, button in map(None, self._channel_strips, buttons or []):
			strip.set_arm_button(button)
	

	def set_solo_buttons(self, buttons):
		for strip, button in map(None, self._channel_strips, buttons or []):
			strip.set_solo_button(button)
	

	def set_mute_buttons(self, buttons):
		for strip, button in map(None, self._channel_strips, buttons or []):
			strip.set_mute_button(button)
	

	def set_track_select_buttons(self, buttons):
		for strip, button in map(None, self._channel_strips, buttons or []):
			strip.set_select_button(button)
	

	def set_shift_button(self, button):
		for strip in self._channel_strips or []:
			strip.set_shift_button(button)
	

	def set_bank_buttons(self, up_button, down_button):
		do_update = False
		if up_button is not self._bank_up_button:
			do_update = True
			self._bank_up_button = up_button
			self._bank_up_button_slot.subject = up_button
		if down_button is not self._bank_down_button:
			do_update = True
			self._bank_down_button = down_button
			self._bank_down_button_slot.subject = down_button
		if do_update:
			self.on_track_list_changed()
	

	def set_select_buttons(self, next_button, prev_button):
		do_update = False
		if next_button is not self._next_track_button:
			do_update = True
			self._next_track_button = next_button
			self._next_track_button_slot.subject = next_button
		if prev_button is not self._prev_track_button:
			do_update = True
			self._prev_track_button = prev_button
			self._prev_track_button_slot.subject = prev_button
		if do_update:
			self.on_selected_track_changed()
	

	def set_track_offset(self, new_offset):
		assert(isinstance(new_offset, int))
		assert(new_offset >= 0)
		if new_offset != self._track_offset:
			self._offset_can_start_after_tracks |= new_offset > (len(self.tracks_to_use()) - 1)
		self._track_offset = new_offset
		self._reassign_tracks()
	

	def on_enabled_changed(self):
		self.update()
	

	def on_track_list_changed(self):
		if not self._offset_can_start_after_tracks:
			self._track_offset = min(self._track_offset, len(self.tracks_to_use()) - 1)
		self._reassign_tracks()
	

	def on_selected_track_changed(self):
		selected_track = self.song.view.selected_track
		if self._selected_strip != None:
			self._selected_strip.set_track(selected_track)
		if self.is_enabled():
			turn_button_on_off(self._next_track_button, on=selected_track != self.song.master_track)
			turn_button_on_off(self._prev_track_button, on=selected_track != self.song.visible_tracks[0])
	

	@listens('return_tracks')
	def _on_return_tracks_changed(self):
		num_sends = self.num_sends
		if self._send_index is not None:
			self.send_index = clamp(self._send_index, 0, num_sends - 1) if num_sends > 0 else None
		else:
			self.send_index = 0 if num_sends > 0 else None
		self.on_num_sends_changed()
	

	def on_num_sends_changed(self):
		pass
	

	def tracks_to_use(self):
		return self.song.visible_tracks
	

	def update(self):
		super(MixerComponentBase, self).update()
		if self._allow_updates:
			master_track = self.song.master_track
			if self.is_enabled():
				if self._prehear_volume_control != None:
					self._prehear_volume_control.connect_to(master_track.mixer_device.cue_volume)
				if self._crossfader_control != None:
					self._crossfader_control.connect_to(master_track.mixer_device.crossfader)
			else:
				release_control(self._prehear_volume_control)
				release_control(self._crossfader_control)
				map(lambda x: turn_button_on_off(x, on=False), [self._bank_up_button,
				 self._bank_down_button,
				 self._next_track_button,
				 self._prev_track_button])
		else:
			self._update_requests += 1
	

	def _reassign_tracks(self):
		tracks = self.tracks_to_use()
		returns = self.song.return_tracks
		num_strips = len(self._channel_strips)
		for index in range(num_strips):
			track_index = self._track_offset + index
			track = tracks[track_index] if len(tracks) > track_index else None
			self._channel_strips[index].set_track(track)

		for index in range(len(self._return_strips)):
			if len(returns) > index:
				self._return_strips[index].set_track(returns[index])
			else:
				self._return_strips[index].set_track(None)

		turn_button_on_off(self._bank_down_button, on=self._track_offset > 0)
		turn_button_on_off(self._bank_up_button, on=len(tracks) > self._track_offset + num_strips)
	

	def _create_strip(self):
		return ChannelStripComponent()
	

	def _bank_up_value(self, value):
		assert(isinstance(value, int))
	 	assert(self._bank_up_button != None)
		if self.is_enabled():
			new_offset = (value is not 0 or not self._bank_up_button.is_momentary()) and self._track_offset + len(self._channel_strips)
			len(self.tracks_to_use()) > new_offset and self.set_track_offset(new_offset)
	

	def _bank_down_value(self, value):
		assert(isinstance(value, int))
		assert(self._bank_down_button != None)
		self.is_enabled() and (value is not 0 or not self._bank_down_button.is_momentary()) and self.set_track_offset(max(0, self._track_offset - len(self._channel_strips)))
	

	def _next_track_value(self, value):
		assert(self._next_track_button != None)
		assert(value != None)
		assert(isinstance(value, int))
		selected_track = self.is_enabled() and (value is not 0 or not self._next_track_button.is_momentary()) and self.song.view.selected_track
		all_tracks = tuple(self.song.visible_tracks) + tuple(self.song.return_tracks) + (self.song.master_track,)
		assert(selected_track in all_tracks)
		if selected_track != all_tracks[-1]:
			index = list(all_tracks).index(selected_track)
			self.song.view.selected_track = all_tracks[index + 1]
	

	def _prev_track_value(self, value):
		assert(self._prev_track_button != None)
		assert(value != None)
		assert(isinstance(value, int))
		selected_track = self.is_enabled() and (value is not 0 or not self._prev_track_button.is_momentary()) and self.song.view.selected_track
		all_tracks = tuple(self.song.visible_tracks) + tuple(self.song.return_tracks) + (self.song.master_track,)
		assert(selected_track in all_tracks)
		if selected_track != all_tracks[0]:
			index = list(all_tracks).index(selected_track)
			self.song.view.selected_track = all_tracks[index - 1]
	

	def _auto_name(self):
		self.name = 'Mixer'
		self.master_strip().name = 'Master_Channel_Strip'
		self.selected_strip().name = 'Selected_Channel_Strip'
		for index, strip in enumerate(self._channel_strips):
			strip.name = 'Channel_Strip_%d' % index
	


class MixerComponent(OldMixerComponentBase):


	def __init__(self, *a, **k):
		super(MixerComponent,self).__init__( *a, **k)
	

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
			selected_track = self.song.view.selected_track
			all_tracks = tuple(self.song.visible_tracks) + tuple(self.song.return_tracks) + (self.song.master_track,)
			assert(selected_track in all_tracks)
			if selected_track != all_tracks[-1]:
				index = list(all_tracks).index(selected_track)
				self.song.view.selected_track = all_tracks[index + 1]
	

	def select_prev_track(self):
		if self.is_enabled():
			selected_track = self.song.view.selected_track
			all_tracks = tuple(self.song.visible_tracks) + tuple(self.song.return_tracks) + (self.song.master_track,)
			assert(selected_track in all_tracks)
			if selected_track != all_tracks[0]:
				index = list(all_tracks).index(selected_track)
				self.song.view.selected_track = all_tracks[index - 1]
	

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
		return tuple(self.song.visible_tracks) + tuple(self.song.return_tracks)
	

	@listens('value')
	def _on_track_select_dial_value(self, value):
		debug('_on_track_select_dial_value', value)
		if value > 64:
			self.select_prev_track()
		else:
			self.select_next_track()
	



class ChannelStripComponent(ChannelStripComponentBase):


	def __init__(self, *a, **k):
		super(ChannelStripComponent, self).__init__(*a, **k)
		
		self._device_component = None
		#self._device_component = DeviceComponent(*a, **k)
		#self._device_component._show_msg_callback = lambda message: None
		self._ChannelStripComponent__on_selected_track_changed.subject = None
		self._on_selected_track_changed.subject = self.song.view
		self._fold_task = self._tasks.add(Task.sequence(Task.wait(TRACK_FOLD_DELAY), Task.run(self._do_fold_track))).kill()
		#self._cue_volume_slot = self.register_disconnectable(ParameterSlot())
		self._track_state = self.register_disconnectable(TrackArmState())
		self._on_arm_state_changed.subject = self._track_state
		self._eq_gain_controls = None
		self._eq_device = None
		self._record_button_value = 0
		self._arming_select_button = None
		
	

	@listens('selected_track')
	def _ChannelStripComponent__on_selected_track_changed(self):
		debug('_ChannelStripComponent__on_selected_track_changed')
		if liveobj_valid(self._track) or self.empty_color == None:
			if self.song.view.selected_track == self._track:
				self.select_button.color = 'Mixer.SelectedOn'
			else:
				self.select_button.color = 'Mixer.SelectedOff'
		else:
			self.select_button.color = self.empty_color
		self._update_device_selection()
	

	def set_track(self, track):
		assert(isinstance(track, (type(None), Live.Track.Track)))
		self._on_devices_changed.subject = track
		self._update_device_selection()
		self._detect_eq(track)
		super(ChannelStripComponent,self).set_track(track)
	

	#def on_selected_track_changed(self):
	#	if self.is_enabled():
	#		if self._select_button != None:
	#			if self._track != None or self.empty_color == None:
	#				if self.song.view.selected_track == self._track:
	#					self._select_button.set_light('Mixer.SelectedOn')
	#				else:
	#					self._select_button.set_light('Mixer.SelectedOff')
	#			else:
	#				self._select_button.set_light(self.empty_color)
	#		self._update_track_button()
	#	self._update_device_selection()
	
	@listens('selected_track')
	def _on_selected_track_changed(self):
		if liveobj_valid(self._track) or self.empty_color == None:
			if self.song.view.selected_track == self._track:
				self.select_button.color = 'Mixer.SelectedOn'
			else:
				self.select_button.color = 'Mixer.SelectedOff'
		else:
			self.select_button.color = self.empty_color
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
	

	@listens('arm')
	def _on_arm_state_changed(self):
		if self.is_enabled() and self._track:
			self._update_track_button()
	

	@listens('value')
	def _on_stop_value(self, value):
		if self._track:
			self._track.stop_all_clips()
	

	@listens('value')
	def _arming_select_value(self, value):
		if value and self.song.view.selected_track == self._track:
			self._do_toggle_arm(exclusive=self.song.exclusive_arm)
		else:
			if self.song.view.selected_track != self._track:
				self.song.view.selected_track = self._track
		if value and self._track.is_foldable and self._select_button.is_momentary():
			self._fold_task.restart()
		else:
			self._fold_task.kill()
	

	#@listens('selected_track')
	#def _on_selected_track_changed(self):
	#	self.on_selected_track_changed()
	

	@listens('devices')
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
				if self._track in chain(self.song.tracks, self.song.return_tracks) and self._track.mute != self._invert_mute_feedback:
					self._mute_button.set_light('Mixer.MuteOn')
				else:
					self._mute_button.set_light('Mixer.MuteOff')
			else:
				self._mute_button.set_light(self.empty_color)
	

	def _on_solo_changed(self):
		if self.is_enabled() and self._solo_button != None:
			if self._track != None or self.empty_color == None:
				if self._track in chain(self.song.tracks, self.song.return_tracks) and self._track.solo:
					self._solo_button.set_light('Mixer.SoloOn')
				else:
					self._solo_button.set_light('Mixer.SoloOff')
			else:
				self._solo_button.set_light(self.empty_color)
	

	def _on_arm_changed(self):
		if self.is_enabled() and self._arm_button != None:
			if self._track != None or self.empty_color == None:
				if self._track in self.song.tracks and self._track.can_be_armed and self._track.arm:
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
					if self._track == self.song.view.selected_track:
						if self._track.arm:
							self._arming_select_button.set_light('Mixer.ArmSelected')
						else:
							self._arming_select_button.set_light('Mixer.ArmSelectedImplicit')
					else:
						self._arming_select_button.set_light('Mixer.ArmUnselected')
				elif self._track == self.song.view.selected_track:
					self._arming_select_button.turn_on()
				else:
					self._arming_select_button.turn_off()
	

	def _do_toggle_arm(self, exclusive = False):
		if self._track.can_be_armed:
			self._track.arm = not self._track.arm
			if exclusive and (self._track.implicit_arm or self._track.arm):
				for track in self.song.tracks:
					if track.can_be_armed and track != self._track:
						track.arm = False
	

	def _do_fold_track(self):
		if self.is_enabled() and self._track != None and self._track.is_foldable:
			self._track.fold_state = not self._track.fold_state
	

	def _do_select_track(self, track):
		pass
	



