from pathlib import Path

from camera.calibration import CameraCalibration

PROJECT_ROOT = Path(__file__).resolve().parent.parent

IMAGE_DIR = PROJECT_ROOT / "calibration_images"

cal = CameraCalibration()

cal.calibrate(str(IMAGE_DIR))
