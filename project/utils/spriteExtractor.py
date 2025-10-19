import json
import os
from PIL import Image

def extractSprites(json_path, spritesheet_path, output_dir):
    # load JSON
    with open(json_path, "r") as f:
        data = json.load(f)

    # load the PNG spritesheet
    sheet = Image.open(spritesheet_path).convert("RGBA")
    os.makedirs(output_dir, exist_ok=True)

    for sheet_entry in data.get("spritesheets", []):
        sheet_name = sheet_entry["name"]

        # create subfolder for this sheet
        sheet_dir = os.path.join(output_dir, sheet_name)
        os.makedirs(sheet_dir, exist_ok=True)

        for sprite_entry in sheet_entry["sprites"]:
            sprite_name = sprite_entry["name"]

            for frame in sprite_entry["spriteLocation"]:
                x, y, w, h = frame["position"]

                box = (int(x), int(y), int(x + w), int(y + h))
                cropped = sheet.crop(box)

                # build filename with index - this does not correspond to equip.xml or any other gamefiles
                index = frame.get("index", 0)
                filename = f"{sprite_name}_{index}.png"
                save_path = os.path.join(sheet_dir, filename)

                cropped.save(save_path)
                print(f"Saved {save_path}")


extractSprites(
    json_path="spritesheet.json",
    spritesheet_path=r"C:\Code\RotMGCalc\localfiles\spritesheets\mapObjects.png", # TODO env variable
    output_dir="output_sprites"
)