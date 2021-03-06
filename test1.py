__author__ = 'will'
#!/usr/bin/env python

'''
This sample demonstrates Canny edge detection.

Usage:
  edge.py [<video source>]

  Trackbars control edge thresholds.

'''

import cv2
import numpy as np

if __name__ == '__main__':

    def nothing(*arg):
        pass

    cap = None
    try:
        cap = cv2.VideoCapture(0)
    except:
        print "could not open camera!"

    cv2.namedWindow('edge')
    cv2.createTrackbar('thrs1', 'edge', 2000, 5000, nothing)
    cv2.createTrackbar('thrs2', 'edge', 4000, 5000, nothing)

    while True:
        flag, img = cap.read()
        h, w = img.shape[:2]

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thrs1 = cv2.getTrackbarPos('thrs1', 'edge')
        thrs2 = cv2.getTrackbarPos('thrs2', 'edge')
        edge = cv2.Canny(gray, thrs1, thrs2, apertureSize=5)
        vis = img.copy()
        vis /= 2
        vis[edge != 0] = (0, 255, 0)
        cv2.imshow('edge', vis)

        vis2 = np.zeros((h, w), np.uint8)
        vis2[edge != 0] = 255

        _, contours0, hierarchy = cv2.findContours(vis2.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = [cv2.approxPolyDP(cnt, 3, True) for cnt in contours0]

        selected = []



        vis3 = np.zeros((h, w), np.uint8)
        #**[Next, Previous, First_Child, Parent]**

        lastkids = []
        for i, h in enumerate(hierarchy[0]):
            if h[0] == -1 and h[1] == -1 and h[2] == -1:
                lastkids.append(i)

        chains = []

        for kidId in lastkids:
            n = kidId
            chain = [contours[kidId]]
            while hierarchy[0][n][0] == -1 and hierarchy[0][n][1] == -1 and hierarchy[0][n][3] != -1:
                n = hierarchy[0][n][3]
                chain.append(contours[n])

            if len(chain) > 2:
                chains.append(chain)


        ########### mostra quadrados
        try:
            contours = [chains[0][-1]]

            for chain in chains[1:]:
                contours.append(chain[-1])

            cv2.drawContours(vis, contours, -1, (255, 0, 0), 2, cv2.LINE_AA)
        except:
            pass
        #######################

        for candidate in chains:
            for square in candidate:
                try:
                    M = cv2.moments(square)
                    #print M
                    cx = int(M['m10']/M['m00'])
                    cy = int(M['m01']/M['m00'])
                    cv2.circle(vis, (cx, cy), 5, (255, 0, 255), 5)
                except Exception, e:
                    pass
                    print e


        cv2.imshow('edge', vis)

        ch = cv2.waitKey(5) & 0xFF
        if ch == 27:
            break
    cv2.destroyAllWindows()