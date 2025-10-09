import warnings
warnings.filterwarnings("ignore")
from dataclasses import dataclass
import mediapipe as mp
import numpy as np
import cv2

@dataclass
class Positions:
	eye_left: np.ndarray
	eye_right: np.ndarray
	iris_left: np.ndarray
	iris_right: np.ndarray


class EyeTracker:
	def __init__(self, camera_index=0, frame_average=3):
		self.cap = cv2.VideoCapture(camera_index)
		self.frame_average = frame_average
		self.video_writer = None
		self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
		self.positions

		#Buffer pour le lissage
		self.left_buffer = []
		self.right_buffer = []

		# Regions d'intérêts
		self.LEFT_EYE = [33, 133, 160, 159, 158, 144, 153, 154, 155]
		self.RIGHT_EYE = [362, 263, 387, 386, 385, 373, 380, 381, 382]
		self.LEFT_IRIS = [474, 475, 476, 477]
		self.RIGHT_IRIS = [469, 470, 471, 472]

		# MediaPipe Face Mesh
		self.face_mesh = mp.solutions.face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

	def get_bbox(self, landmarks, indices, w, h, margin=3):
		xs = [landmarks[i].x * w for i in indices]
		ys = [landmarks[i].y * h for i in indices]
		xmin, xmax = int(min(xs)) - margin, int(max(xs)) + margin
		ymin, ymax = int(min(ys)) - margin, int(max(ys)) + margin
		return max(0, xmin), max(0, ymin), min(w, xmax), min(h, ymax)

	def get_eye_center(self, landmarks, indices, w, h):
		x1, y1, x2, y2 = self.get_bbox(landmarks, indices, w, h, margin=5)
		return np.array([y1 + (y2 - y1) / 2, x1 + (x2 - x1) / 2])

	def get_iris_center(self, landmarks, indices, w, h):
		x1, y1, x2, y2 = self.get_bbox(landmarks, indices, w, h, margin=3)
		return np.array([(y1 + y2) / 2, (x1 + x2) / 2])

	def process_frame(self, frame):
		h, w, _ = frame.shape
		# rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		results = self.face_mesh.process(frame)

		if not results.multi_face_landmarks:
			return frame

		lm = results.multi_face_landmarks[0].landmark

		left_eye_pos = self.get_eye_center(lm, self.LEFT_EYE, w, h)
		right_eye_pos = self.get_eye_center(lm, self.RIGHT_EYE, w, h)
		left_iris_pos = self.get_iris_center(lm, self.LEFT_IRIS, w, h)
		right_iris_pos = self.get_iris_center(lm, self.RIGHT_IRIS, w, h)

		self.left_buffer.append(left_iris_pos)
		self.right_buffer.append(right_iris_pos)
		if len(self.left_buffer) > self.frame_average:
			self.left_buffer.pop(0)
		if len(self.right_buffer) > self.frame_average:
			self.right_buffer.pop(0)

		left_smoothed_iris = np.mean(self.left_buffer, axis=0)
		right_smoothed_iris = np.mean(self.right_buffer, axis=0)
		return Positions(left_eye_pos, right_eye_pos, left_smoothed_iris, right_smoothed_iris)

	# --- Boucle principale ---
	def run(self):
		while True:
			ret, frame = self.cap.read()
			if not ret:
				break

			self.positions = self.process_frame(frame)

			if cv2.waitKey(1) & 0xFF == ord('q'):
				break

		self.cleanup()

	def cleanup(self):
		self.cap.release()
		if self.video_writer:
			self.video_writer.release()
		cv2.destroyAllWindows()


if __name__ == "__main__":
	tracker = EyeTracker(camera_index=0, frame_average=3)
	tracker.run()