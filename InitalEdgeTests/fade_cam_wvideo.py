# Based on CSI Camera by JetsonHacks

import cv2
import numpy as np
import sys
import dlib
import time
from imutils import face_utils
import multiprocessing
from multiprocessing import Process, Queue
import queue

detector = dlib.get_frontal_face_detector()

def detectPresence(boolQ, camQ):
    while True:
        img = camQ.get()
        if img is None:
            break
        ratio = 2
        imSmall = cv2.resize(img, (int(1260/ratio), int(1024/ratio)))
        dets = detector(imSmall )
        if len(dets) > 0:
            boolQ.put(True)
        else:
            boolQ.put(False)
    print("detector daemon killed")

def decodeVideo(vidQ, killQ, lower=30, upper=55):
    cap = cv2.VideoCapture("wave.mp4")
    frameList = []
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            edge = cv2.Canny(frame, lower, upper)
            frameList.append(edge)
        else:
            break
    cap.release()
    count = 0
    maxVal = len(frameList)
    print("Video Loaded")
    print(maxVal)
    while True:
        try:
            temp = killQ.get_nowait()
            if temp is None:
                print("breaking")
                break
        except queue.Empty:
            time.sleep(0.0001)   
        if count < maxVal:
            vidQ.put(frameList[count])
            #print("putting frame: "+str(count))
            count += 1
        else:
            count = 0
    print("video daemon killed")
    


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

def show_camera(sigma=0.33, lower=30, upper=55, mix=0.0, present = False, vidBool = True):
    boolQ = Queue()
    camQ = Queue()
    vidQ = Queue((300))
    killQ = Queue()

    detectP = Process(target=detectPresence, args=(boolQ, camQ))
    detectP.daemon = True
    detectP.start()
    if vidBool:
        vidP = Process(target=decodeVideo, args=(vidQ, killQ))
        vidP.daemon = True
        vidP.start()

    cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=2), cv2.CAP_GSTREAMER)
    if cap.isOpened():
        window_handle = cv2.namedWindow('test', cv2.WINDOW_AUTOSIZE)
        # Window 
        while cv2.getWindowProperty('test',0) >= 0:
            ret_val, img = cap.read()
            img = cv2.flip(img, 1)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            if camQ.empty():
                camQ.put(gray)
            blur = cv2.blur(gray, (5,5))
            edges = cv2.Canny(blur, lower, upper)   
            edges = cv2.dilate(edges, np.ones((3,3)))
            #out = cv2.addWeighted(gray,mix, edges,0.8)
            #cv2.namedWindow('test', cv2.WND_PROP_FULLSCREEN)
            #cv2.setWindowProperty('test', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            if not boolQ.empty():
                present = bool(boolQ.get())
            if present:
                if mix <1.0:
                    mix += 0.02
            else:
                if mix > 0.0:
                     mix -= 0.08
            print(mix)
            try:
                frame = vidQ.get_nowait()
                #a = np.double(edges)
                #b = a * mix
                #edges2 = np.uint8(
                #out1 = cv2.bitwise_or(edges2, frame,0)
                #mix2 = max(1-mix, 0.3) 
                out = cv2.addWeighted(frame, 1-mix, edges, mix, 0)
                cv2.imshow('test', out)
            except queue.Empty:
                cv2.imshow('test', edges*mix)
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
        
        camQ.put(None)
        killQ.put(None)
        cap.release()
        cv2.destroyAllWindows()
        detectP.join()
        if vidBool:
            while True:
                try:
                    trash = vidQ.get_nowait()
                    time.sleep(0.01)
                except queue.Empty:
                    print("done")
                    break
            vidP.join()
    else:
        print('Unable to open camera')


if __name__ == '__main__':
    show_camera()
