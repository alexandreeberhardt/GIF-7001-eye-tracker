from Model.NotificationCenter import NotificationCenter
from Model.NotificationList import AppNotification
from Model.GlobalVariables import GlobalVariables
from Model.SingletonDecorator import singleton
from Model.ThreadWorker import Worker
from Model.EyeTracker import EyeTracker
import numpy as np
import random as rd
import shutil
import time
import os


@singleton
class AppTracking():
	def __init__(self):
		super().__init__()
		self.actual_worker = Worker(self.tracking_function, None)
		self.notification_subscription()

	def notification_subscription(self):
		NotificationCenter().add_observer(self, self.start_tracking, AppNotification.START)
		NotificationCenter().add_observer(self, self.stop_tracking, AppNotification.STOP)

	def start_tracking(self, notification):
		args = None
		if not self.actual_worker.is_alive():
			self.actual_worker = Worker(self.tracking_function, args, progress_callback=self.show_positions, finished_callback=self.close_tracking_thread)
			self.actual_worker.start()

	def stop_tracking(self, notification):
		if self.actual_worker.is_alive():
			self.actual_worker.stop()

	def tracking_function(self, args, progress_callback=None, worker=None):
		eye_tracker = EyeTracker()
		while True:
			if worker.is_stopped():
				break
			infos = eye_tracker.get_infos()

			if infos.eye_left is not None:
				dydx_left = 2*(infos.eye_left-infos.iris_left)/infos.left_size
				dydx_right = 2*(infos.eye_right-infos.iris_right)/infos.right_size

				test = f"{dydx_left[0]:3.2f} | {dydx_left[-1]:3.2f}"
				progress_callback((dydx_left, dydx_right))
		eye_tracker.cleanup()
		return 0

	def show_positions(self, positions):
		NotificationCenter().post_notification(AppNotification.SEND_POSITIONS, self, positions)

	def close_tracking_thread(self, infos):
		if type(infos) is str:
			NotificationCenter().post_notification(AppNotification.SEND_ERROR_MESSAGE, self, f"error: {infos}")

	def angle_from_dxdy(self, dy, dx):
		angle = np.degrees(np.arctan2(dy, dx))
		return angle % 360