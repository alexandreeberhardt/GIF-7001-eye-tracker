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
		""" Voici le problème:
			La caméra a un champ de vision, que l'on doit sûrement caractériser.
			Comme ça on pourra savoir qu'une position de pixel à L distance de l'écran
			 = à X mètre du centre de la caméra dans le plan de la caméra. Ensuite, on
			 fait un ptit classique trigonométrie pour trouver la position du regard
			 obtenue avec l'angle des vecteurs.
			 On pourra ensuite utiliser cette position pour entrainer le modèle de 
			 MonitorMap. Est-ce que ça vous va?
		"""
		# test un peu bullshit qui montre l'idée générale du calcul à faire
		alpha_l = np.abs(left_vector.x-right_vector.x) / 6  # pixel/cm, environ 6 cm entre les pupilles
		left_x_world = (left_vector.x-self.w/2)/alpha_l + l*np.tan(np.pi*left_vector.theta_x/180) # cm
		left_y_world = (left_vector.y-self.h/2)/alpha_l + l*np.tan(np.pi*left_vector.theta_y/180) # cm
		right_x_world = (right_vector.x-self.w/2)/alpha_l + l*np.tan(np.pi*right_vector.theta_x/180) # cm
		right_y_world = (right_vector.x-self.h/2)/alpha_l + l*np.tan(np.pi*right_vector.theta_y/180) # cm
		return PosWorld(left_x_world, left_y_world), PosWorld(right_x_world, right_y_world)
