from definitions import *

class Port:
	def __init__(self, port_type, occupied):
		self.type = port_type
		self.occupied = occupied

	def __str__(self):
		return str(self.type)

	def __eq__(self, other):
		return self.type == other

class Junction:
	def __init__(self, port, cable):
		self.port = port
		self.cable = cable
		self.loose_end = cable.get_other_end(self.port)

class Connection:
	def __init__(self, left_port, cable, right_port):
		self.output_junction = Junction(left_port, cable)
		self.input_junction = Junction(right_port, cable)
		self.cable = cable

class Cable:
	def __init__(self, left, right, supports_daisy_chaining=CANNOT_DAISY_CHAIN):
		self.left = Port(left, None)  # Can't use 'to'/'from' (they're keywords)
		self.right = Port(right, None)
		self.supports_daisy_chaining = supports_daisy_chaining

	def __str__(self):
		return str(self.left) + "-" + str(self.right)

	def __eq__(self, other):
		return self.left == other.left and self.right == other.right

	def get_other_end(self, end):
		return self.left if end == self.right else self.right

	@staticmethod
	def get_valid_cables(left, right, cables):
		return [cable for cable in cables if cable == Cable(left, right)]

	@staticmethod
	def get_single_cable(left, right, cables):
		valid_cables = Cable.get_valid_cables(left, right, cables)
		if not valid_cables:
			raise ValueError("You don't have any cables that connect these two:", left, right, [str(c)for c in cables])
		if len(valid_cables) > 1:
			raise ValueError("Cable is ambiguous, could be: ", valid_cables)
		return valid_cables[0]

	@staticmethod
	def exists(left, right, cables):
		return bool(Cable.get_valid_cables(left, right, cables))

















