import xml.etree.ElementTree as ET

players = r'C:\Code\RotMGCalc\localfiles\xml\Players.xml'

class Character:
	def __init__(self):
		return

	tree = ET.parse(players)
	root = tree.getroot()

	# retrieve character information from XML
	for childs in root:
		if childs.tag == 'Object':
			print(f"{childs.attrib.get('id')}")
			for rotmgClass in childs:
				print(f"{rotmgClass.tag}" f"{rotmgClass.text}")






