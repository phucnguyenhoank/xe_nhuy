import cv2
import torch
from ultralytics import YOLO
import socket
import time

class FireDetector:
    def __init__(self, model_path="weights/best.pt", conf_threshold=0.5):
        """Initialize the detector and automatically select the best hardware."""
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Initializing YOLO11 on: {self.device}")
        
        self.model = YOLO(model_path)
        self.conf = conf_threshold

    def process_frame(self, frame):
        """Runs inference and extracts object centers."""
        results = self.model(frame, imgsz=320, conf=self.conf, device=self.device, verbose=False)
        
        centers = []
        is_fire_detected = False
        
        for r in results:
            for box in r.boxes.xywh:
                x, y, w, h = box
                centers.append((int(x), int(y)))
                is_fire_detected = True # Đánh dấu là có lửa
        
        return results[0].plot(), centers, is_fire_detected

def main():
    # --- CẤU HÌNH CAMERA & MODEL ---
    STREAM_URL = "http://192.168.188.141:81/stream"
    MODEL_PATH = "weights/best_2.pt"
    
    # --- CẤU HÌNH GỬI LỆNH XUỐNG ESP32 (QUAN TRỌNG) ---
    ESP_IP = "192.168.188.122" # IP của ESP32 (lấy từ Serial Monitor)
    ESP_PORT = 4210            # Port UDP đã khai báo trong code ESP32
    
    # Khởi tạo UDP Socket (Chỉ khởi tạo 1 lần duy nhất)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.1) # Không chờ đợi quá lâu để tránh lag video

    # Biến kiểm soát tốc độ gửi (Debounce)
    last_sent_time = 0
    SEND_INTERVAL = 2.0 # Chỉ gửi lệnh mỗi 2 giây để tránh treo xe

    # 1. Setup Detector
    detector = FireDetector(model_path=MODEL_PATH)

    # 2. Setup Stream
    cap = cv2.VideoCapture(STREAM_URL, cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    if not cap.isOpened():
        print("Error: Could not open stream.")
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Mất kết nối camera")
                break

            # 3. Detect
            annotated_frame, centers, is_fire = detector.process_frame(frame)

            # 4. Gửi lệnh điều khiển (Logic thông minh)
            current_time = time.time()
            
            if is_fire:
                # Chỉ gửi nếu đã qua khoảng thời gian chờ (2 giây)
                if (current_time - last_sent_time) > SEND_INTERVAL:
                    try:
                        print(f"🔥 FIRE DETECTED! Gửi lệnh bơm nước tới {ESP_IP}...")
                        
                        # Gửi lệnh 'w' (bơm nước) hoặc 'a' (còi hú) tùy ý bạn
                        sock.sendto(b'w', (ESP_IP, ESP_PORT)) 
                        
                        # Cập nhật thời gian vừa gửi
                        last_sent_time = current_time 
                    except Exception as e:
                        print(f"Lỗi gửi mạng: {e}")
            
            # In tọa độ ra màn hình (tùy chọn)
            # for x, y in centers:
            #     print(f"Fire Center: {x}, {y}")

            # 5. UI Logic
            cv2.imshow("YOLO11 Fire Detection", annotated_frame)
            
            # Nhấn 'q' để thoát
            if cv2.waitKey(1) & 0xFF == ord("q"):
                # Gửi lệnh tắt auto hoặc tắt bơm trước khi thoát nếu cần
                sock.sendto(b'o', (ESP_IP, ESP_PORT)) 
                break
                
    finally:
        cap.release()
        cv2.destroyAllWindows()
        sock.close() # Đóng socket

if __name__ == "__main__":
    main()