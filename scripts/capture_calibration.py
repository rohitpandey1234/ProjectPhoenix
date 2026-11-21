import cv2
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Calibration image folder
IMAGE_DIR = PROJECT_ROOT / "calibration_images"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

cap = cv2.VideoCapture(0)

count = len(list(IMAGE_DIR.glob("*.jpg")))

print("===================================")
print("Project Phoenix Camera Calibration")
print("SPACE : Capture Image")
print("Q     : Quit")
print("===================================")

while True:

    ret, frame = cap.read()

    if not ret:
        break

    cv2.imshow("Calibration Capture", frame)

    key = cv2.waitKey(1)

    if key == ord(' '):

        filename = IMAGE_DIR / f"img_{count}.jpg"

        cv2.imwrite(str(filename), frame)

        print(f"Saved : {filename}")

        count += 1

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
