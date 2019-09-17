# Based on CSI Camera by JetsonHacks

import cv2
import numpy as np
import sys
import dlib
import time
from imutils import face_utils
import multiprocessing
from multiprocessing import Process, Queue

detector = dlib.get_frontal_face_detector()

def detectPresence(q, q1):
    while True:
        img = q1.get()
        if img is None:
            break
        ratio = 2
        imSmall = cv2.resize(img, (int(1260/ratio), int(1024/ratio)))
        dets = detector(imSmall )
        if len(dets) > 0:
            q.put(True)
        else:
            q.put(False)
    print("daemon killed")

# gstreamer_pipeline returns a GStreamer pipeline for capturing from the CSI camera
# Defaults to 1280x720 @ 60fps 
# Flip the image by setting the flip_method (most common values: 0 and 2)
# display_width and display_height determine the size of the window on the screen

def gstreamer_pipeline (capture_width=1024, capture_height=1260, display_width=1260, display_height=1024, framerate=60, flip_method=2) :   
    return ('nvarguscamerasrc ! ' 
    'video/x-raw(memory:NVMM), '
    'width=(int)%d, height=(int)%d, '
    'format=(string)NV12, framerate=(fraction)%d/1 ! '
    'nvvidconv flip-method=%d ! '
    'video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! '
    'videoconvert ! '
    'video/x-raw, format=(string)BGR ! appsink'  % (capture_width,capture_height,framerate,flip_method,display_width,display_height))

def show_camera(sigma=0.33, lower=30, upper=55, mix=0.0, present = False):
    q = Queue()
    q1 = Queue()

    p = Process(target=detectPresence, args=(q, q1))
    p.daemon = True
    p.start()

    cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=2), cv2.CAP_GSTREAMER)
    cap1 = cv2.VideoCapture("wave.mp4")
    if cap.isOpened():
        window_handle = cv2.namedWindow('test', cv2.WINDOW_AUTOSIZE)
        # Window 
        while cv2.getWindowProperty('test',0) >= 0:
            ret_val, img = cap.read()
            img = cv2.flip(img, 1)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            if q1.empty():
                q1.put(gray)
            blur = cv2.blur(gray, (5,5))
            edges = cv2.Canny(blur, lower, upper)   
            edges = cv2.dilate(edges, np.ones((3,3)))
            #out = cv2.addWeighted(gray,mix, edges,0.8)
            #cv2.namedWindow('test', cv2.WND_PROP_FULLSCREEN)
            #cv2.setWindowProperty('test', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            if not q.empty():
                present = bool(q.get())
            if present:
                if mix < 0.002:
                    mix = max(min(mix + 0.0001, 0.002), 0)
                elif mix >= 0.002 and mix <=1.0:
                    mix = max(min(mix * 1.3, 1.0), 0)
            else:
                if mix > 0.002:
                     mix = max(min(mix*(0.6), 1.0), 0)
                elif mix > 0: 
                    mix = max(min(mix - 0.0003, 0.002), 0)
            #print(mix)
            if cap1.isOpened():
                ret, frame = cap1.read()
                
                if ret:
                    #frame = cv2.resize(frame, (1260, 1024))
                    #vedges = cv2.Canny(frame, lower, upper)
                    a = np.double(edges)
                    b = a * mix
                    edges2 = np.uint8(b)
                    edges2 = cv2.cvtColor(edges2, cv2.COLOR_GRAY2RGB)
                    out = cv2.bitwise_or(edges2, frame,0)
                    cv2.imshow('test', out)
                else:
                    cap1.set(cv2.CAP_PROP_POS_FRAMES, 0)
            

            #cv2.imshow('test', edges*mix)

	    # This also acts as 
            keyCode = cv2.waitKey(30) & 0xff
            # Stop the program on the ESC key
            if keyCode == 27:
               break
            elif keyCode == 97:
               lower = lower - 5
               print(lower)
            elif keyCode == 113:
               lower = lower + 5
               print(lower)
            elif keyCode == 115:
               upper = upper - 5
               print(upper)
            elif keyCode == 119:
               upper = upper + 5
               print(upper)
        
        q1.put(None)
        cap.release()
        #cap1.release
        cv2.destroyAllWindows()
        p.join()
    else:
        print('Unable to open camera')


if __name__ == '__main__':
    show_camera()
