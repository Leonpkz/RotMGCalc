import struct
import json
from PIL import Image

with open(r"c:\Code\RotMGCalc\localfiles\xml\spritesheetf.xml", "rb") as f:

objectMapWidth, objectMapHeight = Image.open(r"c:\Code\RotMGCalc\localfiles\spritesheets\mapObjects.png").size

size = len(f.read())
atlas = {}

for offset in range(0, size - 32, 4):
    # 8 ints
    block = struct.unpack_from("<8I", data, offset)
    # first 4 floats
    floats = struct.unpack_from("<4f", data, offset)

    type_id = block[4]
    if type_id != 0 and type_id not in atlas:
        x, y, w, h = floats

        x_px = int(x * objectMapWidth)
        y_px = int(y * objectMapHeight)
        w_px = int(w * objectMapWidth)
        h_px = int(h * objectMapHeight)

        atlas[hex(type_id)] = {
            "x": x_px,
            "y": y_px,
            "w": w_px,
            "h": h_px,
            "extra": [hex(block[5]), hex(block[6]), hex(block[7])],
            "offset": hex(offset)
        }

# write lookup to JSON
with open("sprite_lookup.json", "w") as out:
    json.dump(atlas, out, indent=2)
