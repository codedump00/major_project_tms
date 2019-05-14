
import os
import numpy as np

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
VID_DATA_DIR = os.path.join(FILE_DIR, 'data', 'video')
IMG_DATA_DIR = os.path.join(FILE_DIR, 'data', 'image')
MIN_LINE_LENGTH = 40  # minimum number of pixels making up a line
MAX_LINE_GAP = 30    # maximum gap in pixels between connectable line segments
THETA = np.pi/180  # angular resolution in radians of the Hough grid
