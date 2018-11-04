from components import Cable, Connection
from electronics import Device, Monitor
from definitions import *


class DeviceMonitorConnection(Connection):
	def __init__(self, device, device_port, monitor, monitor_port, cable=None, supports_daisy_chaining=None, cables=None):
		if not cable and not cables:
			raise ValueError("A connection cannot be established without access to cable information.")

		cable = cable if cable else Cable.get_single_cable(device_port, monitor_port, cables)
		super().__init__(device_port, cable, monitor_port)

		self.device = device
		self.monitor = monitor
		self.supports_daisy_chaining = supports_daisy_chaining

		if self.supports_daisy_chaining is None:
			if self.device is not None:
				self.supports_daisy_chaining = self.device.supports_daisy_chaining and self.cable.supports_daisy_chaining
			else:
				self.supports_daisy_chaining = CANNOT_DAISY_CHAIN

	def __str__(self):
		name = 'None' if not self.device else self.device.name
		return name + \
				" is connected from " + self.output_junction.port + " to (" + str(self.monitor) + ")" + self.input_junction.port +\
				" with" + ("" if self.supports_daisy_chaining else "out") + " daisy-chain support"



class MonitorSetup:
	def __init__(self, monitors, monitor_input_sources, connections, users_devices, cables):
		if len(monitors) != len(monitor_input_sources):
			raise ValueError("The number of monitors must match the number of input sources supplied.", len(monitors), len(monitor_input_sources))	
	
		for i, monitor in enumerate(monitors):
			monitor.active_port = monitor_input_sources[i]
		self.monitors = monitors

		self.connections = []
		for device_name, device_port, monitor_index, monitor_port in connections:
			device_name = device_name if device_name is None else users_devices[device_name]
			self.connections.append(DeviceMonitorConnection(
				device_name, device_port, self.monitors[monitor_index], monitor_port, cables=cables
			))
		# Ensure connections are valid here... (1 connection per port)

	def get_connection(self, monitor_index, port):
		for c in self.connections:
			if (c.monitor.index == monitor_index) and (c.input_junction.port == port):
				return c
		raise ValueError("Could not find that connection: ", monitor_index, port)


	def get_monitor_display(self, monitor_index):
		''' input_types are the current input-sources on each monitor: ['hdmi, 'dp', 'mdp'] 
			This will output what is being displayed, for example if monitor 3 is requested:
			it would output (2, 'dp') indicating it is showing the displayport output from monitor 1.
			Also returns (monitor_index of monitor_output, monitor_input_source of monitor_output, made use of daisy chaining) '''
		monitor = self.monitors[monitor_index]
		if monitor.index < 0:
			raise ValueError("The monitor index must be non-negative.")
		if monitor.index > len(self.monitors):
			raise ValueError("The monitor index cannot exceed the number of monitors")
		
		if monitor.index != 0:
			if monitor.active_port == 'mdp':  # Handle daisy chaining
				previous_monitor, previous_active_port = self.get_monitor_display(self.monitors[monitor.index - 1].index)
				if previous_active_port == 'dp':
					if self.get_connection(previous_monitor.index, 'dp').supports_daisy_chaining:
						return (previous_monitor, previous_active_port)
				return (monitor, None)  # Daisy-chaining can't work with any other setup.

		return (monitor, monitor.active_port)

	def get_displays(self):
		return [self.get_monitor_display(monitor.index) for monitor in self.monitors]

	def get_displays_pretty(self):
		return [(int(str(display[0])), display[1]) for display in self.get_displays()]

















