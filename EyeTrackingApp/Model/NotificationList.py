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
