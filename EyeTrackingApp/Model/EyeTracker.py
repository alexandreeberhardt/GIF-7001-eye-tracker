import warnings
warnings.filterwarnings("ignore")
from dataclasses import dataclass
from scipy.ndimage import gaussian_filter
import mediapipe as mp
import numpy as np
import cv2

@dataclass
class Infos:
	eye_left: np.ndarray
	eye_right: np.ndarray
	pupil_left: np.ndarray
	pupil_right: np.ndarray
	x_size: float
	y_size: float
	pitch: float
	yaw: float
	roll: float

@dataclass
class LineOfSight:
	x: float
	y: float
	theta_x: float
	theta_y: float

class EyeTracker:
	def __init__(self, camera_index=1, frame_average=5):
		self.cap = cv2.VideoCapture(camera_index)

		self.frame_average = frame_average
		self.positions = None

		self.width  = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
		self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

		#Buffer pour le lissage
		self.left_pupil_buffer = []
		self.right_pupil_buffer = []
		self.x_size_buffer = []
		self.y_size_buffer = []
		self.left_eye_buffer = []
		self.right_eye_buffer = []

		# Regions d'intérêts
		self.LEFT_EYE = [33, 133] # coins des yeux
		self.RIGHT_EYE = [263, 362] # coins des yeux
		self.LEFT_ORBIT = [33, 133, 160, 159, 158, 144, 145, 153, 154, 155]
		self.RIGHT_ORBIT = [263, 362, 387, 386, 385, 373, 374, 380, 381, 382]
		self.LEFT_PUPIL = 468
		self.RIGHT_PUPIL = 473

		# MediaPipe Face Mesh
		self.face_mesh = mp.solutions.face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

	def get_head_pose(self, landmarks, w, h):
		FACE_IDX = {
			"nose_tip": 1,
			"chin": 152,
			"left_eye_corner": 33,
			"right_eye_corner": 263,
			"left_mouth": 61,
			"right_mouth": 291}

		model_points = np.array([
			(0.0, 0.0, 0.0),			 # nez
			(0.0, -63.6, -12.5),		 # menton
			(-43.3, 32.7, -26.0),		# coin œil gauche
			(43.3, 32.7, -26.0),		 # coin œil droit
			(-28.9, -28.9, -24.1),	   # bouche gauche
			(28.9, -28.9, -24.1)])		 # bouche droite

		image_points = np.array([
			(landmarks[FACE_IDX["nose_tip"]].x * w, landmarks[FACE_IDX["nose_tip"]].y * h),
			(landmarks[FACE_IDX["chin"]].x * w, landmarks[FACE_IDX["chin"]].y * h),
			(landmarks[FACE_IDX["left_eye_corner"]].x * w, landmarks[FACE_IDX["left_eye_corner"]].y * h),
			(landmarks[FACE_IDX["right_eye_corner"]].x * w, landmarks[FACE_IDX["right_eye_corner"]].y * h),
			(landmarks[FACE_IDX["left_mouth"]].x * w, landmarks[FACE_IDX["left_mouth"]].y * h),
			(landmarks[FACE_IDX["right_mouth"]].x * w, landmarks[FACE_IDX["right_mouth"]].y * h)], dtype="double")

		focal_length = w
		center = (w/2, h/2)
		camera_matrix = np.array([
			[focal_length, 0, center[0]],
			[0, focal_length, center[1]],
			[0, 0, 1]], dtype="double")

		dist_coeffs = np.zeros((4,1))
		success, rotation_vector, translation_vector = cv2.solvePnP(
			model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE)

		rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
		proj_matrix = np.hstack((rotation_matrix, translation_vector))
		_, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(proj_matrix)

		pitch, yaw, roll = [float(a) for a in euler_angles]
		return pitch, yaw, roll

	def get_bbox(self, landmarks, indices, w, h, margin=0):
		xs = [landmarks[i].x * w for i in indices]
		ys = [landmarks[i].y * h for i in indices]
		xmin, xmax = int(min(xs)) - margin, int(max(xs)) + margin
		ymin, ymax = int(min(ys)) - margin, int(max(ys)) + margin
		return max(0, xmin), max(0, ymin), min(w, xmax), min(h, ymax)

	def get_eye_center(self, landmarks, indices, w, h):
		xs = [landmarks[i].x * w for i in indices]
		ys = [landmarks[i].y * h for i in indices]
		
		return np.array([ys[-1], np.mean(xs)])

	def get_left_eye_center(self, landmarks, w, h):
		x = w * np.mean([landmarks[33].x,  landmarks[133].x])
		y = h * np.mean([landmarks[225].y,
			landmarks[224].y, landmarks[223].y, landmarks[222].y,
			landmarks[221].y, landmarks[117].y, landmarks[118].y,
			landmarks[119].y, landmarks[120].y, landmarks[121].y])
		return np.array([y, x])

	def get_right_eye_center(self, landmarks, w, h):
		x = w * np.mean([landmarks[263].x, landmarks[362].x])
		y = h * np.mean([landmarks[445].y,
			landmarks[444].y, landmarks[443].y, landmarks[442].y,
			landmarks[441].y, landmarks[346].y,landmarks[347].y,
			landmarks[348].y, landmarks[349].y, landmarks[350].y])
		return np.array([y, x])

	def get_pupil_center(self, landmarks, indice, w, h):
		x = landmarks[indice].x * w
		y = landmarks[indice].y * h
		return np.array([y, x])

	def eye_width(self, landmarks, indices, w, h):
		x1, y1, x2, y2 = self.get_bbox(landmarks, indices, w, h, margin=0)
		return np.abs(x2-x1)

	def process_frame(self, frame):
		h, w, _ = frame.shape
		# rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		results = self.face_mesh.process(frame)

		if not results.multi_face_landmarks:
			return Infos(None,None,None,None,None,None,None,None,None)

		lm = results.multi_face_landmarks[0].landmark

		pitch, yaw, roll = self.get_head_pose(lm, w, h)

		left_eye_pos = self.get_left_eye_center(lm, w, h)
		right_eye_pos = self.get_right_eye_center(lm, w, h)
		left_pupil_pos = self.get_pupil_center(lm, self.LEFT_PUPIL, w, h)
		right_pupil_pos = self.get_pupil_center(lm, self.RIGHT_PUPIL, w, h)

		size = np.mean([self.eye_width(lm, self.LEFT_EYE, w, h), self.eye_width(lm, self.RIGHT_EYE, w, h)])
		x_size = size
		y_size = size

		left_eye_pos[0] = left_eye_pos[0] - 0.1*y_size
		right_eye_pos[0] = right_eye_pos[0] - 0.1*y_size

		self.left_pupil_buffer.append(left_pupil_pos)
		self.right_pupil_buffer.append(right_pupil_pos)
		if len(self.left_pupil_buffer) > self.frame_average:
			self.left_pupil_buffer.pop(0)
		if len(self.right_pupil_buffer) > self.frame_average:
			self.right_pupil_buffer.pop(0)

		self.left_eye_buffer.append(left_eye_pos)
		self.right_eye_buffer.append(right_eye_pos)
		if len(self.left_eye_buffer) > self.frame_average:
			self.left_eye_buffer.pop(0)
		if len(self.right_eye_buffer) > self.frame_average:
			self.right_eye_buffer.pop(0)

		self.x_size_buffer.append(x_size)
		self.y_size_buffer.append(y_size)
		if len(self.x_size_buffer) > self.frame_average:
			self.x_size_buffer.pop(0)
		if len(self.y_size_buffer) > self.frame_average:
			self.y_size_buffer.pop(0)

		left_smoothed_pupil = np.mean(self.left_pupil_buffer, axis=0)
		right_smoothed_pupil = np.mean(self.right_pupil_buffer, axis=0)
		left_smoothed_eye = np.mean(self.left_eye_buffer, axis=0)
		right_smoothed_eye = np.mean(self.right_eye_buffer, axis=0)
		x_smoothed_size = np.mean(self.x_size_buffer, axis=0)
		y_smoothed_size = np.mean(self.y_size_buffer, axis=0)

		return Infos(left_smoothed_eye, right_smoothed_eye, left_smoothed_pupil, right_smoothed_pupil, x_smoothed_size, y_smoothed_size, pitch, yaw, roll)

	def get_vectors(self):
		ret, frame = self.cap.read()
		frame  = gaussian_filter(frame, sigma=2, radius=8)
		infos = self.process_frame(frame)
		if infos.eye_left is None:
			return None, None

		if infos.pitch<0:
			infos.pitch = -(180+infos.pitch)
		else:
			infos.pitch = 180-infos.pitch
		# si positif on doit descendre si négatif on doit monter
		# print(0.05*infos.eye_left[0]*(infos.pitch/90))
		# if infos.pitch>0:
		# 	infos.eye_left[0] = infos.eye_left[0] - 0.5*infos.y_size*(infos.pitch/90)
		# 	infos.eye_right[0] = infos.eye_right[0] - 0.5*infos.y_size*(infos.pitch/90)
		# else:
		# 	infos.eye_left[0] = infos.eye_left[0] + 0.5*infos.y_size*(infos.pitch/90)
		# 	infos.eye_right[0] = infos.eye_right[0] + 0.5*infos.y_size*(infos.pitch/90)

		if infos.yaw>0:
			infos.eye_left[1] = infos.eye_left[1] - 0.5*infos.x_size*(infos.yaw/90)
			infos.eye_right[1] = infos.eye_right[1] - 0.5*infos.x_size*(infos.yaw/90)
		else:
			infos.eye_left[1] = infos.eye_left[1] + 0.5*infos.x_size*(infos.yaw/90)
			infos.eye_right[1] = infos.eye_right[1] + 0.5*infos.x_size*(infos.yaw/90)

		dydx_left = 2*(infos.eye_left-infos.pupil_left)/np.array([infos.y_size, infos.x_size])
		dydx_right = 2*(infos.eye_right-infos.pupil_right)/np.array([infos.y_size, infos.x_size])

		left_y, left_x = dydx_left
		right_y, right_x = dydx_right

		angle_left_x = self.compute_angle( np.clip(left_x, -1, 1) )
		angle_left_y = self.compute_angle( np.clip(left_y, -1, 1) )
		angle_right_x = self.compute_angle( np.clip(right_x, -1, 1) )
		angle_right_y = self.compute_angle( np.clip(right_y, -1, 1) )
		left_vector = LineOfSight(infos.eye_left[-1], infos.eye_left[0], angle_left_x, angle_left_y)
		right_vector = LineOfSight(infos.eye_right[-1], infos.eye_right[0], angle_right_x, angle_right_y)
		return left_vector, right_vector

	def compute_angle(self, x):
		angle = np.degrees(np.arctan(x))
		return angle

	def cleanup(self):
		self.cap.release()
		cv2.destroyAllWindows()