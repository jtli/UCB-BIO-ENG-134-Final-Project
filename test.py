import picamera
import time
import numpy as np

camera = picamera.PiCamera()
camera.resolution = (640,480)
time.sleep(2)
camera.capture('output.png')
