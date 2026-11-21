import os
import math
import requests
import mercantile
from tqdm import tqdm

# =====================================================
# CONFIGURATION
# =====================================================

API_KEY = "l2ctx1fXjyMLZ4TTuBpT"

CENTER_LAT = -35.362699   
CENTER_LON = 149.165412

RADIUS_KM = 5      # 10 km x 10 km area

ZOOM = 18

SAVE_DIR = "data/maps"

# =====================================================

os.makedirs(SAVE_DIR, exist_ok=True)


def meters_to_deg(lat, meters):

    dlat = meters / 111320

    dlon = meters / (
        111320 *
        math.cos(math.radians(lat))
    )

    return dlat, dlon


dlat, dlon = meters_to_deg(
    CENTER_LAT,
    RADIUS_KM * 1000
)

north = CENTER_LAT + dlat
south = CENTER_LAT - dlat

east = CENTER_LON + dlon
west = CENTER_LON - dlon

tiles = list(

    mercantile.tiles(

        west,
        south,
        east,
        north,
        ZOOM

    )

)

print("-----------------------------------")
print("Tiles to download :", len(tiles))
print("-----------------------------------")

for tile in tqdm(tiles):

    folder = os.path.join(

        SAVE_DIR,

        f"z{tile.z}"

    )

    os.makedirs(folder, exist_ok=True)

    filename = os.path.join(

        folder,

        f"x{tile.x}_y{tile.y}.png"

    )

    if os.path.exists(filename):
        continue

    url = (
        f"https://api.maptiler.com/maps/satellite/"
        f"{tile.z}/{tile.x}/{tile.y}.jpg"
        f"?key={API_KEY}"
    )

    r = requests.get(url)

    if r.status_code != 200:

        print("Failed :", tile)

        continue

    with open(filename, "wb") as f:

        f.write(r.content)

print("-----------------------------------")
print("Download Finished")
print("-----------------------------------")
