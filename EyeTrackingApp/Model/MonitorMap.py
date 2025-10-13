from dataclasses import dataclass
import numpy as np

@dataclass
class LineOfSight:
	x: float # pixel
	y: float # pixel
	theta_x: float # degrés
	theta_y: float # degrés

class MonitorMap:
	def __init__(self, screen_width, screen_height):
		self.w = screen_width
		self.h = screen_height

	def set_new_point(self, point_id, left_vectors, right_vectors):
		""" ici left_vectors et right_vectors sont des listes de LineOfSight
			point_id est un int de 0 à 8, tu peux retrouver la ligne + colonne 
			avec point_i//3, point_id%3). cela représente la position relative
			sur ton écran, de haut en bas.
		""" 
		pass

	def translate_to_monitor_position(self, left_vector, right_vector):
		return np.array([y, x])