# by amounra 0513 : http://www.aumhaa.com

from __future__ import with_statement
import Live
import sys
import contextlib

from _Framework.SubjectSlot import SubjectEvent
from _Framework.Signal import Signal
from _Framework.NotifyingControlElement import NotifyingControlElement
from _Framework.Util import in_range
from _Framework.Debug import debug_print
from _Framework.Disconnectable import Disconnectable

import modRemixNet as RemixNet
import modOSC
from modZeroconf import *
import modsocket as socket

from _Mono_Framework.MonoClient import MonoClient
from _Mono_Framework.LiveUtils import *

from MonoLink_Map import *


MODES = ['SerialOSC', 'MonomeSerial']
MSG = ['/grid/key', '/press']
QUADS = [[0, 0], [8, 0], [0, 8], [8, 8]]



class MonoLinkClient(MonoClient):


	def __init__(self, *a, **k):
		super(MonoLinkClient, self).__init__(*a, **k)

		#monolink specific 
		self._prefix = '/MonoLink'
		self.basicAPI = False
		self.conf = None
		self._inPrt = int(PRESETS[0][2][0])
		self._outPrt = int(PRESETS[0][2][1])
		self._inst = 0
		
		try:	
			self.conf = Zeroconf(self)
		except:
			self._host.log_message('Could not create Bonjour Registerer...something must be blocking this port or address') 
		
		self._is_monolink = True
		self._format = 0
		self.oscServer = None
		self._setup_oscServer()

	

	def _setup_oscServer(self):
		if not self.oscServer is None:
			self.oscServer.shutdown()	
		self.basicAPI = False
		self.oscServer = RemixNet.OSCServer('localhost', self._outPrt, 'localhost', self._inPrt)
		self._inPrt = int(self.oscServer.srcPort)	##doing this in case the port wasn't available and had to be advanced by the oscServer
		self.oscServer.sendOSC('/MonoLink', 'startup')
	

	def _banner(self):
		pass
	

	def disconnect(self):
		super(MonoLinkClient, self).disconnect()
		if not self.oscServer is None:
			self.oscServer.shutdown()
		self.oscServer = None
		self.unregister()
	

	def reset(self):
		pass
	

	def _connect_to(self, device=None):
		self._connected = True
		self._host._refresh_stored_data()
	

	def _disconnect_client(self):
		#self._host.log_message('disconnect' + str(self._number))
		self._create_grid()
		self._create_keys()
		self._swing = 0
		self._report_offset = False
		self._connected = False
		self._device = None
		for host in self._active_host:
			host.update()
	

	def _device_listener(self):
		pass
	

	def _send_offset(self, x, y):
		pass
	

	def _send_key(self, index, value):
		pass
	

	def _send_grid(self, column, row, value):
		self._send(MSG[self._format], [column, row, value])
	

	def _send(self, addr = None, val = None, args3 = None, args4 = None):
		#self._host.log_message('_send' + str(addr) + str(val))
		if (self._enabled is True) and (self.oscServer != None):
			#self._host.log_message('really _send' + str(self._prefix) + str(addr) + ' ' + str(val))
			self.oscServer.sendOSC(str(self._prefix)+addr, val)
	

	def receive_autoselect_enabled(self, val):
		pass
	

	#MonoLinkComponent specific calls 

	def call_network_functions(self):
		#self._host.log_message('call_net_func')		  
		if self.basicAPI is False:
			#self._host.log_message('basicAPI is False')		
			try:
				doc = self._host.song()
			except:
				return
			try:
				#self._host.log_message('trying to assign callbacks')
				self.basicAPI = self._assign_sys_callbacks()
				# Commented for stability
				#doc.add_current_song_time_listener(self.oscServer.processIncomingUDP)
				self.oscServer.sendOSC('/MonoLink', ['basicAPI:', int(self.basicAPI)])
				self.register()
				self._assign_callbacks(self._prefix)
				self.set_enabled(1)
			except:
				return
		if self.is_active() and self.oscServer:
			try:
				self.oscServer.processIncomingUDP()
			except:
				pass
	

	def _conf_info(self):
		desc = {'type':'_monome-osc._udp','domain':'local'}
		return ServiceInfo("_monome-osc._udp.local.", "monolink "+str(self._inst)+"._monome-osc._udp.local.", socket.inet_aton("127.0.0.1"), self._inPrt, 0, 0, desc, "localhost")
	
	

	def register(self):
		if self.conf:
			#self._host.log_message('registering service info for port ' + str(self._inPrt))
			try:
				self.conf.registerService([self._conf_info(), 0], 20)
			except:
				self._host.log_message('cannot register current service info')
	

	def unregister(self):
		if self.conf:
			#self._host.log_message('unregistering service for port ' + str(self._inPrt))
			try:
				self.conf.unregisterService([self._conf_info(), 0])
			except:
				self._host.log_message('cannot unregister current service info')
			self._inst += 1
	

	def _assign_sys_callbacks(self):
		#self._host.log_message('assign_sys_callbacks')
		if self.oscServer:
			#self._host.log_message('deleting sys callbacks')
			self.oscServer.resetCallbacks()
		else:
			return False
		if self._format is 0:
			self.oscServer.addCallback(self.sysEchoCB, "/echo")
			self.oscServer.addCallback(self.sysInfoCB, "/sys/info")
			self.oscServer.addCallback(self.sysPortCB, "/sys/port")
			self.oscServer.addCallback(self.sysHostCB, "/sys/host")
			self.oscServer.addCallback(self.sysIdCB, "/sys/id")
			self.oscServer.addCallback(self.sysPrefixCB, "/sys/prefix")
			self._assign_callbacks(self._prefix)
			#self._host.log_message('serialosc sys callbacks assigned, returning true')
			return True
		elif self._format is 1:
			self.oscServer.addCallback(self.sysEchoCB, "/echo")
			self.oscServer.addCallback(self.sysOffsetCB, "/sys/offset")
			self.oscServer.addCallback(self.sysPrefixCB, "/sys/prefix")
			self.oscServer.addCallback(self.sysReportCB, "/sys/report")
			#self._host.log_message('monomeserial sys callbacks assigned, returning true')
			self._assign_callbacks(self._prefix)
			return True
		else:
			return False
	

	def sysEchoCB(self, msg=None):
		self.oscServer.sendOSC("/MonoLink/echo", msg)
	

	def sysInfoCB(self, msg=None):
		self._host.log_message('infoCB' + str(self._outPrt) + str(self._prefix))
		self._host.schedule_message(30, self._info_return)
	

	def _info_return(self):
		if(self.oscServer):
			if self._format is 0:
				self._host.log_message('info return serialosc')
				self.oscServer.sendOSC("/sys/port", self._outPrt)
				self.oscServer.sendOSC("/sys/prefix", self._prefix)
				self.oscServer.sendOSC("/sys/id", self._number)
			elif self._format is 1:
				self._host.log_message('info return monomeserial')
				self.oscServer.sendOSC("/sys/devices", 1)
				self.oscServer.sendOSC("/sys/prefix", [0, self._prefix])
				self.oscServer.sendOSC("/sys/type", [0, 256])
				self.oscServer.sendOSC("/sys/cable", [0, 'up'])
				self.oscServer.sendOSC("/sys/offset", [0, 0, 0])
		self._host.log_message('info return completed')
	

	def sysPortCB(self, msg=None):
		self._host.log_message('sysPortCB' + str(msg))
		if msg[2] != None:
			self._host.log_message('old outport ' + str(self._outPrt))
			if	self._outPrt != int(msg[2]):
				self._outPrt = int(msg[2])
				self.oscServer.set_outPort(self._outPrt)
				self._host.log_message('changed')
	

	def sysHostCB(self, msg=None):
		self._host.log_message('sysHostCB' + str(msg))
	

	def sysIdCB(self, msg=None):
		self._host.log_message('sysIdCB' + str(msg))
	

	def sysPrefixCB(self, msg=None):
		self._host.log_message('sysPrefix' + str(msg))
		self._prefix = str(msg[2])
		self._assign_callbacks(msg[2])
		self._host.schedule_message(30, self._info_return)
	

	def sysOffsetCB(self, msg=None):
		pass
	

	def sysReportCB(self, msg=None):
		pass
	

	def _assign_callbacks(self, prefix):
		#self._host.log_message('assigning callbacks for prefix')
		if self._prefix != prefix:
			self.oscServer.removeCallback(str(self._prefix+'/grid/led/set'))
			self.oscServer.removeCallback(str(self._prefix+'/grid/led/all'))
			self.oscServer.removeCallback(str(self._prefix+'/grid/led/map'))
			self.oscServer.removeCallback(str(self._prefix+'/grid/led/row'))
			self.oscServer.removeCallback(str(self._prefix+'/grid/led/col'))
			self.oscServer.removeCallback(str(self._prefix+'/led'))
			self.oscServer.removeCallback(str(self._prefix+'/clear'))
			self.oscServer.removeCallback(str(self._prefix+'/frame'))
			self.oscServer.removeCallback(str(self._prefix+'/led_row'))
			self.oscServer.removeCallback(str(self._prefix+'/led_col'))
			self.oscServer.removeCallback(str(self._prefix+'/grid/led/intensity'))
			self.oscServer.removeCallback(str(self._prefix+'/grid/led/level/set'))
			self.oscServer.removeCallback(str(self._prefix+'/grid/led/level/all'))
			self.oscServer.removeCallback(str(self._prefix+'/grid/led/level/map'))
			self.oscServer.removeCallback(str(self._prefix+'/grid/led/level/row'))
			self.oscServer.removeCallback(str(self._prefix+'/grid/led/level/col'))
			#self._host.log_message('prefixed callbacks deleted')
		if prefix != None:
			self._prefix = prefix
			if self._format is 0:
				self.oscServer.addCallback(self.ledSet, str(self._prefix+'/grid/led/set'))
				self.oscServer.addCallback(self.ledAll, str(self._prefix+'/grid/led/all'))
				self.oscServer.addCallback(self.ledMap, str(self._prefix+'/grid/led/map'))
				self.oscServer.addCallback(self.ledRow, str(self._prefix+'/grid/led/row'))
				self.oscServer.addCallback(self.ledCol, str(self._prefix+'/grid/led/col'))
				self.oscServer.addCallback(self.ledIntensity, str(self._prefix+'/grid/led/intensity'))
				self.oscServer.addCallback(self.ledLvlSet, str(self._prefix+'/grid/led/level/set'))
				self.oscServer.addCallback(self.ledLvlAll, str(self._prefix+'/grid/led/level/all'))
				self.oscServer.addCallback(self.ledLvlMap, str(self._prefix+'/grid/led/level/map'))
				self.oscServer.addCallback(self.ledLvlRow, str(self._prefix+'/grid/led/level/row'))
				self.oscServer.addCallback(self.ledLvlCol, str(self._prefix+'/grid/led/level/col'))
			elif self._format is 1:
				self.oscServer.addCallback(self.ledSet, str(self._prefix+'/led'))
				self.oscServer.addCallback(self.ledClear, str(self._prefix+'/clear'))
				self.oscServer.addCallback(self.ledMap, str(self._prefix+'/frame'))
				self.oscServer.addCallback(self.led_row, str(self._prefix+'/led_row'))
				self.oscServer.addCallback(self.led_col, str(self._prefix+'/led_col'))
		#self._host.log_message('prefixed callbacks assigned')
	

	def ledSet(self, msg=None):
		#self._script.log_message('_ledSet' + str(msg[2]) + str(msg[3]) + str(msg[4]))
		self.receive_grid(msg[2], msg[3], msg[4])
	

	def ledAll(self, msg=None):
		self.receive_grid_all(msg[2])
	

	def ledRow(self, msg=None):
		if len(msg) > 3:
			xOff = int(msg[2])
			if xOff%8 is 0:
				yOff = int(msg[3])
				rows = msg[4:]
				for quad in range(len(rows)):
					rowOut = self.int2bin(rows[quad])
					for cell in range(8):
						#self._host.log_message(str(xOff+index+QUADS[quad][0]) + str(yOff+cell+QUADS[quad][1]) + str(rowOut[index]))
						self.receive_grid(xOff+QUADS[quad][0], yOff+cell+QUADS[quad][1], rowOut[cell])
	

	def ledCol(self, msg=None):
		if len(msg) > 3:
			yOff = int(msg[3])
			if yOff%8 is 0:
				xOff = int(msg[2])
				cols = msg[4:]
				for quad in range(len(cols)):
					colOut = self.int2bin(cols[quad])
					for cell in range(8):
						#self._host.log_message(str(xOff+index+QUADS[quad][0]) + str(yOff+cell+QUADS[quad][1]) + str(rowOut[index]))
						self.receive_grid(xOff+cell+QUADS[quad][0], yOff+QUADS[quad][1], colOut[cell])
	

	def ledMap(self, msg=None):
		xOff = int(msg[2])
		yOff = int(msg[3])
		map = msg[4:]
		if len(map) is 8:
			for row in range(8):
				rowOut = self.int2bin(row)
				for cell in range(8):
					self.receive_grid(x_Off+cell, yOff+row, rowOut[cell])
	

	def ledIntensity(self, msg=None):
		pass
	

	def ledLvlSet(self, msg=None):
		pass
	

	def ledLvlAll(self, msg=None):
		pass
	

	def ledLvlMap(self, msg=None):
		pass
	

	def ledLvlRow(self, msg=None):
		pass
	

	def ledLvlCol(self, msg=None):
		pass
	

	def ledClear(self, msg=None):
		self.receive_grid_all(0)
	

	def led_col(self, msg=None):
		if len(msg) > 2:
			xOff = int(msg[2])
			cols = msg[3:]
			for quad in range(len(cols)):
				colOut = self.int2bin(cols[quad])
				for cell in range(8):
					self.receive_grid(xOff+QUADS[quad][0], cell+QUADS[quad][1], colOut[cell])

	

	def led_row(self, msg=None):
		if len(msg) > 2:
			yOff = int(msg[2])
			rows = msg[3:]
			for quad in range(len(rows)):
				rowOut = self.int2bin(rows[quad])
				for cell in range(8):
					self.receive_grid(cell+QUADS[quad][0], yOff+QUADS[quad][1], rowOut[cell])

	

	def _display_info(self, inPrt, outPrt):
		self._host.show_message('Preset: ' + str(PRESETS[self._channel][3]) + ' In: ' + str(inPrt) + ' Out: ' + str(outPrt) + ' Format: ' + str(MODES[self._format]) + ' Pre: ' + str(self._prefix))
	

	def _change_ports(self, ports):
		self._host.log_message('ports ' + str(ports))
		inPrt = self._inPrt
		outPrt = self._outPrt
		if len(ports[0]) > 0:
			str_inPrt = ''.join(ports[0]).strip('\'')
			inPrt = str_inPrt
		inPrt = int(inPrt)
		if len(ports[1]) > 0:
			str_outPrt = ''.join(ports[1]).strip('\'')
			outPrt = str_outPrt
		outPrt = int(outPrt)
		if inPrt in range(0,65535) and outPrt in range(0,65535):
			if not (self._outPrt == outPrt):
				self._outPrt = outPrt
				PRESETS[self._channel][2][1] = str(self._outPrt)
			if not (self._inPrt == inPrt):
				self._inPrt = inPrt
				self.unregister()
				PRESETS[self._channel][2][0] = str(self._inPrt)
				self._host.schedule_message(15, self._setup_oscServer)
			else:
				self.oscServer.set_outPort(self._outPrt)
	

	def _change_modes(self, value):
		self._format = value
		self._assign_sys_callbacks()
	

	def int2bin(self, n):
		return [((n >> y) & 1) for y in range(8)]
	


#self.device = self._host.song().view.selected_track.view.selected_device

