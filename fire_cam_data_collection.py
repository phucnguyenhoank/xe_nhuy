import cv2
import os
import time

stream_url = "http://192.168.188.141:81/stream"
SAVE_DIR = "real_fire_dataset/"
os.makedirs(SAVE_DIR, exist_ok=True)

cap = cv2.VideoCapture(stream_url, cv2.CAP_FFMPEG)
# cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
if not cap.isOpened():
    raise RuntimeError("Cannot open stream")

state = "nofire"
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to read frame")
        break
    cv2.imshow("ESP32 Stream", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break
    elif key == ord("f"):
        state = "fire"
    elif key == ord("n"):
        state = "nofire"

    filename = f"{state}_image_{int(time.time() * 1000)}.jpg"
    path = os.path.join(SAVE_DIR, filename)
    cv2.imwrite(path, frame)
    print("Saved:", path)

cap.release()
cv2.destroyAllWindows()
