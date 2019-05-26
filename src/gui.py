import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
from main import find_configuration, DDM
import ast

LARGE_FONT = ("Verdana", 18)
BOLD_FONT = 'Helvetica 8 bold'
WIDTH = 1200
HEIGHT = 800

class SeaofBTCapp(tk.Tk):
	def __init__(self, *args, **kwargs):

		tk.Tk.__init__(self, *args, **kwargs)

		#tk.Tk.iconbitmap(self,default='clienticon.ico')
		tk.Tk.wm_title(self, "Monitor Manager")
		tk.Tk.wm_geometry(self, f"{WIDTH}x{HEIGHT}")

		container = tk.Frame(self, width=1000, height=1000)
		container.grid_rowconfigure(0, weight=1)
		container.grid_columnconfigure(0, weight=1)

		self.frames = {}

		for F in (StartPage, PageOne, PageTwo):
				frame = F(container, self)
				self.frames[F] = frame
				frame.grid(row=0, column=0, sticky="nsew")

		self.show_frame(StartPage)

	def show_frame(self, cont):
		frame = self.frames[cont]
		frame.tkraise()


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

from math import pi, cos, sin
from numpy import arange

def motion(event):
    x, y = event.x, event.y
    print('{}, {}'.format(x, y))


def handle_button(details):
	name, kind, connection = details
	print(details)


# https://stackoverflow.com/questions/10865116/tkinter-creating-buttons-in-for-loop-passing-command-arguments
class StartPage(tk.Frame):

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

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		parent.config(bg = '#F0F0F0')
		parent.pack(fill = "both", expand = 1)

		canvas = tk.Canvas(self, width=WIDTH, height=HEIGHT, background="#D2D2D2")
		canvas.place(x=0, y=0)
		self.monitor_displays = {}

		submit = ttk.Button(self, text="Apply Choice", command=self.on_submit)
		dw, dh = place_element(canvas, 50, 500, submit)

		self.output = tk.Listbox(self, width=100, selectmode='single')
		place_element(canvas, 50, 500+dh, self.output)

		import os
		import subprocess, sys
		path = os.path.join(R"C:\Users\Nawar\Documents\GitHub\Monitor-Setup-Helper\src", "get_monitors.ps1")
		p = subprocess.check_output(["powershell.exe", "-ExecutionPolicy", "Unrestricted", path])
		p = str(p).strip("\\b'").strip("\\'").replace('\\x00', '').strip('\\r\\n')
		serials = []
		for monitor in p.split('\\r\\n'):
			serials.append(monitor.split(',')[1].strip())

		w = 50
		for serial in serials:
			submit = ttk.Button(self, text=f"Flash", command=lambda serial=serial:DDM(serial).flash())
			dw, dh = place_element(canvas, w, 25, submit)
			w += dw
			submit = tk.Listbox(self, selectmode='single', height=1)
			submit.insert(0, serial)
			dw, dh = place_element(canvas, w, 25, submit)
			w += dw + 10

		def draw_monitor(x, y, monitor):
			padding = 10

			label = ttk.Label(self, text=monitor.name.capitalize(), font=LARGE_FONT)
			monitor_w, monitor_h = place_element(canvas, x, y, label)


			options = [name.capitalize() for name, details in DEVICES.items() if not hasattr(details, 'watching')]

			self.monitor_displays[monitor.name].set(options[0])
			option = ttk.OptionMenu(self, self.monitor_displays[monitor.name], options[0], *options, command=lambda _:self.on_choose())
			monitor_w, monitor_h = place_element(canvas, x, y+monitor_h, option)

			positions = {}

			# Inputs
			total_width = 0  # Determine Size
			for port in monitor.inputs:
				button = ttk.Button(self, text=port['kind'])
				w, h = probe_bbox(canvas, x, y, button)
				total_width += w

			width = 0  # Draw
			for i, port in enumerate(monitor.inputs):
				string = (monitor.name, port['kind'], (port['used'][0].name, port['used'][1])) if port['used'] else (monitor.name, port['kind'], None)
				button = ttk.Button(self, text=port['kind'], command=lambda string=string: handle_button(string))
				X, Y = x+width-total_width/2+monitor_w/2, y+h+padding+2*monitor_h
				w, h = place_element(canvas, X, Y, button)
				positions[(monitor.name, 'in', port['kind'])] = (X, Y, w, h)
				width += w

			# Outputs
			total_height = 0  # Determine Size
			for port in monitor.outputs:
				button = ttk.Button(self, text=port['kind'])
				w, h = probe_bbox(canvas, x, y, button)
				total_height += h

			height = 0  # Draw
			for i, port in enumerate(monitor.outputs):
				button = ttk.Button(self, text=port['kind'])
				X, Y = x-total_width/2-w/2, y+height-h+2*monitor_h
				w, h = place_element(canvas, X, Y, button)
				positions[(monitor.name, 'out', port['kind'])] = (X, Y, w, h)
				height += h

			x1, y1, x2, y2 = x-total_width/2-w/2-padding, y-total_height/2, x+total_width/2+w, y+total_height/2+2*h+2*monitor_h+padding
			canvas.create_rectangle(x1, y1, x2, y2)
			return x1, y1, x2, y2, positions

		def draw_device(x, y, device):
			padding = 10

			label = ttk.Label(self, text=name.capitalize(), font=LARGE_FONT)
			w, h = probe_bbox(canvas, x, y, label)
			monitor_width, h = place_element(canvas, x-w/2, y, label)

			positions = {}

			# Outputs
			total_height = h*2
			total_width = 0  # Determine Size
			for port in device.outputs:
				button = ttk.Button(self, text=port['kind'])
				w, h = probe_bbox(canvas, x, y, button)
				total_width += w

			width = 0  # Draw
			for i, port in enumerate(device.outputs):
				button = ttk.Button(self, text=port['kind'])
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
				self.monitor_displays.update({name: tk.StringVar(self)})
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
					print(name, port['kind'], connected_port)
					canvas.create_line(x+w/2, y, X+W/2, Y+H/2)

		self.on_choose()

	def on_choose(self):
			desired_configuration = {n: v.get().lower() for n, v in self.monitor_displays.items()}
			x = find_configuration(DEVICES, desired_configuration)
			self.output.delete(0, self.output.size())
			for i, y in enumerate(x):
				self.output.insert(i, y)


class PageOne(tk.Frame):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		label = ttk.Label(self, text="Page One!!!", font=LARGE_FONT)
		label.pack(pady=10,padx=10)

		button1 = ttk.Button(self, text="Back to Home",
									 command=lambda: controller.show_frame(StartPage)).pack()



class PageTwo(tk.Frame):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		label = ttk.Label(self, text="Page Two!!!", font=LARGE_FONT)
		label.pack(pady=10,padx=10)

		button1 = ttk.Button(self, text="Back to Home",
									 command=lambda: controller.show_frame(StartPage))
		button1.pack()

		button2 = ttk.Button(self, text="Page One",
									 command=lambda: controller.show_frame(PageOne))
		button2.pack()


if __name__ == '__main__':
	from main import load, save
	CABLES, DEVICES, CONNECTIONS = load()
	app = SeaofBTCapp()
	# app.bind('<Motion>', motion)
	app.mainloop()
