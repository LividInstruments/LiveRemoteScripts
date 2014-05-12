
"""
Base_Map.py

Created by amounra on 2012-12-30.

This file allows the reassignment of the controls from their default arrangement.  The order is from left to right; 
Buttons are Note #'s and Faders/Rotaries are Controller #'s
"""
OSC_TRANSMIT = False

OSC_OUTPORT = 9001

CHANNEL = 0		#main channel (0 - 15)

PADS = [36, 37, 38, 39, 4]

BUTTONS = [40, 41, 42, 43, 44, 45, 46, 47, 48, 49]

SLIDERS = [1, 2, 3]

ACCELS = [5, 6, 7]

CCS = [8, 9, 10, 11]


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

MUTE = [2, 2, 127]
SOLO = [3, 9, 127]
ARM = [5, 5, 8]
SEND_RESET = [1, 7, 7]
STOP_CLIPS = [127, 1, 1]
STOP_CLIPS_OFF = [127, 127, 127]
SELECT = [127, 127, 127]
SCENE_LAUNCH = [7, 3, 17]
USER1_COLOR = [4, 4, 29]
USER2_COLOR = [5, 5, 29]
USER3_COLOR = [6, 6, 29]
CROSSFADE_TOGGLE = [4, 4, 127]
TRACK_STOP = [127, 127, 127]
DEVICE_SELECT = [1, 1, 8]
BANK_BUTTONS = [1, 1, 1]
STOP_ALL = [127, 127, 15]
SESSION_NAV = [2, 2, 32]
SESSION_NAV_OFF = [3, 3, 33]
OVERDUB = [4, 4, 127]
LOOP = [3, 3, 127]
STOP = [127, 127, 127]
STOP_OFF = [127, 127, 127]
RECORD = [5, 5, 15]
RECORD_ON = [11, 11, 15]
PLAY = [6, 6, 127]
PLAY_ON = [18, 18, 127]
DEVICE_BANK = [127, 127, 127]
DEVICE_NAV = [1, 1, 127]
DEVICE_ON = [127, 127, 127]
DEVICE_LOCK = [4, 4, 127]
CLIP_RECORDING = [5, 11, 8] 
CLIP_STARTED = [6, 6, 32]
CLIP_STOP = [1, 127, 127]
CLIP_TRG_REC = [11, 4, 8]
CLIP_TRG_PLAY = [12, 2, 15]
ZOOM_STOPPED = [1, 127, 127]
ZOOM_PLAYING = [6, 6, 15]
ZOOM_SELECTED = [8, 1, 8]
STOP_CLIP = [127, 127, 2]

