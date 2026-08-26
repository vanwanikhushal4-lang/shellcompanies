#!/usr/bin/env python3
from pathlib import Path

from PIL import Image, ImageDraw


source = Path("/Users/apple/Downloads/Shell companies/tmp/spreadsheet_previews/company_intelligence_pilot")
output = source / "all_sheets_contact.png"
files = sorted(p for p in source.glob("*.png") if p.name != output.name)
thumb_width = 900
label_height = 34
gap = 18
thumbs = []
for file in files:
    image = Image.open(file).convert("RGB")
    scale = min(1.0, thumb_width / image.width)
    thumb = image.resize((round(image.width * scale), round(image.height * scale)))
    canvas = Image.new("RGB", (thumb_width, label_height + thumb.height), "white")
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, thumb_width, label_height), fill="#132238")
    draw.text((10, 8), file.stem.replace("_", " ").title(), fill="white")
    canvas.paste(thumb, (0, label_height))
    thumbs.append(canvas)

cols = 2
rows = (len(thumbs) + cols - 1) // cols
row_heights = []
for row in range(rows):
    row_heights.append(max((thumbs[i].height for i in range(row * cols, min((row + 1) * cols, len(thumbs)))), default=0))
sheet = Image.new("RGB", (cols * thumb_width + (cols + 1) * gap, sum(row_heights) + (rows + 1) * gap), "#DCE3EA")
y = gap
for row in range(rows):
    for col in range(cols):
        idx = row * cols + col
        if idx >= len(thumbs):
            break
        sheet.paste(thumbs[idx], (gap + col * (thumb_width + gap), y))
    y += row_heights[row] + gap
sheet.save(output)
print(output)
