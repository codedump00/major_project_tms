
import cv2 as cv
import requests
import asyncio
import json

from rest import Rest
from tasks import LaneDetector
from extractor import Extractors
from tracker import CentroidTracker
from utils import roi, getBoxes, getCap, approxCnt, getBBoxes
from globals import VID_DATA_DIR, TEXT_COLOR, CV_FONT, CV_AA, ROI_AREA
print('using OpenCV {}'.format(cv.__version__))

req = Rest()
cap = getCap('{}/one.mp4'.format(VID_DATA_DIR))
tracker = CentroidTracker()
ex = Extractors(roi(cap.read()[1]))
WIDTH = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
HEIGHT = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
lanes = LaneDetector(HEIGHT, WIDTH)


async def detectVehicles(frame):
    sub = ex.update(frame, "fg")
    contours, _ = cv.findContours(
        sub, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE
    )
    hulls = approxCnt(contours)
    boxes, area = getBoxes(hulls)
    objects = tracker.update(boxes)
    if len(boxes) > 0:
        tracker.density(int(area))
    else:
        tracker.density(area)
    frame = getBBoxes(hulls, objects, frame)
    return frame, sub


async def detectLanes(frame):
    background = ex.update(frame)
    return lanes.update(background)


async def main():
    MAX_COUNTED = 0
    averaged = []
    SKIP = False
    status = False
    averagedLines = False

    while cap.isOpened():
        start = cv.getTickCount()
        _, frame = cap.read()
        detection, ret = await detectVehicles(roi(frame))

        if SKIP:
            for points in averaged:
                try:
                    cv.line(detection, (int(points[0][0]),
                                        int(points[0][1])),
                            (int(points[1][0]),
                             int(points[1][1])), (255, 0, 0), 5)
                except Exception as e:
                    print(e)
        else:
            averagedLines, status = await detectLanes(frame)
            if status:
                averaged = averagedLines
                SKIP = True
                start = False
                averagedLines = False
            elif averagedLines:
                # print(len(averagedLines))
                for points in averagedLines:
                    try:
                        cv.line(detection, (int(points[0][0]),
                                            int(points[0][1])),
                                (int(points[1][0]),
                                int(points[1][1])), (255, 0, 0), 5)
                    except Exception as e:
                        print(e)

        end = cv.getTickCount()
        fps = 'FPS: '+str(int(1/((end - start)/cv.getTickFrequency())))
        cv.putText(detection, fps, (20, 50), CV_FONT,
                   0.8, TEXT_COLOR, 1, CV_AA)
        cv.putText(detection, "Count: {}".format(tracker.count()), (20, 80),
                   CV_FONT, 0.8, TEXT_COLOR, 1, CV_AA)
        cv.putText(detection, "Density:{:.3f}%".format(tracker.density()*100 /
                                                       ROI_AREA), (20, 115),
                   CV_FONT, 0.8, TEXT_COLOR, 1, CV_AA)
        count = tracker.count()
        
        if count > MAX_COUNTED:
            MAX_COUNTED = count

        cv.imshow('frame', detection)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    cv.destroyAllWindows()
    cap.release()

if __name__ == '__main__':
    asyncio.run(main())
    # payload = dict(pos="chyasal", status="medium", density=12, count=123)
    # r = requests.post('http://localhost:3000/traffic/',
    #                   data=payload)
    # # r = requests.get('https://tmsbackend.herokuapp.com/traffic/')
    # print(r.content)
