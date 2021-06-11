import cv2
cap = cv2.VideoCapture(0)
# self.cap.set(3,400)
# self.cap.set(4,400)
if not cap.isOpened():
    print("Cannot open webcam")
else:
    print("cam Found")
ret, frame = cap.read()
cv2.imwrite('imagess.png',frame)
cap.release()
