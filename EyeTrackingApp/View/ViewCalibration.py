from Model.NotificationCenter import NotificationCenter
from Model.NotificationList import AppNotification
from Model.GlobalVariables import GlobalVariables
from Model.SingletonDecorator import singleton
from tkinter import ttk, messagebox
from tkinter import font as tkfont
import tkinter as tk
import os


@singleton
class ViewCalibration(tk.Toplevel):
	def __init__(self, shared_font=None):
		super().__init__()
		self.withdraw()
		self.attributes("-topmost", True)
		self.iconbitmap(f"{os.path.abspath('')}{os.sep}View{os.sep}logo{os.sep}logo.ico")
		self.shared_font = shared_font if shared_font else tkfont.Font(family="Arial", size=10)
		self.protocol("WM_DELETE_WINDOW", self.on_close)

		NotificationCenter().add_observer(self, self.close_all_window, AppNotification.CLOSE_ALL_WINDOW)
		NotificationCenter().add_observer(self, self.open_this_window, AppNotification.SHOW_SUB_WINDOW)



	def close_all_window(self, notification):
		self.destroy()

	def on_close(self):
		self.withdraw()

	def open_this_window(self, notification):
		if notification.posted_data == "pb_calibrate":
			self.deiconify()
