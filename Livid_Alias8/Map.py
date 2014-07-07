
"""
Alias_Map.py

Created by amounra on 2012-12-30.
Copyright (c) 2010 __artisia__. All rights reserved.

This file allows the reassignment of the controls from their default arrangement.  The order is from left to right; 
Buttons are Note #'s and Faders/Rotaries are Controller #'s
"""

DISABLE_MASTER_VOLUME = False  #Option for disabling shift-functionality to assign far right fader to MASTER VOLUME

CHANNEL = 0		#main channel (0 - 15)

ALIAS_BUTTONS = [index for index in range(16)]    #there are 16 of these

ALIAS_FADERS = [(index+17) for index in range(9)]		#there are 9 of these

ALIAS_DIALS = [(index+1) for index in range(16)]		#there are 16 of these

ALIAS_ENCODER = 42

FOLLOW = True		#this sets whether or not the last selected device on a track is selected for editing when you select a new track

"""	The default assignment of colors within the OhmRGB is:
Note 2 = white
Note 4 = cyan 
Note 8 = magenta 
Note 16 = red 
Note 32 = blue 
Note 64 = yellow
Note 127 = green
Because the colors are reassignable, and the default colors have changed from the initial prototype,
	MonOhm script utilizes a color map to assign colors to the buttons.  This color map can be changed 
	here in the script.  The color ordering is from 1 to 7.  
"""
COLOR_MAP = [2, 64, 4, 8, 16, 127, 32]
#COLOR_MAP = [1, 6, 2, 3, 4, 7, 5]

MUTE_TOG = 2
REC_TOG = 5

## a



