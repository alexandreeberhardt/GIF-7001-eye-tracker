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
		self.attributes('-fullscreen', True)# Plein écran
		self.attributes("-topmost", True)
		self.config(bg='black')

		self.canvas = tk.Canvas(self, bg='black', highlightthickness=0)
		self.canvas.pack(fill='both', expand=True)

		#self.iconbitmap(f"{os.path.abspath('')}{os.sep}View{os.sep}logo{os.sep}logo.ico")
		self.iconphoto(False, tk.PhotoImage(file="EyeTrackingApp/View/logo/logo.png"))
		self.shared_font = shared_font if shared_font else tkfont.Font(family="Arial", size=10)
		self.protocol("WM_DELETE_WINDOW", self.on_close)
		self.bind('<Escape>', lambda e: self.on_close())

		NotificationCenter().add_observer(self, self.close_all_window, AppNotification.CLOSE_ALL_WINDOW)
		NotificationCenter().add_observer(self, self.open_this_window, AppNotification.SHOW_SUB_WINDOW)
		NotificationCenter().add_observer(self, self.on_close, AppNotification.CLOSE_CALIBRATION_WINDOW)
		NotificationCenter().add_observer(self, self.show_calibration_point, AppNotification.UPDATE_CALIBRATION_POINT)

	def close_all_window(self, notification):
		self.destroy()

	def on_close(self, notification=None):
		if notification is None:
			NotificationCenter().post_notification(AppNotification.STOP_CALIBRATION, self, True)
		self.withdraw()

	def open_this_window(self, notification):
		if notification.posted_data == "pb_calibrate":
			self.deiconify()

	def show_calibration_point(self, notification):
		w = self.winfo_screenwidth()
		h = self.winfo_screenheight()

		point_id = notification.posted_data
		rayon = int(0.05*np.min([w,h]))
		self.canvas.delete('point')
		if point_id != 10:
			x = (point_id//3)*w/2
			y = (point_id%3)*h/2
			self.canvas.create_oval(
				x - rayon, y - rayon,
				x + rayon, y + rayon,
				fill='lime', outline='', tags='point')
