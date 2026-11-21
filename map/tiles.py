import mercantile


class TileManager:

    def __init__(self, zoom=18):

        self.zoom = zoom

        self.current_tile = None

    # -------------------------------------------------
    # GPS → Tile
    # -------------------------------------------------

    def gps_to_tile(self, latitude, longitude):

        tile = mercantile.tile(

            longitude,

            latitude,

            self.zoom

        )

        self.current_tile = tile

        return tile.x, tile.y

    # -------------------------------------------------
    # Tile → GPS Bounds
    # -------------------------------------------------

    def tile_bounds(

        self,

        x,

        y,

        zoom=None

    ):

        if zoom is None:

            zoom = self.zoom

        bounds = mercantile.bounds(

            x,

            y,

            zoom

        )

        return {

            "north": bounds.north,

            "south": bounds.south,

            "east": bounds.east,

            "west": bounds.west

        }

    # -------------------------------------------------
    # Tile Center
    # -------------------------------------------------

    def tile_center(

        self,

        x,

        y

    ):

        b = mercantile.bounds(

            x,

            y,

            self.zoom

        )

        lat = (b.north + b.south) / 2.0

        lon = (b.east + b.west) / 2.0

        return lat, lon

    # -------------------------------------------------
    # Neighbor Tiles
    # -------------------------------------------------

    def neighbors(

        self,

        x,

        y

    ):

        return self.search_tiles(

            x,

            y,

            1

        )

    # -------------------------------------------------
    # Variable Search Radius
    # -------------------------------------------------

    def search_tiles(

        self,

        x,

        y,

        radius

    ):

        tile_list = []

        for yy in range(

            y - radius,

            y + radius + 1

        ):

            for xx in range(

                x - radius,

                x + radius + 1

            ):

                tile_list.append(

                    (xx, yy)

                )

        return tile_list

    # -------------------------------------------------
    # Update Tile From Position
    # -------------------------------------------------

    def update_tile_from_motion(

        self,

        latitude,

        longitude

    ):

        return self.gps_to_tile(

            latitude,

            longitude

        )

    # -------------------------------------------------

    def print_tile(

        self,

        x,

        y

    ):

        print("--------------------------------")

        print("Current Tile")

        print(f"Zoom : {self.zoom}")

        print(f"X    : {x}")

        print(f"Y    : {y}")

        print("--------------------------------")
