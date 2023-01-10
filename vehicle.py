# Module: vehicle.py
# Desc: controls the movement of the dunebuggy
# Author: Brad Denniston
# Version: 0.3, 12 Nov 2018

import pygame
import cmath
import tools

TEST = False

# Vehicle - class of module vehicle
# Desc: a sprite representing a vehicle that is moved
# Usage: public, desertmap.simmap
class Vehicle(pygame.sprite.Sprite):
	# Def __init__ of class Vehicle
	# Desc: define the vehicle
	# Usage: public, desertmap.simmap
	def __init__(self, screen, config) :
		
		global TEST  # this enables it to be changed in a method
		TEST = config['test']

		# objects complex and debug
		self.c = tools.Cplx()
		self.debug = tools.Debug(config)

		pygame.sprite.Sprite.__init__(self)
		self.screen = screen
		self.width = self.screen.get_width()
		self.height = self.screen.get_height()

		# vehicle location on the map
		self.sloc_rect = [self.width/2, self.height/2] # center as screen_x,screen_y: rectangular
		self.sloc_comp = (self.width/2 + self.height/2 * 1j)
		
		# vehicle previous location - gets overprinted with background
		self.prev_sloc_rect = self.sloc_rect
		
		# current heading, start pointing North
		self.heading_deg = 90.0
		self.heading_rad = self.debug.deg2rad(self.heading_deg)
		
		# current speed initially is 5 pixels per turn
		self.max_speed = 20
		self.speed = 5
		
		# previous speed_change and angle_change in polar
		self.previous_change_command_comp = (0 + 0j)
		
		# get a 20x20 pixel vehicle sprite based on the image
		self.vehicle_sprite, self.rect = load_png("DBn.png")
		self.screen.blit(self.vehicle_sprite, self.sloc_rect)

		# get a 20x20 background sprite based on the sand image
		self.sand_bgn_sprite, self.rectangle = load_png("sand.png")
			
	# Def: user_key of class Vehicle
	# Desc: 
	#	left,right arrow key - modify change direction by +/- 30 degrees
	#   up,down arrow keys - add/subtract 10 from speed
	#	other keys - take a step per the current vector
	#	else return (0,0) - repeat previous move
	# Parm: key - that was activated
    # Return: polar direction change and magnitude of change, same as AI return.
	#	A return of (0,0) results in no change in speed or angle
	# Usage: user input, from main
	def user_key( self, key ):
		if TEST:
			print(key)
		# right key, rotate to CCW 30 degrees
		if key == 'right' :
			# change = complex of -30 degrees
			if TEST: print('right 30 (-30)')
			speed_change = 0
			angle_change = self.debug.deg2rad(-30)
			
		# left button, rotate to CW 30 degrees
		elif key == 'left' :
			# change = complex of -30 degrees
			if TEST: print('left 30 (+30)')
			speed_change = 0
			angle_change = self.debug.deg2rad(30)
			
		# up key, increase magnitude of change by 5 up to 20
		elif key == 'up' :
			if TEST: print('speed up 5')
			speed_change = 5
			angle_change = 0
			
		# down key, decrease magnitude of change by 5 down to 0
		elif key == 'down' :
			if TEST: print('speed down 5')
			speed_change = -5
			angle_change = 0

		# space bar, repeat previous command
		elif key == 'space' :
			if TEST: print('repeat')
			return (0 + 0j)
			
		# else - any other key means repeat previous command
		else:
			if TEST: print('repeat')
			return self.previous_change_command_polar
			
		# return complex direction change and speed change 
		change_vector_comp = speed_change * (cmath.cos(angle_change) + cmath.sin(angle_change) * 1j)
		if TEST:
			print('in user key')
			print('speed change', speed_change, 'angle_change', angle_change)
			print('complex =', change_vector_comp)
		return change_vector_comp

	# Def: move of class Vehicle
	# Desc: change vehicle location by adding a change_vector, then move
	# 	Called after keyboard key or AI command.
	# Parm: change_vector_polar - polar speed change and direction change. 
	#	if (0,0) then no change, move per current heading and speed
	# Usage: desertmap
	def move( self, change_vector_comp ) :	

		speed_change = abs(change_vector_comp)
		angle_change_rad = cmath.phase(change_vector_comp)
		
		new_angle = self.heading_rad + angle_change_rad
		new_speed = self.speed + speed_change
		
		change_vector_comp = new_speed * (cmath.cos(new_angle) + cmath.sin(new_angle)*1j)
		
		if TEST: 
			print('in move....')
			print('speed change:',speed_change, 'at angle',
					self.debug.rad2deg( angle_change_rad ))		
		
		if TEST: print('change_vector_comp =', change_vector_comp)
		self.previous_change_command_comp = change_vector_comp

		# don't go past map boundaries or into a hill
		# don't go too fast
		new_location_rect = self.limit(change_vector_comp)
		if TEST: print('new loc:', new_location_rect)
		self.draw(new_location_rect)

	# Def: limit of class Vehicle
	# Desc: apply proposed change to current loc and test against 
	#	map edges, hills and exit
	# Parm: change_vector_polar - polar direction change and speed change.
	# Ref: self.sloc_comp - current vector
    # Ref: self.sloc - current map coordinates of the vehicle
	# Ref: self.speed - current speed
	# Ref: self.heading - current direction of travel	
	# Usage: local.move
	# Return: new location, destination of the move
	def limit(self, change_vector_comp):
	
		speed_change = change_vector_comp.real
		if TEST: print('limit: speed change:', speed_change)
		angle_change = change_vector_comp.imag
		if TEST: print('limit: angle change:', angle_change)
		
		self.speed += speed_change
		if self.speed < 0 :
			self.speed = -self.speed
			angle_change = angle_change - cmath.pi # back up
		if TEST: print('new speed', self.speed)

		# speed limit
		if self.speed > self.max_speed : self.speed = self.max_speed
		
		if TEST: print('limited speed', self.speed)
		if TEST: print( 'limit 1: initial heading deg:', self.heading_deg)
		if TEST: print( 'limit 1: angle change rad:', angle_change)
		
		self.heading_rad = self.heading_rad + angle_change
		self.heading_deg = self.debug.rad2deg(self.heading_rad)
		if TEST: print( 'limit 2: heading deg:', self.heading_deg)

		change_vector_comp = (self.speed + angle_change *1j)	

		# add the change vector to the current location
		if TEST: print('current loc:',self.sloc_comp)
		if TEST: print('change vector:', change_vector_comp)
		self.sloc_comp = self.sloc_comp + change_vector_comp
		if TEST: print('new loc:',self.sloc_comp)
		
		# convert complex location vector to rectangular and limit by walls
		sLocX = int(self.sloc_comp.real)	
		
		if sLocX < 0 : sLocX = 0
		if sLocX > self.width : sLocX = self.width
		
		sLocY = int(self.sloc_comp.imag)
		if sLocY < 0 : sLocY = 0
		if sLocY > self.height : sLocY = self.height
		
		# convert back to complex
		self.sloc_comp = (sLocX + sLocY * 1j)
		self.sloc_rect = (sLocX, sLocY)
		if TEST: print('back to complex, call draw with: ',self.sloc_rect)
		return( self.sloc_rect )

	# Def draw of class Vehicle
	# Desc: draw the vehicle, converting y to screen y
    # Parm: new_location_rect - draw at this location
	# Ref: self.prev_sloc - location to overwrite in background blit
	# Usage: Vehicle.move
	def draw( self, new_location_rect ):
		
		self.sloc_rect = new_location_rect
		
		# paint ground over current location to erase the current vehicle blit
		screen_y = self.height - self.prev_sloc_rect[1] # convert to screen coords
		self.screen.blit(self.sand_bgn_sprite, (self.prev_sloc_rect[0], screen_y))
		# if TEST: print('Draw: draw vehicle from', self.prev_sloc_rect, 'to:', new_location_rect)
		
		# update the backup location to the new location
		self.prev_sloc_rect = new_location_rect

		# paint the vehicle at the new location
		screen_y = self.height - self.sloc_rect[1]		
		self.screen.blit(self.vehicle_sprite, (self.sloc_rect[0], screen_y))

# Def load_pgn of module vehicle.py
# Desc: load a .png picture
# Parm: name - file name, local directory only
# Usage: private
def load_png(name):

	try:
		image = pygame.image.load(name)  # in local directory
		if image.get_alpha is None:
			image = image.convert()
		else:
			image = image.convert_alpha()
	except (pygame.error, message):
		print('Cannot load image:',image)
		return None, None
	return image, image.get_rect()
