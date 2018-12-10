from easygui import msgbox, choicebox, exceptionbox, ynbox
from user import UsersStuff
from solver import Solver

import os
import time

import subprocess
import sys

DEVICES = UsersStuff.devices
MONITORS = UsersStuff.monitors
CABLES = UsersStuff.cables
CONNECTIONS = UsersStuff.connections

def change_input_sources(input_sources):
	def execute_monitor_command(command):
		full_command = f"ddm.exe {command}"
		print(f"Executing: {full_command.split(' ')}")
		subprocess.Popen(full_command.split(' '), shell=True)
		time.sleep(3)
	for i, source in reversed(list(enumerate(input_sources))): # Do primary last
		source = source.upper().replace("'", '').strip()
		execute_monitor_command(f"{i+1}:SetActiveInput {source}")
	execute_monitor_command("Exit")


def summary(desired_display):
	title = "How would you like to change your settings?"
	response = f"You are trying to display: {desired_display}.\n"
	choice = None
	source_options = get_display_source_options(desired_display, False)

	if not source_options:
		source_options = get_display_source_options(desired_display, True)
		if not source_options:
			msgbox(response + "There is no way to display this.\n")
		else:
			response += "To display this, you require additional connections.\n"
	if source_options:
		if len(source_options) == 1: # Choicebox requires more than one option.
			response += "Would you like to switch your input sources to:\n"
			response += source_options[0]
			if ynbox(response, title):
				choice = source_options[0]
		else:
			response += "Your changes will automatically be applied when you select an option.\n"
			response += "Please select an option:\n"
			choice = choicebox(response, title, source_options)

	if choice:
		choice = choice.split('==>')[0]
		input_sources = choice.replace('(', '').replace(')', '').split(',')
		change_input_sources(input_sources)

def get_display_source_options(desired_display, try_new_connections):
	def get_required_connections(source):
		additional_connections_required = []
		for connection in source[0]:
			name, device_port = connection[0]
			index, monitor_port = connection[1]
			if (name, device_port, index, monitor_port) not in CONNECTIONS:
				additional_connections_required.append(
					f"m{index}-{monitor_port} to {name}-{device_port}")

		if not additional_connections_required:
			return ""
		return " ==> " + ', and '.join(additional_connections_required)

	sources = Solver(
		DEVICES, MONITORS, CABLES, CONNECTIONS
	).get_input_sources_for_display(desired_display, try_new_connections)
	return [str(source[1]) + get_required_connections(source) for source in sources]


def get_users_request():
	msg = lambda n: f"What would you like monitor {n} to display?"
	title = "Monitor Setup"

	request = []
	for i in range(1, len(MONITORS)+1):
		choice = choicebox(msg(i), title, [k.title() for k in DEVICES])
		if not choice:  # Exit if the user cancels
			return None
		request.append(choice.lower())
	return request

if __name__ == '__main__':
	request = get_users_request()
	print(request)
	try:
		if request:
			summary(request)
	except Exception as e:
		print(e)
		exceptionbox()
