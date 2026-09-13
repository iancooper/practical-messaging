#!/usr/bin/env python3
"""Bring the four 2021 worked-flow exports into the notation the slide beside them teaches.

    python3 tools/repaint_paper_reds.py --check     # report, touch nothing
    python3 tools/repaint_paper_reds.py             # patch the .drawio and the .png
    python3 tools/repaint_paper_reds.py "Customer Order Errors"   # just this one

A flow whose master has no red left is reported and **not rewritten**, so a re-run
is a no-op rather than a meaningless `resources/` diff; `--force` overrides that.

**The disagreement.** `paper-worked-flows-montage` embeds four flows the delegates
built in 2021 -- `Restaurant Onboarding`, `Customer Order`, `Order Placement`,
`Order Confirmation` -- and they draw **paper moving as a red dashed arrow**. Since
`79c735c` the key beside them says paper moving is a **carbon** dashed arrow and that
**red is spent once per figure, on the one idea**. `paper-notation-key` is printed in
the delegate brief and read aloud in the exercise, so the montage was teaching a
notation the rest of the section had stopped using.

**Why this is a remap and not a re-export.** There is no draw.io CLI on this machine,
so the `.png` cannot be regenerated from the `.drawio` -- and the `.png` is what the
deck shows. But the two red layers turn out to be **two distinct pixel values**, so
they can be separated in the image exactly as `repatch_steps.py` repaints step
numbers, without opening draw.io at all:

    #CC0000   strokeColor on `endArrow=open;dashed=1` edges   -- paper moving
    #ff6666   <font color> on every text cell                 -- the commentary layer

**Both halves are annotation, and they land on different colours.** The dashed arrows
are the notation's own word for a hand-off, so they go to `CARBON`, which is what the
key says. The salmon text is the layer the delegates wrote *on top of* the flow, so it
goes to `COMMENT`. Checked against the export before choosing: the role names --
*Hungry Customer*, *Order Taker* -- are already **black** in these files, and every
salmon string is a remark or an action gloss sitting on a desk rather than the desk's
own name. So "a name is ink, a remark is comment green" is satisfied by mapping the
whole salmon layer to green; there is no name hiding in it.

**`#FF3333` is deliberately left alone.** It is a `fillColor` on `mxgraph.citrix.document`
glyphs and does not read as red in the export at all -- it is under the fold line. A
remap that chased it would repaint the paper icons themselves, which are not the
problem.

**The `.drawio` is patched too**, so the editable master and the render agree. Without
that, the next person to open the file in draw.io and export it would put the red back.
The payload is `<diagram>`-wrapped, URL-encoded, raw-deflated and base64'd, and it is
rewritten the same way -- the file stays in the form draw.io wrote it.

**Antialiasing is remapped, not thresholded.** Each reddish pixel is un-blended against
the paper to recover the alpha draw.io drew it at, then re-blended with the new colour
at that same alpha, so strokes and glyph edges keep their shape instead of growing a
hard fringe. A pixel that fits neither source within tolerance is left untouched.
"""

import base64
import os
import re
import sys
import urllib.parse
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagram import CARBON, COMMENT, PAPER                       # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "resources")

FLOWS = ("Restaurant Onboarding", "Customer Order",
         "Order Placement", "Order Confirmation")

# The same two red layers, in the three 2021 error flows on *How Do We Deal with
# Errors?*. R4-15 recorded these as "recolour = redraw" and `BACKLOG.md` G1 work,
# on the reasoning that there is no `.drawio` renderer here. That was wrong: they
# are byte-for-byte the same shape as FLOWS -- `#CC0000` on `endArrow=open;dashed=1`
# edges and `#ff6666` on the commentary text -- so the same remap does them.
ERROR_FLOWS = ("Restaurant Onboarding Errors", "Customer Order Errors",
               "Order Placement Errors")

# **The eighth, added 2026-09-12 on Ian's ruling.** It sat out R4-15 because the
# presenter note on *Your Flow, in the Standard Notation* leaned on its red, and
# the note is true as drawn: every red arrow stays one side of the heavy bar and
# the two blacks cross it. But the note's own argument is *which side of the bar*
# -- it says so, and says "it is not the arrow style" -- so one clause frees it.
# ⚑ It differs from the other seven twice over, and both are handled below rather
# than by renaming Ian's file: its master is UNCOMPRESSED, and its render is
# `<name>.png`, not `<name>.drawio.png`.
GUEST_FLOW = ("Pre-Arrival Guest Flow",)

ALL = FLOWS + ERROR_FLOWS + GUEST_FLOW

# source -> target. Keys are what draw.io wrote; the comparison is case-insensitive
# because these files use both `#CC0000` and `#ff6666`.
REMAP = {
    "#CC0000": CARBON,      # dashed paper hand-offs -- the notation conflict itself
    "#FF6666": COMMENT,     # the commentary layer the delegates wrote on top
}

TOLERANCE = 18      # max per-channel error before a pixel is left alone


def _rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def payload(path):
    """The decoded `<diagram>` XML, and a function to put it back the same way."""
    raw = open(path, encoding="utf-8").read()
    m = re.search(r"(<diagram[^>]*>)(.*?)(</diagram>)", raw, re.S)
    if not m:
        raise SystemExit(f"{path}: no <diagram> element")
    body = m.group(2).strip()

    # **draw.io writes the model two ways and both are valid**: base64 +
    # raw-deflate, or plain XML inline. Seven of the eight paper flows are
    # packed and `Pre-Arrival Guest Flow` is not, so detect it -- feeding real
    # XML to `b64decode` fails on a file that is perfectly well formed.
    if body.startswith("<mxGraphModel"):
        def repack_plain(new_xml):
            return raw[:m.start(2)] + new_xml + raw[m.end(2):]
        return body, repack_plain

    xml = urllib.parse.unquote(zlib.decompress(base64.b64decode(body), -15).decode())

    def repack(new_xml):
        z = zlib.compressobj(9, zlib.DEFLATED, -15)
        packed = z.compress(urllib.parse.quote(new_xml, safe="~()*!.'").encode())
        packed += z.flush()
        enc = base64.b64encode(packed).decode()
        return raw[:m.start(2)] + enc + raw[m.end(2):]

    return xml, repack


def patch_drawio(name, write):
    path = os.path.join(OUT, f"{name}.drawio")
    xml, repack = payload(path)
    hits = {}
    for src, dst in REMAP.items():
        n = len(re.findall(re.escape(src), xml, re.I))
        if n:
            hits[src] = n
            xml = re.sub(re.escape(src), dst, xml, flags=re.I)
    if write and hits:
        open(path, "w", encoding="utf-8").write(repack(xml))
    return hits


def patch_png(name, write):
    """Un-blend each reddish pixel against the paper, then re-blend with the target.

    Two sources have to be told apart and one of them is `#ff6666`, whose red channel
    is saturated -- so its alpha can only be read off green and blue, and a *pale*
    `#CC0000` pixel fits it almost as well. Both are fitted and the better fit wins,
    which separates them cleanly: a true `#ff6666` pixel misses the `#CC0000` model by
    about 50 on the red channel, well outside tolerance.
    """
    import numpy as np
    from PIL import Image

    # `resources/` uses two naming conventions -- see CLAUDE.md. Seven flows
    # render to `<name>.drawio.png`; the eighth is a bare `<name>.png`.
    path = os.path.join(OUT, f"{name}.drawio.png")
    if not os.path.exists(path):
        path = os.path.join(OUT, f"{name}.png")
    im = Image.open(path)
    arr = np.array(im.convert("RGB")).astype(float)
    bg = np.array(_rgb(PAPER), dtype=float)

    # draw.io exports on white, not on our paper cream; un-blend against what is
    # actually there or every stroke picks up a tint it never had.
    white = np.array([255.0, 255.0, 255.0])

    best_err = np.full(arr.shape[:2], float(TOLERANCE) + 1)
    best_new = arr.copy()
    for src, dst in REMAP.items():
        s = np.array(_rgb(src), dtype=float)
        t = np.array(_rgb(dst), dtype=float)
        span = white - s
        usable = span > 30                      # a saturated channel carries no alpha
        alpha = ((white - arr)[:, :, usable] / span[usable]).mean(axis=2)
        alpha = np.clip(alpha, 0.0, 1.0)
        pred = alpha[:, :, None] * s + (1 - alpha[:, :, None]) * white
        err = np.abs(pred - arr).max(axis=2)
        take = (err < best_err) & (err <= TOLERANCE) & (alpha > 0.02)
        best_err = np.where(take, err, best_err)
        new = alpha[:, :, None] * t + (1 - alpha[:, :, None]) * white
        best_new = np.where(take[:, :, None], new, best_new)

    changed = int((best_err <= TOLERANCE).sum())
    if write and changed:
        out = Image.fromarray(np.rint(best_new).astype("uint8"))
        if im.mode == "RGBA":
            out.putalpha(im.getchannel("A"))
        out.save(path)
    return changed, arr.shape[0] * arr.shape[1], bg


def main(argv):
    write = "--check" not in argv
    force = "--force" in argv
    names = [a for a in argv if not a.startswith("-")] or list(ALL)
    unknown = [n for n in names if n not in ALL]
    if unknown:
        raise SystemExit(f"not a paper flow: {', '.join(unknown)}\n  known: "
                         + "\n         ".join(ALL))

    print(f"{'flow':<30} {'.drawio hits':>26}  {'px repainted':>13}")
    for name in names:
        hits = patch_drawio(name, write)
        # Only repaint the render when the master still had red in it. The remap
        # leaves ~100-250 antialias pixels behind that fit the model on a second
        # pass, so an unguarded re-run keeps nudging files that are already done
        # and shows up as a `resources/` diff that means nothing. `--force` is for
        # the one case that needs it: draw.io has re-exported a patched master.
        px, total, _ = patch_png(name, write and bool(hits or force))
        h = "  ".join(f"{k} x{v}" for k, v in sorted(hits.items())) or "none"
        note = "" if (hits or force) else "  (already carbon; not rewritten)"
        print(f"{name:<30} {h:>26}  {px:>9,} px  ({100 * px / total:.2f}%){note}")
    print("\n" + ("patched" if write else "--check: nothing written"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
