import numpy as np
import cv2
from transform import four_point_transform
import imutils


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
        self._cap.set(cv2.CAP_PROP_SETTINGS,1)
        self._cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
        self._cap.set(cv2.CAP_PROP_EXPOSURE, -5)
        print (self._cap.get(cv2.CAP_PROP_EXPOSURE))

        self._dictionary =\
            cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self._corners = [None]*4

        # Top left, bottom left, top right, bottom right
        self._aruco_ids = [0, 4, 5, 9]

    def set_exposure(self, exposure):
        self._cap.set(cv2.CAP_PROP_EXPOSURE, 40)

    def _all_corners_found(self, corners):
        if (len(corners) < 4):
            return False
        for c in corners:
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

            markers = [None] * 4
            for i in range(len(ids)):
                for j in range(4):
                    if (ids[i] == self._aruco_ids[j]):
                        markers[j] = Marker(id, corners[i][0])

            return markers
        return []

    def get_frame_and_warp(self):

        # Get frame
        ret, frame = self._cap.read()

        # resize for efficency (our camera has too high of a resolution!)
        frame = imutils.resize(frame, width=600)

        # get height and width
        h, w = frame.shape[:2]

        # Don't draw the labels onto the warp, because we check that for colors!
        frame_labled = frame.copy()
        corners = self._get_corners(frame_labled)

        if self._all_corners_found(corners):
            self._corners = corners

        warp = None

        if self._all_corners_found(self._corners):
            centers = []
            for c in self._corners:
                [x, y] = c.get_corner_center()

                # draw pink circles on the 4 corners
                cv2.circle(frame_labled, (int(x), int(y)), 5, (255, 0, 255), -1)
                centers.append([x, y])
            centers = np.array(centers)
            warp = four_point_transform(frame, centers)
        return frame_labled, warp

    def close(self):
        self._cap.release()
