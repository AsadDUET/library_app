# import numpy as np
import pyzbar.pyzbar as pyzbar

def scan(frame):
    data = []
    decodedObjects = pyzbar.decode(frame)
    for obj in decodedObjects:
        data.append(obj.data.decode())
    if data:
        return str(data[0])
    else:
        return None

if __name__=='__main__':
    import cv2
    cap = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_PLAIN
    while True:
        _, frame = cap.read()
        d = scan(frame)
        print (d)
        if d is not None:
            cv2.putText(frame, d, (50, 50), font, 2,
                        (255, 0, 0), 3)

        cv2.imshow("Frame", frame)

        key = cv2.waitKey(1)
        if key == 27:
            cap.release()
            cv2.destroyAllWindows()
            break
