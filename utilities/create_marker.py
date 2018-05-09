import cv2.aruco as aruco
import numpy as np
import cv2

aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
print(aruco_dict)

# second parameter is id number
# last parameter is total image size
img = aruco.drawMarker(aruco_dict, 2, 700)
cv2.imwrite("test_marker.jpg", img)

cv2.imshow('frame',img)
cv2.waitKey(0)
cv2.destroyAllWindows()