# Useful links:
#	 https://stackoverflow.com/questions/10865116/tkinter-creating-buttons-in-for-loop-passing-command-arguments

from tkinter import ttk
import tkinter as tk
import tkinter.messagebox as messagebox

from solver import find_configuration
from ddm import DDM, batch_commands

from numpy import arange
import numpy as np

import subprocess, sys
import os

THIS_SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
GET_MONITOR_SCRIPT_PATH = os.path.join(THIS_SCRIPT_PATH,
		os.path.join("ddm", "get_monitors.ps1")
)

LARGE_FONT = ("Verdana", 18)
BOLD_FONT = 'Helvetica 8 bold'
WIDTH = 1500
HEIGHT = 800

def probe_bbox(canvas, x, y, element):
	button_window = canvas.create_window(0, 0, window=element)
	element.place(x=x, y=y)
	canvas.update()

	w = element.winfo_width()
	h = element.winfo_height()
	canvas.delete(button_window)
	element.place_forget()
	return w, h


def place_element(canvas, x, y, element):
	w, h = probe_bbox(canvas, x, y, element)
	button_window = canvas.create_window(0, 0, window=element)
	element.place(x=x, y=y)
	canvas.update()
	return w, h

def handle_button(details):
	name, kind, connection = details
	print(details)

def get_attached_monitor_serial_numbers():
	p = subprocess.check_output(["powershell.exe", "-ExecutionPolicy", "Unrestricted", GET_MONITOR_SCRIPT_PATH])
	p = str(p).strip("\\b'").strip("\\'").replace('\\x00', '').strip('\\r\\n')
	serials = []
	for monitor in p.split('\\r\\n'):
		if monitor:
			serials.append(monitor.split(',')[1].strip())
	return serials

class StartPage:
	none_alias = 'Any'  # What the user should see when they want to select None for a monitor display

	def __init__(self, master):
		self.master = master
		self.master.title("Monitor Manager")
		self.master.geometry(f"{WIDTH}x{HEIGHT}")
		tk.Tk.iconbitmap(self.master, default=os.path.join(
			os.path.dirname(THIS_SCRIPT_PATH),
			'icon2.ico')
		)

		canvas = tk.Canvas(master, width=WIDTH, height=HEIGHT, background="#D2D2D2")
		canvas.place(x=0, y=0)
		self.monitor_displays = {}

		submit = ttk.Button(self.master, text="Apply Choice", command=self.on_submit)
		dw, dh = place_element(canvas, 50, 500, submit)

		self.output = tk.Listbox(self.master, width=100, selectmode='single')
		_, dh2 = place_element(canvas, 50, 500+dh, self.output)

		submit = ttk.Button(self.master, text=f"Sleep",
			command=lambda :[DDM(serial).sleep() for serial in get_attached_monitor_serial_numbers()])
		place_element(canvas, 25, 500+dh+dh2+20, submit)
		submit = ttk.Button(self.master, text=f"Wake",
			command=lambda :[DDM(serial).wake() for serial in get_attached_monitor_serial_numbers()])
		place_element(canvas, 125, 500+dh+dh2+20, submit)

		submit = ttk.Button(self.master, text=f"b^All",
			command=lambda: batch_commands(get_attached_monitor_serial_numbers(), "IncControl 10 A"))
		place_element(canvas, 250, 500+dh+dh2+20, submit)
		submit = ttk.Button(self.master, text=f"bvAll",
			command=lambda: batch_commands(get_attached_monitor_serial_numbers(), "DecControl 10 A"))
		place_element(canvas, 350, 500+dh+dh2+20, submit)

		submit = ttk.Button(self.master, text=f"c^All",
			command=lambda: batch_commands(get_attached_monitor_serial_numbers(), "IncControl 12 A"))
		place_element(canvas, 475, 500+dh+dh2+20, submit)
		submit = ttk.Button(self.master, text=f"cvAll",
			command=lambda: batch_commands(get_attached_monitor_serial_numbers(), "DecControl 12 A"))
		place_element(canvas, 575, 500+dh+dh2+20, submit)

		submit = ttk.Button(self.master, text=f"b50All",
			command=lambda: batch_commands(get_attached_monitor_serial_numbers(), "SetControl 10 32"))
		place_element(canvas, 700, 500+dh+dh2+20, submit)
		submit = ttk.Button(self.master, text=f"c50All",
			command=lambda: batch_commands(get_attached_monitor_serial_numbers(), "SetControl 12 32"))
		place_element(canvas, 800, 500+dh+dh2+20, submit)


		w = 50
		for serial in get_attached_monitor_serial_numbers():
			submit = ttk.Button(self.master, text=f"Flash", command=lambda serial=serial:DDM(serial).flash())
			dw, dh = place_element(canvas, w, 25, submit)
			w += dw
			submit = tk.Listbox(self.master, selectmode='single', height=1)
			submit.insert(0, serial)
			dw, dh = place_element(canvas, w, 25, submit)
			w += dw + 10

		def draw_monitor(x, y, monitor):
			padding = 10

			label = ttk.Label(self.master, text=monitor.name.capitalize(), font=LARGE_FONT, background="#D2D2D2")
			monitor_w, monitor_h = place_element(canvas, x, y, label)


			options = [name.capitalize() for name, details in DEVICES.items() if not hasattr(details, 'watching')]
			options.append(self.none_alias)

			self.monitor_displays[monitor.name].set(options[0])
			option = ttk.OptionMenu(self.master, self.monitor_displays[monitor.name], options[0], *options, command=lambda _:self.on_choose())
			monitor_w, monitor_h = place_element(canvas, x, y+monitor_h, option)

			positions = {}

			# Options
			total_width = 0  # Determine Size
			button_texts = {
				'b^': lambda : DDM(monitor.serial).changeBrightness(10),
				'bv': lambda : DDM(monitor.serial).changeBrightness(-10),
				'c^': lambda : DDM(monitor.serial).changeContrast(10),
				'cv': lambda : DDM(monitor.serial).changeContrast(-10),
			}
			for text in button_texts.keys():
				button = ttk.Button(self.master, text=text)
				button.config(width=3)
				w, h = probe_bbox(canvas, x, y, button)
				total_width += w

			width = 0  # Draw
			for text, func in button_texts.items():
				button = ttk.Button(self.master, text=text,
					command=func)
				button.config(width=3)
				X, Y = x+width-total_width/2+monitor_w/2, y+h-padding+-2*monitor_h
				w, h = place_element(canvas, X, Y, button)
				width += w

			# Inputs
			total_width = 0  # Determine Size
			for port in monitor.inputs:
				button = ttk.Button(self.master, text=port['kind'])
				w, h = probe_bbox(canvas, x, y, button)
				total_width += w

			width = 0  # Draw
			for i, port in enumerate(monitor.inputs):
				string = (monitor.name, port['kind'], (port['used'][0].name, port['used'][1])) if port['used'] else (monitor.name, port['kind'], None)
				button = ttk.Button(self.master, text=port['kind'], command=lambda string=string: handle_button(string))
				X, Y = x+width-total_width/2+monitor_w/2, y+h+padding+2*monitor_h
				w, h = place_element(canvas, X, Y, button)
				positions[(monitor.name, 'in', port['kind'])] = (X, Y, w, h)
				width += w

			# Outputs
			total_height = 0  # Determine Size
			for port in monitor.outputs:
				button = ttk.Button(self.master, text=port['kind'])
				w, h = probe_bbox(canvas, x, y, button)
				total_height += h

			height = 0  # Draw
			for i, port in enumerate(monitor.outputs):
				button = ttk.Button(self.master, text=port['kind'])
				X, Y = x-total_width/2-w/2, y+height-h+2*monitor_h
				w, h = place_element(canvas, X, Y, button)
				positions[(monitor.name, 'out', port['kind'])] = (X, Y, w, h)
				height += h

			x1, y1, x2, y2 = x-total_width/2-w/2-padding, y-total_height/2, x+total_width/2+w, y+total_height/2+2*h+2*monitor_h+padding
			canvas.create_rectangle(x1, y1, x2, y2)
			return x1, y1, x2, y2, positions

		def draw_device(x, y, device):
			padding = 10

			label = ttk.Label(self.master, text=name.capitalize(), font=LARGE_FONT)
			w, h = probe_bbox(canvas, x, y, label)
			monitor_width, h = place_element(canvas, x-w/2, y, label)

			positions = {}

			# Outputs
			total_height = h*2
			total_width = 0  # Determine Size
			for port in device.outputs:
				button = ttk.Button(self.master, text=port['kind'])
				w, h = probe_bbox(canvas, x, y, button)
				total_width += w

			width = 0  # Draw
			for i, port in enumerate(device.outputs):
				button = ttk.Button(self.master, text=port['kind'])
				X, Y = x+width-total_width/2, y-h-padding
				w, h = place_element(canvas, X, Y, button)
				positions[(device.name, 'out', port['kind'])] = (X, Y, w, h)
				width += w

			x1, y1, x2, y2 = x-total_width/2-w, y-total_height/2-h, x+total_width/2+w, y+total_height/2+2*h
			canvas.create_rectangle(x1, y1, x2, y2)
			return x1, y1, x2, y2, positions


		positions = {}
		monitor_x = 200
		device_x = 200
		for device in DEVICES.items():
			name, device = device
			if hasattr(device, "whats_displayed"):
				self.monitor_displays.update({name: tk.StringVar(self.master)})
				x1, y1, x2, y2, pos = draw_monitor(monitor_x, 100, device)
				monitor_x += (x2-x1) + 10
			else:
				x1, y1, x2, y2, pos = draw_device(device_x, 400, device)
				device_x += (x2-x1) + 10
			positions.update(pos)

		for name, device in DEVICES.items():
			for i, port in enumerate(device.inputs):
				x, y, w, h = positions[(name, 'in', port['kind'])]
				if port['used']:
					connected_device, connected_port = port['used']
					X, Y, W, H = positions[(connected_device.name, 'out', connected_port)]
					scale = 0
					x, y, X, Y = x+w/2, y+h/2, X+W/2, Y+H/2
					dt = 0

					ax = dt * (X - x) + x
					ay = dt * (Y - y) + y
					bx = (1-dt) * (X - x) + x
					by = (1-dt) * (Y - y) + y
					cx = bx + 20
					cy = by - 20
					tm = (bx - ax) / (cx - ax)

					if Y > y:
						Y += -15
						y += 15
					else:
						Y += 15
						y += -15
					canvas.create_line(x, y, X, Y, arrow='first')
		self.on_choose()


	def on_submit(self):
		if not self.output.size():
			messagebox.showinfo("No options available", "The configuration you request is not possible to display with your setup.")
			return

		selected = self.output.curselection()
		choice = None
		if not selected:
			if self.output.size() == 1:
				choice = self.output.get(0)
			else:
				messagebox.showinfo("Need Selection", "Your configuration has multiple solutions, please select one then try again.")
				return
		else:
			choice = self.output.get(int(selected[0]))

		for name, port in choice:
			DDM(DEVICES[name].serial).setSource(port)

	def on_choose(self):
			desired_configuration = {n: (v.get().lower() if v.get() != self.none_alias else None)
					for n, v in self.monitor_displays.items()
			}
			x = find_configuration(DEVICES, desired_configuration)
			self.output.delete(0, self.output.size())
			for i, y in enumerate(x):
				self.output.insert(i, y)


if __name__ == '__main__':
	from main import load, save
	CABLES, DEVICES, CONNECTIONS = load()

	root = tk.Tk()
	app = StartPage(root)
	root.mainloop()

