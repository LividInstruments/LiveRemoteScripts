# by amounra 0914 : http://www.aumhaa.com

OSC_TRANSMIT = False

OSC_OUTPORT = 9001

CHANNEL = 0		#main channel (0 - 15)

DS1_BUTTONS = [0, 2, 4, 6, 8, 10, 12, 14, 1, 3, 5, 7, 9, 11, 13, 15]	#there are 16 of these

DS1_GRID = [[16, 19, 22],
			[17, 20, 23],
			[18, 21, 24]]


DS1_FADERS = [41, 42, 43, 44, 45, 46, 47, 48]

DS1_MASTER = 49

DS1_DIALS = [[1, 2, 3, 4, 5],
				[6, 7, 8, 9, 10],
				[11, 12, 13, 14, 15],
				[16, 17, 18, 19, 20],
				[21, 22, 23, 24, 25],
				[26, 27, 28, 29, 30],
				[31, 32, 33, 34, 35],
				[36, 37, 38, 39, 40]]

DS1_ENCODERS = [96, 97, 98, 99]

DS1_ENCODER_BUTTONS = [25, 26, 27, 28]

DS1_SIDE_DIALS = [50, 51, 52, 53]

from _Framework.ButtonElement import Color
from _Mono_Framework.LividColors import LividRGB

class DS1Colors:


	class ModeButtons:
		Main = LividRGB.WHITE
		Select = LividRGB.RED
		Clips = LividRGB.MAGENTA
	

	class ModeButtons:
		ModSwitcher = LividRGB.BlinkMedium.CYAN
		ModSwitcherDisabled = LividRGB.CYAN
		Translations = LividRGB.BlinkMedium.MAGENTA
		TranslationsDisabled = LividRGB.MAGENTA
		DeviceSelector = LividRGB.BlinkMedium.YELLOW
		DeviceSelectorDisabled = LividRGB.YELLOW
	

	class DefaultButton:
		On = LividRGB.WHITE
		Off = LividRGB.OFF
		Disabled = LividRGB.OFF
		Alert = LividRGB.BlinkFast.WHITE
	

	class Session:
		StopClipTriggered = LividRGB.BlinkFast.BLUE
		StopClip = LividRGB.WHITE
		Scene = LividRGB.CYAN
		NoScene = LividRGB.OFF
		SceneTriggered = LividRGB.GREEN
		ClipTriggeredPlay = LividRGB.BlinkFast.GREEN
		ClipTriggeredRecord = LividRGB.BlinkFast.RED
		RecordButton = LividRGB.OFF
		ClipStopped = LividRGB.WHITE
		ClipStarted = LividRGB.GREEN
		ClipRecording = LividRGB.RED
		NavigationButtonOn = LividRGB.CYAN
		NavigationButtonOff = LividRGB.YELLOW
		ZoomOn = LividRGB.BlinkFast.WHITE
		ZoomOff = LividRGB.WHITE
	

	class Zooming:
		Selected = LividRGB.BlinkFast.YELLOW
		Stopped = LividRGB.WHITE
		Playing = LividRGB.GREEN
		Empty = LividRGB.OFF
	

	class LoopSelector:
		Playhead = LividRGB.YELLOW
		OutsideLoop = LividRGB.BLUE
		InsideLoopStartBar = LividRGB.CYAN
		SelectedPage = LividRGB.WHITE
		InsideLoop = LividRGB.CYAN
		PlayheadRecord = LividRGB.RED
	

	class Transport:
		PlayOn = LividRGB.BlinkMedium.GREEN
		PlayOff = LividRGB.GREEN
		StopOn = LividRGB.BLUE
		RecordOn = LividRGB.BlinkMedium.RED
		RecordOff = LividRGB.RED
		OverdubOn = LividRGB.BlinkFast.RED
		OverdubOff = LividRGB.RED	
		SeekBackwardOn = LividRGB.BlinkMedium.CYAN
		SeekBackwardOff = LividRGB.CYAN
		LoopOn = LividRGB.BlinkMedium.YELLOW
		LoopOff = LividRGB.YELLOW
	

	class Mixer:
		SoloOn = LividRGB.BLUE
		SoloOff = LividRGB.CYAN
		MuteOn = LividRGB.YELLOW
		MuteOff = LividRGB.WHITE
		ArmSelected = LividRGB.RED
		ArmUnselected = LividRGB.RED
		ArmOff = LividRGB.WHITE
		StopClip = LividRGB.BLUE
		SelectedOn = LividRGB.GREEN
		SelectedOff = LividRGB.MAGENTA
	

	class Recording:
		Transition = LividRGB.BlinkFast.MAGENTA
	

	class Recorder:
		On = LividRGB.WHITE
		Off = LividRGB.BLUE
		NewOn = LividRGB.BlinkMedium.YELLOW
		NewOff = LividRGB.YELLOW
		FixedOn = LividRGB.BlinkMedium.CYAN
		FixedOff = LividRGB.CYAN
		RecordOn = LividRGB.BlinkMedium.MAGENTA
		RecordOff = LividRGB.MAGENTA
		AutomationOn = LividRGB.BlinkMedium.CYAN
		AutomationOff = LividRGB.CYAN
		FixedAssigned = LividRGB.MAGENTA
		FixedNotAssigned = LividRGB.OFF
	

	class Device:
		NavOn = LividRGB.MAGENTA
		NavOff = LividRGB.OFF
		BankOn = LividRGB.YELLOW
		BankOff = LividRGB.OFF
		ChainNavOn = LividRGB.RED
		ChainNavOff = LividRGB.OFF
		ContainNavOn = LividRGB.CYAN
		ContainNavOff = LividRGB.OFF
	

