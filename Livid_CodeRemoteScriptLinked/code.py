#!/usr/bin/env python
#Code.py 
#This is a midi remote script for the Code by Peter Nyboer, based on Ohm64 script by Michael Chenetz
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
from VCM600.MixerComponent import MixerComponent # Class encompassing several channel strips to form a mixer
from _Framework.SceneComponent import SceneComponent # Class representing a scene in Live
from _Framework.SessionComponent import SessionComponent # Class encompassing several scene to cover a defined section of Live's session
from _Framework.SessionZoomingComponent import DeprecatedSessionZoomingComponent as SessionZoomingComponent
from _Framework.SliderElement import SliderElement # Class representing a slider on the controller
#from _Framework.TransportComponent import TransportComponent # Class encapsulating all functions in Live's transport section
from _Framework.EncoderElement import EncoderElement
from _Framework.DeviceComponent import DeviceComponent 
from _Framework.M4LInterfaceComponent import M4LInterfaceComponent

from TransportComponent import TransportComponent
from DetailViewCntrlComponent import DetailViewCntrlComponent
from AddlTransportComponent import AddlTransportComponent #adds undo/redo
from ShiftableTransportComponent import ShiftableTransportComponent
from ShiftableTranslatorComponent import ShiftableTranslatorComponent


""" Here we define some global variables """
CHAN = 0 # Channels are numbered 0 through 15, this script only makes use of one MIDI Channel (Channel 1)
session = None #Global session object - global so that we can manipulate the same session object from within our methods 
mixer = None #Global mixer object - global so that we can manipulate the same mixer object from within our methods
factoryreset = (240,0,1,97,4,6,247)
btn_channels = (240, 0, 1, 97, 4, 19, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, 0, 247);
enc_channels = (240, 0, 1, 97, 4, 20, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, CHAN, 247);

class code(ControlSurface):
	__module__ = __name__
	__doc__ = " Code controller script "
	
	def __init__(self, c_instance):
		ControlSurface.__init__(self, c_instance)
		with self.component_guard():
			self.log_message(time.strftime("%d.%m.%Y %H:%M:%S", time.localtime()) + "--------------= Code opened =--------------") # Writes message into Live's main log file. This is a ControlSurface method.		  
			self._link_offset = [False, True]  ##change the way multiple codes are linked together = [offset for Track, offset for Scene]
			self._send_midi(factoryreset)
			self._send_midi(btn_channels)
			self._send_midi(enc_channels)
			self._setup_mixer_control() # Setup the mixer object
			self._setup_transport_control()
			self._setup_session_control()  # Setup the session object - do this last
			self._setup_m4l_interface()
			for control in self.controls:
				if isinstance(control, EncoderElement):
					control.set_feedback_delay(-1)
			for component in self.components:
				component.set_enabled(True)
		
	def handle_sysex(self, midi_bytes):
		self._send_midi(tuple([240, 00, 01, 97, 04, 15, 01, 247]))
		#response = [long(0),long(0)]
		#self.log_message(str(response))
	


	def _setup_m4l_interface(self):
		self._m4l_interface = M4LInterfaceComponent(controls=self.controls, component_guard=self.component_guard)
		self.get_control_names = self._m4l_interface.get_control_names
		self.get_control = self._m4l_interface.get_control
		self.grab_control = self._m4l_interface.grab_control
		self.release_control = self._m4l_interface.release_control
	

	def _setup_transport_control(self):
		is_momentary = True # We'll only be using momentary buttons here
		transport = ShiftableTransportComponent() #Instantiate a Transport Component
		#addtransport = AddlTransportComponent() #Instantiate an AddlTransport Component
		
		device_param_controls = []
		#effects_knob_cc = [16,20,24,28,17,21,25,29]
		effects_knob_cc = [17,21,25,29,18,22,26,30]
		device = DeviceComponent()
		for index in range(8):
			device_param_controls.append(EncoderElement(MIDI_CC_TYPE, CHAN, effects_knob_cc[index], Live.MidiMap.MapMode.absolute))
		device.set_parameter_controls(tuple(device_param_controls))
		#self.set_device_component(device)
		
		#from apc
		device_bank_buttons = []
		#device_param_controls = []
		#device_buttons =[16,20,24,28,17,21,25,29];
		device_buttons =[17,21,25,29,18,22,26,30];
		bank_button_labels = ('Clip_Track_Button', 'Device_On_Off_Button', 'Previous_Device_Button', 'Next_Device_Button', 'Detail_View_Button', 'Rec_Quantization_Button', 'Midi_Overdub_Button', 'Device_Lock_Button') #'Metronome_Button')
		for index in range(8):
			device_bank_buttons.append(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHAN, device_buttons[index]))
			device_bank_buttons[-1].name = bank_button_labels[index]
			#ring_mode_button = ButtonElement(not is_momentary, MIDI_CC_TYPE, 0, 24 + index)
			#ringed_encoder = RingedEncoderElement(MIDI_CC_TYPE, 0, 16 + index, Live.MidiMap.MapMode.absolute)
			#ringed_encoder.set_ring_mode_button(ring_mode_button)
			#ringed_encoder.name = 'Device_Control_' + str(index)
			#ring_mode_button.name = ringed_encoder.name + '_Ring_Mode_Button'
			#device_param_controls.append(ringed_encoder)
		device.name = 'Device_Component'
		device.set_bank_buttons(tuple(device_bank_buttons))
		detail_view_toggler = DetailViewCntrlComponent()
		detail_view_toggler.name = 'Detail_View_Control'
		detail_view_toggler.set_device_clip_toggle_button(device_bank_buttons[0])
		device.set_on_off_button(device_bank_buttons[1])
		detail_view_toggler.set_device_nav_buttons(device_bank_buttons[2], device_bank_buttons[3])
		detail_view_toggler.set_detail_toggle_button(device_bank_buttons[4])
		device.set_lock_button(device_bank_buttons[7]) #assign device lock to bank_button 8 (in place of metronome)...
		self.set_device_component(device)
		#detail_view_toggler.set_shift_button(self._shift_button)
		#from apc 
		
		self._shift_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 37) 
		"""set up the buttons"""
		play_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHAN, 24) #ButtonElement(is_momentary, msg_type, channel, identifier) Note that the MIDI_NOTE_TYPE constant is defined in the InputControlElement module
		stop_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHAN, 28)
		record_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHAN, 32)
		nudge_up_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHAN, 27)
		nudge_down_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHAN, 23)
#		tap_tempo_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHAN, 19)
		redo_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHAN, 19)
		undo_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHAN, 20)
		play_button.name = 'Play_Button'
		stop_button.name = 'Stop_Button'
		record_button.name = 'Record_Button'
		nudge_up_button.name = 'Nudge_Up_Button'
		nudge_down_button.name = 'Nudge_Down_Button'
#		tap_tempo_button.name = 'Tap_Tempo_Button'
		redo_button.name = 'Redo_Button'
		undo_button.name = 'Undo_Button'
		transport.set_shift_button(self._shift_button)
		transport.set_play_button(play_button)
		transport.set_stop_button(stop_button)
		transport.set_record_button(record_button)
		transport.set_nudge_buttons(nudge_up_button, nudge_down_button)
		#addtransport.set_undo_button(undo_button) 
		#addtransport.set_redo_button(redo_button) 
		transport.set_tap_tempo_button(nudge_up_button) #shifted nudge
		transport.set_quant_toggle_button(device_bank_buttons[5])
		transport.set_overdub_button(device_bank_buttons[6])
#		transport.set_metronome_button(device_bank_buttons[7])
		#transport.set_tempo_encoder(self.prehear_control) #shifted prehear
		bank_button_translator = ShiftableTranslatorComponent()
		bank_button_translator.set_controls_to_translate(tuple(device_bank_buttons))
		bank_button_translator.set_shift_button(self._shift_button)
			  

	def _setup_mixer_control(self):
		is_momentary = True # We use non-latching buttons (keys) throughout, so we'll set this as a constant
		num_tracks = 4 # Here we define the mixer width in tracks (a mixer has only one dimension)
		global mixer # We want to instantiate the global mixer as a MixerComponent object (it was a global "None" type up until now...)
		mixer = MixerComponent(num_tracks, 2, with_eqs=True, with_filters=False) #(num_tracks, num_returns, with_eqs, with_filters)
		mixer.set_track_offset(0) #Sets start point for mixer strip (offset from left)
		"""set up the mixer buttons"""		  
		self.song().view.selected_track = mixer.channel_strip(0)._track
		#mute_notes = [1,5,9,13]
		#solo_notes = [2,6,10,14]
		#arm_notes = [3,7,11,15]
		track_select_notes = [38,39,40,41]#more note numbers need to be added if num_scenes is increased
		send_ccs = [2,6,10,14,1,5,9,13]
		pan_ccs = [3,7,11,15]
		slider_ccs = [4,8,12,16]
		for index in range(num_tracks):
			mixer.channel_strip(index).set_select_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHAN, track_select_notes[index]))
			mixer.channel_strip(index).set_volume_control(SliderElement(MIDI_CC_TYPE, CHAN, slider_ccs[index]))
			mixer.channel_strip(index).set_pan_control(EncoderElement(MIDI_CC_TYPE, CHAN, pan_ccs[index], Live.MidiMap.MapMode.absolute))
			#put send A and send B controllers into an array, which is then "tupled" for set_send_controls:
			send_controlers = [EncoderElement(MIDI_CC_TYPE, CHAN, send_ccs[index], Live.MidiMap.MapMode.absolute), EncoderElement(MIDI_CC_TYPE, CHAN, send_ccs[index+num_tracks], Live.MidiMap.MapMode.absolute)]
			mixer.channel_strip(index).set_send_controls(tuple(send_controlers))
		
		crossfader = SliderElement(MIDI_CC_TYPE, CHAN, 28)
		master_volume_control = SliderElement(MIDI_CC_TYPE, CHAN, 32)
		returna_pan_control = SliderElement(MIDI_CC_TYPE, CHAN, 19)
		returna_volume_control = SliderElement(MIDI_CC_TYPE, CHAN, 20)
		returnb_pan_control = SliderElement(MIDI_CC_TYPE, CHAN, 23)
		returnb_volume_control = SliderElement(MIDI_CC_TYPE, CHAN, 24)
		master_select_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHAN, 31)
		prehear_control = EncoderElement(MIDI_CC_TYPE, CHAN, 30, Live.MidiMap.MapMode.absolute)
		crossfader.name = 'Crossfader'
		master_volume_control.name = 'Master_Volume_Control'
		returna_pan_control.name = 'ReturnA_Pan_Control'
		returna_volume_control.name = 'ReturnA_Volume_Control'
		returnb_pan_control.name = 'ReturnB_Pan_Control'
		returnb_volume_control.name = 'ReturnB_Volume_Control'
		master_select_button.name = 'Master_Select_Button'
		prehear_control.name = 'Prehear_Volume_Control'
		mixer.set_crossfader_control(crossfader)
		mixer.master_strip().set_volume_control(master_volume_control)
		mixer.master_strip().set_select_button(master_select_button)
		mixer.set_prehear_volume_control(prehear_control)
		mixer.return_strip(0).set_pan_control(returna_pan_control)
		mixer.return_strip(0).set_volume_control(returna_volume_control)
		mixer.return_strip(1).set_pan_control(returnb_pan_control)
		mixer.return_strip(1).set_volume_control(returnb_volume_control)
		
	def _setup_session_control(self):
		is_momentary = True		  
		right_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHAN, 43)
		left_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHAN, 42)
		up_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHAN, 44)
		down_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHAN, 45)
		right_button.name = 'Bank_Select_Right_Button'
		left_button.name = 'Bank_Select_Left_Button'
		up_button.name = 'Bank_Select_Up_Button'
		down_button.name = 'Bank_Select_Down_Button'
		global session
		session = SessionComponent(4, 4)
		session.name = 'Session_Control'
		session.set_track_bank_buttons(right_button, left_button)
		session.set_scene_bank_buttons(down_button, up_button)
		self._session = session
		matrix = ButtonMatrixElement()
		matrix.name = 'Button_Matrix'
		scene_launch_notes = [33,34,35,36]
		scene_launch_buttons = [ ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHAN, scene_launch_notes[index]) for index in range(4) ]
		#track_stop_buttons = [ ButtonElement(is_momentary, MIDI_NOTE_TYPE, index, 52) for index in range(4) ]
		for index in range(len(scene_launch_buttons)):
			scene_launch_buttons[index].name = 'Scene_'+ str(index) + '_Launch_Button'
		#for index in range(len(track_stop_buttons)):
		#	 track_stop_buttons[index].name = 'Track_' + str(index) + '_Stop_Button'
		#stop_all_button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, 0, 81)
		#stop_all_button.name = 'Stop_All_Clips_Button'
		#self._session.set_stop_all_clips_button(stop_all_button)
		#self._session.set_stop_track_clip_buttons(tuple(track_stop_buttons))
		#self._session.set_stop_clip_value(2)
		button_notes = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32]
		for scene_index in range(4):
			scene = session.scene(scene_index)
			scene.name = 'Scene_' + str(scene_index)
			button_row = []
			scene.set_launch_button(scene_launch_buttons[scene_index])
			#scene.set_triggered_value(2)
			for track_index in range(4):
				button = ButtonElement(is_momentary, MIDI_NOTE_TYPE, CHAN, (track_index * 4) + scene_index + 1)
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
		self.set_highlighting_session_component(session)
		session.set_mixer(mixer)
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
		if self._session._is_linked():
			self._session._unlink()
		self.log_message(time.strftime("%d.%m.%Y %H:%M:%S", time.localtime()) + "--------------= Code log closed =--------------") #Create entry in log file
		ControlSurface.disconnect(self)
		return None

	def connect_script_instances(self, instanciated_scripts):
		link = False
		offsets = [0, 0]
		new_channel = CHAN
		for s in instanciated_scripts:
			if isinstance(s, code) and not s is self:
				link = True
				if s._session._is_linked():
					self.log_message('found other linked instance')
					offsets[0] += (int(self._link_offset[0]) * 8)
					offsets[1] += (int(self._link_offset[1]) * 4)
					new_channel += 1
		if link and not self._session._is_linked():
			self._session.set_offsets(offsets[0], offsets[1])
			self._session._link()
		self._set_code_channels(new_channel)
	

	def _set_code_channels(self, channel):
		for control in self.controls:
			if(isinstance(control, InputControlElement)):
				control.set_channel(channel)
				control._original_channel = channel
				#self.log_message('new channel' + str(control))
		self.request_rebuild_midi_map()
		#self.log_message('setting new code channel' + str(channel))
		self._send_midi(tuple([240,0,1,97,4,6,247]))
		self._send_midi(tuple([240, 0, 1, 97, 4, 19, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, 247]));
		self._send_midi(tuple([240, 0, 1, 97, 4, 20, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, channel, 247]));
		for index in range(128):
			self._send_midi(tuple([240, 0, 1, 97, 04, 21, index, 0, channel, 247]))
			#self._send_midi(tuple([240, 0, 1, 97, 04, 21, index, 1, channel, 247]))

