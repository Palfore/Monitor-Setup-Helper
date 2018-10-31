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
	'desktop' : (1, 'dp'),
	'mac' : (3, 'dp'),
	'laptop' : (2, 'dp'),  # You could also connect your laptop to hdmi
	'hdmi1' : (1, 'hdmi'),
	'hdmi2' : (2, 'hdmi'),
	'hdmi3' : (3, 'hdmi'),
	'tbd_mdp' : (1, 'mdp'),
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


class Cable:
	def __init__(self, input, output):
		self.input = input
		self.output = output

class Device:
	def __init__(self, name, outputs):
		self.name = name
		self.outputs = outputs

class Monitor2:
	def __init__(self, index):
		self.index = index
		self.inputs = ['dp', 'mpi', 'hdmi']

class Connection:
	def __init__(self, device, output, monitor, input, supports_daisy_chaining=False):
		self.device = device
		self.device_output = output
		self.monitor = monitor
		self.monitor_input = input
		self.supports_daisy_chaining = supports_daisy_chaining

cables = [
	Cable('hdmi', 'hdmi'),
	Cable('usb-c', 'dp'),
	Cable('mdp', 'dp'),
]

devices = [
	Device('desktop', ['usb-c', 'hdmi']),
	Device('laptop', ['usb-c', 'hdmi']),
	Device('mac', ['mdp']),
]

class Setup:
	def __init__(self, number_of_monitors):
		self.num_monitors = number_of_monitors
		self.connections = [
			Connection(devices[0], 'usb-c', 1, 'dp', supports_daisy_chaining=True),
			Connection(devices[0], 'hdmi', 1, 'hdmi'),
			Connection(devices[1], 'usb-c', 2, 'dp', supports_daisy_chaining=True),
			Connection(devices[1], 'hdmi', 2, 'hdmi'),
			Connection(devices[2], 'mdp', 3, 'dp'),
		]

	def get_connection(self, monitor, input):
		for c in self.connections:
			if (c.monitor == monitor) and (c.monitor_input == input):
				return c
		raise ValueError("Could not find that connection: ", monitor, input)

	def what_is_displayed(self, input_types, monitor):
		''' input_types are the current input-sources on each monitor: ['hdmi, 'dp', 'mdp'] 
			This will output what is being displayed, for example if monitor 3 is requested:
			it would output (2, 'dp') indicating it is showing the displayport output from monitor 1.
			Also returns (-, -, 'made use of daisy chaining')
		'''
		def get_input(monitor):
			''' Provides indexing without confusing 'previous monitor' for monitor - 1. '''
			return input_types[monitor - 1]

		if monitor < 1:
			raise ValueError("Must be +")
		if monitor > len(input_types):
			raise ValueError("less than")
		
		if monitor != 1:
			if get_input(monitor) == 'mdp':  # Handle daisy chaining
				previous_monitor, previous_input, _ = self.what_is_displayed(input_types, monitor-1)
				if previous_input == 'dp':
					if self.get_connection(previous_monitor, 'dp').supports_daisy_chaining:
						return (previous_monitor, previous_input, True)
				return (monitor, None, False)  # Daisy-chaining can't work any other setup.

		return (monitor, get_input(monitor), False)


	def whole_display(self, arrangment):
		# assert arremgnts size is number of moitores
		return [self.what_is_displayed(arrangment, i) for i in range(1, self.num_monitors+1)]

	def how_to_get(self, users_request):
		request = [personal_setup_get(r.lower()) for r in users_request]

		# All possible monitor input-sources
		configurations = []
		for arrangment in itertools.product(['hdmi', 'mdp', 'dp'], repeat=3):
			configurations.append((arrangment, self.whole_display(arrangment)))

		# check lengths of  num_monitors == request == output
		# imporove this to use self.connections and (global) cables otherwise it isn't accurate.
		# because multiple connections may exists and are not captured here.
		possible_input_types = []
		for inputs, outputs in configurations:
			print(inputs, outputs, request)
			if all(not request[i] or (request[i][0] == outputs[i][0] and request[i][1] == outputs[i][1]) for i in range(self.num_monitors)):
				daisy_chained = ['M' + str(i+1) + ' to M' + str(i) for i, o in enumerate(outputs) if o[2]]
				message = 'by chaining ' + ' and '.join(list(reversed(daisy_chained)))
				this_input = (inputs, message) if any([o[2] for o in outputs]) else inputs
				possible_input_types.append(this_input)

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




































