import json
from sys import exception
import os
from collections import defaultdict
import SpriteSheetRoot

# spritesheetf.bin file extracted from game file
SPRITE_SHEET_BIN = os.environ.get('SPRITE_SHEET_BIN')
# spriteMapRequirements.json file
SPRITE_MAP_REQUIREMENTS = "spriteMapRequirements.json"

'''
This module considers the use of flatc (https://flatbuffers.dev/) to decode the binary file

This is done decoding the spritesheetf binary from the unity game files - if you are using the exalt extractor tool the 
file will be named spritesheetf.xml you can rename it to spritesheet.bin, and then using the sprites.fbs file provided 
you can decode the binary using the following command:

          ./flatc.exe --python sprites.fbs

This will generate the necessary python scripts used to map the spritesheet to a JSON. If the schema (sprites.fbs) 
changes in future you won't be able to decode the spritesheef file as the exact "table"s and "struct"s need to be known.

# TODO re-organise this as it would make more sense to have the flatbuffer extracted files in their own directory 
'''


# read binary file for spritesheet and return a dictionary containing the sprite data
def spriteToDict(sprite):
	# these are the functions from the decoded Schema
	position = sprite.Position()
	mask_position = sprite.MaskPosition()
	color = sprite.Color()

	# dict comprehension on position and color values, assigning them to their respective tag for JSON
	return {
		"position": [getattr(position, attr)() for attr in ['X', 'Y', 'H', 'W']],
		"mask_position": [getattr(mask_position, attr)() for attr in ['X', 'Y', 'W', 'H']],
		"color": [getattr(color, attr)() for attr in ['R', 'G', 'B', 'A']],
		"transparent": sprite.IsTransparent()
	}


def buildSpritesheetJson(sprite_sheet, allowed_sheet_names=None):
	# builds the json with all the required sprites
	result = []
	for i in range(sprite_sheet.SpritesLength()):
		sheet = sprite_sheet.Sprites(i)
		sheet_name = sheet.Name().decode("utf-8")

		if allowed_sheet_names is not None and sheet_name not in allowed_sheet_names:
			continue

		sprite_info = defaultdict(list)
		sprite_indices = defaultdict(list)

		# this value is just for logging purposes - it does not correspond to the XML or any gamefile value
		index_counter = 0

		for j in range(sheet.SpritesLength()):
			sprite = sheet.Sprites(j)

			current_index = index_counter
			index_counter += 1

			# specify what sprite width and height you want to export
			if not widthHeightParsing(sprite, requiredWidthHeight=(8.0, 8.0)):
				continue

			current_sprite = sprite.Name().decode("utf-8")
			sprite_info[current_sprite].append(spriteToDict(sprite))
			sprite_indices[current_sprite].append(current_index)

		result.append({
			"name": sheet_name,
			"atlasId": sheet.AtlasId(),
			"sprites": [
				{
					"name": name,
					"spriteLocation": [
						{**frame, "index": idx}
						for frame, idx in zip(frames, sprite_indices[name])
					]
				}
				for name, frames in sprite_info.items()
			]
		})

	return result



def loadSpritesheet(sprite_file_path):
	try:
		with open(sprite_file_path, "rb") as f:
			data = f.read()

		buffer = bytearray(data)
		sprite_sheet_root = SpriteSheetRoot.SpriteSheetRoot.GetRootAsSpriteSheetRoot(buffer, 0)
		return sprite_sheet_root
	except exception as error:
		print(f"Unable to find file path or failure to read file data, please validate file path and or the decoded "
		      f"Schema files - see exception - {error}")


def loadSpriteMapRequirements(sprite_requirements):
	try:
		with open(sprite_requirements) as f:
			sprite_map_reqs = json.load(f)
			if sprite_map_reqs is not None:
				return set(sprite_map_reqs)
	except:
		print("No spriteMapRequirements.json found, exporting all sprites")

''' 
this function allows you to parse the sprites by their width and height, which allows us to specifically export the 
sprites for gear in the game.
'''
def widthHeightParsing(sprite, requiredWidthHeight=(None, None)):
	position = sprite.Position()
	return position.W() == requiredWidthHeight[0] and position.H() == requiredWidthHeight[1]



if __name__ == "__main__":

	sprite_sheet = loadSpritesheet(SPRITE_SHEET_BIN)
	# load optional specified spritesheets
	spriteMapSet = loadSpriteMapRequirements(SPRITE_MAP_REQUIREMENTS)

	# returns a dictionary with all necessary values to map each sprite on the spritesheet
	sprite_sheet_dict = {
		"spritesheets": buildSpritesheetJson(sprite_sheet, spriteMapSet),
		"animated_sprites": [
			{
				"name": (anim := sprite_sheet.AnimatedSprites(i)).Name().decode("utf-8"),
				"index": anim.Index(),
				"set": anim.Set(),
				"direction": anim.Direction(),
				"action": anim.Action(),
				"sprite": spriteToDict(anim.Sprite())
			}
			for i in range(sprite_sheet.AnimatedSpritesLength())
			# specify what sprite width and height you want to export
			if widthHeightParsing(sprite_sheet.AnimatedSprites(i).Sprite(), requiredWidthHeight=(8.0, 8.0))
		]
	}

with open("../spritesheet.json", "w") as f:
	json.dump(sprite_sheet_dict, f, indent=2)
