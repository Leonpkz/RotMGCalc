# RotMGCalc

# TBC / NOTES FOR SELF

- Crop the sprite sheets, this will allow me to search the sprites as needed
  - https://github.com/X-com/RealmShark/blob/ad8cc2e8cb54fba08e914dcb0d811408d1c858bb/src/main/java/assets/SpriteFlatBuffer.java
  - https://github.com/X-com/RealmShark/blob/ad8cc2e8cb54fba08e914dcb0d811408d1c858bb/src/main/java/assets/ImageBuffer.java
- The above will give insight on how to crop these, porting this to python seems like the solution
- Following this it would be worth a re-factor of what is currently available in my project to cut down on 
confusion as to what is required and how to acquire this, on top of this the
re-organisation and creation of directories for better future proofing

## Overview

This project is to be the "end all be all" for RotMG DPS calculators.

There are no current up-to-date calculators which check all the below boxes

- Accurate DPS representation for **all** equipment
- Exaltation & Enchantment inclusion
- Ability to save current "calculations" for later use
- Correct data (in regards to ingame updates)

One of the goals is to accurately display the above information (with some nuance in regards to Enchantments which will be explained) and maintaining data validity for the forseeable future whilst being encapsulated in an easy to update open source project.

A further ambition for this project is to include a "Stat calculator" aspect, this will allow you to use the features available to customise your gear with the exact Enchantments & buffs so that you can figure out a build which works for you or so that you dont need to spend so much time figuring it out yourself. 

## Outline

### Technology

1. Written in Python with Django as its web application framework
2. Extraction of data from RotMG using the exalt extractor https://github.com/rotmg-network/exalt-extractor
3. Possible Javascript integration in future for better UX

I have written a basic draft on the things which I believe need to be completed to achieve the most accurate possible solution, this is under outline.md
