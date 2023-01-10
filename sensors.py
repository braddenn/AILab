# Module: sensors.py
# Desc: define and manage sensors on the vehicle
#
# Classes:
# class Sensors - detect the environment, pass results to the AI
#
# Author: Brad Denniston
# Version: 0.3, 9 Feb 2019 

# import python game module
import pygame
import cmath
import tools
TEST = False

# Sensors class of module sensors
# Desc: Sensors detect the environment, pass results to the AI.
# 	Object created by SimMap
# 	A sensor has a sine detection pattern (peak at 90 deg). Each sensor points in a 
# 	different direction. Add together all hill locations a sensor 
# 	sees modified by sensor pattern. X is the desired target signal. 
# 	Form X / (X + sum(Hi)) for the front sensor. Form
# 	1 / (X + sum(Hi)) for every other sensor. The X is preferred
# 	by the front sensor. Feed each sensor to a neuron. The optimal
# 	result is 1/1. 
class Sensors :

	# __init__ def of class Sensors
	# Desc: all angles are in radians relative to vehicle heading
	# Parm: vehicle - the element that is moved across the screen
	# Parm: hills - list of objects vehicle must avoid, target is the first one
	# Parm: sensor_angles - list, degrees off of vehicle heading for each sensor
	def __init__(self, vehicle, hills, config) :
		global TEST
		TEST = config['test']
		self.vehicle = vehicle
		self.hills = hills
		sensor_dict = config['sensors']
		self.num_sensors = sensor_dict["count"]
		# sensor focus angle in degrees off heading
		sensor_angles = sensor_dict["angles"]
		self.sensor_angles_rad = []
		self.sensor_angles_deg = []
		for sens in range(self.num_sensors):
			self.sensor_angles_deg.append(float(sensor_angles[sens]))
			self.sensor_angles_rad.append(self.deg_to_r(self.sensor_angles_deg[sens]))
		self.power_rcvd = 0.0
	
	# DEF: get_sensor_data def of class Sensors
	# Desc: for each sensor add vectors to each object.
	# 	lidar has rectangular profile, not affected by angle to object
	# 	lidar returns direction of object, not power
	#	radar has cosine profile, power = cos(angle), returns angle and power
	# 	Add one sensor for the target data
	# Parm: hills - list of hill location coordinates. Exit is the first one.
	# Return: list of neuron complex inputs, each sum of complex received 
	# 	return from each hill
	def get_sensor_data( self, hills ) :
		heading_rad = self.vehicle.heading_rad
		heading_deg = self.r_to_deg(heading_rad)
		sensor_inputs = []
		sensor_results = []
		if TEST : print('vehicle heading:', heading_deg, ', x to right, y is up')
		x_range = hills[0].x - self.vehicle.sloc_rect[0]
		y_range = hills[0].y - self.vehicle.sloc_rect[1] 
		self.power_rcvd = cmath.sqrt(x_range * x_range + y_range * y_range).real
		# for each sensor find sum of input vectors
		for sensor in range(self.num_sensors) :
			sensor_sum = 0
			if TEST : print('For sensor pointing at', self.sensor_angles_deg[sensor], 'degrees')
			for hill in hills : # hill 0 is the  target
				if TEST : print( '    For hill at x =', hill.x, 'y =', hill.y)
				x_range = hill.x - self.vehicle.sloc_rect[0]
				y_range = hill.y - self.vehicle.sloc_rect[1]
				if TEST : print("       x_range",x_range, "y_range", y_range)
				hill_angle_deg = self.r_to_deg(cmath.atan(y_range / x_range))
				sensor_to_hill_deg = (heading_deg + self.sensor_angles_deg[sensor] - hill_angle_deg).real
				sensor_to_hill_rad = self.deg_to_r(sensor_to_hill_deg)
				if TEST : print('       sensor', sensor, 'is at angle', int(sensor_to_hill_deg), 'to this hill' )
				# sqrt returns complex value
				distance_to_hill = cmath.sqrt(x_range * x_range + y_range * y_range).real
				if hill == hills[0] :
					result = complex( (1.0/distance_to_hill),(sensor_to_hill_rad))
				else:
					if TEST : print('       distance to hill:{}'.format(int(distance_to_hill)))
					if abs(sensor_to_hill_deg) > 90 : 
						print('        angle too big')
						power_rcvd = 0
					else:
						# antenna is a COS pattern, 0 at +/- 90 degrees
						power_rcvd = 1.0/distance_to_hill * cmath.cos(sensor_to_hill_rad).real
					result = power_rcvd * cmath.rect(distance_to_hill, sensor_to_hill_rad)
				if TEST :
					real,imag = self.trun_comp(result)
					print('       signal received: {}+{}j'.format(real, imag))
				sensor_sum += result

			# Each sensor/neuron input is sum of all hills and exit
			sensor_results.append(sensor_sum)
		return sensor_results

	# get_expected_result def of class Sensors
	# Return: (power received * 2 / range + 0j)  -  not affected by angle 
	def get_expected_result( self) :
		return (self.power_rcvd * 2 + 0j)
		
	def r_to_deg( self, radians ):
		return radians * 180 / cmath.pi
		
	def deg_to_r( self, degrees ):
		return degrees * cmath.pi/180
		
	# trunc complex values for printing
	# Return: real, imag
	def trun_comp( self, comp ):
		return int(comp.real * 1000 )/1000, int(comp.imag * 1000 )/1000