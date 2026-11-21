from fusion.state import NavigationState

import math
import time


class NavigationEKF:

    def __init__(self):

        self.state = NavigationState()

        # Last update time
        self.last_time = time.time()

        # Previous Local Position
        self.prev_x = 0.0
        self.prev_y = 0.0
        self.prev_z = 0.0

        # Home GPS
        self.home_lat = None
        self.home_lon = None
        self.home_alt = None

        # Earth Radius
        self.EARTH_RADIUS = 6378137.0
            # -------------------------------------------------
    # GPS HEALTH
    # -------------------------------------------------

    def gps_healthy(self):

        if self.state.gps_fix < 3:
            return False

        if self.state.gps_satellites < 8:
            return False

        if self.state.gps_hdop > 2.0:
            return False

        return True

    # -------------------------------------------------
    # VISUAL ODOMETRY HEALTH
    # -------------------------------------------------

    def vo_healthy(self):

        if self.state.vo_confidence < 0.60:
            return False

        return True

    # -------------------------------------------------
    # MAP HEALTH
    # -------------------------------------------------

    def map_healthy(self):

        if self.state.map_confidence < 0.60:
            return False

        return True

    # -------------------------------------------------
    # SAVE HOME POSITION
    # -------------------------------------------------

    def set_home(self):

        if self.home_lat is not None:
            return

        if not self.gps_healthy():
            return

        self.home_lat = self.state.gps_lat
        self.home_lon = self.state.gps_lon
        self.home_alt = self.state.gps_alt

        print("--------------------------------")
        print("HOME POSITION SAVED")
        print(
            self.home_lat,
            self.home_lon,
            self.home_alt
        )
        print("--------------------------------")
            # -------------------------------------------------
    # MAIN FUSION
    # -------------------------------------------------

    def update(self):

        now = time.time()

        dt = now - self.last_time

        if dt <= 0:
            dt = 0.02

        self.last_time = now

        # --------------------------------------------
        # Save Home Position
        # --------------------------------------------

        self.set_home()

        gps_ok = self.gps_healthy()
        vo_ok = self.vo_healthy()
        map_ok = self.map_healthy()

        # --------------------------------------------
        # PRIORITY 1
        # GPS + VO
        # --------------------------------------------

        if gps_ok and vo_ok:

            self.state.source = "GPS+VO"

            self.state.fused_lat = self.state.gps_lat
            self.state.fused_lon = self.state.gps_lon
            self.state.fused_alt = self.state.gps_alt

            self.state.fused_roll = self.state.vo_roll
            self.state.fused_pitch = self.state.vo_pitch
            self.state.fused_yaw = self.state.vo_yaw

            self.state.fused_x = self.state.vo_x
            self.state.fused_y = self.state.vo_y
            self.state.fused_z = self.state.vo_z

            self.state.fused_confidence = min(
                self.state.gps_confidence,
                self.state.vo_confidence
            )

        # --------------------------------------------
        # PRIORITY 2
        # MAP + VO
        # --------------------------------------------

        elif map_ok and vo_ok:

            self.state.source = "MAP+VO"

            self.state.fused_lat = self.state.map_lat
            self.state.fused_lon = self.state.map_lon
            self.state.fused_alt = self.state.gps_alt

            self.state.fused_roll = self.state.vo_roll
            self.state.fused_pitch = self.state.vo_pitch
            self.state.fused_yaw = self.state.vo_yaw

            self.state.fused_x = self.state.vo_x
            self.state.fused_y = self.state.vo_y
            self.state.fused_z = self.state.vo_z

            self.state.fused_confidence = min(
                self.state.map_confidence,
                self.state.vo_confidence
            )

        # --------------------------------------------
        # PRIORITY 3
        # GPS ONLY
        # --------------------------------------------

        elif gps_ok:

            self.state.source = "GPS"

            self.state.fused_lat = self.state.gps_lat
            self.state.fused_lon = self.state.gps_lon
            self.state.fused_alt = self.state.gps_alt

            self.state.fused_roll = self.state.vo_roll
            self.state.fused_pitch = self.state.vo_pitch
            self.state.fused_yaw = self.state.vo_yaw

            self.state.fused_confidence = self.state.gps_confidence

        # --------------------------------------------
        # PRIORITY 4
        # MAP ONLY
        # --------------------------------------------

        elif map_ok:

            self.state.source = "MAP"

            self.state.fused_lat = self.state.map_lat
            self.state.fused_lon = self.state.map_lon
            self.state.fused_alt = self.state.gps_alt

            self.state.fused_roll = self.state.vo_roll
            self.state.fused_pitch = self.state.vo_pitch
            self.state.fused_yaw = self.state.vo_yaw

            self.state.fused_confidence = self.state.map_confidence

        # --------------------------------------------
        # PRIORITY 5
        # VO ONLY
        # --------------------------------------------

        elif vo_ok:

            self.state.source = "VO"

            self.state.fused_x = self.state.vo_x
            self.state.fused_y = self.state.vo_y
            self.state.fused_z = self.state.vo_z

            self.state.fused_roll = self.state.vo_roll
            self.state.fused_pitch = self.state.vo_pitch
            self.state.fused_yaw = self.state.vo_yaw

            self.state.fused_confidence = self.state.vo_confidence

        # --------------------------------------------
        # NOTHING AVAILABLE
        # --------------------------------------------

        else:

            self.state.source = "NONE"

            self.state.fused_confidence = 0.0

        # --------------------------------------------
        # Velocity
        # --------------------------------------------

        self.state.fused_vx = (
            self.state.fused_x - self.prev_x
        ) / dt

        self.state.fused_vy = (
            self.state.fused_y - self.prev_y
        ) / dt

        self.state.fused_vz = (
            self.state.fused_z - self.prev_z
        ) / dt

        self.prev_x = self.state.fused_x
        self.prev_y = self.state.fused_y
        self.prev_z = self.state.fused_z

        return self.state
            # -------------------------------------------------
    # GPS TO LOCAL NED
    # -------------------------------------------------

    def gps_to_local(self):

        if self.home_lat is None:
            return

        dlat = math.radians(
            self.state.fused_lat - self.home_lat
        )

        dlon = math.radians(
            self.state.fused_lon - self.home_lon
        )

        lat0 = math.radians(self.home_lat)

        north = dlat * self.EARTH_RADIUS

        east = (
            dlon *
            self.EARTH_RADIUS *
            math.cos(lat0)
        )

        down = self.home_alt - self.state.fused_alt

        self.state.fused_x = north
        self.state.fused_y = east
        self.state.fused_z = down

    # -------------------------------------------------
    # EULER TO QUATERNION
    # -------------------------------------------------

    def update_quaternion(self):

        roll = self.state.fused_roll
        pitch = self.state.fused_pitch
        yaw = self.state.fused_yaw

        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)

        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)

        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)

        self.state.fused_qw = (
            cr * cp * cy +
            sr * sp * sy
        )

        self.state.fused_qx = (
            sr * cp * cy -
            cr * sp * sy
        )

        self.state.fused_qy = (
            cr * sp * cy +
            sr * cp * sy
        )

        self.state.fused_qz = (
            cr * cp * sy -
            sr * sp * cy
        )
        

    # -------------------------------------------------
    # FINALIZE STATE
    # -------------------------------------------------

    def finalize(self):

        self.gps_to_local()

        self.update_quaternion()

        self.state.timestamp = time.time()
            # -------------------------------------------------
    # RESET
    # -------------------------------------------------

    def reset(self):

        self.state = NavigationState()

        self.last_time = time.time()

        self.prev_x = 0.0
        self.prev_y = 0.0
        self.prev_z = 0.0

        self.home_lat = None
        self.home_lon = None
        self.home_alt = None

        self.state.reset_counter += 1

    # -------------------------------------------------
    # STATUS
    # -------------------------------------------------

    def print_status(self):

        print("--------------------------------------------")
        print("Navigation EKF")
        print("--------------------------------------------")

        print("Source :", self.state.source)

        print(
            "GPS:",
            self.gps_healthy()
        )

        print(
            "VO :",
            self.vo_healthy()
        )

        print(
            "MAP:",
            self.map_healthy()
        )

        print("--------------------------------------------")

        print(
            "GPS :",
            self.state.gps_lat,
            self.state.gps_lon,
            self.state.gps_alt
        )

        print(
            "MAP :",
            self.state.map_lat,
            self.state.map_lon
        )

        print(
            "VO :",
            self.state.vo_x,
            self.state.vo_y,
            self.state.vo_z
        )

        print("--------------------------------------------")

        print(
            "FUSED GLOBAL :",
            self.state.fused_lat,
            self.state.fused_lon,
            self.state.fused_alt
        )

        print(
            "FUSED LOCAL :",
            self.state.fused_x,
            self.state.fused_y,
            self.state.fused_z
        )

        print(
            "VELOCITY :",
            self.state.fused_vx,
            self.state.fused_vy,
            self.state.fused_vz
        )

        print("--------------------------------------------")
