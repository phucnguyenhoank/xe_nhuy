import cv2
import torch
from ultralytics import YOLO

class FireDetector:
    def __init__(self, model_path="weights/best.pt", conf_threshold=0.5):
        """Initialize the detector and automatically select the best hardware."""
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Initializing YOLO11 on: {self.device}")
        
        self.model = YOLO(model_path)
        self.conf = conf_threshold

    def process_frame(self, frame):
        """Runs inference and extracts object centers."""
        # imgsz=320 matches your 240x320 dataset requirements
        results = self.model(frame, imgsz=320, conf=self.conf, device=self.device, verbose=False)
        
        centers = []
        for r in results:
            for box in r.boxes.xywh:
                x, y, w, h = box
                centers.append((int(x), int(y)))
        
        # results[0].plot() provides the annotated image
        return results[0].plot(), centers

def main():
    # Configuration
    STREAM_URL = "http://192.168.188.141:81/stream"
    MODEL_PATH = "weights/best_2.pt"
    
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
                break

            # 3. Detect and Get Metadata
            annotated_frame, centers = detector.process_frame(frame)

            # 4. Handle Results (Modular output)
            for x, y in centers:
                print(f"Fire Detected at Center: X={x}, Y={y}")

            # 5. UI Logic
            cv2.imshow("YOLO11 Fire Detection", annotated_frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
