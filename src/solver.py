""" This file contains the functions that solve display requests.
	Which is when the user wants monitor1 to display device1, and monitor2 to ...

	The solving functionality for what is displayed on a monitor is in the
	Monitor class in electronics.py under the whats_displayed method.
"""
from electronics import Monitor
import itertools

def find_configuration_by_port(devices, monitor_display):
	""" Returns the monitor input sources for the queries of the form:
			{M1: (deviceA, portA), M2: (deviceB, portB), ... }
		Ie requesting specific device ports to be displayed on specific monitors.
		To solve queries that don't care about which port is displayed
		see find_configuration. """

	valid_configs = set()
	displays = [devices[name] for name in monitor_display]

	# Brute force through all monitor input sources
	sources = [[i['kind'] for i in m.inputs] for m in displays]
	for config in itertools.product(*sources):
		for i, display in enumerate(displays):
			display.watch(config[i])

		# If they match the request add it as a possibility.
		valid = True
		for display in displays:
			if monitor_display[display.name] is None:
				continue
			if monitor_display[display.name] != display.whats_displayed(devices):
				valid = False
		if valid:
			valid_configs.add(tuple(zip([d.name for d in displays], config)))
	return set(valid_configs)

def find_configuration(devices, monitor_display):
	""" Returns the monitor input sources for the queries of the form:
			{M1: deviceA, M2: deviceB, ... }
		Ie requesting specific devices to be displayed on specific monitors. """

	# Generate all possible input combinations of the form (device, port).
	# since we don't care about which port, satisfiying any port is valid.
	options = []
	for monitor, device in monitor_display.items():
		if device is None:
			options.append((None, None))
		else:
			options.append([
				(device, o['kind']) for o in devices[device].outputs
			])

	# Concatonate all those results
	results = set()
	for p in itertools.product(*options):
		results |= find_configuration_by_port(devices, {x: y for x, y in zip(monitor_display, p)})
	return results
