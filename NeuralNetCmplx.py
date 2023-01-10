# Module: NeuralNetCmplx.py
# Desc: AI for AILab using complex math.
#	For input sets (one of several input lists) compute an output set. 
#	There is an output neuron that is trained for each input set.
#	This is a general purpose AI where the structure 
#	(#layers, #neurons/layer) is defined in a JSON configuration file.
#	Extension: applied to controlling vehicle movement
#	Extension: all math is complex 
#	Extension: prints state after each step if TEST is True in config
#
#	Comment references:
#	[1] Wikipedia article on Backpropagation
#		http://en.wikipedia.org/wiki/Backpropagation#Finding_the_derivative_of_the_error
#	[2] Neural Networks for Machine Learning course on Coursera by Geoffrey Hinton
#		https://class.coursera.org/neuralnets-2012-001/lecture/39
#	[3] The Back Propagation Algorithm
#		https://www4.rgu.ac.uk/files/chapter3%20-%20bp.pdf  
#
import random
import math
import cmath

TEST = False

# CLASS: NeuralNetCmplx class of module NeuralNetCmplx
# Desc: AI for complex input vectors, returns a complex adjustment
class NeuralNetCmplx:

	# DEF: __init__ def of class NeuralNetCmplx
	# Desc: The structure of this ANN is defined in a passed in dictionary
	#
	# Parm: config -  dictionary of configuration data
	# 	See the config file and AILab documentation
	#
	# Usage: public, started in the map module i.e. desertmap.py
	def __init__(self, config ):
		global TEST
		if config['test'] == 'true' :
			TEST =  True
		
		self.num_test_sets = config['test set count']
		self.structure = config['structure']
		self.targets = 1		# where target = s/(s+n) with n == 0
		
		#  Number of layers is input + possible hidden + output (min is 2, input and output)
		self.layers = self.structure['layers']
		self.num_layers = self.layers['count']
		if self.num_layers < 2 : 
			print ('Error: number of layers is less than 2')
			error_exit()
		self.num_outputs = self.num_test_sets				# number of input/output signals
		self.learning_rate = config['learning rate'] 	# somewhere around 0.001
		self.cycle_limit = config['cycle limit']     	# maximum number of steps
		# return once error is smaller than this value
		self.errlim_mag = config['error limit mag']
		self.errlim_ang = config['error limit ang']
		self.target_output = (0+0j)
		self.error_return = (0+0j)
		
		# create a list of layer dictionaries
		self.layers = list()
		for id in range(self.num_layers) :
			layer_dict = self.structure['layers'][str(id)]
			if id < self.num_layers :
				next_layer_dict = self.structure['layers'][str(++id)]
			else :
				next_layer_dict = None
			layer = Layer(id, layer_dict, next_layer_dict, self.learning_rate)
			if layer == 'error' :
				error_exit()
			self.layers.append(layer)
		self.sensor_inputs = list()

    # DEF: adapt def of class NeuralNetCmplx
	# Desc: The target is a signal, S, in the distance. A vehicle traverses
	# the field to get to the target. There are hills that block the vehicle. 
	# Each adapt step responds to new input data and returns a vehicle command.
	# 		Loop steps until minimum error or max cycle count
	# 		The goal is to avoid the hills and make S / (Sc + N) == 1
	# Parm: sensor_inputs - array of sensor inputs, target plus hill noise.
	# Parm: target_input - pure target signal, S, and no hill noise, N. 
	# Return: vehicle_command, a complex value of direction and speed.	
	# Usage: desert_map
	def adapt(self, sensor_inputs, target_input, step):
		self.sensor_inputs = sensor_inputs
		# apply the sensor data to the input layer
		# this data never changes until the next adaptation
		print('Adapt to sensor inputs:')
		for i in range(len(sensor_inputs)):
			sens_mag, sens_ang = cmplxToRect(sensor_inputs[i])
			print( '{} : mag = {} angle = {} deg'.format(i, sens_mag, sens_ang))
		targ_mag, targ_ang = cmplxToRect(target_input)
		print( 'Target: mag = {} angle = {} deg'.format(targ_mag, targ_ang))
		
		# support user input of single step
		if( step == True ) :
			return self.step( sensor_inputs, target_input )
			
		self.errlim_mag = self.errlim_mag + 10
		self.errlim_ang = self.errlim_ang + 180
		cycle_count = 0
		self.error_return = complex(self.errlim_mag + 10, self.errlim_ang + 180)
		e_mag,e_ang = cmplxToRect(self.error_return)
		print( 'e_mag:{}, e_ang:{}, cycle_count:{}'.format(e_mag, e_ang, cycle_count))
		print( 'maglim:{}, anglim:{}'.format(self.errlim_mag, self.errlim_ang))

		# else cycle....
		while((e_mag > self.errlim_mag \
			or e_ang > self.errlim_ang) \
			and cycle_count < self.cycle_limit) :
			vehicle_command = self.step( sensor_inputs, target_input )
			cycle_count += 1
			print( 'e_mag:{}, e_ang:{}, cycle_count:{}'.format(e_mag, e_ang, cycle_count))
		return vehicle_command
			
    # DEF: step def of class NeuralNetCmplx
	# Desc: one step in adaptation to new input data.
	#		Adapts weights to data, returns vehicle command
	# Assumptions: 
	#		AI structure is set by a config file.
	#		Output layer has num_outputs neurons where num_outputs
	#			is the number of training sets
	# Parm: inputs - list: state of the environment (input signals)
	#		There is a set of inputs for each target output.
	#		note: sensor_inputs must be normaized by magnitude
	# Parm: target_output - value of the target signal, no noise, normalized
	# Return: vehicle command, complex, of direction and speed 
	# Usage: public for one step and adapt if loop till below error limit
	def step(self, inputs, target_output ):
		
		# For signal Se as the independently received exit signal. 
		# and Signal Sc as the computed exit signal.
		# and N is the computed sum of hill signals, the noise.
		# the output of the last neuron is Sc + N.
		#
		# Set the output goal to Se / (Sc + N), i.e. reference / output.
		# Ideally N is 0 so the target value is Se / Sc == 1 at the exit.
		# If not yet at the exit, the error is the speed and direction to move.
		# So the error at the output is 1 - output.
		# Use the error to compute inner layer weight changes.
		
		# feed forward: propagate inputs through all layers
		# this applies the inputs to the  first layer outputs
		previous_outputs = inputs
		for layer in self.layers : 
			previous_outputs = layer.feed_forward(previous_outputs)
 
		# now the inputs have been passed through all neurons and
		# the final output is available. So:
		# backward propagation: feed the error back through the layers
		# to adjust the weights
		output_error = self.calculate_total_error(target_output)	
		mag, angle = cmath.polar(output_error)
		if TEST:
			rmag = round(mag)
			angle = round(angle)
			print('After feedforward, error is: {} at {} degrees'.format(rmag, angle))
			print('errlim_mag is', self.errlim_mag)
		
		if mag < self.errlim_mag :
			self.error_return = output_error
			return -1

		# walk backward through the layers to adjust weights
		# First put output_error into final virtual layer, "error"
		self.layers[self.num_layers - 1].setFinalError(output_error)

		# Then start from there and walk backwards to update the weights for the next round.
        # Calculate the derivative of the error with respect to the output of each layer neuron
        # dE/dyⱼ = Σ ∂E/∂zⱼ * ∂z/∂yⱼ = Σ ∂E/∂zⱼ * wᵢⱼ
		# The error at the neuron output is passed backward 
		# and reduced by the input weight. It is stored in the neuron input dictionary.
		# Pass error back to input through rest of the layers

		for layer_idx in range(self.num_layers-2, 0, -1) : 
			self.layers[layer_idx].back_propagation()
			# so: start at output, put error into each neuron weight in layer/neuron dict
			# Then go back one layer and do same for each neuron
			
		return 0
		
	# DEF: calculate_total_error def of class NeuralNetCmplx
	# Desc: calculate error over all input sets. 
	#		NOTE: Currently, this code	assumes that there is 
	#		only one input set and one output.
	# Parm: target_output - goal of regression
	# Return: sum of errors for all input sets.
	# Usage: called by step                                                                           
	def calculate_total_error(self, target_output):
		# NOTE: this calc is for only one output neuron
		final_output = self.layers[self.num_layers - 2].neurons[0].output
		# add these up for all outputs
		return 0.5 * (target_output - final_output) ** 2

# CLASS: Layer of module NeuralNetCmplx
# Desc: a vertical layer of neurons. Create and support the neurons of this layer
# Usage: NeuralNetCmplx.init
class Layer:
	# DEF: __init__ def of class Layer
	# Parm: layer_id - the numeric id of this layer, a string
	# Parm: layer_dict - a dictionary describing the layer:
	# Parm: next_layer_dict - holds 
	# Parm: learning_rate - manages rate of weight change during feedback			
	# Usage: public - see *map.py
	def __init__(self, layer_id, layer_dict, next_layer_dict, learning_rate):

		self.layer_id = layer_id
		self.layer_dict = layer_dict
		self.next_layer_dict = next_layer_dict
		self.learning_rate = learning_rate
		
		self.layer_type = layer_dict['type']  # type is input, hidden, or output
		self.bias = complex(layer_dict['bias'])
		self.neurons_dict = layer_dict['neurons']
		
		self.neurons = list()   # neurons in this layer
		
		# create the neurons for this layer
		self.neuron_dict = layer_dict['neurons']
		self.neuron_count = self.neuron_dict['count'] # number of neurons in this layer
		for id in range(self.neuron_count):
			self.neurons.append( Neuron(self.layer_id, self.bias, id, \
				self.neuron_dict[str(id)], self.layer_type, learning_rate ))			
	
    # DEF: feed_forward def of class Layer
	# Desc: called layer by layer, layer outputs are next layer inputs.
	# Parm: inputs - set of input values that go to each neuron in the layer
	# Return: a list of computed output values, one per neuron in this layer 
	# Usage: local
	def feed_forward(self, inputs):
		outputs = []
		# support user input of single step
		print('LAYER {} Type {} Bias {}'.format(self.layer_id, self.layer_type, self.bias))
		for neuron_indx in range(self.neuron_count):
			outputs.append(self.neurons[neuron_indx].feed_forward( inputs, neuron_indx ))
		return outputs
	
	# DEF: setFinalError def of class Layer
	# Parm: value of the final output error
	# Usage: local
	def setFinalError(self, output_error):
		error_neuron = self.neurons[self.neuron_count - 1]
		error_neuron.setFinalError( output_error )
	
	# DEF: back_propagation def of class layer
	# Desc: for each neuron, sum the errors from connected inputs
	# 		in the next layer. Use the sum to modify the input weights.
	def back_propagation(self):
		for neuron_id in range(self.neuron_count):
			neuron = self.neurons[neuron_id]
			neuron.back_propagation(self.neuron_dict[str(neuron_id)], self.next_layer_dict)
			
	# DEF: get_outputs def of class Layer
	# Return: list of the output from each neuron 
	# Usage: public (print_state of class NeuralNetCmplx)
	def get_outputs(self):
		outputs = list()
		for neuron in self.neurons:
			# append output of each neuron to a list
			outputs.append( neuron.output )
		return outputs
				
# CLASS: Neuron of module NeuralNetCmplx
# Desc: a single AI neuron - all weights and calculations
class Neuron:
	# DEF: __init__ of class Neuron
	# Desc: create a neuron, connect outputs to next layer, set/adjust weights
	# Parm: layer_id - number of this layer
	# Parm: layer_bias - a complex value
	# Parm: neuron_dict - dictionary of neuron configuration
	# Parm: layer type: input, hidden, output
	# Parm: learning_rate - controls rate of weight change
	# Usage: created/referenced by class Layer
	def __init__(self, layer_id, layer_bias, id, neuron_dict, layer_type, learning_rate):
		self.layer_id = layer_id
		self.neuron_id = id
		self.bias = layer_bias		# complex
		self.inputs_dict = neuron_dict['inputs']  # returns the backward prop err value
		self.dest_dict = neuron_dict['destinations'] # list of output connections
		self.type = layer_type
		# expected value at output layer, S/(S+N) where N == 0
		self.learning_rate = learning_rate
		
		self.num_inputs = self.inputs_dict['count']
		self.inputs = [0j] * self.num_inputs
		
		# read in the initial weight values
		self.weights = [(0+0j)] * self.num_inputs    # each input has a weight
		for wt_cnt in range(self.num_inputs) :
			cmp_num_str = self.inputs_dict[str(wt_cnt)]
			self.weights[wt_cnt] = complex(cmp_num_str[0]) # convert string to complex
		self.output = (0+0j)
	
	# DEF: feed_forward of class Neuron
	# Desc: for an input set, compute the output as sum of weighted inputs.
	#     Always squash the output to limit range to 0:1. 
	#     If complex just squash the magnitude
	# Parm: inputs - either from sensors or outputs from previous layer
	# Return: inputs summed then squashed
	# Usage: layer.feedforward
	def feed_forward(self, inputs, neuron_index ):
		if self.type == "inputs" : # just return this one input signal
			self.output = inputs[0]
		else :
			self.output = self.bias
			for ndx in range(self.num_inputs):
				self.output += (inputs[ndx] * self.weights[ndx])
			# squash the magnitude to 0..1 (NOT -1..1, angle does that)
			# This is the sigmoid function.
			self.output = self.squash(self.output)
		
		# print each input, weight and the output
		if TEST:
			print('Neuron {}'.format(neuron_index))
			for ndx in range(self.num_inputs):
				inmag,inang = cmplxToRect(inputs[ndx])
				wtmag,wtang = cmplxToRect(self.weights[ndx])
				print('    input {}: {} at {} deg  weight {} at {} deg.'.format(ndx, inmag, inang, wtmag, wtang))
			mag,ang = cmplxToRect(self.output)
			print('    output {} at {} degrees'.format( mag, ang))
			print()
		return self.output
		
	# DEF: squash def of class Neuron
    # Apply the logistic function to squash the output of the neutron
	# This is complex math so only squash the magnitude.
	# Usage: local
	def squash(self, total_net_input):
		mag, angle = cmath.polar(self.output)
		mag =  1 / (1 + math.exp(-abs(mag)))
		# back to complex with new magnitude
		return complex(mag, angle)

	# DEF: setFinalError def of class Neuron
	# Parm: value of the final output error
	# Usage: local
	def setFinalError(self, output_error):
		self.inputs_dict['0'][1] = output_error
		# this must be called for each layer/neuron. is it?
		print('Output error: ', output_error)

	# DEF:  back_propagation of class neuron
	# Desc: gradient descent feed_back for each neuron output
	#		For each neuron the output error is the sum the errors 
	#		from next layer inputs that are connected to this neuron output.
	# 		New weight = input weight - sum * learning rate
	# 		To start, already put final error into the 'error' layer neuron 0, input 0.
	#		See setFinalError()
	# Parm: neuron_dict - provides destinations info for this neuron
	# Parm: next_layer_dict - dictionary of next layer neuron dictionaries 
	#		where the feedback error values are. 
	#		They were calculated during forward propagation.
	# Usage: class Layer.back_propagation
	def back_propagation(self, neuron_dict, next_layer_dict) :
		dest_dict = neuron_dict['destinations']
		next_neurons_dict = next_layer_dict['neurons']

		# collect one sum of all destination inputs back to this neuron
		error_sum = (0+0j)
		
		# to collect and sum errors: walk destinations list in the config file
		# list entries are pairs: neuron id and input id
		#	"neurons" :
		#		"count" : 3,
		#		"0",
		#			{
		#			"destinations" :
		#				{
		#				"count" : 3, 
		#				"dests" : [0, 0, 1, 0, 2, 0]
		#				}
		
		# get the destinations list count (list size) and then the list
		dest_count = neuron_dict['destinations']['count']
		dest_dests_list = neuron_dict['destinations']['dests']
		
		# apply the feedback error at the output to modify each input weight
		for dests in range(0,dest_count,2):
			# list entries are pairs: neuron id and input id
			dest_neuron_id = str(dest_dests_list[dests])
			dest_input_id  = str(dest_dests_list[dests + 1])
			# "inputs" :
			#	{
			#	"count" : 1,
			#	"0" : ["1.0+0j","0+0j"] which are: input weight, error fed back to this input]
			#	},
			dest_neuron_inputs_dict = next_neurons_dict[dest_neuron_id]['inputs']
			error = complex(dest_neuron_inputs_dict[dest_neuron_id][1])
			# add all the next layer errors together to feed back total error for this neuron
			error_sum =  error_sum + error
			
		# Now adjust the input weights of this neuron
		print('error sum, before weights:', error_sum, self.weights)
		for w_index in range(self.num_inputs):
			self.weights[w_index] -= error_sum * self.learning_rate
		print('after weights:', self.weights)

# DEF: cmplxToRect
# Desc: convert complex # to mag,degrees with accuracy to 5 digits
# Parm: complex #
# Return: magnitude, angle
def cmplxToRect( cmplx ):
	mag, rads = cmath.polar(cmplx)
	degrees = round(angle(rads))
	mag = round(mag)
	return mag, degrees

# DEF: round
# Parm: value: small value to be truncated/rounded
# Return: value limited to 5 digits
def round(value):
	return( int(value * 10000) / 10000)	

# DEF: angle
# Desc: convert double radians to degrees in whole values  
# Parm: value - radians                                                                       
def angle(value):
	return int(10000 * (value * 180 / cmath.pi)) / 10000

# DEF: error_exit of module NerualNetCmplx.py
def error_exit() :
	pygame.quit()
	sys.exit(0)

# DEF: print_complex of module NeuralNetCmplx
# Desc: convert complex to mag,degrees and round to 5 places then print
# Parm: value - complex value
def print_complex(value):
	mag, radians = cmath.polar(value)
	angle = int(10000 * (radians * 180 / cmath.pi)) / 10000
	mag = int(10000 * mag) / 10000
	print(mag, angle)
		
# ------------------Supplemental Information ---------------------------	
#
# j - sets of inputs. 
# yⱼ - one output for each input set, j.
# Tⱼ - target output for an input set
# E - final error.
#
# ----------------------------------------------------------------------
# Backward Propagation: Determine how much a neuron's total input has 
# to change to move closer to the expected output 
# by feeding back the error, E, neuron by neuron. Each weight reduces
# the feed back error to the previous neuron. Then the weight is changed
# by the error amount.
#
# We have the partial derivative of the error, E, with respect 
# to the each output, yⱼ, for j input sets and j outputs:
#     (∂E/∂yⱼ)
# and the derivative of the outputs, yⱼ, with respect to the 
# total net input (dyⱼ/dzⱼ) 
#
# So we can calculate the partial derivative of the error with 
# respect to the total net input. This value is also known as the 
# delta (δ):
# δ = ∂E/∂zⱼ = ∂E/∂yⱼ * ∂yⱼ/∂zⱼ
#
#def calculate_pd_error_wrt_total_net_input(self, target_output):
#    self.calculate_pd_error_wrt_output(target_output) \
#    * self.calculate_pd_total_net_input_wrt_input();
#
# which reduces to:
#    -(T - E) * E * (1 - E)
#
# The partial derivative of the error with respect to actual output
# then is calculated by:
#     2 * 0.5 * (T - E) ^ (2 - 1) * -1
#     = -(T - E)
#     = (E - T)
#
# Alternative, you can use (T - yⱼ), but then need to add it during backpropagation [3]
#
# Note that the actual output of the output neuron is often written as yⱼ and target output as tⱼ so:
# = ∂E/∂yⱼ = -(tⱼ - yⱼ)
#
#def calculate_pd_error_wrt_output(self, target_output):
#	return -(target_output - self.output)
#
# The total net input into a neuron is squashed using
# the logistic function to calculate the neuron's output:
# yⱼ = φ = 1 / (1 + e^(-zⱼ))
# Note that where ⱼ represents the output of the neurons in 
# whatever layer we're looking at and ᵢ represents the layer after it.
# For complex values ignore the phase, only use the magnitude. This is
# because squashing the magnitude prevents runaway feedback, squashing
# the phase does not.
#
# The derivative (not partial derivative since there is only one variable) of the output then is:
# dyⱼ/dzⱼ = yⱼ * (1 - yⱼ)
#
#def calculate_pd_total_net_input_wrt_input(self, output):
#	return output * (1 - output)


