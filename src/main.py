from electronics import *
import json
import os

JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'json')

class MyEncoder(json.JSONEncoder):
	def default(self, o):
		if isinstance(o, Device):
			dictionary = {}
			for k, v in o.__dict__.items():
				if k in ('inputs', 'outputs'):
					dictionary[k] = [p['kind'] for p in v]
				else:
					dictionary[k] = v
			return dictionary
		else:
			return super().default(o)

def save():
	string = json.dumps(CABLES.__dict__, indent=4)
	with open(os.path.join(JSON_PATH, 'cables.json'), 'w') as f:
		f.write(string)

	string = json.dumps(DEVICES, indent=4, cls=MyEncoder)
	# print(string)
	with open(os.path.join(JSON_PATH, 'devices.json'), 'w') as f:
		f.write(string)

	string = json.dumps(CONNECTIONS, indent=4)
	with open(os.path.join(JSON_PATH, 'connections.json'), 'w') as f:
		f.write(string)

def load():
	with open(os.path.join(JSON_PATH, 'cables.json'), 'r') as f:
		CABLES = Cables(json.loads(f.read())['cables'])

	with open(os.path.join(JSON_PATH, 'devices.json'), 'r') as f:
		DEVICES = {}
		for name, details in json.loads(f.read()).items():
			ElectronicClass = Monitor if 'watching' in details else Device
			DEVICES.update({name: ElectronicClass(**details)})

	with open(os.path.join(JSON_PATH, 'connections.json'), 'r') as f:
		CONNECTIONS = json.loads(f.read())

	for A, portA, B, portB in CONNECTIONS:
		DEVICES[A].connect(portA, DEVICES[B], portB, CABLES)
	return CABLES, DEVICES, CONNECTIONS


if __name__ == '__main__':
	CABLES, DEVICES, CONNECTIONS = load()
	save()

	x = y = z = None
	DEVICES['monitor1'].watch('mdp')
	DEVICES['monitor2'].watch('dp')
	DEVICES['monitor3'].watch('mdp')
	x = DEVICES['monitor1'].whats_displayed(DEVICES)
	y = DEVICES['monitor2'].whats_displayed(DEVICES)
	z = DEVICES['monitor3'].whats_displayed(DEVICES)
	print(x, y, z)

	# for device in DEVICES.values():
	# 	device.draw()

	# configs = find_configuration(DEVICES, {
	# 	"monitor1": None,
	# 	"monitor2": "laptop",
	# 	"monitor3": "mac",
	# })

	# if not configs:
	# 	print("Couldn't find any")
	# elif len(configs) == 1:
	# 	print(f"Use this configuration:", *configs)
	# else:
	# 	newline = '\n\t'
	# 	print(f"Use one of:\n\t{newline.join([str(c) for c in configs])}")
	#