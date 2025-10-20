import hashlib
import os

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

def computeHash(image):
	# return encoded hash for a sprite
	return hashlib.sha256(image.read_bytes()).digest()

def loadSkipBinary():
	'''
	returns the binary data as a set, each 32 bytes in size. you can encode your own images which should then yield
	the same binary data for my encoded data in the file "skiparchive.bin".
	'''
	skip_set = set()
	with open(SKIP_ARCHIVE, "rb") as skipBinaryData:
		while True:
			spriteHash = skipBinaryData.read(32)
			if not spriteHash:
				break
			skip_set.add(spriteHash)
	return skip_set

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
	return None


def checkIfSkip(image):
	return None
