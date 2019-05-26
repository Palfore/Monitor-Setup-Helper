# Open question: I Daisy-Chain using dp->mdp.
# 	Is that because it can only happen with mdp input?
#	Or would a dp->dp work as well?
#	For now, assume only dp->mdp works.

from electronics import *
from pprint import pprint
import itertools
import json

def save():
	string = json.dumps(CABLES.__dict__, indent=4)
	with open('cables.json', 'w') as f:
		f.write(string)

	string = json.dumps(DEVICES, indent=4, default=lambda obj: obj.__dict__)
	with open('devices.json', 'w') as f:
		f.write(string)

	string = json.dumps(CONNECTIONS, indent=4)
	with open('connections.json', 'w') as f:
		f.write(string)

def load():
	with open('cables.json', 'r') as f:
		CABLES = Cables(json.loads(f.read())['CABLES'])

	with open('devices.json', 'r') as f:
		DEVICES = {}
		for name, details in json.loads(f.read()).items():
			ElectronicClass = Monitor if 'watching' in details else Device
			DEVICES.update({name: ElectronicClass(**details)})

	with open('connections.json', 'r') as f:
		CONNECTIONS = json.loads(f.read())

	for A, portA, B, portB in CONNECTIONS:
		DEVICES[A].connect(portA, DEVICES[B], portB, CABLES)
	return CABLES, DEVICES, CONNECTIONS

def find_configuration_by_port(devices, monitor_display):
	valid_configs = []
	displays = [devices[name] for name in monitor_display]
	for config in itertools.product(Monitor.DISPLAY_STATES, repeat=len(monitor_display)):
		for i, display in enumerate(displays):
			display.watch(config[i])

		valid = True
		for display in displays:
			if monitor_display[display.name] != display.whats_displayed():
				valid = False
		if valid:
			valid_configs.append(tuple(zip([d.name for d in displays], config)))
	return tuple(valid_configs)

import itertools
def find_configuration(devices, monitor_display):
	# Generate all possible input combinations
	options = []
	for monitor, device in monitor_display.items():
		options.append([
			(device, o['kind']) for o in devices[device].outputs
		])

	# Concatonate all those results
	results = set()
	for p in itertools.product(*options):
		x = find_configuration_by_port(devices, {x: y for x, y in zip(monitor_display, p)})
		for y in x:
			results.add(y)
	return tuple(results)


import os
class DDM:
	def __init__(self, serial, disable_execution=False):
		self.serial = serial
		self.disable_execution = disable_execution


	def execute(self, command):
		command = f"/{self.serial}:" + command
		print(f"ddm.exe {command}")
		if not self.disable_execution:
			os.system(f"ddm.exe {command}")

	def setSource(self, source):
		self.execute(f"SetActiveInput {source}")

	def setContrast(self, contrast):
		""" 0 < contrast < 100 """
		self.execute(f"SetContrastLevel {contrast}")

	def setBrightness(self, brightness):
		""" 0 < contrast < 100 """
		self.execute(f"SetBrightnessLevel {brightness}")

	def flash(self):
		self.execute("SetPowerMode Off")
		self.execute("SetPowerMode On")

if __name__ == '__main__':
	CABLES, DEVICES, CONNECTIONS = load()
	# for device in DEVICES.values():
	# 	device.draw()

	configs = find_configuration(DEVICES, {
		"monitor1": "laptop",
		"monitor2": "laptop",
		"monitor3": "laptop",
	})

	if not configs:
		print("Couldn't find any")
	elif len(configs) == 1:
		print(f"Use this configuration:", *configs)
	else:
		print(configs)
		newline = '\n\t'
		print(f"Use one of:\n\t{newline.join([str(c) for c in configs])}")
