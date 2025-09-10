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

INPUT_XML = os.environ.get("INPUT_XML")

def spriteSheetCounter(input_xml):
	tree = ET.parse(input_xml)
	root = tree.getroot()

	# find file tag
	file_tag = [f.text for f in root.findall(".//File") if f.text]

	counts = Counter(file_tag)
	tagSet = set()

	for i, (tag_name, count) in enumerate(counts.items(), start=1):
		# print(f"{tag_name} = {count}")
		tagSet.add(tag_name)

	tagSet = list(tagSet)

	json.dump(tagSet, open("spriteMapRequirements.json", "w"), indent=2)


if __name__ == '__main__':
	spriteSheetCounter(INPUT_XML)
