import json
from collections import defaultdict
import SpriteSheetRoot

# todo - set as environment variable
FILEPATH = r'C:\Code\RotMGCalc\localfiles\xml\spritesheetf.bin'
SPRITEMAPREQUIREMENTS = "spriteMapRequirements.json"

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

		animatedSprite = defaultdict(list)
		for j in range(sheet.SpritesLength()):
			sprite = sheet.Sprites(j)
			currentSprite = sprite.Name().decode("utf-8")
			animatedSprite[currentSprite].append(spriteToDict(sprite))

		result.append({
			"name": sheetName,
			"atlasId": sheet.AtlasId(),
			"sprites": [
				{"name": name, "spriteLocation": frames}
				for name, frames in animatedSprite.items()
			]
		})

	return result


def loadSpritesheet(spriteFilePath):
	try:
		with open(spriteFilePath, "rb") as f:
			data = f.read()

		buf = bytearray(data)
		rootsheet = SpriteSheetRoot.SpriteSheetRoot.GetRootAsSpriteSheetRoot(buf, 0)
		return rootsheet
	except:
		print(f"unable to load spritesheet or failure to read data, please validate ")


def loadSpriteMapRequirements(spriteRequirements):
	try:
		with open(spriteRequirements) as f:
			spriteMapReqs = json.load(f)
			if spriteMapReqs is not None:
				return set(spriteMapReqs)
	except:
		print("No spriteMapRequirements.json found, exporting all sprites")


if __name__ == "__main__":

	spriteSheet = loadSpritesheet(FILEPATH)
	# load optional specified spritesheets
	spriteMapSet = loadSpriteMapRequirements(SPRITEMAPREQUIREMENTS)

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
		]
	}

with open("spritesheet.json", "w") as f:
	json.dump(spriteSheetDict, f, indent=2)
