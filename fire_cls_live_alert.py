import cv2
import torch
from fire_model import FireClassifier
import socket
import time

ESP32_IP = "192.168.28.122"
PORT = 4210

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load model
model = FireClassifier().to(device)
model.load_state_dict(torch.load("best_fire_model.pth", map_location=device))
model.eval()

# ESP32-CAM stream
stream_url = "http://192.168.28.141:81/stream"
cap = cv2.VideoCapture(stream_url, cv2.CAP_FFMPEG)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

def detect_fire(frame):
    # --- FAST PREPROCESS ---
    # img = cv2.resize(frame, (224, 224))
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    input_tensor = (
        torch.from_numpy(img)
        .permute(2, 0, 1)
        .unsqueeze(0)
        .float()
        .div(255.0)
        .to(device)
    )

    logit = model(input_tensor)
    prob = torch.sigmoid(logit).item()

    label = "FIRE" if prob >= 0.5 else "NON-FIRE"
    return label, prob

with torch.no_grad():
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Stream disconnected")
            time.sleep(0.5)
            continue

        label, prob = detect_fire(frame)
        print(f"{prob}, {label}")

        # ---- SEND COMMAND ----
        if label == "FIRE":
            cmd = "a"
            sock.sendto(cmd.encode(), (ESP32_IP, PORT))
        else:
            cmd = "o"
            sock.sendto(cmd.encode(), (ESP32_IP, PORT))

        # ---- DRAW OVERLAY ----
        color = (0, 0, 255) if label == "FIRE" else (0, 255, 0)
        text = f"{label}  {prob:.2f}"

        cv2.putText(
            frame,
            text,
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            color,
            3,
            cv2.LINE_AA
        )

        # ---- SHOW STREAM ----
        # Resize for display only
        display = cv2.resize(frame, (320, 240))

        # Show
        cv2.imshow("ESP32 Fire Detection", display)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()
