import cv2

stream_url = "http://192.168.188.141:81/stream"

cap = cv2.VideoCapture(stream_url, cv2.CAP_FFMPEG)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

if not cap.isOpened():
    raise RuntimeError("Cannot open stream")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to read frame")

    cv2.imshow("ESP32 Raw Stream", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
