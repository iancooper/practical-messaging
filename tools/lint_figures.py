#!/usr/bin/env python3
"""Measure every figure's labels against the shapes around them.

    python3 tools/lint_figures.py            # all nine families
    python3 tools/lint_figures.py bpmn_hotel paper_flow

Two checks, both of which found real defects the eye did not, during the label-size
sweep of 2026-09-07:

  * **a centred label wider than the shape it sits in** -- the label runs out of its
    own box. `Pay for the Booking` stopped fitting its task at 17pt; `IIP` was one
    unit proud of its packet.
  * **an edge label landing on a node** -- including on the node the edge *ends at*,
    which is where it usually happens, because a right-angled route puts the label
    right up against its destination. `room free` landed on the message marker of the
    task it labels; `the payment` sat on the boundary bar it crosses.

Neither is caught by `diagram.py`'s glyph warning, and neither is visible in the
source. **Run this after any size or geometry change**, then still look at the PNG:
this measures overlap, it does not have taste.

A hit is a report, not a failure -- some overlaps are fine, and the margin below is
deliberately generous. Exit status is 0 unless a family fails to build.
"""

import collections
import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagram import _Outliner, HAND, PLAIN                       # noqa: E402

FAMILIES = ("eip_figures", "coupling_grids", "if_later", "queues_streams",
            "integration_styles", "app_shapes", "conversations", "bpmn_hotel",
            "bpmn_shopping", "paper_flow", "flow_reactive", "asyncapi_figures")

# node kinds that belong to the BPMN vocabulary and so are set in Plex Sans
BPMN_KINDS = {"task", "event", "gateway", "choreo", "pool", "lane"}

# a label may come this close to a shape before it is reported
MARGIN = 5


def _advance(text, face, size):
    _, adv = _Outliner.outline(text, face, size, 0, 0, "middle",
                               weight=490 if face == PLAIN else None)
    return adv


def check(families=FAMILIES):
    """Yield (family, figure, kind, description) for every measured collision."""
    for fam in families:
        module = importlib.import_module(fam)
        for name, build in module.FIGURES.items():
            d = build()
            d._legible()          # sizes are only final once the floor has run

            for n in d.nodes:
                if n["kind"] == "note" or not n.get("label"):
                    continue
                if n.get("label_pos") != "center" or not n.get("w"):
                    continue
                face = PLAIN if n["kind"] in BPMN_KINDS else d.font
                for line in str(n["label"]).split("\n"):
                    adv = _advance(line, face, n["size"])
                    if adv > n["w"] - 2 * MARGIN:
                        yield (fam, name, "overflow",
                               f'{n["kind"]} label "{line}" is {adv:.0f} wide in '
                               f'{n["w"]}')

            # free text against the canvas edges. `note` is the only element whose
            # width is not declared, so it is the only one that can quietly grow off
            # the page -- and raising a floor is exactly when it does. The 18pt sweep
            # pushed three foot comments off their canvases and nothing caught it,
            # because every other check measures a label against a *shape*.
            for n in d.nodes:
                if n["kind"] != "note" or not n.get("label"):
                    continue
                face = n.get("font") or d.font
                anchor = n.get("anchor", "middle")
                for line in str(n["label"]).split("\n"):
                    adv = _advance(line, face, n["size"])
                    x0 = {"middle": n["x"] - adv / 2, "start": n["x"],
                          "end": n["x"] - adv}[anchor]
                    if x0 < MARGIN or x0 + adv > d.w - MARGIN:
                        yield (fam, name, "off-canvas",
                               f'note "{line}" spans {x0:.0f}..{x0 + adv:.0f} '
                               f'in a canvas {d.w} wide')

            # free notes against the shapes. A note is placed in open ground by hand,
            # so anything it overlaps is a mistake -- and until `compact()` moved the
            # shapes out from under them, nothing measured it. Groups are excluded:
            # a note inside a container is normal and is what a container is for.
            for n in d.nodes:
                if n["kind"] != "note" or not n.get("label"):
                    continue
                face = n.get("font") or d.font
                lines = str(n["label"]).split("\n")
                lead = n["size"] * 1.05
                top = n["y"] - (len(lines) - 1) * lead / 2
                for i, line in enumerate(lines):
                    if not line:
                        continue
                    a = _advance(line, face, n["size"])
                    anchor = n.get("anchor", "middle")
                    x0 = {"middle": n["x"] - a / 2, "start": n["x"],
                          "end": n["x"] - a}[anchor]
                    base = top + i * lead
                    y0, y1 = base - n["size"] * 0.78, base + n["size"] * 0.22
                    for m in d.nodes:
                        if m is n or m["kind"] in ("note", "rule") or not m.get("w"):
                            continue
                        if not (x0 < m["x"] + m["w"] - MARGIN
                                and x0 + a > m["x"] + MARGIN
                                and y0 < m["y"] + m["h"] - MARGIN
                                and y1 > m["y"] + MARGIN):
                            continue
                        # writing a note INSIDE a shape is a technique, not a defect --
                        # the exchange-pattern cells, the UML class body, the IN and
                        # OUT on a desk are all done that way. What is always wrong is
                        # a note lying ACROSS the shape's stroke, so only report a note
                        # that is not wholly contained.
                        if (x0 >= m["x"] and x0 + a <= m["x"] + m["w"]
                                and y0 >= m["y"] and y1 <= m["y"] + m["h"]):
                            continue
                        what = str(m.get("label", "")).replace("\n", " ") or m["kind"]
                        yield (fam, name, "note-on-shape",
                               f'note "{line}" crosses the edge of {what}')
                        break
                    else:
                        continue
                    break

            for e in d.edges:
                if not e.get("label"):
                    continue
                pts = d._points(e)
                mx, my = d._mid(pts)
                size = d._edge_pt(e)
                bpmn = e.get("bpmn")
                face = d.font if bpmn else HAND
                adv = _advance(e["label"], face, size)
                x0 = mx + e.get("lx", 0) - adv / 2
                x1 = x0 + adv
                base = my - (6 if bpmn else 7) + e.get("ly", 0)
                # the outline's own box: roughly the ascender down to the descender
                y0, y1 = base - size * 0.78, base + size * 0.22
                hit = False
                for n in d.nodes:
                    if n["kind"] in ("note", "rule") or not n.get("w"):
                        continue
                    if (x0 < n["x"] + n["w"] + MARGIN and x1 > n["x"] - MARGIN
                            and y0 < n["y"] + n["h"] + MARGIN
                            and y1 > n["y"] - MARGIN):
                        what = str(n.get("label", "")).replace("\n", " ") or n["kind"]
                        yield (fam, name, "collision",
                               f'edge label "{e["label"]}" lands on {what}')
                        hit = True
                        break
                if hit:
                    continue
                # an edge label sitting across its OWN line. A label on a horizontal
                # run sits above the stroke and is fine -- that is how every figure in
                # the deck is drawn. On a vertical run there is no "above", so `_mid`
                # puts the text straight through the line. Nothing caught this until
                # `compact()` moved two fan-out labels onto their own risers.
                sx0, sy0 = pts[max(0, (len(pts) - 1) // 2)]
                sx1, sy1 = pts[max(0, (len(pts) - 1) // 2) + 1]
                if abs(sx1 - sx0) < abs(sy1 - sy0) and x0 - MARGIN < sx0 < x1 + MARGIN:
                    yield (fam, name, "on-its-line",
                           f'edge label "{e["label"]}" sits across its own vertical '
                           f'run at x={sx0:.0f}')
                    continue
                # ...and across ANY OTHER edge's vertical run, which is the same
                # defect with a different owner: "failed" cleared its own line and
                # landed on the riser of the arrow above it. Only vertical segments are
                # checked, because a horizontal stroke under a label is how every
                # figure in the deck is drawn and would be all noise.
                for o in d.edges:
                    if o is e:
                        continue
                    op = d._points(o)
                    for (ax, ay), (bx, by) in zip(op, op[1:]):
                        if abs(bx - ax) >= abs(by - ay):
                            continue
                        if not (min(ay, by) - MARGIN < y1 and max(ay, by) + MARGIN > y0):
                            continue
                        if x0 - MARGIN < ax < x1 + MARGIN:
                            yield (fam, name, "on-a-line",
                                   f'edge label "{e["label"]}" sits across the '
                                   f'"{o["label"] or "unlabelled"}" arrow at x={ax:.0f}')
                            hit = True
                            break
                    if hit:
                        break
                if hit:
                    continue
                # a container's own border. Sitting INSIDE a group is normal -- that is
                # what a group is for -- so only the two vertical edges are a defect,
                # and they are exactly where an arrow label between a box and the
                # apparatus wants to land. Nothing caught this until two labels in
                # `integration_styles` came out sitting on a dashed edge.
                for g in d.groups:
                    if g["kind"] in ("pool", "image") or not g.get("w"):
                        continue
                    if not (y0 < g["y"] + g["h"] and y1 > g["y"]):
                        continue
                    for ex in (g["x"], g["x"] + g["w"]):
                        if x0 - MARGIN < ex < x1 + MARGIN:
                            yield (fam, name, "on-border",
                                   f'edge label "{e["label"]}" crosses the '
                                   f'"{g["label"] or g["kind"]}" border at x={ex:.0f}')
                            break
                    else:
                        continue
                    break


def main(argv):
    families = [a for a in argv if not a.startswith("-")] or list(FAMILIES)
    hits = collections.defaultdict(list)
    for fam, name, kind, detail in check(families):
        hits[(fam, name)].append((kind, detail))
    for (fam, name), items in sorted(hits.items()):
        print(f"{fam}/{name}")
        for kind, detail in items:
            print(f"    {kind:10} {detail}")
    total = sum(len(v) for v in hits.values())
    print(f"\n{total} in {len(hits)} figures"
          if total else "\nno labels running out of their shape or onto another")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
