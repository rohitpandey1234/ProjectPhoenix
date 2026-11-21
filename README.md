# ProjectPhoenix
GPS Denied Navigation using Visual Odometery and Map Localisation for Ardupilot 4.6.3
PROJECT PHOENIX
GPS-Denied UAV Navigation: Developer Setup, Architecture & Testing
ArduCopter 4.6.3 • EKF3 • Jetson Orin Nano • Python • MAVLink
Project	Development setup
Autopilot	ArduCopter 4.6.3 / EKF3 (version used during development)
Companion	Jetson Orin Nano / Linux
Ground station	QGroundControl
Stage	Experimental; simulation and controlled testing

1. Purpose and System Overview
Project Phoenix is an experimental navigation system intended to keep a UAV's navigation estimate available when GPS is unreliable or unavailable. It combines GPS, camera-based Visual Odometry (VO), and satellite-map localization. It checks source health/confidence, selects a source, maintains a navigation state and sends position/attitude to ArduPilot over MAVLink.
The current source-selection code is rule-based; it is not yet a full mathematical Kalman Filter.
Architecture
CAMERA → image capture → ORB features/tracking → Visual Odometry
GPS → global position and health metrics
SATELLITE MAP → downloaded tiles → map matching/localization
GPS + VO + MAP → health checks and source selection → NavigationState
NavigationState → MAVLink Bridge → VISION_POSITION_ESTIMATE → ArduPilot EKF3 → QGroundControl
Phoenix internal source selection and ArduPilot EKF source-set selection are separate. Phoenix reporting VO does not automatically switch ArduPilot to Source Set 2 unless a source-switch mechanism is configured/implemented.
2. Requirements and Dependencies
Hardware
•	Linux companion computer (development target: Jetson Orin Nano)
•	Camera supported by capture code/driver
•	ArduPilot flight controller and MAVLink connection (USB, UART or UDP)
•	GPS receiver for GPS-assisted testing
Software
•	Ubuntu/Linux (Ubuntu 22.04 was preferred during development; adapt to installed Jetson OS)
•	Python 3.10+; check package compatibility
•	Git, pip and venv
•	OpenCV, NumPy, PyMAVLink, Rasterio
•	ArduPilot SITL for simulation and QGroundControl
Install system packages
sudo apt update
sudo apt upgrade -y
sudo apt install -y \
  python3 python3-pip python3-venv python3-dev \
  git build-essential pkg-config \
  libopencv-dev python3-opencv \
  gstreamer1.0-tools gstreamer1.0-plugins-base \
  gstreamer1.0-plugins-good gstreamer1.0-plugins-bad \
  gstreamer1.0-plugins-ugly
Clone and set up Python environment
git clone https://github.com/YOUR_USERNAME/ProjectPhoenix.git
cd ProjectPhoenix
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install numpy opencv-python pymavlink rasterio
Verify installation
python --version
python -c "import cv2; print(cv2.__version__)"
python -c "import numpy; print(numpy.__version__)"
python -c "from pymavlink import mavutil; print('pymavlink OK')"
python -c "import rasterio; print(rasterio.__version__)"
These are the core dependencies identified in setup notes. Additional imports in the actual checkout may require more packages. Maintain a tested requirements.txt rather than blindly freezing unrelated packages.
# After confirming the environment works:
pip freeze > requirements.txt
# On another machine:
pip install -r requirements.txt
3. Camera Setup and Calibration
VO depends on the selected camera, lens, resolution, focus, exposure, frame rate and distortion. Every camera/lens/resolution setup needs its own calibration; do not reuse calibration from another camera.
Find and test camera
ls /dev/video*
 
python - <<'PY'
import cv2
cam=cv2.VideoCapture(0)  # change index for your camera
print("Camera opened:",cam.isOpened())
if cam.isOpened():
    ok,frame=cam.read()
    print("Frame:",ok, None if frame is None else frame.shape)
cam.release()
PY
Edit camera/webcam.py for the camera index/device, resolution, frame rate, image format and camera-specific exposure/focus options. Some cameras require a vendor SDK or a GStreamer pipeline rather than OpenCV VideoCapture.
Calibration procedure
•	Print a checkerboard with known square dimensions.
•	Capture sharp checkerboard images from varied angles, distances and positions in the frame.
•	Use camera/calibration.py (confirm the actual script command in the repository).
•	Calculate camera matrix (fx, fy, cx, cy) and distortion coefficients (k1, k2, p1, p2, k3).
•	Save calibration and load it in camera/VO configuration; calibrate at the same resolution used for operation.
•	Test image quality, ORB matches, tracking, VO confidence and behavior with blur/low texture/vibration.
The calibration command/arguments are not specified here because the exact current script entry point has not been checked.
4. Satellite Map Setup, API and Reference Coordinates
Map localization uses satellite tiles downloaded for a defined area and stored locally. Development notes specify data/maps and zoom level 18. The download setup needs a provider API key, reference/start latitude and longitude, and square-area size/coverage.
Required setting	What the user supplies
Map imagery API key	Create own provider account/key; enable imagery service and review license, quota and billing.
Reference/start latitude	Latitude of the reference point used to center/anchor the square download (follow downloader convention).
Reference/start longitude	Longitude for that same reference point.
Square coverage/size	Desired square area around reference coordinates; confirm units/interpretation in downloader.
Zoom	Current project note: zoom 18; adjust if appropriate and supported.
Output	Store downloaded tiles in data/maps using expected naming/layout.

The latitude/longitude define where map downloading starts/is centered; area size defines the square coverage. Ensure the square covers the test route and enough neighboring tiles for movement.
Keep API key private
# Example only, if downloader supports this environment variable:
export MAP_API_KEY="YOUR_OWN_API_KEY"
 
# Ignore local secrets in .gitignore, for example:
# .env
# config_local.py
Do not commit personal API keys. Provider licensing, attribution, quota and billing rules apply. The exact provider, downloader filename, CLI options and download command are not verified from the source checkout; inspect the actual downloader/config and insert its real invocation.
Load map tiles
# Module usage described in project notes:
tiles = TileManager(ZOOM)
loader = MapLoader(MAP_FOLDER, tiles)
localizer = MapLocalizer()
 
# Example neighbor-tile preload:
neighbor_tiles = loader.preload_neighbors(
    ZOOM, current_tile_x, current_tile_y, radius=1
)
MapLoader/TileManager load local tiles; MapLocalizer compares camera information to satellite imagery to estimate global location. Confirm downloaded tile coverage and directory structure match the loader.
5. Software Structure
Module	Purpose
main.py	Application loop and module coordination
config.py	Shared thresholds, settings and connection configuration
camera/webcam.py	Capture frames and camera settings
camera/calibration.py	Camera calibration workflow
vo/orb_vo.py	ORB feature detection/matching and VO estimation
vo/tracker.py	Track features across frames
vo/pose.py	Motion/pose estimation helpers
map/loader.py	Load map imagery/tiles from disk
map/tiles.py	Tile indexing, coordinates and neighbor handling
map/localiser.py	Map matching/localization
fusion/ekf.py	Current rule-based health/source selection and state update
fusion/state.py	Shared sensor and fused state container
mavlink/bridge.py	Receive telemetry, heartbeat and external-vision transmission
mavlink/sitl.py	Simulation helpers, if used
utils/	Helpers and diagnostics

6. Navigation State, Health and Source Logic
NavigationState stores GPS values, VO position/attitude/confidence, map position/confidence, fused x/y/z, roll/pitch/yaw, velocity/quaternion fields (when populated), confidence, selected source and timestamp.
Source	Health check in project notes
GPS	Fix ≥ 3, satellites ≥ 8, HDOP ≤ 2
VO	VO confidence ≥ 0.60
Map	Map confidence ≥ 0.60

GPS	VO	Map	Selected Phoenix source
Healthy	Healthy	Any	GPS+VO
Unhealthy	Healthy	Healthy	MAP+VO
Healthy	Unhealthy	Any	GPS
Unhealthy	Unhealthy	Healthy	MAP
Unhealthy	Healthy	Unhealthy	VO
Unhealthy	Unhealthy	Unhealthy	NONE

This is rule-based selection, not probabilistic Kalman fusion. Review each branch for whether unselected values are retained, reset or copied. Local convention in notes is NED: X North, Y East, Z Down. GPS/map coordinates may be converted relative to a stored home/reference. Roll/pitch/yaw may be converted to quaternion. Validate all frames, signs, scales and camera-to-vehicle mounting.
7. MAVLink Bridge and External Vision
Bridge uses pymavlink, waits for heartbeat, receives telemetry and sends navigation. Current default connection: udp:127.0.0.1:14551; change for the SITL/hardware link.
Telemetry caching
Latest GPS_RAW_INT, GLOBAL_POSITION_INT, ATTITUDE and HEARTBEAT are cached because different message types do not necessarily arrive in the same loop. Cached messages must have age/timeouts; otherwise stale data may remain healthy after GPS loss.
External vision message
•	Currently sends VISION_POSITION_ESTIMATE.
•	Includes timestamp, x/y/z and roll/pitch/yaw.
•	Configured rate approximately 30 Hz.
•	Validates source and values (None/NaN/Infinity) before sending.
•	Timestamp convention, coordinate frame, scale, sensor offsets and stream health must be checked with target firmware.
ODOMETRY can carry more information and is generally preferred for newer integrations, but this initial integration uses VISION_POSITION_ESTIMATE. Verify requirements against exact firmware.
8. ArduPilot Configuration — ArduCopter 4.6.3 / EKF3
Values below reflect development notes; verify enum meanings and parameter availability on installed firmware.
Parameter	Value	Meaning
AHRS_EKF_TYPE	3	EKF3
EK3_ENABLE	1	Enable EKF3
EK2_ENABLE	0	Disable EKF2
VISO_TYPE	3	External Vision interface as configured
VISO_POS_X/Y/Z	0 / 0 / 0	Sensor-offset placeholders; enter actual camera offsets where needed
EK3_SRC1_POSXY	3	GPS horizontal position
EK3_SRC1_VELXY	3	GPS horizontal velocity
EK3_SRC1_POSZ	1	Barometer vertical position
EK3_SRC1_VELZ	0	None
EK3_SRC1_YAW	1	Compass
EK3_SRC2_POSXY	6	ExternalNav horizontal position
EK3_SRC2_VELXY	0	None
EK3_SRC2_POSZ	6	ExternalNav vertical position
EK3_SRC2_VELZ	0	None
EK3_SRC2_YAW	6	ExternalNav

MAVProxy example
param set AHRS_EKF_TYPE 3
param set EK3_ENABLE 1
param set EK2_ENABLE 0
param set VISO_TYPE 3
param set VISO_POS_X 0
param set VISO_POS_Y 0
param set VISO_POS_Z 0
 
param set EK3_SRC1_POSXY 3
param set EK3_SRC1_VELXY 3
param set EK3_SRC1_POSZ 1
param set EK3_SRC1_VELZ 0
param set EK3_SRC1_YAW 1
 
param set EK3_SRC2_POSXY 6
param set EK3_SRC2_VELXY 0
param set EK3_SRC2_POSZ 6
param set EK3_SRC2_VELZ 0
param set EK3_SRC2_YAW 6
Reboot when required. Sensor offsets are placeholders and must reflect the real installation.
9. EKF Source-Set Switching
Source Set 1 is GPS; Source Set 2 is ExternalNav. Phoenix's displayed source label is not an ArduPilot EKF switch. Configure a supported source-set switching method (e.g., auxiliary RC source switch) or implement the appropriate control logic and verify the active set. A development note used RCx_OPTION = 90 as an example; replace x with the channel and verify option meaning for the target firmware.
# Example only—confirm channel and option for firmware:
param set RCx_OPTION 90
10. Run Phoenix
cd ProjectPhoenix
source venv/bin/activate
python3 main.py
Check camera feed, ORB match count, VO confidence, map confidence, source label, MAVLink heartbeat and vision-send diagnostics. Verify the configured endpoint is correct.
11. Recommended Test Sequence
•	Test camera capture and correct device/resolution.
•	Calibrate camera and confirm calibration is loaded.
•	Test ORB detection/tracking and VO with textured scenes.
•	Check VO position/confidence and loss/recovery behavior.
•	Download/load tiles for correct reference coordinates and square coverage.
•	Test map localization alone; monitor confidence.
•	Run SITL and verify MAVLink connection.
•	Confirm ArduPilot receives External Vision and reports it healthy.
•	Simulate GPS loss using a method that actually stops simulated GPS messages; confirm Phoenix GPS health goes false and source changes.
•	Separately verify ArduPilot EKF source-set switching to ExternalNav.
•	Proceed to controlled hardware tests only after frames, signs, scales, timing, offsets and health behavior are checked.
12. Current Limitations / Status
•	Fusion module is rule-based source selection, not a full Kalman filter.
•	GPS cache needs age/timeouts to prevent stale data being treated as healthy.
•	Phoenix source selection and ArduPilot EKF switching are separate.
•	Map localization/confidence requires further testing.
•	External Vision timing, frames, offsets and health need validation against ArduCopter 4.6.3.
•	GPS-denied autonomous navigation is experimental and has not been operationally validated or certified.
13. Security and Safety
•	Never publish API keys, credentials or private configs; use environment variables/local ignored files.
•	Respect imagery provider licensing, attribution, quotas and billing.
•	Use SITL first and controlled tests with a pilot ready to take over.
•	Do not rely on this experimental system as the sole navigation source for safety-critical missions.
14. References
•	ArduPilot Copter 4.6.3 parameters: https://ardupilot.org/copter/docs/parameters-Copter-stable-V4.6.3.html
•	Non-GPS position estimation: https://ardupilot.org/dev/docs/mavlink-nongps-position-estimation.html
•	EKF source selection: https://ardupilot.org/copter/docs/common-ekf-sources.html
•	PyMAVLink: https://mavlink.io/en/mavgen_python/
•	OpenCV: https://opencv.org/
•	Rasterio: https://rasterio.readthedocs.io/
