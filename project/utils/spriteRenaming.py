import xml.etree.ElementTree as ET
import os
import tkinter
import shutil

import unusedSpriteToBinary
from os import error

from PIL import Image, ImageTk

from project.utils.unusedSpriteToBinary import computeHash, SKIP_ARCHIVE

"""
This file is to be used on the unnamed images extracted from the sprite sheets to make manually renaming the 
required images a little bit less torturous 

This will enable the following
	- to know exactly how many sprites should be in each <File> (seen in Equip.xml)
		- so none are missed, but those that are will be logged so I can manually review & amend
	- make things a bit easier than right click rename or some other CLI method
	- reduces human error to a degree 
"""

# XML for specific sheet, for example equip.xml
INPUT_XML = os.environ.get("INPUT_XML")
# Folder for the sprites to be / already renamed by this script
BASE_RENAMED_SPRITES_DIR = os.environ.get("BASE_RENAMED_SPRITES_DIR")
# Manually parsed sprites, not renamed
PARSED_OUTPUT_SPRITES = os.environ.get("PARSED_OUTPUT_SPRITES")
# we only want these sprites, so only the tags with these labels will be exported, thus reducing data
labels_required = {"ARMOR", "WEAPON", "RING", "ABILITY"}

FINISHED_SPRITES = 'spriteRenameComplete.xml'


def spriteSheetReader(input_xml):
	"""
	reads an XML with the required data and returns a compact version of that for parsing

	this is to be used with the equip.xml file as it specifically targets important info for manually renaming sprites

	this is also used to read the spriteRenameComplete.xml file which will be used to verify what has already
	been done, so I can pick up from where I left off

	:returns: ID (Item name), Type (Item ID), File (SpriteSheet item is on), Display ID, Description, and Labels packed
	as a nested dictionaries in a list (results).
	Item count per sprite sheet as a dictionary (file_count)
	"""
	tree = ET.parse(input_xml)
	root = tree.getroot()

	results = []
	file_count = {}

	for obj in root.findall(".//Object"):
		# get the required attributes to verify sprites, honestly its a lot but deca does not name things aptly
		type = obj.get("type")
		id = obj.get("id")
		labels = obj.findtext("Labels")
		display_id = obj.findtext("DisplayId")
		description = obj.findtext("Description")
		file = obj.findtext(".//Texture/File")
		# used for caching images of the sprites, so that they can be skipped in future runs
		imageHash = obj.findtext(".//Texture/ImageHash")

		# skip entries missing labels or file
		if not labels or not file:
			continue

		label_list = {lbl.strip().upper() for lbl in labels.split(",") if lbl.strip()}

		if not (label_list & labels_required):
			continue

		try:
			file_count[file] += 1
		except KeyError:
			file_count.update({file: 1})

		results.append({
			"id": id,
			"type": type,
			"labels": list(label_list),
			"display_id": display_id,
			"description": description,
			"file": file,
			"imageHash": imageHash,
		})
	# sort by file so it matches folder order
	results.sort(key=lambda x: x["file"].lower())
	return results, file_count


"""	
	for r in results:
		print(f"ID: {r['id']}")
		print(f"Type: {r['type']}")
		print(f"File: {r['file']}")
		print(f"Display ID: {r['display_id']}")
		print(f"Description: {r['description']}")
		print(f"Labels: {', '.join(r['labels'])}")
		print("-" * 40)
"""


def saveCurrentProgress(equipment_data):
	with open(FINISHED_SPRITES, "a+") as f:
		return




def spriteRenamer(sprite_file_path, sprite_info):
	# get the list of renamed sprites to be skipped
	renamed_sprites, spriteCountPerSheet = spriteSheetReader('spriteRenameComplete.xml')

	tree = ET.parse(renamed_sprites)
	root = tree.getroot()

	for obj in root.findall(".//Object"):
		return obj
	return None


def imagePreview(path, size=(0, 0)):
	raw_image = Image.open(path)

	if size != (0, 0):  # change size of preview if specified resolution selected
		raw_image = raw_image.resize(size, Image.NEAREST)

	image = ImageTk.PhotoImage(raw_image)
	# panel = tkinter.Label(root, image=image, bg='#00ff08')
	panel.image = image



if __name__ == '__main__':
	equipObjects, spriteCountPerSheet = spriteSheetReader(INPUT_XML)

	parsedSpritesRoot = os.listdir(PARSED_OUTPUT_SPRITES)
	renamedSpritesRoot = os.listdir(BASE_RENAMED_SPRITES_DIR)

	rootWindow = tkinter.Tk()
	rootWindow.title("Sprite Preview")
	panel = tkinter.Label(rootWindow, bg='#00ff08')
	panel.pack()

	# check if the destination directories exist, if not, create them
	for originalFolder in parsedSpritesRoot:
		dest_path = os.path.join(BASE_RENAMED_SPRITES_DIR, originalFolder)
		if not os.path.exists(dest_path):
			os.mkdir(dest_path)

	# iterate through sprite folders
	for spriteFolders in parsedSpritesRoot:
		spriteFolderPath = os.path.join(PARSED_OUTPUT_SPRITES, spriteFolders)

		# files available on the disk
		fileCount = len(os.listdir(spriteFolderPath))

		if fileCount < spriteCountPerSheet[spriteFolders]:
			print(f"You appear to have the incorrect amount of sprites in the folder {spriteFolders}, it is expecting "
			      f"{spriteCountPerSheet[spriteFolders]} but shows {fileCount}.")
		if fileCount > spriteCountPerSheet[spriteFolders]:
			print(f"You appear to have the incorrect amount of sprites in the folder {spriteFolders}, it is expecting "
			      f"{spriteCountPerSheet[spriteFolders]} but shows {fileCount}.")
		else:
			print(f"Sprite count appears to be correct for directory {spriteFolders}")

		renamedSpriteFolder = os.path.join(BASE_RENAMED_SPRITES_DIR, spriteFolders)

		currentFileCount = 0

		for spriteImage in os.listdir(spriteFolderPath):
			currentFileCount += 1
			if currentFileCount > spriteCountPerSheet[spriteFolders]:
				break

			spriteImagePath = os.path.join(spriteFolderPath, spriteImage)
			imagePreview(spriteImagePath, size=(500, 500))
			spriteImageHash = computeHash(spriteImagePath)


			print("1")
			rootWindow.update()






