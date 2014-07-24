
"""
Base_Map.py

Created by amounra on 2012-12-30.

This file allows the reassignment of the controls from their default arrangement.  The order is from left to right; 
Buttons are Note #'s and Faders/Rotaries are Controller #'s
"""
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

FOLLOW = True		#this sets whether or not the last selected device on a track is selected for editing when you select a new track

TRACK_BANKING_INCREMENT = 8

""" The default assignment of colors within the OhmRGB is:
Note 2 = white
Note 4 = cyan 
Note 8 = magenta 
Note 16 = red 
Note 32 = blue 
Note 64 = yellow
Note 127 = green
Because the colors are reassignable, and the default colors have changed from the initial prototype,
	MonOhm script utilizes a color map to assign colors to the buttons.	 This color map can be changed 
	here in the script.	 The color ordering is from 1 to 7.	 
"""
COLOR_MAP = [2, 64, 4, 8, 16, 127, 32]
#COLOR_MAP = [7, 1, 3, 2, 6, 5, 4]

"""This variable determines whether or not the script automatically arms an instruments track for recording when it is selected"""
AUTO_ARM_SELECTED = True

"""This variable determines whether the octave shift for the note offset controls work as momentary or toggle"""
OFFSET_SHIFT_IS_MOMENTARY = False
CHAN_SELECT = 7
MUTE = 2
SOLO = 3
OFFSET = 6
SHIFT_OFFSET = 13
VERTOFFSET = 7
MIDIMODE = 14
USERMODE = 13
SCALEOFFSET = 5
SPLITMODE = 1
SEQUENCERMODE = 6
DRUMBANK = 7
OVERDUB = 5
RECORD = 6
NEW = 2
LENGTH = 3
SELECTED_NOTE = 6

"""[non-banked, banked]"""
SESSION_NAV = [127, 3]
DEVICE_NAV = 5
BANK_NAV = 4
CHAIN_NAV = 11
DEVICE_LAYER = 12


TRACK_MUTE = 2
TRACK_ARM = 5
TRACK_SOLO = 3
TRACK_STOP = 127

STOP_CLIP = 127
CLIP_TRG_PLAY = 13
CLIP_TRG_REC = 11
CLIP_STOP = 1
CLIP_STARTED = 6
CLIP_RECORDING = 5
ZOOM_STOPPED = 127
ZOOM_PLAYING = 6
ZOOM_SELECTED = 8

