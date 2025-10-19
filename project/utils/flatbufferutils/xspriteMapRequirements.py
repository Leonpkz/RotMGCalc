import json
from collections import Counter
import xml.etree.ElementTree as ET
import os

'''
This script is meant to read the XML files extracted from the game so that you are able to identify which
corresponding spritesheets are required for a given sprite. This allows you to cut down the amount of data stored
in spritesheet.json to allow for faster data retrieval.

There would otherwise be far too many redundant spritesheets to store in the JSON, you can modify this script if you 
wish to include things like dungeon sprites or bullet sprites.
'''

# XML for specific sheet, for example equip.xml
INPUT_XML = os.environ.get("INPUT_XML")

def spriteSheetCounter(input_xml):
	tree = ET.parse(input_xml)
	root = tree.getroot()

	# we only want these sprites, so only the tags with these labels will be exported, thus reducing data
	labels_required = {"ARMOR", "WEAPON", "RING", "ABILITY"}
	file_tags = []

	for obj in root.findall(".//Object"):
		labels = obj.find("Labels")
		if labels is None:
			continue

		label_list = {lbl.strip().upper() for lbl in labels.text.split(",")}
		if not (label_list & labels_required):
			continue

		texture_file = obj.find(".//Texture/File")
		if texture_file is not None and texture_file.text:
			file_tags.append(texture_file.text)

	tagSet = sorted(set(file_tags))

	json.dump(tagSet, open("spriteMapRequirements.json", "w"), indent=2)


if __name__ == '__main__':
	spriteSheetCounter(INPUT_XML)
