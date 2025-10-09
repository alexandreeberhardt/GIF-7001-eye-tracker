from Model.GlobalVariables import GlobalVariables
import threading


class Worker(threading.Thread):
	def __init__(self, workerFunction, *args, progress_callback=None, finished_callback=None):
		super().__init__(daemon=True)
		self.function = workerFunction
		self.after = GlobalVariables().root.after
		self.args = args
		self.progress_callback = progress_callback
		self.finished_callback = finished_callback
		self.result = None
		self._stop_requested = False

	def stop(self):
		self._stop_requested = True

	def is_stopped(self):
		"""Retourne True si une annulation a été demandée"""
		return self._stop_requested

	def run(self):
		try:
			func_params = self.function.__code__.co_varnames
			kwargs = {}

			# Inject progress_callback si attendu
			if "progress_callback" in func_params and self.progress_callback:
				def safe_progress(value):
					if not self._stop_requested:
						self.after(0, lambda v=value: self.progress_callback(v))
				kwargs["progress_callback"] = safe_progress

			# Inject worker si attendu
			if "worker" in func_params:
				kwargs["worker"] = self

			# Exécuter la fonction
			self.result = self.function(*self.args, **kwargs)

			# Callback de fin
			if self.finished_callback and not self._stop_requested:
				self.after(0, lambda r=self.result: self.finished_callback(r))

		except Exception as e:
			print(str(e))
			self.result = str(e)
			if self.finished_callback:
				self.after(0, lambda r=self.result: self.finished_callback(r))
