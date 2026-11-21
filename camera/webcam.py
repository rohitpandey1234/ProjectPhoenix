import cv2


class Webcam:

    def __init__(self, camera_id=0):

        self.camera_id = camera_id

        self.cap = cv2.VideoCapture(camera_id)

        if not self.cap.isOpened():

            raise RuntimeError(

                f"Cannot open camera {camera_id}"

            )

        print("--------------------------------")
        print("Camera Initialized")
        print("--------------------------------")

    # ----------------------------------------

    def read(self):

        ret, frame = self.cap.read()

        if not ret:

            return None

        return frame

    # ----------------------------------------

    def width(self):

        return int(

            self.cap.get(

                cv2.CAP_PROP_FRAME_WIDTH

            )

        )

    # ----------------------------------------

    def height(self):

        return int(

            self.cap.get(

                cv2.CAP_PROP_FRAME_HEIGHT

            )

        )

    # ----------------------------------------

    def fps(self):

        return self.cap.get(

            cv2.CAP_PROP_FPS

        )

    # ----------------------------------------

    def release(self):

        self.cap.release()
