# by amounra 0513 : http://www.aumhaa.com

from __future__ import with_statement
import contextlib
from _Framework.SubjectSlot import SubjectEvent
from _Framework.Signal import Signal
from _Framework.NotifyingControlElement import NotifyingControlElement
from _Framework.Util import in_range
from _Framework.Debug import debug_print
from _Framework.Disconnectable import Disconnectable
from _Framework.InputControlElement import InputSignal


class SwitchboardElement(NotifyingControlElement):
	__module__ = __name__
	__doc__ = ' Class that connects and disconnects monomodular clients'


	__subject_events__ = (SubjectEvent(name='value', signal=InputSignal, override=True),)
	_input_signal_listener_count = 0

	def __init__(self, host, clients, *a, **k):
		super(SwitchboardElement, self).__init__(host, clients, *a, **k)
		self._host = host
		self._devices = []
		for index in range(len(clients)):
			setattr(self, 'client_'+str(index), clients[index])
		self._client = clients
	

	def script_wants_forwarding(self):
		return True
	

	def disconnect(self):
		for client in self._client:
			client = None
		self._client = []
		super(SwitchboardElement, self).disconnect()
	

	def send_swing(self, client, val):
		self._host._client[client].receive_swing(val)
	

	def receive_swing(self, client, val):
		self._send('receive_swing', client, val)
	

	def disconnect_client(self, device):
		for client in self._client:
			if client.device == device:
				client._disconnect_client()
	

	def reset(self):
		pass
	

	def _send(self, args1 = None, args2 = None, args3 = None, args4 = None):
		self.notify_value(args1, args2, args3, args4)
	

	def reset_callbacks(self):
		pass
	


	def request_connection(self, device, version, inLive = 0):
		#self._host.log_message('request_connection ' + str(device))
		if version == self._host._version_check:
			client_num = len(self._client)
			for client in self._client:
				if client.device == device:
					client._disconnect_client()
			for client in self._client: 
				if client._connected is False:
					client._connect_to(device)
					client_num = client._number
					break
		else:
			client_num = self._host._version_check
		return client_num
	

	def force_connection(self, device, client_number, version):
		#self._host.log_message('force ' + str(device) + ' ' + str(client_number) + ' build ' + str(self._host._in_build_midi_map))
		if version == self._host._version_check:
			for client in self._client:
				if client.device == device:
					client._disconnect_client()
			self._client[client_number]._disconnect_client(True)
			self._client[client_number]._connect_to(device)
		else:
			client_number = self._host._version_check
		return client_number
	

	def editor_connection(self, device, version):
		#self._host.log_message('editor_connection ' + str(device) + ' ' + ' build ' + str(self._host._in_build_midi_map))
		if version == self._host._version_check:
			client_num = len(self._client)
			for client in self._client: 
				if client._connected is False:
					client._connect_to(device)
					client_num = client._number
					break
		else:
			client_num = self._host._version_check
		return client_num
	

	def set_client_enabled(self, client_num, enabled):
		self._client[client_num].set_enabled(enabled)
	


