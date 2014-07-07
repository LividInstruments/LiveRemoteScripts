import Live
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement
TEMPO_TOP = 200.0
TEMPO_BOTTOM = 60.0
TEMPO_FINE_RANGE = 2.5600000000000001
class TransportComponent(ControlSurfaceComponent):
	__doc__ = " Class encapsulating all functions in Live's transport section  "

	def __init__(self):
		ControlSurfaceComponent.__init__(self)
		self._stop_button = None
		self._play_button = None
		self._ffwd_button = None
		self._rwd_button = None
		self._loop_button = None
		self._punch_in_button = None
		self._punch_out_button = None
		self._record_button = None
		self._tap_tempo_button = None
		self._nudge_up_button = None
		self._nudge_down_button = None
		self._metronome_button = None
		self._overdub_button = None
		self._tempo_control = None
		self._tempo_fine_control = None
		self._song_position_control = None
		self._rwd_button_pressed = False
		self._ffwd_button_pressed = False
		self._fine_tempo_needs_pickup = True
		self._prior_fine_tempo_value = -1
		self.song().add_loop_listener(self._on_loop_status_changed)
		self.song().add_punch_in_listener(self._on_punch_in_status_changed)
		self.song().add_punch_out_listener(self._on_punch_out_status_changed)
		self.song().add_record_mode_listener(self._on_record_status_changed)
		self.song().add_is_playing_listener(self._on_playing_status_changed)
		self.song().add_nudge_down_listener(self._on_nudge_down_changed)
		self.song().add_nudge_up_listener(self._on_nudge_up_changed)
		self.song().add_metronome_listener(self._on_metronome_changed)
		self.song().add_overdub_listener(self._on_overdub_changed)
		return None

	def disconnect(self):
		self.song().remove_loop_listener(self._on_loop_status_changed)
		self.song().remove_punch_in_listener(self._on_punch_in_status_changed)
		self.song().remove_punch_out_listener(self._on_punch_out_status_changed)
		self.song().remove_record_mode_listener(self._on_record_status_changed)
		self.song().remove_is_playing_listener(self._on_playing_status_changed)
		self.song().remove_nudge_down_listener(self._on_nudge_down_changed)
		self.song().remove_nudge_up_listener(self._on_nudge_up_changed)
		self.song().remove_metronome_listener(self._on_metronome_changed)
		self.song().remove_overdub_listener(self._on_overdub_changed)
		if self._stop_button != None:
			self._stop_button.remove_value_listener(self._stop_value)
			self._stop_button = None
		if self._play_button != None:
			self._play_button.remove_value_listener(self._play_value)
			self._play_button = None
		if self._ffwd_button != None:
			self._ffwd_button.remove_value_listener(self._ffwd_value)
			self._ffwd_button = None
		if self._rwd_button != None:
			self._rwd_button.remove_value_listener(self._rwd_value)
			self._rwd_button = None
		if self._loop_button != None:
			self._loop_button.remove_value_listener(self._loop_value)
			self._loop_button = None
		if self._punch_in_button != None:
			self._punch_in_button.remove_value_listener(self._punch_in_value)
			self._punch_in_button = None
		if self._punch_out_button != None:
			self._punch_out_button.remove_value_listener(self._punch_out_value)
			self._punch_out_button = None
		if self._record_button != None:
			self._record_button.remove_value_listener(self._record_value)
			self._record_button = None
		if self._tap_tempo_button != None:
			self._tap_tempo_button.remove_value_listener(self._tap_tempo_value)
			self._tap_tempo_button = None
		if self._nudge_down_button != None:
			self._nudge_down_button.remove_value_listener(self._nudge_down_value)
			self._nudge_down_button = None
		if self._nudge_up_button != None:
			self._nudge_up_button.remove_value_listener(self._nudge_up_value)
			self._nudge_up_button = None
		if self._metronome_button != None:
			self._metronome_button.remove_value_listener(self._metronome_value)
			self._metronome_button = None
		if self._overdub_button != None:
			self._overdub_button.remove_value_listener(self._overdub_value)
			self._overdub_button = None
		if self._tempo_control != None:
			self._tempo_control.remove_value_listener(self._tempo_value)
			self._tempo_control = None
		if self._tempo_fine_control != None:
			self._tempo_fine_control.remove_value_listener(self._tempo_fine_value)
			self._tempo_fine_control = None
		if self._song_position_control != None:
			self._song_position_control.release_parameter()
			self._song_position_control = None
		return None

	def on_enabled_changed(self):
		if (not self.is_enabled()):
			if (self._ffwd_button_pressed or self._rwd_button_pressed):
				self._unregister_timer_callback(self._on_timer)
				self._ffwd_button_pressed = False
				self._rwd_button_pressed = False
		self.update()

	def set_stop_button(self, button):
		assert ((button == None) or isinstance(button, ButtonElement))
		if (self._stop_button != button):
			if (self._stop_button != None):
				self._stop_button.remove_value_listener(self._stop_value)
			self._stop_button = button
			if (self._stop_button != None):
				self._stop_button.add_value_listener(self._stop_value)
			self.update()

	def set_play_button(self, button):
		assert ((button == None) or isinstance(button, ButtonElement))
		if (self._play_button != button):
			if (self._play_button != None):
				self._play_button.remove_value_listener(self._play_value)
			self._play_button = button
			if (self._play_button != None):
				self._play_button.add_value_listener(self._play_value)
			self.update()

	def set_seek_buttons(self, ffwd_button, rwd_button):
		assert ((ffwd_button == None) or isinstance(ffwd_button, ButtonElement))
		assert ((rwd_button == None) or isinstance(rwd_button, ButtonElement))
		do_update = (self._ffwd_button != ffwd_button) or (self._rwd_button != rwd_button)
		remove_timer = self._ffwd_button_pressed or self._rwd_button_pressed
		if self._ffwd_button != ffwd_button:
			if self._ffwd_button != None:
				self._ffwd_button.remove_value_listener(self._ffwd_value)
			self._ffwd_button_pressed = False
			self._ffwd_button = ffwd_button
			if self._ffwd_button != None:
				self._ffwd_button.add_value_listener(self._ffwd_value)
		if self._rwd_button != rwd_button:
			if self._rwd_button != None:
				self._rwd_button.remove_value_listener(self._rwd_value)
			self._rwd_button_pressed = False
			self._rwd_button = rwd_button
			if self._rwd_button != None:
				self._rwd_button.add_value_listener(self._rwd_value)
		if do_update:
			if remove_timer:
				self._unregister_timer_callback(self._on_timer)
			self.update()
		return None

	def set_nudge_buttons(self, up_button, down_button):
		assert ((up_button == None) or (isinstance(up_button, ButtonElement) and up_button.is_momentary()))
		assert ((down_button == None) or (isinstance(down_button, ButtonElement) and down_button.is_momentary()))
		if self._nudge_up_button != None:
			self._nudge_up_button.remove_value_listener(self._nudge_up_value)
		self._nudge_up_button = up_button
		if self._nudge_up_button != None:
			self._nudge_up_button.add_value_listener(self._nudge_up_value)
		if self._nudge_down_button != None:
			self._nudge_down_button.remove_value_listener(self._nudge_down_value)
		self._nudge_down_button = down_button
		if self._nudge_down_button != None:
			self._nudge_down_button.add_value_listener(self._nudge_down_value)
		self.update()
		return None

	def set_record_button(self, button):
		assert ((button == None) or isinstance(button, ButtonElement))
		if self._record_button != button:
			if self._record_button != None:
				self._record_button.remove_value_listener(self._record_value)
			self._record_button = button
			if self._record_button != None:
				self._record_button.add_value_listener(self._record_value)
			self.update()
		return None

	def set_tap_tempo_button(self, button):
		assert ((button == None) or isinstance(button, ButtonElement))
		if self._tap_tempo_button != button:
			if self._tap_tempo_button != None:
				self._tap_tempo_button.remove_value_listener(self._tap_tempo_value)
			self._tap_tempo_button = button
			if self._tap_tempo_button != None:
				self._tap_tempo_button.add_value_listener(self._tap_tempo_value)
			self.update()
		return None

	def set_loop_button(self, button):
		assert ((button == None) or isinstance(button, ButtonElement))
		if self._loop_button != button:
			if self._loop_button != None:
				self._loop_button.remove_value_listener(self._loop_value)
			self._loop_button = button
			if self._loop_button != None:
				self._loop_button.add_value_listener(self._loop_value)
			self.update()
		return None

	def set_punch_buttons(self, in_button, out_button):
		assert ((in_button == None) or isinstance(in_button, ButtonElement))
		assert ((out_button == None) or isinstance(out_button, ButtonElement))
		if self._punch_in_button != None:
			self._punch_in_button.remove_value_listener(self._punch_in_value)
		self._punch_in_button = in_button
		if self._punch_in_button != None:
			self._punch_in_button.add_value_listener(self._punch_in_value)
		if self._punch_out_button != None:
			self._punch_out_button.remove_value_listener(self._punch_out_value)
		self._punch_out_button = out_button
		if self._punch_out_button != None:
			self._punch_out_button.add_value_listener(self._punch_out_value)
		self.update()
		return None

	def set_metronome_button(self, button):
		assert ((button == None) or isinstance(button, ButtonElement))
		if self._metronome_button != button:
			if self._metronome_button != None:
				self._metronome_button.remove_value_listener(self._metronome_value)
			self._metronome_button = button
			if self._metronome_button != None:
				self._metronome_button.add_value_listener(self._metronome_value)
			self._on_metronome_changed()
			self.update()
		return None

	def set_overdub_button(self, button):
		assert ((button == None) or isinstance(button, ButtonElement))
		if self._overdub_button != button:
			if self._overdub_button != None:
				self._overdub_button.remove_value_listener(self._overdub_value)
			self._overdub_button = button
			if self._overdub_button != None:
				self._overdub_button.add_value_listener(self._overdub_value)
			self._on_overdub_changed()
			self.update()
		return None

	def set_tempo_control(self, control, fine_control = None):
		assert ((control == None) or (isinstance(control, EncoderElement) and (control.message_map_mode() is Live.MidiMap.MapMode.absolute)))
		assert ((fine_control == None) or (isinstance(fine_control, EncoderElement) and (fine_control.message_map_mode() is Live.MidiMap.MapMode.absolute)))
		if (self._tempo_control != None):
			self._tempo_control.remove_value_listener(self._tempo_value)
		self._tempo_control = control
		if (self._tempo_control != None):
			self._tempo_control.add_value_listener(self._tempo_value)
		if (self._tempo_fine_control != None):
			self._tempo_fine_control.remove_value_listener(self._tempo_fine_value)
		self._tempo_fine_control = fine_control
		self._fine_tempo_needs_pickup = True
		self._prior_fine_tempo_value = -1
		if (self._tempo_fine_control != None):
			self._tempo_fine_control.add_value_listener(self._tempo_fine_value)
		self.update()
		

	def set_song_position_control(self, control):
		assert ((control == None) or isinstance(control, EncoderElement))
		if self._song_position_control != control:
			if (self._song_position_control != None):
				self._song_position_control.remove_value_listener(self._song_position_value)
			self._song_position_control = control
			if (self._song_position_control != None):
				self._song_position_control.add_value_listener(self._song_position_value)
			self.update()
		

	def update(self):
		if self.is_enabled():
			#self._rebuild_callback()
			self._on_playing_status_changed()
			self._on_record_status_changed()
			self._on_loop_status_changed()
			self._on_overdub_changed()
			self._on_metronome_changed()
			self._on_punch_in_status_changed()
			self._on_punch_out_status_changed()
			self._on_nudge_down_changed()
			self._on_nudge_up_changed()


	def _on_playing_status_changed(self):
		if self.is_enabled():
			if (self._stop_button != None):
				self._stop_button.turn_off()
			if (self._play_button != None):
				if self.song().is_playing:
					self._play_button.turn_on()
				else:
					self._play_button.turn_off()
		

	def _on_record_status_changed(self):
		if self.is_enabled():
			if (self._record_button != None):
				if self.song().record_mode:
					self._record_button.turn_on()
				else:
					self._record_button.turn_off()
					

	def _on_loop_status_changed(self):
		if self.is_enabled():
			if (self._loop_button != None):
				if self.song().loop:
					self._loop_button.turn_on()
				else:
					self._loop_button.turn_off()
					

	def _on_punch_in_status_changed(self):
		if self.is_enabled():
			if (self._punch_in_button != None):
				if self.song().punch_in:
					self._punch_in_button.turn_on()
				else:
					self._punch_in_button.turn_off()
					

	def _on_punch_out_status_changed(self):
		if self.is_enabled():
			if (self._punch_out_button != None):
				if self.song().punch_out:
					self._punch_out_button.turn_on()
				else:
					self._punch_out_button.turn_off()
					

	def _on_nudge_down_changed(self):
		if self.is_enabled():
			if (self._nudge_down_button != None):
				if self.song().nudge_down:
					self._nudge_down_button.turn_on()
				else:
					self._nudge_down_button.turn_off()
					

	def _on_nudge_up_changed(self):
		if self.is_enabled():
			if (self._nudge_up_button != None):
				if self.song().nudge_up:
					self._nudge_up_button.turn_on()
				else:
					self._nudge_up_button.turn_off()		

					
	def _on_metronome_changed(self):
		if self.is_enabled() and self._metronome_button != None:
			if self.song().metronome:
				self._metronome_button.turn_on()
			else:
				self._metronome_button.turn_off()


	def _on_overdub_changed(self):
		if (self.is_enabled() and (self._overdub_button != None)):
			if self.song().overdub:
				self._overdub_button.turn_on()
			else:
				self._overdub_button.turn_off()

				
	def _stop_value(self, value):
		assert (self._stop_button != None)
		assert isinstance(value, int)
		if self.is_enabled():
			if ((value != 0) or (not self._stop_button.is_momentary())):
				self.song().is_playing = False


	def _play_value(self, value):
		assert (self._play_button != None)
		assert isinstance(value, int)
		if self.is_enabled():
			if ((value != 0) or (not self._play_button.is_momentary())):
				self.song().is_playing = True


	def _ffwd_value(self, value):
		assert (self._ffwd_button != None)
		assert isinstance(value, int)
		if self.is_enabled():
			self.song().current_song_time += 1
			if self._ffwd_button.is_momentary():
				if (self._ffwd_button_pressed is not (value != 0)):
					self._ffwd_button_pressed = (value != 0)
					if (not self._rwd_button_pressed):
						if self._ffwd_button_pressed:
							self._register_timer_callback(self._on_timer)
						else:
							self._unregister_timer_callback(self._on_timer)
		

	def _rwd_value(self, value):
		assert (self._rwd_button != None)
		assert isinstance(value, int)
		if self.is_enabled():
			self.song().current_song_time = max(0, (self.song().current_song_time - 1))
			if self._rwd_button.is_momentary():
				if (self._rwd_button_pressed is not (value != 0)):
					self._rwd_button_pressed = (value != 0)
					if (not self._ffwd_button_pressed):
						if self._rwd_button_pressed:
							self._register_timer_callback(self._on_timer)
						else:
							self._unregister_timer_callback(self._on_timer)
		
		
	def _nudge_down_value(self, value):
		assert (self._nudge_down_button != None)
		assert (value in range(128))
		if self.is_enabled():
			self.song().nudge_down = (value != 0)


	def _nudge_up_value(self, value):
		assert (self._nudge_up_button != None)
		assert (value in range(128))
		if self.is_enabled():
			self.song().nudge_up = (value != 0)
			

	def _loop_value(self, value):
		assert (self._loop_button != None)
		assert isinstance(value, int)
		if self.is_enabled():
			if ((value != 0) or (not self._loop_button.is_momentary())):
				self.song().loop = (not self.song().loop)


	def _punch_in_value(self, value):
		assert (self._punch_in_button != None)
		assert isinstance(value, int)
		if self.is_enabled():
			if ((value != 0) or (not self._punch_in_button.is_momentary())):
				self.song().punch_in = (not self.song().punch_in)


	def _punch_out_value(self, value):
		assert (self._punch_out_button != None)
		assert isinstance(value, int)
		if self.is_enabled():
			if ((value != 0) or (not self._punch_out_button.is_momentary())):
				self.song().punch_out = (not self.song().punch_out)


	def _record_value(self, value):
		assert (self._record_button != None)
		assert isinstance(value, int)
		if self.is_enabled():
			if ((value != 0) or (not self._record_button.is_momentary())):
				self.song().record_mode = (not self.song().record_mode)


	def _tap_tempo_value(self, value):
		assert (self._tap_tempo_button != None)
		assert isinstance(value, int)
		if self.is_enabled():
			if ((value != 0) or (not self._tap_tempo_button.is_momentary())):
				self.song().tap_tempo()
				

	def _tempo_value(self, value):
		assert (self._tempo_control != None)
		assert (value in range(128))
		if self.is_enabled():
			fraction = ((TEMPO_TOP - TEMPO_BOTTOM) / 127.0)
			self.song().tempo = ((fraction * value) + TEMPO_BOTTOM)


	def _tempo_fine_value(self, value):
		assert (self._tempo_fine_control != None)
		assert (value in range(128))
		if self.is_enabled():
			if self._fine_tempo_needs_pickup:
				if (self._prior_fine_tempo_value in range(128)):
					range_max = max(value, self._prior_fine_tempo_value)
					range_min = min(value, self._prior_fine_tempo_value)
					if (64 in range(range_min, (range_max + 1))):
						self._fine_tempo_needs_pickup = False
			else:
				assert (self._prior_fine_tempo_value in range(128))
				difference = (value - self._prior_fine_tempo_value)
				new_tempo = min(TEMPO_TOP, max(TEMPO_BOTTOM, (self.song().tempo + (difference / (127.0 / TEMPO_FINE_RANGE)))))
				self.song().tempo = new_tempo
		self._prior_fine_tempo_value = value
		
		
	def _song_position_value(self, value):
		assert (self._song_position_control != None)
		assert isinstance(value, int)
		debug_print('Code Missing')
		assert False
		

	def _metronome_value(self, value):
		assert (self._metronome_button != None)
		assert (value in range(128))
		if self.is_enabled():
			if ((value != 0) or (not self._metronome_button.is_momentary())):
				self.song().metronome = (not self.song().metronome)


	def _overdub_value(self, value):
		assert (self._overdub_button != None)
		assert (value in range(128))
		if self.is_enabled():
			if ((value != 0) or (not self._overdub_button.is_momentary())):
				self.song().overdub = (not self.song().overdub)


	def _on_timer(self):
		if ((not self._ffwd_button_pressed) or (not self._rwd_button_pressed)):
			if self._ffwd_button_pressed:
				self.song().current_song_time += 1
			elif self._rwd_button_pressed:
				self.song().current_song_time = max(0, (self.song().current_song_time - 1))




