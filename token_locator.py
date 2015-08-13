# !/usr/bin/env python


import cv2
import numpy as np

from itertools import tee, izip
import binascii

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)


def nothing(kargs=[]):
    pass


class QrFinder():
    cap = None
    img = None

    def try_to_decode(self, candidate, source, target):
        epsilon = 0.01 * cv2.arcLength(candidate, True)
        approx = cv2.approxPolyDP(candidate, epsilon, True)

        # makes sure epsilon gives us a square
        while len(approx) > 4:
            epsilon *= 1.01
            approx = cv2.approxPolyDP(candidate, epsilon, True)

        ### draw on screen
        for a, b in pairwise(approx):
            cv2.line(target, tuple(a[0]), tuple(b[0]), (0, 0, 255), 3)
        cv2.line(target, tuple(approx[-1][0]), tuple(approx[0][0]), (0, 0, 255), 3)

        center = sum(approx) / 4
        topleft = None
        topright = None
        bottomleft = None
        bottomright = None

        for i in approx:
            if i[0][0] < center[0][0] and i[0][1] < center[0][1]:
                topleft = i
            elif i[0][0] > center[0][0] and i[0][1] < center[0][1]:
                topright = i
            elif i[0][0] < center[0][0] and i[0][1] > center[0][1]:
                bottomleft = i
            elif i[0][0] > center[0][0] and i[0][1] > center[0][1]:
                bottomright = i

        targetperspective = np.float32([[[0, 0]], [[100, 0]], [[100, 100]], [[0, 100]]])
        source_perspective = np.float32([topleft, topright, bottomright, bottomleft])

        matrix = cv2.getPerspectiveTransform(source_perspective, targetperspective)
        cv2.warpPerspective(source, matrix, (100, 100), self.corrected)
        bits = []
        gridsize = 8
        step = 100/(gridsize+3)
        for y in range(2, gridsize + 2):
            for x in range(2, gridsize + 2):
                #cv2.circle(self.corrected, (step*x, step*y), 1, (255, 0, 0), 2)
                bits.append(self.corrected[step*y][step*x])
        avg = sum(bits)/len(bits)
        #print len(bits), avg
        text = ""
        for pixel in bits:
            text += "1" if pixel < avg else "0"
        data = [text[i:i+8] for i in range(0, len(text), 8)]
        result = ""
        for number in data:
            n = int('0b'+number, 2)
            print binascii.unhexlify('%x' % n)
            print number
        cv2.namedWindow('corrected')
        cv2.imshow('corrected', self.corrected)



    def __init__(self):

        self.cap = None
        self.corrected = np.zeros((100, 100), np.uint8)

        try:
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280);
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 768);
        except:
            print "could not open camera!"

        cv2.namedWindow('edge')
        cv2.createTrackbar('thrs1', 'edge', 2000, 5000, nothing)
        cv2.createTrackbar('thrs2', 'edge', 4000, 5000, nothing)

        while True:
            flag, self.img = self.cap.read()
            h, w = self.img.shape[:2]

            gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
            thrs1 = cv2.getTrackbarPos('thrs1', 'edge')
            thrs2 = cv2.getTrackbarPos('thrs2', 'edge')
            edge = cv2.Canny(gray, thrs1, thrs2, apertureSize=5)
            vis = self.img.copy()
            vis /= 2
            vis[edge != 0] = (0, 255, 0)
            cv2.imshow('edge', vis)

            vis2 = np.zeros((h, w), np.uint8)
            vis2[edge != 0] = 255

            _, contours0, hierarchy = cv2.findContours(vis2.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            contours = [cv2.approxPolyDP(cnt, 3, True) for cnt in contours0]

            selected = []
            # **[Next, Previous, First_Child, Parent]**
            for c, h in zip(contours, hierarchy[0]):
                if h[0] == -1 and h[1] == -1:
                    kid = h[2]
                    if kid != -1:
                        kidh = hierarchy[0][kid]
                        if kidh[0] == -1 and kidh[1] == -1:  ### only checking for nested circles, without brothers
                            selected.append(c)

            cv2.drawContours(vis, selected, -1, (255, 0, 0), 2, cv2.LINE_AA)
            for candidate in selected:
                try:
                    self.try_to_decode(candidate, gray, vis)
                except Exception, e:
                    print e

            cv2.imshow('contours', vis)

            ch = cv2.waitKey(5) & 0xFF
            if ch == 27:
                break
        cv2.destroyAllWindows()


if __name__ == '__main__':
    finder = QrFinder()
