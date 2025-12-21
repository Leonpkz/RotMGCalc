import xml.etree.ElementTree as ET
import os
import tkinter
import shutil
from os.path import abspath

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


def spriteSheetReader(input_xml, ignore_labels=False):
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

		# the "or" is required so it reads my complete sprites xml
		type = obj.get("type") or obj.findtext("Type")
		id = obj.get("id") or obj.findtext("Id")
		labels = obj.findtext("Labels")
		display_id = obj.findtext("DisplayId")
		description = obj.findtext("Description")
		file = obj.findtext(".//Texture/File") or obj.findtext("File")
		# used for caching images of the sprites, so that they can be skipped in future runs
		imageHash = obj.findtext(".//Texture/ImageHash")

		# skip entries missing labels or file
		if not labels or not file:
			continue

		label_list = {lbl.strip().upper() for lbl in labels.split(",") if lbl.strip()}

		if not ignore_labels and not (label_list & labels_required):
			continue

		try:
			file_count[file] += 1
		except KeyError:
			file_count.update({file: 1})

		results.append({
			"Id": id,
			"Type": type,
			"Labels": list(label_list),
			"DisplayID": display_id,
			"Description": description,
			"File": file,
			"ImageHash": imageHash,
		})
	# sort by file so it matches folder order
	results.sort(key=lambda x: x["File"].lower())
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


def equipmentImageParsing(parsed_sprites_root, renamed_sprites_root):
	"""

	This function yields image path data for the currently selected sprite in the gui.

	I will be hashing each images data, and attaching it to spriteRenameComplete.xml, this is one way of making
	sure that i don't repeat images, as there is no guarantee that the extraction will ever give the same name for the
	sprite twice.

	The only guarantee is that hashing the 8x8 image will always yield the same hash so long as the sprite doesn't
	change, this will make it very easy to pick up reskins, as well as using it to skip completed images
	"""


	# check if the destination directories exist, if not, create them
	for originalFolder in parsedSpritesRoot:
		dest_path = os.path.join(BASE_RENAMED_SPRITES_DIR, originalFolder)
		if not os.path.exists(dest_path):
			os.mkdir(dest_path)

	# iterate through sprite folders

	for spriteFolders in parsedSpritesRoot:
		spriteFolderPath = os.path.join(PARSED_OUTPUT_SPRITES, spriteFolders)
		files = os.listdir(spriteFolderPath)
		# files available on the disk
		fileCount = len(files)
		# expected file count, as per the equip.xml data
		equipObjectsFileCount = spriteCountPerSheet[spriteFolders]
		# information for the gui
		fileStatus = None

		if fileCount != equipObjectsFileCount:
			fileStatus = (
				f"You appear to have the incorrect amount of sprites in the folder {spriteFolders}, it is expecting "
				f"{equipObjectsFileCount} but shows {fileCount}.")
		else:
			fileStatus = f"Sprite count appears to be correct for directory {spriteFolders}"

		# destination rename folder
		renamedSpriteFolder = os.path.join(BASE_RENAMED_SPRITES_DIR, spriteFolders)

		for spriteImage in files:
			spriteImagePath = os.path.join(spriteFolderPath, spriteImage)
			spriteImageHash = computeHash(spriteImagePath)

			yield {
				"status": fileStatus,
				"spritePath": spriteImagePath,
				"destinationRenamePath": renamedSpriteFolder,
				"fileCount": fileCount,
				"equipObjectsFileCount": equipObjectsFileCount,
				"imageHash": spriteImageHash,
			}


def imagePreview(path, size=(0, 0)):
	raw_image = Image.open(path)
	if size != (0, 0):  # change size of preview if specified resolution selected
		raw_image = raw_image.resize(size, Image.NEAREST)
	return ImageTk.PhotoImage(raw_image)

class ReviewSession:
	def __init__(self):
		self.spriteRenameComplete = None
		self.currentImagePath = None
		self.currentImageHash = None

		self.completedEquipmentObjects = []
		self.completedHashes = {}
		self.completedTypes = {}
		self.equipmentObjects = []
		self.spriteCountPerSheet = {}


	def load_XML_Sources(self, INPUT_XML, FINISHED_SPRITES):
		self.equipmentObjects, spriteCountPerSheet = spriteSheetReader(INPUT_XML)
		self.completedEquipmentObjects, _ = spriteSheetReader(FINISHED_SPRITES, ignore_labels=True)

		# will store the hashed image data for completed sprites
		self.completedHashes = {
			e["ImageHash"]: e for e in self.completedEquipmentObjects
		}

		# this will store the "type" for each equipment item which has been completed
		self.completedTypes = {
			e["Type"] for e in self.completedEquipmentObjects
		}


class InitialiseApp:
	def __init__(self, master):
		self.master = master
		master.title("Sprite Renaming")
		self.reviewSession = ReviewSession()
		self.reviewSession.load_XML_Sources(INPUT_XML, FINISHED_SPRITES)

		self.index = 0

		self.equipImages = list(equipmentImageParsing(parsedSpritesRoot, renamedSpritesRoot))
		self.incompleteEquipImages = [
			e for e in self.equipImages
			if e["imageHash"] not in self.reviewSession.completedHashes
		]
		self.incompleteEquipmentData = [
			e for e in self.reviewSession.equipmentObjects
			if e["Type"] not in self.reviewSession.completedTypes
		]
		self.filteredEquipmentEntries = []
		self.completedRenamesData = []
		self.undoStack = []
		self.redoStack = []
		self.currentImage = None
		self.currentXmlEntry = None

		# for the scroll wheel thumbnails, to make it more performant
		self.THUMB_SIZE = 64
		self.VISIBLE_ROWS = 12
		self.BUFFER_ROWS = 4
		self.TOTAL_ROWS = len(self.incompleteEquipImages)
		self.FIRST_VISIBLE_INDEX = 0
		self.THUMB_WIDGETS = []
		self.THUMB_IMAGES_CACHE = {}

		menu = tkinter.Menu(master)
		editMenu = tkinter.Menu(menu, tearoff=0)
		editMenu.add_command(label="Undo", command=self.undo)
		editMenu.add_command(label="Redo", command=self.redo)
		menu.add_cascade(label="Edit", menu=editMenu)
		master.config(menu=menu)


		self.leftFrame = tkinter.Frame(master)
		self.thumbCanvas = tkinter.Canvas(self.leftFrame, width=80)
		self.thumbCanvas.pack(side="left", fill="y", expand=True)
		self.thumbnailsFrame = tkinter.Frame(self.thumbCanvas)
		self.thumbCanvas.create_window((0, 0), window=self.thumbnailsFrame, anchor="nw")
		self.thumbCanvasScrollbar = tkinter.Scrollbar(self.leftFrame, orient="vertical", command=self.thumbCanvas.yview)
		self.thumbCanvasScrollbar.pack(side="right", fill="y")
		self.thumbCanvasScrollbar.config(command=self.onCanvasScroll)
		self.thumbCanvas.configure(yscrollcommand=self.thumbCanvasScrollbar.set)
		self.thumbnailsFrame.bind(
			"<Configure>",
			lambda e: self.thumbCanvas.configure(
				scrollregion=self.thumbCanvas.bbox("all")
			)
		)

		self.leftFrame.pack(side="left", padx=10, pady=10)
		self.rightFrame = tkinter.Frame(master)
		self.rightFrame.pack(side="right", padx=10, pady=10)

		self.previewFrame = tkinter.Frame(self.leftFrame)
		self.previewFrame.pack(side="left", padx=10)

		self.imageLabel = tkinter.Label(self.previewFrame)
		self.imageLabel.pack()

		self.folderStatus = tkinter.Label(
			self.previewFrame,
			wraplength=500,
			justify="left",
			anchor="w"
		)
		self.folderStatus.pack(pady=(8, 0), fill="x")

		tkinter.Label(self.rightFrame, text="Fuzzy Search XML Data:", ).pack(pady=20)
		self.searchBar = tkinter.Entry(self.rightFrame)
		self.searchBar.pack(fill="x")
		tkinter.Button(self.rightFrame, text="Search", command=self.runSearch).pack(pady=10)

		self.searchResults = tkinter.Listbox(self.rightFrame, width=25)
		self.searchResults.pack(fill=tkinter.BOTH, expand=True)
		self.searchResults.bind("<<ListboxSelect>>", self.onSearchSelect)
		self.runSearch()

		tkinter.Button(self.rightFrame, text="Rename Sprite", command=self.renameSprite).pack(pady=10)

		self.createThumbnailPool()
		self.updateVisibleThumbnails()


	def undo(self):
		return


	def redo(self):
		return


	def fuzzyMatch(self, entry, queryText):
		queryText = queryText.lower()

		haystack = " ".join([
			str(entry.get("Id", "")),
			str(entry.get("DisplayId", "")),
			str(entry.get("Description", ""))
		]).lower()

		return queryText in haystack


	def runSearch(self):
		query = self.searchBar.get().strip().lower()
		self.searchResults.delete(0, tkinter.END)

		data = self.incompleteEquipmentData

		if not query:
			self.filteredEquipmentEntries = data[:]
		else:
			self.filteredEquipmentEntries = [
				e for e in self.reviewSession.equipmentObjects
				if self.fuzzyMatch(e, query)
			]

		for entry in self.filteredEquipmentEntries:
			self.searchResults.insert(tkinter.END, str(entry["Id"]))


	def onSearchSelect(self, event):
		if not self.searchResults.curselection():
			return

		idx = self.searchResults.curselection()[0]
		self.currentXmlEntry = self.filteredEquipmentEntries[idx]


	def renameSprite(self):
		spriteRenamer(self.currentImage, self.currentXmlEntry, self)



	def loadImage(self, entry):
		image = imagePreview(entry["spritePath"], size=(500, 500))
		self.imageLabel.configure(image=image, background="#39FF14")
		self.imageLabel.image = image
		self.folderStatus.config(text=f"{entry["status"]}")
		self.currentImage = entry["spritePath"]


	def selectImage(self, index):
		self.currentImage = self.incompleteEquipImages[index]
		self.index = index
		self.loadImage(self.currentImage)


	def createThumbnailPool(self):
		for i in range(self.VISIBLE_ROWS + self.BUFFER_ROWS):
			lbl = tkinter.Label(
				self.thumbnailsFrame,
				cursor="hand2"
			)
			lbl.pack(anchor="w", pady=4)
			lbl.bind("<Button-1>", lambda e, idx=i: self.onThumbnailClick(idx))
			self.THUMB_WIDGETS.append(lbl)


	def getThumbnailImage(self, index):
		if index in self.THUMB_IMAGES_CACHE:
			return self.THUMB_IMAGES_CACHE[index]

		entry = self.incompleteEquipImages[index]
		img = imagePreview(entry["spritePath"], size=(64, 64))
		self.THUMB_IMAGES_CACHE[index] = img
		return img


	def updateVisibleThumbnails(self):
		start = max(0, self.FIRST_VISIBLE_INDEX - self.BUFFER_ROWS)
		end = min(
			self.TOTAL_ROWS,
			start + self.VISIBLE_ROWS + self.BUFFER_ROWS
		)

		for widget_idx, data_idx in enumerate(range(start, end)):
			widget = self.THUMB_WIDGETS[widget_idx]

			img = self.getThumbnailImage(data_idx)
			widget.configure(image=img)
			widget.image = img

			widget.config(
				relief="solid" if data_idx == self.index else "flat",
				bd=2 if data_idx == self.index else 0
			)

			widget.data_index = data_idx

	def onCanvasScroll(self, *args):
		self.thumbCanvas.yview(*args)

		first, last = self.thumbCanvas.yview()
		self.FIRST_VISIBLE_INDEX = int(first * self.TOTAL_ROWS)

		self.updateVisibleThumbnails()


	def onThumbnailClick(self, widget_index):
		widget = self.THUMB_WIDGETS[widget_index]
		data_index = widget.data_index

		self.selectImage(data_index)


if __name__ == '__main__':
	equipObjects, spriteCountPerSheet = spriteSheetReader(INPUT_XML)

	parsedSpritesRoot = os.listdir(PARSED_OUTPUT_SPRITES)
	renamedSpritesRoot = os.listdir(BASE_RENAMED_SPRITES_DIR)

	approot = tkinter.Tk()
	initialiseApp = InitialiseApp(approot)

approot.mainloop()






