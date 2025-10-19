#!/usr/bin/env python3
"""
build_spritesheet.py

Pack many item PNGs into one or more spritesheet PNGs and a JSON atlas.

- Expects item images named as "<item_id>.png"
- Outputs:
  - spritesheet.png (or spritesheet_0.png, spritesheet_1.png, ... if multiple)
  - spritesheet.json mapping item_id -> { sheet, x, y, w, h }

Why:
- Avoid serving 30k+ separate images by shipping a single (or few) sprite sheet(s)
- Greatly reduces HTTP requests and improves page load times

Requirements:
- Python 3.8+
- Pillow (PIL): pip install Pillow

Typical usage:
  python tools/build_spritesheet.py \
    --input ../img \
    --out-dir ../public \
    --basename spritesheet \
    --max-size 8192 \
    --padding 1

Notes:
- This script reads image headers to get width/height first (low memory),
  then does a second pass to paste them onto the final sheet(s).
- By default it will attempt to pack everything into a single spritesheet
  up to --max-size. If it doesn't fit, it will automatically spill over
  to multiple sheets named <basename>_0.png, <basename>_1.png, etc.
- If you want to ensure single file output only, pass --single-sheet to
  raise an error if it doesn't fit.

JSON Schema example:
{
  "meta": {
    "generated": "2025-09-22T12:34:56Z",
    "tool": "build_spritesheet.py",
    "input": "path/to/img",
    "padding": 1,
    "max_size": 8192,
    "sheet_count": 1,
    "sheets": [
      {"file": "spritesheet.png", "w": 4096, "h": 3872}
    ]
  },
  "sprites": {
    "12345": {"sheet": "spritesheet.png", "x": 16, "y": 32, "w": 16, "h": 16},
    "67890": {"sheet": "spritesheet.png", "x": 48, "y": 32, "w": 16, "h": 16}
  }
}
"""

from __future__ import annotations

import argparse
import json
import math
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

try:
    from PIL import Image
except Exception as e:
    raise SystemExit(
        f"Pillow is required. Install it with: pip install Pillow\nImport error: {e}"
    )


# -------------------------
# Packing: simple shelf packer
# -------------------------


@dataclass
class Rect:
    id: str
    path: str
    w: int
    h: int


@dataclass
class Placed:
    rect: Rect
    x: int
    y: int
    sheet_index: int


class ShelfPacker:
    """
    A straightforward shelf bin-packer:
    - Sort rectangles by height (desc) before adding
    - Fill the current shelf left-to-right
    - When out of horizontal space, start a new shelf
    - When out of vertical space, report "doesn't fit" so caller can start a new sheet

    This is not as optimal as MaxRects, but quite efficient and simple.
    """

    def __init__(self, max_w: int, max_h: int, padding: int = 1):
        self.max_w = max_w
        self.max_h = max_h
        self.padding = padding

        # Current shelf info
        self.current_x = padding
        self.current_y = padding
        self.shelf_h = 0

        # Track used bounds to crop final image
        self.used_w = 0
        self.used_h = 0

        # List of placements (Rect -> (x, y))
        self.placements: List[Tuple[Rect, int, int]] = []

    def try_place(self, rect: Rect) -> bool:
        rw = rect.w
        rh = rect.h
        pad = self.padding

        # If this is the first in a shelf, shelf height becomes rect height (plus padding)
        if self.shelf_h == 0:
            self.shelf_h = rh + pad

        # Does it fit horizontally in current shelf?
        if self.current_x + rw + pad <= self.max_w:
            x, y = self.current_x, self.current_y
            self.placements.append((rect, x, y))

            self.current_x += rw + pad
            # Update used bounds
            self.used_w = max(self.used_w, x + rw + pad)
            self.used_h = max(self.used_h, y + rh + pad)
            return True

        # If not, move to a new shelf (increase current_y by shelf height, reset x)
        new_y = self.current_y + self.shelf_h
        if new_y + rh + pad > self.max_h:
            # Doesn't fit vertically in this sheet
            return False

        self.current_y = new_y
        self.current_x = pad
        self.shelf_h = rh + pad

        # Place now at start of new shelf
        x, y = self.current_x, self.current_y
        self.placements.append((rect, x, y))

        self.current_x += rw + pad
        self.used_w = max(self.used_w, x + rw + pad)
        self.used_h = max(self.used_h, y + rh + pad)
        return True

    def dims_used(self) -> Tuple[int, int]:
        # Clamp at least to 1x1 to avoid invalid sizes
        w = max(1, min(self.max_w, self.used_w))
        h = max(1, min(self.max_h, self.used_h))
        return (w, h)


# -------------------------
# Utility
# -------------------------


def iter_pngs(input_dir: str, recursive: bool = False):
    """
    Yield (absolute_path, filename) for .png files in input_dir.
    Does not load image data here, just lists files.
    """
    if recursive:
        for root, _dirs, files in os.walk(input_dir):
            for f in files:
                if f.lower().endswith(".png"):
                    yield os.path.join(root, f), f
    else:
        for f in os.listdir(input_dir):
            if f.lower().endswith(".png"):
                yield os.path.join(input_dir, f), f


def load_image_size(path: str) -> Tuple[int, int]:
    """
    Open an image to read its size with minimal cost.
    """
    with Image.open(path) as im:
        im.load()  # Ensure header is read; still cheap for size
        return im.size


def natural_key(s: str) -> Tuple:
    """
    Sort keys 'naturally', attempting to place numeric filenames properly.
    E.g., '10.png' after '2.png', etc.
    """
    import re

    return tuple(int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s))


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def write_json(path: str, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_png(
    path: str, image: Image.Image, optimize: bool = True, compress_level: int = 9
):
    # Pillow 'optimize' can be CPU heavy but helps reduce file size
    image.save(path, format="PNG", optimize=optimize, compress_level=compress_level)


# -------------------------
# Main logic
# -------------------------


def build_spritesheet(
    input_dir: str,
    out_dir: str,
    basename: str,
    max_size: int,
    padding: int,
    bg_color: str,
    single_sheet: bool,
    recursive: bool,
) -> Tuple[List[str], Dict[str, dict]]:
    """
    Returns:
      - list of generated sheet file paths (relative names)
      - mapping of id -> sprite meta { sheet, x, y, w, h }
    """
    # Collect PNGs
    files = list(iter_pngs(input_dir, recursive=recursive))
    if not files:
        raise RuntimeError(f"No .png files found in {input_dir}")

    # Parse rects: read sizes (lazy, only headers)
    rects: List[Rect] = []
    for abspath, filename in sorted(files, key=lambda x: natural_key(x[1])):
        stem = os.path.splitext(filename)[0]
        try:
            w, h = load_image_size(abspath)
        except Exception as e:
            print(f"[WARN] Skipping {filename}: cannot read size ({e})")
            continue
        rects.append(Rect(id=stem, path=abspath, w=w, h=h))

    if not rects:
        raise RuntimeError("No readable PNGs found to pack.")

    # Sort rects by height desc, then width desc for better packing
    rects.sort(key=lambda r: (-r.h, -r.w, natural_key(r.id)))

    # Attempt to pack into sheets
    sheet_index = 0
    all_placements: List[Placed] = []
    sheet_packers: List[ShelfPacker] = []

    current = ShelfPacker(max_size, max_size, padding)
    sheet_packers.append(current)

    for r in rects:
        ok = current.try_place(r)
        if not ok:
            if single_sheet:
                raise RuntimeError(
                    f"Sprites do not fit into a single sheet of size {max_size}x{max_size}. "
                    f"Try increasing --max-size or remove --single-sheet."
                )
            # Create next sheet and place
            sheet_index += 1
            current = ShelfPacker(max_size, max_size, padding)
            sheet_packers.append(current)
            ok2 = current.try_place(r)
            if not ok2:
                raise RuntimeError(
                    f"Rect {r.id} ({r.w}x{r.h}) cannot fit in empty sheet of {max_size}x{max_size}."
                )

    # Build placements with sheet indices
    placements_by_sheet: List[List[Tuple[Rect, int, int]]] = []
    start = 0
    for packer in sheet_packers:
        count = len(packer.placements)
        placements_by_sheet.append(packer.placements)
        start += count

    # Create output images and paste
    ensure_dir(out_dir)
    sheet_files: List[str] = []
    id_to_meta: Dict[str, dict] = {}

    # Parse bg_color (#RRGGBBAA or #RRGGBB)
    bg = bg_color
    if bg.startswith("#"):
        bg = bg[1:]
    if len(bg) == 6:
        # add full alpha
        bg_rgba = tuple(int(bg[i : i + 2], 16) for i in (0, 2, 4)) + (0,)
    elif len(bg) == 8:
        bg_rgba = tuple(int(bg[i : i + 2], 16) for i in (0, 2, 4, 6))
    else:
        raise ValueError("Invalid --background color. Use #RRGGBB or #RRGGBBAA.")

    for idx, packer in enumerate(sheet_packers):
        used_w, used_h = packer.dims_used()
        # Create minimal sized sheet for used area
        sheet = Image.new("RGBA", (used_w, used_h), color=bg_rgba)

        # Determine file name
        if len(sheet_packers) == 1:
            sheet_name = f"{basename}.png"
        else:
            sheet_name = f"{basename}_{idx}.png"
        sheet_path = os.path.join(out_dir, sheet_name)

        # Paste sprites
        # Iterate over placements in this packer
        for rect, x, y in packer.placements:
            # Open and paste
            with Image.open(rect.path) as im:
                if im.mode != "RGBA":
                    im = im.convert("RGBA")
                sheet.paste(im, (x, y))

            # Save meta
            id_to_meta[rect.id] = {
                "sheet": sheet_name,
                "x": x,
                "y": y,
                "w": rect.w,
                "h": rect.h,
            }

        # Save the sheet
        save_png(sheet_path, sheet, optimize=True, compress_level=9)
        sheet_files.append(sheet_name)
        print(
            f"[OK] Wrote sheet: {sheet_path} ({used_w}x{used_h}) with {len(packer.placements)} sprites"
        )

    return sheet_files, id_to_meta


def main():
    parser = argparse.ArgumentParser(
        description="Pack item PNGs into a spritesheet and JSON atlas"
    )
    parser.add_argument(
        "--input",
        type=str,
        default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "img")),
        help="Path to input directory containing <id>.png images (default: ../img relative to this script)",
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
        help="Directory to write spritesheet(s) and JSON (default: project root)",
    )
    parser.add_argument(
        "--basename",
        type=str,
        default="spritesheet",
        help="Base name for output files (default: spritesheet)",
    )
    parser.add_argument(
        "--max-size",
        type=int,
        default=8192,
        help="Max width/height of a sheet (default: 8192). Use 4096 if targeting older GPUs/browsers.",
    )
    parser.add_argument(
        "--padding",
        type=int,
        default=1,
        help="Padding (in pixels) between sprites to avoid bleeding (default: 1)",
    )
    parser.add_argument(
        "--background",
        type=str,
        default="#00000000",
        help="Background color in #RRGGBB or #RRGGBBAA (default: transparent)",
    )
    parser.add_argument(
        "--single-sheet",
        action="store_true",
        help="Fail if sprites cannot fit into one sheet (default: allows multiple sheets)",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recurse into subdirectories of --input to find PNG files",
    )

    args = parser.parse_args()

    input_dir = os.path.abspath(args.input)
    out_dir = os.path.abspath(args.out_dir)

    if not os.path.isdir(input_dir):
        raise SystemExit(f"Input directory not found: {input_dir}")

    print(f"[INFO] Scanning input: {input_dir}")
    print(f"[INFO] Output directory: {out_dir}")
    print(
        f"[INFO] Max sheet size: {args.max_size}x{args.max_size} | Padding: {args.padding}"
    )
    print(
        f"[INFO] Background: {args.background} | Single sheet: {args.single_sheet} | Recursive: {args.recursive}"
    )

    sheets, sprites = build_spritesheet(
        input_dir=input_dir,
        out_dir=out_dir,
        basename=args.basename,
        max_size=args.max_size,
        padding=args.padding,
        bg_color=args.background,
        single_sheet=args.single_sheet,
        recursive=args.recursive,
    )

    meta = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "tool": "build_spritesheet.py",
        "input": input_dir,
        "padding": args.padding,
        "max_size": args.max_size,
        "sheet_count": len(sheets),
        "sheets": [],
    }

    # Determine each sheet's actual size by opening saved image headers (cheap)
    for name in sheets:
        path = os.path.join(out_dir, name)
        try:
            with Image.open(path) as im:
                w, h = im.size
        except Exception:
            w = h = None
        meta["sheets"].append({"file": name, "w": w, "h": h})

    atlas = {
        "meta": meta,
        "sprites": sprites,
    }

    json_path = os.path.join(out_dir, f"{args.basename}.json")
    write_json(json_path, atlas)
    print(f"[OK] Wrote atlas JSON: {json_path}")

    if len(sheets) > 1 and args.single_sheet:
        # Should not happen (we error earlier), but guard for consistency
        raise SystemExit("Multiple sheets generated while --single-sheet was set.")


if __name__ == "__main__":
    main()
