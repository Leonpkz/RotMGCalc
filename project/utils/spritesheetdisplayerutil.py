import json
from collections import defaultdict

# Load the JSON
with open("spritesheet.json", "r") as f:
    data = json.load(f)

# Map: atlasId -> list of sprites
atlas_sprites = defaultdict(list)

# Regular sprites
for sheet in data["spritesheets"]:
    atlas_id = sheet["atlasId"]
    for sprite in sheet["sprites"]:
        atlas_sprites[atlas_id].append(sprite)

# Animated sprites (optional)
for anim in data["animated_sprites"]:
    atlas_id = anim["sprite"]["atlasId"]
    atlas_sprites[atlas_id].append(anim["sprite"])

# Now you can query:
for atlas_id, sprites in atlas_sprites.items():
    print(f"Atlas {atlas_id} has {len(sprites)} sprites")