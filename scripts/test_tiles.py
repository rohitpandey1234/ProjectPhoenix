from map.tiles import TileManager

tiles = TileManager(18)

x, y = tiles.gps_to_tile(

    17.443210,

    78.348100

)

tiles.print_tile(x, y)

print()

print("Neighbors")

print()

for tile in tiles.neighbors(x, y):

    print(tile)
