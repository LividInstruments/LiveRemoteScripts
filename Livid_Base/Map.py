
"""
Base_Map.py

Created by amounra on 2014-7-26.

This file allows the reassignment of the controls from their default arrangement.  The order is from left to right; 
Buttons are Note #'s and Faders/Rotaries are Controller #'s
"""
OSC_TRANSMIT = False

OSC_OUTPORT = 9001

SHIFT_LATCHING = False

CHANNEL = 0		#main channel (0 - 15)

AFTERTOUCH = True   #when True, sends AT in instrument modes and UserMode.  When false, turns CC's off for instrument modes and transmits CC's in UserModes.

BASE_PADS = [60, 61, 62, 63, 64, 65, 66, 67, 52, 53, 54, 55, 56, 57, 58, 59, 44, 45, 46, 47, 48, 49, 50, 51, 36, 37, 38, 39, 40, 41, 42, 43]	#there are 16 of these

BASE_TOUCHSTRIPS = [1, 2, 3, 4, 5, 6, 7, 8, 9]		#there are 9 of these

BASE_TOUCHPADS = [10, 11, 12, 13, 14, 15, 16, 17]

BASE_BUTTONS = [18, 19, 20, 21, 22, 23, 24, 25]		#there are 16 of these

BASE_RUNNERS = [68, 69, 70, 71, 72, 73, 74, 75]

BASE_LCDS = [34, 35]

COLOR_MAP = [2, 64, 4, 8, 16, 127, 32]

"""You can change the orientation of the Up, Down, Left, and Right buttons (where applicable) by changing the array.  The values correspond to the buttons from top to bottom."""
UDLR = [0, 1, 2, 3]

"""The values in this array determine the choices for what length of clip is created when "Fixed Length" is turned on:
0 = 1 Beat
1 = 2 Beat
2 = 1 Bar
3 = 2 Bars
4 = 4 Bars
5 = 8 Bars
6 = 16 Bars
7 = 32 Bars
"""
LENGTH_VALUES = [2, 3, 4]

"""It is possible to create a custom list of scales to be used by the script.  For instance, the list below would include major, minor, auto, drumpad, and chromatic scales, in that order."""
#SCALENAMES = ['Major', 'Minor', 'Auto', 'DrumPad', 'Chromatic']

from _Framework.ButtonElement import Color
from _Mono_Framework.LividColors import *

class BaseColors:


	class DefaultButton:
		On = LividRGB.WHITE
		Off = LividRGB.OFF
		Disabled = LividRGB.OFF
		Alert = LividRGB.BlinkFast.WHITE
	

	class Session:
		StopClipTriggered = LividRGB.BlinkFast.BLUE
		StopClip = LividRGB.BLUE
		Scene = LividRGB.CYAN
		NoScene = LividRGB.OFF
		SceneTriggered = LividRGB.BlinkFast.BLUE
		ClipTriggeredPlay = LividRGB.BlinkFast.GREEN
		ClipTriggeredRecord = LividRGB.BlinkFast.RED
		RecordButton = LividRGB.OFF
		ClipStopped = LividRGB.WHITE
		ClipStarted = LividRGB.GREEN
		ClipRecording = LividRGB.RED
		NavigationButtonOn = LividRGB.BLUE
	

	class NoteEditor:

		class Step:
			Low = LividRGB.CYAN
			High = LividRGB.WHITE 
			Full = LividRGB.YELLOW
			Muted = LividRGB.YELLOW
			StepEmpty = LividRGB.OFF
		

		class StepEditing:
			High = LividRGB.GREEN
			Low = LividRGB.CYAN
			Full = LividRGB.YELLOW
			Muted = LividRGB.WHITE
		

		StepEmpty = LividRGB.OFF
		StepEmptyBase = LividRGB.OFF
		StepEmptyScale = LividRGB.OFF
		StepDisabled = LividRGB.OFF
		Playhead = Color(31)
		PlayheadRecord = Color(31)
		StepSelected = LividRGB.GREEN
		QuantizationSelected = LividRGB.RED
		QuantizationUnselected = LividRGB.MAGENTA
	

	class LoopSelector:
		Playhead = LividRGB.YELLOW
		OutsideLoop = LividRGB.BLUE
		InsideLoopStartBar = LividRGB.CYAN
		SelectedPage = LividRGB.WHITE
		InsideLoop = LividRGB.CYAN
		PlayheadRecord = LividRGB.RED
	

	class DrumGroup:
		PadAction = LividRGB.WHITE
		PadFilled = LividRGB.GREEN
		PadSelected = LividRGB.WHITE
		PadSelectedNotSoloed = LividRGB.WHITE
		PadEmpty = LividRGB.OFF
		PadMuted = LividRGB.YELLOW
		PadSoloed = LividRGB.CYAN
		PadMutedSelected = LividRGB.BLUE
		PadSoloedSelected = LividRGB.BLUE
		PadInvisible = LividRGB.OFF
		PadAction = LividRGB.RED
	

	class Mixer:
		SoloOn = LividRGB.CYAN
		SoloOff = LividRGB.OFF
		MuteOn = LividRGB.YELLOW
		MuteOff = LividRGB.OFF
		ArmSelected = LividRGB.GREEN
		ArmUnselected = LividRGB.RED
		ArmOff = LividRGB.OFF
		StopClip = LividRGB.BLUE
		SelectedOn = LividRGB.BLUE
		SelectedOff = LividRGB.OFF
	

	class Recording:
		Transition = LividRGB.BlinkSlow.GREEN
	

	class Recorder:
		On = LividRGB.WHITE
		Off = LividRGB.BLUE
		NewOn = LividRGB.BlinkFast.YELLOW
		NewOff = LividRGB.YELLOW
		FixedOn = LividRGB.BlinkFast.CYAN
		FixedOff = LividRGB.CYAN
		RecordOn = LividRGB.BlinkFast.GREEN
		RecordOff = LividRGB.GREEN
		FixedAssigned = LividRGB.MAGENTA
		FixedNotAssigned = LividRGB.OFF
	

	class Transport:
		OverdubOn = LividRGB.BlinkFast.RED
		OverdubOff = LividRGB.RED
	

	class Sequencer:
		OctaveOn = LividRGB.BlinkFast.CYAN
		OctaveOff = LividRGB.OFF
		On = LividRGB.WHITE
		Off = LividRGB.OFF
	

	class Device:
		NavOn = LividRGB.MAGENTA
		NavOff = LividRGB.OFF
		BankOn = LividRGB.YELLOW
		BankOff = LividRGB.OFF
		ChainNavOn = LividRGB.RED
		ChainNavOff = LividRGB.OFF
		ContainNavOn = LividRGB.CYAN
		ContainNavOff = LividRGB.OFF
	

	class Mod:
		
		class Nav:
			OnValue = LividRGB.RED
			OffValue = LividRGB.WHITE
		
	

	class MonoInstrument:

		PressFlash = LividRGB.WHITE
		OffsetOnValue = LividRGB.GREEN
		ScaleOffsetOnValue = LividRGB.RED
		SplitModeOnValue = LividRGB.WHITE
		SequencerModeOnValue = LividRGB.CYAN
		DrumOffsetOnValue = LividRGB.MAGENTA
		VerticalOffsetOnValue = LividRGB.BLUE

		class Keys:
			SelectedNote = LividRGB.GREEN
			RootWhiteValue = LividRGB.RED
			RootBlackValue = LividRGB.MAGENTA
			WhiteValue = LividRGB.CYAN
			BlackValue = LividRGB.BLUE
		

		class Drums:
			SelectedNote = LividRGB.BLUE
			EvenValue = LividRGB.GREEN
			OddValue = LividRGB.MAGENTA
		

	

	class Translation:

		class Channel_10:
			Pad_0 = LividRGB.OFF
			Pad_1 = LividRGB.OFF
			Pad_2 = LividRGB.OFF
			Pad_3 = LividRGB.OFF
			Pad_4 = LividRGB.OFF
			Pad_5 = LividRGB.OFF
			Pad_6 = LividRGB.OFF
			Pad_7 = LividRGB.OFF
			Pad_8 = LividRGB.OFF
			Pad_9 = LividRGB.OFF
			Pad_10 = LividRGB.OFF
			Pad_11 = LividRGB.OFF
			Pad_12 = LividRGB.OFF
			Pad_13 = LividRGB.OFF
			Pad_14 = LividRGB.OFF
			Pad_15 = LividRGB.OFF
			Pad_16 = LividRGB.OFF
			Pad_17 = LividRGB.OFF
			Pad_18 = LividRGB.OFF
			Pad_19 = LividRGB.OFF
			Pad_20 = LividRGB.OFF
			Pad_21 = LividRGB.OFF
			Pad_22 = LividRGB.OFF
			Pad_23 = LividRGB.OFF
			Pad_24 = LividRGB.OFF
			Pad_25 = LividRGB.OFF
			Pad_26 = LividRGB.OFF
			Pad_27 = LividRGB.OFF
			Pad_28 = LividRGB.OFF
			Pad_29 = LividRGB.OFF
			Pad_30 = LividRGB.OFF
			Pad_31 = LividRGB.OFF
		

		class Channel_11:
			Pad_0 = LividRGB.OFF
			Pad_1 = LividRGB.OFF
			Pad_2 = LividRGB.OFF
			Pad_3 = LividRGB.OFF
			Pad_4 = LividRGB.OFF
			Pad_5 = LividRGB.OFF
			Pad_6 = LividRGB.OFF
			Pad_7 = LividRGB.OFF
			Pad_8 = LividRGB.OFF
			Pad_9 = LividRGB.OFF
			Pad_10 = LividRGB.OFF
			Pad_11 = LividRGB.OFF
			Pad_12 = LividRGB.OFF
			Pad_13 = LividRGB.OFF
			Pad_14 = LividRGB.OFF
			Pad_15 = LividRGB.OFF
			Pad_16 = LividRGB.OFF
			Pad_17 = LividRGB.OFF
			Pad_18 = LividRGB.OFF
			Pad_19 = LividRGB.OFF
			Pad_20 = LividRGB.OFF
			Pad_21 = LividRGB.OFF
			Pad_22 = LividRGB.OFF
			Pad_23 = LividRGB.OFF
			Pad_24 = LividRGB.OFF
			Pad_25 = LividRGB.OFF
			Pad_26 = LividRGB.OFF
			Pad_27 = LividRGB.OFF
			Pad_28 = LividRGB.OFF
			Pad_29 = LividRGB.OFF
			Pad_30 = LividRGB.OFF
			Pad_31 = LividRGB.OFF
		

		class Channel_12:
			Pad_0 = LividRGB.OFF
			Pad_1 = LividRGB.OFF
			Pad_2 = LividRGB.OFF
			Pad_3 = LividRGB.OFF
			Pad_4 = LividRGB.OFF
			Pad_5 = LividRGB.OFF
			Pad_6 = LividRGB.OFF
			Pad_7 = LividRGB.OFF
			Pad_8 = LividRGB.OFF
			Pad_9 = LividRGB.OFF
			Pad_10 = LividRGB.OFF
			Pad_11 = LividRGB.OFF
			Pad_12 = LividRGB.OFF
			Pad_13 = LividRGB.OFF
			Pad_14 = LividRGB.OFF
			Pad_15 = LividRGB.OFF
			Pad_16 = LividRGB.OFF
			Pad_17 = LividRGB.OFF
			Pad_18 = LividRGB.OFF
			Pad_19 = LividRGB.OFF
			Pad_20 = LividRGB.OFF
			Pad_21 = LividRGB.OFF
			Pad_22 = LividRGB.OFF
			Pad_23 = LividRGB.OFF
			Pad_24 = LividRGB.OFF
			Pad_25 = LividRGB.OFF
			Pad_26 = LividRGB.OFF
			Pad_27 = LividRGB.OFF
			Pad_28 = LividRGB.OFF
			Pad_29 = LividRGB.OFF
			Pad_30 = LividRGB.OFF
			Pad_31 = LividRGB.OFF
		

		class Channel_13:
			Pad_0 = LividRGB.OFF
			Pad_1 = LividRGB.OFF
			Pad_2 = LividRGB.OFF
			Pad_3 = LividRGB.OFF
			Pad_4 = LividRGB.OFF
			Pad_5 = LividRGB.OFF
			Pad_6 = LividRGB.OFF
			Pad_7 = LividRGB.OFF
			Pad_8 = LividRGB.OFF
			Pad_9 = LividRGB.OFF
			Pad_10 = LividRGB.OFF
			Pad_11 = LividRGB.OFF
			Pad_12 = LividRGB.OFF
			Pad_13 = LividRGB.OFF
			Pad_14 = LividRGB.OFF
			Pad_15 = LividRGB.OFF
			Pad_16 = LividRGB.OFF
			Pad_17 = LividRGB.OFF
			Pad_18 = LividRGB.OFF
			Pad_19 = LividRGB.OFF
			Pad_20 = LividRGB.OFF
			Pad_21 = LividRGB.OFF
			Pad_22 = LividRGB.OFF
			Pad_23 = LividRGB.OFF
			Pad_24 = LividRGB.OFF
			Pad_25 = LividRGB.OFF
			Pad_26 = LividRGB.OFF
			Pad_27 = LividRGB.OFF
			Pad_28 = LividRGB.OFF
			Pad_29 = LividRGB.OFF
			Pad_30 = LividRGB.OFF
			Pad_31 = LividRGB.OFF
		

	








	