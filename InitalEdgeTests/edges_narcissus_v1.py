# MIT License
# Copyright (c) 2019 JetsonHacks
# See license
# Using a CSI camera (such as the Raspberry Pi Version 2) connected to a 
# NVIDIA Jetson Nano Developer Kit using OpenCV
# Drivers for the camera and OpenCV are included in the base image

import cv2
import numpy as np
import random

# gstreamer_pipeline returns a GStreamer pipeline for capturing from the CSI camera
# Defaults to 1280x720 @ 60fps 
# Flip the image by setting the flip_method (most common values: 0 and 2)
# display_width and display_height determine the size of the window on the screen

def gstreamer_pipeline (capture_width=1024, capture_height=1260, display_width=1260, display_height=1024, framerate=60, flip_method=0) :   
    return ('nvarguscamerasrc ! ' 
    'video/x-raw(memory:NVMM), '
    'width=(int)%d, height=(int)%d, '
    'format=(string)NV12, framerate=(fraction)%d/1 ! '
    'nvvidconv flip-method=%d ! '
    'video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! '
    'videoconvert ! '
    'video/x-raw, format=(string)BGR ! appsink'  % (capture_width,capture_height,framerate,flip_method,display_width,display_height))

def show_camera(sigma=0.33, lower=30, upper=55, mix=0.25, blurVal=0):
    # To flip the image, modify the flip_method parameter (0 and 2 are the most common)
    print gstreamer_pipeline(flip_method=0)
    cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=4), cv2.CAP_GSTREAMER)
    if cap.isOpened():
        window_handle = cv2.namedWindow('CSI Camera', cv2.WINDOW_AUTOSIZE)
        # Window 
        while cv2.getWindowProperty('CSI Camera',0) >= 0:
            ret_val, img = cap.read();
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            blur = cv2.blur(gray, (5+blurVal,5+blurVal))
            edges = cv2.Canny(blur, lower, upper)
            #im2, contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 
            
            #cv2.drawContours(edges, contours, -1, 255, 1)                 
            out = cv2.addWeighted(blur,mix, edges,1.0-mix,0)
            #resized = cv2.resize(out, None, fx=2, fy=2, interpolation = cv2.INTER_LINEAR)
            cv2.imshow('CSI Camera',out)
	    # This also acts as 
            keyCode = cv2.waitKey(30) & 0xff
            # Stop the program on the ESC key
            if keyCode == 27:
               break
            elif keyCode == 97:
               lower = lower - 5
               blurVal += 2
	       print lower
            elif keyCode == 113:
               lower = lower + 5
	       blurVal += 2
               print lower
            elif keyCode == 115:
               upper = upper - 5
	       blurVal += 2
               print upper
            elif keyCode == 119:
               upper = upper + 5
	       blurVal += 2
               print upper
            elif keyCode == 101:
               if mix > 0:
	           mix = mix - .05
	       blurVal += 6
               print mix
            elif keyCode == 100:
               if mix < 1:
	           mix = mix + .05
	       blurVal += 6
               print mix
            else:
               if blurVal > 1: 
		 blurVal -= random.uniform(0, 1.5)
		 blurVal = int(blurVal)
		 if blurVal %2 == 1: blurVal +=1
            
        cap.release()
        cv2.destroyAllWindows()
    else:
        print 'Unable to open camera'


if __name__ == '__main__':
    show_camera()
