from Model.NotificationCenter import NotificationCenter
from Model.NotificationList import AppNotification
from Model.GlobalVariables import GlobalVariables
from Model.SingletonDecorator import singleton
from tkinter import ttk, messagebox
from tkinter import font as tkfont
import tkinter as tk
import os


from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np


@singleton
class ViewVisualisation(tk.Toplevel):
	def __init__(self, shared_font=None):
		super().__init__()
		self.withdraw()
		self.attributes("-topmost", True)
		self.iconbitmap(f"{os.path.abspath('')}{os.sep}View{os.sep}logo{os.sep}logo.ico")
		self.shared_font = shared_font if shared_font else tkfont.Font(family="Arial", size=10)
		self.protocol("WM_DELETE_WINDOW", self.on_close)
		self.initialize_graph()
		self.x = []
		self.y = []

		NotificationCenter().add_observer(self, self.close_all_window, AppNotification.CLOSE_ALL_WINDOW)
		NotificationCenter().add_observer(self, self.open_this_window, AppNotification.SHOW_SUB_WINDOW)
		NotificationCenter().add_observer(self, self.draw_graph, AppNotification.SEND_POSITIONS)


	def close_all_window(self, notification):
		self.destroy()

	def on_close(self):
		self.withdraw()

	def open_this_window(self, notification):
		if notification.posted_data == "pb_visualisation":
			self.deiconify()

	def initialize_graph(self):
		w = self.winfo_screenwidth()
		h = self.winfo_screenheight()

		fig = Figure(figsize=(5, 4), dpi=100)
		fig.tight_layout()
		self.ax = fig.add_subplot(111)
		self.line2, = self.ax.plot([0,w,w,0,0], [0,0,-h,-h,0], color="k")
		self.line1, = self.ax.plot([], [], marker=".", color="r")

		self.ax.set_xlim(-2000, w + 2000)
		self.ax.set_ylim(-h-2000, 2000)

		self.canvas = FigureCanvasTkAgg(fig, master=self)
		self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

	def draw_graph(self, notification):
		pos = notification.posted_data
		self.x.append(pos[-1])
		self.y.append(-pos[0])

		if len(self.x)>20:
			self.x.pop(0)
			self.y.pop(0)

		print(pos)
		# self.ax.set_xlim(np.min(self.x), np.min(self.x) + 10)
		# self.ax.set_ylim(np.min(self.y), np.min(self.y) + 10)
		self.line1.set_data(self.x, self.y)
		self.canvas.draw()
