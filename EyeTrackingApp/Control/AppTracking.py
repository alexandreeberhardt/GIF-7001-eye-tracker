from Model.NotificationCenter import NotificationCenter
from Model.NotificationList import AppNotification
from Model.GlobalVariables import GlobalVariables
from Model.SingletonDecorator import singleton
from Model.ThreadWorker import Worker
from Model.EyeTracker import EyeTracker
from Model.MonitorMap import MonitorMap
from Model.ConvertCoordinate import ConvertCoordinate
import numpy as np
import random as rd
import shutil
import time
import os


@singleton
class AppTracking():
	def __init__(self, screen_width, screen_height):
		super().__init__()
		self.actual_worker = Worker(self.tracking_function, None)
		self.monitor_map = MonitorMap(screen_width, screen_height)
		self.convert_coordinate = ConvertCoordinate(screen_width, screen_height)
		self.notification_subscription()

	def notification_subscription(self):
		NotificationCenter().add_observer(self, self.start_tracking, AppNotification.START)
		NotificationCenter().add_observer(self, self.stop_tracking, AppNotification.STOP)
		NotificationCenter().add_observer(self, self.start_calibration, AppNotification.START_CALIBRATION)
		NotificationCenter().add_observer(self, self.stop_calibration, AppNotification.STOP_CALIBRATION)
		NotificationCenter().add_observer(self, self.update_calibration_position, AppNotification.UPDATE_CALIBRATION_POSITION)

	def start_tracking(self, notification):
		args = None
		if not self.actual_worker.is_alive():
			self.actual_worker = Worker(self.tracking_function, args, progress_callback=self.show_positions, finished_callback=self.close_tracking_thread)
			self.actual_worker.start()

	def stop_tracking(self, notification):
		if self.actual_worker.is_alive():
			self.actual_worker.stop()

	def start_calibration(self, notification):
		args = None
		if not self.actual_worker.is_alive():
			self.actual_worker = Worker(self.calibration_function, args, progress_callback=self.calibration_signal, finished_callback=self.close_calibration_thread)
			self.actual_worker.start()

	def stop_calibration(self, notification):
		if self.actual_worker.is_alive():
			self.actual_worker.stop()

	def tracking_function(self, args, progress_callback=None, worker=None):
		eye_tracker = EyeTracker()
		while True:
			if worker.is_stopped():
				break
			left_vector, right_vector = eye_tracker.get_vectors()

			if left_vector is not None:
				new_left, new_right = self.convert_coordinate.camera_to_world(left_vector, right_vector, 60)
				position = self.monitor_map.predict(new_left, new_right)
				progress_callback(position)
		eye_tracker.cleanup()
		return 0

	def calibration_function(self, args, progress_callback=None, worker=None):
		eye_tracker = EyeTracker()
		progress_callback((10, None, None))
		for point_id in range(9):
			progress_callback((point_id, None, None))
			time.sleep(1)
			left_vectors = []
			right_vectors = []
			for frame_id in range(30): 
				left_vector, right_vector = eye_tracker.get_vectors()
				if left_vector is not None:
					left_vectors.append(left_vector)
					right_vectors.append(right_vector)
			progress_callback((point_id, left_vectors, right_vectors))
			if worker.is_stopped():
				break
		progress_callback((10, None, None))
		eye_tracker.cleanup()
		NotificationCenter().post_notification(AppNotification.CLOSE_CALIBRATION_WINDOW, self, True)
		return 0

	def show_positions(self, positions):
		NotificationCenter().post_notification(AppNotification.SEND_POSITIONS, self, positions)

	def calibration_signal(self, infos):
		if infos[-1] is None:
			NotificationCenter().post_notification(AppNotification.UPDATE_CALIBRATION_POINT, self, infos[0])
		else:
			NotificationCenter().post_notification(AppNotification.UPDATE_CALIBRATION_POSITION, self, infos)

	def close_tracking_thread(self, infos):
		if type(infos) is str:
			NotificationCenter().post_notification(AppNotification.SEND_ERROR_MESSAGE, self, f"error: {infos}")

	def close_calibration_thread(self, infos):
		if type(infos) is str:
			NotificationCenter().post_notification(AppNotification.SEND_ERROR_MESSAGE, self, f"error: {infos}")
		else:
			self.monitor_map.train_model()
	def update_calibration_position(self, notification):
		point_id, left_vectors, right_vectors = notification.posted_data
		left_positions = []
		right_positions = []
		for i in range(len(left_vectors)): 
			left_pos, right_pos = self.convert_coordinate.camera_to_world(left_vectors[i], right_vectors[i], 60)
			left_positions.append(left_pos)
			right_positions.append(right_pos)
		self.monitor_map.set_new_point(point_id, left_positions, right_positions)