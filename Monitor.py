''' This script asks the user which inputs they would like to see on their monitors, and provides
	them with the appropriate settings.
	
	There are a few key assumptions:
		1) 3 Dell U2141-H monitors are setup as follows:
			[Monitor 1] - dp_out -> [Monitor 2] - dp_out -> [Monitor 3 (mst-off)]
			Each has three inputs port: [dp, mdp, hdmi]
		2) Devices are not limited to the number of monitors they can output to, or daisy-chain to.
			This would only be an issue for older devices connecting to more than 3 monitors.

	There are some definitions:
		0) daisy-chaining: The act of passing the output of one monitor into another to display one device on multiple monitors.
		1) monitor = monitor_index: Refers to the enumerated index of the monitor. *
		2) monitor_inputs: The input_port of the monitor.
		3) input_source = monitor_input_source: The monitor setting which selects which monitor_input to display.
		4) monitor_output: The monitor_input being displayed on a given monitor. **
		5) monitor_devices = monitor_displayed_devices: The actual device being displayed on the monitor. **

	
		* Note that there is the programatic [0, n] and user-friendly [1, n-1].
		** Note that due to daisy-chaining this is not just the input_source.


	Limitations:
		1) Doesn't handle asking for nothing to be displayed on a monitor.
		2) There are issues since the None's use the same output multiple times like laptop-hdmi-to-hdmi1 and laptop-hdmi-to-hdmi2

	Improvements:
		1) If there are loose cables (eg: a spare hdmi-hdmi connected to monitor 2) and the user wants to display 
			a device which can't otherwise be displayed on that monitor, suggest connecting the hdmi-hdmi cable to the device.
		2) Go through all possible connections (given a set of cables) and see which one gives the most options/flexibility 
			for displaying devices.
		3) If Dell Display Manager (ddm.exe) is installed, automatically change the configuration (warning that pressing okay will do so).
		4) Ensure that the above definitions are used correctly.
'''
import itertools
from easygui import msgbox, choicebox


class Cable:
	def __init__(self, input, output):
		self.input = input
		self.output = output

	def __repr__(self):
		return self.input + "-" + self.output

class Device:
	def __init__(self, name, outputs):
		self.name = name
		self.outputs = outputs

	def can_connect_to(self, connection_input, cables):
		for device_output in self.outputs:
			for cable in cables:
				if connection_input == cable.output and device_output == cable.input:
					return (True, cable)
		return (False, None)

	def possible_connections(self, cables):
		monitor_inputs = []
		for output in self.outputs:
			monitor_inputs += [cable.output for cable in cables if output == cable.input]
		return monitor_inputs

	def how_does_connect_to(self, connected_to, cables):
		monitor_inputs = []
		for output in self.outputs:
			monitor_inputs += [cable for cable in cables if output == cable.input and cable.output == connected_to]
		return monitor_inputs

class Connection:
	def __init__(self, device, output, monitor, input, supports_daisy_chaining=False):
		# could check to make sure this is valid given the cables.
		self.device = device
		self.device_output = output
		self.monitor = monitor
		self.monitor_input = input
		self.supports_daisy_chaining = supports_daisy_chaining

	def __repr__(self):
		name = 'None' if not self.device else self.device.name
		return name + " is connected from " + self.device_output + " to (" + str(self.monitor) + ")" + self.monitor_input

cables = [
	Cable('hdmi', 'hdmi'),
	Cable('usbc', 'dp'),
	Cable('mdp', 'dp'),
]

devices = {
	'desktop': Device('desktop', ['usbc', 'hdmi']),  # Is there a way to avoid duplicate desktop? I guess a Devices class?
	'laptop': Device('laptop', ['usbc', 'hdmi']),
	'mac': Device('mac', ['mdp', 'hdmi']), # hdmi just for testing
}


class Test:
	@staticmethod
	def device():
		print(Device('desktop', ['usbc', 'hdmi']).can_connect_to('hdmi', cables))
		print(Device('desktop', ['usbc', 'hdmi']).can_connect_to('mdp', cables))
		print(Device('desktop', ['usbc', 'hdmi']).can_connect_to('dp', cables))

		print(Device('mac', ['mdp']).can_connect_to('hdmi', cables))
		print(Device('mac', ['mdp']).can_connect_to('mdp', cables))
		print(Device('mac', ['mdp']).can_connect_to('dp', cables))


class Setup:
	def __init__(self, number_of_monitors):
		self.num_monitors = number_of_monitors
		self.connections = [
			Connection(devices['desktop'], 'usbc', 1, 'dp', supports_daisy_chaining=True),
			Connection(devices['laptop'], 'usbc', 2, 'dp', supports_daisy_chaining=True),
			Connection(devices['mac'], 'mdp', 3, 'dp'),
			Connection(None, 'hdmi', 1, 'hdmi'),
			Connection(None, 'hdmi', 2, 'hdmi'),
			Connection(None, 'hdmi', 3, 'hdmi'),
			Connection(None, 'dpi', 1, 'mdp')
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
			Also returns (monitor_index of monitor_output, monitor_input_source of monitor_output, made use of daisy chaining) '''
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
				return (monitor, None, False)  # Daisy-chaining can't work with any other setup.

		return (monitor, get_input(monitor), False)


	def whole_display(self, arrangment):
		# assert arremgnts size is number of moitores
		return [self.what_is_displayed(arrangment, i) for i in range(1, self.num_monitors+1)]

	def how_to_get(self, users_devices_request):
		def all_available_monitor_outputs():
			# All possible monitor input-sources and what monitor-outputs they display
			configurations = []
			for input_sources in itertools.product(['hdmi', 'mdp', 'dp'], repeat=3):  # [ , , ] -> Possible monitor connections
				configurations.append((input_sources, self.whole_display(input_sources)))
			return configurations

		def all_possible_monitor_outputs(available_outputs, connections):
			# Of all possible monitor-outputs, which are possible given what is connected as the monitor-inputs.
			# ie there are connections to the monitor that can show these outputs.
			# check lengths of num_monitors == request == output
			possible_connections = []
			for configuration in available_outputs:
				def do_connections_support_configuration(connections, configuration):
					input_sources, monitor_outputs = configuration

					simplified_monitor_outputs = [[smo[0], smo[1]] for smo in monitor_outputs]
					simplified_connections = []
					for connection in connections:
						simplified_connections.append([connection.monitor, connection.monitor_input])
					return all([smo in simplified_connections for smo in simplified_monitor_outputs])

				valid = do_connections_support_configuration(connections, configuration)
				if valid:
					possible_connections.append(configuration)
			return possible_connections

		def get_displayed_device(monitor_output):
			# What devices are displayed, given the monitor input displayed
			devices_displayed = []
			input_sources, monitor_inputs = monitor_output
			for i, input in enumerate(monitor_inputs):
				print(i, input)
				for connection in self.connections:
					if connection.monitor == input[0] and connection.monitor_input == input[1]:
						devices_displayed.append(None if not connection.device else connection.device.name)

			if len(devices_displayed) > self.num_monitors:
				msg = "You connected more than 1 device to the same input:\n"
				for c in self.connections:
					msg += '\t' + str(c) + '\n'
				raise ValueError(msg)
			return (input_sources, devices_displayed)
			

		def get_requested_inputs(request, possible_devices_displayed):
			request = [r.lower() for r in request]
			possible_inputs_for_request = []

			for input_sources, devices_displayed in possible_devices_displayed:
				if request == devices_displayed:
					possible_inputs_for_request.append(input_sources)
			return possible_inputs_for_request

		

		def get_requested_inputs_via_new_connections(request, possible_devices_displayed):
			# Make sure it doesn't tell you to connect two devices to the same monitor.
			# This doesnt work, think about appending to a new list where None is replaced by all 
			# possible valid connections, and calling the above code on that.
			for p in possible_devices_displayed:
				print(p)

			request = [r.lower() for r in request]
			new_possible_devices_displayed = []
			for input_sources, devices_displayed in possible_devices_displayed:
				if None in devices_displayed:
					new_displays = (input_sources, [])
					message = []
					for i, device in enumerate(devices_displayed):
						if device is None:
							device_connects_to = devices[request[i]].possible_connections(cables)
							if input_sources[i] in device_connects_to:
								new_displays[1].append(request[i])
								possible_cables = devices[request[i]].how_does_connect_to(input_sources[i], cables)
								possible_cables = ' or '.join([str(c) for c in possible_cables])
								message.append(request[i] + " to " + input_sources[i] + "("+str(i+1)+") by " + possible_cables)
						else:
							new_displays[1].append(device)
					new_possible_devices_displayed.append((new_displays, ' and '.join(message)))

			for p in new_possible_devices_displayed:
				print('---',[p[0]], p[1])
			possible_inputs_for_request = [(get_requested_inputs(request, [d[0]]), d[1]) for d in new_possible_devices_displayed]
			possible_inputs_for_request = [p for p in possible_inputs_for_request if p[0]]
			for p in possible_inputs_for_request:
				print('>>>', p)
			return possible_inputs_for_request

		def summary_to_user(matching_input_sources):
			response = 'To get: ' + str(users_devices_request) + '\n'
			if not matching_input_sources:
				response += "There is no way to do that.\n"
			elif len(matching_input_sources) == 1:
				response += "Set your monitor inputs to:\n"
				response += '\t' + str(matching_input_sources[0]) + '\n'
			else:
				response += "There are multiple ways to do that:\n"
				for input_types in matching_input_sources:
					response += '\t' + str(input_types) + '\n'
			return response


		
		available_outputs = all_available_monitor_outputs()
		possible_outputs = all_possible_monitor_outputs(available_outputs, self.connections)
		possible_devices_displayed = [get_displayed_device(output) for output in possible_outputs]
		matching_input_sources = get_requested_inputs(users_devices_request, possible_devices_displayed)
		summary = summary_to_user(matching_input_sources)
		if "no way" in summary:
			summary = "You aren't able to get this configuration as is.\n"
			summary += "However, by connecting loose cables:\n"
			matching_input_sources = get_requested_inputs_via_new_connections(users_devices_request, possible_devices_displayed)
			summary += summary_to_user(matching_input_sources)
		return summary

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
	TESTING = 1
	if TESTING:
		Test.device()
		print('========================')

		#print(Setup(3).how_to_get(['Desktop', 'Laptop', 'Laptop']))
		#print("next")
		#print(Setup(3).how_to_get(['Desktop', 'Laptop', None]))
		#print("next")
		print(Setup(3).how_to_get(['Laptop', 'Laptop', 'Laptop']))
		#print("next")
		#print(Setup(3).how_to_get(['mac', None, None]))		
		exit(0)

	Setup(3).prompt_user()




































