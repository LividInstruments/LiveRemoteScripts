# by amounra 0115 : http://www.aumhaa.com

import Live

#from _Framework.ControlSurface import ControlSurface
from ableton.v2.control_surface import ControlSurface

#from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from ableton.v2.control_surface.component import Component

import modRemixNet as RemixNet
import modOSC

from aumhaa.v2.base.debug import *

debug = initialize_debug()

class OSCDisplay(Component):


	def __init__(self, prefix = '/Live/0', model_name = 'ControlSurface', model = ControlSurface, outport = 10001, *a, **k):
		super(OSCDisplay, self).__init__(*a, **k)
		self._prefix = prefix
		self._outPrt = outport
		self._OSC_id = 0
		if hasattr(__builtins__, 'control_surfaces') or (isinstance(__builtins__, dict) and 'control_surfaces' in __builtins__.keys()):
			for cs in __builtins__['control_surfaces']:
				if cs is self:
					break
				elif isinstance(cs, model):
					self._OSC_id += 1
		self._prefix = prefix + '/' +str(model_name) + '/' + str(self._OSC_id) + '/'
		self._outPrt = outport
		hasattr(self, 'oscServer') and self.oscServer.shutdown()
		self.oscServer = RemixNet.OSCServer('localhost', self._outPrt, 'localhost', 10001)
	

	def disconnect(self):
		self.oscServer and self.oscServer.shutdown()
		super(OSCDisplay, self).disconnect()
	

	def sendOSC(self, suffix, message):
		#debug('sendOSC', suffix, message)
		try:
			self.is_enabled() and self.oscServer and self.oscServer.sendOSC(str(self._prefix+suffix), str(message))
		except:
			pass
	