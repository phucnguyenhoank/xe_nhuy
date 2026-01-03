import cv2
import time
import socket
import torch
from ultralytics import YOLO
import random

# ===== CONFIG =====
STREAM_URL = "http://192.168.188.141:81/stream"
ESP32_IP = "192.168.188.122"
PORT = 4210

CENTER = 160
R = 25
CONTROL_HZ = 2
CONTROL_INTERVAL = 1.0 / CONTROL_HZ
# ==================

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_cmd(cmd):
    sock.sendto(cmd.encode(), (ESP32_IP, PORT))
    print("Sent:", cmd)

# ===== YOLO =====
device = "cuda" if torch.cuda.is_available() else "cpu"
print("Using device:", device)
model = YOLO("weights/best_2.pt")

# ===== STREAM =====
cap = cv2.VideoCapture(STREAM_URL)

if not cap.isOpened():
    print("❌ Cannot open stream. Check ESP32 IP / WiFi.")
    exit(1)

last_control_time = 0
last_pump_time = 0
is_pumping = False
# ===== LOOP =====
while True:
    print(f'running...{random.random()}')
    ret, frame = cap.read()
    if not ret:
        print("❌ Stream lost")
        break

    results = model(frame, imgsz=320, conf=0.5, device=device, verbose=False)
    # annotated = results[0].plot()

    centers = []
    for box in results[0].boxes.xywh:
        x, y, w, h = box
        centers.append((int(x), int(y)))

    now = time.time()
    if centers and now - last_control_time >= CONTROL_INTERVAL:
        last_control_time = now
        x, y = centers[0]

        if x < CENTER - R:
            send_cmd("l")
        elif x > CENTER + R:
            send_cmd("r")
        else:
            print("🔥 FIRE CENTERED")
            print("WATER PUMP")
            send_cmd("w")
            last_pump_time = now
            is_pumping = True
    elif is_pumping and last_pump_time - now > 3:
        print("STOP PUMP WATER")
        send_cmd("s")
        is_pumping = False

    # cv2.imshow("Fire Detection", annotated)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
