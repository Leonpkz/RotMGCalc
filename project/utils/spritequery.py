import json
import os

SPRITE_SHEET_JSON = os.environ.get('SPRITE_SHEET_JSON')

with open(SPRITE_SHEET_JSON) as f:
    sprites = json.load(f)

for row in sprites:
    print(row)
