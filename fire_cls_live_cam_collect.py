import cv2
import torch
import os
from datetime import datetime
from fire_model import FireClassifier

# 1. Tạo thư mục lưu trữ nếu chưa có
output_folder = "saved_frames"
os.makedirs(output_folder, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = FireClassifier().to(device)
model.load_state_dict(torch.load("best_fire_model.pth", map_location=device))
model.eval()

stream_url = "http://192.168.28.141:81/stream"
cap = cv2.VideoCapture(stream_url, cv2.CAP_FFMPEG)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

def detect_fire(original_frame):
    # Tạo bản sao để xử lý dự đoán, không làm ảnh hưởng ảnh gốc
    input_frame = cv2.resize(original_frame, (224, 224))
    input_frame = cv2.cvtColor(input_frame, cv2.COLOR_BGR2RGB)

    input_tensor = (
        torch.from_numpy(input_frame)
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
    print("Đang bắt đầu stream... Nhấn 'q' để thoát.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Không thể nhận frame từ camera.")
            break
        
        # Nhận kết quả dự đoán
        label, prob = detect_fire(frame)

        # 2. Vẽ nhãn và độ tin cậy lên khung hình gốc (để hiển thị)
        color = (0, 0, 255) if label == "FIRE" else (0, 255, 0)
        text = f"{label} ({prob:.2f})"
        cv2.putText(frame, text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        # 3. Hiển thị hình ảnh
        cv2.imshow("Fire Detection Stream", frame)

        # 4. Lưu khung hình gốc (giữ nguyên size) vào folder
        # Tên file bao gồm thời gian để không bị ghi đè
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = os.path.join(output_folder, f"frame_{timestamp}.jpg")
        # cv2.imwrite(filename, frame)

        # In log ra terminal
        print(f"Saved: {filename} | Prediction: {label} ({prob:.3f})")

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()


# import cv2
# import torch
# import os
# from datetime import datetime
# from fire_model import FireClassifier

# # 1. Tạo thư mục lưu trữ nếu chưa có
# output_folder = "saved_frames2"
# os.makedirs(output_folder, exist_ok=True)

# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# model = FireClassifier().to(device)
# model.load_state_dict(torch.load("best_fire_model.pth", map_location=device))
# model.eval()

# stream_url = "http://192.168.28.141:81/stream"
# cap = cv2.VideoCapture(stream_url, cv2.CAP_FFMPEG)
# cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)


# with torch.no_grad():
#     print("Đang bắt đầu stream... Nhấn 'q' để thoát.")
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             print("Không thể nhận frame từ camera.")
#             break
    
#         # 3. Hiển thị hình ảnh
#         cv2.imshow("Fire Detection Stream", frame)

#         # 4. Lưu khung hình gốc (giữ nguyên size) vào folder
#         # Tên file bao gồm thời gian để không bị ghi đè
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
#         filename = os.path.join(output_folder, f"frame_{timestamp}.jpg")
#         cv2.imwrite(filename, frame)

#         # In log ra terminal
#         print(f"Saved: {filename}")

#         if cv2.waitKey(1) & 0xFF == ord("q"):
#             break

# cap.release()
# cv2.destroyAllWindows()
