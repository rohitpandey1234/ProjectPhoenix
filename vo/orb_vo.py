import cv2

from vo.tracker import FeatureTracker
from vo.pose import PoseEstimator


class VisualOdometry:

    def __init__(self):

        self.orb = cv2.ORB_create(
            nfeatures=1500,
            scaleFactor=1.2,
            nlevels=8
        )

        self.tracker = FeatureTracker()

        self.pose = PoseEstimator()

        self.prev_keypoints = None
        self.prev_descriptors = None

    # -------------------------------------------------
    # PROCESS FRAME
    # -------------------------------------------------

    def process(self, frame):

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        keypoints, descriptors = self.orb.detectAndCompute(
            gray,
            None
        )

        output = frame.copy()

        cv2.drawKeypoints(
            output,
            keypoints,
            output,
            color=(0, 255, 0),
            flags=0
        )

        pose = None

        matches = []

        if (
            self.prev_descriptors is not None and
            descriptors is not None
        ):

            matches = self.tracker.match(

                self.prev_descriptors,

                descriptors

            )

            pose = self.pose.estimate(

                self.prev_keypoints,

                keypoints,

                matches

            )

        self.prev_keypoints = keypoints
        self.prev_descriptors = descriptors

        if pose is None:

            pose = {

                "x": 0.0,
                "y": 0.0,
                "z": 0.0,

                "vx": 0.0,
                "vy": 0.0,
                "vz": 0.0,

                "roll": 0.0,
                "pitch": 0.0,
                "yaw": 0.0,

                "confidence": 0.0,

                "matches": 0,

                "timestamp": 0.0

            }

        return {

            "frame": output,

            "keypoints": len(keypoints),

            "matches": len(matches),

            "pose": pose

        }

    # -------------------------------------------------
    # RESET
    # -------------------------------------------------

    def reset(self):

        self.prev_keypoints = None

        self.prev_descriptors = None

        self.pose = PoseEstimator()
