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

def spriteSheetReader(input_xml):
	tree = ET.parse(input_xml)
	root = tree.getroot()

	results = []

	for obj in root.findall(".//Object"):
		# get the required attributes to verify sprites
		type = obj.get("type")
		id = obj.get("id")
		labels = obj.findtext("Labels")
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
			"file": file
		})

"""	
	for r in results:
		print(f"ID: {r['id']}")
		print(f"Type: {r['type']}")
		print(f"File: {r['file']}")
		print(f"Labels: {', '.join(r['labels'])}")
		print("-" * 40)
"""

if __name__ == '__main__':
	spriteSheetReader(INPUT_XML)
