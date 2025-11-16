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
class ViewCalibration(tk.Toplevel):
	def __init__(self, shared_font=None):
		super().__init__()
		self.withdraw()
		self.attributes("-topmost", True)
		#self.iconbitmap(f"{os.path.abspath('')}{os.sep}View{os.sep}logo{os.sep}logo.ico")
		self.iconphoto(False, tk.PhotoImage(file="View/logo/logo.png"))
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
		if notification.posted_data == "pb_calibrate":
			self.deiconify()

	def initialize_graph(self):
		fig = Figure(figsize=(5, 4), dpi=100)
		fig.tight_layout()
		ax = fig.add_subplot(111)
		ax.set_xlim(-1, 1)
		ax.set_ylim(-1, 1)
		self.line1, = ax.plot([], [], marker=".", color="r")
		self.line2, = ax.plot([], [], marker=".", color="b")

		self.angle_y = ax.text(-0.9, 0.9, "Angle y: 0.0", fontsize=12, ha='center')
		self.angle_x = ax.text(-0.9, 0.8, "Angle y: 0.0", fontsize=12, ha='center')


		self.canvas = FigureCanvasTkAgg(fig, master=self)
		self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

	def draw_graph(self, notification):
		pos = notification.posted_data

		self.left_x.append(pos[0][-1])
		self.right_x.append(pos[-1][-1])
		self.left_y.append(pos[0][0])
		self.right_y.append(pos[-1][0])

		if len(self.left_x)>10:
			self.left_x = self.left_x[-10:]
			self.left_y = self.left_y[-10:]
		if len(self.right_x)>10:
			self.right_x = self.right_x[-10:]
			self.right_y = self.right_y[-10:]

		angle_y = np.mean([ self.compute_angle(np.mean(self.left_y)), self.compute_angle(np.mean(self.right_y)) ])
		angle_x = np.mean([ self.compute_angle(np.mean(self.left_x)), self.compute_angle(np.mean(self.right_x)) ])

		self.line1.set_data([np.mean(self.left_x)], [np.mean(self.left_y)])
		self.line2.set_data([np.mean(self.right_x)], [np.mean(self.right_y)])
		self.angle_y.set_text(f"Angle y: {angle_y:2.2f}")
		self.angle_x.set_text(f"Angle x: {angle_x:2.2f}")
		self.canvas.draw()

	def compute_angle(self, x):
		angle = np.degrees(np.arcsin(x))
		return angle