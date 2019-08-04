""" A wrapper class for the Dell Display Manager (DDM) executable. """

import subprocess
import time
import os

def batch_commands(serials, command):
	command = ' '.join([f"/{serial}:" + command for serial in serials])
	command = f"{DDM.EXECUTABLE} {command} \\exit"
	print(command)
	os.system(command)


class VCP_CODES:
	brightness = '10'
	contrast = '12'

class DDM:
	EXECUTABLE = os.path.join(os.path.dirname(os.path.realpath(__file__)),
		os.path.join("ddm", "ddm.exe")
	)

	def __init__(self, serial, disable_execution=False):
		self.serial = serial
		self.disable_execution = disable_execution

	def execute(self, command):
		command = f"/{self.serial}:" + command
		if not self.disable_execution:
			command = f"{DDM.EXECUTABLE} {command} \\exit"
			print(command)
			os.system(command)

	def setSource(self, source):
		self.execute(f"SetActiveInput {source}")

	def setContrast(self, contrast):
		""" 0 < contrast < 100 """
		self.execute(f"SetContrastLevel {contrast}")

	def setBrightness(self, brightness):
		""" 0 < contrast < 100 """
		self.execute(f"SetBrightnessLevel {brightness}")

	def changeBrightness(self, amount=1):
		""" 0 < contrast < 100 """
		control = ("Inc" if amount > 0 else "Dec") + "Control"
		self.execute(f"{control} {VCP_CODES.brightness} {abs(amount)}")

	def changeContrast(self, amount=1):
		""" 0 < contrast < 100 """
		control = ("Inc" if amount > 0 else "Dec") + "Control"
		self.execute(f"{control} {VCP_CODES.contrast} {abs(amount)}")

	def sleep(self):
		self.execute("SetPowerMode Off")

	def wake(self):
		self.execute("SetPowerMode On")

	def flash(self):
		self.sleep()
		self.wake()