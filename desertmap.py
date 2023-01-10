# Module: desertmap.py
# Desc: manage the screen - map, menu, help
# Classes:
#	class SimMap - draws the frame and menu
#	class Help - display help file in multiple screens
#	class Menu - display the menu, return user selections
#
#	Author: Brad Denniston
#	Version: 0.3, 22 Nov 2018
#
# Notation Notes:
#	variable_rect : rectangular
#	variable_comp : complex
#	variable_rad : radians
#	variable_deg : degrees
# import python modules
import random
import copy  
import pygame
import cmath

# import dunebuggy modules
import button
import vehicle
import sensors
import tools		# debug support

# choose the complex math version
import NeuralNetCmplx
# or choose the real math version: 
# import NeuralNet

import pprint

SAND  = (242,234,193)
BLACK = (  0,  0,  0)
WHITE = (255,255,255)
RED   = (255,  0,  0)
GREEN = (  0,255,  0)
BLUE  = (  0,  0,255)
GRASS = (64,128,  0)
GRAY  = (128,128,128)

SIZE = 10  # 1/2 width and height of a 20x20

if not pygame.font.get_init() :
    pygame.font.init()
   
TEST = False

# SimMap class of module desertmap
# Desc: draws display, menu. Supports the user interface.
# 	created by main. This is a desert map implementation. Other 
# 	maps use the same methods. Module desertmap may be replaced with 
#	seamap or citymap or another maps as long as class SimMap is implemented.
# 	The screen is x : increases to the right, 
#                 y : increases down (backwards from program coordinates )
class SimMap:

    # Def: SimMap.__init__ 
	def __init__(self, config):
		if config['test'] == 'true' :
			TEST =  True
			
		self.complex = True
		self.sprites = []       # sprite list
		self.map_width = 400    #  How wide the map is
		self.map_height = 400   #  How high the map is in pixels
		self.menu_height = 25   #  50 ? Above the map for menu
		self.map_color = SAND   # map background
		self.map_text_color = BLACK   # map text			
		self.font = pygame.font.SysFont('helvetica',8)
		self.menu = None
		self.screen = None
		self.hills = None
		self.new_frame() # sets self.screen, menu, hills
		self.vehicle = vehicle.Vehicle( self.screen, config )
		self.sensors = sensors.Sensors(self.vehicle, self.hills, config)
		self.debug = tools.Debug( config )
		self.AIRun = False
		self.drive_mode = 'Manual'

		self.AI = NeuralNetCmplx.NeuralNetCmplx(config)

			
    # new_frame def of class SimMap
	# Desc - clear data, draw a new frame, insert the menu
	#	Does set_mode( resolution=(0,0), flags=0, depth=0) 
	#	which creates a display surface with resolution( width, height)
	#	flags: depth and color bits (don't use) 
	# Usage: __init__()
	def new_frame(self):
		self.screen = pygame.display.set_mode((self.map_width,
                                 self.map_height + self.menu_height))
		self.screen.fill(self.map_color)
		pygame.display.set_icon(pygame.image.load("DBn.png"))
		pygame.display.set_caption("Dune Buggy")

		self.hills = Hills(self.screen, self.map_height) # an object of hills
		exit_loc = [self.map_width-1, self.menu_height + 8]
		if TEST: print('exit loc = ', exit_loc)
		self.hills.add(exit_loc)
		# now put a menu across the top of the new screen
		self.menu = Menu(self.screen, self.menu_height, self.map_color)
		
   	# direction_key def of class SimMap
	# Desc: change sprite action according to which key is down
	#	Note that user or AI can change the vehicle change vector
	#	Take a step after each change
	# Parm: keyboard event where the key is 
	#		Speed is: up,down. Direction is: left, right. spacebar
	# Usage: main
	def direction_key(self, event ) :
        # get complex: direction and magnitude of change
		change = self.vehicle.user_key(pygame.key.name(event.key))
		# take a step implementing the change
		self.vehicle.move(change)

	# mouse_button def of class SimMap
	# Desc: Left/right mouse button, not a menu button
	# Parm: event from the keyboard/ 
	def mouse_button( self, event ):
		if event.type == pygame.MOUSEBUTTONDOWN :
			# location is an (x,y) vector
			location = pygame.mouse.get_pos()
			
			# buttons is a tuple of left, middle, right
			buttons = pygame.mouse.get_pressed()

			if buttons[2] == True : # right button pushed, delete this hill
				self.hills.remove(location)
				return
			
			elif buttons[0] == True : # left button pushed, add a hill here
				self.hills.add(location)
				return
				
			else:
				print('Did not read the button, hold it down a little longer')
	
    # menu_load def of class SimMap
	# Desc: load the map from a file
	# Parm: filename - name of file to read from
	def menu_load(self, filename):
		if TEST: print('load from {}'.format(filename))
		self.running = False

    # menu_save def of class SimMap
	# Desc: user request to save the map and sprites to a file 
	def menu_save(self) :
		if TEST: print('save to file to be implemented')
		self.running = False

	# menu_manual def of class SimMap
	# Desc: set mode to manual, vehicle driven by keyboard
	def menu_manual(self):
		if TEST: print( 'manual')
		self.running = False
		self.driveMode = 'manual'
		self.menu.update_menu(2, 'AI')
		self.menu.update_menu(4, 'Run')

	# menu_ai def of class SimMap
	# Desc: set mode to AI, vehicle driven by AI
	def menu_ai(self):
		if TEST: print( 'ai')
		self.running = False
		self.driveMode = 'ai'
		self.menu.update_menu(2, 'Manual')
		self.menu.update_menu(4, 'Run')
		self.step = True
	
	# menu_step def of class SimMap
	# Desc: step or run button: advance the vehicle one step
	#	Either a manual step or, if AI is active, an AI step 
	# Parm: mode "manual" or "AI"
	# Return: True to move vehicle and run again, False at optimal result
	# Called by: AILab user 'step' or 'run' event
	def menu_step(self):
		# new input set, normalize magnitudes
		if self.drive_mode == 'manual' :
			vehicle_command = self.vehicle.user_vector( self, 'space' )
			# update the display
			self.vehicle.move(vehicle_command)
			return True

		sensor_data = self.sensors.get_sensor_data( self.hills.hillslist )
		sensor_data = self.normalize_complex_set(sensor_data)

		# get reference signal received as if at the exit (0 angle, full power)
		target_value = self.sensors.get_expected_result()
		mag,angle = cmath.polar(target_value)
	
		# normalize target magnitude to 1
		target_result = complex(1,angle)
		print('Normalized target value is {}'.format(target_result))
	
		# compute a change of direction and speed for the vehicle (complex)
		vehicle_command = self.AI.adapt(sensor_data, target_result, True)
		if vehicle_command == -1 : # AI is at the optimal result
			return False	
			
		# update the display
		self.vehicle.move(vehicle_command)
		return True
	
	# menu_stop def of class SimMap
	# Desc: stop running, change menu item 4 from 'Stop' to 'Run'
	#    can be running in AI mode or manual mode
	def menu_stop(self):
		if TEST: print( 'stop')
		self.menu.update_menu(4, 'Run')

	# menu_help def of class SimMap
	# Desc: display help information to the user
	# NOTE: probably not needed
	def menu_help(self):
		if TEST: print('Help not yet implemented')

	# menu_exit def of class SimMap
	# Desc: clean up before exit to system
	def menu_exit(self):
		if TEST: print('exit')	

	# normalize_complex_set def of class NeuralNetCmplx
	# Desc: get largest magnitude, use to normalize magnitudes
	# Parm: set - a list of complex values
	# Return: normalized list of complex values
	def normalize_complex_set( self, set ):
		max = 0
		size = len(set)
		for index in range(size):
			value = set[index]
			mag, angle = cmath.polar(set[index])
			if mag > max : max = mag
		if TEST: print('Normalized')
		for index in range(size):
			mag, angle = cmath.polar(set[index])
			mag = mag / max
			set[index] = complex(mag, angle)
			print(self.trun_comp(set[index] ) )
		return set
		
	# def trun_comp
	# Desc: convert complex into truncated and rounded values
	# Return: real, imag
	def trun_comp( self, comp ):
		return int(comp.real * 1000 )/1000, int(comp.imag * 1000 )/1000

# Menu - class of module desertmap
# Desc: draw the menu across the top of the screen.
# Usage: created by SimMap.new_frame
class Menu:

	# __init__ def of class Menu
	# Desc: build and display the menu at the top with buttons
	# Parm: screen - area of display reserved for this map
	# Parm: menu_height - number of pixels of menu height above map
	# Parm: map_color - color of map background
	def __init__(self, screen, menu_height, map_color):

		self.screen = screen
		self.button_text = ["Load", "Save", "Manual", "Step", "Run", "Help", "Exit"]
		self.button_count =  len(self.button_text)
		self.buttons = []
		self.menu_height = menu_height
		self.backgound = map_color

		## -- MAIN MENU -- ###
		self.button_height = 25        #  The height of each button
		self.button_width = screen.get_width() / (self.button_count)
		self.button_border_size = 2    #  The thickness of the borders on the buttons
		self.button_gap_size = 10      #  The vertical gap between each button
		self.menu_text_size = 18       #  The size of the text in the buttons
		self.colors = {
			'border' : BLACK,
			'text' : BLACK,
			'background' : SAND,
			'button' : WHITE
			}
		self.draw_menu()

	# draw_menu def of class Menu
	# Desc: Draws the menu of buttons at the top of the screen
	def draw_menu(self):
		for index in range(self.button_count):
			x = self.button_width * index
			# Parms: (text, screen, x, y, w, h, border_size, color, hover_color ):
			aButton = button.Button( self.button_text[index], self.screen, x, 0, 
				self.button_width, self.button_height, 
				self.button_border_size,
				self.colors['button']
				)
			self.buttons.append(aButton)
		pygame.display.update()

	# check_menu def of class Menu
	# Desc: An event was detected, check for menu events. 
	# Desc: Changes color if hovering on a button.
	# Parm: action - MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN
	# Return: Text for the selected menu item, else 'scene'
	# Usage: main
	def check_menu( self, event ):
		x,y = event.pos
		ret = None
		for button in self.buttons :
			if event.type == pygame.MOUSEBUTTONDOWN :
				text = button.check_down(x, y)
				if text != None :
					return text
			if event.type == pygame.MOUSEBUTTONUP :
				return button.check_up(x, y)
		return 'scene' # not on a menu button
                               
	# update_menu def of class Menu
	# Desc: change test of a menu button
	# Parm: index - index of button to change, 0-n
	# Parm: text - new text
	# Usage: main
	def update_menu( self, index, text ):
		self.button_text[index] = text
		self.buttons[index].set_text( text )
		self.draw_menu( )
	
# Hills class of module desertmap
# Desc: support a list of hills
# Usage: created by class SimMap
class Hills(pygame.sprite.Sprite):

	# __init__ def of classs Hills
	# Desc: define a list for hills. Support actions on hills.
	# Parm: screen - screen surface where the hills are displayed
	def __init__(self, screen, screen_height):
		self.screen = screen
		self.screen_height = screen_height
		# get a sprite based on the image
		self.hillImage, self.hillRect = self.load_png("hill.png")
		# get a background sprite based on the grass image
		self.sand_bgn, self.rectangle = self.load_png("sand.png")
		# list of all hills
		self.hillslist = []    
		
	# add def of class Hills
	# Desc: add a hill to the list. Convert y coord to go up, not down
	# Parm: location in form [x,y] screen pixel coords, center of a cell
	#		where a cell contains a vehicle or hill
	# Usage: mouse_button
	def add(self, location):
		x = location[0]
		# Convert y coord to go up, not down, so 0 is at the bottom
		y =  self.screen_height - location[1]
		# walk the list looking for a free hill in cell around x,y
		for hill in self.hillslist :
			# SIZE is height of a cell in pixels.
			# SIZE is a global set to 10
			# So a cell is 20 x 20 pixels
			if x < hill.x and x > hill.x \
			and y > hill.y - SIZE and y < hill.y + SIZE : # SIZE is # pixels in a cell
				if hill.state == 'free' :
					self.screen.blit(self.hillImage, (hill.x - SIZE, hill.y - SIZE))
					hill.state = 'inUse'
					return

		# no hill at this location so add a hill object	
		hill = self.Hill(x,y)
		self.hillslist.append(hill)
		# paint the image around the location coordinates
		self.screen.blit(self.hillImage, (location[0] - SIZE, location[1] - SIZE))

	# remove def of class Hills
	# Desc: delete a hill from display and list
	# Parm: location - x,y anywhere in a SIZE x SIZE box
	def remove(self, location) :
		x = location[0]
		y = location[1]
		# walk the list looking for a free hill at x,y, replace with sand
		for hill in self.hillslist :
			if x > hill.x - SIZE and x < hill.x + SIZE \
				and y > hill.y and  y < hill.y + SIZE:
				# x,y are in this hill box
				if hill.state == 'inUse' :
					hill.state = 'free'
					self.screen.blit(self.sand_bgn, (hill.x - SIZE, hill.y - SIZE))
					return
		
	# load_pgn def of class Hills
	# Desc: load a .png picture
	# Parm: name - file name, local directory only
	def load_png(self, name):
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

	# Hills inner class of class Hills
	# Desc: defines a hill object. Sets state to inUse.
	# Note: a hill cannot be printed - it contains a sprite
	class Hill( pygame.sprite.Sprite ):
		# __init__ def of classs Hill
		# Desc: create a hill with state 'inUse' 
		def __init__(self, x, y):
			self.x = x
			self.y = y
			self.sprite = pygame.sprite.Sprite
			self.state = 'inUse'
	

