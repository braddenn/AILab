# Module:	button.py
#
# Description: creates and supports a clickable button object
#
# Author: Brad Denniston
# Version: 0.1, 02 Dec 2018

import pygame
from pygame.locals import *

# Button - class of module button
# Desc: draw and manage a button
# Usage: menu.draw_menu
class Button() :
	# Button.__init___
	# Parm: text - text to display in the button
	# Parm: screen - surface where button is drawn
	# Parm: x - horizontal offset of the left edge of the button
	# Parm: y - vertical offset down from screen top to the top of the button
	# Parm: w - width of the button
	# Parm: h - height of the button
	# Parm: border_size - width of the button border
	# Parm: base_color - button color
	# Usage: public, menu.draw_menu
	def __init__(self, text, screen, x, y, w, h, border_size, base_color ):
		self.screen = screen
		self.text = text
		self.x = x
		self.y = y 
		self.w = w
		self.h = h
		self.border_size = border_size
		self.textx = x + border_size
		self.texty = y + border_size
		self.textw = w - self.border_size * 2
		self.texth = h - self.border_size * 2
		self.border_color = (0,0,0) # can be changed by external reference
		self.base_color = base_color  # color when not clicked or hovered over
		self.current_color = self.base_color
		self.draw(0)

	# draw def of class Button
	# Parm: border_width - width of the border around the button
	# Usage: public
	def draw(self, border_width) :
		pygame.draw.rect( self.screen, self.border_color, [self.x, self.y, self.w, self.h])
		bw = border_width/2
		pygame.draw.rect( self.screen, self.base_color,\
				(self.textx + bw, self.texty + bw, self.textw - border_width, 
				self.texth - border_width))
		button_font = pygame.font.SysFont("helvetica", 14)

		# button_text = button_font.render(self.text, True, self.base_color)
		button_text = button_font.render(self.text, True, (80,80,80))
		text_loc = ( (self.textx + 4), (self.texty + self.texth/4))
		self.screen.blit(button_text, text_loc)         
        
	# check_down def of class Button
	# Desc: respond to mouse click down
	# Usage: public
	def check_down(self, x, y):
		if ( self.x < x and (self.x + self.w) > x \
		and ( self.y < y and (self.y + self.h) > y ) ) :
			# show more border
			self.draw(4)
			return self.text
		return None
        
	# check_up def of class Button
	# Desc: respond to mouse button going up
	# Parm: x - number of pixels to right of 0
	# Parm: y - number of pixels down from top
	# Usage: public
	def check_up(self, x, y):
		if ( self.x < x and (self.x + self.w) > x \
		and ( self.y < y and (self.y + self.h) > y ) ) :
			# reset border width
			self.draw(0)
			return None
		return 'scene'
	
	# set_text setter of class Button
	# Desc: change the text of this button
	def set_text( self, new_text ):
		self.text = new_text
        