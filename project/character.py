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
		# example of a character
		# <Object type="0x0300" id="Rogue">
		  #   <Class>Player</Class>
		  #   <Description>The rogue relies on his speed to deal damage at medium range while avoiding attacks.</Description>
		  #   <AnimatedTexture>
		  #     <File>players</File>
		  #     <Index>0</Index>
		  #   </AnimatedTexture>
		  #   <HitSound>player/rogue_hit</HitSound>
		  #   <DeathSound>player/rogue_death</DeathSound>
		  #   <Player />
		  #   <BloodProb>1.0</BloodProb>
		  #   <SlotTypes>2, 13, 6, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0</SlotTypes>
		  #   <Equipment>0xa14, 0xa56, 0xa78, -1, 0xa22, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1</Equipment>
		  #   <MaxHitPoints max="750">150</MaxHitPoints>
		  #   <MaxMagicPoints max="252">100</MaxMagicPoints>
		  #   <Attack max="55">16</Attack>
		  #   <Defense max="25">0</Defense>
		  #   <Speed max="65">26</Speed>
		  #   <Dexterity max="75">17</Dexterity>
		  #   <HpRegen max="40">5</HpRegen>
		  #   <MpRegen max="50">15</MpRegen>
		  #   <LevelIncrease min="25" max="25">MaxHitPoints</LevelIncrease>
		  #   <LevelIncrease min="5" max="5">MaxMagicPoints</LevelIncrease>
		  #   <LevelIncrease min="1" max="1">Attack</LevelIncrease>
		  #   <LevelIncrease min="0" max="1">Defense</LevelIncrease>
		  #   <LevelIncrease min="1" max="1">Speed</LevelIncrease>
		  #   <LevelIncrease min="2" max="2">Dexterity</LevelIncrease>
		  #   <LevelIncrease min="1" max="1">HpRegen</LevelIncrease>
		  #   <LevelIncrease min="1" max="1">MpRegen</LevelIncrease>
		  #   <UnlockLevel level="5" type="0x0307">Archer</UnlockLevel>
		  #   <UnlockCost>199</UnlockCost>
		# </Object>






