"""
This tool will be used to compare all the extracted sprites to my manually filtered list of equipment sprites and 
will take the image data for the "Unneeded sprites" by doing a comparison of what no longer exists in the filtered list

I will then store the image data as a SHA256 32 Bit hash. This hash, along with all the others, 
will be stored in a .bin file. This file can then be referenced in future sprite extractions

The idea is that each sprite is unique, thus each hash is unique, storing the hashes is very data efficient and can be 
referenced very quickly. I can then use this binary file so that any future extraction will skip these files entirely.

This will make it so that all future manual reviews (these are required, due to images needing to be labelled) will
take considerably less long, due to the fact you wont need to parse through 10k+ sprites which are entirely useless
for this situation 
"""