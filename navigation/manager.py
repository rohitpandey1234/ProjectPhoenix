from fusion.ekf import NavigationEKF


class NavigationManager:

    def __init__(self):

        self.ekf = NavigationEKF()

        self.last_source = "GPS"

    # -------------------------------------------------
    # Main Navigation Update
    # -------------------------------------------------

    def update(self):

        state = self.ekf.update()

        if state.source != self.last_source:

            print("--------------------------------")
            print("Navigation Source Changed")
            print(
                self.last_source,
                "-->",
                state.source
            )
            print("--------------------------------")

            self.last_source = state.source

        return state

    # -------------------------------------------------
    # GPS Monitor
    # -------------------------------------------------

    def gps_available(self):

        return self.ekf.gps_healthy()

    # -------------------------------------------------
    # VO Monitor
    # -------------------------------------------------

    def vo_available(self):

        return self.ekf.vo_healthy()

    # -------------------------------------------------
    # MAP Monitor
    # -------------------------------------------------

    def map_available(self):

        return self.ekf.map_healthy()

    # -------------------------------------------------
    # Current Source
    # -------------------------------------------------

    def source(self):

        return self.ekf.state.source

    # -------------------------------------------------
    # GPS Jammer Detection (Version 1)
    # -------------------------------------------------

    def gps_jammed(self):

        if self.ekf.state.gps_fix < 3:

            return True

        if self.ekf.state.gps_hdop > 4.0:

            return True

        if self.ekf.state.gps_satellites < 5:

            return True

        return False

    # -------------------------------------------------
    # Print Status
    # -------------------------------------------------

    def print_status(self):

        print("------------------------------------")
        print("Navigation Manager")
        print("------------------------------------")

        print(
            "Source :",
            self.source()
        )

        print(
            "GPS Healthy :",
            self.gps_available()
        )

        print(
            "VO Healthy :",
            self.vo_available()
        )

        print(
            "MAP Healthy :",
            self.map_available()
        )

        print(
            "GPS Jammed :",
            self.gps_jammed()
        )

        print("------------------------------------")
