# by amounra 0413 : http://www.aumhaa.com

from __future__ import with_statement

import contextlib
from _Framework.Util import product

from _Framework.EncoderElement import EncoderElement 
from _Framework.SubjectSlot import SubjectEvent
from _Framework.Signal import Signal
from _Framework.NotifyingControlElement import NotifyingControlElement
from _Framework.Util import in_range
from _Framework.Debug import debug_print
from _Framework.Disconnectable import Disconnectable
from _Framework.ButtonMatrixElement import ButtonMatrixElement

class InputSignal(Signal):
	"""
	Special signal type that makes sure that interaction with input
	works properly. Special input control elements that define
	value-dependent properties should use this kind of signal.
	"""

	def __init__(self, sender = None, *a, **k):
		super(InputSignal, self).__init__(sender=sender, *a, **k)
		self._input_control = sender

	@contextlib.contextmanager
	def _listeners_update(self):
		old_count = self.count
		yield
		diff_count = self.count - old_count
		self._input_control._input_signal_listener_count += diff_count
		listener_count = self._input_control._input_signal_listener_count
		#if diff_count > 0 and listener_count == diff_count or diff_count < 0 and listener_count == 0:
		#	self._input_control._request_rebuild()

	def connect(self, *a, **k):
		with self._listeners_update():
			super(InputSignal, self).connect(*a, **k)

	def disconnect(self, *a, **k):
		with self._listeners_update():
			super(InputSignal, self).disconnect(*a, **k)

	def disconnect_all(self, *a, **k):
		with self._listeners_update():
			super(InputSignal, self).disconnect_all(*a, **k)

class EncoderMatrixElement(NotifyingControlElement):
	' Class representing a 2-dimensional set of buttons '


	def __init__(self, script, *a, **k):
		super(EncoderMatrixElement, self).__init__(*a, **k)
		self._script = script
		self._dials = []
		self._dial_coordinates = {}
		self._max_row_width = 0


	def disconnect(self):
		NotifyingControlElement.disconnect(self)
		self._dials = None
		self._dial_coordinates = None


	def add_row(self, dials):
		assert (dials != None)
		assert isinstance(dials, tuple)
		index = 0
		for dial in dials:
			assert (dial != None)
			assert isinstance(dial, EncoderElement)
			assert (dial not in self._dial_coordinates.keys())
			dial.add_value_listener(self._dial_value, identify_sender=True)
			self._dial_coordinates[dial] = (index,
			 len(self._dials))
			index += 1

		if (self._max_row_width < len(dials)):
			self._max_row_width = len(dials)
		self._dials.append(dials)


	def width(self):
		return self._max_row_width


	def height(self):
		return len(self._dials)


	def send_value(self, column, row, value, force = False):
		assert (value in range(128))
		assert (column in range(self.width()))
		assert (row in range(self.height()))
		if (len(self._dials[row]) > column):
			self._dials[row][column].send_value(value, force)


	def get_dial(self, column, row):
		assert (column in range(self.width()))
		assert (row in range(self.height()))
		dial = None
		if (len(self._dials[row]) > column):
			dial = self._dials[row][column]
		return dial


	def reset(self):
		for dial_row in self._dials:
			for dial in dial_row:
				dial.send_value(0, True)
		#for dial in self._dials:
		#	dial.reset()

	def _dial_value(self, value, sender):
		assert isinstance(value, int)
		assert (sender in self._dial_coordinates.keys())
		assert isinstance(self._dial_coordinates[sender], tuple)
		coordinates = tuple(self._dial_coordinates[sender])
		self.notify_value(value, coordinates[0], coordinates[1])
		"""for entry in self._value_notifications:
			callback = entry['Callback']
			callback(value, coordinates[0], coordinates[1])"""
	

class NewEncoderMatrixElement(ButtonMatrixElement):
	' Class representing a 2-dimensional set of buttons '


	def __init__(self, script, *a, **k):
		super(NewEncoderMatrixElement, self).__init__(*a, **k)
		self._script = script
		self._dials = []
		self._dial_coordinates = {}
		self._max_row_width = 0


	def disconnect(self):
		super(NewEncoderMatrixElement, self).disconnect()
		self._dials = None
		self._dial_coordinates = None
	

	def get_dial(self, *a, **k):
		self.get_button(self, *a, **k)
	

	def _dial_value(self, value, sender):
		assert isinstance(value, int)
		assert (sender in self._dial_coordinates.keys())
		assert isinstance(self._dial_coordinates[sender], tuple)
		coordinates = tuple(self._dial_coordinates[sender])
		self.notify_value(value, coordinates[0], coordinates[1])
	

	def xiterbuttons(self):
		for i, j in product(xrange(self.width()), xrange(self.height())):
			button = self.get_button(i, j)
			yield (button, (i, j))
	

