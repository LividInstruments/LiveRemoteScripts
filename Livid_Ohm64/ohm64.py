#Ohm64.py 
#This is a midi remote script for the Ohm64 by Michael Chenetz
#updated for Live9 by amounra

from __future__ import with_statement
import Live # This allows us (and the Framework methods) to use the Live API on occasion
import time # We will be using time functions for time-stamping our log file outputs

""" We are only using using some of the Framework classes them in this script (the rest are not listed here) """
from _Framework.ButtonElement import ButtonElement # Class representing a button a the controller
from _Framework.ButtonMatrixElement import ButtonMatrixElement 
from _Framework.ChannelStripComponent import ChannelStripComponent # Class attaching to the mixer of a given track
from _Framework.ClipSlotComponent import ClipSlotComponent # Class representing a ClipSlot within Live
from _Framework.CompoundComponent import CompoundComponent # Base class for classes encompasing other components to form complex components
from _Framework.ControlElement import ControlElement # Base class for all classes representing control elements on a controller
from _Framework.ControlSurface import ControlSurface # Central base class for scripts based on the new Framework
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent # Base class for all classes encapsulating functions in Live
from _Framework.InputControlElement import * # Base class for all classes representing control elements on a controller
from _Framework.MixerComponent import MixerComponent # Class encompassing several channel strips to form a mixer
from _Framework.SceneComponent import SceneComponent # Class representing a scene in Live
from _Framework.SessionComponent import SessionComponent # Class encompassing several scene to cover a defined section of Live's session
from _Framework.SessionZoomingComponent import DeprecatedSessionZoomingComponent as SessionZoomingComponent
from _Framework.SliderElement import SliderElement # Class representing a slider on the controller
from _Framework.TransportComponent import TransportComponent # Class encapsulating all functions in Live's transport section
from _Framework.EncoderElement import EncoderElement
from _Framework.DeviceComponent import DeviceComponent 
from _Framework.M4LInterfaceComponent import M4LInterfaceComponent


""" Here we define some global variables """
CHANNEL = 0 # Channels are numbered 0 through 15, this script only makes use of one MIDI Channel (Channel 1)
session = None #Global session object - global so that we can manipulate the same session object from within our methods 
mixer = None #Global mixer object - global so that we can manipulate the same mixer object from within our methods
switchxfader = (240, 00, 01, 97, 02, 15, 01, 247)

class ohm64(ControlSurface):
	__module__ = __name__
	__doc__ = " Ohm64 controller script "
	
	def __init__(self, c_instance):
		ControlSurface.__init__(self, c_instance)
		with self.component_guard():
			self.log_message(time.strftime("%d.%m.%Y %H:%M:%S", time.localtime()) + "--------------= Ohm64 opened =--------------") # Writes message into Live's main log file. This is a ControlSurface method.	   
			self._send_midi(switchxfader)
			self._setup_transport_control()
			self._setup_mixer_control() # Setup the mixer object
			self._setup_session_control()  # Setup the session object
			self._setup_m4l_interface()


	def handle_sysex(self, midi_bytes):
		self._send_midi(240, 00, 01, 97, 02, 15, 01, 247)
		response = [long(0),long(0)]
		self.log_message(response)
		

	def _setup_m4l_interface(self):
		self._m4l_interface = M4LInterfaceComponent(controls=self.controls, component_guard=self.component_guard)
		self.get_control_names = self._m4l_interface.get_control_names
		self.get_control = self._m4l_interface.get_control
		self.grab_control = self._m4l_interface.grab_control
		self.release_control = self._m4l_interface.release_control
	

	def _setup_transport_control(self):
		is_momentary = True # We'll only be using momentary buttons here
		transport = TransportComponent() #Instantiate a Transport Component
		"""set up the buttons"""
		transport.set_play_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 69)) #ButtonElement(is_momentary, msg_type, channel, identifier) Note that the MIDI_NOTE_TYPE constant is defined in the InputControlElement module
		transport.set_stop_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 70))
		#transport.set_record_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 66))
		#transport.set_overdub_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 68))
		#transport.set_nudge_buttons(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 80), ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 73)) #(up_button, down_button)
		#transport.set_tap_tempo_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 80))
		#transport.set_metronome_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 80)) #For some reason, in Ver 7.x.x this method's name has no trailing "e" , and must be called as "set_metronom_button()"...
		#transport.set_loop_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 82))
		#transport.set_punch_buttons(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 85), ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 87)) #(in_button, out_button)
		#transport.set_seek_buttons(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 90), ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 92)) # (ffwd_button, rwd_button)
		#"""set up the sliders"""
		#transport.set_tempo_control(SliderElement(MIDI_CC_TYPE, CHANNEL, 26), SliderElement(MIDI_CC_TYPE, CHANNEL, 25)) #(control, fine_control)
		#transport.set_song_position_control(SliderElement(MIDI_CC_TYPE, CHANNEL, 24))
		
		device_param_controls = []
		effects_knob_cc = [17,16,9,8,19,18,11,10]
		device = DeviceComponent()
		for index in range(8):
			device_param_controls.append(EncoderElement(MIDI_CC_TYPE, 0, effects_knob_cc[index], Live.MidiMap.MapMode.absolute))
		device.set_parameter_controls(tuple(device_param_controls))
		self.set_device_component(device)


	def _setup_mixer_control(self):
		is_momentary = True # We use non-latching buttons (keys) throughout, so we'll set this as a constant
		num_tracks = 7 # Here we define the mixer width in tracks (a mixer has only one dimension)
		global mixer # We want to instantiate the global mixer as a MixerComponent object (it was a global "None" type up until now...)
		mixer = MixerComponent(num_tracks, 0) #(num_tracks, num_returns, with_eqs, with_filters)
		mixer.set_track_offset(0) #Sets start point for mixer strip (offset from left)
		"""set up the mixer buttons"""		  
		self.song().view.selected_track = mixer.channel_strip(0)._track
		mixer.selected_strip().set_mute_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 64))
		#mixer.selected_strip().set_solo_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 44))
		mixer.selected_strip().set_arm_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, 72))
		track_select_notes = [65, 73, 66, 74, 67, 75, 68, 76] #more note numbers need to be added if num_scenes is increased
		slider_select_notes = [23, 22, 15, 14, 5, 7, 6, 4]
		pan_select_notes = [21, 20, 13, 12, 3, 1, 0, 2]
		master_volume_control = SliderElement(MIDI_CC_TYPE, 0, 4)
		master_select_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 76)
		prehear_control = EncoderElement(MIDI_CC_TYPE, 0, 26, Live.MidiMap.MapMode.absolute)
		crossfader = SliderElement(MIDI_CC_TYPE, 0, 24)
		for index in range(num_tracks):
			mixer.channel_strip(index).set_select_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, track_select_notes[index]))
			mixer.channel_strip(index).set_volume_control(SliderElement(MIDI_CC_TYPE, CHANNEL, slider_select_notes[index]))
			mixer.channel_strip(index).set_pan_control(EncoderElement(MIDI_CC_TYPE, CHANNEL, pan_select_notes[index], Live.MidiMap.MapMode.absolute))
		crossfader.name = 'Crossfader'
		master_volume_control.name = 'Master_Volume_Control'
		master_select_button.name = 'Master_Select_Button'
		prehear_control.name = 'Prehear_Volume_Control'
		mixer.set_crossfader_control(crossfader)
		mixer.set_prehear_volume_control(prehear_control)
		mixer.master_strip().set_volume_control(master_volume_control)
		mixer.master_strip().set_select_button(master_select_button)

	def _setup_session_control(self):
		is_momentary = True
		self._shift_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 87)		   
		right_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 78)
		left_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 77)
		up_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 71)
		down_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 79)
		right_button.name = 'Bank_Select_Right_Button'
		left_button.name = 'Bank_Select_Left_Button'
		up_button.name = 'Bank_Select_Up_Button'
		down_button.name = 'Bank_Select_Down_Button'
		global session
		session = SessionComponent(7, 8)
		session.name = 'Session_Control'
		session.set_track_bank_buttons(right_button, left_button)
		session.set_scene_bank_buttons(down_button, up_button)
		matrix = ButtonMatrixElement()
		matrix.name = 'Button_Matrix'
		scene_launch_notes = [56,57,58,59,60,61,62,63]
		scene_launch_buttons = [ ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, scene_launch_notes[index]) for index in range(8) ]
		#track_stop_buttons = [ ButtonElement(is_momentary, MIDI_NOTE_TYPE, index, 52) for index in range(8) ]
		for index in range(len(scene_launch_buttons)):
			scene_launch_buttons[index].name = 'Scene_'+ str(index) + '_Launch_Button'
		#for index in range(len(track_stop_buttons)):
		#	 track_stop_buttons[index].name = 'Track_' + str(index) + '_Stop_Button'
		#stop_all_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 81)
		#stop_all_button.name = 'Stop_All_Clips_Button'
		#self._session.set_stop_all_clips_button(stop_all_button)
		#self._session.set_stop_track_clip_buttons(tuple(track_stop_buttons))
		#self._session.set_stop_track_clip_value(2)
		#button_notes = [0,8,16,24,32,40,48,56,1,9,17,25,33,41,49,57,2,10,18,26,34,42,50,58,3,11,19,27,35,43,51,59,4,12,20,28,36,44,52,60,5,13,21,29,37,45,53,61,6,14,22,30,38,46,54,62]
		for scene_index in range(8):
			scene = session.scene(scene_index)
			scene.name = 'Scene_' + str(scene_index)
			button_row = []
			scene.set_launch_button(scene_launch_buttons[scene_index])
			#scene.set_triggered_value(2)
			for track_index in range(7):
				button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHANNEL, (track_index * 8) + scene_index)
				button.name = str(track_index) + '_Clip_' + str(scene_index) + '_Button'
				button_row.append(button)
				clip_slot = scene.clip_slot(track_index)
				clip_slot.name = str(track_index) + '_Clip_Slot_' + str(scene_index)
				#clip_slot.set_triggered_to_play_value(2)
				#clip_slot.set_triggered_to_record_value(4)
				clip_slot.set_stopped_value(0)
				clip_slot.set_started_value(64)
				#clip_slot.set_recording_value(3)
				clip_slot.set_launch_button(button)

			matrix.add_row(tuple(button_row))

		#self._session.set_slot_launch_button(ButtonElement(is_momentary, MIDI_CC_TYPE, 0, 67))
		session.selected_scene().name = 'Selected_Scene'
		#session.selected_scene().set_launch_button(ButtonElement(is_momentary, MIDI_CC_TYPE, 0, 64))
		#session_zoom = SessionZoomingComponent(session)
		#session_zoom.name = 'Session_Overview'
		#session_zoom.set_button_matrix(matrix)
		#session_zoom.set_zoom_button(self._shift_button)
		#session_zoom.set_nav_buttons(up_button, down_button, left_button, right_button)
		#session_zoom.set_scene_bank_buttons(tuple(scene_launch_buttons))
		#session_zoom.set_stopped_value(0)
		#session_zoom.set_selected_value(127)
		session.set_mixer(mixer)
		self.set_highlighting_session_component(session)
		return None #return session


		
	   
	#def _on_selected_scene_changed(self):
	#	 """This is an override, to add special functionality (we want to move the session to the selected scene, when it changes)"""
	#	 """When making changes to this function on the fly, it is sometimes necessary to reload Live (not just the script)..."""
	#	 ControlSurface._on_selected_scene_changed(self) # This will run component.on_selected_scene_changed() for all components
	#	 """Here we set the mixer and session to the selected track, when the selected track changes"""
	#	 selected_scene = self.song().view.selected_scene #this is how we get the currently selected scene, using the Live API
	#	 all_scenes = self.song().scenes #then get all of the scenes
	#	 index = list(all_scenes).index(selected_scene) #then identify where the selected scene sits in relation to the full list
	#	 session.set_offsets(session._track_offset, index) #(track_offset, scene_offset) Set the session's scene offset to match the selected track (but make no change to the track offset)
		
	def disconnect(self):
		"""clean things up on disconnect"""
		self.log_message(time.strftime("%d.%m.%Y %H:%M:%S", time.localtime()) + "--------------= Ohm64 log closed =--------------") #Create entry in log file
		ControlSurface.disconnect(self)
		return None

