""" This file contains the definitions for the Cables, Device, and Monitor Classes. """

class Cables:
	def __init__(self, cables):
		self.cables = cables

	def can_connect(self, portA, portB):
		return any((ca, cb) == (portA, portB) or (cb, ca) == (portA, portB)
			for ca, cb in self.cables)

	def __str__(self):
		return f"{self.__class__.__name__}: {self.__dict__}"

	def __repr__(self):
		return self.__str__()

class Device():
	def __init__(self, name, inputs=(), outputs=()):
		""" inputs/outputs => ['hdmi', 'dp'] """
		self.name = name
		self.inputs = tuple([
			{'kind':i, 'used':None} for i in list(inputs)
		])
		self.outputs = tuple([
			{'kind':o, 'used':None} for o in list(outputs)
		])

	def connect_port(self, direction, portA, other_device, portB, cables):
		if not cables.can_connect(portA, portB):
			raise ValueError(f"Cannot connect {portA} to {portB} using any of {cables}.")

		for i in getattr(self, direction):
			if i['kind'] == portA and not i['used']:
				i['used'] = tuple([other_device, portB])
				return
		raise ValueError(f"Unable to connect {self.name}'s {portA} to {other_device.name}'s {portB}.")

	def connect(self, portA, deviceB, portB, cables):
		""" Ouput of A into input of B. """
		self.connect_port('outputs', portA, deviceB, portB, cables)
		deviceB.connect_port('inputs', portB, self, portA, cables)

	def get_connected_input_device(self, port):
		""" Returns the (name, port) of the device connected to this devices requested port. """
		for i in self.inputs:
			if i['used'] and i['kind'] == port:
				other, other_port = i['used']
				for o in other.outputs:
					if other_port == o['kind']:
						return other.name, o['kind']
		return None

	def __str__(self):
		return f"{self.__class__.__name__}=> {self.__dict__}"

	def __repr__(self):
		return self.__str__()

	def draw(self):
		print(self.name)
		for kind, connections in {'In': self.inputs, 'Out': self.outputs}.items():
			for i in connections:
				print(f"\t{kind}: {i['kind']}")
				if i['used']:
					device, port = i['used']
					print('\t\t', device.name, port)


class Monitor(Device):
	def __init__(self, name, inputs=(), outputs=(), watching='hdmi', serial=None):
		super().__init__(name, inputs, outputs)
		assert watching in inputs
		self.watching = watching
		self.serial = serial

	def draw(self, devices):
		super().draw()
		print('\tState: ', self.watching)
		print('\tDisplay: ', self.whats_displayed(devices))

	def watch(self, watching):
		self.watching = watching

	def whats_displayed(self, devices):
		""" Returns the device and port of the device that is displayed on the monitor.
			This takes daisy-chaining into account. """

		# Developping this algorithm was difficult.
		# The most useful aspects in solving it were to:
		# 	A) Break down the problem into daisy-chaining and non-daisy-chaining sections.
		#   B) Implement automatic tests to verify that changes didn't break.
		#   C) Be aware that recursion was required.
		#   D) Use Pen and paper
		#   E) Make the 'notation' second nature.
		if self.watching in ('mdp', 'dp'):
			# The monitor is displaying an input that is capable of daisy-chaining
			gotten_input = self.get_connected_input_device(self.watching)
			if gotten_input is None:
				# If no device is attached to the displayed input, nothing is shown.
				return None

			name, port = gotten_input
			if isinstance(devices[name], Monitor) and port == 'dp':
				# The monitor is displaying the output of another monitor's display port
				# and is therefore daisy chaining.
				return devices[name].daisy_chain(devices)
			else:
				# The monitor is displaying the output of a device.
				return self.get_connected_input_device(self.watching)
		else:
			# The monitor is displaying an input that is not capable of daisy-chaining
			# So it simply displays the device connected to that input. (could be None).
			return self.get_connected_input_device(self.watching)

	def daisy_chain(self, devices):
		""" Carries out the recursive daisy-chaining evaluation to determine
				which (device, port) is being displayed when daisy-chaining is occuring.

			If a circular connection exists this may loop indefinitely.
			Its the user's job to make sure this doesn't happen.
			Future work could calculate the number of monitors that can chain
			according to the standard, this may involved knowing the resolution
			of the monitors.

			It is assumed that if a monitor could pass on DP and MDP input
			in a daisy-chain, that the displayport has precedence over MDP.
			This is an assumption since I don't have the devices to test this.
		"""

		def device_or_monitor_chain(device):
			""" If the device is a device, it is returned. If it is a monitor,
				it returns the device at the start of the chain. """
			if device is None:
				return None
			name, port = device
			if isinstance(devices[name], Monitor):
				return devices[name].daisy_chain(devices)
			return device

		if self.watching in ('dp', 'mdp'):
			# If the monitor's input source is daisy-chain capable, it overrides
			# whatever would have been daisy-chained. This means that the input_device
			# connected to the input source associated with self.watching is the new start
			# of the chain, so it should be returned.
			return device_or_monitor_chain(self.get_connected_input_device(self.watching))
		else:
			# Otherwise the chain is allowed to continue through this monitor.
			# If either DP or MDP devices are connected to the monitor,
			# the DP chain is attempted first, if there is no available device,
			# then MDP is attempted. ie. dp takes precedence over mdp.
			# Note that this is an assumption! Since I don't actually
			# have the physical devices to test the standard with.
			dp_device = self.get_connected_input_device('dp')
			mdp_device = self.get_connected_input_device('mdp')

			if dp_device:
				return device_or_monitor_chain(dp_device)
			elif mdp_device:
				return device_or_monitor_chain(mdp_device)

		# If none of the above was able to return a device,
		# no such device exists.
		return None

