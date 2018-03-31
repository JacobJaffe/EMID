import numpy as np
import cv2
from transform import four_point_transform

# global state of last found corners
Marker_Top_Left = []
Marker_Top_Right = []
Marker_Bot_Left = []
Marker_Bot_Right = []

# shitty code to ensure all have been found
a = False
b = False
c = False
d = False

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
        frame_blank = np.zeros((h, w,3), np.uint8)

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

        if (a and b and c and d):

            corners = [Marker_Top_Left, Marker_Bot_Left, Marker_Top_Right, Marker_Bot_Right]
            corner_centers = np.array([[-1,-1], [-1,-1], [-1,-1], [-1,-1]])

            index = 0
            for corner in corners:
                x, y = getCornerCenter(corner)

                # draw pink circles on the 4 corners
                cv2.circle(frame, (int(x), int(y)), 5, (255,0,255), -1)

                # add to our np.array for warping
                corner_centers[index] = [x, y]

                # iterate
                index = index + 1

            # warp the image based on these corners:
            warp = four_point_transform(frame, corner_centers)

            # paste warp in the blank frame
            frame_blank[0:0+warp.shape[0], 0:0+warp.shape[1]] = warp

        frame = np.hstack((frame, frame_blank))

        # Display the resulting frame
        cv2.imshow('frame',frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
