from dataclasses import dataclass
import numpy as np


@dataclass
class LineOfSight:
	x: float  # pixel
	y: float  # pixel
	theta_x: float  # degrés
	theta_y: float  # degrés


@dataclass
class PosWorld:
	x: float  # cm
	y: float  # cm



class ConvertCoordinate:
	def __init__(self, screen_width, screen_height):
		self.w = screen_width
		self.h = screen_height

	def camera_to_world(self, left_vector, right_vector, l):
		# facteur de conversion pixels → cm (6 cm entre pupilles)
		alpha_l = 6.0 / np.abs(left_vector.x - right_vector.x)  # cm/pixel

		# Conversion en coordonnées monde
		left_x_world  = (left_vector.x  - self.w/2) * alpha_l + l * np.tan(np.deg2rad(left_vector.theta_x))
		left_y_world  = (left_vector.y  - self.h/2) * alpha_l + l * np.tan(np.deg2rad(left_vector.theta_y))
		right_x_world = (right_vector.x - self.w/2) * alpha_l + l * np.tan(np.deg2rad(right_vector.theta_x))
		right_y_world = (right_vector.y - self.h/2) * alpha_l + l * np.tan(np.deg2rad(right_vector.theta_y))

		return PosWorld(left_x_world, left_y_world), PosWorld(right_x_world, right_y_world)