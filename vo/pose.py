import cv2
import numpy as np
import time


class PoseEstimator:

    def __init__(self):

        # Camera Intrinsics
        self.K = np.array([
            [700, 0, 320],
            [0, 700, 240],
            [0,   0,   1]
        ], dtype=np.float64)

        # Global Pose
        self.R_total = np.eye(3)
        self.t_total = np.zeros((3, 1))

        # Velocity
        self.prev_t = np.zeros((3, 1))
        self.prev_time = time.time()

    # -------------------------------------------------
    # Rotation Matrix -> Euler
    # -------------------------------------------------

    def rotation_to_euler(self, R):

        sy = np.sqrt(
            R[0, 0] * R[0, 0] +
            R[1, 0] * R[1, 0]
        )

        singular = sy < 1e-6

        if not singular:

            roll = np.arctan2(
                R[2, 1],
                R[2, 2]
            )

            pitch = np.arctan2(
                -R[2, 0],
                sy
            )

            yaw = np.arctan2(
                R[1, 0],
                R[0, 0]
            )

        else:

            roll = np.arctan2(
                -R[1, 2],
                R[1, 1]
            )

            pitch = np.arctan2(
                -R[2, 0],
                sy
            )

            yaw = 0.0

        return roll, pitch, yaw

    # -------------------------------------------------
    # Estimate Pose
    # -------------------------------------------------

    def estimate(self, kp1, kp2, matches):

        if len(matches) < 8:
            return None

        pts1 = np.float32(
            [kp1[m.queryIdx].pt for m in matches]
        )

        pts2 = np.float32(
            [kp2[m.trainIdx].pt for m in matches]
        )

        E, mask = cv2.findEssentialMat(
            pts1,
            pts2,
            self.K,
            method=cv2.RANSAC,
            prob=0.999,
            threshold=1.0
        )

        if E is None:
            return None

        _, R, t, mask = cv2.recoverPose(
            E,
            pts1,
            pts2,
            self.K
        )

        # Update Global Pose
        self.t_total += self.R_total @ t
        self.R_total = R @ self.R_total

        roll, pitch, yaw = self.rotation_to_euler(
            self.R_total
        )

        # Position
        x = float(self.t_total[0])
        y = float(self.t_total[1])
        z = float(self.t_total[2])

        # Velocity
        now = time.time()

        dt = now - self.prev_time

        if dt <= 0:
            dt = 0.02

        vx = (x - float(self.prev_t[0])) / dt
        vy = (y - float(self.prev_t[1])) / dt
        vz = (z - float(self.prev_t[2])) / dt

        self.prev_t = self.t_total.copy()
        self.prev_time = now

        confidence = min(
            1.0,
            len(matches) / 300.0
        )

        return {

            "R": self.R_total,

            "t": self.t_total,

            "x": x,
            "y": y,
            "z": z,

            "vx": vx,
            "vy": vy,
            "vz": vz,

            "roll": roll,
            "pitch": pitch,
            "yaw": yaw,

            "confidence": confidence,

            "matches": len(matches),

            "timestamp": now

        }
