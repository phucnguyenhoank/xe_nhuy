import cv2
import time
import socket
import torch
import threading
from ultralytics import YOLO
import queue

# ===== CONFIG =====
STREAM_URL = "http://192.168.188.141:81/stream"
ESP32_IP = "192.168.188.122"
PORT = 4210

CENTER = 160
R = 25
CONTROL_HZ = 2
CONTROL_INTERVAL = 1.0 / CONTROL_HZ
# ==================

class VideoStream:
    def __init__(self, src):
        self.cap = cv2.VideoCapture(src)
        # maxsize=1 cực kỳ quan trọng: Luôn chỉ giữ 1 frame mới nhất
        self.q = queue.Queue(maxsize=1) 
        self.stopped = False

    def start(self):
        t = threading.Thread(target=self.update, args=(), daemon=True)
        t.start()
        return self

    def update(self):
        while not self.stopped:
            ret, frame = self.cap.read()
            if not ret:
                # Nếu mất kết nối, thử khởi động lại cap sau 2 giây
                print("⚠️ Stream lost. Reconnecting...")
                self.cap.release()
                time.sleep(2)
                self.cap = cv2.VideoCapture(STREAM_URL)
                continue
            
            # Kỹ thuật xóa frame cũ, nạp frame mới vào queue
            if not self.q.empty():
                try:
                    self.q.get_nowait()
                except queue.Empty:
                    pass
            self.q.put(frame)

    def read(self):
        # Lấy frame từ queue mà không bị chặn (non-blocking)
        if not self.q.empty():
            return True, self.q.get()
        return False, None

    def stop(self):
        self.stopped = True
        self.cap.release()

# ===== KHỞI TẠO =====
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
def send_cmd(cmd):
    try:
        sock.sendto(cmd.encode(), (ESP32_IP, PORT))
        print("Sent:", cmd)
    except: pass

device = "cuda" if torch.cuda.is_available() else "cpu"
model = YOLO("weights/best_2.pt")

vs = VideoStream(STREAM_URL).start()
time.sleep(2.0)

last_control_time = 0
last_pump_time = 0
is_pumping = False

# ===== LOOP CHÍNH =====
try:
    while True:
        ret, frame = vs.read()
        
        if not ret or frame is None:
            time.sleep(0.01) # Tránh treo CPU khi đợi frame
            continue

        # XỬ LÝ YOLO
        # imgsz=160 là chìa khóa để chạy cực nhanh trên GPU/CPU
        results = model(frame, imgsz=160, conf=0.5, device=device, verbose=False)
        annotated = results[0].plot()

        centers = []
        for box in results[0].boxes.xywh:
            x, y, w, h = box
            centers.append((int(x), int(y)))

        now = time.time()
        
        # Điều hướng
        if centers:
            if now - last_control_time >= CONTROL_INTERVAL:
                last_control_time = now
                x, y = centers[0]
                if x < CENTER - R: send_cmd("l")
                elif x > CENTER + R: send_cmd("r")
                else:
                    print("🎯 FIRE CENTERED")
                    send_cmd("w")
                    last_pump_time = now
                    is_pumping = True
        
        # Logic tắt bơm
        if is_pumping and (now - last_pump_time > 3.0):
            print("🛑 STOP PUMP")
            send_cmd("s")
            is_pumping = False

        cv2.imshow("Fire Detection", annotated)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
finally:
    vs.stop()
    cv2.destroyAllWindows()
    sock.close()
