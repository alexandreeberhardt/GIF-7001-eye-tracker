from enum import Enum


class AppNotification(Enum):
	CLOSE_ALL_WINDOW = "close_all_window"
	SHOW_SUB_WINDOW = "show_sub_window"
	RECORD = "record"
	START = "start"
	STOP = "stop"
	POSITIONS_NOTIFICATION = "positions_notification"
	SEND_ERROR_MESSAGE = "send_error_message"
	SEND_POSITIONS = "send_positions"
	CLOSE_CALIBRATION_WINDOW = "close_calibration_window"
	UPDATE_CALIBRATION_POINT = "update_calibration_point"
	UPDATE_CALIBRATION_POSITION = "update_calibration_position"
	START_CALIBRATION = "start_calibration"
	STOP_CALIBRATION = "stop_calibration"
