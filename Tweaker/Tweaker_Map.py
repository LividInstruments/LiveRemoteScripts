# by amounra 0413 : http://www.aumhaa.com
"""
Tweaker_Map.py

Created by amounra on 2012-04-30.
Copyright (c) 2010 __artisia__. All rights reserved.

This file allows the reassignment of the controls from their default arrangement.  The order is from left to right; 
Buttons are Note #'s and Faders/Rotaries are Controller #'s
"""

CHANNEL = 0		#main channel (0 - 15)


TWEAKER_BUTTONS = [33, 34, 35, 36, 37, 38]    #buttons on each channel strip, 3 on each side

TWEAKER_NAVS = [39, 40, 41, 42, 43]			#navigation cluster, there are 5 of these

TWEAKER_ENCODER_BUTTONS = [44, 45, 46, 47, 48, 49, 50]		#buttons for shuttle and encoders on each channel strip, 3 on each side

TWEAKER_DIALS = [51, 52]		#analog knobs, there are 2? of these

TWEAKER_FADERS = [53, 54]		#faders on each channel strip

CROSSFADER = 55		#single

TWEAKER_ENCODERS = [56, 57, 58, 59, 60, 61, 62]		#shuttle and encoders on each channel strip, 3 on each side

TWEAKER_PADS = [63, 64, 65, 66, 67, 68, 69, 70]    #velocity sensitive drumpads notes

TWEAKER_PAD_PRESSURES = [71, 72, 73, 74, 75, 76, 77, 78]    #velocity sensitive drumpads cc's

PAD_SENSITIVITY = 10  #this determines how sensitive the pads are, 0 being stiffest, 5 being easiest to trigger the highest velocity; the setting is sent to the Tweaker when it initializes

PAD_TRANSLATION = 	((0, 0, 0, 63), (0, 1, 1, 64), (0, 2, 2, 65), (0, 3, 3, 66),		#this is used by DrumRacks to translate input to one of the visible grid squares for triggering
					(1, 0, 4, 67), (1, 1, 5, 68), (1, 2, 6, 69), (1, 3, 7, 70))			#the format is (x position, y position, note-number, channel)


FOLLOW = True		#this sets whether or not the last selected device on a track is selected for editing when you select a new track

#	The default assignments of colors for the Tweaker RGB's are:
#	1:Note 2 = green
#	2:Note 4 = red 
#	3:Note 8 = yellow 
#	4:Note 16 = blue 
#	5:Note 32 = cyan 
#	6:Note 64 = magenta
#	7:Note 127 = white
#	Because the colors are reassignable, and the default colors have changed from the initial prototype,
#		Tweaker script utilizes a color map to assign colors to the buttons.  This color map can be changed 
#		here in the script.  The color ordering is from 1 to 7.  

#COLOR_MAP = [1, 2, 3, 4, 5, 6, 7]   #new version

COLOR_MAP = [2, 4, 8, 16, 32, 64, 127]		#old version

#	In addition, there are two further color maps that are used depending on whether the RGB or Monochrome 
#		Ohm64 is detected.  The first number is the color used by the RGB (from the ordering in the COLOR_MAP array),
#		the second the Monochrome.  Obviously the Monochrome doesn't use the colors.  
#	However, the flashing status of a color is derived at by modulus.  Thus 1-7 are the raw colors, 8-14 are a fast
#		flashing color, 15-21 flash a little slower, etc.  You can assign your own color maps here:

MUTE = 3
SOLO = 4
ARM = 2
SEND_RESET = 8
SCENE_LAUNCH = 6 
CROSSFADE_TOGGLE = 4
TRACK_STOP = 4
BANK_BUTTONS = 1
STOP_ALL = 13 
SESSION_NAV = 1 
OVERDUB = 4
LOOP = 3 
STOP = 127 
RECORD = 5
PLAY = 6 
PLAY_ON = 18 
DEVICE_BANK = 127
DEVICE_NAV = 1
DEVICE_ON = 127
DEVICE_LOCK = 4 
CLIP_RECORDING = 2	
CLIP_STARTED = 1
CLIP_STOP = 127
CLIP_TRG_REC = 8 
CLIP_TRG_PLAY = 13 
ZOOM_STOPPED = 127 
ZOOM_PLAYING = 1 
ZOOM_SELECTED = 3 
STOP_CLIP = 127

ACTIVE_CHAN = 3

SHIFT_ON = 4
SHIFT_OFF = 127

NAV_COLORS = [4, 5]
RETURN_NAV_COLORS = [2, 6]

CROSSFADE_A = 1
CROSSFADE_B = 2

PAD_CHANNEL = 9
## a



