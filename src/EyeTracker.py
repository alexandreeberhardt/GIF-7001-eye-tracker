import mediapipe as mp
import numpy as np
import cv2
import time
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


def centroid(pixels):
    return np.mean(pixels, axis=0).astype(int)


class EyeTracker:
    # Landmarks de mediapipe
    RIGHT_IRIS_LANDMARKS = [473, 474, 475, 476, 477]
    LEFT_IRIS_LANDMARKS = [468, 469, 470, 471, 472]

    LEFT_EYE_LANDMARKS = [33, 133, 160, 159, 158, 144, 153, 154, 155]
    RIGHT_EYE_LANDMARKS = [362, 263, 387, 386, 385, 373, 380, 381, 382]

    def __init__(self, cam_index=0):
        """
        Classe encapsulant la capture d'images + détection des yeux / pupilles.
        Gère mediapipe et la capture avec openCV.
        :param cam_index: int, index où trouver la caméra. Par défaut, c'est 0.
        """
        self._cam_index = cam_index
        self.capture = cv2.VideoCapture(cam_index)
        self._cam_h = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self._cam_w = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.cam_fps = self.capture.get(cv2.CAP_PROP_FPS)
        self._face_mesh = mp.solutions.face_mesh

    def start_tracking(self, stop_condition: callable, record: str = None, callback: callable = None):
        """
        Méthode permettant de commencer la détection des yeux. Utilise mediapipe pour détecter les yeux et openCV pour
        la capture d'images.
        :param stop_condition: callable, fonction permettant d'arrêter la capture, par exemple un timer.
        :param record: str, chaîne de caractère spécifiant où enregistrer la capture.
        Par défaut None, pas d'enregistrement.
        :param callback: callable, fonction à appeler à chaque capture et détection des yeux. Doit minimalement
        accepter les points associés à l'oeil droit, ceux de l'iris droit, ceux de l'oeil gauche, ceux de l'iri gauche
        et la capture courante.
        :return: Rien.
        """
        # TODO: Option pour enregistrer la capture? Utiliser record (nom/path)
        normalisation = np.array([self._cam_w, self._cam_h])
        ARs = []
        with self._face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True) as face_mesh:
            while not stop_condition() and self.capture.isOpened():
                success, frame = self.capture.read()
                if not success:
                    break
                frame.flags.writeable = False
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_landmarks = face_mesh.process(frame_rgb).multi_face_landmarks
                frame.flags.writeable = True
                if not face_landmarks:
                    print("No landmarks detected")
                else:
                    landmarks = face_landmarks[0].landmark
                    left_iris_points = self.__left_iris_points(landmarks) / normalisation
                    left_eye_points = self.__left_eye_points(landmarks) / normalisation

                    right_iris_points = self.__right_iris_points(landmarks) / normalisation
                    right_eye_points = self.__right_eye_points(landmarks) / normalisation
                    left_eye_AR = self.__left_eye_AR(landmarks)
                    right_eye_AR = self.__right_eye_AR(landmarks)
                    ARs.append([left_eye_AR, right_eye_AR])

                    if callback:
                        # Permet de faire des trucs en temps réel, par exemple afficher un graphique
                        # de l'aspect ratio. Devrait pouvoir spécifier ce qu'on veut avec une liste de str.
                        # Par exemple ["re_pts", "ri_pts"] pour qu'on ne donne que les points de l'oeil droit
                        # (right eye points -> re_pts) et les points de l'iris de l'oeil droit (ri_pts)
                        # Peut-être plusieurs callbacks? Ou un callback qui fait plusieurs callbacks à l'interne?
                        callback(right_eye_points, right_iris_points, left_eye_points, left_iris_points, frame)

        # Idéalement, ne devrait rien retourner, mais pour des tests, on peut retourner quelque chose.
        # Ou devrait-on retourner quelque chose?
        return np.array(ARs)

    def __left_eye_AR(self, landmarks):
        """
        Méthode privée permettant de calculer l'aspect ratio de l'oeil gauche.
        :param landmarks: liste des landmarks du visage courant.
        :return: l'aspect ratio de l'oeil gauche.
        """
        # top left, bottom left, top right, bottom right, left, right
        LEFT_EYE_INDICES_ASPECT_RATIO = [160, 144, 158, 153, 33, 133]
        positions = np.array([[landmarks[i].x, landmarks[i].y] for i in LEFT_EYE_INDICES_ASPECT_RATIO])
        aspect_ratio_num_1 = np.linalg.norm(positions[0] - positions[1])
        aspect_ratio_num_1 *= aspect_ratio_num_1
        aspect_ratio_num_2 = np.linalg.norm(positions[2] - positions[3])
        aspect_ratio_num_2 *= aspect_ratio_num_2
        aspect_ratio_denom = np.linalg.norm(positions[4] - positions[5])
        aspect_ratio_denom *= 2 * aspect_ratio_denom
        return (aspect_ratio_num_1 + aspect_ratio_num_2) / aspect_ratio_denom

    def __right_eye_AR(self, landmarks):
        """
        Méthode privée permettant de calculer l'aspect ratio de l'oeil droit.
        :param landmarks: liste des landmarks du visage courant.
        :return: l'aspect ratio de l'oeil droit.
        """
        # TODO merge avec l'autre oeil, permettre de spécifier quel oeil ou les deux.
        # top left, bottom left, top right, bottom right, left, right
        RIGHT_EYE_INDICES_ASPECT_RATIO = [385, 380, 387, 373, 362, 263]
        positions = np.array([[landmarks[i].x, landmarks[i].y] for i in RIGHT_EYE_INDICES_ASPECT_RATIO])
        aspect_ratio_num_1 = np.linalg.norm(positions[0] - positions[1])
        aspect_ratio_num_1 *= aspect_ratio_num_1
        aspect_ratio_num_2 = np.linalg.norm(positions[2] - positions[3])
        aspect_ratio_num_2 *= aspect_ratio_num_2
        aspect_ratio_denom = np.linalg.norm(positions[4] - positions[5])
        aspect_ratio_denom *= 2 * aspect_ratio_denom
        return (aspect_ratio_num_1 + aspect_ratio_num_2) / aspect_ratio_denom

    def __left_iris_points(self, landmarks):
        """
        Méthode privée permettant de calculer les points associés à l'iris de l'oeil gauche.
        :param landmarks: liste des landmarks du visage courant.
        :return: les points (x, y) de l'iris de l'oeil gauche.
        """
        indices = self.LEFT_IRIS_LANDMARKS
        return np.array([[landmarks[i].x * self._cam_w, landmarks[i].y * self._cam_h] for i in indices])

    def __left_eye_points(self, landmarks):
        """
        Méthode privée permettant de calculer les points associés à l'oeil gauche.
        :param landmarks: liste de landmarks du visage courant.
        :return: les points (x, y) de l'oeil gauche.
        """
        indices = self.LEFT_EYE_LANDMARKS
        return np.array([[landmarks[i].x * self._cam_w, landmarks[i].y * self._cam_h] for i in indices])

    def __right_iris_points(self, landmarks):
        """
        Méthode privée permettant de calculer les points associés à l'iris de l'oeil droit.
        :param landmarks: liste de landmarks du visage courant.
        :return: les points (x, y) de l'iris de l'oeil droit.
        """
        # TODO: merge avec l'autre iris. Pouvoir spécifier quel iris ou les deux.
        indices = self.RIGHT_IRIS_LANDMARKS
        return np.array([[landmarks[i].x * self._cam_w, landmarks[i].y * self._cam_h] for i in indices])

    def __right_eye_points(self, landmarks):
        """
        Méthode privée permettant de calculer les points associés à l'oeil droit.
        :param landmarks: liste de landmarks du visage courant.
        :return: les points (x, y) de l'oeil droit.
        """
        # TODO: merge avec l'autre oeil. Pouvoir spécifier quel oeil ou les deux.
        indices = self.RIGHT_EYE_LANDMARKS
        return np.array([[landmarks[i].x * self._cam_w, landmarks[i].y * self._cam_h] for i in indices])

    def close_capture(self):
        """
        Méthode permettant de libérer la caméra utilisée pour la capture.
        :return: rien.
        """
        if self.capture.isOpened():
            self.capture.release()

    def __del__(self):
        """
        Destructeur de la classe courante. Pour l'instant, on ne fait que s'assurer que la caméra utilisée soit
        libérée.
        :return: rien.
        """
        self.close_capture()


if __name__ == '__main__':

    def condition(max_time=15, t=[]):
        # Timer pour condition d'arrêt. Doit stocker une valeur initiale, d'où une liste en paramètre.
        # Modifier la liste en paramètre la modifie pour tous les appels subséquents. C'est pas idéal, mais je ne
        # sais pas trop comment faire autrement.
        if not t:
            t.append(time.time())
        return (time.time() - t[0]) >= max_time


    et = EyeTracker()
    ARs = et.start_tracking(condition)
    plt.plot(ARs[:, 0], label="AR oeil gauche")
    plt.plot(ARs[:, 1], label="AR oeil droit")
    plt.show()
