import cv2
import torch
import socket
from ultralytics import YOLO

class FireTrackingCar:
    def __init__(self, model_path="weights/best.pt", esp32_ip="192.168.188.122", port=4210):
        # 1. AI Setup
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = YOLO(model_path)
        
        # 2. Network Setup
        self.esp32_ip = esp32_ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # 3. Control Constants (Based on 320px width)
        self.FRAME_CENTER_X = 160 
        self.DEADZONE = 25  # Pixels (+/-) where the fire is "centered enough"
        self.last_cmd = None

    def send_command(self, cmd):
        """Sends command only if it's different from the last one to save bandwidth."""
        if cmd != self.last_cmd:
            self.sock.sendto(cmd.encode(), (self.esp32_ip, self.port))
            self.last_cmd = cmd
            print(f"Action: {cmd}")

    def track_fire(self, frame):
        """Logic to decide movement based on fire position."""
        results = self.model(frame, imgsz=320, conf=0.5, device=self.device, verbose=False)
        
        centers = []
        for r in results:
            for box in r.boxes.xywh:
                centers.append(int(box[0])) # We only need X-center for steering

        if not centers:
            # Optional: self.send_command("s") # Stop if fire is lost
            return results[0].plot()

        # Track the first fire detected
        fire_x = centers[0]

        # 4. Movement Logic
        if fire_x < (self.FRAME_CENTER_X - self.DEADZONE):
            self.send_command("l") # Fire is to the left, turn left
        elif fire_x > (self.FRAME_CENTER_X + self.DEADZONE):
            self.send_command("r") # Fire is to the right, turn right
        else:
            # Fire is in the center! Stop movement.
            # You could also send 'w' here to start the pump
            self.send_command("s") 
            print("FIRE CENTERED - READY")

        return results[0].plot()

def main():
    STREAM_URL = "http://192.168.188.141:81/stream"
    car = FireTrackingCar()
    
    cap = cv2.VideoCapture(STREAM_URL, cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break

        # Process and Control
        annotated_frame = car.track_fire(frame)

        cv2.imshow("Smart Fire-Fighting Car", annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            car.send_command("s") # Safety stop
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
