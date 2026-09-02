#!/usr/bin/env python3
"""Re-render the step numbers of a paper-flow PNG from its .drawio.

    python3 tools/repatch_steps.py "resources/Pre-Arrival Guest Flow"

**Why this exists.** The paper flows are hand-made draw.io files whose renders were
exported by draw.io, and there is **no drawio CLI on this machine**. When a step is
renumbered in the `.drawio` the `.png` goes stale, and the `.png` is what the deck
shows -- and what `bpmn-your-flow-side-by-side` embeds. Rather than leave the two
disagreeing until someone opens draw.io, this repaints just the numbers.

It is deliberately narrow: it only touches pixels that are already a step number.
It finds the blue `#3333FF` glyph clusters in the PNG, matches each to a numbered
cell in the `.drawio` by position, paints the old glyph out in white and draws the
new value in **Helvetica** -- draw.io's own default face, which librsvg can reach
here -- at the same centre. Everything else in the image is untouched.

If draw.io ever does re-export one of these files, its output supersedes this and
the two should agree, because the face, size, colour and position all match.
"""

import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

BLUE = "#3333FF"
FONT = "Helvetica"


def number_cells(drawio):
    """Every step-number cell: (value, centre-x, centre-y) in draw.io coordinates."""
    root = ET.fromstring(open(drawio, encoding="utf-8").read())
    out = []
    for c in root.iter("mxCell"):
        g, v = c.find("mxGeometry"), c.get("value") or ""
        if g is None or g.get("x") is None or "29px" not in v:
            continue
        m = re.search(r">(\d+)<", v)
        if not m:
            continue
        out.append((m.group(1),
                    float(g.get("x")) + float(g.get("width") or 0) / 2,
                    float(g.get("y")) + float(g.get("height") or 0) / 2))
    return out


def content_origin(drawio):
    """draw.io crops its export to the content box, so that box is the PNG origin."""
    root = ET.fromstring(open(drawio, encoding="utf-8").read())
    xs, ys = [], []
    for c in root.iter():
        if c.tag not in ("mxGeometry", "mxPoint"):
            continue
        if c.get("x") is None or c.get("y") is None:
            continue
        xs.append(float(c.get("x")))
        ys.append(float(c.get("y")))
    return min(xs), min(ys)


def glyph_boxes(png):
    """The blue clusters already in the image -- the numbers as draw.io drew them."""
    import numpy as np
    from PIL import Image
    im = np.array(Image.open(png).convert("RGB")).astype(int)
    mask = ((abs(im[:, :, 0] - 51) < 70) & (abs(im[:, :, 1] - 51) < 70)
            & (im[:, :, 2] > 200))
    ys, xs = mask.nonzero()
    boxes = []
    for x, y in sorted(zip(xs, ys)):
        for b in boxes:
            if abs(b[1] - x) < 60 and b[2] - 40 < y < b[3] + 40:
                b[0], b[1] = min(b[0], x), max(b[1], x)
                b[2], b[3] = min(b[2], y), max(b[3], y)
                b[4] += 1
                break
        else:
            boxes.append([x, x, y, y, 1])
    return [b for b in boxes if b[4] > 30], Image.open(png).size


def repatch(base):
    drawio, png = f"{base}.drawio", f"{base}.png"
    for p in (drawio, png):
        if not os.path.exists(p):
            sys.exit(f"missing {p}")
    cells = number_cells(drawio)
    ox, oy = content_origin(drawio)
    boxes, (W, H) = glyph_boxes(png)
    if len(boxes) != len(cells):
        sys.exit(f"{len(boxes)} glyphs in the png but {len(cells)} numbered cells "
                 f"in the drawio -- refusing to guess")

    pairs = []
    for b in boxes:
        cx, cy = (b[0] + b[1]) / 2, (b[2] + b[3]) / 2
        val, dx, dy = min(cells, key=lambda k: (k[1] - ox - cx) ** 2 + (k[2] - oy - cy) ** 2)
        pairs.append((val, b, dx - ox, dy - oy))

    with open(png, "rb") as fh:
        import base64
        uri = "data:image/png;base64," + base64.b64encode(fh.read()).decode()

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" '
           f'xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}">',
           f'<image x="0" y="0" width="{W}" height="{H}" xlink:href="{uri}"/>']
    for val, b, cx, cy in pairs:
        out.append(f'<rect x="{b[0]-4}" y="{b[2]-4}" width="{b[1]-b[0]+9}" '
                   f'height="{b[3]-b[2]+9}" fill="#FFFFFF"/>')
    for val, b, cx, cy in pairs:
        out.append(f'<text x="{cx}" y="{(b[2]+b[3])/2 + 9.5}" font-family="{FONT}" '
                   f'font-size="29" fill="{BLUE}" text-anchor="middle">{val}</text>')
    out.append("</svg>")

    with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False,
                                     encoding="utf-8") as tmp:
        tmp.write("\n".join(out))
        tmp_path = tmp.name
    try:
        subprocess.run(["rsvg-convert", "-w", str(W), "-h", str(H), tmp_path,
                        "-o", png], check=True, capture_output=True)
    finally:
        os.unlink(tmp_path)
    print(f"  {os.path.basename(png)}: repainted "
          f"{', '.join(v for v, *_ in sorted(pairs, key=lambda p: int(p[0])))}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for b in sys.argv[1:]:
        repatch(b.removesuffix(".drawio").removesuffix(".png"))
