import os
import xml.etree.ElementTree as ET

INPUT_XML = os.environ.get("INPUT_XML")
def spriteSheetReader(input_xml, output_xml):
	tree = ET.parse(input_xml)
	root = tree.getroot()

	required = 'nildrop'

	with open(output_xml, 'a') as output_file:
		for obj in root.findall(".//Object"):
			id = obj.get("id")
			if not (required in id.lower()):
				continue
			xml_str = ET.tostring(obj, encoding='unicode')
			output_file.write(xml_str + "\n")


if __name__ == '__main__':
	outputFile = 'queriedoutput.xml'
	spriteSheetReader(INPUT_XML, outputFile)