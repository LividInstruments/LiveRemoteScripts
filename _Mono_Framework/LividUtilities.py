# by amounra 0814 : http://www.aumhaa.com

from Debug import *

debug = initialize_debug()

LIVID_RGB_COLORMAP = [2, 64, 4, 8, 16, 127, 32]

QUERYSURFACE = (240, 126, 127, 6, 1, 247)

CALLS = {'set_streaming_enabled':62,
		'set_function_button_leds_linked':68,
		'set_capacitive_fader_note_output_enabled':69,
		'set_fader_led_colors':61,
		'set_pad_output_type':66,
		'set_local_control':8,
		'set_pad_pressure_output_type':10,
		'set_encoder_mapping':11,
		'set_encoder_encosion_mode':17}

def fallback_send_midi(message = None, *a, **k):
	debug('control surface not assigned to the sysex call:', message);


def get_call_type(call_type):
	#debug('call type is:', call_type)
	if call_type in CALLS:
		return [CALLS[call_type]]
	else:
		return False



class LividSettings(object):

	def __init__(self, prefix = [240, 0, 1, 97], model = None, control_surface = None, *a, **k):
		super(LividSettings, self).__init__()
		self._prefix = prefix
		self._model = [model]
		self._send_midi = control_surface._send_midi if control_surface else fallback_send_midi
		for keyword, value in k.iteritems():
			setattr(self, keyword, value)
	

	def query_surface(self):
		self._send_midi(QUERYSURFACE)
	

	def set_model(self, model):
		self._model = [model]
	

	def send(self, call = None, message = [], *a, **k):
		call = get_call_type(call)
		if call:
			message = self._prefix + self._model + call + message + [247]
			self._send_midi(tuple(message))
		else:
			debug(call, 'is not a valid lividsettings call')
	









