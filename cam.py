from picamera import PiCamera
import time
try:
    from PIL import Image,ImageEnhance
except ImportError:
    import Image, ImageEnhance
import pytesseract
import cv2
import numpy as np
camera = PiCamera()
camera.resolution = (512, 512)
time.sleep(2)
camera.capture("idimg.jpg")
idimg=cv2.imread("idimg.jpg")
idimg = cv2.rotate(idimg, cv2.ROTATE_90_CLOCKWISE)
x=250
y=200
idimg = idimg[x: x+150, y: y+300]
idimg = cv2.cvtColor(idimg, cv2.COLOR_BGR2GRAY)

cv2.imwrite('idimg2.jpg',idimg)
text = pytesseract.image_to_string(idimg,config='--psm 6')

print(text)