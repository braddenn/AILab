# Module: AIlab.py - program start - there is no main()
#
# Description:
# main but withou a 'main()'
# AI/user controlled Dune Buggy moves towards an exit.
# 	It avoids blocks (hills) detected by radar sensors.
#	The observer can set/unset blocks.
#
# Program Structure:
# 	pygame - imported library to support screen, graphics and actors.
#	AILab - starts in this module. NOTE: there is no main. Execution starts here.
#	desertmap - map implemented in desert version
#		Draws the user viewable surface, help text and menu on the screen.
#	vehicle - define and manage vehicle and hill sprites
#	tools - (optional) logging, debug, write, help
#	button - provides menu button objects
#	neuronNetCmplx - AI of neurons, complex math to control vehicle
#	This is based on Neuron.py that only uses real math.
#
#	History:
#		Based on version 2 which is just a working AI based on github code
#	Author: Brad Denniston
#	Version: 0.2, 18 Dec 2019 

# import python game module
import pygame
from pygame.locals import *
   
import time
import json

# local simulator imports
import desertmap
import tools

# how fast the simulation runs
fps = 5    

pygame.init()
if not pygame.font.get_init() :
	pygame.font.init()

config_file = open("config-ailab1.jsn")
# To validate the config file uncomment the next two lines
# pp = pprint.PrettyPrinter(indent=2)
# pp.pprint(config_file)
json_string = config_file.read()
config = json.loads(json_string)  # converts JSON to a dictionary

# build a new map (frame and menu) on the screen
# may be replaced with other maps
sim_map = desertmap.SimMap(config)

# Set up and respond to events
# Turn off all events so that
# PyGame will now not check for any inputs
pygame.event.set_allowed(None)

# enable a few events for this program
allowed_events = (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN,
	pygame.MOUSEBUTTONUP, pygame.KEYDOWN, pygame.KEYUP, pygame.QUIT)
for event in allowed_events:
	pygame.event.set_allowed(event)

# now get and process user events, take a step
fps_clock = pygame.time.Clock()

# User Interaction
# menu buttons:
#	0 - Load - Stop running, set to Manual, load file
#	1 - Save - Stop running, set to Manual, write hills & state of vehicle to file
#	2 - Manual/AI mode - stop running
#			Manual - change to AI mode, button to AI
#			AI - change to manual mode , button to Manual
#	3 - Step - stop running
#			if manual take one Step
#			if AI take one step
#	4 - Run - Change button to Stop
#			Manual mode - run at previous speed, arrow keys change dir and step size
#			AI mode - run at previous speed, arrow keys change loop speed
#	
running = False
while True:
	# check for user action, then run a step
	for event in pygame.event.get() :
		if event.type == QUIT:
			# screen X, quit
			print('exiting')
			pygame.quit()
			sys.exit(0)

		# is this event a mouse action?
		elif event.type == pygame.MOUSEBUTTONUP:
			# reset the button image up not active
			sim_map.menu.check_menu(event)
			continue

		elif event.type == pygame.MOUSEBUTTONDOWN:
			# it is a menu button, get button name 
			menu_return = sim_map.menu.check_menu(event)
			if menu_return != 'scene' :
				sim_map.mouse_button(event)
				print(menu_return)
			
			if menu_return == 'Run':
				running = True
				sim_map.menu_run()
				
			elif menu_return == 'Load':
				sim_map.menu_load()
			
			elif menu_return == 'Save':
				print('Save')
				sim_map.menu_save()			
			
			elif menu_return == 'Manual':
				print('menu item is Manual')
				sim_map.menu_manual()

			elif menu_return == 'AI':
				print('menu item is AI')
				sim_map.menu_ai()
			
			elif menu_return == 'Step':
				# if running then stop, then take a step
				if running :
					running == False
					sim_map.menu_stop()
				sim_map.menu_step()
    
			elif menu_return == 'Stop':
				running = False
				sim_map.menu_stop()

			elif menu_return == 'Help':
				running = False
				sim_map.menu_help()
				# show help screen till user enters 'return' or ESC
				# help_display = frame.help()
                
			elif menu_return == 'Exit':
				# do you want to save first?
				sim_map.menu_exit()
				pygame.quit()
				exit(0)
                
		# no click on button, so check the direction keys
		elif event.type == KEYDOWN :
			sim_map.direction_key(event)

	# no valid user action, 
	# move the vehicle under AI or manual control
	if running :
		sim_map.menu_step()

	pygame.display.update()
	
	# slow everything down depending on size of fps
	fps_clock.tick(fps)
	# loop de loop


# check_exit def in main
# Desc: global, Checks whether the user tried to quit the sim with the ESC key.
# Param: events from keyboard via pygame
# Return: True if ESC hit, else False	for event in events: 
def check_exit(events):
	if event.type == pygame.QUIT: # the ESC key
		exit_sim()
	if pygame.key.get_pressed()[pygame.K_ESCAPE]:
		return True
	return False

# exit_sim def in main
# Desc: global, exits to OS	
def exit_sim():
	pygame.quit()
	exit(0)

    
