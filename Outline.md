
#### Method
**Make calculations based on data provided in XML and based on verified formulae** 
- [**Character stat calucations**](https://www.realmeye.com/wiki/character-stats)
- Each **Character** is its own object
	- **Character** can be saved, for later import
- Each **Character** is ran through a calculation
	- **Exaltations** 
		- Raw % dmg increase (Added on top of everything)
		- Stat increases
	- **Weapon** / **Ability** / **Armour** / **Ring** damage all included
	- **Retaliation damage on Enchantments**
		- The addition of **Enchantments** in their entirety, including "Incompatible Labels"
	- Think about the order of calculation
		- Defense - **DEFENSE CAP AT 90%**
		- Armour Piercing
		- Buffs
		- Accuracy (Weapon / Ability)

As a later calculation figure out and display **passive statistics**	

# Detail

### Character
- Data 
	- Life / Mana / Att / Def / Spd / Dex / Vit / Wis - **Hard stats for each class**
		- *Each stat will be configurable per Character*
	- **Exaltations** 
		- % damage increase
		- Stats added onto **hard stats**
	- Pet - How this affects Wis, should just be a flat addition but have to bear in mind combat
	- **Equipment** 
		- **Flat stat modifiers for ALL**
		- **Enchantments for ALL** - **0-4 Slot**
			- **Flat** stats
			- **On Ability/Shot/Hit** stat increase enchantments = Assuming constant activation, average value increase over **x** (time)
			- **Bonus** stat calculations are made **after** all other flat stat increases
			- **Tradeoff** stats
			- **Specific enchantments**
				- **Weapon / Ability / Armour / Ring**
				- **Awakened**
			- *Consider incompatible enchantments*
		- Weapon
			- Accuracy - Flat value
			- Fire rate
			- Min / Max DPS - random(Min, Max)
			- Armour piercing
			- Shot count
			- **"Special" weapons - Divinity - Valor**
				- For example 600-800 damage per second
				- Reactive proc
		- Ability
			- Accuracy (if applicable)
			- StatMod
			- On use stat modifications
			- DPS
			- Armour piercing
		- Armour
			- On use stat modifications
			- Misc. effects
				- Reactive proc
		- Ring 
			- On use stat modifications
			- Misc. effects
				- Reactive pr oc
	- **Buffs currently active - DPS**
		- Berserk & Damaging - [Attack speed / Damage Dealt](https://www.realmeye.com/wiki/character-stats#dexterity) 
		- Stat increase (Armour, Ring, Enchantment)
			- Stat reduction 
		- Weak
	- **Passive buffs**
		- Energized +10mp/s (relative to WIS)
		- Healing +20hp/s

Calculate all stats based on the information above, this will then be packaged as some form of object which can be used in the damage calculation.

### Damage Calculation / Enemy
Enemy object, import of in game data TBC, will be flat calculations based on set values.

Raw calculations based on the data from the **Character**.

- Data
	- **Defense**
	- **Status effects**
		- Armoured
		- Armour broken
		- Curse 25%^ (Last calculation?)
		- Exposed -20 Def (Can go below 0)
