import cv2
import time

from camera.webcam import Webcam

from vo.orb_vo import VisualOdometry

from map.loader import MapLoader
from map.tiles import TileManager
from map.localizer import MapLocalizer

from navigation.manager import NavigationManager

from mavlink.bridge import MAVLinkBridge


#######################################################
# CONFIGURATION
#######################################################

ZOOM = 18

CAMERA_ID = 0

MAP_FOLDER = "data/maps"

DISPLAY = True

#######################################################
def main():

    print("--------------------------------------")
    print("      PROJECT PHOENIX V2")
    print("--------------------------------------")
        ###################################################
    # CAMERA
    ###################################################

    camera = Webcam()

    ###################################################
    # VISUAL ODOMETRY
    ###################################################

    vo = VisualOdometry()

    ###################################################
    # MAP
    ###################################################

    tiles = TileManager(ZOOM)

    loader = MapLoader(
        MAP_FOLDER,
        tiles
    )

    localizer = MapLocalizer()

    ###################################################
    # NAVIGATION
    ###################################################

    navigation = NavigationManager()

    ###################################################
    # MAVLINK
    ###################################################

    bridge = MAVLinkBridge()

    ###################################################
    # SHARED STATE
    ###################################################

    state = navigation.ekf.state

    ###################################################
    # SEARCH
    ###################################################

    current_tile_x = None
    current_tile_y = None

    search_radius = 1

    print()

    print("All Modules Initialized")

    print()
        ###################################################
    # MAIN LOOP
    ###################################################

    while True:

        frame = camera.read()

        if frame is None:

            continue
                    ###################################################
        # VISUAL ODOMETRY
        ###################################################

        vo_result = vo.process(frame)

        pose = vo_result["pose"]

        if pose is not None:

            state.vo_x = pose["x"]
            state.vo_y = pose["y"]
            state.vo_z = pose["z"]

            state.vo_vx = pose["vx"]
            state.vo_vy = pose["vy"]
            state.vo_vz = pose["vz"]

            state.vo_roll = pose["roll"]
            state.vo_pitch = pose["pitch"]
            state.vo_yaw = pose["yaw"]

            state.vo_confidence = pose["confidence"]
                    ###################################################
        # GPS
        ###################################################

        gps = bridge.get_gps()

        if gps is not None:

            state.gps_lat = gps["lat"]
            state.gps_lon = gps["lon"]
            state.gps_alt = gps["alt"]

            state.gps_fix = gps["gps_fix"]
            state.gps_satellites = gps["satellites"]
            state.gps_hdop = gps["hdop"]
                    ###################################################
        # ATTITUDE
        ###################################################

        attitude = bridge.get_attitude()

        if attitude is not None:

            state.vo_roll = attitude["roll"]
            state.vo_pitch = attitude["pitch"]

            if pose is None:

                state.vo_yaw = attitude["yaw"]
                        ###################################################
        # FLIGHT MODE
        ###################################################

        mode = bridge.get_mode()

        if mode is not None:

            state.mode = mode
                    ###################################################
        # SELECT CURRENT TILE
        ###################################################

        if gps is not None:

            current_tile_x, current_tile_y = tiles.gps_to_tile(

                state.gps_lat,

                state.gps_lon

            )

        elif current_tile_x is None:

            current_tile_x = state.map_tile_x

            current_tile_y = state.map_tile_y

        ###################################################
        # LOAD NEIGHBOR TILES
        ###################################################

        neighbor_tiles = loader.preload_neighbors(

            ZOOM,

            current_tile_x,

            current_tile_y,

            radius=search_radius

        )

        ###################################################
        # MAP LOCALIZATION
        ###################################################

        best_result = None

        best_confidence = -1.0

        best_tile = None

        for (tx, ty), tile in neighbor_tiles.items():

            result = localizer.localize(

                frame,

                f"{tx}_{ty}",

                tile["image"],

                tile["bounds"]

            )

            if result is None:

                continue

            if result["confidence"] > best_confidence:

                best_result = result

                best_confidence = result["confidence"]

                best_tile = (tx, ty)

        ###################################################
        # UPDATE MAP STATE
        ###################################################

        if best_result is not None:

            current_tile_x = best_tile[0]

            current_tile_y = best_tile[1]

            state.map_tile_x = current_tile_x

            state.map_tile_y = current_tile_y

            state.map_lat = best_result["latitude"]

            state.map_lon = best_result["longitude"]

            state.map_confidence = best_result["confidence"]

            state.map_matches = best_result["matches"]

            state.map_inliers = best_result["inliers"]

            if "altitude" in best_result:

                state.map_alt = best_result["altitude"]

            if "x" in best_result:

                state.map_x = best_result["x"]

            if "y" in best_result:

                state.map_y = best_result["y"]

            if "z" in best_result:

                state.map_z = best_result["z"]

            search_radius = localizer.search_radius(

                best_result["confidence"]

            )

        else:

            search_radius = min(

                search_radius + 1,

                4

            )

        ###################################################
        # NAVIGATION FUSION
        ###################################################

        state = navigation.update()

        ###################################################
        # SEND TO ARDUPILOT
        ###################################################

        bridge.send_navigation(

            state

        )
                ###################################################
        # DISPLAY
        ###################################################

        display = vo_result["frame"].copy()

        cv2.putText(

            display,

            f"MODE : {state.mode}",

            (20,30),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (0,255,0),

            2

        )

        cv2.putText(

            display,

            f"SOURCE : {state.source}",

            (20,60),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (0,255,0),

            2

        )

        cv2.putText(

            display,

            f"GPS FIX : {state.gps_fix}",

            (20,90),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (255,255,0),

            2

        )

        cv2.putText(

            display,

            f"SAT : {state.gps_satellites}",

            (20,120),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (255,255,0),

            2

        )

        cv2.putText(

            display,

            f"HDOP : {state.gps_hdop:.2f}",

            (20,150),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (255,255,0),

            2

        )

        cv2.putText(

            display,

            f"VO MATCHES : {vo_result['matches']}",

            (20,180),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (0,255,255),

            2

        )

        cv2.putText(

            display,

            f"VO CONF : {state.vo_confidence:.2f}",

            (20,210),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (0,255,255),

            2

        )

        cv2.putText(

            display,

            f"MAP CONF : {state.map_confidence:.2f}",

            (20,240),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (0,255,255),

            2

        )

        cv2.putText(

            display,

            f"TILE : {current_tile_x}, {current_tile_y}",

            (20,270),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (255,200,0),

            2

        )

        ###################################################
        # FUSED POSITION
        ###################################################

        cv2.putText(

            display,

            f"GPS : {state.gps_lat:.6f}, {state.gps_lon:.6f}",

            (20,310),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.55,

            (255,255,255),

            2

        )

        cv2.putText(

            display,

            f"MAP : {state.map_lat:.6f}, {state.map_lon:.6f}",

            (20,340),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.55,

            (0,255,0),

            2

        )

        cv2.putText(

            display,

            f"FUSED : {state.fused_lat:.6f}, {state.fused_lon:.6f}",

            (20,370),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.55,

            (0,255,255),

            2

        )

        cv2.putText(

            display,

            f"LOCAL XYZ : {state.fused_x:.2f}  {state.fused_y:.2f}  {state.fused_z:.2f}",

            (20,400),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.55,

            (255,255,255),

            2

        )

        cv2.putText(

            display,

            f"VEL XYZ : {state.fused_vx:.2f}  {state.fused_vy:.2f}  {state.fused_vz:.2f}",

            (20,430),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.55,

            (255,255,255),

            2

        )

        ###################################################
        # SHOW WINDOW
        ###################################################

        if DISPLAY:

            cv2.imshow(

                "PROJECT PHOENIX",

                display

            )

        ###################################################
        # KEYBOARD
        ###################################################

        key = cv2.waitKey(1) & 0xFF

        if key == 27:

            break

        elif key == ord("a"):

            bridge.arm()

        elif key == ord("g"):

            bridge.guided()

        elif key == ord("l"):

            bridge.land()

        elif key == ord("r"):

            bridge.rtl()

        elif key == ord("o"):

            bridge.loiter()

        elif key == ord("t"):

            bridge.takeoff(10)
            ###################################################
    # SHUTDOWN
    ###################################################

    print()

    print("----------------------------------------")
    print("Closing Project Phoenix...")
    print("----------------------------------------")

    try:

        camera.release()

    except Exception:

        pass

    try:

        bridge.close()

    except Exception:

        pass

    cv2.destroyAllWindows()

    print("Project Phoenix Closed Successfully")


###########################################################


if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print()

        print("----------------------------------------")
        print("Keyboard Interrupt")
        print("----------------------------------------")

    except Exception as e:

        print()

        print("----------------------------------------")
        print("PROJECT PHOENIX CRASHED")
        print("----------------------------------------")

        print(e)

        raise
            
