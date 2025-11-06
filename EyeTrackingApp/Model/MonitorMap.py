from dataclasses import dataclass
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.pipeline import Pipeline
from pickle import dump

import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


@dataclass
class PosWorld:
	x: float  # cm
	y: float  # cm


class MonitorMap:
	def __init__(self, screen_width, screen_height, pre_existing_models=None):
		self.w = screen_width
		self.h = screen_height
		self.x_screen = []
		self.y_screen = []
		self.data = []
		if pre_existing_models:
			self.model_x = pre_existing_models[0]
			self.model_y = pre_existing_models[1]
		self.feature_mat = None

	def set_new_point(self, point_id, vectors):
		""" 
			point_id est un int de 0 à 8, tu peux retrouver la ligne + colonne
			avec point_i//3, point_id%3). cela représente la position relative
			sur ton écran, de haut en bas.
		"""
		x_point = (point_id // 3) / 2 * self.w  # Divise par deux, car index va jusqu'à 2x la taille
		y_point = (point_id % 3) / 2 * self.h
		nframes = len(vectors)
		self.x_screen.extend([x_point] * nframes)
		self.y_screen.extend([y_point] * nframes)
		data = np.zeros((len(vectors), 2))
		for i in range(nframes):
			data[i] = vectors[i].x, vectors[i].y
		self.data.append(data)

	def feature_matrix(self):
		return np.vstack(self.data)

	def train_model(self, polynomial_degree=2, alpha=1):
		X = self.feature_matrix()
		poly = PolynomialFeatures(degree=polynomial_degree, include_bias=True)
		scaler = StandardScaler()

		pipeline_x = Pipeline([("scaler", scaler), ("poly", poly), ("ridge", Ridge(alpha=alpha))])
		pipeline_y = Pipeline([("scaler", scaler), ("poly", poly), ("ridge", Ridge(alpha=alpha))])
		pipeline_x.fit(X, self.x_screen)
		pipeline_y.fit(X, self.y_screen)
		self.model_x, self.model_y = pipeline_x, pipeline_y

	def predict(self, vector: PosWorld):
		if self.model_x is None or self.model_y is None:
			raise ValueError("Please train the model before predicting.")
		x = vector.x
		y = vector.y
		X = np.array([x, y]).reshape(1, -1)
		pred_x = self.model_x.predict(X)
		pred_y = self.model_y.predict(X)
		return np.array([pred_y, pred_x])

	def translate_to_monitor_position(self, vector):
		return self.predict(vector)

	def save_models(self, eye):
		if self.model_x is None or self.model_y is None:
			raise ValueError("Please train the model before saving.")
		with open(eye + "_model_x.pkl", "wb") as f:
			dump(self.model_x, f, protocol=5)
		with open(eye + "_model_y.pkl", "wb") as f:
			dump(self.model_y, f, protocol=5)
		with open(eye + "_calibration.txt", "w", encoding="utf-8") as f:
			X = self.feature_matrix()
			for i in range(len(self.x_screen)-1):
				f.write(f"{self.x_screen[i]},{self.y_screen[i]},{X[i][0]},{X[i][1]}\n")
			f.write(f"{self.x_screen[-1]},{self.y_screen[-1]},{X[-1][0]},{X[-1][1]}\n")
