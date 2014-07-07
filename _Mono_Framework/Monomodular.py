# by amounra 0513 : http://www.aumhaa.com

from __future__ import with_statement
import Live
import time
import math
import sys
#import posix
#import gc




import Live.String
from _Tools import types
#import _Framework

#from _MxDCore.MxDUtils import MxDUtils
#if not ("/usr/lib/python2.5") in sys.path:
#	sys.path.append("/usr/lib/python2.5")
#sys.path = []
#for item in sys.path:
#	if item is ('/usr/lib/python2.5'):
#		sys.path.remove(item)

""" All of the Framework files are listed below, but we are only using using some of them in this script (the rest are commented out) """
from _Framework.ButtonElement import ButtonElement # Class representing a button a the controller
from _Framework.ButtonMatrixElement import ButtonMatrixElement # Class representing a 2-dimensional set of buttons
from _Framework.ChannelStripComponent import ChannelStripComponent # Class attaching to the mixer of a given track
from _Framework.CompoundComponent import CompoundComponent # Base class for classes encompasing other components to form complex components
from _Framework.ControlElement import ControlElement # Base class for all classes representing control elements on a controller 
from _Framework.ControlSurface import ControlSurface # Central base class for scripts based on the new Framework
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent # Base class for all classes encapsulating functions in Live
from _Framework.DeviceComponent import DeviceComponent # Class representing a device in Live
from _Framework.EncoderElement import EncoderElement # Class representing a continuous control on the controller
from _Framework.InputControlElement import * # Base class for all classes representing control elements on a controller
from _Framework.ModeSelectorComponent import ModeSelectorComponent # Class for switching between modes, handle several functions with few controls
from _Framework.NotifyingControlElement import NotifyingControlElement # Class representing control elements that can send values
from _Framework.TransportComponent import TransportComponent # Class encapsulating all functions in Live's transport section

"""Imports from the Monomodular Framework"""
from SwitchboardElement import SwitchboardElement
from MonoClient import MonoClient
from LiveUtils import *
from ModDevices import *

"""Custom files, overrides, and files from other scripts"""
from MonoLinkClient import MonoLinkClient
from MonoLink_Map import MONOLINK_ENABLE

#from _Generic.Devices import *

	
class Monomodular(ControlSurface):
	__module__ = __name__
	__doc__ = " Monomodular control script "



	def __init__(self, *a, **k):
		super(Monomodular, self).__init__(*a, **k)
		with self.component_guard():
			self._version_check = 'b995'
			self.log_message("<<<<<<<<<<<<<<<<<<<<<<<<< Monomodular " + str(self._version_check) + " log opened >>>>>>>>>>>>>>>>>>>>>>>>>") 
			#self._log_version_data()
			self._hosts = []
			self._client = [None for index in range(16)]
			self._setup_monomod()
			self._setup_switchboard()
			self._monolink_is_enabled = self._setup_monolink(MONOLINK_ENABLE)
			self._setup_device()
	

	"""script initialization methods"""
	"""def _log_version_data(self):
		self.log_message('modules' + str(sys.builtin_module_names))
		self.log_message('version' + str(sys.version))
		self.log_message('sys.path: ' + str(sys.path))
		for item in dir(gc):
			self.log_message(str(item))
		looks_at = gc.get_referrers(self)
		for item in looks_at:
			self.log_message(str(item))"""
	

	"""def _hijack_mxdcore(self):
		if sys.modules['_MxDCore.MxDCore']:
			self.log_message('got it!')
			#OldModule = sys.modules['_MxDCore.MxDCore']
			#sys.modules['_MxDCore.MxDCore'] = module
			#reload(sys.modules['_MxDCore.MxDCore'])"""
	


	def _setup_monomod(self):
		for index in range(16):
			self._client[index] = MonoClient(self, index)
			self._client[index].name = 'Client_' + str(index)
			self._client[index]._device_component.set_device_defs(MOD_BANK_DICT, MOD_TYPES)
		self._active_client = self._client[0]
		self._active_client._is_active = True
	

	def _setup_switchboard(self):
		self._switchboard = SwitchboardElement(self, self._client)
		self._switchboard.name = 'Switchboard'
	

	def _setup_monolink(self, enabled=False):
		if enabled:
			self._client.append(MonoLinkClient(self, 16))
			self._client[16].name = 'MonoLinkClient'
		return enabled
	

	def _setup_device(self):
		self._device = DeviceComponent()
		self._device.name = 'Device_Component'
		self.set_device_component(self._device)
	

	def update_display(self):
		super(Monomodular, self).update_display()
		if self._monolink_is_enabled:
			self._client[16].call_network_functions()
	

	"""general functionality"""
	def disconnect(self):
		"""clean things up on disconnect"""
		self.log_message("<<<<<<<<<<<<<<<<<<<<<<<<< Monomodular " + str(self._version_check) + " log closed >>>>>>>>>>>>>>>>>>>>>>>>>")
		#self._switchboard.disconnect()
		#for client in self._client:
		#	client.disconnect()
		super(Monomodular, self).disconnect()
		self._hosts = []
	

	def connect_script_instances(self, instanciated_scripts):
		hosts = []
		#self.log_message('monomodular connect script instances')
		for s in instanciated_scripts:
			if '_monomod_version' in dir(s):
				if s._monomod_version == self._version_check:
					#self.show_message('found monomod version ' + str(s._monomod_version) + ' in script ' + str(s._host_name))
					for host in s.hosts:
						hosts.append(host)
						host.connect_to_clients(self)
						#if not self._awake:
						#	self.log_message = s.log_message
						#	s._register_timer_callback(self.update_display)
						#	self._awake = True
					self.log_message('found monomod version ' + str(s._monomod_version) + ' in script ' + str(s._host_name))
				else:
					self.log_message('version mismatch: Monomod version ' + str(self._version_check) + ' vs. Host version ' + str(s._monomod_version))
					#self.show_message('version mismatch: Monomod version ' + str(self._version_check) + ' vs. Host version ' + str(s._monomod_version))
		self._hosts = hosts
	

	def display_message(self, message):
		self.show_message(message)
	

	def send_midi(self, Type, num, val):
		#self.log_message('send_midi' + str(Type) + str(num) + str(val))
		#if len(values==3) and (values[0]!=240):
		Type = min(192, max(Type, 144))
		num = min(127, max(num, 0))
		val = min(127, max(val, 0))
		self.log_message('send_midi' + str(Type) + str(num) + str(val))
		self._send_midi(tuple([Type, num, val]));
	

	"""def _setup_midi_input(self):
		for channel in range(16):
			for message_id in range(127):
				Live.MidiMap.forward_midi_note(self._c_instance.handle(), self._midi_map_handle, channel, message_id)
				Live.MidiMap.forward_midi_cc(self._c_instance.handle(), self._midi_map_handle, channel, message_id)
			#Live.MidiMap.forward_midi_pitchbend(self._midi_map_handle, channel)
		self.log_message('setup midi input')"""
	


	#def _setup_mxdcore(self):
	#	self._mxdcore = MxDCore()
	#	self._mxdcore.set_manager(self._c_instance)
	
	
	
	
	
	