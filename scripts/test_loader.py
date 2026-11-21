from map.loader import MapLoader

loader = MapLoader("data/maps")

image = loader.load_tile(

    18,

    188089,

    118135

)

print(image.shape)
