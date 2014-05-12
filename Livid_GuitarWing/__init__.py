# by amounra 0314 : http://www.aumhaa.com

from GuitarWing import GuitarWing
from _Framework.Capabilities import controller_id, inport, outport, CONTROLLER_ID_KEY, PORTS_KEY, HIDDEN, NOTES_CC, SCRIPT, REMOTE, SYNC, TYPE_KEY, FIRMWARE_KEY, AUTO_LOAD_KEY


def get_capabilities():
	return {CONTROLLER_ID_KEY: controller_id(vendor_id=2536, product_ids=[115], model_name='Livid Instruments GuitarWing'),
	 PORTS_KEY: [inport(props=[HIDDEN, NOTES_CC, SCRIPT, REMOTE]), 
					inport(props = []),
					outport(props=[HIDDEN, NOTES_CC, SCRIPT, REMOTE]),
					outport(props=[])],
	 TYPE_KEY: 'push',
	 AUTO_LOAD_KEY: False}


def create_instance(c_instance):
	""" Creates and returns the GuitarWing script """
	return GuitarWing(c_instance)

