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
		self.name = name
		self.inputs = tuple([{'kind':i, 'used':None} if not isinstance(i, dict) else i for i in list(inputs)])
		self.outputs = tuple([{'kind':o, 'used':None}  if not isinstance(o, dict) else o for o in list(outputs)])

	def connect_port(self, direction, portA, other_device, portB, cables):
		if not cables.can_connect(portA, portB):
			raise ValueError(f"Cannot connect {portA} to {portB} using any of {cables}.")

		for i in getattr(self, direction):
			if i['kind'] == portA and not i['used']:
				i['used'] = tuple([other_device, portB])
				return
		raise ValueError(f"Unable to connect {i['kind']}.")

	def connect(self, portA, deviceB, portB, cables):
		""" Ouput of A into input of B. """
		self.connect_port('outputs', portA, deviceB, portB, cables)
		deviceB.connect_port('inputs', portB, self, portA, cables)

	def __str__(self):
		return f"{self.__class__.__name__}: {self.__dict__}"

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
	DISPLAY_STATES = ('hdmi', 'mdp', 'dp')

	def __init__(self, name, inputs=(), outputs=(), watching='hdmi', serial=None):
		super().__init__(name, inputs, outputs)
		assert watching in Monitor.DISPLAY_STATES
		self.watching = watching
		self.serial = serial

	def draw(self):
		super().draw()
		print('\tState: ', self.watching)
		print('\tDisplay: ', self.whats_displayed())

	def watch(self, watching):
		self.watching = watching

	def whats_displayed(self):
		# This has a bug
		for i in self.inputs:
			# Daisy Chaining
			if i['used'] and self.watching == "mdp":
				device, port = i['used']
				if port == 'dp' and hasattr(device, "whats_displayed"):
					return device.whats_displayed()

			# Regular Display
			if i['used'] and i['kind'] == self.watching:
				device, port = i['used']
				return device.name, port
		return None
