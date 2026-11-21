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

    # Tile descriptor cache
    self.cache = {}

    # Debug information
    self.last_tile = None
    self.last_confidence = 0.0
    self.last_matches = 0
    self.last_inliers = 0
