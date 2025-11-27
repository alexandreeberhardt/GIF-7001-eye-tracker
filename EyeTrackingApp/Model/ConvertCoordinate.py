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

    def __init__(self, frame_width, frame_height,
                 real_eye_distance_cm: float = 6.0,
                 focal_length_px: float | None = None):
        self.w = frame_width
        self.h = frame_height
        self.real_eye_distance_cm = float(real_eye_distance_cm)

        self.focal_length_px = float(focal_length_px) if focal_length_px is not None else float(frame_width)

    def compute_head_distance_cm(self, left_vector: LineOfSight, right_vector: LineOfSight) -> float:

        pixel_distance = abs(left_vector.x - right_vector.x)
        if pixel_distance <= 1e-6:
            return 0.0
        return (self.real_eye_distance_cm * self.focal_length_px) / pixel_distance

    def camera_to_world(self, left_vector: LineOfSight, right_vector: LineOfSight, l: float | None = None):


        if l is None:
            l = self.compute_head_distance_cm(left_vector, right_vector)

        pixel_distance = abs(left_vector.x - right_vector.x)

        if pixel_distance <= 1e-6:
            return PosWorld(0.0, 0.0), PosWorld(0.0, 0.0)
        alpha_l = self.real_eye_distance_cm / pixel_distance 

        left_x_world  = (left_vector.x  - self.w / 2.0) * alpha_l + l * np.tan(np.deg2rad(left_vector.theta_x))
        left_y_world  = (left_vector.y  - self.h / 2.0) * alpha_l + l * np.tan(np.deg2rad(left_vector.theta_y))
        right_x_world = (right_vector.x - self.w / 2.0) * alpha_l + l * np.tan(np.deg2rad(right_vector.theta_x))
        right_y_world = (right_vector.y - self.h / 2.0) * alpha_l + l * np.tan(np.deg2rad(right_vector.theta_y))

        return PosWorld(left_x_world, left_y_world), PosWorld(right_x_world, right_y_world)