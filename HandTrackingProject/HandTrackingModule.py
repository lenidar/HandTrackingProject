import cv2
import time
import mediapipe as mp
import math
# https://stackoverflow.com/questions/71759248/importerror-cannot-import-name-builder-from-google-protobuf-internal
# https://github.com/singhania0601/Gesture_Volume_Control/blob/main/Hand_Tracking_Module.py

class handDetector():
    def __init__(self, mode=False, maxHands=2,modelC=1, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.modelC = modelC
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,self.modelC, self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.result = self.hands.process(imgRGB)
        # print(result.multi_hand_landmarks)

        if self.result.multi_hand_landmarks:
            for handLand in self.result.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLand, self.mpHands.HAND_CONNECTIONS)

        return img

    def findPosition(self, img, handNo=0, draw=True):
        xList = []
        yList = []
        bbox=[]
        self.PosList = []
        if self.result.multi_hand_landmarks:
            myHand = self.result.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                xList.append(cx)
                yList.append(cy)
                self.PosList.append([id, cx, cy])

                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 255, 255), cv2.FILLED)
            xmin,xmax = min(xList), max(xList)
            ymin, ymax = min(yList), max(yList)
            bbox = xmin,ymin,xmax,ymax
            if draw:
                cv2.rectangle(img,(bbox[0]-20,bbox[1]-20),(bbox[2]+20,bbox[3]+20),(200,162,200),2)

        return self.PosList,bbox

    def fingerUp(self):
        fingers = []
        if self.PosList[self.tipIds[0]][1] > self.PosList[self.tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)
        for id in range(1, 5):

            if self.PosList[self.tipIds[id]][2] < self.PosList[self.tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers
    def findDis(self,p1,p2,img,draw = True):
        x1, y1 = self.PosList[p1][1], self.PosList[p1][2]
        x2, y2 = self.PosList[p2][1], self.PosList[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        if draw:
            cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
        length = math.hypot(x2 - x1, y2 - y1)
        return length,img,[x1,y1,x2,y2,cx,cy]


def main():
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)
    detector = handDetector()

    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        PosList = detector.findPosition(img)

        if len(PosList) != 0:
            print(PosList[4])

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_DUPLEX, 3, (255, 0, 0), 3)

        cv2.imshow("Webcam", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()