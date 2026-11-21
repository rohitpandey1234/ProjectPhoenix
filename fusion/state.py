from dataclasses import dataclass


@dataclass
class NavigationState:

    # =====================================================
    # GPS
    # =====================================================

    gps_lat: float = 0.0
    gps_lon: float = 0.0
    gps_alt: float = 0.0

    gps_fix: int = 0
    gps_satellites: int = 0
    gps_hdop: float = 99.0
    gps_confidence: float = 0.0

    # =====================================================
    # VISUAL ODOMETRY
    # =====================================================

    vo_x: float = 0.0
    vo_y: float = 0.0
    vo_z: float = 0.0

    vo_vx: float = 0.0
    vo_vy: float = 0.0
    vo_vz: float = 0.0

    vo_roll: float = 0.0
    vo_pitch: float = 0.0
    vo_yaw: float = 0.0

    vo_confidence: float = 0.0

    # =====================================================
    # MAP LOCALIZATION
    # =====================================================

    map_lat: float = 0.0
    map_lon: float = 0.0
    map_alt: float = 0.0

    map_x: float = 0.0
    map_y: float = 0.0
    map_z: float = 0.0

    map_tile_x: int = 0
    map_tile_y: int = 0

    map_matches: int = 0
    map_inliers: int = 0
    map_confidence: float = 0.0

    # =====================================================
    # FUSED NAVIGATION
    # =====================================================

    # Global Position
    fused_lat: float = 0.0
    fused_lon: float = 0.0
    fused_alt: float = 0.0

    # Local Position (meters)
    fused_x: float = 0.0
    fused_y: float = 0.0
    fused_z: float = 0.0

    # Local Velocity (m/s)
    fused_vx: float = 0.0
    fused_vy: float = 0.0
    fused_vz: float = 0.0

    # Euler Angles
    fused_roll: float = 0.0
    fused_pitch: float = 0.0
    fused_yaw: float = 0.0

    # Quaternion (w,x,y,z)
    fused_qw: float = 1.0
    fused_qx: float = 0.0
    fused_qy: float = 0.0
    fused_qz: float = 0.0

    fused_confidence: float = 0.0

    # =====================================================
    # SOURCE
    # =====================================================

    source: str = "NONE"

    # Possible values:
    # NONE
    # GPS
    # VO
    # MAP
    # GPS+VO
    # MAP+VO

    # =====================================================
    # VEHICLE
    # =====================================================

    armed: bool = False
    mode: str = ""

    # =====================================================
    # TIMESTAMP
    # =====================================================

    timestamp: float = 0.0

    # =====================================================
    # RESET COUNTER
    # Required by MAVLink ODOMETRY
    # =====================================================

    reset_counter: int = 0
