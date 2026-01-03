import cv2
import torch
import redis
import json
from ultralytics import YOLO

# ===== CONFIG =====
STREAM_URL = "http://192.168.188.141:81/stream"
MODEL_PATH = "weights/best_2.pt"
QUEUE_NAME = "fire_centers"
# ==================

class FireDetector:
    def __init__(self, model_path, conf=0.5):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print("YOLO running on:", self.device)
        self.model = YOLO(model_path)
        self.conf = conf

    def detect(self, frame):
        results = self.model(
            frame,
            imgsz=320,
            conf=self.conf,
            device=self.device,
            verbose=False
        )

        centers = []
        for box in results[0].boxes.xywh:
            x, y, w, h = box
            centers.append((int(x), int(y)))

        return results[0].plot(), centers


def main():
    r = redis.Redis()
    detector = FireDetector(MODEL_PATH)

    cap = cv2.VideoCapture(STREAM_URL, cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    if not cap.isOpened():
        print("❌ Cannot open stream")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        annotated, centers = detector.detect(frame)

        # Push only metadata (small & fast)
        if centers:
            payload = {
                "centers": centers,
                "timestamp": cv2.getTickCount()
            }
            r.rpush(QUEUE_NAME, json.dumps(payload))

        cv2.imshow("Fire Detection", annotated)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
