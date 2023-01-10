# module Tools - 
# Desc: provide tools for unit testing and logging
# Classes: Tools includes:
#    Debug - with logging or print support. Default is to print.
#        To use logging call start_logging(), then call print_debug(False)
#        To direct back to printing call print_debug(True)
#    Help - displays help pages
#    Write - show text on the screen
# Author: Brad Denniston
# Version: 0.3 - 13 jan 2020

import logging  # for logging
import datetime # for logging
import time     # for logging
import pygame
import cmath
	
TEST = False
	
# -------------------------------------
# CLASS Debug of module tools
class Debug():
	# Def: __init__ of class Debug
	# Usage: public
	def __init__(self, config) :
		global TEST
		TEST = config['test']
		self.logging_enabled = False   # logging not enabled, prints messages
		# implement Python logging - not active till debug_state != 'print'
		self.log = None
		
		# self_test complex	add and multiply	
		self.c = Cplx()
		#self.c.cplx_test()
		
    # Def: debug - method of class Debug
    # Desc: - send the message to print or logfile
    # Parm: message - text to be logged or printed
	def debug( self, message ) :
		if self.logging_enabled == False :
			print(message)
		else :
			logging.DEBUG(message)
	
	# Def: print_debug of class Debug
	# Desc: Enable debugging to print to screen
	#     else send messages to a log file
	# Parm: enable - set to True to print, False to log
	#       At init messages are printed
	def print_debug( self, enable ) :
		if enable == True :
			self.logging_enabled = False    # print the messages
		elif self.log == None :
			print('ERROR: logging has not been set up')
		else :
			self.logging_enabled = True   # send to log file
	
	# Def: deg2rad of class Debug
	# Parm: degrees
	# Return: radians
	def deg2rad( self, deg ):
		return deg / 180 * cmath.pi
		
	# Def: rad2deg of class Debug
	# Parm: radians
	# Return: degrees
	def rad2deg( self, rad ):
		return rad * 180 / cmath.pi	

	# ---------------------
    # Def: start_logging for class Debug
    # Desc: provide python based logging, overwrites existing file.
    # Return: returns python log handle. Use as log.debug(message)
    # Usage: startup
	def start_logging(self):
		logFilename = './dunebuggy.log'
		logger_date = "%04d%02d%02d" % (dtNow.year, dtNow.month, dtNow.day)

		self.log = logging.getLogger()
		self.log.setLevel(logging.DEBUG)
		formatter = logging.Formatter(
			fmt = '%(asctime)s %(levelname)s: (%(filename)s:%(lineno)d) %(message)s', datefmt='#H:%M:%S')
		self.fileHandler = logging.FileHandler(filename = self.logFilename)
		self.fileHandler.setFormatter(formatter)
		self.log.addHandler(self.fileHandler)

    # ---------------------
    # Def: log_off for class Debug
    # Desc: disable printing or logging to file
	# Usage: startup
	def log_off(self, log, file_handler):
		self.log.removeHandler(self.file_handler)
		self.log = None
		self.logging_enabled = False


	# DEF: printc of class Debug
	# Desc: convert complex to mag,degrees and round to 5 places then print
	# Parm: value - complex value
	def printc(self, text, value):
		mag, radians = cmath.polar(value)
		angle = int(10000 * (radians * 180 / cmath.pi)) / 10000
		mag = int(10000 * mag) / 10000
		print( text, 'Mag='+str(mag), 'Deg='+str(angle))

		
# ------------------------------------------
# Class Cplx - complex add and multiply
# Provide complex addition and multiplication
class Cplx :
	# Def: cadd - add two complex numbers
	# Parm - a, b - complex numbers
	# Return complex 
	def cadd( self, a, b) :
		return ((a.real + b.real) + (a.imag + b.imag) * 1j)
		
	# Def: csub - add two complex numbers
	# Parm - a, b - complex numbers
	# Return complex 
	def csub( self, a, b) :
		return ((a.real - b.real) + (a.imag - b.imag) * 1j)
		
	# Def: cmul - multiply two complex numbers
	# Parm - a, b - complex numbers
	# Return complex 
	def cmul( self, a, b) :
		real_part = a.real * b.real - a.imag * b.imag
		imag_part = a.real * b.imag + a.imag * b.real
		return (real_part + imag_part * 1j)
		
	# Def: cplx_test - test complex add and multiply
	def cplx_test( self ) :
		# if TEST: return
		if TEST:
			a = (5 + 1j * 5) # mag is 7
			b = (3 + 1j * 4) # mag is 5, angle is 
			if self.cadd(a,b) != (8+9j) : print('cadd is FALSE')
			if self.csub(a,b) != (2+1j) : print('csub is FALSE')
			if self.cmul(a,b) != (-5+35j) : print('cmul is FALSE')

			print("complex test add a",a, "+ b",b,"=", self.cadd(a, b))
			print("complex test sub a",a, "- b",b,"=", self.csub(a, b))
			print("complex test mul a",a, "* b",b,"=", self.cmul(a, b))


# ------------------------------------------
# Class Write - write text to the screen
class Write :
	def __init__(self) :
		self.text_size = 32           # 32  #  The size of the text
		self.right_column_size = 150  # 150 #  The size of the column on the right
		self.button_height = 50       # 50  #  The height of the button
		self.button_border_size = 3   # 3   #  The size of the border of the button
		self.win_message_width = 500  # 500 #  The width of the win message
		self.win_message_height = 300 # 300 #  The height of the win message
		self.color = (0,0,0)
		self.font = "Arial"  
        
    # ---------------------------------------------------------
    # Def: write - for class Tools
	#		used by - 
    # Desc: Puts text onto the screen at point x,y. 
    #     Note that these values relate to x and y respectively whatever the
    #     rotation, which is in degrees. Max_len allows you to wrap a line if
    #     it becomes too long; the text will be restricted to being that many
    #     pixels long, and if it gets longer a new line will be started.
    # Param: screen - display area
    # Param: x - horizontal offset in pixels from the screen left edge
    # Param: y - vertical offset upwards in pixels from the screen bottom
    # Param: text - characters to write
    # Param: color - font color
    # Param: size - font size
    # Param: max_len - default is None
    # Param: gap - defaults to 0
    # Param: font - font type defaults to simFont
    # Param: rotate - defaults to 0 degrees
    # Param: alignment - The alignment variable, if used, can take: first value
    #          left\", \"center\" or \"right\"
    #          and the second value can be \"top\", \"center\" or \"bottom\".
    # Return: count of extra space
	def write(self, screen, x, y, text, color, size, max_len=None, gap=0, rotate=0,
			alignment=("left", "top")):
        
		font_obj = pygame.font.SysFont(self.font, size)
		if text == "":  # if it's a blank line
			line = 1
			extra_space = size
		else:
			line = 0
			extra_space = 0
		while len(text.split()) > 0:  # while there is still text that hasn't been written
			line += 1
			game_surface = pygame.transform.rotate(font_obj.render(text, False, color), rotate)
			used = len(text.split())  # the amount of text not used so far - uses less until it fits
			while max_len is not None and game_surface.get_width() > max_len:  # within limits, if
				used -= 1                               # any, then starts a new line and does it again
				game_surface = pygame.transform.rotate(font_obj.render(" ".join(text.split()[:used]),
							False, color), rotate)
			game_rect = game_surface.get_rect()
			a, b = game_surface.get_size()
			if alignment[0] == "center":
				new_x = x - a // 2
			elif alignment[0] == "right":
				new_x = x - a
			else:
				new_x = x
			if alignment[1] == "center":
				new_y = y - b // 2
			elif alignment[1] == "bottom":
				new_y = y - b
			else:
				new_y = y
			game_rect.topleft = (new_x, new_y)  # where the two objects will be merged
			screen.blit(game_surface, game_rect)  # merges them
			y += game_surface.get_height() + gap
			extra_space += game_surface.get_height() + gap
			text = " ".join(text.split()[used:])  # deletes text used - it has been written,
		return extra_space                        # and is no longer needed    
        
# ------------------------------
# Class Help
#		used by 
# def display
# def draw
# def getSurfaces
class Help:
	#! ---------------------------
	#! DEF: __init__ for class Help
	def __init__(self):
		self.height = 600  # gets changed in the program depending on space taken up by help
		self.surfaces = self.get_surfaces()
		self.font = pygame.font.SysFont("Arial",8) 
		self.text_size  = 20
		self.title_size = 30
		self.indext_size = 40
		self.slider_width = 10
		self.slider_gap_size = 5
		self.slider_length = 100
		self.width = 1000 + slider_width + slider_gap_size
		self.scroll_amount = 50
		self.color = { 
			'background': (120,120,120),
			'text' : (0,0,0),
			'slider' : (0,244,100),
			}

	# -------------------------------------------
	# DEF: display of class Help
	# Desc: Displays the help page on the given screen
	# Param: screen
	def display(self, screen):
        
		print ('Help selected')
		pygame.display.set_caption("DuneBuggy Help")
		pygame.display.set_mode((self.width, self.surfaces[0].get_height()))
		screen.fill(self.color['background'])
		self.height = screen.get_height()
		slider_range = (self.slider_gap_size + self.slider_length // 2,
						self.height - self.slider_gap_size - self.slider_length // 2)
		slider_center = slider_range[0]
		help_rect = self.surfaces[0].get_rect()  # initialises the help surface to be written
		help_rect.topleft = (self.help_gap_size, self.help_gap_size)
		screen.blit(self.surfaces[0], help_rect)  # puts help surface onto the screen
		self.draw(screen, self.surfaces[1], slider_center, slider_range)
		slider_last_turn = False/config.help_scroll_amount
		while True:
			events = pygame.event.get()
			if check_quit(events):
				break
			x, y = pygame.mouse.get_pos()
			if pygame.mouse.get_pressed()[0]:
				if slider_last_turn:
					y = max(min(y + slider_center - mouse_start, slider_range[1]), slider_range[0])
					self.draw(screen, self.surfaces[1], y, slider_range)
				elif -2 * config.slider_gap_size - config.slider_width < x - self.width < 0:
					slider_last_turn = True
					mouse_start = y
					if not slider_center - config.slider_length / 2 <\
						y < slider_center + config.slider_length / 2:  # if mouse was not clicked
						slider_center = y  # directly on top of the slider
			elif slider_last_turn:
				slider_last_turn = False
				slider_center += y - mouse_start  # reset the position of the slider
			if x > (self.width - config.help_slider_width - self.section_gap_size) / 2 - self.slider_gap_size:
				draw = False
				for e in events:
					if e.type == pygame.MOUSEBUTTONDOWN:
						if e.button == 4:  # if scrolled down
							slidercenter = max(slidercenter - self.ScrollAmount, sliderRange[0])
							draw = True
						if e.button == 5:  # if scrolled up
							slidercenter = min(slidercenter + self.ScrollAmount, sliderRange[1])
							draw = True
				if draw:
					self.draw(screen, self.Surfaces[1], slidercenter, sliderRange)
			pygame.display.update()
			fps_limiter.tick(config.FPS)
    
    # -------------------------------------------
    # DEF: draw of class Help
    # Desc: Draws the right hand side of text & slider at given levels
    # Param: screen - the frame to write to
    # Param: help_surface
    # Param: slider_center
	def draw(self, screen, help_surface, slider_center, slider_range):
        
		pygame.draw.rect(screen, config.help_color["Background"],  # draws over changing part of screen
                         ((self.width - config.slider_width - config.slider_gap_size)
                          // 2 - config.slider_gap_size, 0, self.width, self.height))
		pygame.draw.rect(screen, self.color["Slider"],  # draws slider
                         (config.slider_width - config.slider_gap_size - config.slider_width,
                          slider_center - self.slider_length // 2,
                          config.slider_width, config.slider_length))
		help_rect = help_surface.get_rect()
		text_range = (config.help_gap_size, help_surface.get_height()
                      - self.height + 2 * config.help_gap_size)
		top_y = text_range[0] - (text_range[1] - text_range[0]) * (slider_center - slider_range[0])\
                                // (slider_range[1] - slider_range[0])  # where the help surface is
		help_rect.topleft = (int((config.help_width - config.slider_width) // 2) + config.slider_gap_size, top_y)
		screen.blit(help_surface, help_rect)# sets position of help surface in relation to the screen
		pygame.display.update()

    # -------------------------------------------
    # DEF: get_surfaces of class Help
    # Desc: Gets the surfaces for the help screen. this needs to only be called once,
    #     and the surfaces saved to a variable, as it takes a while to run
    # Returns: array of help surfaces to be displayed via slider
	def get_surfaces(self):
		text = open("help.txt").read().split("++")  # split into the two sections
		for section in range(len(text)):
			text[section] = text[section].split("\n")  # splits into lines
		help_surfaces = []
        
		for section in text:
			extra = 0  # first time is to see how big the surface must be to fit the text,
			for _ in range(2):  # the second time it writes it onto a surface of that size
				help_surface = pygame.Surface(((self.width - config.slider_width)
                                               // 2 - config.help_gap_size - config.slider_gap_size,
                                               extra))
				help_surface.fill(config.help_color['Background'])
				extra = 0
				for line in section:
					if line.startswith("**"):  # bold text - titles etc.
						size = config.help_title_size
						line = line[2:]
					else:
						size = config.help_text_size
					indent = 0
					while line.startswith("--"):  # indented text
						indent += 1
						line = line[2:]
    	               # screen, x, y, text, color, size, max_len = None, gap = 0, 
    	               # font=config.font, rotate = 0, alignment = ("left", "top")):
					maxLen = (help_surface.get_width() - indent * config.help_indent_size) + \
						config.help_gap_size
					extra += self.write(help_surface, indent * config.help_indent_size, extra, line,
							self.color["Text"], size, max_len = maxLen )
				help_surfaces.append(help_surface)
		return help_surfaces
        
