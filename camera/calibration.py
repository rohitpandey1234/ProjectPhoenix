import cv2
import numpy as np
import glob
import os


class CameraCalibration:

    def __init__(self):

        self.board_size = (9, 6)
        self.square_size = 1.0

        self.criteria = (
            cv2.TERM_CRITERIA_EPS +
            cv2.TERM_CRITERIA_MAX_ITER,
            30,
            0.001
        )

        self.objp = np.zeros(
            (self.board_size[0] * self.board_size[1], 3),
            np.float32
        )

        self.objp[:, :2] = np.mgrid[
            0:self.board_size[0],
            0:self.board_size[1]
        ].T.reshape(-1, 2)

        self.objpoints = []
        self.imgpoints = []

    def calibrate(self, image_folder):

        images = glob.glob(
            os.path.join(image_folder, "*.jpg")
        )

        if len(images) == 0:
            print("No calibration images found.")
            return

        image_size = None

        for filename in images:

            image = cv2.imread(filename)

            gray = cv2.cvtColor(
                image,
                cv2.COLOR_BGR2GRAY
            )

            image_size = gray.shape[::-1]

            found, corners = cv2.findChessboardCorners(
                gray,
                self.board_size,
                None
            )

            if found:

                self.objpoints.append(self.objp)

                refined = cv2.cornerSubPix(
                    gray,
                    corners,
                    (11, 11),
                    (-1, -1),
                    self.criteria
                )

                self.imgpoints.append(refined)

                cv2.drawChessboardCorners(
                    image,
                    self.board_size,
                    refined,
                    found
                )

                cv2.imshow("Calibration", image)
                cv2.waitKey(200)

        cv2.destroyAllWindows()

        if len(self.objpoints) < 10:

            print("Need at least 10 successful images.")

            return

        ret, K, dist, rvecs, tvecs = cv2.calibrateCamera(
            self.objpoints,
            self.imgpoints,
            image_size,
            None,
            None
        )

        np.save("data/calibration/camera_matrix.npy", K)
        np.save("data/calibration/dist_coeffs.npy", dist)

        print("\nCalibration Complete")
        print("---------------------------")
        print("Reprojection Error :", ret)
        print("\nCamera Matrix\n")
        print(K)

        print("\nDistortion\n")
        print(dist)
