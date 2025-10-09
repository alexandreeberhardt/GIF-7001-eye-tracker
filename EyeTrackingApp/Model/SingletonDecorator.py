
def singleton(cls):
	instances = {}

	def get_instance(*args, **kwargs):
		if cls not in instances:
			instances[cls] = cls(*args, **kwargs)
		return instances[cls]

	def is_initialized():
		return cls in instances

	def reset():
		if cls in instances:
			del instances[cls]

	get_instance.is_initialized = is_initialized
	get_instance.reset = reset

	return get_instance
