from components import Port, Cable
from definitions import *
import copy

class Electronic:
	def __init__(self, ports):
		self.ports = ports

	def has_port(self, port):
		return port in self.ports

	def connect(self, connection_port):
		if connection_port not in self.ports:
			raise ValueError("This port does not exist.")

		sucessful = False
		for port in self.ports:
			if port == connection_port and not port.occupied:
				port.occupied = OCCUPIED
				sucessful = True
		if not sucessful:
			raise ValueError("This port was already occupied")

	def disconnect(self, connection_port):
		if connection_port not in self.ports:
			raise ValueError("This port does not exist.")

		sucessful = False
		for port in self.ports:
			if port == connection_port and port.occupied:
				port.occupied = UNOCCUPIED
				sucessful = True
		if not sucessful:
			raise ValueError("This port was already disconnected, or does not exist.")


class Device(Electronic):
	def __init__(self, name, ports, supports_daisy_chaining=CANNOT_DAISY_CHAIN):  # definitely not a property of the device.
		super().__init__([Port(port, UNOCCUPIED) for port in ports])
		self.name = name
		self.supports_daisy_chaining = supports_daisy_chaining

	def __str__(self):
		return self.name

	def __deepcopy__(self, memo):
		return Device(self.name, copy.copy(self.ports), self.supports_daisy_chaining)

	def get_possible_connections_to_monitor(self, monitor, cables):
		connections = []
		for open_device_port in [port for port in self.ports if not port.occupied]:
			for open_monitor_port in [port for port in monitor.ports if not port.occupied]:
				connections += Cable.get_valid_cables(open_device_port, open_monitor_port, cables)
		connections = [connection for connection in connections if connection]
		return connections

class Monitor(Electronic):
	def __init__(self, index, active_port=None, ports=(('dp', UNOCCUPIED), ('mdp', UNOCCUPIED), ('hdmi', UNOCCUPIED))):
		super().__init__([Port(port[0], port[1]) for port in ports])
		self.index = index
		self.active_port = active_port

	def __str__(self):
		return str(self.index)

	def __deepcopy__(self, memo):
		return Monitor(self.index, self.active_port, [(port.type, port.occupied) for port in self.ports])

