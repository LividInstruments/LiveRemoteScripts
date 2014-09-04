# by amounra 0413 : http://www.aumhaa.com

import Live
from _Framework.EncoderElement import EncoderElement
from _Framework.InputControlElement import InputControlElement
from _Framework.NotifyingControlElement import NotifyingControlElement

MIDI_NOTE_TYPE = 0
MIDI_CC_TYPE = 1
MIDI_PB_TYPE = 2
MIDI_MSG_TYPES = (MIDI_NOTE_TYPE,
 MIDI_CC_TYPE,
 MIDI_PB_TYPE)
MIDI_NOTE_ON_STATUS = 144
MIDI_NOTE_OFF_STATUS = 128
MIDI_CC_STATUS = 176
MIDI_PB_STATUS = 224

class MonoEncoderElement(EncoderElement):
	__module__ = __name__
	__doc__ = ' Class representing a slider on the controller '

	def __init__(self, msg_type, channel, identifier, map_mode, name, num, script, mapping_feedback_delay = 1, *a, **k):
		super(MonoEncoderElement, self).__init__(msg_type, channel, identifier, map_mode=Live.MidiMap.MapMode.absolute, *a, **k)
		self._mapping_feedback_delay = mapping_feedback_delay
		self.name = name
		self.num = num
		self._parameter = None
		self._script = script
		self._is_enabled = True
		self._paramter_lcd_name = ' '
		self._parameter_last_value = None
		self._mapped_to_midi_velocity = False
		self.set_report_values(True, False)
	

	def _report_value(self, value, is_input):
		self._script.touched()
	

	def disconnect(self):
		self.remove_parameter_listener(self._parameter)
		super(MonoEncoderElement, self).disconnect()
	

	def connect_to(self, parameter):
		self._mapped_to_midi_velocity = False
		assignment = parameter
		if(str(parameter.name) == str('Track Volume')):		#checks to see if parameter is track volume
			if(parameter.canonical_parent.canonical_parent.has_audio_output is False):		#checks to see if track has audio output
				if(len(parameter.canonical_parent.canonical_parent.devices) > 0):
					if(str(parameter.canonical_parent.canonical_parent.devices[0].class_name)==str('MidiVelocity')):	#if not, looks for velicty as first plugin
						assignment = parameter.canonical_parent.canonical_parent.devices[0].parameters[6]				#if found, assigns fader to its 'outhi' parameter
						self._mapped_to_midi_velocity = True
		if not self._parameter_to_map_to is assignment:
			self.send_value(0, True)
		super(MonoEncoderElement, self).connect_to(assignment)
		self.add_parameter_listener(self._parameter_to_map_to)
	

	def set_enabled(self, enabled):
		self._is_enabled = enabled
		self._request_rebuild()

	def set_value(self, value):
		if(self._parameter_to_map_to != None):
			newval = float(value * (self._parameter_to_map_to.max - self._parameter_to_map_to.min)) + self._parameter_to_map_to.min
			self._parameter_to_map_to.value = newval
			return [value, str(self.mapped_parameter())]
		else:
			self.receive_value(int(value*127))
	

	def release_parameter(self):
		if(self._parameter_to_map_to != None):
			self.remove_parameter_listener(self._parameter_to_map_to)
		super(MonoEncoderElement, self).release_parameter()
	

	def script_wants_forwarding(self):
		if not self._is_enabled:
			return False
		else:
			return super(MonoEncoderElement, self).script_wants_forwarding()
	

	def forward_parameter_value(self):
		if(not (type(self._parameter) is type(None))):
			#new_value=int(((self._parameter.value - self._parameter.min) / (self._parameter.max - self._parameter.min))  * 127)
			try:
				parameter = str(self.mapped_parameter())
			except:
				parameter = ' '
			if(parameter!=self._parameter_last_value):
				#self._parameter_last_value = str(self.mapped_parameter())
				try:
					self._parameter_last_value = str(self.mapped_parameter())
				except:
					self._parameter_last_value = ' '
				self._script.notification_to_bridge(self._parameter_lcd_name, self._parameter_last_value, self)
	

	def add_parameter_listener(self, parameter):
		self._parameter = parameter
		if parameter:
			if isinstance(parameter, Live.DeviceParameter.DeviceParameter):
				if str(parameter.original_name) == 'Track Volume' or self._mapped_to_midi_velocity is True:
					try:
						self._parameter_lcd_name = str(parameter.canonical_parent.canonical_parent.name)
					except:
						self._parameter_lcd_name = ' '
				elif str(parameter.original_name) == 'Track Panning':
					self._parameter_lcd_name = 'Pan'
				else:
					try:
						self._parameter_lcd_name = str(parameter.name)
					except:
						self._parameter_lcd_name = ' '
			#self._last_value(int(((self._parameter.value - self._parameter.min) / (self._parameter.max - self._parameter.min))  * 127))
			#self._parameter_last_value = str(self.mapped_parameter())
			try:
				self._parameter_last_value = str(self.mapped_parameter())
			except:
				self._parameter_last_value = ' '
			self._script.notification_to_bridge(self._parameter_lcd_name, self._parameter_last_value, self)
			cb = lambda: self.forward_parameter_value()
			parameter.add_value_listener(cb)
	

	def remove_parameter_listener(self, parameter):
		self._parameter = None
		#self._script.log_message('remove_parameter_listener ' + str(parameter.name + str(self.name)))
		if parameter:
			cb = lambda: self.forward_parameter_value()
			if(parameter.value_has_listener is True):
				parameter.remove_value_listener(cb)
			self._parameter_lcd_name = ' '
			self._parameter_last_value = ' '
			self._script.notification_to_bridge(' ', ' ', self)
	
