import json
from collections import defaultdict

import flatbuffers
import AnimatedSpriteSheet, SpriteSheet, SpriteSheetRoot, Sprite, Position, Color

# todo - set as environment variable
filepath = r'C:\Code\exalt-extractor-main\output\xml\spritesheetf.bin'

'''
This module considers the use of flatc (https://flatbuffers.dev/) to decode the binary file

This is done decoding the spritesheetf binary from the unity game files - if you are using the exalt extractor tool the 
file will be named spritesheetf.xml you can rename the file, and then using the sprites.fbs file provided you can 
generate the binary file using the following command:

          ./flatc.exe --python sprites.fbs

This will generate the necessary python scripts used to map the spritesheet to a JSON, if the schema (sprites.fbs) 
changes in future you won't be able to decode the spritesheef file as the exact "table" and "struct" needs to be known. 
'''

# read binary file for spritesheet and return a dictionary containing the sprite data
def spriteToDict(sprite):
	pos = sprite.Position()
	mask_pos = sprite.MaskPosition()
	color = sprite.Color()

	# list comprehension on position and color values decreased file size by 20MB
	return {
		"position": [getattr(pos, attr)() for attr in ['X', 'Y', 'W', 'H']],
		"mask_position": [getattr(mask_pos, attr)() for attr in ['X', 'Y', 'W', 'H']],
		"color": [getattr(color, attr)() for attr in ['R', 'G', 'B', 'A']],
		"transparent": sprite.IsTransparent()
	}


def buildSpritesheetJson(root):

	# TODO - refactor for readability
	return [
		{
			"name": sheet.Name().decode('utf-8'),
			"atlasId": sheet.AtlasId(),
			"sprites": [
				{
					"name": sprite_name,
					"frames": [
						spriteToDict(sheet.Sprites(j))
						for j in range(sheet.SpritesLength())
						if sheet.Sprites(j).Name().decode('utf-8') == sprite_name
					]
				}
				for sprite_name in {sheet.Sprites(j).Name().decode('utf-8') for j in range(sheet.SpritesLength())}
			]
		}
		for sheet in (root.Sprites(i) for i in range(root.SpritesLength()))
	]

def loadSpritesheet(file_path):
	with open(file_path, "rb") as f:
		data = f.read()

	buf = bytearray(data)
	rootsheet = SpriteSheetRoot.SpriteSheetRoot.GetRootAsSpriteSheetRoot(buf, 0)
	return rootsheet


if __name__ == "__main__":
	root = loadSpritesheet(filepath)

	''' TODO - refactor this
		it uses the functions which we retrieve from the schema, these functions are called to then get the desired
		information and then save it into a JSON format
	'''
	# returns a dictionary with all necessary values to map each sprite on the spritesheet
	root_dict = {
		"spritesheets": buildSpritesheetJson(root),
		"animated_sprites": [
			{
				"name": (anim := root.AnimatedSprites(i)).Name().decode('utf-8'),
				"index": anim.Index(),
				"set": anim.Set(),
				"direction": anim.Direction(),
				"action": anim.Action(),
				"sprite": spriteToDict(anim.Sprite())
			}
			for i in range(root.AnimatedSpritesLength())
		]
	}

with open("spritesheet.json", "w") as f:
	json.dump(root_dict, f, indent=2)
