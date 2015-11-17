# by amounra 0413 : http://www.aumhaa.com

"""
Codec_Map.py

Created by amounra on 2010-10-05.
Copyright (c) 2010 __artisia__. All rights reserved.

This file allows the reassignment of the controls from their default arrangement.  The order is from left to right; 
Buttons are Note #'s and Faders/Rotaries are Controller #'s
"""
CHANNEL = 0		#main channel (0 - 15)

CODE_BUTTONS = 		[[1, 5, 9, 13, 17, 21, 25, 29],
    				 [2, 6, 10, 14, 18, 22, 26, 30],
					 [3, 7, 11, 15, 19, 23, 27, 31],
					 [4, 8, 12, 16, 20, 24, 28, 32]]

CODE_DIALS = 		[[1, 5, 9, 13, 17, 21, 25, 29],
    				 [2, 6, 10, 14, 18, 22, 26, 30],
					 [3, 7, 11, 15, 19, 23, 27, 31],
					 [4, 8, 12, 16, 20, 24, 28, 32]]	

CODE_COLUMN_BUTTONS = [38, 39, 40, 41, 42, 43, 44, 45]

CODE_ROW_BUTTONS = [33, 34, 35, 36]

LIVID = 37			#single

FOLLOW = True		#this sets whether or not the last selected device on a track is selected for editing when you select a new track

COLOR_MAP = [127, 127, 127, 127, 127, 127, 127]

USE_DEVICE_SELECTOR = True

FACTORY_RESET = True


## a



