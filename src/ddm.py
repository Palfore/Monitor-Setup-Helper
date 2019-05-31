""" A wrapper class for the Dell Display Manager (DDM) executable. """

import os
import time

class DDM:
	EXECUTABLE = os.path.join(os.path.dirname(os.path.realpath(__file__)),
		os.path.join("ddm", "ddm.exe")
	)

	def __init__(self, serial, disable_execution=False):
		self.serial = serial
		self.disable_execution = disable_execution

	def execute(self, command):
		command = f"/{self.serial}:" + command
		print(f"{DDM.EXECUTABLE} {command}")
		if not self.disable_execution:
			os.system(f"{DDM.EXECUTABLE} {command}")
			time.sleep(1)  # ddm.exe seems to 'jam' if commands are too quick.

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
