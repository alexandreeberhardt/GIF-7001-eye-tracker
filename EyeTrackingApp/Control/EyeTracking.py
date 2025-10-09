from Model.NotificationCenter import NotificationCenter
from Model.NotificationList import AppNotification
from Model.GlobalVariables import GlobalVariables
from Model.SingletonDecorator import singleton
from Model.ThreadWorker import Worker
import random as rd
import shutil
import time
import os


@singleton
class EyeTracking():
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
		while True:
			if worker.is_stopped():
				break
			progress_callback(rd.randint(0,10))
			time.sleep(1)
		return 0

	def show_positions(self, positions):
		NotificationCenter().post_notification(AppNotification.SEND_POSITIONS, self, positions)

	def close_tracking_thread(self, infos):
		if type(infos) is str:
			NotificationCenter().post_notification(AppNotification.SEND_ERROR_MESSAGE, self, f"error: {infos}")
