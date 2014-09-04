# by amounra 0814 : http://www.aumhaa.com

from __future__ import absolute_import, with_statement
from _Framework.ControlElement import ControlElementClient
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent

#from Debug import *

#debug = initialize_debug()


class MonoM4LInterfaceComponent(ControlSurfaceComponent, ControlElementClient):
	"""
	Simplified API for interaction from M4L as a high priority layer
	superposed on top of any functionality.
	"""


	def __init__(self, controls = None, component_guard = None, priority = 1, *a, **k):
		super(MonoM4LInterfaceComponent, self).__init__(self, *a, **k)
		self._priority = priority
		self._controls = dict(map(lambda x: (x.name, x), controls))
		self._grabbed_controls = []
		self._component_guard = component_guard
	

	def disconnect(self):
		for control in self._grabbed_controls[:]:
			self.release_control(control)
		super(MonoM4LInterfaceComponent, self).disconnect()
	

	def set_control_element(self, control, grabbed):
		if hasattr(control, 'release_parameter'):
			control.release_parameter()
		control.reset()
	

	def get_control_names(self):
		return self._controls.keys()
	

	def get_control(self, control_name):
		return self._controls[control_name] if control_name in self._controls else None
	

	def grab_control(self, control):
		assert(control in self._controls.values())
		with self._component_guard():
			if control not in self._grabbed_controls:
				control.resource.grab(self, priority=self._priority)
				self._grabbed_controls.append(control)
	

	def release_control(self, control):
		assert(control in self._controls.values())
		with self._component_guard():
			if control in self._grabbed_controls:
				self._grabbed_controls.remove(control)
				control.resource.release(self)
	
