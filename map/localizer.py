import cv2
import numpy as np


class MapLocalizer:

    def __init__(self):

        self.orb = cv2.ORB_create(
            nfeatures=3000,
            scaleFactor=1.2,
            nlevels=8,
            edgeThreshold=31,
            firstLevel=0,
            WTA_K=2,
            scoreType=cv2.ORB_HARRIS_SCORE,
            patchSize=31,
            fastThreshold=15
        )

        self.matcher = cv2.BFMatcher(
            cv2.NORM_HAMMING,
            crossCheck=True
        )

        self.cache = {}

        self.last_tile = None
        self.last_confidence = 0.0
        self.last_matches = 0
        self.last_inliers = 0

    ####################################################
    # FEATURE EXTRACTION
    ####################################################

    def compute_features(
        self,
        image
    ):

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        keypoints, descriptors = self.orb.detectAndCompute(
            gray,
            None
        )

        return keypoints, descriptors

    ####################################################
    # TILE CACHE
    ####################################################

    def get_tile_features(
        self,
        tile_id,
        tile_image
    ):

        if tile_id in self.cache:

            return self.cache[tile_id]

        kp, des = self.compute_features(
            tile_image
        )

        self.cache[tile_id] = (
            kp,
            des
        )

        return kp, des

    ####################################################
    # MATCH CAMERA TO TILE
    ####################################################

    def match_tile(

        self,

        camera_frame,

        tile_id,

        tile_image

    ):

        cam_kp, cam_des = self.compute_features(
            camera_frame
        )

        map_kp, map_des = self.get_tile_features(
            tile_id,
            tile_image
        )

        if cam_des is None:
            return None

        if map_des is None:
            return None

        matches = self.matcher.match(
            cam_des,
            map_des
        )

        matches = sorted(
            matches,
            key=lambda m: m.distance
        )

        return {

            "camera_keypoints": cam_kp,

            "map_keypoints": map_kp,

            "matches": matches

        }

    ####################################################
    # ESTIMATE HOMOGRAPHY
    ####################################################

    def estimate_pose(

        self,

        match_result,

        camera_frame

    ):

        if match_result is None:
            return None

        matches = match_result["matches"]

        if len(matches) < 20:
            return None

        cam_kp = match_result["camera_keypoints"]
        map_kp = match_result["map_keypoints"]

        src_pts = np.float32(
            [
                cam_kp[m.queryIdx].pt
                for m in matches
            ]
        ).reshape(-1, 1, 2)

        dst_pts = np.float32(
            [
                map_kp[m.trainIdx].pt
                for m in matches
            ]
        ).reshape(-1, 1, 2)

        H, mask = cv2.findHomography(

            src_pts,

            dst_pts,

            cv2.RANSAC,

            5.0

        )

        if H is None:
            return None

        inliers = int(mask.sum())

        h, w = camera_frame.shape[:2]

        corners = np.float32(

            [

                [0, 0],

                [w, 0],

                [w, h],

                [0, h]

            ]

        ).reshape(-1, 1, 2)

        projected = cv2.perspectiveTransform(
            corners,
            H
        )

        center = projected.mean(axis=0)

        cx = float(center[0][0])
        cy = float(center[0][1])

        return {

            "homography": H,

            "center_pixel": (
                cx,
                cy
            ),

            "matches": len(matches),

            "inliers": inliers

        }

    ####################################################
    # CONFIDENCE
    ####################################################

    def confidence(

        self,

        pose

    ):

        if pose is None:
            return 0.0

        return float(

            pose["inliers"] /

            max(
                pose["matches"],
                1
            )

        )
            ####################################################
    # PIXEL TO GPS
    ####################################################

    def pixel_to_gps(

        self,

        tile_bounds,

        center_pixel,

        tile_size=256

    ):

        cx, cy = center_pixel

        west = tile_bounds["west"]
        east = tile_bounds["east"]

        north = tile_bounds["north"]
        south = tile_bounds["south"]

        lon = west + (cx / tile_size) * (east - west)

        lat = north - (cy / tile_size) * (north - south)

        return lat, lon

    ####################################################
    # COMPLETE LOCALIZATION
    ####################################################

    def localize(

        self,

        camera_frame,

        tile_id,

        tile_image,

        tile_bounds

    ):

        result = self.match_tile(

            camera_frame,

            tile_id,

            tile_image

        )

        if result is None:
            return None

        pose = self.estimate_pose(

            result,

            camera_frame

        )

        if pose is None:
            return None

        confidence = self.confidence(
            pose
        )

        latitude, longitude = self.pixel_to_gps(

            tile_bounds,

            pose["center_pixel"]

        )

        self.last_tile = tile_id
        self.last_confidence = confidence
        self.last_matches = pose["matches"]
        self.last_inliers = pose["inliers"]

        return {

            "tile_id": tile_id,

            "latitude": latitude,

            "longitude": longitude,

            "confidence": confidence,

            "center_pixel": pose["center_pixel"],

            "matches": pose["matches"],

            "inliers": pose["inliers"],

            "homography": pose["homography"]

        }

    ####################################################
    # SEARCH RADIUS
    ####################################################

    def search_radius(

        self,

        confidence

    ):

        if confidence >= 0.80:

            return 0

        elif confidence >= 0.60:

            return 1

        elif confidence >= 0.40:

            return 2

        else:

            return 3

    ####################################################
    # CACHE
    ####################################################

    def clear_cache(

        self

    ):

        self.cache.clear()
