import xml.etree.ElementTree as ET
from collections import Counter

'''
This script is meant to read the XML files extracted from the game so that you are able to identify which
corresponding spritesheets are required for a given sprite. This allows you to cut down the amount of data stored
in spritesheet.json to allow for faster data retrieval.

There would otherwise be far too many redundant spritesheets to store in the JSON, you can modify this script if you 
wish to include things like dungeon sprites or bullet sprites.
'''
# todo - set as environment variable
inputxml = r'C:\Code\RotMGCalc\localfiles\xml\equip.xml'

# Load XML file (replace 'input.xml' with your XML filename)
tree = ET.parse("input.xml")
root = tree.getroot()

# Find all <File> tags and collect their text
files = [f.text for f in root.findall(".//File") if f.text]

# Count occurrences
counts = Counter(files)

# Print results
for i, (fname, count) in enumerate(counts.items(), start=1):
    print(f"{fname} = {count}")