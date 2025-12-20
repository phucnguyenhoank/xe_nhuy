import cv2
import os
import time

save_dir = "no_fire_images"
os.makedirs(save_dir, exist_ok=True)

cap = cv2.VideoCapture(0)

count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow("Camera", frame)

    # save image every frame (VERY FAST)
    filename = os.path.join(save_dir, f"img_{count:05d}.jpg")
    cv2.imwrite(filename, frame)
    count += 1

    key = cv2.waitKey(1)
    if key == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()

print(f"Saved {count} images")
