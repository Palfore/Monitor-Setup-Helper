''' This script asks the user which inputs they would like to see on their monitors, and provides
	them with the appropriate settings.
	There are a few key assumptions:
		1) 3 Dell U2141-H monitors are setup as follows:
			[Monitor 1] - dp_out -> [Monitor 2] - dp_out -> [Monitor 3 (mst-off)]
		2) Both

'''
import itertools
from easygui import msgbox, choicebox

personal_setup = {
	'desktop' : ('1', 'dp'),
	'mac' : ('3', 'dp'),
	'laptop' : ('2', 'dp'),  # You could also connect your laptop to hdmi
	'hdmi1' : ('1', 'hdmi'),
	'hdmi2' : ('2', 'hdmi'),
	'hdmi3' : ('3', 'hdmi'),
	'tbd_mdp' : ('1', 'mdp'),
	"doesnt matter" : None
}

def personal_setup_get(input):
	''' Looks up the input corresponding to the users personal_setup.
		The personal_setup gives names to the inputs into the monitors.
		For example an entry 'desktop': ('1', 'dp') shows that the user's
		desktop is connected to the displayport of monitor 1. This makes user
		requests much easier.
		@param input The input to lookup.
	'''
	if input in personal_setup:
		return personal_setup[input]
	else:
		return input

class Monitor:

	@staticmethod
	def displaying(input_types, monitor):
		# Check monitor > 0 and < len(input_types)
		if monitor < 0:
			raise ValueError("Must be +")
		if monitor >= len(input_types):
			raise ValueError("less than")
		
		if monitor == 0:
			return (monitor, input_types[monitor])
		else:
			if input_types[monitor] == 'mdp':  # Handle daisy chaining
				previous_monitor, previous_input = Monitor.displaying(input_types, monitor-1)
				if previous_input == 'dp':
					return (previous_monitor, previous_input)
				else:
					return (monitor, None)  # Daisy-chaining can't work any other setup.
			else:
				return (monitor, input_types[monitor])

		raise ValueError("Something went horribly wrong.")

	@staticmethod
	def displaying_nice(arrangment, monitor):
		temp = Monitor().displaying(arrangment, monitor  -1)
		display = (str(int(temp[0]) + 1), temp[1])
		return display

class Setup:
	def __init__(self, number_of_monitors):
		self.num_monitors = number_of_monitors

	def whole_display(self, arrangment):
		# assert arremgnts size is number of moitores
		return [Monitor.displaying_nice(arrangment, i) for i in range(1, self.num_monitors+1)]

	def how_to_get(self, users_request):
		request = [personal_setup_get(r.lower()) for r in users_request]
		configurations = []
		for arrangment in itertools.product(['hdmi', 'mdp', 'dp'], repeat=3):
			configurations.append((arrangment, self.whole_display(arrangment)))

		# lengths of  num_monitors == request == output
		possible_input_types = []
		for inputs, outputs in configurations:
			if all(not request[i] or (request[i] == outputs[i]) for i in range(self.num_monitors)):
				possible_input_types.append(inputs)

		# Output if daisy chaining and from where to where

		response = 'To get: ' + str(users_request) + '\n'
		if not possible_input_types:
			response += "There is no way to do that.\n"
		elif len(possible_input_types) == 1:
			response += "Set your monitor inputs to:\n"
			response += '\t' + str(possible_input_types[0]) + '\n'
		else:
			response += "There are multiple ways to do that:\n"
			for input_types in possible_input_types:
				response += '\t' + str(input_types) + '\n'
		return response

	def prompt_user(self):
		msg = lambda n: f"What would you like monitor {n} to display?"
		title = "Monitor Setup"

		request = []
		for i in range(1, self.num_monitors+1):
			choice = choicebox(msg(i), title, [k.title() for k in personal_setup.keys()])
			if not choice:  # Exit if the user cancels
				return
			request.append(choice)
		msgbox(self.how_to_get(request), "Monitor Inputs")

if __name__ == '__main__':
	Setup(3).prompt_user()




































