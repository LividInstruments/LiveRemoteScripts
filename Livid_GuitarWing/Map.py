
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



