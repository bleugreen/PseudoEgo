# MIT License
# Copyright (c) 2019 JetsonHacks
# See license
# Using a CSI camera (such as the Raspberry Pi Version 2) connected to a 
# NVIDIA Jetson Nano Developer Kit using OpenCV
# Drivers for the camera and OpenCV are included in the base image

import cv2
import numpy as np
import sys
import dlib
import time
from imutils import face_utils


predictor_path = "shape_predictor_68_face_landmarks.dat"

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(predictor_path)
detector = dlib.get_frontal_face_detector()
color_green = (0,255,0)
line_width = 3


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

def show_camera(sigma=0.33, lower=30, upper=55, mix=0.25):
    # To flip the image, modify the flip_method parameter (0 and 2 are the most common)
    cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=2), cv2.CAP_GSTREAMER)
    if cap.isOpened():
        window_handle = cv2.namedWindow('CSI Camera', cv2.WINDOW_AUTOSIZE)
        # Window 
        count = 0
        timeV = 0
        bound = [0,0,0,0]
        bounds = [bound]
        shapes = []
        while cv2.getWindowProperty('CSI Camera',0) >= 0:
            ret_val, img = cap.read()
            img = cv2.flip(img, 1)
            #rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            blur = cv2.blur(gray, (5,5))
            edges = cv2.Canny(blur, lower, upper)
            #out = gray
            count += 1
            if count%10==0:
                ratio = 3
                imSmall = cv2.resize(gray, (int(1260/ratio), int(1024/ratio)))
                dets = detector(imSmall)
                rect = False
                bounds *= 0
                for det in dets:
                    rect = True
                    bounds.append([det.left()*ratio, det.top()*ratio, det.right()*ratio, det.bottom()*ratio])
                
                    #cv2.rectangle(edges,(bound[0],bound[1]),(bound[2],bound[3]), (255), 3, 0)
            shapes *= 0
            for bound in bounds:    
                #cv2.rectangle(edges, (int(bound[0]-40), int(bound[1]-40)), (int(bound[2]+40),int(bound[3]+40)), 0, -1, 8, 0)
                shape = predictor(img, dlib.rectangle(left=bound[0], top=bound[1], right=bound[2], bottom=bound[3]))
                shape = face_utils.shape_to_np(shape)
                shapes.append(shape)
            #for (x,y) in shape:
                #cv2.circle(img, (x,y), 3, (0,0,255), -1)
            col = (255)
            wid = 5
            for shape in shapes:
                for i in range(16):
                    cv2.line(edges, tuple(shape[i]), tuple(shape[i+1]), col, wid, 8, 0)
                for i in range(17,21):
                    cv2.line(edges, tuple(shape[i]), tuple(shape[i+1]), col, wid, 8, 0)
                for i in range(22,26):
                    cv2.line(edges, tuple(shape[i]), tuple(shape[i+1]), col, wid, 8, 0)
                for i in range(27,30):
                    cv2.line(edges, tuple(shape[i]), tuple(shape[i+1]), col, wid, 8, 0)
                for i in range(31,35):
                    cv2.line(edges, tuple(shape[i]), tuple(shape[i+1]), col, wid, 8, 0)
                for i in range(36,41):
                    cv2.line(edges, tuple(shape[i]), tuple(shape[i+1]), col, wid, 8, 0)
                for i in range(42,47):
                    cv2.line(edges, tuple(shape[i]), tuple(shape[i+1]), col, wid, 8, 0)
                for i in range(48,67):
                    cv2.line(edges, tuple(shape[i]), tuple(shape[i+1]), col, wid, 8, 0)

                
                
            
            #im2, contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 
            
            #cv2.drawContours(edges, contours, -1, 255, 1)                 
            #out = cv2.addWeighted(gray,mix, edges,0.8)
            #resized = cv2.resize(out, None, fx=2, fy=2, interpolation = cv2.INTER_LINEAR)
            cv2.namedWindow('test', cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty('test', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.imshow('test',edges)

	    # This also acts as 
            keyCode = cv2.waitKey(30) & 0xff
            # Stop the program on the ESC key
            if keyCode == 27:
               break
        cap.release()
        cv2.destroyAllWindows()
    else:
        print('Unable to open camera')


if __name__ == '__main__':
    show_camera()
