import hashlib
import os
from unittest.util import three_way_cmp

from PIL.ImageChops import difference

"""
This tool compares all the extracted sprites to my manually filtered list of equipment sprites and encodes them as a
sha256 hash, this hash can be utilised for future filtering of required equipment sprites.

The idea is that each sprite is unique, thus each encoded hash is unique, storing the hashes is very data efficient and 
can be referenced easily. I can then use this binary file so that any future extraction will skip these files entirely.

This will make it so that all future manual reviews (these are required, due to images needing to be labelled) will
take considerably less long, due to the fact you wont need to parse through 14000+ sprites which are entirely useless
for this situation

Original Sprite Count - 13973
Manually Parsed Sprite Count - 2407
Final Sprite Count - ... 
"""

SKIP_ARCHIVE = "skiparchive.bin"
ORIGINAL_SPRITES = os.environ.get("ORIGINAL_SPRITES")
PARSED_OUTPUT_SPRITES = os.environ.get("PARSED_OUTPUT_SPRITES")

def computeHash(imagePath):
	# return encoded hash for a sprite
	with open(imagePath, "rb") as imageFile:
		imageBytes = imageFile.read()
		return hashlib.sha256(imageBytes).hexdigest()

def loadSkipBinary():
	'''
	returns the binary data as a set, each 32 bytes in size. you can encode your own images which should then yield
	the same binary data for my encoded data in the file "skiparchive.bin".
	'''
	skipped_set = set()
	with open(SKIP_ARCHIVE, "rb") as skipBinaryData:
		if not skipBinaryData:
			print("Skip Data not found")
		while True:
			spriteHash = skipBinaryData.read(32)
			if not spriteHash:
				break
			skipped_set.add(spriteHash)
	return skipped_set

def saveSkipBinary(skip_set):
	# saves the set of encoded sprite hashes to the binary file
	with open(SKIP_ARCHIVE, "wb") as skipBinaryData:
		for spriteHash in skip_set:
			skipBinaryData.write(spriteHash)

def updateSkipBinary(ORIGINAL_SPRITES, PARSED_OUTPUT_SPRITES):
	"""
	Updates the binary as needed

	:arg	ORIGINAL_SPRITES: Directory of all extracted sprites
	:arg    PARSED_OUTPUT_SPRITES: Directory of manually parsed sprites
	"""
	skipSet = loadSkipBinary()




def checkIfSkip(hash):
	return None

if __name__ == "__main__":
	# if there is a binary, load it
	# skippedSet = loadSkipBinary()
	hashedSprites = set()
	throwawayHashedSprites = set()

	originalSpritesRoot = os.listdir(ORIGINAL_SPRITES)
	# TODO - RENAME THIS TO THE PARSED FOLDER, AS IT CURRENTLY POINTS TO THE NON-RENAMED SPRITES
	currentParsedSpritesRoot = os.listdir(PARSED_OUTPUT_SPRITES)
	for currentParsedSpriteFolders in currentParsedSpritesRoot:
		# get the current / parsed sprites file path, and then hash those images
		currentSprites = [
			os.path.join(PARSED_OUTPUT_SPRITES, currentParsedSpriteFolders, sprite)
			for sprite in os.listdir(os.path.join(PARSED_OUTPUT_SPRITES, currentParsedSpriteFolders))
			]
		hashedSprites.update(
			computeHash(os.path.abspath(sprite)) for sprite in currentSprites
		)


	for originalSpriteFolders in originalSpritesRoot:
		# do the same thing as the above, but for the full sprite list
		throwawaySprites = [
			os.path.join(ORIGINAL_SPRITES, originalSpriteFolders, sprite)
			for sprite in os.listdir(os.path.join(ORIGINAL_SPRITES, originalSpriteFolders))
		]
		throwawayHashedSprites.update(
			computeHash(os.path.abspath(sprite)) for sprite in throwawaySprites
		)
	# compute the final throwaway binary set
	# TODO - MY OUTPUT IS NOT COMPLETE, ONCE THE SPRITES ARE MANUALLY PARSED IT WILL BE USEABLE, THIS IS FOR TESTING
	throwawayHashedSprites.difference_update(hashedSprites)
	saveSkipBinary(throwawayHashedSprites)

