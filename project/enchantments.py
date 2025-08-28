import xml.etree.ElementTree as ET

enchantmentsXML = r'C:\Code\RotMGCalc\localfiles\xml\Enchantments.xml'

class Enchantment:
	def __init__(self):
		return

	tree = ET.parse(enchantmentsXML)
	root = tree.getroot()

	# retrieve character information from XML
	for childs in root:
		if childs.tag == 'Enchantment':
			print(childs.attrib, childs.text)
	# This is an example of an enchantment
	# <Enchantment id="Defense_Dexterity_Tradeoff_4" type="0x4C2">
    # <DisplayId>Defense -Dexterity Tradeoff IV</DisplayId>
    # <Texture>
    #   <File>enchantments16x16</File>
    #   <Index>49</Index>
    # </Texture>
    # <Description>Increases Defense by 5 decreases Dexterity by 3.8</Description>
    # <Weight>1875</Weight>
    # <CompatibleWithItemLabels>EQUIPMENT</CompatibleWithItemLabels>
    # <IncompatibleWithItemLabels />
    # <IncompatibleWithItemIds />
    # <EnchantmentLabels>STAT,DUALSTAT,DEFENSE,DEXTERITY,TRADEOFF,ROLLABLE,TIER4</EnchantmentLabels>
    # <IncompatibleWithEnchantmentLabels>DUALSTAT</IncompatibleWithEnchantmentLabels>
    # <Mutators>
    #   <ActivateOnEquip stat="DEF" amount="5">IncrementStat</ActivateOnEquip>
    #   <ActivateOnEquip stat="DEX" amount="-3.8">IncrementStat</ActivateOnEquip>
    # </Mutators>
    # <PowerLevelAdd>0</PowerLevelAdd>
    # <PowerLevelMult>1</PowerLevelMult>