#!/usr/bin/env python3
"""Emit a diagram as BOTH editable .drawio XML and a .png preview, from one definition.

Why both from one source: draw.io XML is the canonical, editable artefact (it matches the ~40
sources already in resources/), but there is no drawio CLI on this machine, so nothing can render
it locally. Maintaining a separate preview by hand guarantees the two drift apart. This emits them
together, so they cannot.

Style comes from styles.md -- direction C, "Field Guide". Hand-drawn register, ink stroke, carbon
for flow, annotation red reserved for the one thing the diagram is about.

Fonts are outlined to vector paths with fontTools, so the preview is faithful WITHOUT installing
anything system-wide (librsvg here ignores @font-face data URIs -- verified).

    python3 tools/diagram.py --check     verify renderer and fonts
    python3 tools/diagram.py --demo      render the worked example to /tmp

Usage as a library:

    from diagram import Diagram
    d = Diagram("Point-to-Point Channel", w=260, h=170)
    a = d.box(14, 26, 86, 52, "Sender")
    b = d.box(160, 26, 86, 52, "Receiver")
    d.arrow(a, b, "message")
    d.save("resources/eip-point-to-point")
"""

import base64
import html
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")

# ---- styles.md palette -------------------------------------------------------
INK        = "#181B1F"
PAPER      = "#FDFCFA"
CARBON     = "#1D4E6B"
ANNOTATION = "#C0453B"
MANILA     = "#F3EFE6"
RULE       = "#E0D9C8"
MUTED      = "#8A8578"

HAND = "Caveat"          # diagram labels -- never body copy
PLAIN = "IBM Plex Sans"  # straight labels where a hand face would be wrong

_FONT_FILES = {
    HAND:  "Caveat.ttf",
    PLAIN: "IBMPlexSans-Variable.ttf",
    "IBM Plex Mono": "IBMPlexMono-Regular.ttf",
}


# ---- text -> vector paths ----------------------------------------------------

class _Outliner:
    """Convert a run of text into SVG path data, so no font install is needed."""

    _cache = {}

    @classmethod
    def _font(cls, family):
        if family not in cls._cache:
            from fontTools.ttLib import TTFont
            path = os.path.join(FONT_DIR, _FONT_FILES[family])
            if not os.path.exists(path):
                raise FileNotFoundError(
                    f"missing {path}\n"
                    f"  fetch it with:  see tools/README.md")
            font = TTFont(path, fontNumber=0, lazy=True)
            cls._cache[family] = font
        return cls._cache[family]

    @classmethod
    def outline(cls, text, family, size, x, y, anchor="start", weight=None):
        """Return (svg_path_d, advance_width_px)."""
        from fontTools.pens.svgPathPen import SVGPathPen
        from fontTools.pens.transformPen import TransformPen

        font = cls._font(family)
        upem = font["head"].unitsPerEm
        scale = size / upem
        cmap = font.getBestCmap()
        gs = font.getGlyphSet(location={"wght": weight}) if weight else font.getGlyphSet()
        hmtx = font["hmtx"]

        # measure first so we can honour the anchor
        advance = 0
        names = []
        for ch in text:
            gname = cmap.get(ord(ch))
            if gname is None:
                gname = ".notdef"
            names.append(gname)
            advance += hmtx[gname][0] * scale

        ox = {"start": x, "middle": x - advance / 2, "end": x - advance}[anchor]

        parts = []
        pen_x = ox
        for gname in names:
            pen = SVGPathPen(gs)
            # flip y: font units go up, SVG goes down
            tp = TransformPen(pen, (scale, 0, 0, -scale, pen_x, y))
            gs[gname].draw(tp)
            d = pen.getCommands()
            if d:
                parts.append(d)
            pen_x += hmtx[gname][0] * scale
        return " ".join(parts), advance


# ---- the diagram -------------------------------------------------------------

class Diagram:
    """A small declarative diagram. Coordinates are in diagram units (~px)."""

    def __init__(self, title, w=260, h=170, panel=False):
        self.title = title
        self.w, self.h = w, h
        self.panel = panel          # draw the manila panel behind it
        self.nodes = []             # dicts with kind/geometry/label
        self.edges = []
        self._n = 0

    # -- elements --
    def box(self, x, y, w, h, label, accent=False):
        self._n += 1
        node = dict(id=f"n{self._n}", kind="box", x=x, y=y, w=w, h=h,
                    label=label, accent=accent)
        self.nodes.append(node)
        return node

    def cylinder(self, x, y, w, h, label="", accent=False):
        self._n += 1
        node = dict(id=f"n{self._n}", kind="cyl", x=x, y=y, w=w, h=h,
                    label=label, accent=accent)
        self.nodes.append(node)
        return node

    def pipe(self, x, y, w, h, label="", accent=False):
        """An EIP channel -- a horizontal pipe."""
        self._n += 1
        node = dict(id=f"n{self._n}", kind="pipe", x=x, y=y, w=w, h=h,
                    label=label, accent=accent)
        self.nodes.append(node)
        return node

    def note(self, x, y, text, color=MUTED, size=14, anchor="middle"):
        self.nodes.append(dict(id=None, kind="note", x=x, y=y, label=text,
                               color=color, size=size, anchor=anchor))

    def arrow(self, src, dst, label="", accent=False, dashed=False):
        self.edges.append(dict(src=src, dst=dst, label=label,
                               accent=accent, dashed=dashed))

    def attach(self, src, dst):
        """A dashed 'this belongs to that' tie -- e.g. a service to its database."""
        self.edges.append(dict(src=src, dst=dst, label="", accent=False,
                               dashed=True, plain=True))

    # -- geometry helpers --
    @staticmethod
    def _anchor_pair(a, b):
        ax, ay = a["x"] + a["w"] / 2, a["y"] + a["h"] / 2
        bx, by = b["x"] + b["w"] / 2, b["y"] + b["h"] / 2
        if abs(bx - ax) >= abs(by - ay):        # mostly horizontal
            if bx > ax:
                return (a["x"] + a["w"], ay, b["x"], by)
            return (a["x"], ay, b["x"] + b["w"], by)
        if by > ay:                              # mostly vertical
            return (ax, a["y"] + a["h"], bx, b["y"])
        return (ax, a["y"], bx, b["y"] + b["h"])

    # ---- SVG preview ----
    def to_svg(self):
        W, H = self.w, self.h
        o = []
        o.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
                 f'viewBox="0 0 {W} {H}">')
        o.append(
            '<defs>'
            '<filter id="wob" x="-5%" y="-5%" width="110%" height="110%">'
            '<feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="7"/>'
            '<feDisplacementMap in="SourceGraphic" scale="1.7"/></filter>'
            f'<marker id="ar" markerWidth="9" markerHeight="9" refX="6.5" refY="3" orient="auto">'
            f'<path d="M0,0 L6,3 L0,6" fill="none" stroke="{CARBON}" stroke-width="1.3" '
            f'stroke-linecap="round"/></marker>'
            f'<marker id="arR" markerWidth="9" markerHeight="9" refX="6.5" refY="3" orient="auto">'
            f'<path d="M0,0 L6,3 L0,6" fill="none" stroke="{ANNOTATION}" stroke-width="1.3" '
            f'stroke-linecap="round"/></marker>'
            '</defs>')
        o.append(f'<rect width="{W}" height="{H}" fill="{MANILA if self.panel else PAPER}"/>')

        # shapes, wobbled together so the hand is consistent
        o.append(f'<g filter="url(#wob)" fill="none" stroke-linecap="round" stroke-linejoin="round">')
        for n in self.nodes:
            c = ANNOTATION if n.get("accent") else INK
            if n["kind"] == "box":
                o.append(f'<rect x="{n["x"]}" y="{n["y"]}" width="{n["w"]}" height="{n["h"]}" '
                         f'rx="4" stroke="{c}" stroke-width="1.7"/>')
            elif n["kind"] == "cyl":
                x, y, w, h = n["x"], n["y"], n["w"], n["h"]
                rx, ry = w / 2, min(8, h / 4)
                o.append(f'<ellipse cx="{x+rx}" cy="{y+ry}" rx="{rx}" ry="{ry}" '
                         f'stroke="{c}" stroke-width="1.7"/>')
                o.append(f'<path d="M{x},{y+ry} v{h-2*ry} a{rx},{ry} 0 0 0 {w},0 v{-(h-2*ry)}" '
                         f'stroke="{c}" stroke-width="1.7"/>')
            elif n["kind"] == "pipe":
                x, y, w, h = n["x"], n["y"], n["w"], n["h"]
                o.append(f'<path d="M{x},{y} h{w} M{x},{y+h} h{w}" stroke="{c}" stroke-width="1.7"/>')
                o.append(f'<ellipse cx="{x}" cy="{y+h/2}" rx="{max(3,h/3)}" ry="{h/2}" '
                         f'stroke="{c}" stroke-width="1.4"/>')
        for e in self.edges:
            x1, y1, x2, y2 = self._anchor_pair(e["src"], e["dst"])
            col = MUTED if e.get("plain") else (ANNOTATION if e["accent"] else CARBON)
            dash = ' stroke-dasharray="3 4"' if e["dashed"] else ""
            mark = "" if e.get("plain") else (
                ' marker-end="url(#arR)"' if e["accent"] else ' marker-end="url(#ar)"')
            o.append(f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{col}" stroke-width="1.8"'
                     f'{dash}{mark}/>')
        o.append('</g>')

        # text, outlined -- deliberately NOT wobbled, so labels stay legible
        for n in self.nodes:
            if not n["label"]:
                continue
            if n["kind"] == "note":
                self._text(o, n["label"], n["x"], n["y"], n.get("size", 14),
                           n.get("color", MUTED), n.get("anchor", "middle"))
            else:
                cx = n["x"] + n["w"] / 2
                cy = n["y"] + n["h"] / 2 + 5
                col = ANNOTATION if n.get("accent") else INK
                self._text(o, n["label"], cx, cy, 15, col, "middle")
        for e in self.edges:
            if not e["label"]:
                continue
            x1, y1, x2, y2 = self._anchor_pair(e["src"], e["dst"])
            col = ANNOTATION if e["accent"] else CARBON
            self._text(o, e["label"], (x1 + x2) / 2, (y1 + y2) / 2 - 7, 15, col, "middle")

        o.append('</svg>')
        return "\n".join(o)

    @staticmethod
    def _text(out, text, x, y, size, color, anchor, family=HAND):
        try:
            d, _ = _Outliner.outline(text, family, size, x, y, anchor,
                                     weight=600 if family == PLAIN else None)
            if d:
                out.append(f'<path d="{d}" fill="{color}"/>')
                return
        except Exception as exc:                       # pragma: no cover
            print(f"  ! outline failed ({exc}); falling back to <text>", file=sys.stderr)
        out.append(f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
                   f'fill="{color}" text-anchor="{anchor}">{html.escape(text)}</text>')

    # ---- draw.io source ----
    def to_drawio(self):
        mx = ET.Element("mxfile", host="practical-messaging", type="device")
        dia = ET.SubElement(mx, "diagram", name=self.title)
        model = ET.SubElement(dia, "mxGraphModel", dx="800", dy="600", grid="1",
                              gridSize="10", page="1",
                              pageWidth=str(self.w), pageHeight=str(self.h),
                              background=MANILA if self.panel else PAPER)
        root = ET.SubElement(model, "root")
        ET.SubElement(root, "mxCell", id="0")
        ET.SubElement(root, "mxCell", id="1", parent="0")

        base = (f"sketch=1;hachureGap=4;jiggle=2;curveFitting=1;"
                f"fontFamily={HAND};fontSize=15;html=1;")
        for n in self.nodes:
            if n["kind"] == "note":
                style = (f"text;html=1;align=center;fontFamily={HAND};"
                         f"fontSize={n.get('size',14)};fontColor={n.get('color',MUTED)};")
                cell = ET.SubElement(root, "mxCell", id=f"t{id(n)}", value=n["label"],
                                     style=style, vertex="1", parent="1")
                ET.SubElement(cell, "mxGeometry", x=str(n["x"] - 60), y=str(n["y"] - 12),
                              width="120", height="20").set("as", "geometry")
                continue
            stroke = ANNOTATION if n.get("accent") else INK
            shape = {"box": "rounded=1;arcSize=12;",
                     "cyl": "shape=cylinder3;boundedLbl=1;backgroundOutline=1;",
                     "pipe": "shape=tube;"}[n["kind"]]
            style = (base + shape +
                     f"strokeColor={stroke};strokeWidth=1.7;fillColor=none;fontColor={stroke};")
            cell = ET.SubElement(root, "mxCell", id=n["id"], value=n["label"],
                                 style=style, vertex="1", parent="1")
            ET.SubElement(cell, "mxGeometry", x=str(n["x"]), y=str(n["y"]),
                          width=str(n["w"]), height=str(n["h"])).set("as", "geometry")

        for i, e in enumerate(self.edges):
            col = MUTED if e.get("plain") else (ANNOTATION if e["accent"] else CARBON)
            style = (f"sketch=1;jiggle=2;curveFitting=1;edgeStyle=none;rounded=0;"
                     f"strokeColor={col};strokeWidth=1.8;fontFamily={HAND};fontSize=15;"
                     f"fontColor={col};html=1;")
            if e["dashed"]:
                style += "dashed=1;"
            if e.get("plain"):
                style += "endArrow=none;"
            cell = ET.SubElement(root, "mxCell", id=f"e{i}", value=e["label"], style=style,
                                 edge="1", parent="1",
                                 source=e["src"]["id"], target=e["dst"]["id"])
            ET.SubElement(cell, "mxGeometry", relative="1").set("as", "geometry")

        ET.indent(mx, space="  ")
        return ET.tostring(mx, encoding="unicode")

    # ---- output ----
    def save(self, basename, scale=3):
        """Write <basename>.drawio and <basename>.png. Returns the paths written."""
        os.makedirs(os.path.dirname(os.path.abspath(basename)) or ".", exist_ok=True)
        drawio = f"{basename}.drawio"
        png = f"{basename}.png"
        with open(drawio, "w", encoding="utf-8") as fh:
            fh.write(self.to_drawio())
        svg = self.to_svg()
        with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False,
                                         encoding="utf-8") as tmp:
            tmp.write(svg)
            tmp_path = tmp.name
        try:
            rsvg = shutil.which("rsvg-convert")
            if not rsvg:
                raise RuntimeError("rsvg-convert not found -- cannot render the preview")
            subprocess.run([rsvg, "-w", str(int(self.w * scale)), tmp_path, "-o", png],
                           check=True, capture_output=True)
        finally:
            os.unlink(tmp_path)
        return drawio, png


# ---- self-check and demo -----------------------------------------------------

def check():
    ok = True
    rsvg = shutil.which("rsvg-convert")
    print(f"rsvg-convert   {rsvg or 'MISSING'}")
    ok &= bool(rsvg)
    try:
        import fontTools
        print(f"fontTools      {fontTools.version}")
    except ImportError:
        print("fontTools      MISSING"); ok = False
    for fam, fn in _FONT_FILES.items():
        p = os.path.join(FONT_DIR, fn)
        print(f"{fam:<14} {'ok' if os.path.exists(p) else 'MISSING  ' + p}")
        ok &= os.path.exists(p)
    print("\n" + ("all good" if ok else "something is missing -- see tools/README.md"))
    return 0 if ok else 1


def demo(out=None):
    """Point-to-Point Channel -- the first of the 12 EIP replacements."""
    d = Diagram("Point-to-Point Channel", w=340, h=150)
    snd = d.box(10, 42, 84, 50, "Sender")
    rcv = d.box(246, 42, 84, 50, "Receiver")
    pipe = d.pipe(126, 56, 88, 22)
    d.arrow(snd, pipe, "")
    d.arrow(pipe, rcv, "")
    d.note(170, 34, "one message, one receiver", ANNOTATION, 16)
    d.note(170, 118, "point-to-point channel", MUTED, 14)
    out = out or os.path.join(tempfile.gettempdir(), "eip-point-to-point")
    paths = d.save(out)
    for p in paths:
        print(f"  wrote {p}  ({os.path.getsize(p):,} bytes)")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--check" in args:
        sys.exit(check())
    if "--demo" in args:
        i = args.index("--demo")
        sys.exit(demo(args[i + 1] if len(args) > i + 1 else None))
    print(__doc__)
