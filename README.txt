NOTE: This version does not work as complex math cannot (or I haven't
figured out how to use complex notation) be used to compute the error]
term at the final output to feed back to the weights. Need to go back
to the real version and have two separate arrays of inputs, one real and one
imaginary . TBD.

This app is directed to providing an AI experimentation lab.
It implements a complex math AI to move the dunebuggy like vehicle.
The display is a map with the dunebuggy.
Arrow buttons can be used to move the vehicle.
Code implements an AI that drives the vehicle through hills on the map.
It can print out the status (weights, current error, ...) of each step.
The AI structure is fully determined in JSON file config-ailab1.jsn

