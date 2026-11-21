from pymavlink import mavutil
import time


class MAVLinkBridge:

    def __init__(
        self,
        connection_string="udp:127.0.0.1:14551"
    ):

        print("------------------------------------")
        print("Connecting to ArduPilot...")
        print("------------------------------------")

        self.master = mavutil.mavlink_connection(
            connection_string
        )

        print("Waiting for heartbeat...")

        self.master.wait_heartbeat()

        print("------------------------------------")
        print("Heartbeat Received")
        print("------------------------------------")

        print(
            "System ID :",
            self.master.target_system
        )

        print(
            "Component ID :",
            self.master.target_component
        )

        # Transmission timing
        self.last_send = 0.0
        self.last_heartbeat = 0.0
        self.send_rate = 30.0

    # -------------------------------------------------
    # HEARTBEAT TO FC
    # -------------------------------------------------

    def send_heartbeat(self):

        self.master.mav.heartbeat_send(

            mavutil.mavlink.MAV_TYPE_ONBOARD_CONTROLLER,

            mavutil.mavlink.MAV_AUTOPILOT_INVALID,

            0,

            0,

            0

        )

    # -------------------------------------------------
    # GPS
    # -------------------------------------------------

    def get_gps(self):

        gps = self.master.recv_match(
            type="GPS_RAW_INT",
            blocking=False
        )

        pos = self.master.recv_match(
            type="GLOBAL_POSITION_INT",
            blocking=False
        )

        if gps is None or pos is None:
            return None

        return {

            "lat": pos.lat / 1e7,

            "lon": pos.lon / 1e7,

            "alt": pos.relative_alt / 1000.0,

            "gps_fix": gps.fix_type,

            "satellites": gps.satellites_visible,

            "hdop": gps.eph / 100.0

        }

    # -------------------------------------------------
    # ATTITUDE
    # -------------------------------------------------

    def get_attitude(self):

        msg = self.master.recv_match(
            type="ATTITUDE",
            blocking=False
        )

        if msg is None:
            return None

        return {

            "roll": msg.roll,

            "pitch": msg.pitch,

            "yaw": msg.yaw

        }

    # -------------------------------------------------
    # FLIGHT MODE
    # -------------------------------------------------

    def get_mode(self):

        msg = self.master.recv_match(
            type="HEARTBEAT",
            blocking=False
        )

        if msg is None:
            return None

        return mavutil.mode_string_v10(msg)
            # -------------------------------------------------
    # ARM
    # -------------------------------------------------

    def arm(self):

        print("Arming Vehicle...")

        self.master.arducopter_arm()

        self.master.motors_armed_wait()

        print("Vehicle Armed")

    # -------------------------------------------------
    # DISARM
    # -------------------------------------------------

    def disarm(self):

        print("Disarming Vehicle...")

        self.master.arducopter_disarm()

        self.master.motors_disarmed_wait()

        print("Vehicle Disarmed")

    # -------------------------------------------------
    # SET MODE
    # -------------------------------------------------

    def set_mode(self, mode):

        mapping = self.master.mode_mapping()

        if mapping is None:

            print("Unable to get mode mapping")

            return False

        if mode not in mapping:

            print("Unknown Flight Mode :", mode)

            return False

        self.master.set_mode(

            mapping[mode]

        )

        print("Mode Changed :", mode)

        return True

    # -------------------------------------------------
    # TAKEOFF
    # -------------------------------------------------

    def takeoff(self, altitude):

        print(f"Takeoff Command : {altitude} m")

        self.master.mav.command_long_send(

            self.master.target_system,

            self.master.target_component,

            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,

            0,

            0,

            0,

            0,

            0,

            0,

            0,

            altitude

        )

    # -------------------------------------------------
    # LAND
    # -------------------------------------------------

    def land(self):

        self.set_mode("LAND")

    # -------------------------------------------------
    # RTL
    # -------------------------------------------------

    def rtl(self):

        self.set_mode("RTL")

    # -------------------------------------------------
    # GUIDED
    # -------------------------------------------------

    def guided(self):

        self.set_mode("GUIDED")

    # -------------------------------------------------
    # LOITER
    # -------------------------------------------------

    def loiter(self):

        self.set_mode("LOITER")

    # -------------------------------------------------
    # CONNECTION STATUS
    # -------------------------------------------------

    def connected(self):

        return self.master is not None

    # -------------------------------------------------
    # WAIT HEARTBEAT
    # -------------------------------------------------

    def wait_heartbeat(self):

        self.master.wait_heartbeat()
            # -------------------------------------------------
    # SEND NAVIGATION TO ARDUPILOT
    # -------------------------------------------------

    def send_navigation(self, state):

        now = time.time()

        # -----------------------------
        # Limit transmission rate
        # -----------------------------

        if (now - self.last_send) < (1.0 / self.send_rate):
            return

        self.last_send = now

        # -----------------------------
        # Send heartbeat every second
        # -----------------------------

        if (now - self.last_heartbeat) >= 1.0:

            self.send_heartbeat()

            self.last_heartbeat = now

        timestamp = int(now * 1e6)

        # -----------------------------
        # Vision Position Estimate
        # -----------------------------

        self.master.mav.vision_position_estimate_send(

            timestamp,

            state.fused_x,

            state.fused_y,

            state.fused_z,

            state.fused_roll,

            state.fused_pitch,

            state.fused_yaw

        )

    # -------------------------------------------------
    # PRINT NAVIGATION
    # -------------------------------------------------

    def print_navigation(self, state):

        print("--------------------------------------")

        print("Navigation")

        print("--------------------------------------")

        print("Source :", state.source)

        print()

        print(
            "Position :",
            round(state.fused_x, 2),
            round(state.fused_y, 2),
            round(state.fused_z, 2)
        )

        print(
            "Attitude :",
            round(state.fused_roll, 2),
            round(state.fused_pitch, 2),
            round(state.fused_yaw, 2)
        )

        print()

        print(
            "Confidence :",
            round(state.fused_confidence, 2)
        )

        print("--------------------------------------")      
            # -------------------------------------------------
    # RECEIVE ANY MESSAGE
    # -------------------------------------------------

    def receive(self, message_type=None, blocking=False):

        if message_type is None:

            return self.master.recv_match(
                blocking=blocking
            )

        return self.master.recv_match(

            type=message_type,

            blocking=blocking

        )

    # -------------------------------------------------
    # CHECK CONNECTION
    # -------------------------------------------------

    def is_connected(self):

        try:

            return (
                self.master.target_system != 0
            )

        except Exception:

            return False

    # -------------------------------------------------
    # FLUSH MAVLINK BUFFER
    # -------------------------------------------------

    def flush(self):

        while True:

            msg = self.master.recv_match(
                blocking=False
            )

            if msg is None:

                break

    # -------------------------------------------------
    # PRINT CONNECTION INFO
    # -------------------------------------------------

    def print_connection(self):

        print("------------------------------------")

        print("MAVLink Connection")

        print("------------------------------------")

        print(
            "System ID :",
            self.master.target_system
        )

        print(
            "Component ID :",
            self.master.target_component
        )

        print(
            "Connected :",
            self.is_connected()
        )

        print("------------------------------------")

    # -------------------------------------------------
    # CLOSE CONNECTION
    # -------------------------------------------------

    def close(self):

        print()

        print("------------------------------------")
        print("Closing MAVLink Connection")
        print("------------------------------------")

        try:

            self.master.close()

        except Exception:

            pass

        print("Connection Closed")  
