import json
from collections import Counter
import xml.etree.ElementTree as ET
import os

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
# we only want these sprites, so only the tags with these labels will be exported, thus reducing data
labels_required = {"ARMOR", "WEAPON", "RING", "ABILITY"}

finished_sprites = 'spriteRenameComplete.xml'


def spriteSheetReader(input_xml):
	"""
	reads an XML with the required data and returns a compact version of that for parsing

	this is to be used with the equip.xml file as it specifically targets important info for manually renaming sprites

	this is also used to read the spriteRenameComplete.xml file which will be used to verify what has already
	been done, so I can pick up from where I left off
	"""
	tree = ET.parse(input_xml)
	root = tree.getroot()

	results = []
	index_counter = 0

	for obj in root.findall(".//Object"):
		# get the required attributes to verify sprites, honestly its a lot but deca does not name things aptly
		type = obj.get("type")
		id = obj.get("id")
		labels = obj.findtext("Labels")
		display_id = obj.findtext("DisplayId")
		description = obj.findtext("Description")
		file = obj.findtext(".//Texture/File")

		# skip entries missing labels or file
		if not labels or not file:
			continue

		label_list = {lbl.strip().upper() for lbl in labels.split(",") if lbl.strip()}

		if not (label_list & labels_required):
			continue


		results.append({
			"id": id,
			"type": type,
			"labels": list(label_list),
			"display_id": display_id,
			"description": description,
			"file": file,
		})
	# sort by file so it matches folder order
	results.sort(key=lambda x: x["file"].lower())
	for result in results:
		index_counter += 1
		result["index"] = index_counter
	return results

"""	
	for r in results:
		print(f"ID: {r['id']}")
		print(f"Type: {r['type']}")
		print(f"File: {r['file']}")
		print(f"Display ID: {r['display_id']}")
		print(f"Description: {r['description']}")
		print(f"Labels: {', '.join(r['labels'])}")
		print(f"Index: {r['index']}")
		print("-" * 40)
"""

def saveCurrentProgress():
	return


def spriteRenamer(object, image):
	# get the list of renamed sprites to be skipped
	renamed_sprites = spriteSheetReader('spriteRenameComplete.xml')

	return


if __name__ == '__main__':
	spriteSheetReader(INPUT_XML)
