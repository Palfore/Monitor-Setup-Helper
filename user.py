from definitions import *
from components import Cable
from electronics import Device, Monitor

class UsersStuff:
	cables = [
		Cable('hdmi', 'hdmi'),
		Cable('usbc', 'dp', supports_daisy_chaining=CAN_DAISY_CHAIN),
		Cable('mdp', 'dp'),
		Cable('mdp', 'hdmi')
	]

	devices = {
		#'desktop': Device('desktop', ['usbc', 'hdmi'], supports_daisy_chaining=CAN_DAISY_CHAIN),
		'laptop': Device('laptop', ['usbc', 'hdmi'], supports_daisy_chaining=CAN_DAISY_CHAIN),
		'mac': Device('mac', ['mdp'], supports_daisy_chaining=CANNOT_DAISY_CHAIN),
		'xbox': Device('xbox', ['hdmi'], supports_daisy_chaining=CANNOT_DAISY_CHAIN)
	}

	monitors = (  # maybe unoccupied should say unavailable
		Monitor(0, ports=(('dp', UNOCCUPIED), ('mdp', UNOCCUPIED), ('hdmi', UNOCCUPIED))),
		Monitor(1, ports=(('dp', UNOCCUPIED), ('mdp', OCCUPIED), ('hdmi', UNOCCUPIED))),
		#Monitor(2, ports=(('dp', UNOCCUPIED), ('mdp', OCCUPIED), ('hdmi', UNOCCUPIED))),
	)

	connections = (
		#('desktop', 'usbc', 0, 'dp'),
		('laptop', 'usbc', 0, 'dp'),
		('mac', 'mdp', 1, 'hdmi'),
		(None, 'hdmi', 0, 'hdmi'),
		(None, 'hdmi', 1, 'hdmi'),
		#(None, 'hdmi', 2, 'hdmi'),
	)
