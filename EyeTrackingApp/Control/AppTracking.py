from Model.NotificationCenter import NotificationCenter
from Model.NotificationList import AppNotification
from Model.GlobalVariables import GlobalVariables
from Model.SingletonDecorator import singleton
from Model.ThreadWorker import Worker
from Model.EyeTracker import EyeTracker
from Model.MonitorMap import MonitorMap
from Model.ConvertCoordinate import ConvertCoordinate
from dataclasses import dataclass
import numpy as np
import random as rd
import shutil
import time
from pickle import load
import os


@dataclass
class Pos:
	x: int
	y: int

@singleton
class AppTracking():
	def __init__(self, screen_width, screen_height):
		super().__init__()
		self.actual_worker = Worker(self.tracking_function, None)

		self.left_monitor_map_1 = MonitorMap(1920, 1080, "camera1_left")
		self.right_monitor_map_1 = MonitorMap(1920, 1080, "camera1_right")
		self.left_monitor_map_2 = MonitorMap(1920, 1080, "camera2_left")
		self.right_monitor_map_2 = MonitorMap(1920, 1080, "camera2_right")

		eye_tracker = EyeTracker()
		self.convert_coordinate = ConvertCoordinate(eye_tracker.width, eye_tracker.height, focal_length_px=983.0)
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
			self.actual_worker = Worker(self.tracking_function, args, progress_callback=self.show_positions,
										finished_callback=self.close_tracking_thread)
			self.actual_worker.start()

	def stop_tracking(self, notification):
		if self.actual_worker.is_alive():
			self.actual_worker.stop()

	def start_calibration(self, notification):
		args = None
		if not self.actual_worker.is_alive():
			self.actual_worker = Worker(self.calibration_function, args, progress_callback=self.calibration_signal,
										finished_callback=self.close_calibration_thread)
			self.actual_worker.start()

	def stop_calibration(self, notification):
		if self.actual_worker.is_alive():
			self.actual_worker.stop()

	def tracking_function(self, args, progress_callback=None, worker=None):
		eye_tracker_1 = EyeTracker(camera_index=0)
		eye_tracker_2 = EyeTracker(camera_index=1)
		start = time.perf_counter()
		while True:
			if worker.is_stopped():
				break
			left_vector_1, right_vector_1 = eye_tracker_1.get_vectors()
			left_vector_2, right_vector_2 = eye_tracker_2.get_vectors()

			if left_vector is not None:
				d1 = self.convert_coordinate.compute_head_distance_cm(left_vector_1, right_vector_1)
				d2 = self.convert_coordinate.compute_head_distance_cm(left_vector_2, right_vector_2)

				new_left_1, new_right_1 = self.convert_coordinate.camera_to_world(left_vector_1, right_vector_1, d1)
				new_left_2, new_right_2 = self.convert_coordinate.camera_to_world(left_vector_2, right_vector_1, d2)

				position_left_1 = self.left_monitor_map_1.predict(new_left_1)
				position_right_1 = self.left_monitor_map_1.predict(new_right_1)
				position_left_2 = self.left_monitor_map_2.predict(new_left_2)
				position_right_2 = self.left_monitor_map_2.predict(new_right_2)

				x = np.mean([position_left_1.x, position_right_1.x, position_left_2.x, position_right_2.x])
				y = np.mean([position_left_1.y, position_right_1.y, position_left_2.y, position_right_2.y])
				progress_callback(Pos(int(x), int(y)))
		eye_tracker_1.cleanup()
		eye_tracker_2.cleanup()
		return 0

	def calibration_function(self, args, progress_callback=None, worker=None):
		eye_tracker_1 = EyeTracker(camera_index=0)
		eye_tracker_2 = EyeTracker(camera_index=1)
		progress_callback((10, None, None, None, None))
		for point_id in range(9):
			progress_callback((point_id, None, None, None, None))
			time.sleep(1)
			left_positions_1 = []
			right_positions_1 = []

			left_positions_2 = []
			right_positions_2 = []

			for buffer_frame in range(15):
				_, _ = eye_tracker_1.get_vectors()
				_, _ = eye_tracker_2.get_vectors()
			for frame_id in range(30):
				left_vector_1, right_vector_1 = eye_tracker_1.get_vectors()
				left_vector_2, right_vector_2 = eye_tracker_2.get_vectors()
				if left_vector_1 is not None:
					d1 = self.convert_coordinate.compute_head_distance_cm(left_vector_1, right_vector_1)
					d2 = self.convert_coordinate.compute_head_distance_cm(left_vector_2, right_vector_2)

					left_pos_1, right_pos_1 = self.convert_coordinate.camera_to_world(left_vector_1, right_vector_1, d1)
					left_pos_2, right_pos_2 = self.convert_coordinate.camera_to_world(left_vector_2, right_vector_2, d2)

					left_positions_1.append(left_pos_1)
					right_positions_1.append(right_pos__1)
					left_positions_2.append(left_pos__2)
					right_positions_2.append(right_pos__2)
			progress_callback((point_id, left_positions_1, right_positions_1, left_positions_2, right_positions_2))
			if worker.is_stopped():
				break
		progress_callback((10, None, None, None, None))
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
			self.left_monitor_map_1.train_model()
			self.right_monitor_map_1.train_model()
			self.left_monitor_map_2.train_model()
			self.right_monitor_map_2.train_model()

			self.left_monitor_map_1.save_models("camera1_left")
			self.right_monitor_map_1.save_models("camera1_right")
			self.left_monitor_map_2.save_models("camera2_left")
			self.right_monitor_map_2.save_models("camera2_right")

	def update_calibration_position(self, notification):
		point_id, left_positions_1, right_positions_1, left_positions_2, right_positions_2 = notification.posted_data

		self.left_monitor_map.set_new_point(point_id, left_positions)
		self.right_monitor_map.set_new_point(point_id, right_positions)

		self.left_monitor_map_1.set_new_point(point_id, left_positions_1)
		self.right_monitor_map_1.set_new_point(point_id, right_positions_1)
		self.left_monitor_map_2.set_new_point(point_id, left_positions_2)
		self.right_monitor_map_2.set_new_point(point_id, right_positions_2)