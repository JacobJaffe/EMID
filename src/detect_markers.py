import numpy as np
import cv2
from transform import four_point_transform

# global state of last found corners
Marker_Top_Left = []
Marker_Top_Right = []
Marker_Bot_Left = []
Marker_Bot_Right = []

# so we don't warp untill we find corners
cornersFound = False

# shitty (shidi) code to ensure all have been found
a = False
b = False
c = False
d = False

# global state of last points to use for projection
corner_centers = np.array([[-1,-1], [-1,-1], [-1,-1], [-1,-1]])


def getCornerCenter(corner):
    x = (corner[0][0] + corner[1][0] + corner[2][0] + corner[3][0]) / 4
    y = (corner[0][1] + corner[1][1] + corner[2][1] + corner[3][1]) / 4
    return x, y

if __name__ == "__main__":
    cap = cv2.VideoCapture(1)
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

    while(True):

        # Capture frame-by-frame
        ret, frame = cap.read()
        h, w = frame.shape[:2]
        frame_projection = np.zeros((h, w,3), np.uint8)

        # Our operations on the frame come here
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # detect the markers
        corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray,dictionary)

        if len(corners) > 0:
            cv2.aruco.drawDetectedMarkers(frame,corners,ids)

            # We gotta do this case they are not gaurenteed to be sorted,
            # and we its not worth re ordering both of these arrays
            for i in range(len(ids)):
                marker_id = ids[i][0]
                if (marker_id == 0):
                    Marker_Top_Left = corners[i][0]
                    a = True
                elif (marker_id == 4):
                    Marker_Bot_Left = corners[i][0]
                    b = True
                elif (marker_id == 5):
                    Marker_Top_Right = corners[i][0]
                    c = True
                elif (marker_id == 9):
                    Marker_Bot_Right = corners[i][0]
                    d = True

        # recompute the corners if possible
        if (a and b and c and d):
            cornersFound = True
            corners = [Marker_Top_Left, Marker_Bot_Left, Marker_Top_Right, Marker_Bot_Right]

            index = 0
            for corner in corners:
                x, y = getCornerCenter(corner)

                # draw pink circles on the 4 corners
                cv2.circle(frame, (int(x), int(y)), 5, (25 5,0,255), -1)

                # add to our np.array for warping
                corner_centers[index] = [x, y]

                # iterate
                index = index + 1

        # If u want them in the same window
        # frame_side_by_side = np.hstack((frame, frame_projection))

        if (cornersFound):
            # warp the image based on last found corners:
            warp = four_point_transform(frame, corner_centers)

            # paste warp in the blank frame
            frame_projection[0:0+warp.shape[0], 0:0+warp.shape[1]] = warp

        # Display the resulting frame
        cv2.imshow('Camera',frame)
        cv2.imshow('Projection', frame_projection)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
