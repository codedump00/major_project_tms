
import os
import cv2
import numpy as np


def save(frame, dir, name="untitled"):
    '''
        Saves specified frame into a directory.
        Parameters
        ----------
            @params: frame: Numpy Array
            @params: dir  : String
            @params: name : String
    '''
    if dir is not None:
        return cv2.imsave(os.path.join(dir, name), frame)
    return cv2.imsave(name, frame)


def getCapture(device=0):
    '''
        Gets media capture from a device.
        Parameters
        ----------
            @params: device: Integer
            @returns: cap: Device capture
    '''
    cap = cv2.VideoCapture(device)
    if cap.isOpened():
        return cap


def getBoundingBoxes(contour, frame, color=(0, 255, 0)):
    '''
        Draws rectangles around contours.
        Parameters
        ----------
            @param: contour: List
            @param: frame  : Numpy Array
            @param: color  : RGB tuple
            @return frame: List
                Numpy array of an image.
    '''
    for c in contour:
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        # rect = cv2.minAreaRect(c)
        # box = cv2.boxPoints(rect)
        # box = np.int0(box)
        # frame = cv2.drawContours(frame, [box], 0, (0, 0, 255), 2)
    return frame


def smoothContours(contours, thresh=0.3):
    '''
        Combines multiple bounding boxes into a single one.
        Parameters
        ----------
            @param: contour: List
            @param: thresh: Int
            @return contour: List
                Array of smoothed contours.
    '''
    if contours is None:
        return
    weights = []
    try:
        contours, weights = cv2.groupRectangles(contours, thresh)
    except Exception as e:
        pass
    # if width of the contour is very high than it's
    # height then it is probably an error.
    contours = list(x for x in contours if cv2.boundingRect(x)
                    [2]/3 <= cv2.boundingRect(x)[3])
    contours = list(x for x in contours if cv2.contourArea(x) > 50)
    return contours


def findHull(contour):
    '''
        A function to calculate convex hull of contours.
        Parameters
        ----------
            @param: contour: List
            @return hull: List
                Array of convex hulls.
    '''
    return list(cv2.convexHull(x) for x in contour)


def approximateContours(contours):
    smooth = smoothContours(contours)
    return findHull(smooth)


def getBoxes(contour):
    '''
        Gets bounding boxes from contours.
        Parameters
        ----------
            @param: contour: List
            @returns: boxes: List
    '''
    if contour is None:
        return []
    boxes = []
    for c in contour:
        x, y, w, h = cv2.boundingRect(c)
        boxes.append((x, y, x+w, y+h))
    return boxes  # list(cv2.boundingRect(c) for c in contour)


def roi(frame):
    '''
        Extracts a region of interest from given frame.
        Parameters
        ----------
            @param frame: List
                Numpy array of an image.
            @return frame: List
                Numpy array of an image.
    '''
    imshape = frame.shape
    vertices = np.array([[(0, imshape[0]/1.5),
                          (450, 320),
                          (800, 320),
                          (imshape[1], imshape[0]/1.1),
                          (imshape[1], imshape[0]),
                          (0, imshape[0])]
                         ], dtype=np.int32)
    mask = np.zeros(frame.shape, dtype=np.uint8)
    cv2.fillPoly(mask, vertices, (255, 255, 255))
    return cv2.bitwise_and(mask, frame)


def compare(array):
    '''
        Compares each and every element of an array with other.
        Parameters
        ----------
            @params: array: List
    '''
    for i in range(len(array)):
        for j in range(i + 1, len(array)):
            print(array[i], array[j], '\n')


def averageLines(lines):
    '''
        Averages over a list of line points.
        Parameters
        ----------
            @params: lines: List of lines
    '''
    for hlines in lines:
        for i in range(len(hlines)):
            for j in range(i+1, len(hlines)):
                slopeI = hlines[i][0][1]-hlines[i][0][0] / \
                    hlines[i][1][1]-hlines[i][1][0]

                slopeII = hlines[j][0][1]-hlines[j][0][0] / \
                    hlines[j][1][1]-hlines[j][1][0]
                print(hlines[j][0][1]-hlines[i][0][1])
