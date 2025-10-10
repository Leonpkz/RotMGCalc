import json
from collections import defaultdict
from sys import exception
import os

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
	maskPositon = sprite.MaskPosition()
	color = sprite.Color()

	# dict comprehension on position and color values, assigning them to their respective tag for JSON
	return {
		"position": [getattr(position, attr)() for attr in ['X', 'Y', 'W', 'H']],
		"maskPositon": [getattr(maskPositon, attr)() for attr in ['X', 'Y', 'W', 'H']],
		"color": [getattr(color, attr)() for attr in ['R', 'G', 'B', 'A']],
		"transparent": sprite.IsTransparent()
	}


def buildSpritesheetJson(spriteSheet, allowedSheetNames=None):
	# builds the json with all the required sprites
	result = []
	for i in range(spriteSheet.SpritesLength()):
		sheet = spriteSheet.Sprites(i)
		sheetName = sheet.Name().decode("utf-8")
		if allowedSheetNames is not None and sheetName not in allowedSheetNames:
			continue

		spriteInfo = defaultdict(list)
		for j in range(sheet.SpritesLength()):
			sprite = sheet.Sprites(j)
			# specify what sprite width and height you want to export
			if not widthHeightParsing(sprite, requiredWidthHeight=(8.0, 8.0)):
				continue
			currentSprite = sprite.Name().decode("utf-8")
			spriteInfo[currentSprite].append(spriteToDict(sprite))

		result.append({
			"name": sheetName,
			"atlasId": sheet.AtlasId(),
			"sprites": [
				{"name": name, "spriteLocation": frames}
				for name, frames in spriteInfo.items()
			]
		})

	return result


def loadSpritesheet(spriteFilePath):
	try:
		with open(spriteFilePath, "rb") as f:
			data = f.read()

		buffer = bytearray(data)
		spriteSheetRoot = SpriteSheetRoot.SpriteSheetRoot.GetRootAsSpriteSheetRoot(buffer, 0)
		return spriteSheetRoot
	except exception as error:
		print(f"Unable to find file path or failure to read file data, please validate file path and or the decoded "
		      f"Schema files - see exception - {error}")


def loadSpriteMapRequirements(spriteRequirements):
	try:
		with open(spriteRequirements) as f:
			spriteMapReqs = json.load(f)
			if spriteMapReqs is not None:
				return set(spriteMapReqs)
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

	spriteSheet = loadSpritesheet(SPRITE_SHEET_BIN)
	# load optional specified spritesheets
	spriteMapSet = loadSpriteMapRequirements(SPRITE_MAP_REQUIREMENTS)

	# returns a dictionary with all necessary values to map each sprite on the spritesheet
	spriteSheetDict = {
		"spritesheets": buildSpritesheetJson(spriteSheet, spriteMapSet),
		"animated_sprites": [
			{
				"name": (anim := spriteSheet.AnimatedSprites(i)).Name().decode("utf-8"),
				"index": anim.Index(),
				"set": anim.Set(),
				"direction": anim.Direction(),
				"action": anim.Action(),
				"sprite": spriteToDict(anim.Sprite())
			}
			for i in range(spriteSheet.AnimatedSpritesLength())
			# specify what sprite width and height you want to export
			if widthHeightParsing(spriteSheet.AnimatedSprites(i).Sprite(), requiredWidthHeight=(8.0, 8.0))
		]
	}

with open("spritesheet.json", "w") as f:
	json.dump(spriteSheetDict, f, indent=2)
