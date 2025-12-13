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
ORIGINAL_OUTPUT_FOLDER = os.environ.get("ORIGINAL_SPRITES")
PARSED_OUTPUT_FOLDER = os.environ.get("PARSED_OUTPUT_SPRITES")


def computeHash(imagePath):
	# return encoded hash for a sprite
	with open(imagePath, "rb") as imageFile:
		imageBytes = imageFile.read()
		return hashlib.sha256(imageBytes).digest()


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
	print("Saving skip binary...")
	with open(SKIP_ARCHIVE, "wb") as skipBinaryData:
		for spriteHash in skip_set:
			skipBinaryData.write(spriteHash)
		print("Save complete")


def returnHashedImages(imageFolder):
	hashedSprites = set()

	hashedSpritesRoot = os.listdir(imageFolder)
	for originalSpriteFolders in hashedSpritesRoot:
		# do the same thing as the above, but for the full sprite list
		throwawaySprites = [
			os.path.join(imageFolder, originalSpriteFolders, sprite)
			for sprite in os.listdir(os.path.join(imageFolder, originalSpriteFolders))
		]
		hashedSprites.update(
			computeHash(os.path.abspath(sprite)) for sprite in throwawaySprites
		)
	return hashedSprites


def updateSkipBinary(originalFolder, parsedFolder):
	"""
	Updates the binary as needed

	:arg	originalFolder: Directory of all extracted sprites
	:arg    parsedFolder: Directory of manually parsed sprites
	"""
	# TODO - RENAME THIS TO THE PARSED FOLDER, AS IT CURRENTLY POINTS TO THE NON-RENAMED SPRITES
	hashedSprites = set(returnHashedImages(parsedFolder))
	throwawayHashedSprites = set(returnHashedImages(originalFolder))

	# compute the final throwaway binary set
	# TODO - MY OUTPUT IS NOT COMPLETE, ONCE THE SPRITES ARE MANUALLY PARSED IT WILL BE USEABLE, THIS IS FOR TESTING
	throwawayHashedSprites.difference_update(hashedSprites)

	skipBinary = loadSkipBinary()

	if len(skipBinary) > 1:
		print("Binary file found, saving the difference")
		skipBinary.difference_update(throwawayHashedSprites)
		saveSkipBinary(skipBinary)
		return
	else:
		print("Binary file not found")
		saveSkipBinary(throwawayHashedSprites)


def checkIfSkip():
	return None


if __name__ == "__main__":
	# if there is a binary, load it
	# skippedSet = loadSkipBinary()
	updateSkipBinary(ORIGINAL_OUTPUT_FOLDER, PARSED_OUTPUT_FOLDER)



