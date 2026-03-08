
class Tilemap:
    def __init__(self, assets, tile_size=8):
        self.tile_size = tile_size
        self.tilemap = {}
        
        for i in range(10):
            self.tilemap[str(3 + i) + ';10'] = {'type': 'cliff', 'variant': 1, 'pos': (3 + i, 10)}
            self.tilemap['10;' + str(i + 5)] = {'type': 'cliff', 'variant': 1, 'pos': (10, i + 5)}

        def render(self, surf):
            for loc in self.tilemap:
                tile = self.tilemap[loc]
                surf.blit(self.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size))
