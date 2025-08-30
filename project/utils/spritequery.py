import json

# todo - set as environment variable
spriteSheetJson = 'spritesheet.json'

with open(spriteSheetJson) as f:
    sprites = json.load(f)

for row in sprites:
    print(row)
