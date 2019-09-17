#!/usr/bin/python3

# Simple random twinkle for scroll ambiance
# Based off of strandtest.py in the Adafruit DotStarPiPainter library

import time
import board
import adafruit_dotstar as dotstar
import random

numpixels = 312           # Number of LEDs in strip
order     = dotstar.BGR  # Might need GRB instead for older DotStar LEDs
strip     = dotstar.DotStar(board.SCK, board.MOSI, numpixels,
              brightness=1.0, auto_write=False, pixel_order=order)

def limit(x):
    return max(min(x, 1.0), 0.0)

def lerp(a,b,t):
    return ((1-t)*a)+(t*b)

pix1 = []
pix2 = []
count = 0
cycle = 50

for i in range(numpixels):
    pix1.append(limit(random.gauss(0.4, 0.5)))
    pix2.append(limit(random.gauss(0.4, 0.5)))

while True:                  # Loop forever
    for i in range(numpixels):
        n = (count+(i%13))%(cycle+(i%(numpixels/2)))
        if(n == 0):
            strip[i] = (1,1,1,pix2[i])
            pix1[i] = pix2[i]
            if random.uniform(0,2) > 1.4:
                pix2[i] = limit(random.gauss(0.5, 0.7))
            else:
                pix2[i] = 0
        else:
            brightness = lerp(pix1[i], pix2[i], float(n)/(cycle+(i%(numpixels/2))))
            strip[i] = (1,1,1,(brightness))

    count += 1
    strip.show()
        # Update strip
    time.sleep(1.0 / 100)