from dataclasses import dataclass
import numpy as np
import os
from pickle import dump, load

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt


# =====================================================
# ---- Thin Plate Spline interpolation helpers ----
# =====================================================

def _tps_U(r):
	"""Thin-plate radial basis: U(r) = r^2 * log(r^2); handle r=0 -> 0."""
	with np.errstate(divide='ignore', invalid='ignore'):
		rr = r**2
		out = rr * np.log(rr)
		out[np.isnan(out)] = 0.0
		out[np.isinf(out)] = 0.0
	return out


def _build_K(points):
	"""Build TPS kernel matrix K_ij = U(||pi - pj||)."""
	n = points.shape[0]
	K = np.zeros((n, n), dtype=float)
	for i in range(n):
		d = np.linalg.norm(points[i] - points, axis=1)
		K[i, :] = _tps_U(d)
	return K


def _tps_fit(points, targets):
	"""
	Fit TPS mapping points -> targets (1D scalar per target)
	returns (w, a) where w are n weights, a are 3 affine parameters.
	"""
	n = points.shape[0]
	K = _build_K(points)
	P = np.column_stack([points, np.ones(n)])
	A = np.zeros((n + 3, n + 3), dtype=float)
	A[:n, :n] = K
	A[:n, n:] = P
	A[n:, :n] = P.T
	rhs = np.concatenate([targets, np.zeros(3)])
	params = np.linalg.solve(A, rhs)
	w = params[:n]
	a = params[n:]
	return w, a


def _tps_predict(points_ctrl, w, a, query_points):
	"""Evaluate TPS mapping at query_points."""
	m = query_points.shape[0]
	Kq = np.zeros((m, len(points_ctrl)), dtype=float)
	for i in range(m):
		d = np.linalg.norm(query_points[i] - points_ctrl, axis=1)
		Kq[i, :] = _tps_U(d)
	Pq = np.column_stack([query_points, np.ones(m)])
	return Kq.dot(w) + Pq.dot(a)


# =====================================================
# ---- Main data classes ----
# =====================================================

@dataclass
class PosWorld:
	x: float  # cm
	y: float  # cm


class MonitorMap:
	"""Calibration mapping between world (cm) and monitor (px) using Thin Plate Spline."""

	def __init__(self, screen_width, screen_height, model_path=None):
		self.w = screen_width
		self.h = screen_height
		self.x_screen = []
		self.y_screen = []
		self.data = []

		# TPS model parameters
		self._tps_ctrl = None
		self._tps_wx = None
		self._tps_ax = None
		self._tps_wy = None
		self._tps_ay = None

		# Charger un modèle existant si spécifié
		if model_path is not None:
			if os.path.exists(f"{model_path}_model.pkl"):
				self.load_models(model_path)

	# -----------------------------
	#   Calibration point handling
	# -----------------------------
	def set_new_point(self, point_id, vectors):
		"""
		Add a calibration point (3×3 grid -> 9 points).
		point_id: int 0–8 (row-major)
		vectors: iterable of PosWorld
		"""
		col = point_id // 3
		row = point_id % 3

		x_point = (col / 2.0) * self.w
		y_point = (row / 2.0) * self.h
		self.x_screen.append(float(x_point))
		self.y_screen.append(float(y_point))

		if not vectors:
			raise ValueError("vectors must contain at least one PosWorld measurement.")
		arr = np.array([[v.x, v.y] for v in vectors], dtype=float)
		median_xy = np.median(arr, axis=0)
		self.data.append(median_xy)

	def feature_matrix(self):
		if len(self.data) == 0:
			raise ValueError("No calibration data available.")
		return np.vstack(self.data)

	# -----------------------------
	#   Train / Predict
	# -----------------------------
	def train_model(self):
		"""Train the Thin Plate Spline (TPS) model."""
		X = self.feature_matrix()
		yx = np.array(self.x_screen, dtype=float)
		yy = np.array(self.y_screen, dtype=float)

		self._tps_ctrl = X
		self._tps_wx, self._tps_ax = _tps_fit(X, yx)
		self._tps_wy, self._tps_ay = _tps_fit(X, yy)

	def predict(self, vector: PosWorld):
		"""Predict (x_pixel, y_pixel) from a measured position (cm)."""
		if self._tps_ctrl is None:
			raise ValueError("TPS model not trained or loaded.")
		pt = np.array([[float(vector.x), float(vector.y)]])
		px = _tps_predict(self._tps_ctrl, self._tps_wx, self._tps_ax, pt)[0]
		py = _tps_predict(self._tps_ctrl, self._tps_wy, self._tps_ay, pt)[0]
		return PosWorld(float(px), float(py))

	def translate_to_monitor_position(self, vector):
		return self.predict(vector)

	def save_models(self, filename_prefix):
		if self._tps_ctrl is None:
			raise ValueError("No trained TPS model to save.")
		
		data = {"ctrl": np.asarray(self._tps_ctrl, dtype=float),
			"wx": np.asarray(self._tps_wx, dtype=float),
			"ax": np.asarray(self._tps_ax, dtype=float),
			"wy": np.asarray(self._tps_wy, dtype=float),
			"ay": np.asarray(self._tps_ay, dtype=float),}

		path = f"{filename_prefix}_model.pkl"
		with open(path, "wb") as f:
			dump(data, f, protocol=4)

	def load_models(self, model_path):
		model_path = f"{model_path}_model.pkl"
		with open(model_path, "rb") as f:
			data = load(f)

		self._tps_ctrl = np.array(data["ctrl"], dtype=float)
		self._tps_wx = np.array(data["wx"], dtype=float)
		self._tps_ax = np.array(data["ax"], dtype=float)
		self._tps_wy = np.array(data["wy"], dtype=float)
		self._tps_ay = np.array(data["ay"], dtype=float)
