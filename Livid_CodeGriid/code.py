#Code.py 
#This is a midi remote script for the Code by Peter Nyboer, based on Ohm64 script by amounra
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
from _Framework.TransportComponent import TransportComponent # Class encapsulating all functions in Live's transport section
from _Framework.EncoderElement import EncoderElement
from _Framework.DeviceComponent import DeviceComponent 
from _Framework.M4LInterfaceComponent import M4LInterfaceComponent

from ShiftModeComponent import ShiftModeComponent
##from DetailViewCntrlComponent import DetailViewCntrlComponent


""" Here we define some global variables """
STANDALONE = False	# If this is false, certain functions (like clip-launching) will not be setup since it is assumed that another script is taking care of these functions
COLS = 8
ROWS = 4
CH = 0 # Channels are numbered 0 through 15, this script only makes use of one MIDI Channel (Channel 1)
DIALCOUNT = 32
session = None #Global session object - global so that we can manipulate the same session object from within our methods 
mixer = None #Global mixer object - global so that we can manipulate the same mixer object from within our methods
factoryreset = (240,0,1,97,4,6,247)
btn_channels = (240, 0, 1, 97, 4, 19, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, 0, 247)
enc_channels = (240, 0, 1, 97, 4, 20, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, CH, 247)
track_select_notes = [38,39,40,41,42,43,44,45]
mode_select_notes = [33,34,35,36,37]
matrix_nums = [1,5,9,13,17,21,25,29,2,6,10,14,18,22,26,30,3,7,11,15,19,23,27,31,4,8,12,16,20,24,28,32]	
#device_encoders=[0,1,2,3, 8,9,10,11, 4,5,6,7, 12,13,14,15, 16,17,18,19, 24,25,26,27, 20,21,22,23, 28,29,30,31] #used to group devices in 4x2, rather than 1x8 rows.
device_encoders=[0,8,16,24, 1,9,17,25, 2,10,18,26, 3,11,19,27, 4,12,20,28, 5,13,21,29, 6,14,22,30, 7,15,23,31]

class code(ControlSurface):
	__module__ = __name__
	__doc__ = " Code controller script "
	
	def __init__(self, c_instance):
		ControlSurface.__init__(self, c_instance)
		with self.component_guard():
			self.log_message(time.strftime("%d.%m.%Y %H:%M:%S", time.localtime()) + "--------------= Code opened =--------------") # Writes message into Live's main log file. This is a ControlSurface method.		  
			self._send_midi(factoryreset)
			self._send_midi(btn_channels)
			self._send_midi(enc_channels)
			#self.set_suppress_rebuild_requests(True) # Turn off rebuild MIDI map until after we're done setting up
			self._setup_controls()
			self._setup_device_controls()
			self._setup_mixer_control() # Setup the mixer object
			self._setup_transport_control()
			self._setup_session_control()  # Setup the session object - do this last
			self._setup_modes()
			self._setup_m4l_interface()
			#self.set_suppress_rebuild_requests(False) # Turn rebuild back on, once we're done setting up
			##self.assign_page_2()

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
	

	def _setup_controls(self):
		is_momentary = True
		self._dial = [None for index in range(DIALCOUNT)]
		self._trackbtns = [None for index in range(8)]
		self._modebtns = [None for index in range(5)]
		for index in range(DIALCOUNT):
			self._dial[index] = EncoderElement(MIDI_CC_TYPE, CH, matrix_nums[index], Live.MidiMap.MapMode.absolute)
			self._dial[index].name = 'Dial_' + str(index)
			self._dial[index].set_feedback_delay(-1)
		for index in range(8):
			self._trackbtns[index] = ButtonElement(is_momentary, MIDI_NOTE_TYPE, CH, track_select_notes[index])
			self._trackbtns[index].name =  'Button_' + str(index)
		for index in range(5):
			self._modebtns[index] = ButtonElement(is_momentary, MIDI_NOTE_TYPE, CH, mode_select_notes[index])
			self._modebtns[index].name = 'ModeButton_' + str(index)
		self._matrix = ButtonMatrixElement()
		self._matrix.name = 'Matrix'
		self._grid = [None for index in range(COLS)]
		for column in range(COLS):
			self._grid[column] = [None for index in range(COLS)]
			for row in range(ROWS):
				nn = 1+(column * ROWS) + row
				self._grid[column][row] = ButtonElement(is_momentary, MIDI_NOTE_TYPE, CH, nn) #comment out if you don't want clip launch
				self._grid[column][row].name = 'Grid_' + str(column) + '_' + str(row)
		for row in range(ROWS):
			button_row = []
			for column in range(COLS):
				button_row.append(self._grid[column][row])
			self._matrix.add_row(tuple(button_row)) 
	  
	""" not sure about this bit, but somehow I'll need to set up the modes here...!"""
	def _setup_modes(self):
		self._shift_mode = ShiftModeComponent(self, tuple(button for button in self._modebtns))
		self._shift_mode.name = 'Mix_Mode' #mode 1
		#self._shift_mode.set_mode_buttons(self._modebtns)
		
	def _setup_transport_control(self):
		self._transport = TransportComponent() 
		self._transport.name = 'Transport'

	def _setup_mixer_control(self):
		is_momentary = True
		self._num_tracks = (COLS)
		global mixer
		mixer = MixerComponent(COLS, 0, True, True)
		mixer.name = 'Mixer'
		self._mixer = mixer
		mixer.set_track_offset(0) #Sets start point for mixer strip (offset from left)
		for index in range(COLS):
			#use the bottom row of encoders for volume, so add 24 to offset the index
			mixer.channel_strip(index).set_volume_control(self._dial[index+24])
		for index in range(COLS):
			mixer.channel_strip(index).name = 'Mixer_ChannelStrip_' + str(index)
			mixer.track_eq(index).name = 'Mixer_EQ_' + str(index)
			mixer.track_filter(index).name = 'Mixer_Filter_' + str(index)  #added by a
			mixer.channel_strip(index)._invert_mute_feedback = True
			#mixer.channel_strip(index).set_select_button(ButtonElement(is_momentary, MIDI_NOTE_TYPE, CH, track_select_notes[index]))
		self.song().view.selected_track = mixer.channel_strip(0)._track #set the selected strip to the first track, so that we don't, for example, try to assign a button to arm the master track, which would cause an assertion error

	""" Technically, we aren't using the session control, but I'm going to set it up in case inter-script communication needs it"""
	def _setup_session_control(self):
		is_momentary = True
		num_tracks = COLS
		num_scenes = ROWS
		global session
		session = SessionComponent(num_tracks, num_scenes)
		session.name = "Session"
		session.set_offsets(0, 0)
		self._session = session
		self._session.set_stop_clip_value(0)
		self._scene = [None for index in range(ROWS)]
		for row in range(num_scenes):
			self._scene[row] = session.scene(row)
			self._scene[row].name = 'Scene_' + str(row)
			for column in range(num_tracks):
				clip_slot = self._scene[row].clip_slot(column)
				clip_slot.name = str(column) + '_Clip_Slot_' + str(row)
				clip_slot.set_triggered_to_play_value(64)
				clip_slot.set_triggered_to_record_value(64)
				clip_slot.set_stopped_value(0)
				clip_slot.set_started_value(64)
				clip_slot.set_recording_value(64)
				#clip_slot.set_launch_button(self._grid[column][row]) #comment out if you don't want clip launch
		session.set_mixer(mixer)
		self._session_zoom = SessionZoomingComponent(session)
		self._session_zoom.name = 'Session_Overview'
		self._session_zoom.set_stopped_value(0)
		self._session_zoom.set_playing_value(64)
		self._session_zoom.set_selected_value(64)
		if STANDALONE is True:
			self.set_highlighting_session_component(self._session)
			self._session.set_track_bank_buttons(self._grid[5][3], self._grid[4][3])   #comment out when using with Griid
			self._session.set_scene_bank_buttons(self._grid[7][3], self._grid[6][3])	# comment out when using with Griid
		
		
	"""this is where we take care of setting up the the multiple devices per page, we will need 4"""
	def _setup_device_controls(self):
		self._device = [None for index in range(4)]
		for index in range(ROWS):
			self._device[index] = DeviceComponent()
			self._device[index].name = 'Device_Component_' + str(index)
			#self.set_device_component(self._device)  #this doesn't work anymore, because we have multiple devices for the controller....we'll have to get fancy here, but that's for later
			#self._device_navigator = DetailViewControllerComponent()  #its unclear if we'll need this....how is device navigation (i.e. banking for device parameter banks) going to be handled by the script? 
			#self._device_navigator.name = 'Device_Navigator'
			device_param_controls = []
			for control in range(COLS):
				"""this setups up 8 device parameters per row"""
				#dial_index = control + (index*COLS)
				"""alternatively, this setus up device controls in 4 4x2 groups"""
				dial_index = device_encoders[control + (index*COLS)]
				device_param_controls.append(self._dial[dial_index])

				
			
			self._device[index].set_parameter_controls(tuple(device_param_controls))

	"""this is where we deassign every control that will be changing function when we switch modes...best to just deassign them all, and reassign them on update"""
	def deassign_matrix(self):
		for index in range(DIALCOUNT):			#this should totally work!!! I'm over appealing to Python's sadistic mannerisms right now....
			self._dial[index].send_value(0, True)	##this is kind of a hack, and should be unnecessary; the bool at the end tells the send_value method to force the value out to the controller
		for index in range(COLS):
			self._mixer.track_eq(index).set_enabled(False)	##set_gain_controls(tuple([None for index in range(3)]))
			self._mixer.channel_strip(index).set_volume_control(None)
			self._mixer.track_filter(index).set_enabled(False)	##set_filter_controls(tuple([None, None]))
			self._mixer.channel_strip(index).set_pan_control(None)
			self._mixer.channel_strip(index).set_select_button(None)
			self._mixer.channel_strip(index).set_send_controls(tuple([None for index in range(4)]))
		for device in range(4):
			self._device[device].set_bank_nav_buttons(None, None)
			self._device[device].set_enabled(False)	 ##set_parameter_controls(tuple([None for index in range(8)]))
		for track in range(8):
			self._mixer.channel_strip(track).set_select_button(None)
			for scene in range(4):
				self._scene[scene].clip_slot(track).set_launch_button(None)
		#self.request_rebuild_midi_map()  # I think this is causing problems updating the leds when in build?

	"""EQ Hi/Mid/Low and volume"""
	def assign_page_0(self):
		"""for each column"""
		is_momentary = True
		for index in range(COLS):
			self._mixer.track_eq(index).set_gain_controls((self._dial[index+16],self._dial[index+8],self._dial[index]))
			self._mixer.track_eq(index).set_enabled(True)
			self._mixer.channel_strip(index).set_volume_control(self._dial[index+24])#use the bottom row of encoders for volume, so add 24 to offset the index
			self._mixer.channel_strip(index).set_select_button(self._trackbtns[index])
			self.assign_cliplaunch()
			self._mixer.update()
			
	"""sends 1-4"""
	def assign_page_1(self):
		is_momentary = True
		for index in range(COLS):
			send_controllers = [self._dial[index],self._dial[index+8],self._dial[index+16],self._dial[index+24]]
			self._mixer.channel_strip(index).set_send_controls(tuple(send_controllers))
			self._mixer.channel_strip(index).set_select_button(self._trackbtns[index])
			self._mixer.update()

	"""devices 1-8"""
	def assign_pages_2_3(self):			##these need to be here anyway, whether or not there is a device present to control
		for index in range(4):
			self._device[index].set_enabled(True)
			#device_param_controls = []			###no need to reassign it, since we are turning it off and on
			#for control in range(COLS):		###in fact, I think we can assign all this stuff in the header except for things directly connected to the mixer module
			#	device_param_controls.append(self._dial[control + (index*COLS)])
			#self._device[index].set_parameter_controls(tuple(device_param_controls))
		self._reassign_devices(self._shift_mode._mode_index)
	
	""" filter res,filter q, pan, volume"""
	def assign_page_4(self):
		is_momentary = True
		for index in range(COLS):
			self._mixer.track_filter(index).set_filter_controls(self._dial[index], self._dial[index + 8]) #set_filter_controls(self, freq, reso)
			self._mixer.track_filter(index).set_enabled(True) 
			#self._mixer.track_eq(index).set_gain_controls((self._dial[index],self._dial[index+8],self._dial[index+16]))
			self._mixer.channel_strip(index).set_pan_control(self._dial[index+16])
			self._mixer.channel_strip(index).set_volume_control(self._dial[index+24])
			self._mixer.channel_strip(index).set_select_button(self._trackbtns[index])
			self._mixer.update()
	

	def assign_cliplaunch(self):
		if STANDALONE is True:
			for column in range(COLS):
				for row in range(ROWS-1):
					self._scene[row].clip_slot(column).set_launch_button(self._grid[column][row])

	def _reassign_devices(self, mode_index):
		if self._shift_mode._mode_index in range(2, 4): ##both of these lines would be better handled by a property 
			offset = (mode_index - 2) * 4				## set up in an override module of the device_component....bleh
			track = self.song().view.selected_track
			for index in range(4):
				if index + offset < len(track.devices):
					#self.log_message('assigning device')
					self._device[index].set_device(track.devices[index + offset])
				else:
					#self.log_message('assigning device to None')
					self._device[index].set_device(None)
				self._device[index].set_bank_nav_buttons(self._trackbtns[(index * 2)], self._trackbtns[(index * 2) + 1])
				self._device[index].update()

	def disconnect(self):
		"""clean things up on disconnect"""
		self.log_message(time.strftime("%d.%m.%Y %H:%M:%S", time.localtime()) + "--------------= Code log closed =--------------") #Create entry in log file
		ControlSurface.disconnect(self)
		return None		