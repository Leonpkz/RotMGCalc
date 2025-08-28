import struct
import json
import os
from PIL import Image

with open(r"c:\Code\RotMGCalc\localfiles\xml\spritesheetf.xml", "rb") as f:
	data = f.read()

# REFACTOR
atlas_width, atlas_height  = Image.open(r"c:\Code\RotMGCalc\localfiles\spritesheets\mapObjects.png").size

size = len(data)
atlas = {}

offset = 0
record_size = 32  # approximate record size (8 ints / 4 floats)
min_valid_type = 0x100  # minimal plausible type ID
max_valid_type = 0xFFFF

while offset < size - record_size:
	try:
		# Unpack 8 ints (32 bytes) from current offset
		block = struct.unpack_from("<8I", data, offset)

		# The fifth int is typically the type ID in your previous hit
		type_id = block[4]

		# sanity check for valid type
		if min_valid_type <= type_id <= max_valid_type:
			# Unpack first 4 floats (x, y, w, h) safely
			floats = struct.unpack_from("<4f", data, offset)
			x, y, w, h = floats

			# Skip invalid floats
			if any(map(lambda f: not isinstance(f, float) or f != f, [x, y, w, h])):
				offset += 4
				continue

			# Convert normalized floats to pixels
			x_px = max(0, min(int(x * atlas_width), atlas_width))
			y_px = max(0, min(int(y * atlas_height), atlas_height))
			w_px = max(0, min(int(w * atlas_width), atlas_width - x_px))
			h_px = max(0, min(int(h * atlas_height), atlas_height - y_px))

			atlas[hex(type_id)] = {
				"x": x_px,
				"y": y_px,
				"w": w_px,
				"h": h_px,
				"offset": hex(offset)
			}

			offset += record_size
		else:
			offset += 4

	except struct.error:
		# Move forward safely if unpacking fails
		offset += 4

# Save the pixel coordinates for 2D texture mapping
with open("sprite_lookup.json", "w") as out:
	json.dump(atlas, out, indent=2)


