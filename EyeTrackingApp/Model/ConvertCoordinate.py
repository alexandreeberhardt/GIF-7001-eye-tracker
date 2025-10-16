from dataclasses import dataclass
import numpy as np


@dataclass
class LineOfSight:
	x: float  # pixel
	y: float  # pixel
	theta_x: float  # degrés
	theta_y: float  # degrés


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
		new_x = l*(left_vector.x-self.w/2)/self.w + l*np.tan(np.pi*left_vector.theta_x/180)
