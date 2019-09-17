#!/usr/bin/python3

# Simple random twinkle for scroll ambiance
# Based off of strandtest.py in the Adafruit DotStarPiPainter library

import time
import board
import copy
import adafruit_dotstar as dotstar
import random
from colour import Color

numpixels = 312           # Number of LEDs in strip
order     = dotstar.BGR  # Might need GRB instead for older DotStar LEDs
strip     = dotstar.DotStar(board.SCK, board.MOSI, numpixels,
              brightness=0.25, auto_write=False, pixel_order=order)

def limit(x):
    return max(min(x, 1.0), 0.0)

def lerp(a,b,t):
    return ((1-t)*a)+(t*b)

def parseColor(color):
    return eval("0x%s"%(color.hex_l[1:]))

pix1 = []
pix2 = []
count = 0
cycle = 20
baseHue = Color("blue").hue


for i in range(numpixels):
    pix1.append(Color(hsl=(limit(random.gauss(baseHue, 0.05)),limit(random.gauss(0.7, 0.3)),limit(random.gauss(0.4, 0.5)))))
    pix2.append(Color(hsl=(limit(random.gauss(baseHue, 0.05)),limit(random.gauss(0.7, 0.3)),limit(random.gauss(0.4, 0.5)))))

while True:                  # Loop forever
    for i in range(numpixels):
        n = (count+(i%17))%(cycle)
        if(n == 0):

            pix1[i] = copy.copy(pix2[i])
            strip[i] = parseColor(pix1[i])
            if random.uniform(0,2) > 1.3:
                hue = limit(random.gauss(baseHue, 0.05))
                sat = limit(random.gauss(0.8, 0.2))
                lum = limit(random.gauss(0.3, 0.3))
                pix2[i] = Color(hsl=(hue,sat,lum))
            else:
                pix2[i] = Color(hsl=(pix2[i].hue, pix2[i].saturation, 0))
        else:
            hue = lerp(pix1[i].hue, pix2[i].hue, float(n)/(cycle))
            sat = lerp(pix1[i].saturation, pix2[i].saturation, float(n)/(cycle))
            lum = lerp(pix1[i].luminance, pix2[i].luminance, float(n)/(cycle))
            strip[i] = parseColor(Color(hsl=(hue, sat, lum)))

    count += 1
    strip.show()
        # Update strip
    #time.sleep(1.0 / 500)