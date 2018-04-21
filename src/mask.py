from constants import *

class Mask:
    def __init__(self,  color):
        self.color = color
        self.hsv = HSV[color]
        self.image = None

    def update(self, image):
        color = self.color
        ''' creates a mask over a image for a color '''

        ''' resize the frame, blur it, and convert it to the
            HSV color space'''
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        ''' construct a mask for the color, then perform a series
            of dilations and erosions to remove any small blobs
            left in the mask '''
        mask = cv2.inRange(hsv, self.hsv['lower'], self.hsv['upper'])
        if (color == RED):
            mask = mask | cv2.inRange(hsv, Scalar(170, 70, 50), Scalar(180, 255, 255));

        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=3)
        self.mask = mask

    def get_contours(self):
        ''' Returns balls of a given color determined by mask '''
        return cv2.findContours(self.mask.copy(),
                cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
