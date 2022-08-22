# Importing all the required libraries
import cv2
import mediapipe as mp
from math import hypot
import screen_brightness_control as sbc
import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

#get the video input from our computer’s primary camera.
cap = cv2.VideoCapture(0)

#mediapipe hand module to detect the hands from the video input we got from our primary camera.
mpHands = mp.solutions.hands
hands = mpHands.Hands()

#draw the connections and landmarks on the detected hand
mpDraw = mp.solutions.drawing_utils

# Accessing the speaker using pycaw
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Finding the volume range between the minimum and maximum volume
volMin,volMax = volume.GetVolumeRange()[:2]

# Capturing an image from our camera and converting it to an RGB image
while True:
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results= hands.process(imgRGB)

    # Checking whether we have multiple hands in our input
    lmList = []
    if results.multi_hand_landmarks:
        # Creating a for loop to manipulate each hand
        for handlandmark in results.multi_hand_landmarks:
            for id, lm in enumerate(handlandmark.landmark):
                h, w, _ = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
            mpDraw.draw_landmarks(img, handlandmark, mpHands.HAND_CONNECTIONS)

    if lmList != []:
        # Specifying the points of the thumb,index finger and small finger we will use
        # 4 is the points number and 1,2 are x and y co-ordinate respectively.
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        x3, y3 = lmList[20][1], lmList[20][2]
        # Drawing a circle between the tip of the thumb and the tip of the index finger
        cv2.circle(img, (x1, y1), 4, (0, 0, 0), cv2.FILLED)
        cv2.circle(img, (x2, y2), 4, (0, 0, 0), cv2.FILLED)
        cv2.circle(img, (x3, y3), 4, (0, 0, 0), cv2.FILLED)
        # Drawing lines between points 4 and 8,4 and 20
        # (255,0,0) is color of the line and 3 is thickness
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)
        cv2.line(img, (x1, y1), (x3, y3), (255, 0, 0), 3)

        # Finding the distance between points using the distance formula
        length = hypot(x2 - x1, y2 - y1)
        distance = hypot(x3-x1,y3-y1)

        bright = np.interp(length, [15, 220], [0, 100])
        sbc.set_brightness(int(bright))
        print(bright)

        # Hand range 15 - 220
        # Brightness range 0 - 100

        # Converting the hand range to the volume range
        vol = np.interp(distance, [15, 220], [volMin, volMax])
        volume.SetMasterVolumeLevel(vol, None)
        print(vol)
        # Hand range 15-220, Volume range -63.5 -0.0

    # Displaying the video output
    cv2.imshow('Image', img)

    #  terminate the program when the user presses the q key.
    if cv2.waitKey(1) & 0xff == ord('q'):
        break