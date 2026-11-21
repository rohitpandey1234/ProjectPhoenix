import os
import cv2


class MapLoader:

    def __init__(self, map_folder, tile_manager):

        self.map_folder = map_folder

        self.tiles = tile_manager

        self.cache = {}

        self.max_cache = 100

    # -------------------------------------------------

    def tile_filename(self, zoom, x, y):

        return os.path.join(

            self.map_folder,

            f"z{zoom}",

            f"x{x}_y{y}.png"

        )

    # -------------------------------------------------

    def load_tile(self, zoom, x, y):

        key = (zoom, x, y)

        if key in self.cache:

            return self.cache[key]

        filename = self.tile_filename(

            zoom,

            x,

            y

        )

        if not os.path.exists(filename):

            return None

        image = cv2.imread(filename)

        if image is None:

            return None

        self.cache[key] = image

        if len(self.cache) > self.max_cache:

            oldest = list(self.cache.keys())[0]

            del self.cache[oldest]

        return image

    # -------------------------------------------------

    def preload_neighbors(

        self,

        zoom,

        x,

        y,

        radius=1

    ):

        images = {}

        for dx in range(-radius, radius + 1):

            for dy in range(-radius, radius + 1):

                tx = x + dx
                ty = y + dy

                img = self.load_tile(

                    zoom,

                    tx,

                    ty

                )

                if img is None:

                    continue

                images[(tx, ty)] = {

                    "image": img,

                    "bounds": self.tiles.tile_bounds(

                        tx,

                        ty,

                        zoom

                    )

                }

        return images

    # -------------------------------------------------

    def clear_cache(self):

        self.cache.clear()
