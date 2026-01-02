import cv2
import torch
from fire_model import FireClassifier

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = FireClassifier().to(device)
model.load_state_dict(torch.load("best_fire_model.pth", map_location=device))
model.eval()

stream_url = "http://192.168.188.141:81/stream"
cap = cv2.VideoCapture(stream_url, cv2.CAP_FFMPEG)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

def detect_fire(frame):
    # BGR → RGB
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    input_tensor = (
        torch.from_numpy(frame)
        .permute(2, 0, 1)
        .unsqueeze(0)
        .float()
        .div(255.0)
        .to(device)
    )

    logit = model(input_tensor)
    prob = torch.sigmoid(logit).item()

    label = "FIRE" if prob >= 0.5 else "NON-FIRE"
    print(f"{prob:.3f} → {label}")
    return label, prob

with torch.no_grad():
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        label, prob = detect_fire(frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()
