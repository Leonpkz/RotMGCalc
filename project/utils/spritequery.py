import json
import os
import PIL.Image

# spritesheet extracted from spritemapping.py
SPRITE_SHEET_JSON = os.environ.get('SPRITE_SHEET_JSON')

with open(SPRITE_SHEET_JSON) as f:
    sprites = json.load(f)

for row in sprites:
    print(row)

spriteSheet = PIL.Image.open(r"c:\Code\RotMGCalc\localfiles\spritesheets\mapObjects.png")
# spriteSheet.alpha_composite(dest=spriteSheet)
spriteSheet.show()