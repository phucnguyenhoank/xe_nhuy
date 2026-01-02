import cv2
from ultralytics import YOLO

# 1. Load your trained model
# Replace with the path to your actual trained model file
# If you exported to OpenVINO, point to the directory: "runs/detect/train/weights/best_openvino_model/"
model = YOLO("weights/best.pt")

stream_url = "http://192.168.188.141:81/stream"

cap = cv2.VideoCapture(stream_url, cv2.CAP_FFMPEG)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

if not cap.isOpened():
    raise RuntimeError("Cannot open stream")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to read frame")
        break

    # 2. Run Inference
    # imgsz=320: Matches your training size for best accuracy
    # verbose=False: Prevents printing every prediction to the console
    # conf=0.5: Only show detections with >50% confidence (adjust as needed)
    results = model(frame, imgsz=320, conf=0.5, verbose=False)

    # 3. Visualize Results
    # .plot() draws the bounding boxes and labels directly onto the frame
    annotated_frame = results[0].plot()

    # 4. Display the annotated frame
    cv2.imshow("YOLO11 Fire Detection", annotated_frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
