# by amounra 0513 : http://www.aumhaa.com

from __future__ import with_statement
import Live
import math

from Map import *

from Livid_Base.Base import *

class Base_LE(Base):


	def __init__(self, *a, **k):
		super(Base_LE, self).__init__(*a, **k)
	

	def _set_layer0(self, shifted = False):
		with self.component_guard():
			self._display_mode()
			self._send_midi(LIVEBUTTONMODE)
			self._mixer.master_strip().set_volume_control(self._fader[8])
			self._send_midi(tuple([240, 0, 1, 97, 12, 61, 7, 7, 7, 7, 7, 7, 7, 7, 2, 247]))
			for index in range(8):
				#self._send_midi((191, index+1, LAYERSPLASH[0]))
				self._touchpad[index].set_on_off_values(CHAN_SELECT, 0)
				self._mixer.channel_strip(index).set_select_button(self._touchpad[index])
				self._mixer.channel_strip(index).set_volume_control(self._fader[index])
			self._session.set_scene_bank_buttons(self._button[7], self._button[4])
			self._session.set_track_bank_buttons(self._button[5], self._button[6])
			self._current_nav_buttons = self._button[4:8]
			for index in range(4):
				self._button[index+4].set_on_off_values(SESSION_NAV[shifted], 0)
			self._session.update()
			if not shifted:
				for column in range(7): 
					for row in range(4):
						self._scene[row].clip_slot(column).set_launch_button(self._pad[column + (row*8)])
				for row in range(4):
					self._scene[row].set_launch_button(self._pad[7 + (row*8)])
			else:
				self._send_midi(tuple([240, 0, 1, 97, 12, 61, 7, 7, 7, 7, 7, 7, 7, 7, 2, 247]))
				self._session._shifted = True
				for index in range(8):
					#self._send_midi((191, index+1, LAYERSPLASH[0]))
					self._pad[index].set_on_off_values(TRACK_MUTE, 0)
					self._mixer.channel_strip(index).set_mute_button(self._pad[index])
					self._pad[index+8].set_on_off_values(TRACK_SOLO, 0)
					self._mixer.channel_strip(index).set_solo_button(self._pad[index+8])
					self._pad[index+16].set_on_off_values(TRACK_ARM, 0)
					self._mixer.channel_strip(index).set_arm_button(self._pad[index+16])
					self._pad[index+24].set_on_off_values(TRACK_STOP, TRACK_STOP)
					self._pad[index+24].send_value(TRACK_STOP)
				self._session.set_stop_track_clip_buttons(tuple(self._pad[24:32]))
			self._mixer.update()
		self.request_rebuild_midi_map()
	

	def _set_layer1(self, shifted = False):
		with self.component_guard():
			self._display_mode()
			for index in range(4):
				self._mixer.return_strip(index).set_volume_control(self._fader[index+4])
			self._mixer._selected_strip.set_send_controls(tuple(self._fader[0:4]))
			self._mixer.master_strip().set_volume_control(self._fader[8])
			if not shifted:
				self._send_midi(tuple([240, 0, 1, 97, 12, 61, 5, 5, 5, 5, 4, 4, 4, 4, 2, 247]))
				for index in range(8):
					#self._send_midi((191, index+1, LAYERSPLASH[1]))
					self._touchpad[index].set_on_off_values(CHAN_SELECT, 0)
					self._mixer.channel_strip(index).set_select_button(self._touchpad[index])
				if self._mixer.shifted() or not self._assign_midi_layer():
					self._send_midi(LIVEBUTTONMODE)
					for column in range(7): 
						for row in range(4):
							self._scene[row].clip_slot(column).set_launch_button(self._pad[column + (row*8)])
					for row in range(4):
						self._scene[row].set_launch_button(self._pad[7 + (row*8)])
					self._session.set_scene_bank_buttons(self._button[7], self._button[4])
					self._session.set_track_bank_buttons(self._button[5], self._button[6])
					self._current_nav_buttons = self._button[4:8]
					self._session.set_show_highlight(True)
					for index in range(4):
						self._button[index+4].set_on_off_values(SESSION_NAV[shifted], 0)
					self._session.update()
			else:
				if not self._assign_midi_shift_layer():
					for index in range(8):
						self._touchpad[index].set_on_off_values(CHAN_SELECT, 0)
						self._mixer.channel_strip(index).set_select_button(self._touchpad[index])
					self._send_midi(LIVEBUTTONMODE)
					self._session._shifted = True
					self._session.set_scene_bank_buttons(self._button[7], self._button[4])
					self._session.set_track_bank_buttons(self._button[5], self._button[6])
					self._current_nav_buttons = self._button[4:8]
					#self._session.set_show_highlight(True)
					for index in range(4):
						self._button[index+4].set_on_off_values(SESSION_NAV[shifted], 0)
					self._session.update()
				self._send_midi(tuple([240, 0, 1, 97, 12, 61, 7, 7, 7, 7, 7, 7, 7, 7, 2, 247]))
				for index in range(8):
					#self._send_midi((191, index+1, LAYERSPLASH[0]))
					self._mixer.channel_strip(index).set_volume_control(self._fader[index])
					self._pad[index].set_on_off_values(TRACK_MUTE, 0)
					self._mixer.channel_strip(index).set_mute_button(self._pad[index])
					self._pad[index+8].set_on_off_values(TRACK_SOLO, 0)
					self._mixer.channel_strip(index).set_solo_button(self._pad[index+8])
					self._pad[index+16].set_on_off_values(TRACK_ARM, 0)
					self._mixer.channel_strip(index).set_arm_button(self._pad[index+16])
					self._pad[index+24].set_on_off_values(TRACK_STOP, TRACK_STOP)
					self._pad[index+24].send_value(TRACK_STOP)
				self._session.set_stop_track_clip_buttons(tuple(self._pad[24:32]))
			self._mixer.update()
		self.request_rebuild_midi_map()
	

	def _set_layer2(self, shifted = False):
		with self.component_guard():
			self._display_mode()
			self._device.set_parameter_controls(tuple(self._fader[0:8]))
			self._device.set_enabled(True)
			self._mixer.master_strip().set_volume_control(self._fader[8])
			if not shifted:
				self._send_midi(tuple([240, 0, 1, 97, 12, 61, 6, 6, 6, 6, 6, 6, 6, 6, 2, 247]))
				for index in range(8):
					#self._send_midi((191, index+1, LAYERSPLASH[2]))
					self._touchpad[index].set_on_off_values(CHAN_SELECT, 0)
					self._mixer.channel_strip(index).set_select_button(self._touchpad[index])
				if self._mixer.shifted() or not self._assign_midi_layer():
					self._send_midi(LIVEBUTTONMODE)
					for column in range(8): 
						for row in range(4):
							self._scene[row].clip_slot(column).set_launch_button(self._pad[column + (row*8)])
					for row in range(4):
						self._scene[row].set_launch_button(self._pad[7 + (row*8)])
				self._device.set_bank_nav_buttons(self._button[4], self._button[5])
				self._device_navigator.set_nav_buttons(self._button[7], self._button[6])
				self._current_nav_buttons = self._button[4:8]
				for index in range(4):
					self._button[index+4].set_on_off_values(DEVICE_NAV, 0)
				self._device.update()
				self._device_navigator.update()
			else:
				if not self._assign_midi_shift_layer():
					for index in range(8):
						self._touchpad[index].set_on_off_values(CHAN_SELECT, 0)
						self._mixer.channel_strip(index).set_select_button(self._touchpad[index])
					self._send_midi(LIVEBUTTONMODE)
					self._session._shifted = True
					for index in range(4):
						self._button[index+4].set_on_off_values(DEVICE_NAV, 0)
					#self._device.update()
					#self._device_navigator.update()
				self._device.deassign_all()
				self._send_midi(tuple([240, 0, 1, 97, 12, 61, 7, 7, 7, 7, 7, 7, 7, 7, 2, 247]))
				for index in range(8):
					#self._send_midi((191, index+1, LAYERSPLASH[0]))
					self._mixer.channel_strip(index).set_volume_control(self._fader[index])
					self._pad[index].set_on_off_values(TRACK_MUTE, 0)
					self._mixer.channel_strip(index).set_mute_button(self._pad[index])
					self._pad[index+8].set_on_off_values(TRACK_SOLO, 0)
					self._mixer.channel_strip(index).set_solo_button(self._pad[index+8])
					self._pad[index+16].set_on_off_values(TRACK_ARM, 0)
					self._mixer.channel_strip(index).set_arm_button(self._pad[index+16])
					self._pad[index+24].set_on_off_values(TRACK_STOP, TRACK_STOP)
					self._pad[index+24].send_value(TRACK_STOP)
				self._session.set_stop_track_clip_buttons(tuple(self._pad[24:32]))
			#self._device.set_bank_nav_buttons(self._button[4], self._button[5])
			#self._device_navigator.set_nav_buttons(self._button[7], self._button[6])
			self._mixer.update()
		self.request_rebuild_midi_map()
	

	def _assign_alternate_mappings(self, chan = 0):
		self._send_midi(MIDIBUTTONMODE)
		for pad in self._touchpad:
			pad.use_default_message()
			pad.set_channel(chan)
			pad.set_enabled(False)
			pad.reset()
		for pad in self._pad:
			pad.use_default_message()
			pad.set_channel(chan)
			pad.set_enabled(False)
		for pad in self._pad_CC:
			pad.release_parameter()
			pad.set_channel(chan)
			pad.set_enabled(False)
		for pad in self._touchpad:
			pad.use_default_message()
			pad.set_channel(chan)
			pad.set_enabled(chan is 0)
		for fader in self._fader[0:8]:
			fader.use_default_message()
			if chan!=12:
				fader.set_channel(chan)
			else:
				fader.set_channel(0)
			fader.set_enabled(False)
		self.request_rebuild_midi_map()
	


#a

