from monitorSetup import MonitorSetup
import itertools
import copy

class Solver:
	def __init__(self, devices, monitors, cables, connections):
		self.possible_input_source_configurations = list(itertools.product(*[monitor.ports for monitor in monitors]))
		self.userDevices = devices
		self.userMonitors = monitors
		self.userCables = cables
		self.userConnections = connections

	def get_input_sources_for_desired_monitor_outputs(self, desired_output):
		''' [(0, 'dp'), (0, 'dp'), (2, 'hdmi')] => ('dp', 'mdp', 'hdmi') '''
		valid_input_sources = []
		for input_source_configuration in self.possible_input_source_configurations:
			display = MonitorSetup(
				self.userMonitors, input_source_configuration, self.userConnections, self.userDevices, self.userCables
			).get_displays_pretty()
			if display == desired_output:
				valid_input_sources.append(input_source_configuration)
		return valid_input_sources

	def convert_devices_to_monitor_outputs(self, desired_devices, check_new_connections):
		''' ['desktop', 'desktop', 'laptop'] => [(0, dp), (0, dp), (2, hdmi)] '''
		def get_current_possible_connections(connections):
			possible_connections = []
			for i, desired_device_name in enumerate(desired_devices):
				for c in connections:
					device_name, device_port, monitor_index, monitor_port = c
					if not device_name:
						continue
					if desired_device_name.lower() == device_name.lower():
						possible_connections.append(((desired_device_name, device_port), (monitor_index, monitor_port)))
			return possible_connections
		
		def get_new_possible_connections(connections):
			''' If the user plugs in unconnected monitor cables '''
			new_connections = []
			for c in connections:
				device_name, device_port, monitor_index, monitor_port = c
				if device_name:
					continue
				for i, desired_device_name in enumerate(self.userDevices):
					if self.userDevices[desired_device_name].has_port(device_port):
						new_connections.append(((desired_device_name, device_port), (monitor_index, monitor_port)))
			return new_connections

		def get_valid_connections(connections):
			''' Checks to see if same port on a device is being plugged into multiple times on the same device.
				Since the monitor values represent what is displayed (not what is plugged in) the same check 
				does not need to be done for them. '''
			valid_connections = []
			for c in set(itertools.permutations(possible_connections, r=len(self.userMonitors))):
				devices = {c[i][0][0]: copy.deepcopy(self.userDevices[c[i][0][0]]) for i in range(len(c))}

				if len(c) != len(self.userMonitors):
					raise ValueError("There should be a display for each monitor.")

				# Can all ports connect with no overlap?
				try:
					# The same connection shouldn't count as another connection => list(set(c))
					non_duplicate_connections = list(set(c))
					for connection in non_duplicate_connections:
						device_data = connection[0]
						device_name = device_data[0]
						device_port = device_data[1]
						devices[device_name].connect(device_port)
					valid_connections.append(c)
				except ValueError as e:
					if "already occupied" in str(e):
						pass
					else:
						raise
			return set(valid_connections)

		def associated_monitor_displays(valid_connections):
			displays = []
			for c in valid_connections:
				displayed_devices = [x[0][0] for x in c]
				required_ports = [x[1] for x in c]
				if displayed_devices == desired_devices:
					displays.append((c, required_ports))
			return displays
					
		possible_connections = get_current_possible_connections(self.userConnections)
		if check_new_connections:
			possible_connections += get_new_possible_connections(self.userConnections)

		valid_connections = get_valid_connections(possible_connections)
		monitor_displays = associated_monitor_displays(valid_connections)
		return monitor_displays


	def get_input_sources_for_display(self, desired_devices, check_new_connections):
		possible_monitor_outputs = self.convert_devices_to_monitor_outputs(desired_devices, check_new_connections)
		possible_inputs = []
		for connection, output in possible_monitor_outputs:
			input_sources = self.get_input_sources_for_desired_monitor_outputs(output)
			if not input_sources:
				continue
			for sources in input_sources:
				possible_inputs.append((connection, tuple([str(s) for s in sources])))
		return possible_inputs



