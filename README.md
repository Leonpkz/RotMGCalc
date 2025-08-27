# RotMGCalc

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

1. Written in python with Django as its web application framework
2. Extraction of data from RotMG using the exalt extractor https://github.com/rotmg-network/exalt-extractor
3. Possible Javascript integration in future for better UX

I have written a basic draft on the things which I believe need to be completed to achieve the most accurate possible solution, this is under OUTLINE.MD
