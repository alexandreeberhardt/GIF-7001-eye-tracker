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
		self.left_x = []
		self.right_x = []
		self.left_y = []
		self.right_y = []

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
		fig = Figure(figsize=(5, 4), dpi=100)
		fig.tight_layout()
		ax = fig.add_subplot(111)
		ax.set_xlim(-45, 45)
		ax.set_ylim(-45, 45)
		self.line1, = ax.plot([], [], marker=".", color="r")
		self.line2, = ax.plot([], [], marker=".", color="b")

		self.angle_y = ax.text(-40, 40, "Angle y: 0.0", fontsize=12, ha='center')
		self.angle_x = ax.text(-40, 35, "Angle y: 0.0", fontsize=12, ha='center')


		self.canvas = FigureCanvasTkAgg(fig, master=self)
		self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

	def draw_graph(self, notification):
		angle = notification.posted_data

		self.left_x = angle[0].theta_x
		self.right_x = angle[-1].theta_x
		self.left_y = angle[0].theta_y
		self.right_y = angle[-1].theta_y

		angle_y = np.mean([self.left_y, self.right_y])
		angle_x = np.mean([self.left_x, self.right_x])

		self.line1.set_data([self.left_x], [self.left_y])
		self.line2.set_data([self.right_x], [self.right_y])
		self.angle_y.set_text(f"Angle y: {angle_y:2.2f}")
		self.angle_x.set_text(f"Angle x: {angle_x:2.2f}")
		self.canvas.draw()
