import numpy as np
import cv2
from transform import four_point_transform


class Marker:
    def __init__(self, id, corners):
        self.id = id
        self._corners = corners

    def get_corner_center(self):
        corner = self._corners
        x = (corner[0][0] + corner[1][0] + corner[2][0] + corner[3][0]) / 4
        y = (corner[0][1] + corner[1][1] + corner[2][1] + corner[3][1]) / 4
        return [x, y]


class Camera:
    def __init__(self, camera_id):
        self._cap = cv2.VideoCapture(camera_id)
        self._dictionary =\
            cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self._corners = [None]*4

        # Top left, bottom left, top right, bottom right
        self.aruco_ids = [0, 4, 5, 9]

    def _all_corners_found(self):
        for c in self._corners:
            if c is None:
                return False
        return True

    def _get_corners(self, frame):
        # grayscale the frame
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # detect the markers
        corners, ids, rejectedImgPoints =\
            cv2.aruco.detectMarkers(gray, self._dictionary)

        if len(corners) != 0:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)
            markers = [Marker(id, corners[id][0])
                       for id in sorted(ids) if id in self.aruco_ids]
            return markers
        return []

    def get_frame_and_warp(self):

        # Get frame
        ret, frame = self._cap.read()
        h, w = frame.shape[:2]

        # Create zero matrix to load projection

        corners = self._get_corners(frame)
        if len(corners) == 4:
            self._corners = corners
        warp = None
        if self._all_corners_found():
            centers = []
            for c in self._corners:
                [x, y] = c.get_corner_center()

                # draw pink circles on the 4 corners
                cv2.circle(frame, (int(x), int(y)), 5, (255, 0, 255), -1)
                centers.append([x, y])
            centers = np.array(centers)
            warp = four_point_transform(frame, centers)
        return frame, warp

    def close(self):
        self._cap.release()
