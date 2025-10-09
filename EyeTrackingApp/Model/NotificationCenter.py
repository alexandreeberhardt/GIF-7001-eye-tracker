# credit: Daniel Côté, available on pip: pip install mytk
from threading import RLock
from enum import Enum


class Notification:
	def __init__(self, name, object=None, posted_data=None):
		if not isinstance(name, Enum):
			raise ValueError("You must use an enum-subclass of Enum, not a string for the notification name")

		self.name = name
		self.object = object
		self.posted_data = posted_data

class ObserverInfo:
	def __init__(self, observer, method=None, notification_name=None, observed_object=None):
		self.observer = observer
		self.method = method
		self.observed_object = observed_object
		self.notification_name = notification_name

	def matches(self, other_observer) -> bool:
		if self.notification_name is not None and other_observer.notification_name is not None and self.notification_name != other_observer.notification_name:
			return False
		elif self.observed_object is not None and other_observer.observed_object is not None and self.observed_object != other_observer.observed_object:
			return False
		elif self.observer != other_observer.observer:
			return False
		return True

	def __eq__(self, rhs):
		return self.matches(rhs)

class NotificationCenter:
	_instance = None

	def destroy(self):
		nc = NotificationCenter()
		NotificationCenter._instance = None
		del(nc)

	def __init__(self):
		if not hasattr(self, 'observers'):
			self.observers = {}
		if not hasattr(self, 'lock'):
			self.lock = RLock()

	def __new__(cls, *args, **kwargs):
		if cls._instance is None:
			cls._instance = object.__new__(cls, *args, **kwargs)
		return cls._instance

	def add_observer(self, observer, method, notification_name=None, observed_object=None):
		if notification_name is not None and not isinstance(notification_name, Enum):
			raise ValueError("You must use an enum-subclass of Enum, not a string for the notification_name")

		observer_info = ObserverInfo(observer=observer, method=method, notification_name=notification_name, observed_object=observed_object)

		with self.lock:
			if notification_name not in self.observers.keys():
				self.observers[notification_name] = [observer_info]
			else:
				if observer_info not in self.observers[notification_name]:
					self.observers[notification_name].append(observer_info)

	def remove_observer(self, observer, notification_name=None, observed_object=None):
		if notification_name is not None and not isinstance(notification_name, Enum):
			raise ValueError("You must use an enum-subclass of Enum, not a string for the notification_name")

		observerToRemove = ObserverInfo(observer=observer, notification_name=notification_name, observed_object=observed_object)

		with self.lock:
			if notification_name is not None:
				self.observers[notification_name] = [currentObserver for currentObserver in self.observers[notification_name] if not currentObserver.matches(observerToRemove) ]
			else:
				for name in self.observers.keys():
					self.observers[name] = [observer for observer in self.observers[name] if not observer.matches(observerToRemove) ]		

	def post_notification(self, notification_name, notifying_object, posted_data=None):
		if not isinstance(notification_name, Enum):
			raise ValueError("You must use an enum-subclass of Enum, not a string for the notification_name")

		with self.lock:
			if notification_name in self.observers.keys():
				notification = Notification(notification_name, notifying_object, posted_data)
				for observer_info in self.observers[notification_name]:
					if observer_info.observed_object is None or observer_info.observed_object == notifying_object:
						observer_info.method(notification)

	def observers_count(self):
		with self.lock:
			count = 0
			for name in self.observers.keys():
				count += len(self.observers[name])
			return count

	def clear(self):
		with self.lock:
			self.observers = {}
