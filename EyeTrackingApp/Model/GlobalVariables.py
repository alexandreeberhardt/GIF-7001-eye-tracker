from dataclasses import dataclass


class GlobalVariables:
	_instance = None

	def __new__(cls, *args, **kwargs):
		if cls._instance is None:
			cls._instance = super().__new__(cls)
		return cls._instance

	def __init__(self):
		if not hasattr(self, "initialized"):
			self.initialized = True
			self.root = None

	def reset_all(self):
		self.root = None
