# by amounra 0413 : http://www.aumhaa.com

import Live
import time
import math
#import sys

from _Framework.ControlSurface import ControlSurface # Central base class for scripts based on the new Framework
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent # Base class for all classes encapsulating functions in Live
from _Framework.SceneComponent import SceneComponent # Class representing a scene in Live
from _Framework.SessionComponent import SessionComponent # Class encompassing several scene to cover a defined section of Live's session
from _Framework.MixerComponent import MixerComponent # Class encompassing several channel strips to form a mixer
from _Framework.ClipSlotComponent import ClipSlotComponent # Class representing a ClipSlot within Live
from _Framework.ChannelStripComponent import ChannelStripComponent # Class attaching to the mixer of a given track
from _Framework.ButtonMatrixElement import ButtonMatrixElement # Class representing a 2-dimensional set of buttons




class MonoChopperComponent(ControlSurfaceComponent):
	__module__ = __name__
	__doc__ = " Class that holds chopper variables and methods"


	def __init__(self, cs, mixer, *a, **k):
		super(MonoChopperComponent, self).__init__(*a, **k)
		self._cs = cs
		self._mixer = mixer
		self._clip_focus = None
		self._matrix = None
		self._track = self.song().view.selected_track
		#self._change = time.time()
		self._change = time.clock()
		self._interval = .01
		self.song().add_tempo_listener(self._on_tempo_change)
		self._tempo = self._cs.song().tempo
		self._on_tempo_change()
		self.on_selected_track_changed()
	

	def _on_tempo_change(self):
		self._tempo = self._cs.song().tempo
		self._div =  60/self._tempo  #this number should be 60, but we've lowered it to accomodate the inacuracy of the Python engine, which seems to change depending on the song tempo. Why does this work?  Beats me.....
		#self._cs.log_message('tempo ' + str(self._tempo))
		
	

	def _set_button_matrix(self, buttons):
		#self._cs.log_message('set_matrix ' + str(buttons))
		assert isinstance(buttons, (ButtonMatrixElement, type(None)))
		if buttons != self._matrix:
			if self._matrix != None:
				self._matrix.remove_value_listener(self._matrix_value)
			self._matrix = buttons
			if self._matrix != None:
				self._matrix.add_value_listener(self._matrix_value)
			self._cs.request_rebuild_midi_map()
	

	def _matrix_value(self, value, x, y, is_momentary):
		if self.is_enabled():
			assert (self._matrix != None)
			assert (value in range(128))
			assert (x in range(self._matrix.width()))
			assert (y in range(self._matrix.height()))
			assert isinstance(is_momentary, type(False))
			if ((value != 0) or (not is_momentary)) and (self._clip_focus != None):
				report = self._clip_focus.playing_position 										#current playing position 
				#add = ((time.time() - self._change)/self._div)
				add = ((time.clock() - self._change)/self._div)
				pos = report + add
				new_pos = ((self._clip_focus.loop_end - self._clip_focus.loop_start)/16)*x
				change = new_pos - pos
				#self._cs.log_message('interval ' + str(self._interval) + ' div ' + str(self._div) + ' time ' + str(time.clock()) + ' add ' + str(add) + ' report ' + str(report) + ' pos ' + str(pos) + ' newpos ' + str(new_pos) + ' change ' + str(change))
				self._clip_focus.move_playing_pos(change)
				#self._change[2] = self._change[3]
				#self._change[3] = new_pos + add
				#add = ((time.time() - self._change[0])/self._change[1])*self._change[2]			#interpolation of the time that has passed since the last playing position report

	

	def _clip_playing_position(self):
		if self._clip_focus != None:
			pos = self._clip_focus.playing_position
			start = self._clip_focus.loop_start
			end = self._clip_focus.loop_end
			length = (end - start)
			#self._change = time.time()		#[time.time(), time.time() - self._change[0], pos - self._change[3], pos]
			self._interval = time.clock() - self._change
			self._change = time.clock()
			#self._cs.log_message('start ' + str(start) + ' end ' + str(end) + ' length ' + str(length))
			#self._cs.log_message('time ' + str(self._change) + ' pos: ' + str(pos) + ' ' + str(start) +' ' + str(end) + ' ' + str(length))
			#self._cs.log_message('interval: ' + str(self._interval))
			if self.is_enabled():
				for index in range(16):
					val = int(pos > (length/16)*index)
					#self.log_message('val ' + str(val))
					self._matrix.send_value(index, 0, val, True)
	

	def on_selected_track_changed(self):
		if self._track != None:
			if self._track.can_be_armed:
				if self._track.playing_slot_index_has_listener(self._capture_current_clip):
					self._track.remove_playing_slot_index_listener(self._capture_current_clip)
		self._track = self.song().view.selected_track
		if self._track != None:
			if self._track.can_be_armed:
				self._track.add_playing_slot_index_listener(self._capture_current_clip)
		self._capture_current_clip()
	

	def _capture_current_clip(self):
		if self._clip_focus != None:
			if self._clip_focus.playing_position_has_listener(self._clip_playing_position):
				self._clip_focus.remove_playing_position_listener(self._clip_playing_position)
		self._clip_focus = None
		if self._track != None:
			if self._track.can_be_armed:
				slot = self._track.playing_slot_index
				if slot > -1:
					self._clip_focus = self._track.clip_slots[slot].clip
					self._clip_focus.add_playing_position_listener(self._clip_playing_position)
		if self._clip_focus == None and self.is_enabled():
			if self._matrix != None:
				for index in range(16):
					self._matrix.send_value(index, 0, 0, True)
		

	def update(self):
		pass
	

	def disconnect(self):
		if self._matrix != None:
			self._matrix.remove_value_listener(self._matrix_value)
		if self._track != None:
			if self._track.can_be_armed:
				if self._track.playing_slot_index_has_listener(self._capture_current_clip):
					self._track.remove_playing_slot_index_listener(self._capture_current_clip)
		if self._clip_focus != None:
			if self._clip_focus.playing_position_has_listener(self._clip_playing_position):
				self._clip_focus.remove_playing_position_listener(self._clip_playing_position)
	
	

	def on_enabled_changed(self):
		self._capture_current_clip()
	
