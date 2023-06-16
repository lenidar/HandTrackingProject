import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

def loop(w, h):
    print('setting parameters')
    cap = cv2.VideoCapture(0)
    cap.set(3, w)
    cap.set(4, h)
    pTime = 0

    detector = htm.handDetector(detectionCon=0.7)

    print('Starting the loop')
    while True:
        success, img = cap.read()
        img = cv2.flip(img,1)

        # find hand
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=False)

        if len(lmList[0]) > 0:
            #print(lmList[0][4], lmList[0][8])
            # filter based on hand size 

            # find distance between two fingers


            x1, y1 = lmList[0][4][1],lmList[0][4][2]
            x2, y2 = lmList[0][8][1],lmList[0][8][2] 

            cx, cy = (x1 + x2)//2, (y1 + y2)//2

            cv2.circle(img, (x1,y1), 15, (255,0,255), cv2.FILLED)
            cv2.circle(img, (x2,y2), 15, (255,0,255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255,0,255), 3)
            cv2.circle(img, (cx,cy), 15, (255,0,255), cv2.FILLED)

            length = math.hypot(x2 - x1, y2 - y1)
            #print(length)
            setVolume(length)            
        
            volBar = np.interp(length, [50, 300], [400, 150])
            volPer = np.interp(length, [50, 300], [0, 100])

            cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
            cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
            cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                    1, (255, 0, 0), 3)

            if length < 50:
                cv2.circle(img, (cx,cy), 15, (0,255,0), cv2.FILLED)

        cTime = time.time()
        fps = 1/(cTime - pTime)
        pTime = cTime

        cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1,
                    (255,0,0), 3)


        cv2.imshow("Img", img)
        cv2.waitKey(1)

def setVolume(length):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    #print(volume.GetVolumeRange())
    volRange = volume.GetVolumeRange()
    minVol = volRange[0]
    maxVol = volRange[1]
    vol = np.interp(length, [50, 300], [minVol, maxVol])

    volume.SetMasterVolumeLevel(vol, None)

if __name__ == "__main__":
    wCam, hCam = 640, 480
    print('Application is starting')
    loop(wCam, hCam);

