import xml.etree.ElementTree as ET
import os
import tkinter
import shutil

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




def spriteRenamer(sprite_source_path, sprite_target_path, target_name):
	return


def equipmentParsing(*args):
	"""
	:arg equipment_data: equipment xml data
	:arg parsed_sprites_root: manually parsed sprites
	:arg renamed_sprites_root: renamed sprites (post in-script rename)
	:arg root_window: window for tkinter

	This function renames the sprite to its "equipobjects" "type", for consistency. it will parse the folders of
	manually checked sprites and then allow for easy renaming of subsequent updates

	I will be hashing each images data, and attaching it to spriteRenameComplete.xml, this is one way of making
	sure that i don't repeat images, as there is no guarantee that the extraction will ever give the same name for the
	sprite twice.

	The only guarantee is that hashing the 8x8 image will always yield the same hash so long as the sprite doesn't
	change, this will make it very easy to pick up reskins, as well as using it to skip completed images

	"""

	actionVar = tkinter.BooleanVar(value=False)

	# check if the destination directories exist, if not, create them
	for originalFolder in parsedSpritesRoot:
		dest_path = os.path.join(BASE_RENAMED_SPRITES_DIR, originalFolder)
		if not os.path.exists(dest_path):
			os.mkdir(dest_path)

	# iterate through sprite folders
	if actionVar.get():
		for spriteFolders in parsedSpritesRoot:
			spriteFolderPath = os.path.join(PARSED_OUTPUT_SPRITES, spriteFolders)

			# files available on the disk
			fileCount = len(os.listdir(spriteFolderPath))

			if fileCount != spriteCountPerSheet[spriteFolders]:
				print(
					f"You appear to have the incorrect amount of sprites in the folder {spriteFolders}, it is expecting "
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
				spriteImageHash = computeHash(spriteImagePath)
				print(spriteImageHash)
				imagePreview(spriteImagePath, size=(500,500))




def imagePreview(path, size=(0, 0)):
	raw_image = Image.open(path)

	if size != (0, 0):  # change size of preview if specified resolution selected
		raw_image = raw_image.resize(size, Image.NEAREST)

	return ImageTk.PhotoImage(raw_image)

class ReviewSession:
	def __init__(self):
		self.currentImagePath = None
		self.currentImageHash = None

		self.equipmentObjects = []
		self.spriteCountPerSheet = {}
		self.completedEquipmentObjects = []

		self.spriteRenameFolderDest = None

	def load_XML_Sources(self, INPUT_XML, FINISHED_SPRITES):
		self.equipmentObjects, spriteCountPerSheet = spriteSheetReader(INPUT_XML)
		self.completedEquipmentObjects = spriteSheetReader(FINISHED_SPRITES)


class InitialiseApp:
	def __init__(self, master):
		self.master = master
		master.title("Sprite Renaming")

		self.imagePaths = []
		self.index = 0
		self.equipmentData = []
		self.completedRenamesData = []
		self.undoStack = []
		self.redoStack = []
		self.currentTask = None

		menu = tkinter.Menu(master)
		editMenu = tkinter.Menu(menu, tearoff=0)
		editMenu.add_command(label="Undo", command=self.undo)
		editMenu.add_command(label="Redo", command=self.redo)
		menu.add_cascade(label="Edit", menu=editMenu)
		master.config(menu=menu)

		self.leftFrame = tkinter.Frame(master)
		self.leftFrame.pack(side="left", padx=10, pady=10)
		self.rightFrame = tkinter.Frame(master)
		self.rightFrame.pack(side="right", padx=10, pady=10)

		self.imageLabel = tkinter.label(self.leftFrame)
		self.imageLabel.pack()

		tkinter.Label(self.rightFrame, text="Fuzzy Search XML Data:").pack(pady=10)
		self.searchBar = tkinter.Entry(self.rightFrame)
		self.searchBar.pack(fill="x")
		tkinter.Button(self.rightFrame, text="Search", command=self.runSearch).pack(pady=10)

		self.searchResults = tkinter.Listbox(self.rightFrame)
		self.searchResults.pack(fill=tkinter.BOTH, expand=True)
		self.searchResults.bind("<<ListboxSelect>>")

		tkinter.Button(self.rightFrame, text="Next Image", command=self.nextImage).pack(pady=10)




if __name__ == '__main__':
	equipObjects, spriteCountPerSheet = spriteSheetReader(INPUT_XML)

	parsedSpritesRoot = os.listdir(PARSED_OUTPUT_SPRITES)
	renamedSpritesRoot = os.listdir(BASE_RENAMED_SPRITES_DIR)

	initialiseApp()

initialiseApp().mainloop()






