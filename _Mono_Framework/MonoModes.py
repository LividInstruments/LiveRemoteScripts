# by amounra 0814 : http://www.aumhaa.com

from _Framework.ModesComponent import *
from Debug import *

debug = initialize_debug()


class SendSysexMode(Mode):


	def __init__(self, script = None, sysex = None, *a, **k):
		super(SendSysexMode, self).__init__(*a, **k)
		self._send_midi = script._send_midi
		self._sysex = sysex
	

	def enter_mode(self):
		self._send_midi and self._send_midi(self._sysex)
	

	def leave_mode(self):
		pass
	


class DisplayMessageMode(Mode):


	def __init__(self, script = None, message = None, *a, **k):
		super(DisplayMessageMode, self).__init__(*a, **k)
		self._show_message = script.show_message
		self._message = message
	

	def enter_mode(self):
		self._show_message and self._message and self._show_message(self._message)
	

	def leave_mode(self):
		pass
	


class SendLividSysexMode(Mode):


	def __init__(self, livid_settings = None, call = None, message = None, *a, **k):
		super(SendLividSysexMode, self).__init__(*a, **k)
		self._send = livid_settings.send if hasattr(livid_settings, 'send') else self.fallback_send
		self._call = call
		self._message = message
	

	def fallback_send(self, call = 'no call', message = 'no message', *a, **k):
		debug('sysex call made to invalid livid_settings object:', call, message)
	

	def enter_mode(self):
		self._send(self._call, self._message)
	

	def leave_mode(self):
		pass
	

class MomentaryBehaviour(ModeButtonBehaviour):


	def press_immediate(self, component, mode):
		component.push_mode(mode)
	

	def release_immediate(self, component, mode):
		if len(component.active_modes) > 1:
			component.pop_mode(mode)
	

	def release_delayed(self, component, mode):
		if len(component.active_modes) > 1:
			component.pop_mode(mode)
	


class ExcludingMomentaryBehaviour(ExcludingBehaviourMixin, MomentaryBehaviour):


	def update_button(self, *a, **k):
		pass
	


class DelayedExcludingMomentaryBehaviour(ExcludingMomentaryBehaviour):


	def press_immediate(self, component, mode):
		pass
	

	def press_delayed(self, component, mode):
		component.push_mode(mode)
	


class CancellableBehaviourWithRelease(CancellableBehaviour):


	def release_delayed(self, component, mode):
		component.pop_mode(mode)
	


class ShiftedBehaviour(ModeButtonBehaviour):


	def __init__(self, color = 1, *a, **k):
		super(ShiftedBehaviour, self).__init__(*a, **k)
		self._color = color
		self._chosen_mode = None
	

	def press_immediate(self, component, mode):
		debug('selected_mode:', component.selected_mode, 'mode:', mode, 'chosen_mode:', self._chosen_mode,)
		if mode is component.selected_mode and not component.get_mode(mode+'_shifted') is None:
			self._chosen_mode = mode+'_shifted'
		else:
			self._chosen_mode = mode
		component.push_mode(self._chosen_mode)
	

	def release_immediate(self, component, mode):
		debug('chosen mode is:', self._chosen_mode)
		if component.selected_mode.endswith('_shifted'):
			component.pop_groups(['shifted'])
		elif len(component.active_modes) > 1:
			component.pop_unselected_modes()
	

	def release_delayed(self, component, mode):
		debug('chosen mode is:', self._chosen_mode)
		component.pop_mode(self._chosen_mode)
	

	def update_button(self, component, mode, selected_mode):
		button = component.get_mode_button(mode)
		groups = component.get_mode_groups(mode)
		selected_groups = component.get_mode_groups(selected_mode)
		#debug('--------mode:', mode, 'selected:', selected_mode, 'chosen:', self._chosen_mode)
		if mode == selected_mode:
			button.send_value(self._color, True)
		elif mode+'_shifted' == selected_mode:
			button.send_value(self._color + 7, True)
		else:
			button.send_value(0, True)
	


class LatchingShiftedBehaviour(ShiftedBehaviour):


	def press_immediate(self, component, mode):
		#debug('mode button for ->', mode, 'currently selected_mode:', component.selected_mode, 'last chosen mode:', self._chosen_mode)
		if mode is component.selected_mode and component.get_mode(mode+'_shifted'):
			self._chosen_mode = mode+'_shifted'
		#elif (component.selected_mode != mode + '_shifted') and (self._chosen_mode != mode + '_shifted'):
		#	component.pop_groups(['shifted'])
		#	self._chosen_mode = mode
		else:
			self._chosen_mode = mode
		component.push_mode(self._chosen_mode)
		debug('new chosen_mode:', self._chosen_mode,)
	

	def release_immediate(self, component, mode):
		if len(component.active_modes) > 1:
			component.pop_unselected_modes()
		#debug('selected mode:', component.selected_mode)
	

	def release_delayed(self, component, mode):
		if not mode is self._chosen_mode is mode + '_shifted':
			if len(component.active_modes) > 1:
				component.pop_mode(component.selected_mode)
		#debug('selected mode:', component.selected_mode)
	


class FlashingBehaviour(CancellableBehaviourWithRelease):


	def __init__(self, color = 1, *a, **k):
		super(FlashingBehaviour, self).__init__(*a, **k)
		self._color = color
	

	def update_button(self, component, mode, selected_mode):
		button = component.get_mode_button(mode)
		groups = component.get_mode_groups(mode)
		selected_groups = component.get_mode_groups(selected_mode)
		if mode == selected_mode or bool(groups & selected_groups):
			button.send_value(self._color + 7, True)
		else:
			button.send_value(self._color, True)
	


class CancellableBehaviourWithRelease(CancellableBehaviour):


	def release_delayed(self, component, mode):
		component.pop_mode(mode)
	

	def update_button(self, component, mode, selected_mode):
		button = component.get_mode_button(mode)
		groups = component.get_mode_groups(mode)
		selected_groups = component.get_mode_groups(selected_mode)
		value = (mode == selected_mode or bool(groups & selected_groups))*32 or 1
		button.send_value(value, True)
	


class ColoredCancellableBehaviourWithRelease(CancellableBehaviourWithRelease):


	def __init__(self, color = 'ButtonDefault.On', off_color = 'ButtonDefault.Off', *a, **k):
		super(ColoredCancellableBehaviourWithRelease, self).__init__(*a, **k)
		self._color = color
		self._off_color = off_color
	

	def update_button(self, component, mode, selected_mode):
		button = component.get_mode_button(mode)
		groups = component.get_mode_groups(mode)
		selected_groups = component.get_mode_groups(selected_mode)
		if mode == selected_mode:
			button.set_light(self._color)
		else:
			button.set_light(self._off_color)
	


class BicoloredMomentaryBehaviour(MomentaryBehaviour):


	def __init__(self, color = 'DefaultButton.On', off_color = 'DefaultButton.Off', *a, **k):
		super(BicoloredMomentaryBehaviour, self).__init__(*a, **k)
		self._color = color
		self._off_color = off_color
	

	def update_button(self, component, mode, selected_mode):
		button = component.get_mode_button(mode)
		groups = component.get_mode_groups(mode)
		selected_groups = component.get_mode_groups(selected_mode)
		if mode == selected_mode:
			button.set_light(self._color)
		else:
			button.set_light(self._off_color)
	


class DefaultedBehaviour(ColoredCancellableBehaviourWithRelease):


	def __init__(self, default_mode = 'disabled', *a, **k):
		super(DefaultedBehaviour, self).__init__(*a, **k)
		self._default_mode = default_mode
	

	def press_immediate(self, component, mode):
		if mode is component.selected_mode:
			mode = self._default_mode
		component.push_mode(mode)
	

	def release_immediate(self, component, mode):
		if len(component.active_modes) > 1:
			component.pop_unselected_modes()
	

	def release_delayed(self, component, mode):
		component.pop_mode(mode)
	
