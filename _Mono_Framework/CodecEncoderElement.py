# by amounra 0413 : http://www.aumhaa.com

import Live
from _Framework.EncoderElement import EncoderElement
from _Framework.InputControlElement import InputControlElement
from _Framework.NotifyingControlElement import NotifyingControlElement
from _Framework.SubjectSlot import subject_slot, subject_slot_group

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
output = []
setledringindicators = (240, 0, 1, 97, 8, 32, output, 247)
localringcontrol = (240, 0, 1, 97, 8, 32, output, 247)

WALK = [[0, 0], [1, 0], [2, 0], [4, 0], [8, 0], [16, 0], [32, 0], [64, 0], [0, 1], [0, 2], [0, 4], [0, 8], [0, 16]]  ##, [0, 64]]
FILL = [[0, 0], [1, 0], [3, 0], [7, 0], [15, 0], [31, 0], [63, 0], [127, 0], [127, 1], [127, 3], [127, 7], [127, 15], [127, 31], [127, 63]]
CENTER =  [[127, 0], [126, 0], [124, 0], [120, 0], [112, 0], [96, 0], [64, 0], [64, 1], [64, 3], [64, 7], [64, 15], [64, 31], [64, 63]]
SPREAD =  [[1, 64], [3, 96], [7, 112], [15, 120], [31, 124], [63, 126], [127, 127], [126, 63], [124, 31], [127, 63], [127, 31], [127, 7], [96, 3], [64, 1]]
RING_MODE = [WALK, FILL, CENTER, SPREAD];

class CodecEncoderElement(EncoderElement):
	__module__ = __name__
	__doc__ = ' Class representing an encoder on the Livid Code controller '


	def __init__(self, msg_type, channel, identifier, map_mode, name, num, script, mapping_feedback_delay = 1, *a, **k):
		super(CodecEncoderElement, self).__init__(msg_type, channel, identifier, map_mode, *a, **k)
		self._mapping_feedback_delay = mapping_feedback_delay
		self._script = script
		self.name = name
		self.num = num
		self._parameter = None
		self._ring_mode = 0
		self._ring_value = 0
		self._raw_custom = None
		self._ring_custom = [[0, 0]]
		self._ring_green = 0
		self._is_enabled = True
		self._paramter_lcd_name = ' '
		self._parameter_last_value = None
		self._parameter_last_num_value = 0
		self._mapped_to_midi_velocity = False
		self.set_report_values(True, False)

		#remove when relative mode has been fixed
		self._last_received = -1
	

	def reset(self, force = False):
		self.force_next_send()
		self.send_value(0)
	

	def _reset_to_center(self):
		self._last_received = 64
		self.send_value(64, True)
	

	def _report_value(self, value, is_input):
		self._script.touched()
	

	def disconnect(self):
		self.remove_parameter_listener(self._parameter)
		EncoderElement.disconnect(self)
	

	def change_ring_mode(self, mode):
		#deprecated
		self._ring_mode = mode
	

	def set_ring_value(self, val):
		#deprecated
		self._ring_value = val
	

	def ring_mode(self):
		return self._ring_mode
	

	def set_custom(self, val):
		self._ring_custom = self._calculate_custom(''.join([str(i) for i in val]))
	

	def set_green(self, val, *a):
		self._ring_green = int(val>0)
	

	def set_mode(self, val, *a):
		self._ring_mode = val
	

	def _calculate_custom(self, ring_leds):
		self._raw_custom = str(ring_leds)
		custom = [[0, 0] for index in range(len(ring_leds))]
		for index in range(len(ring_leds)):
			led_ring = ring_leds[index:] + ring_leds[:index] + '0000000000000'
			byte1 = (led_ring[0:7])[::-1]
			#self._script.log_message(str(byte1) + str(type(byte1)) + str(int(byte1, 2)))
			#byte2 = (led_ring[7:10] + `0` + led_ring[10:12])[::-1]
			byte2 = (led_ring[7:12])[::-1]
			custom[index][0] = int(byte1, 2)
			custom[index][1] = int(byte2, 2)
		return custom
	

	def _get_ring(self):
		if self._ring_mode < 4:
			mode = RING_MODE[self._ring_mode]
			length = len(mode)
			byte1 = mode[self._ring_value % length][0]
			byte2 = mode[self._ring_value % length][1]
			bytes = [byte1, byte2]
		elif self._ring_mode == 5:
			mode = RING_MODE[0]
			length = max(0, len(mode)-1)
			byte1 = mode[int(self._parameter_last_num_value*length)][0]
			byte2 = mode[int(self._parameter_last_num_value*length)][1]
			bytes = [byte1, byte2]
		else:
			bytes = self._ring_custom[self._ring_value % len(self._ring_custom)]
		bytes.append(self._ring_green * 32)
		return bytes
	


	def set_value(self, value):
		if(self._parameter_to_map_to != None):
			if(self._parameter_to_map_to.is_enabled):
				newval = float(float(float(value)/127) * (self._parameter_to_map_to.max - self._parameter_to_map_to.min)) + self._parameter_to_map_to.min
				self._parameter_to_map_to.value = newval
		else:
			self.receive_value(int(value))
	


	def connect_to(self, parameter):
		if parameter == None:
			self.release_parameter()
		else:
			self._mapped_to_midi_velocity = False
			assignment = parameter
			try:
				if(str(parameter.name) == str('Track Volume')):		#checks to see if parameter is track volume
					if(parameter.canonical_parent.canonical_parent.has_audio_output is False):		#checks to see if track has audio output
						if(len(parameter.canonical_parent.canonical_parent.devices) > 0):
							if(str(parameter.canonical_parent.canonical_parent.devices[0].class_name)==str('MidiVelocity')):	#if not, looks for velicty as first plugin
								assignment = parameter.canonical_parent.canonical_parent.devices[0].parameters[6]				#if found, assigns fader to its 'outhi' parameter
								self._mapped_to_midi_velocity = True
			except:
				assignment = parameter
			if not self._parameter_to_map_to is assignment:
				self.send_value(0, True)
			super(CodecEncoderElement, self).connect_to(assignment)
			self.add_parameter_listener(self._parameter_to_map_to)
			if(not (type(self._parameter) is type(None))):
				self._parameter_last_num_value = (self._parameter.value - self._parameter.min) / (self._parameter.max - self._parameter.min)
	

	def release_parameter(self):
		if(self._parameter_to_map_to != None):
			self.remove_parameter_listener(self._parameter_to_map_to)
		self.send_value(0, True)
		InputControlElement.release_parameter(self)
		self._parameter_last_num_value = 0
		#self._parameter_to_map_to = None
	

	def script_wants_forwarding(self):
		if not self._is_enabled:
			return False
		else:
			return InputControlElement.script_wants_forwarding(self)
	

	def set_enabled(self, enabled):
		self._is_enabled = enabled
		self._request_rebuild()
	

	def forward_parameter_value(self):
		if(not (type(self._parameter) is type(None))):
			self._parameter_last_num_value = (self._parameter.value - self._parameter.min) / (self._parameter.max - self._parameter.min)
			try:
				parameter = str(self.mapped_parameter())
			except:
				parameter = ' '
			if(parameter!=self._parameter_last_value):
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
					self._parameter_lcd_name = str(parameter.canonical_parent.canonical_parent.name)
				elif str(parameter.original_name) == 'Track Panning':
					self._parameter_lcd_name = 'Pan'
				else:
					self._parameter_lcd_name = str(parameter.name)
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
	

	def decode_parameter_value(self):
		val = str(self.mapped_parameter)
		return val
	

