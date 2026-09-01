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
        self.groups = []            # containers, drawn behind everything
        self.nodes = []             # dicts with kind/geometry/label
        self.edges = []
        self._n = 0

    # -- elements --
    def box(self, x, y, w, h, label, accent=False, size=15, label_pos="center"):
        self._n += 1
        node = dict(id=f"n{self._n}", kind="box", x=x, y=y, w=w, h=h,
                    label=label, accent=accent, size=size, label_pos=label_pos)
        self.nodes.append(node)
        return node

    def group(self, x, y, w, h, label="", accent=False, dashed=True, size=14):
        """A labelled container -- 'Application', 'Messaging Gateway'. Drawn behind."""
        self._n += 1
        node = dict(id=f"g{self._n}", kind="group", x=x, y=y, w=w, h=h,
                    label=label, accent=accent, dashed=dashed, size=size,
                    label_pos="top")
        self.groups.append(node)
        return node

    def msg(self, x, y, label="", accent=False, w=20, h=14, size=12):
        """A message on a channel -- a small envelope. Its own element because the
        EIP figures put messages *in* the pipe, and that is what makes them read."""
        self._n += 1
        node = dict(id=f"m{self._n}", kind="msg", x=x, y=y, w=w, h=h,
                    label=label, accent=accent, size=size, label_pos="center")
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

    def arrow(self, src, dst, label="", accent=False, dashed=False,
              via=None, sides=None, lx=0, ly=0, muted=False):
        """src/dst may be a node or a bare (x, y) point.

        via     -- waypoints, for a divert or a return path that must not cut a corner
        sides   -- ("r", "l") to pin which edge it leaves and enters, overriding the
                   automatic choice; any of l/r/t/b, or None for automatic
        lx, ly  -- nudge the label off the line where it would otherwise sit on it
        """
        ss, ds = (sides or (None, None))
        self.edges.append(dict(src=src, dst=dst, label=label, accent=accent,
                               dashed=dashed, via=list(via or []), ssid=ss, dsid=ds,
                               lx=lx, ly=ly, muted=muted))

    def attach(self, src, dst, via=None, sides=None):
        """A dashed 'this belongs to that' tie -- e.g. a service to its database."""
        ss, ds = (sides or (None, None))
        self.edges.append(dict(src=src, dst=dst, label="", accent=False,
                               dashed=True, plain=True, via=list(via or []),
                               ssid=ss, dsid=ds, lx=0, ly=0, muted=False))

    # -- geometry helpers --
    _SIDES = {"l": (0.0, 0.5), "r": (1.0, 0.5), "t": (0.5, 0.0), "b": (0.5, 1.0)}

    @staticmethod
    def _centre(o):
        return o if isinstance(o, tuple) else (o["x"] + o["w"] / 2, o["y"] + o["h"] / 2)

    @classmethod
    def _side_point(cls, n, side):
        fx, fy = cls._SIDES[side]
        return (n["x"] + n["w"] * fx, n["y"] + n["h"] * fy)

    @staticmethod
    def _auto_point(n, toward):
        """Leave by whichever edge actually faces the next point."""
        cx, cy = n["x"] + n["w"] / 2, n["y"] + n["h"] / 2
        tx, ty = toward
        if abs(tx - cx) >= abs(ty - cy):
            return (n["x"] + n["w"], cy) if tx > cx else (n["x"], cy)
        return (cx, n["y"] + n["h"]) if ty > cy else (cx, n["y"])

    def _points(self, e):
        """The full polyline for an edge: source anchor, waypoints, target anchor."""
        src, dst, via = e["src"], e["dst"], e.get("via") or []
        nxt = via[0] if via else self._centre(dst)
        prv = via[-1] if via else self._centre(src)
        if isinstance(src, tuple):
            p1 = src
        elif e.get("ssid"):
            p1 = self._side_point(src, e["ssid"])
        else:
            p1 = self._auto_point(src, nxt)
        if isinstance(dst, tuple):
            p2 = dst
        elif e.get("dsid"):
            p2 = self._side_point(dst, e["dsid"])
        else:
            p2 = self._auto_point(dst, prv)
        return [p1] + list(via) + [p2]

    @staticmethod
    def _mid(pts):
        """Midpoint of the polyline -- the middle segment, not the chord."""
        i = (len(pts) - 1) // 2
        (x1, y1), (x2, y2) = pts[i], pts[i + 1]
        return (x1 + x2) / 2, (y1 + y2) / 2

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
            f'<marker id="arM" markerWidth="9" markerHeight="9" refX="6.5" refY="3" orient="auto">'
            f'<path d="M0,0 L6,3 L0,6" fill="none" stroke="{MUTED}" stroke-width="1.3" '
            f'stroke-linecap="round"/></marker>'
            '</defs>')
        o.append(f'<rect width="{W}" height="{H}" fill="{MANILA if self.panel else PAPER}"/>')

        # containers first, so everything else sits inside them
        o.append('<g filter="url(#wob)" fill="none" stroke-linecap="round" '
                 'stroke-linejoin="round">')
        for g in self.groups:
            c = ANNOTATION if g.get("accent") else MUTED
            dash = ' stroke-dasharray="6 5"' if g.get("dashed") else ""
            o.append(f'<rect x="{g["x"]}" y="{g["y"]}" width="{g["w"]}" height="{g["h"]}" '
                     f'rx="6" stroke="{c}" stroke-width="1.4"{dash}/>')
        o.append('</g>')

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
            elif n["kind"] == "msg":
                x, y, w, h = n["x"], n["y"], n["w"], n["h"]
                o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="1.5" '
                         f'fill="{PAPER}" stroke="{c}" stroke-width="1.4"/>')
                o.append(f'<path d="M{x},{y} L{x+w/2},{y+h*0.55} L{x+w},{y}" '
                         f'stroke="{c}" stroke-width="1.2"/>')
            elif n["kind"] == "pipe":
                x, y, w, h = n["x"], n["y"], n["w"], n["h"]
                o.append(f'<path d="M{x},{y} h{w} M{x},{y+h} h{w}" stroke="{c}" stroke-width="1.7"/>')
                o.append(f'<ellipse cx="{x}" cy="{y+h/2}" rx="{max(3,h/3)}" ry="{h/2}" '
                         f'stroke="{c}" stroke-width="1.4"/>')
        for e in self.edges:
            pts = self._points(e)
            col = MUTED if (e.get("plain") or e.get("muted")) else (
                ANNOTATION if e["accent"] else CARBON)
            dash = ' stroke-dasharray="3 4"' if e["dashed"] else ""
            mark = "" if e.get("plain") else (
                ' marker-end="url(#arR)"' if e["accent"] else
                ' marker-end="url(#arM)"' if e.get("muted") else ' marker-end="url(#ar)"')
            d = "M" + " L".join(f"{x},{y}" for x, y in pts)
            o.append(f'<path d="{d}" stroke="{col}" stroke-width="1.8"{dash}{mark}/>')
        o.append('</g>')

        # text, outlined -- deliberately NOT wobbled, so labels stay legible
        for g in self.groups:
            if not g["label"]:
                continue
            col = ANNOTATION if g.get("accent") else MUTED
            self._text(o, g["label"], g["x"] + 10, g["y"] + g.get("size", 14) + 2,
                       g.get("size", 14), col, "start")
        for n in self.nodes:
            if not n["label"]:
                continue
            if n["kind"] == "note":
                self._text(o, n["label"], n["x"], n["y"], n.get("size", 14),
                           n.get("color", MUTED), n.get("anchor", "middle"))
            else:
                size = n.get("size", 15)
                col = ANNOTATION if n.get("accent") else INK
                cx = n["x"] + n["w"] / 2
                if n.get("label_pos") == "top":
                    cy = n["y"] + size + 2
                else:
                    cy = n["y"] + n["h"] / 2 + size / 3
                self._text(o, n["label"], cx, cy, size, col, "middle")
        for e in self.edges:
            if not e["label"]:
                continue
            mx, my = self._mid(self._points(e))
            col = MUTED if e.get("muted") else (ANNOTATION if e["accent"] else CARBON)
            self._text(o, e["label"], mx + e.get("lx", 0), my - 7 + e.get("ly", 0),
                       15, col, "middle")

        o.append('</svg>')
        return "\n".join(o)

    @classmethod
    def _text(cls, out, text, x, y, size, color, anchor, family=HAND):
        if "\n" in text:                       # stack the lines, block-centred on y
            lines = text.split("\n")
            lead = size * 1.05
            top = y - (len(lines) - 1) * lead / 2
            for i, line in enumerate(lines):
                cls._text(out, line, x, top + i * lead, size, color, anchor, family)
            return
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

        # containers first so they land behind, and so a reader can drag the whole
        # group in draw.io without the members jumping out of it
        for g in self.groups:
            col = ANNOTATION if g.get("accent") else MUTED
            style = (base + "rounded=1;arcSize=8;verticalAlign=top;align=left;"
                     "spacingLeft=8;spacingTop=2;fillColor=none;"
                     f"strokeColor={col};strokeWidth=1.4;fontColor={col};"
                     f"fontSize={g.get('size',14)};")
            if g.get("dashed"):
                style += "dashed=1;dashPattern=6 5;"
            cell = ET.SubElement(root, "mxCell", id=g["id"], value=g["label"],
                                 style=style, vertex="1", parent="1")
            ET.SubElement(cell, "mxGeometry", x=str(g["x"]), y=str(g["y"]),
                          width=str(g["w"]), height=str(g["h"])).set("as", "geometry")

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
                     "pipe": "shape=tube;",
                     "msg": "shape=message;"}[n["kind"]]
            fill = PAPER if n["kind"] == "msg" else "none"
            style = (base + shape +
                     f"strokeColor={stroke};strokeWidth=1.7;fillColor={fill};"
                     f"fontColor={stroke};fontSize={n.get('size',15)};")
            if n.get("label_pos") == "top":
                style += "verticalAlign=top;spacingTop=2;"
            if n["kind"] == "msg" and n["label"]:
                style += "verticalLabelPosition=bottom;verticalAlign=top;labelPosition=center;"
            cell = ET.SubElement(root, "mxCell", id=n["id"], value=n["label"],
                                 style=style, vertex="1", parent="1")
            ET.SubElement(cell, "mxGeometry", x=str(n["x"]), y=str(n["y"]),
                          width=str(n["w"]), height=str(n["h"])).set("as", "geometry")

        for i, e in enumerate(self.edges):
            col = MUTED if (e.get("plain") or e.get("muted")) else (
                ANNOTATION if e["accent"] else CARBON)
            style = (f"sketch=1;jiggle=2;curveFitting=1;edgeStyle=none;rounded=0;"
                     f"strokeColor={col};strokeWidth=1.8;fontFamily={HAND};fontSize=15;"
                     f"fontColor={col};html=1;")
            if e["dashed"]:
                style += "dashed=1;"
            if e.get("plain"):
                style += "endArrow=none;"
            for side, key in ((e.get("ssid"), "exit"), (e.get("dsid"), "entry")):
                if side:
                    fx, fy = self._SIDES[side]
                    style += f"{key}X={fx};{key}Y={fy};{key}Dx=0;{key}Dy=0;"
            attrs = dict(id=f"e{i}", value=e["label"], style=style, edge="1", parent="1")
            if not isinstance(e["src"], tuple):
                attrs["source"] = e["src"]["id"]
            if not isinstance(e["dst"], tuple):
                attrs["target"] = e["dst"]["id"]
            cell = ET.SubElement(root, "mxCell", **attrs)
            geo = ET.SubElement(cell, "mxGeometry", relative="1")
            geo.set("as", "geometry")
            # a bare (x, y) end has no shape to attach to, so it needs a fixed point
            for end, key in ((e["src"], "sourcePoint"), (e["dst"], "targetPoint")):
                if isinstance(end, tuple):
                    ET.SubElement(geo, "mxPoint", x=str(end[0]),
                                  y=str(end[1])).set("as", key)
            if e.get("via"):
                arr = ET.SubElement(geo, "Array")
                arr.set("as", "points")
                for vx, vy in e["via"]:
                    ET.SubElement(arr, "mxPoint", x=str(vx), y=str(vy))

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
    """Smoke test for the pipeline. The real figures live in eip_figures.py."""
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
