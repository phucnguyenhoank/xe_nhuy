import cv2
from PIL import Image
import torchvision.transforms as transforms
import torch
from fire_model import FireClassifier

# 1. Load the model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# Replace FireClassifier() with your specific model class
model = FireClassifier().to(device) 
# Use weights_only=True for safer loading
model.load_state_dict(torch.load('best_fire_model.pth', weights_only=True)) 
model.eval() # Set to evaluation mode

# 2. Define the exact same preprocessing used in training
preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

# 3. Open the camera
cap = cv2.VideoCapture(0) # 0 is typically the built-in webcam


while True:
    ret, frame = cap.read()
    if not ret: break

    # Convert frame for processing
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb_frame)
    
    # Preprocess and prepare for model input
    input_tensor = preprocess(pil_img).unsqueeze(0).to(device)

    # Prediction
    with torch.no_grad():
        output = model(input_tensor)
        # Apply sigmoid for probability
        prob = torch.sigmoid(output).item() 
        print(prob)
        # Adjust threshold and labels based on your training
        label = "FIRE" if prob >= 0.5 else "NON-FIRE" 
        color = (0, 0, 255) if label == "FIRE" else (0, 255, 0)

    # Display results
    cv2.putText(frame, f"{label} ({prob:.2f})", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    cv2.imshow('Fire Detection Test', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
