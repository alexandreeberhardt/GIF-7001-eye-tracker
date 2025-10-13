from Model.GlobalVariables import GlobalVariables
from Model.NotificationCenter import NotificationCenter
from Model.NotificationList import AppNotification
from Model.SingletonDecorator import singleton
from tkinter import ttk, filedialog
import tkinter as tk
import numpy as np
import os


@singleton
class ViewOption(ttk.Frame):
	def __init__(self, notebook, master):
		super().__init__(notebook)
		self.master = master
		self.setup_ui()
		NotificationCenter().add_observer(self, self.show_positions, AppNotification.SEND_POSITIONS)

	def setup_ui(self):
		for col in range(2):  
			self.columnconfigure(col, weight=1)  

		for row in range(2):  
			self.rowconfigure(row, weight=1)

		self.pb_start = ttk.Button(self, text="Start", command=self.start)
		self.pb_stop = ttk.Button(self, text="Stop", command=self.stop, state="disabled")

		self.pb_visualise = ttk.Button(self, text="Visualisation", command=self.visualise)
		self.pb_calibrate = ttk.Button(self, text="Calibration", command = self.calibrate)

		self.pb_start.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
		self.pb_stop.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
		self.pb_visualise.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
		self.pb_calibrate.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

	def calibrate(self):
		NotificationCenter().post_notification(AppNotification.SHOW_SUB_WINDOW, self, "pb_calibrate")
		NotificationCenter().post_notification(AppNotification.START_CALIBRATION, self, "start calibration")

	def visualise(self):
		NotificationCenter().post_notification(AppNotification.SHOW_SUB_WINDOW, self, "pb_visualisation")

	def record(self):
		NotificationCenter().post_notification(AppNotification.RECORD, self, "record")

	def start(self):
		NotificationCenter().post_notification(AppNotification.START, self, "start")
		self.pb_start.config(state="disabled")
		self.pb_stop.config(state="normal")

	def stop(self):
		NotificationCenter().post_notification(AppNotification.STOP, self, "stop")
		self.pb_start.config(state="normal")
		self.pb_stop.config(state="disabled")

	def show_positions(self, notification):
		pass
		# print(notification.posted_data)
		# print(notification.posted_data)