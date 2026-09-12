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
import math
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
MUTED      = "#8A8578"   # hairlines, guides, dashed ties -- NOT text
COMMENT    = "#2F5D3A"   # our remarks about the drawing

HAND = "Caveat"          # diagram labels -- never body copy
PLAIN = "IBM Plex Sans"  # straight labels where a hand face would be wrong

_FONT_FILES = {
    HAND:  "Caveat.ttf",
    PLAIN: "IBMPlexSans-Variable.ttf",
    "IBM Plex Mono": "IBMPlexMono-Regular.ttf",
    # Phase 3 only -- slide titles. No figure sets a serif label, so adding these
    # cannot move any existing drawing; `tools/build_deck.py` previews through the
    # same outliner and needs them registered here rather than keeping its own map.
    "IBM Plex Serif": "IBMPlexSerif-Regular.ttf",
    "IBM Plex Serif SemiBold": "IBMPlexSerif-SemiBold.ttf",
}

# The two registers are NOT on the same scale, and comparing their point numbers
# is what let the labels drift. Plex Sans's x-height is 0.516em against Caveat's
# 0.400 (OS/2 sxHeight, both faces at 1000upm), so 13pt of Plex reads across a
# room as 17pt of Caveat. Floors are therefore quoted in CAVEAT points and
# converted for whichever face a figure is set in -- a flat "17pt everywhere"
# would make the BPMN family a third larger than the deck around it.
X_HEIGHT = {HAND: 0.400, PLAIN: 0.516}

CONTENT_PT = 18   # anything a delegate reads off the slide and uses
ASIDE_PT   = 18   # our own remarks -- subordinate by HUE, not by being faint,
                  # so they no longer have to be small as well


# ---- text -> vector paths ----------------------------------------------------

class _Outliner:
    """Convert a run of text into SVG path data, so no font install is needed."""

    _cache = {}
    _warned = set()

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
                # .notdef draws as a hollow box, which looks deliberate in a preview
                # and is invisible in the source -- exactly the class of defect that
                # only shows up in the PNG. Say so at build time instead. Caveat is
                # the usual culprit: it has no arrows and no maths.
                if (family, ch) not in cls._warned:
                    cls._warned.add((family, ch))
                    print(f"  ! {family} has no glyph for {ch!r} (U+{ord(ch):04X}) "
                          f"— it will render as a box", file=sys.stderr)
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

    def __init__(self, title, w=260, h=170, panel=False, sketch=True, font=None,
                 transparent=False):
        """sketch=False draws straight strokes -- for a formal notation like BPMN,
        where a wobble would fight the point that this is the standard the industry
        reads. font sets the label face: HAND for our own figures, PLAIN for BPMN.

        transparent=True omits the paper ground, so the PNG carries alpha. It exists
        for ONE thing: an overlay that has to stack over another figure on a slide and
        let it show through. Every ordinary figure wants the ground -- it is the paper
        the whole deck is drawn on -- so this defaults off and nothing else sets it."""
        self.title = title
        self.w, self.h = w, h
        self.panel = panel          # draw the manila panel behind it
        self.transparent = transparent
        self.sketch = sketch
        self.font = font or HAND
        self.groups = []            # containers, drawn behind everything
        self.nodes = []             # dicts with kind/geometry/label
        self.edges = []
        self.traces = []            # fat block arrows laid OVER the drawing
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

    def msg(self, x, y, label="", accent=False, w=20, h=14, size=12,
            label_pos="center"):
        """A message on a channel -- a small envelope. Its own element because the
        EIP figures put messages *in* the pipe, and that is what makes them read.

        `label_pos="above"` / `"below"` names the envelope instead of writing inside
        it, and matters for more than layout: a node label is set in the diagram's own
        face, where `note` is always Caveat. On a BPMN choreography the message names
        are *diagram content*, not our annotation on top of it, so they have to be
        Plex Sans with everything else the notation owns."""
        self._n += 1
        node = dict(id=f"m{self._n}", kind="msg", x=x, y=y, w=w, h=h,
                    label=label, accent=accent, size=size, label_pos=label_pos)
        self.nodes.append(node)
        return node

    BAND = 26          # width of a pool's vertical title band

    # Unit pentagon, point up -- the event-based gateway's inner mark. Written out
    # rather than computed so the .drawio and the .png never depend on a float
    # library's rounding; rebuilds have to be byte-identical.
    _PENTAGON = ((0.0, -1.0), (0.951, -0.309), (0.588, 0.809),
                 (-0.588, 0.809), (-0.951, -0.309))

    @staticmethod
    def _data_uri(path):
        ext = os.path.splitext(path)[1].lower().lstrip(".")
        mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
                "gif": "image/gif"}.get(ext, "image/png")
        with open(path, "rb") as fh:
            return f"data:{mime};base64," + base64.b64encode(fh.read()).decode()

    @staticmethod
    def _symbol(out, cx, cy, kind, col, filled=False):
        """The glyph inside an event circle. Filled means a throwing event."""
        fill = col if filled else "none"
        stroke = PAPER if filled else col
        if kind == "message":
            w, h = 17, 12
            x, y = cx - w / 2, cy - h / 2
            out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" '
                       f'stroke="{col}" stroke-width="1.3"/>')
            out.append(f'<path d="M{x},{y} L{cx},{y+h*0.62} L{x+w},{y}" fill="none" '
                       f'stroke="{stroke}" stroke-width="1.3"/>')
        elif kind == "timer":
            out.append(f'<circle cx="{cx}" cy="{cy}" r="8" fill="none" stroke="{col}" '
                       f'stroke-width="1.3"/>')
            out.append(f'<path d="M{cx},{cy-5.5} v5.5 h4" fill="none" stroke="{col}" '
                       f'stroke-width="1.3"/>')
        elif kind == "compensation":
            out.append(f'<path d="M{cx-1},{cy-6} L{cx-1},{cy+6} L{cx-8},{cy} z '
                       f'M{cx+8},{cy-6} L{cx+8},{cy+6} L{cx+1},{cy} z" '
                       f'fill="{fill if filled else "none"}" stroke="{col}" '
                       f'stroke-width="1.3" stroke-linejoin="round"/>')
        # The five below exist for the delegate reference card, which is the only
        # place in either day that shows an event type the deck does not use. They
        # are the rest of the outline's own list on *BPMN — Tasks, Events and
        # Gateways*: None, Message, Time, Signal, Compensation, Conditional,
        # Escalation, Parallel, Cancel.
        elif kind == "signal":
            out.append(f'<path d="M{cx},{cy-7.5} L{cx+7.5},{cy+5.5} L{cx-7.5},{cy+5.5} z" '
                       f'fill="{fill}" stroke="{col}" stroke-width="1.3" '
                       f'stroke-linejoin="round"/>')
        elif kind == "escalation":
            out.append(f'<path d="M{cx},{cy-8} L{cx+5.5},{cy+6.5} L{cx},{cy+0.5} '
                       f'L{cx-5.5},{cy+6.5} z" fill="{fill}" stroke="{col}" '
                       f'stroke-width="1.3" stroke-linejoin="round"/>')
        elif kind == "conditional":
            out.append(f'<rect x="{cx-6}" y="{cy-7.5}" width="12" height="15" '
                       f'fill="none" stroke="{col}" stroke-width="1.3"/>')
            for i in range(3):
                out.append(f'<path d="M{cx-3.6},{cy-3.6+i*3.6} h7.2" fill="none" '
                           f'stroke="{col}" stroke-width="1.1"/>')
        elif kind == "cancel":
            out.append(f'<path d="M{cx-6},{cy-6} L{cx+6},{cy+6} M{cx+6},{cy-6} '
                       f'L{cx-6},{cy+6}" fill="none" stroke="{col}" '
                       f'stroke-width="2.6" stroke-linecap="round"/>')
        elif kind == "parallel":
            out.append(f'<path d="M{cx-6.5},{cy} h13 M{cx},{cy-6.5} v13" fill="none" '
                       f'stroke="{col}" stroke-width="2.6" stroke-linecap="round"/>')

    @staticmethod
    def _marker(out, x, y, kind, col):
        """The task-type icon in a task's top-left corner."""
        if kind in ("send", "receive"):
            w, h = 14, 10
            out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
                       f'fill="{col if kind == "send" else PAPER}" stroke="{col}" '
                       f'stroke-width="1.2"/>')
            out.append(f'<path d="M{x},{y} L{x+w/2},{y+h*0.62} L{x+w},{y}" fill="none" '
                       f'stroke="{PAPER if kind == "send" else col}" stroke-width="1.2"/>')
        elif kind == "user":
            out.append(f'<circle cx="{x+6.5}" cy="{y+3.6}" r="3.2" fill="none" '
                       f'stroke="{col}" stroke-width="1.2"/>')
            out.append(f'<path d="M{x+1},{y+12} a5.5,5.5 0 0 1 11,0" fill="none" '
                       f'stroke="{col}" stroke-width="1.2"/>')
        elif kind == "service":
            out.append(f'<circle cx="{x+6.5}" cy="{y+6.5}" r="5.4" fill="none" '
                       f'stroke="{col}" stroke-width="1.2"/>')
            out.append(f'<circle cx="{x+6.5}" cy="{y+6.5}" r="2" fill="none" '
                       f'stroke="{col}" stroke-width="1.2"/>')
        # The three below exist for the delegate reference card, which is the only
        # place in either day that shows a task type the deck does not use.
        elif kind == "manual":
            # A hand: palm, three fingers, thumb. `user` is the same work done by a
            # person *through software*, so the two glyphs have to be told apart at a
            # glance -- a head-and-shoulders against a hand. The fingers are drawn as
            # separate capsules rather than as humps on one outline, because at 13
            # units a continuous outline closes up into a mitten.
            out.append(f'<path d="M{x+3.4},{y+12.8} L{x+3.4},{y+7.6} '
                       f'C{x+3.4},{y+6.4} {x+4.4},{y+6} {x+5.4},{y+6} '
                       f'L{x+11},{y+6} C{x+12.2},{y+6} {x+12.6},{y+6.8} '
                       f'{x+12.6},{y+7.6} L{x+12.6},{y+12.8} z" fill="none" '
                       f'stroke="{col}" stroke-width="1.2" stroke-linejoin="round"/>')
            for i, top in enumerate((3.6, 2.4, 3.2)):
                fx = x + 5.2 + i * 2.6
                out.append(f'<path d="M{fx},{y+6} L{fx},{y+top+0.9} '
                           f'a0.9,0.9 0 0 1 1.8,0 L{fx+1.8},{y+6}" fill="none" '
                           f'stroke="{col}" stroke-width="1.1" '
                           f'stroke-linejoin="round"/>')
            out.append(f'<path d="M{x+3.4},{y+8.4} L{x+1},{y+9.8} '
                       f'a1.1,1.1 0 0 0 0.6,2 L{x+3.4},{y+11.4}" fill="none" '
                       f'stroke="{col}" stroke-width="1.1" stroke-linejoin="round"/>')
        elif kind == "script":
            # A page with curled top and bottom edges, and writing on it.
            out.append(f'<path d="M{x+2},{y+1.5} c2.5,2 5,-2 7.5,0 '
                       f'l1.5,0 l0,10 c-2.5,-2 -5,2 -7.5,0 l-1.5,0 z" '
                       f'fill="none" stroke="{col}" stroke-width="1.2" '
                       f'stroke-linejoin="round"/>')
            for i in range(3):
                out.append(f'<path d="M{x+3.5},{y+4+i*2.6} h5" fill="none" '
                           f'stroke="{col}" stroke-width="1"/>')
        elif kind == "rule":
            # A table: a header band across the top, then two cells. BPMN calls it
            # the business-rule marker; the table is the decision table it consults.
            out.append(f'<rect x="{x+1}" y="{y+1.5}" width="12" height="11" '
                       f'fill="none" stroke="{col}" stroke-width="1.2"/>')
            out.append(f'<path d="M{x+1},{y+5} h12 M{x+5.5},{y+5} v7.5" '
                       f'fill="none" stroke="{col}" stroke-width="1"/>')

    @staticmethod
    def _sub_marker(out, cx, cy, kind, col):
        """The marker centred on a task's bottom edge -- a loop, or a compensation.

        BPMN puts these in a different place from the type icon on purpose: the
        top-left says *what kind of work this is* and the bottom centre says *how
        many times, or under what*. A task can carry one of each.
        """
        if kind == "loop":
            out.append(f'<path d="M{cx+5.6},{cy-2.4} A6,6 0 1 0 {cx+5.6},{cy+2.4}" '
                       f'fill="none" stroke="{col}" stroke-width="1.3"/>')
            out.append(f'<path d="M{cx+2.6},{cy+2.2} L{cx+6.2},{cy+3.2} '
                       f'L{cx+5.2},{cy-0.4} z" fill="{col}" stroke="{col}" '
                       f'stroke-width="0.8" stroke-linejoin="round"/>')

    # -- Paper Flow --
    # The vocabulary the delegates draw with by hand during the exercise. Glyphs match
    # the ~15 paper-flow sources already in resources/ (a desk is a rectangle with
    # corner brackets, a tray is a document sitting in a shallow tray) so the legend
    # and the worked flows read as one notation.
    def desk(self, x, y, w, h, label="", accent=False, size=14):
        self._n += 1
        node = dict(id=f"d{self._n}", kind="desk", x=x, y=y, w=w, h=h, label=label,
                    accent=accent, size=size, label_pos="above")
        self.nodes.append(node)
        return node

    def tray(self, x, y, w, h, label="", out=False, accent=False, size=13):
        """An in-tray, or an out-tray when out=True -- the document sits proud of a
        filled tray rather than down in an empty one."""
        self._n += 1
        node = dict(id=f"y{self._n}", kind="tray", x=x, y=y, w=w, h=h, label=label,
                    out=out, accent=accent, size=size, label_pos="below")
        self.nodes.append(node)
        return node

    def folder(self, x, y, w, h, label="", accent=False, size=13):
        """The file -- what a desk knows, written down, because the clerk goes home."""
        self._n += 1
        node = dict(id=f"f{self._n}", kind="folder", x=x, y=y, w=w, h=h, label=label,
                    accent=accent, size=size, label_pos="below")
        self.nodes.append(node)
        return node

    def doc(self, x, y, w, h, label="", accent=False, size=13):
        """A loose sheet of paper -- the artefact in flight, before it lands in a
        tray or a file. The tray already draws one sitting in its tray; this is the
        same sheet on its own, for the hand-offs the guest cycle is made of."""
        self._n += 1
        node = dict(id=f"c{self._n}", kind="doc", x=x, y=y, w=w, h=h, label=label,
                    accent=accent, size=size, label_pos="below")
        self.nodes.append(node)
        return node

    def rule(self, x, y, w, color=None, weight=1.1, h=0):
        """A plain hairline: a writing rule on a printable, a divider on a card, a
        gridline on a plot. Its own element because `arrow` always draws a head, and
        neither a line you write on nor an axis may have one.

        Horizontal by default; pass `w=0, h=<len>` for a vertical one."""
        self._n += 1
        node = dict(id=f"r{self._n}", kind="rule", x=x, y=y, w=w or 1, h=h or 1,
                    label="", accent=False, size=13, label_pos="below",
                    color=color or MUTED, weight=weight, dx=w, dy=h)
        self.nodes.append(node)
        return node

    def point(self, x, y, label="", accent=False, r=7, size=14, label_pos="below"):
        """A plotted item on a grid -- a filled dot and its name. The grids are the
        one place in the deck where the *position* carries the argument, so the mark
        has to be small and exact and the label has to sit clear of it."""
        self._n += 1
        node = dict(id=f"o{self._n}", kind="point", x=x - r, y=y - r, w=2 * r,
                    h=2 * r, label=label, accent=accent, size=size,
                    label_pos=label_pos)
        self.nodes.append(node)
        return node

    def log(self, x, y, w, h, cells, label="", start=0, accent=False, size=17):
        """An append-only log: contiguous numbered cells.

        Drawn as a *different thing* from a queue on purpose. §4.5 spends ten slides
        on queue-versus-stream, and if both are a pipe with envelopes in it the room
        has to be told the difference every time instead of seeing it. A queue is
        loose envelopes in a pipe; a log is cells in a row, each with an offset, and
        nothing ever leaves it.

        Cell i has centre x + (i + 0.5) * w / cells -- compute it in the figure when
        you need to point at one.
        """
        self._n += 1
        node = dict(id=f"l{self._n}", kind="log", x=x, y=y, w=w, h=h, label=label,
                    cells=cells, start=start, accent=accent, size=size,
                    label_pos="below")
        self.nodes.append(node)
        return node

    def icon(self, x, y, kind, accent=False, r=13, label="", size=12):
        """lock | clock | tick | cross -- the four marks §4.5 leans on.

        They are one element rather than four because they only ever appear as small
        annotations on something else, and one element means one place to keep them
        consistent."""
        self._n += 1
        node = dict(id=f"k{self._n}", kind="icon", x=x - r, y=y - r, w=2 * r,
                    h=2 * r, ikind=kind, label=label, accent=accent, size=size,
                    label_pos="below")
        self.nodes.append(node)
        return node

    def phone(self, x, y, w, h, label="", accent=False, size=13):
        """A desk telephone, seen from above: handset on the left, keypad on the
        right. Matches the glyph in `resources/Paper Office.drawio`, so a drawn desk
        and the 2021 worked flows read as one office."""
        self._n += 1
        node = dict(id=f"h{self._n}", kind="phone", x=x, y=y, w=w, h=h, label=label,
                    accent=accent, size=size, label_pos="below")
        self.nodes.append(node)
        return node

    def bar(self, x, y, h, w=7, label="", size=13):
        """The heavy vertical bar: an organisational boundary."""
        self._n += 1
        node = dict(id=f"b{self._n}", kind="bar", x=x, y=y, w=w, h=h, label=label,
                    accent=False, size=size, label_pos="below")
        self.nodes.append(node)
        return node

    def step(self, x, y, n, r=13):
        """A numbered step marker, as the paper flows number their sequence."""
        self._n += 1
        node = dict(id=f"s{self._n}", kind="step", x=x - r, y=y - r, w=2 * r, h=2 * r,
                    label=str(n), accent=False, size=14, label_pos="center")
        self.nodes.append(node)
        return node

    # -- BPMN --
    def pool(self, x, y, w, h, label, lanes=None, accent=False):
        """A participant. `lanes` is a list of (height, label) drawn as bands inside
        it -- BPMN lanes, which is what the paper exercise's desks become."""
        self._n += 1
        node = dict(id=f"p{self._n}", kind="pool", x=x, y=y, w=w, h=h, label=label,
                    accent=accent, lanes=list(lanes or []), size=13)
        self.groups.append(node)
        return node

    def choreo(self, x, y, w, h, label, initiator, recipient, accent=False,
               band=26, size=13):
        """A BPMN choreography task. No pool owns it -- which is the point of the
        slide it is drawn for."""
        self._n += 1
        node = dict(id=f"c{self._n}", kind="choreo", x=x, y=y, w=w, h=h, label=label,
                    initiator=initiator, recipient=recipient, accent=accent,
                    band=band, size=size, label_pos="center")
        self.nodes.append(node)
        return node

    def event(self, x, y, kind="start", symbol=None, label="", accent=False, r=17,
              filled=None, nonint=False):
        """kind: start | intermediate | end.

        symbol: message | timer | compensation | signal | conditional | escalation |
        cancel | parallel, or None for a bare circle.

        The ring says *when*; the symbol's fill says *which way it points*. A hollow
        symbol is caught -- this flow waits for it; a filled one is thrown -- this
        flow raises it. `filled` defaults to the old rule (an end event throws),
        which is true of every event in the deck; the reference card is the only
        figure that needs to say a throwing *intermediate* event exists.

        `nonint` dashes the rings: a non-interrupting boundary event, where the main
        flow carries on regardless.
        """
        self._n += 1
        node = dict(id=f"e{self._n}", kind="event", x=x - r, y=y - r, w=2 * r, h=2 * r,
                    ekind=kind, symbol=symbol, label=label or "", accent=accent, size=13,
                    label_pos="below")
        if filled is not None:
            node["filled"] = filled
        if nonint:
            node["nonint"] = True
        self.nodes.append(node)
        return node

    def gateway(self, x, y, kind="exclusive", label="", accent=False, r=21):
        """kind: exclusive (X, one path) | parallel (+, split or join) |
        inclusive (O, every path whose condition holds) | complex (*) |
        event (the first event to arrive picks the path).

        The last three are on the delegate reference card and nowhere else; the deck
        itself is built from the first two.
        """
        self._n += 1
        node = dict(id=f"g{self._n}", kind="gateway", x=x - r, y=y - r, w=2 * r, h=2 * r,
                    gkind=kind, label=label or "", accent=accent, size=13,
                    label_pos="below")
        self.nodes.append(node)
        return node

    def task(self, x, y, w, h, label, marker=None, accent=False, size=13,
             sub=None, double=False):
        """marker: send | receive | service | user | manual | script | rule -- the
        icon in the task's top-left.

        sub     -- "loop", the marker centred on the bottom edge. Independent of
                   `marker`, because a task has a kind *and* a repetition.
        double  -- a transaction: a second border inside the first. It is a shape
                   type rather than a marker in BPMN, which is why it is not `sub`.
        """
        self._n += 1
        node = dict(id=f"t{self._n}", kind="task", x=x, y=y, w=w, h=h, label=label or "",
                    marker=marker, accent=accent, size=size, label_pos="center")
        if sub:
            node["sub"] = sub
        if double:
            node["double"] = True
        self.nodes.append(node)
        return node

    def flow(self, src, dst, label="", message=False, accent=False, via=None,
             sides=None, lx=0, ly=0):
        """A BPMN connector. Sequence flow is solid and carries the token; message
        flow is dashed and does not. That distinction is the section's whole point,
        so they are drawn as different things, not as one arrow with a flag."""
        ss, ds = (sides or (None, None))
        self.edges.append(dict(src=src, dst=dst, label=label, accent=accent,
                               dashed=message, via=list(via or []), ssid=ss, dsid=ds,
                               lx=lx, ly=ly, muted=False, bpmn=True, message=message))

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

    # -- dataflow / FBP --
    def node(self, x, y, w, h, label, ins=(), outs=(), accent=False,
             accent_ports=(), size=17, port_size=17, port_r=7):
        """A dataflow node / FBP component: a hexagon with named ports.

        **This is the glyph Day 2's whole flow run is built from, so it lives here
        rather than in the figure script.** Twenty-five figures draw it, and a
        component that is a hexagon in one and a rounded box in the next teaches the
        shape again instead of the idea.

        A *dataflow node* and an *FBP component* are the same glyph on purpose: the
        outline says FBP is a subclass of dataflow, and the deltas are the content.
        Drawing them differently would argue they are different things.

        **The left and right vertices are flattened into short vertical edges.** A
        true hexagon has a single point each side, so a second in-port would have to
        sit on a slant at a different x and the two would not line up. Flattening
        them means a port always lands on a stroke, however many there are.

        **Ports on the left are in, ports on the right are out, and data flows left to
        right.** Fixed here, once, because run 1's costliest mistake was settling the
        reading direction per figure and having four of them fight it.

        `ins` / `outs` are port names, in top-to-bottom order; `""` gives an
        unlabelled dot. Returns the node with `["ports"]`, keyed both by name and
        positionally as `in0`, `in1`, `out0` ... -- pass one straight to `arrow`, so
        nothing ever aims at the hexagon's own edge.
        """
        self._n += 1
        n = max(len(ins), len(outs), 1)
        slant = min(h * 0.22, h / (n + 1) - 2)
        hexn = dict(id=f"x{self._n}", kind="hex", x=x, y=y, w=w, h=h, label=label,
                    accent=accent, size=size, label_pos="center", slant=slant)
        self.nodes.append(hexn)
        hexn["ports"] = {}
        for names, px, anch, dx, key in ((ins, x, "end", -13, "in"),
                                         (outs, x + w, "start", 13, "out")):
            for i, name in enumerate(names):
                py = y + h * (i + 1) / (len(names) + 1)
                red = accent or name in accent_ports
                p = self.point(px, py, "", accent=red, r=port_r)
                # every port is reachable positionally as well as by name, so an
                # unnamed dot still has a handle and a figure never has to guess one
                hexn["ports"][f"{key}{i}"] = p
                if name:
                    hexn["ports"][name] = p
                    # a port name is the notation's own word, not our remark on it:
                    # ink, at the same size as the component's name, and bold. It sat
                    # 12 units above the dot at 14pt; at 17 it needs 14 to clear it.
                    self.note(px + dx, py - 14, name,
                              ANNOTATION if red else INK, port_size, anchor=anch,
                              weight=700)
        return hexn

    def packet(self, x, y, w=30, h=26, label="", accent=False, size=13,
               label_pos="center"):
        """An information packet -- a dashed rounded square, empty unless named.

        Deliberately **not** the `msg` envelope. An envelope is a message sitting on a
        channel, and the EIP and queue families own it; an IP is a value in flight
        between ports, with a lifetime that ends when a component consumes it. Two
        ideas, two shapes, so a reader coming from Day 1 is not told they are the
        same thing.
        """
        self._n += 1
        node = dict(id=f"q{self._n}", kind="pkt", x=x, y=y, w=w, h=h, label=label,
                    accent=accent, size=size, label_pos=label_pos)
        self.nodes.append(node)
        return node

    def image(self, x, y, w, h, path):
        """Place an existing raster inside a drawing -- for the one figure that has to
        show a delegate's own artefact beside ours. It is embedded as a data URI in
        both outputs, so neither file depends on the original staying put."""
        self._n += 1
        node = dict(id=f"i{self._n}", kind="image", x=x, y=y, w=w, h=h, label="",
                    path=os.path.abspath(path))
        self.groups.append(node)          # behind everything we draw ourselves
        return node

    def note(self, x, y, text, color=COMMENT, size=14, anchor="middle", font=None,
             weight=None):
        """Free text. Always Caveat unless `font` says otherwise, because a note is
        *our annotation on top of* a diagram -- which is exactly what Caveat means in
        this deck. Pass `font=PLAIN` only where the text is the notation's own
        vocabulary rather than our commentary on it: a column head reading "Gateways"
        on a BPMN figure is a BPMN word, and setting it in a hand face says it is a
        remark when it is a label."""
        self.nodes.append(dict(id=None, kind="note", x=x, y=y, label=text,
                               color=color, size=size, anchor=anchor, font=font,
                               weight=weight))

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

    # **A trace is not an edge, and the difference is the point.** An edge is part
    # of the drawing: it says this box talks to that one, and it is sized to sit
    # among the labels. A trace is laid *over* a finished drawing to say *follow
    # this*, and it is deliberately far too big for what is underneath -- which is
    # what lets the drawing beneath it be tiny. Ian, on the 2025 montage: *"I added
    # arrows to the diagram, colour-coded for synchronous and asynchronous
    # communication and progressively showed the arrows so that the flow could be
    # seen. **For this reason it did not matter that the scale was small.**"*
    #
    # `layer` is what makes the progressive disclosure possible, and it is only
    # bookkeeping here: the family groups its traces by it and renders one
    # transparent overlay per group, and `build_deck.py` stacks those over the base
    # with a click each. So the animation lives in the *deck*, not in the picture,
    # and nothing in the builder has to learn to animate inside a figure -- which is
    # what `REVIEW.md` R4-13 recorded as the blocker.
    def trace(self, src, dst, weight=34, sync=False, layer=0):
        """A fat block arrow over the drawing. src/dst are bare (x, y) points.

        weight  -- the shaft thickness in canvas units; the head scales off it
        sync    -- MUTED rather than CARBON. The montage's 4 synchronous arrows
                   against its 20 asynchronous ones are the section's whole
                   argument, so the asynchronous ones carry the strong colour and
                   the phone calls recede. `styles.md`: muted is for lines, and a
                   block arrow is a line.
        layer   -- which reveal step this arrow belongs to; 0 is always-on
        """
        self.traces.append(dict(src=tuple(src), dst=tuple(dst), weight=weight,
                                sync=bool(sync), layer=int(layer)))

    @staticmethod
    def _trace_poly(t):
        """The seven points of a block arrow: up one side, round the tip, back.

        base_left, neck_left, wing_left, TIP, wing_right, neck_right, base_right --
        so the tip is the middle point of the seven. Head length is capped at 45% of
        the run, or a short arrow degenerates into a triangle with a stub behind it.
        """
        (x1, y1), (x2, y2) = t["src"], t["dst"]
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy) or 1.0
        ux, uy = dx / L, dy / L
        px, py = -uy, ux
        w = t["weight"] / 2.0
        head = min(2.0 * t["weight"], 0.45 * L)
        hw = t["weight"] * 0.95
        nx, ny = x2 - ux * head, y2 - uy * head
        pts = [(x1 + px * w, y1 + py * w), (nx + px * w, ny + py * w),
               (nx + px * hw, ny + py * hw), (x2, y2),
               (nx - px * hw, ny - py * hw), (nx - px * w, ny - py * w),
               (x1 - px * w, y1 - py * w)]
        return " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)

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

    # ---- legibility ----
    def _pt(self, caveat_pt, face=None):
        """A size quoted in Caveat points, in the points of the face in use."""
        return round(caveat_pt * X_HEIGHT[HAND] / X_HEIGHT[face or self.font])

    def _legible(self):
        """Raise every label to the floor for what it is, in place.

        A label that names something in the drawing is CONTENT and gets 17pt; a
        muted remark of ours is an ASIDE and gets 14. Getting that backwards is
        what made the stream offsets and the port names unreadable on a projector,
        and it recurred everywhere because the sizes were set per element as each
        family was built and never reconciled.

        Only the hand-drawn register is swept. The BPMN figures keep the scale
        they were drawn at: Plex Sans's x-height is 1.29x Caveat's, so their 13pt
        labels already clear the floor, and the two crowded ones squeeze tasks to
        10-11pt (13-14pt of Caveat) because the boxes are small on purpose.

        Idempotent, and called from BOTH serialisers so the .drawio and the .png
        can never disagree about a size."""
        for n in self.groups + self.nodes:
            if not n.get("label"):
                continue
            face = (n.get("font") or self.font) if n["kind"] == "note" else self.font
            if face != HAND:
                continue
            floor = (ASIDE_PT if n["kind"] == "note" and n.get("color") == COMMENT
                     else CONTENT_PT)
            n["size"] = max(n.get("size", floor), floor)

    # ---- fitting a figure to the room, not to the canvas ----
    def _advance(self, n):
        """The widest line of a note, in units, at the size it will render."""
        face = (n.get("font") or self.font) if n["kind"] == "note" else self.font
        w = 0.0
        for line in str(n.get("label") or "").split("\n"):
            if line:
                w = max(w, _Outliner.outline(line, face, n["size"], 0, 0, "middle")[1])
        return w

    def _extent(self, k=1.0, ox=0.0, oy=0.0):
        """Bounding box of everything drawn, with geometry scaled by `k` about
        (ox, oy) but **text left at its own size** -- which is the whole point of
        `compact`, and the reason this cannot be a simple multiply."""
        xs, ys = [], []

        def text(n, cx, cy, anchor, size):
            a = self._advance(n)
            if not a:
                return
            x0 = {"middle": cx - a / 2, "start": cx, "end": cx - a}[anchor]
            lines = str(n["label"]).count("\n") + 1
            lead = size * 1.05
            xs.extend((x0, x0 + a))
            ys.extend((cy - (lines - 1) * lead / 2 - size * 0.9,
                       cy + (lines - 1) * lead / 2 + size * 0.3))

        for n in self.groups + self.nodes:
            if n["kind"] == "image":
                continue
            if n["kind"] == "note":
                text(n, (n["x"] - ox) * k, (n["y"] - oy) * k,
                     n.get("anchor", "middle"), n["size"])
                continue
            if not n.get("w"):
                continue
            x, y = (n["x"] - ox) * k, (n["y"] - oy) * k
            w, h = n["w"] * k, n["h"] * k
            xs.extend((x, x + w))
            ys.extend((y, y + h))
            if not n.get("label"):
                continue
            size = n.get("size", 14)
            pos = n.get("label_pos")
            if pos == "below":
                text(n, x + w / 2, y + h + size + 3, "middle", size)
            elif pos == "above":
                text(n, x + w / 2, y - 7, "middle", size)
            elif pos == "top":
                text(n, x + 10, y + size + 2, "start", size)

        for e in self.edges:
            pts = self._points(e)
            for px, py in pts:
                xs.append((px - ox) * k)
                ys.append((py - oy) * k)
            if e.get("label"):
                mx, my = self._mid(pts)
                a = _Outliner.outline(e["label"], self.font if e.get("bpmn") else HAND,
                                      self._edge_pt(e), 0, 0, "middle")[1]
                cx = (mx - ox) * k + e.get("lx", 0)
                cy = (my - oy) * k - 7 + e.get("ly", 0)
                xs.extend((cx - a / 2, cx + a / 2))
                ys.extend((cy - self._edge_pt(e), cy + 4))
        return min(xs), max(xs), min(ys), max(ys)

    K_FLOOR = 0.55        # a figure shrunk by more than this is a mistake, not a compaction
    MARKS = ("icon",)     # kinds `compact` moves but does not resize -- see below

    # The usable area of a 16:9 slide once the title and the margins are off it.
    # Wider than this is fitted by width; squarer is fitted by HEIGHT, and then the
    # width the figure was compacted to stops mattering. Plan §8 items 10 and 18.
    SLIDE_ASPECT = 2.2

    def _effective_w(self, a, b, t, c, margin):
        """The width the *room* sees, which is the only one legibility depends on.

        A figure is scaled to fit the slide, so a squarer-than-2.2:1 drawing is
        fitted by its height and every label shrinks by `2.2 x h / w` more than the
        width alone predicts. `max(w, 2.2 x h)` is that number, and it is what
        `tools/reads_at.py` measures against."""
        return max(b - a + 2 * margin, self.SLIDE_ASPECT * (c - t + 2 * margin))

    def compact(self, target, margin=40):
        """Shrink the **geometry** until the canvas's *effective* width -- what the
        room sees, `max(w, 2.2 x h)` -- is `target` units, leaving every label at the
        size the floor gave it, then crop to what is left.

        **⚑ `target` is the effective width, not `self.w`.** It used to be `self.w`,
        and that was half the rule: the 2026-09-07 sweep took eight families to 890
        and 65 of 92 figures were still under the 18pt floor, because a figure squarer
        than 2.2:1 is fitted by height and the width it was compacted to stopped
        mattering. A wide, flat figure will still land at `self.w == target`; a square
        one now lands narrower, which is the point.

        **Why this exists.** The label floor is in canvas units and a figure is scaled
        to fit its slide, so the same 18pt reads at 32 real points on a 460-unit canvas
        and at 13 on a 1300-unit one. A wide figure is not more detailed, it is just
        less legible. What makes these families wide is *distance* -- long arrow runs
        between a queue and its consumers -- and distance carries no information, so it
        is the thing to spend.

        **Type does not scale, and that is the point.** Boxes are sized for their text
        with a lot of slack (typically 3x), so a 20% shrink brings the label closer to
        filling its box, which is what you want anyway. `lint_figures.py` is the check
        that it has not gone too far.

        Text also sets a floor on how narrow the figure can get: a foot comment 700
        units wide does not shrink, so `target` is a request, not a promise. The search
        is over `k`, and the widest single label wins if it has to.
        """
        self._legible()
        # A shape may not shrink below its own label. Type does not scale, so a
        # packet 24 units wide carrying a 16-unit "IP" is the binding constraint on
        # the whole figure -- and it should be, because the alternative is a label
        # hanging out of the shape it names.
        fit = self.K_FLOOR
        for n in self.nodes:
            if (n["kind"] == "note" or not n.get("label") or not n.get("w")
                    or n.get("label_pos") not in (None, "center")):
                continue
            a = self._advance(n)
            if a:
                fit = max(fit, (a + 12) / n["w"])
        fit = min(fit, 1.0)

        lo, hi, ty, by = self._extent()
        if self._effective_w(lo, hi, ty, by, margin) <= target:
            k = 1.0
        else:
            k, lo_k, hi_k = 1.0, fit, 1.0
            for _ in range(40):                 # effective_w(k) is monotonic, so bisect
                k = (lo_k + hi_k) / 2
                a, b, t, c = self._extent(k, lo, ty)
                if self._effective_w(a, b, t, c, margin) > target:
                    hi_k = k
                else:
                    lo_k = k
            k = lo_k
            a, b, t, c = self._extent(k, lo, ty)
            if self._effective_w(a, b, t, c, margin) > target + 1 and k <= fit + 1e-6:
                pass          # the label-fit clamp bound it, not a long line
            elif (self._effective_w(a, b, t, c, margin) > target + 1
                  and self.SLIDE_ASPECT * (c - t + 2 * margin) > b - a + 2 * margin):
                # Height-bound, so no amount of wrapping will reach the target: the
                # lever for a figure fitted by its height is **rows, not units**.
                # Naming the long label here would send the next reader to fix the
                # wrong thing. Plan §8 item 18.
                print(f"  ! {self.title}: height-bound at {b - a + 2 * margin:.0f}"
                      f"x{c - t + 2 * margin:.0f} — effective width "
                      f"{self._effective_w(a, b, t, c, margin):.0f} > {target}; "
                      f"cut rows, not units", file=sys.stderr)
            elif self._effective_w(a, b, t, c, margin) > target + 1:
                # Text does not scale, so one long line can be wider than the whole
                # target and no amount of shrinking will reach it. Without the floor
                # the search happily drives the drawing to nothing around that line --
                # which it did, to five figures, before this existed. Name the line
                # instead: wrapping it is the fix, and it is a fix worth making anyway
                # at 18pt, because a 1000-unit measure is far too long to read.
                worst = max((n for n in self.groups + self.nodes
                             if n["kind"] == "note" and n.get("label")),
                            key=self._advance, default=None)
                print(f"  ! {self.title}: cannot reach {target} wide; the longest label "
                      f"is {self._advance(worst):.0f} units — wrap it\n"
                      f'    "{str(worst["label"])[:72]}"', file=sys.stderr)
        a, b, t, c = self._extent(k, lo, ty)
        dx, dy = margin - a, margin - t

        def move(px, py):
            return (px - lo) * k + dx, (py - ty) * k + dy

        for n in self.groups + self.nodes:
            if n["kind"] == "image":
                continue
            if n["kind"] in self.MARKS:
                # a lock, a clock, a tick, a cross: these are marks *about* the
                # drawing, like text, and they are already small. Shrinking them with
                # the geometry is the same mistake as shrinking the labels. Move the
                # centre, keep the size.
                cx, cy = move(n["x"] + n["w"] / 2, n["y"] + n["h"] / 2)
                n["x"], n["y"] = cx - n["w"] / 2, cy - n["h"] / 2
                continue
            n["x"], n["y"] = move(n["x"], n["y"])
            for key in ("w", "h", "slant", "band", "dx", "dy"):
                if isinstance(n.get(key), (int, float)):
                    n[key] = n[key] * k
        for e in self.edges:
            e["via"] = [move(px, py) for px, py in e.get("via") or []]
            for end in ("src", "dst"):
                if isinstance(e[end], tuple):
                    e[end] = move(*e[end])
        self.w = round(b - a + 2 * margin)
        self.h = round(c - t + 2 * margin)
        return self

    def _edge_pt(self, e):
        """Edge labels are the one text no figure can override, and they were the
        smallest thing on the slide: 15pt Caveat, 12pt Plex on a BPMN sequence
        flow. A gateway condition is read and used, so both go to the floor."""
        return self._pt(CONTENT_PT, self.font if e.get("bpmn") else HAND)

    # ---- SVG preview ----
    def to_svg(self):
        self._legible()
        W, H = self.w, self.h
        o = []
        o.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
                 f'xmlns:xlink="http://www.w3.org/1999/xlink" '
                 f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
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
            # BPMN: sequence flow takes a solid head, message flow a hollow one, and
            # message flow starts from a small open circle. That is the notation, not
            # decoration -- it is how you tell a token from a message on the page.
            f'<marker id="seq" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">'
            f'<path d="M0,0 L7,3 L0,6 z" fill="{INK}"/></marker>'
            f'<marker id="seqR" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">'
            f'<path d="M0,0 L7,3 L0,6 z" fill="{ANNOTATION}"/></marker>'
            f'<marker id="mfe" markerWidth="9" markerHeight="9" refX="7.5" refY="3" orient="auto">'
            f'<path d="M0.5,0.5 L7,3 L0.5,5.5 z" fill="{PAPER}" stroke="{CARBON}" '
            f'stroke-width="1"/></marker>'
            f'<marker id="mfeR" markerWidth="9" markerHeight="9" refX="7.5" refY="3" orient="auto">'
            f'<path d="M0.5,0.5 L7,3 L0.5,5.5 z" fill="{PAPER}" stroke="{ANNOTATION}" '
            f'stroke-width="1"/></marker>'
            f'<marker id="mfs" markerWidth="8" markerHeight="8" refX="3.4" refY="3" orient="auto">'
            f'<circle cx="3.4" cy="3" r="2.4" fill="{PAPER}" stroke="{CARBON}" '
            f'stroke-width="1"/></marker>'
            f'<marker id="mfsR" markerWidth="8" markerHeight="8" refX="3.4" refY="3" orient="auto">'
            f'<circle cx="3.4" cy="3" r="2.4" fill="{PAPER}" stroke="{ANNOTATION}" '
            f'stroke-width="1"/></marker>'
            '</defs>')
        if not self.transparent:
            o.append(f'<rect width="{W}" height="{H}" '
                     f'fill="{MANILA if self.panel else PAPER}"/>')

        wob = ' filter="url(#wob)"' if self.sketch else ""
        # containers first, so everything else sits inside them
        o.append(f'<g{wob} fill="none" stroke-linecap="round" '
                 'stroke-linejoin="round">')
        for g in self.groups:
            if g["kind"] == "image":
                o.append(f'<image x="{g["x"]}" y="{g["y"]}" width="{g["w"]}" '
                         f'height="{g["h"]}" preserveAspectRatio="xMidYMid meet" '
                         f'xlink:href="{self._data_uri(g["path"])}"/>')
                continue
            if g["kind"] == "pool":
                c = ANNOTATION if g.get("accent") else INK
                x, y, w, h = g["x"], g["y"], g["w"], g["h"]
                o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
                         f'stroke="{c}" stroke-width="1.6"/>')
                o.append(f'<path d="M{x+self.BAND},{y} v{h}" stroke="{c}" stroke-width="1.6"/>')
                ly = y
                for lh, _ in g["lanes"][:-1]:
                    ly += lh
                    o.append(f'<path d="M{x+self.BAND},{ly} h{w-self.BAND}" '
                             f'stroke="{INK}" stroke-width="1.2"/>')
                if g["lanes"]:
                    o.append(f'<path d="M{x+self.BAND*2},{y} v{h}" stroke="{INK}" '
                             f'stroke-width="1.2"/>')
                continue
            c = ANNOTATION if g.get("accent") else MUTED
            dash = ' stroke-dasharray="6 5"' if g.get("dashed") else ""
            o.append(f'<rect x="{g["x"]}" y="{g["y"]}" width="{g["w"]}" height="{g["h"]}" '
                     f'rx="6" stroke="{c}" stroke-width="1.4"{dash}/>')
        o.append('</g>')

        # shapes, wobbled together so the hand is consistent
        o.append(f'<g{wob} fill="none" stroke-linecap="round" stroke-linejoin="round">')
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
            elif n["kind"] == "choreo":
                x, y, w, h, b = n["x"], n["y"], n["w"], n["h"], n["band"]
                o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" '
                         f'fill="{PAPER}" stroke="{c}" stroke-width="1.6"/>')
                o.append(f'<path d="M{x},{y+b} h{w} M{x},{y+h-b} h{w}" stroke="{c}" '
                         f'stroke-width="1.2"/>')
                # the recipient band is filled; the initiator's is not
                o.append(f'<rect x="{x+1}" y="{y+h-b}" width="{w-2}" height="{b-1}" '
                         f'fill="{MANILA}" stroke="none"/>')
                o.append(f'<path d="M{x},{y+h-b} h{w}" stroke="{c}" stroke-width="1.2"/>')
            elif n["kind"] == "desk":
                x, y, w, h = n["x"], n["y"], n["w"], n["h"]
                k = min(22, w / 5, h / 4)
                o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
                         f'fill="{PAPER}" stroke="{c}" stroke-width="1.5"/>')
                for cx, cy, sx, sy in ((x, y, 1, 1), (x + w, y, -1, 1),
                                       (x, y + h, 1, -1), (x + w, y + h, -1, -1)):
                    o.append(f'<path d="M{cx},{cy + sy*k} L{cx},{cy} L{cx + sx*k},{cy}" '
                             f'fill="none" stroke="{c}" stroke-width="3.2"/>')
            elif n["kind"] == "tray":
                x, y, w, h = n["x"], n["y"], n["w"], n["h"]
                lip = h * 0.42
                # the document
                o.append(f'<rect x="{x + w*0.16}" y="{y}" width="{w*0.68}" '
                         f'height="{h - lip + 2}" fill="{PAPER}" stroke="{c}" '
                         f'stroke-width="1.3"/>')
                for i in range(3):
                    ly = y + h * 0.14 + i * h * 0.14
                    o.append(f'<path d="M{x + w*0.26},{ly} h{w*0.48}" stroke="{c}" '
                             f'stroke-width="1"/>')
                # the tray it sits in
                o.append(f'<path d="M{x},{y + h - lip} L{x},{y + h} L{x + w},{y + h} '
                         f'L{x + w},{y + h - lip}" fill="{c if n.get("out") else PAPER}" '
                         f'stroke="{c}" stroke-width="1.5"/>')
            elif n["kind"] == "doc":
                x, y, w, h = n["x"], n["y"], n["w"], n["h"]
                o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
                         f'fill="{PAPER}" stroke="{c}" stroke-width="1.3"/>')
                for i in range(3):
                    ly = y + h * 0.26 + i * h * 0.22
                    o.append(f'<path d="M{x + w*0.16},{ly} h{w*0.68}" stroke="{c}" '
                             f'stroke-width="1"/>')
            elif n["kind"] == "folder":
                x, y, w, h = n["x"], n["y"], n["w"], n["h"]
                tab = h * 0.2
                o.append(f'<path d="M{x},{y + tab} L{x},{y} L{x + w*0.42},{y} '
                         f'L{x + w*0.52},{y + tab} L{x + w},{y + tab} L{x + w},{y + h} '
                         f'L{x},{y + h} z" fill="{MANILA}" stroke="{c}" '
                         f'stroke-width="1.5" stroke-linejoin="round"/>')
                o.append(f'<path d="M{x + w*0.14},{y + h*0.55} h{w*0.72} '
                         f'M{x + w*0.14},{y + h*0.75} h{w*0.5}" stroke="{c}" '
                         f'stroke-width="1"/>')
            elif n["kind"] == "rule":
                o.append(f'<path d="M{n["x"]},{n["y"]} l{n.get("dx") or 0},'
                         f'{n.get("dy") or 0}" fill="none" '
                         f'stroke="{n["color"]}" stroke-width="{n["weight"]}"/>')
            elif n["kind"] == "log":
                x, y, w, h, cn = n["x"], n["y"], n["w"], n["h"], n["cells"]
                cw = w / cn
                o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
                         f'fill="{PAPER}" stroke="{c}" stroke-width="1.6"/>')
                for i in range(1, cn):
                    o.append(f'<path d="M{x + i*cw},{y} v{h}" stroke="{c}" '
                             f'stroke-width="1.1"/>')
                # An offset is the stream's own vocabulary, not our annotation on
                # top of it, so it is set in ink at label size and bold -- not muted
                # at 12. Ian, reviewing the run on a projector: "a little small and
                # faint to read on a slide across a room."
                for i in range(cn):
                    self._text(o, str(n["start"] + i), x + (i + 0.5) * cw,
                               y + h + n["size"] + 6, n["size"], INK, "middle",
                               self.font, weight=700)
            elif n["kind"] == "icon":
                x, y, w, h = n["x"], n["y"], n["w"], n["h"]
                cx, cy, r = x + w / 2, y + h / 2, w / 2
                k = n["ikind"]
                if k == "lock":
                    o.append(f'<path d="M{cx - r*0.5},{cy - r*0.05} '
                             f'v{-r*0.45} a{r*0.5},{r*0.5} 0 0 1 {r},0 v{r*0.45}" '
                             f'fill="none" stroke="{c}" stroke-width="1.8"/>')
                    o.append(f'<rect x="{cx - r*0.72}" y="{cy - r*0.05}" '
                             f'width="{r*1.44}" height="{r*0.95}" rx="2" '
                             f'fill="{PAPER}" stroke="{c}" stroke-width="1.6"/>')
                elif k == "clock":
                    o.append(f'<circle cx="{cx}" cy="{cy}" r="{r*0.82}" '
                             f'fill="{PAPER}" stroke="{c}" stroke-width="1.6"/>')
                    o.append(f'<path d="M{cx},{cy - r*0.5} v{r*0.5} h{r*0.4}" '
                             f'fill="none" stroke="{c}" stroke-width="1.6"/>')
                    o.append(f'<path d="M{cx - r*0.3},{cy - r*0.95} h{r*0.6}" '
                             f'stroke="{c}" stroke-width="1.8"/>')
                elif k == "tick":
                    o.append(f'<path d="M{cx - r*0.7},{cy} l{r*0.5},{r*0.55} '
                             f'l{r*0.95},{-r*1.15}" fill="none" stroke="{c}" '
                             f'stroke-width="2.4" stroke-linecap="round" '
                             f'stroke-linejoin="round"/>')
                elif k == "cross":
                    o.append(f'<path d="M{cx - r*0.6},{cy - r*0.6} '
                             f'l{r*1.2},{r*1.2} M{cx + r*0.6},{cy - r*0.6} '
                             f'l{-r*1.2},{r*1.2}" fill="none" stroke="{c}" '
                             f'stroke-width="2.4" stroke-linecap="round"/>')
            elif n["kind"] == "point":
                o.append(f'<circle cx="{n["x"] + n["w"] / 2}" cy="{n["y"] + n["h"] / 2}" '
                         f'r="{n["w"] / 2}" fill="{c}" stroke="{c}" stroke-width="1"/>')
            elif n["kind"] == "phone":
                x, y, w, h = n["x"], n["y"], n["w"], n["h"]
                o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" '
                         f'fill="{PAPER}" stroke="{c}" stroke-width="1.5"/>')
                o.append(f'<rect x="{x + w*0.07}" y="{y + h*0.12}" width="{w*0.2}" '
                         f'height="{h*0.76}" rx="{min(w*0.09, h*0.16)}" fill="{PAPER}" '
                         f'stroke="{c}" stroke-width="1.5"/>')
                for r_ in range(3):
                    for k in range(3):
                        o.append(f'<rect x="{x + w*(0.38 + k*0.18)}" '
                                 f'y="{y + h*(0.17 + r_*0.24)}" width="{w*0.11}" '
                                 f'height="{h*0.15}" fill="none" stroke="{c}" '
                                 f'stroke-width="1.1"/>')
            elif n["kind"] == "bar":
                o.append(f'<rect x="{n["x"]}" y="{n["y"]}" width="{n["w"]}" '
                         f'height="{n["h"]}" fill="{INK}" stroke="none"/>')
            elif n["kind"] == "step":
                o.append(f'<rect x="{n["x"]}" y="{n["y"]}" width="{n["w"]}" '
                         f'height="{n["h"]}" rx="2" fill="{PAPER}" stroke="{CARBON}" '
                         f'stroke-width="1.4"/>')
            elif n["kind"] == "task":
                o.append(f'<rect x="{n["x"]}" y="{n["y"]}" width="{n["w"]}" '
                         f'height="{n["h"]}" rx="7" fill="{PAPER}" stroke="{c}" '
                         f'stroke-width="1.6"/>')
                if n.get("double"):
                    o.append(f'<rect x="{n["x"]+3.5}" y="{n["y"]+3.5}" '
                             f'width="{n["w"]-7}" height="{n["h"]-7}" rx="5" '
                             f'fill="none" stroke="{c}" stroke-width="1.6"/>')
                if n.get("marker") == "compensate":
                    self._symbol(o, n["x"] + n["w"] / 2, n["y"] + n["h"] - 12,
                                 "compensation", c)
                elif n.get("marker"):
                    self._marker(o, n["x"] + 7, n["y"] + 7, n["marker"], c)
                if n.get("sub"):
                    self._sub_marker(o, n["x"] + n["w"] / 2, n["y"] + n["h"] - 11,
                                     n["sub"], c)
            elif n["kind"] == "event":
                cx, cy = n["x"] + n["w"] / 2, n["y"] + n["h"] / 2
                r = n["w"] / 2
                sw = {"start": 1.5, "intermediate": 1.5, "end": 3.4}[n["ekind"]]
                dash = ' stroke-dasharray="5,3.4"' if n.get("nonint") else ""
                o.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{PAPER}" '
                         f'stroke="{c}" stroke-width="{sw}"{dash}/>')
                if n["ekind"] == "intermediate":
                    o.append(f'<circle cx="{cx}" cy="{cy}" r="{r-3.4}" fill="none" '
                             f'stroke="{c}" stroke-width="1.5"{dash}/>')
                if n.get("symbol"):
                    self._symbol(o, cx, cy, n["symbol"], c,
                                 filled=n.get("filled", n["ekind"] == "end"))
            elif n["kind"] == "gateway":
                cx, cy = n["x"] + n["w"] / 2, n["y"] + n["h"] / 2
                r = n["w"] / 2
                o.append(f'<path d="M{cx},{cy-r} L{cx+r},{cy} L{cx},{cy+r} L{cx-r},{cy} z" '
                         f'fill="{PAPER}" stroke="{c}" stroke-width="1.6"/>')
                k = r * 0.34
                if n["gkind"] == "parallel":
                    o.append(f'<path d="M{cx-k},{cy} h{2*k} M{cx},{cy-k} v{2*k}" '
                             f'stroke="{c}" stroke-width="2"/>')
                elif n["gkind"] == "inclusive":
                    o.append(f'<circle cx="{cx}" cy="{cy}" r="{k*1.32}" fill="none" '
                             f'stroke="{c}" stroke-width="2.4"/>')
                elif n["gkind"] == "complex":
                    o.append(f'<path d="M{cx-k},{cy} h{2*k} M{cx},{cy-k} v{2*k} '
                             f'M{cx-k*0.72},{cy-k*0.72} L{cx+k*0.72},{cy+k*0.72} '
                             f'M{cx+k*0.72},{cy-k*0.72} L{cx-k*0.72},{cy+k*0.72}" '
                             f'stroke="{c}" stroke-width="2" stroke-linecap="round"/>')
                elif n["gkind"] == "event":
                    # The event-based gateway wears an intermediate event's two
                    # rings, because that is what it waits for.
                    o.append(f'<circle cx="{cx}" cy="{cy}" r="{k*1.55}" fill="none" '
                             f'stroke="{c}" stroke-width="1.5"/>')
                    o.append(f'<circle cx="{cx}" cy="{cy}" r="{k*1.18}" fill="none" '
                             f'stroke="{c}" stroke-width="1.5"/>')
                    p = k * 0.78
                    pts = " ".join(f"{round(cx + p * sx, 2)},{round(cy + p * sy, 2)}"
                                   for sx, sy in self._PENTAGON)
                    o.append(f'<polygon points="{pts}" fill="none" stroke="{c}" '
                             f'stroke-width="1.4" stroke-linejoin="round"/>')
                else:
                    o.append(f'<path d="M{cx-k},{cy-k} L{cx+k},{cy+k} '
                             f'M{cx+k},{cy-k} L{cx-k},{cy+k}" stroke="{c}" '
                             f'stroke-width="2"/>')
            elif n["kind"] == "msg":
                x, y, w, h = n["x"], n["y"], n["w"], n["h"]
                o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="1.5" '
                         f'fill="{PAPER}" stroke="{c}" stroke-width="1.4"/>')
                o.append(f'<path d="M{x},{y} L{x+w/2},{y+h*0.55} L{x+w},{y}" '
                         f'stroke="{c}" stroke-width="1.2"/>')
            elif n["kind"] == "hex":
                x, y, w, h, v = n["x"], n["y"], n["w"], n["h"], n["slant"]
                k = min(w * 0.20, h * 0.55)
                pts = ((x, y + v), (x + k, y), (x + w - k, y), (x + w, y + v),
                       (x + w, y + h - v), (x + w - k, y + h), (x + k, y + h),
                       (x, y + h - v))
                d_ = "M" + " L".join(f"{px},{py}" for px, py in pts) + " z"
                o.append(f'<path d="{d_}" fill="{MANILA}" stroke="{c}" '
                         f'stroke-width="1.7"/>')
            elif n["kind"] == "pkt":
                o.append(f'<rect x="{n["x"]}" y="{n["y"]}" width="{n["w"]}" '
                         f'height="{n["h"]}" rx="5" fill="{PAPER}" stroke="{c}" '
                         f'stroke-width="1.5" stroke-dasharray="5 4"/>')
            elif n["kind"] == "pipe":
                x, y, w, h = n["x"], n["y"], n["w"], n["h"]
                o.append(f'<path d="M{x},{y} h{w} M{x},{y+h} h{w}" stroke="{c}" stroke-width="1.7"/>')
                o.append(f'<ellipse cx="{x}" cy="{y+h/2}" rx="{max(3,h/3)}" ry="{h/2}" '
                         f'stroke="{c}" stroke-width="1.4"/>')
        for e in self.edges:
            pts = self._points(e)
            col = MUTED if (e.get("plain") or e.get("muted")) else (
                ANNOTATION if e["accent"] else CARBON)
            if e.get("bpmn"):
                r = "R" if e["accent"] else ""
                if e.get("message"):
                    col = ANNOTATION if e["accent"] else CARBON
                    dash = ' stroke-dasharray="6 5"'
                    mark = f' marker-start="url(#mfs{r})" marker-end="url(#mfe{r})"'
                else:
                    col = ANNOTATION if e["accent"] else INK
                    dash = ""
                    mark = f' marker-end="url(#seq{r})"'
                d = "M" + " L".join(f"{x},{y}" for x, y in pts)
                o.append(f'<path d="{d}" stroke="{col}" stroke-width="1.5"{dash}{mark}/>')
                continue
            dash = ' stroke-dasharray="3 4"' if e["dashed"] else ""
            mark = "" if e.get("plain") else (
                ' marker-end="url(#arR)"' if e["accent"] else
                ' marker-end="url(#arM)"' if e.get("muted") else ' marker-end="url(#ar)"')
            d = "M" + " L".join(f"{x},{y}" for x, y in pts)
            o.append(f'<path d="{d}" stroke="{col}" stroke-width="1.8"{dash}{mark}/>')
        o.append('</g>')

        # text, outlined -- deliberately NOT wobbled, so labels stay legible
        for g in self.groups:
            if not g["label"] or g["kind"] == "image":
                continue
            col = ANNOTATION if g.get("accent") else (
                INK if g["kind"] == "pool" else COMMENT)
            if g["kind"] == "pool":
                # the band label runs up the side, as BPMN draws a participant
                cy = g["y"] + g["h"] / 2
                self._rot(o, g["label"], g["x"] + self.BAND / 2 + 5, cy,
                          g.get("size", 13), col, self.font, fit=g["h"])
                ly = g["y"]
                for lh, name in g["lanes"]:
                    if name:
                        self._rot(o, name, g["x"] + self.BAND * 1.5 + 5, ly + lh / 2,
                                  g.get("size", 13) - 1, INK, self.font, fit=lh)
                    ly += lh
                continue
            self._text(o, g["label"], g["x"] + 10, g["y"] + g.get("size", 14) + 2,
                       g.get("size", 14), col, "start")
        for n in self.nodes:
            if not n["label"]:
                continue
            if n["kind"] == "note":
                self._text(o, n["label"], n["x"], n["y"], n.get("size", 14),
                           n.get("color", MUTED), n.get("anchor", "middle"),
                           n.get("font") or HAND, n.get("weight"))
            elif n["kind"] == "choreo":
                size, col = n.get("size", 13), ANNOTATION if n.get("accent") else INK
                cx, b = n["x"] + n["w"] / 2, n["band"]
                self._text(o, n["initiator"], cx, n["y"] + b - 8, size - 1, col,
                           "middle", self.font)
                self._text(o, n["label"], cx, n["y"] + n["h"] / 2 + size / 3, size,
                           col, "middle", self.font)
                self._text(o, n["recipient"], cx, n["y"] + n["h"] - 8, size - 1, col,
                           "middle", self.font)
            else:
                size = n.get("size", 15)
                col = ANNOTATION if n.get("accent") else (
                    CARBON if n["kind"] == "step" else INK)
                cx = n["x"] + n["w"] / 2
                face = self.font if n["kind"] in ("task", "event", "gateway") else self.font
                if n.get("label_pos") == "top":
                    cy = n["y"] + size + 2
                elif n.get("label_pos") == "above":
                    # _text block-centres a multi-line label on cy, so a two-line
                    # label above an element would sit half on top of it
                    cy = n["y"] - 7 - (n["label"].count("\n")) * size * 1.05 / 2
                elif n.get("label_pos") == "below":
                    cy = n["y"] + n["h"] + size + 3      # events and gateways label under
                else:
                    cy = n["y"] + n["h"] / 2 + size / 3
                    if n["kind"] == "cyl":
                        # **A cylinder's label belongs in its body, not across its
                        # rim.** The interior starts below the top ellipse, at
                        # `y + 2ry`, so centring on the whole shape puts a two-line
                        # label's first line straight through the rim -- which is
                        # exactly what `progress / (a KV store)` and both `if_later`
                        # replicas were doing. `lint_figures.py` cannot see it: it
                        # measures a label against its shape's BOX, and a rim is not
                        # one. Found by eye after `compact` took the shapes down and
                        # left the type where it was.
                        cy += min(8, n["h"] / 4)
                    if n.get("marker") and n["marker"] != "compensate":
                        cy += 7
                self._text(o, n["label"], cx, cy, size, col, "middle", face)
        for e in self.edges:
            if not e["label"]:
                continue
            mx, my = self._mid(self._points(e))
            if e.get("bpmn"):
                col = ANNOTATION if e["accent"] else (
                    CARBON if e.get("message") else COMMENT)
                self._text(o, e["label"], mx + e.get("lx", 0), my - 6 + e.get("ly", 0),
                           self._edge_pt(e), col, "middle", self.font)
                continue
            col = COMMENT if e.get("muted") else (ANNOTATION if e["accent"] else CARBON)
            self._text(o, e["label"], mx + e.get("lx", 0), my - 7 + e.get("ly", 0),
                       self._edge_pt(e), col, "middle")

        # **The traces go on top of everything, including the labels.** They are an
        # overlay on a finished picture, so anything they cover is covered on
        # purpose -- that is the whole licence for drawing them this big. The
        # paper-coloured rim keeps a carbon arrow from merging into a carbon stroke
        # in the drawing underneath it.
        #
        # Guarded on `self.traces` so a figure without any emits exactly the bytes
        # it emitted before this method existed -- `diagram.py` edits have to be
        # additive (CLAUDE.md rule 5) and this one is checked by rebuilding all
        # twelve families and diffing.
        #
        # A *layer* is not a filtered render of this diagram, it is its own diagram:
        # same canvas, no nodes, only that click's traces. rsvg paints no ground, so
        # the result is transparent and stacks over the base on the slide. Rendering
        # the montage nine times instead would have put nine copies of the same four
        # embedded flows in `resources/` and in the .pptx -- 1.3MB each.
        if self.traces:
            o.append(f'<g{wob} stroke-linejoin="round">')
            for t in self.traces:
                col = MUTED if t["sync"] else CARBON
                o.append(f'<polygon points="{self._trace_poly(t)}" fill="{col}" '
                         f'stroke="{PAPER}" stroke-width="2.5"/>')
            o.append('</g>')

        o.append('</svg>')
        return "\n".join(o)

    @classmethod
    def _rot(cls, out, text, x, y, size, color, family, fit=None):
        """Vertical text for a pool or lane band. `fit` is the height available:
        a lane label longer than its lane silently overflows into the next one,
        which is how the first pass of the collaboration diagrams broke."""
        if fit:
            try:
                _, adv = _Outliner.outline(text, family, size, 0, 0, "middle",
                                           weight=490 if family == PLAIN else None)
                if adv > fit - 8:
                    size = max(9, size * (fit - 8) / adv)
            except Exception:
                pass
        buf = []
        cls._text(buf, text, 0, 0, size, color, "middle", family)
        out.append(f'<g transform="translate({x},{y}) rotate(-90)">' +
                   "".join(buf) + "</g>")

    @classmethod
    def _text(cls, out, text, x, y, size, color, anchor, family=HAND, weight=None):
        """`weight` overrides the face's default instance. Both bundled faces are
        variable (Caveat 400-700, Plex Sans 100-700), so this is a real axis setting
        rather than a synthetic bold -- which matters, because a faux-bolded outline
        would thicken by a fixed amount at every size."""
        if "\n" in text:                       # stack the lines, block-centred on y
            lines = text.split("\n")
            lead = size * 1.05
            top = y - (len(lines) - 1) * lead / 2
            for i, line in enumerate(lines):
                cls._text(out, line, x, top + i * lead, size, color, anchor, family,
                          weight)
            return
        try:
            d, _ = _Outliner.outline(text, family, size, x, y, anchor,
                                     weight=weight or (490 if family == PLAIN else None))
            if d:
                out.append(f'<path d="{d}" fill="{color}"/>')
                return
        except Exception as exc:                       # pragma: no cover
            print(f"  ! outline failed ({exc}); falling back to <text>", file=sys.stderr)
        out.append(f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
                   f'fill="{color}" text-anchor="{anchor}">{html.escape(text)}</text>')

    # ---- draw.io source ----
    def to_drawio(self):
        self._legible()
        mx = ET.Element("mxfile", host="practical-messaging", type="device")
        dia = ET.SubElement(mx, "diagram", name=self.title)
        model = ET.SubElement(dia, "mxGraphModel", dx="800", dy="600", grid="1",
                              gridSize="10", page="1",
                              pageWidth=str(self.w), pageHeight=str(self.h),
                              background=MANILA if self.panel else PAPER)
        root = ET.SubElement(model, "root")
        ET.SubElement(root, "mxCell", id="0")
        ET.SubElement(root, "mxCell", id="1", parent="0")
        note_no = 0

        base = (f"sketch=1;hachureGap=4;jiggle=2;curveFitting=1;"
                f"fontFamily={self.font};html=1;")

        # containers first so they land behind, and so a reader can drag the whole
        # group in draw.io without the members jumping out of it
        for g in self.groups:
            if g["kind"] == "image":
                cell = ET.SubElement(root, "mxCell", id=g["id"], value="",
                                     style=("shape=image;html=1;imageAspect=1;"
                                            "aspect=fixed;"
                                            f"image={self._data_uri(g['path'])};"),
                                     vertex="1", parent="1")
                ET.SubElement(cell, "mxGeometry", x=str(g["x"]), y=str(g["y"]),
                              width=str(g["w"]),
                              height=str(g["h"])).set("as", "geometry")
                continue
            if g["kind"] == "pool":
                col = ANNOTATION if g.get("accent") else INK
                pstyle = (f"swimlane;html=1;horizontal=0;startSize={self.BAND};"
                          f"fillColor=none;strokeColor={col};fontColor={col};"
                          f"fontFamily={self.font};fontSize={g.get('size',13)};"
                          f"swimlaneFillColor=none;")
                cell = ET.SubElement(root, "mxCell", id=g["id"], value=g["label"],
                                     style=pstyle, vertex="1", parent="1")
                ET.SubElement(cell, "mxGeometry", x=str(g["x"]), y=str(g["y"]),
                              width=str(g["w"]), height=str(g["h"])).set("as", "geometry")
                oy = 0
                for i, (lh, name) in enumerate(g["lanes"]):
                    lc = ET.SubElement(root, "mxCell", id=f"{g['id']}l{i}", value=name,
                                       style=pstyle, vertex="1", parent=g["id"])
                    ET.SubElement(lc, "mxGeometry", x=str(self.BAND), y=str(oy),
                                  width=str(g["w"] - self.BAND),
                                  height=str(lh)).set("as", "geometry")
                    oy += lh
                continue
            col = ANNOTATION if g.get("accent") else MUTED
            txt = ANNOTATION if g.get("accent") else COMMENT
            style = (base + "rounded=1;arcSize=8;verticalAlign=top;align=left;"
                     "spacingLeft=8;spacingTop=2;fillColor=none;"
                     f"strokeColor={col};strokeWidth=1.4;fontColor={txt};"
                     f"fontSize={g.get('size',14)};")
            if g.get("dashed"):
                style += "dashed=1;dashPattern=6 5;"
            cell = ET.SubElement(root, "mxCell", id=g["id"], value=g["label"],
                                 style=style, vertex="1", parent="1")
            ET.SubElement(cell, "mxGeometry", x=str(g["x"]), y=str(g["y"]),
                          width=str(g["w"]), height=str(g["h"])).set("as", "geometry")

        for n in self.nodes:
            if n["kind"] == "note":
                style = (f"text;html=1;align=center;fontFamily={n.get('font') or HAND};"
                         f"fontSize={n.get('size',14)};fontColor={n.get('color',COMMENT)};")
                if (n.get("weight") or 400) >= 600:
                    style += "fontStyle=1;"
                note_no += 1
                cell = ET.SubElement(root, "mxCell", id=f"t{note_no}", value=n["label"],
                                     style=style, vertex="1", parent="1")
                ET.SubElement(cell, "mxGeometry", x=str(n["x"] - 60), y=str(n["y"] - 12),
                              width="120", height="20").set("as", "geometry")
                continue
            stroke = ANNOTATION if n.get("accent") else INK
            if n["kind"] in ("event", "gateway", "task", "choreo"):
                self._drawio_bpmn(root, n, stroke)
                continue
            # Paper Flow glyphs fall back to the nearest core draw.io shape. The PNG
            # carries the real notation; the .drawio stays editable and roughly right.
            shape = {"box": "rounded=1;arcSize=12;",
                     "cyl": "shape=cylinder3;boundedLbl=1;backgroundOutline=1;",
                     "pipe": "shape=tube;",
                     "msg": "shape=message;",
                     "desk": "rounded=0;",
                     "tray": "shape=document;boundedLbl=1;",
                     "doc": "shape=note;size=0;",
                     "folder": "shape=folder;tabWidth=40;tabHeight=12;tabPosition=left;",
                     "bar": "rounded=0;",
                     "rule": "shape=line;",
                     "point": "ellipse;",
                     "log": "shape=table;childLayout=tableLayout;",
                     "icon": "rounded=1;arcSize=20;",
                     "phone": "shape=mxgraph.telecom.telephone;",
                     "hex": "shape=hexagon;perimeter=hexagonPerimeter2;",
                     "pkt": "rounded=1;arcSize=22;dashed=1;dashPattern=5 4;",
                     "step": "rounded=0;"}[n["kind"]]
            if n["kind"] == "rule":
                stroke = n.get("color", MUTED)
                if n.get("dy"):
                    shape += "direction=north;"
            fill = {"msg": PAPER, "folder": MANILA, "bar": INK, "doc": PAPER,
                    "hex": MANILA, "pkt": PAPER,
                    "tray": PAPER, "desk": PAPER, "step": PAPER, "phone": PAPER,
                    "log": PAPER, "icon": PAPER,
                    "point": stroke}.get(n["kind"], "none")
            if n["kind"] == "step":
                stroke = CARBON
            if n["kind"] in ("tray", "folder", "step", "bar", "doc", "point",
                             "phone", "log", "icon"):
                style_extra = "verticalLabelPosition=bottom;verticalAlign=top;"
            elif n["kind"] == "desk":
                style_extra = "verticalLabelPosition=top;verticalAlign=bottom;"
            else:
                style_extra = ""
            style = (base + shape + style_extra +
                     f"strokeColor={stroke};strokeWidth=1.7;fillColor={fill};"
                     f"fontColor={stroke};fontSize={n.get('size',15)};")
            if n.get("label_pos") == "top":
                style += "verticalAlign=top;spacingTop=2;"
            if n["kind"] == "msg" and n["label"]:
                if n.get("label_pos") == "above":
                    style += "verticalLabelPosition=top;verticalAlign=bottom;labelPosition=center;"
                elif n.get("label_pos") == "below":
                    style += "verticalLabelPosition=bottom;verticalAlign=top;labelPosition=center;"
            cell = ET.SubElement(root, "mxCell", id=n["id"], value=n["label"],
                                 style=style, vertex="1", parent="1")
            ET.SubElement(cell, "mxGeometry", x=str(n["x"]), y=str(n["y"]),
                          width=str(n["w"]), height=str(n["h"])).set("as", "geometry")

        for i, e in enumerate(self.edges):
            col = MUTED if (e.get("plain") or e.get("muted")) else (
                ANNOTATION if e["accent"] else CARBON)
            txt = COMMENT if col == MUTED else col
            style = (f"sketch=1;jiggle=2;curveFitting=1;edgeStyle=none;rounded=0;"
                     f"strokeColor={col};strokeWidth=1.8;fontFamily={HAND};"
                     f"fontSize={self._edge_pt(e)};"
                     f"fontColor={txt};html=1;")
            if e.get("bpmn"):
                col = ANNOTATION if e["accent"] else (
                    CARBON if e.get("message") else INK)
                style = (f"edgeStyle=none;rounded=0;html=1;"
                         f"strokeColor={col};strokeWidth=1.5;"
                         f"fontColor={COMMENT if col == INK else col};"
                         f"fontFamily={self.font};fontSize={self._edge_pt(e)};")
                style += ("dashed=1;dashPattern=6 5;startArrow=oval;startFill=0;"
                          "endArrow=open;endFill=0;" if e.get("message")
                          else "endArrow=block;endFill=1;")
            if e["dashed"] and not e.get("bpmn"):
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

        # The traces, last so they sit on top in draw.io's z-order too. `singleArrow`
        # is draw.io's own block-arrow shape; it is authored pointing right and
        # rotated, which is exactly how the 2025 originals were built, so a file
        # opened in draw.io gives the same handles Ian had.
        for i, t in enumerate(self.traces):
            (x1, y1), (x2, y2) = t["src"], t["dst"]
            L = math.hypot(x2 - x1, y2 - y1) or 1.0
            ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
            col = MUTED if t["sync"] else CARBON
            head = min(2.0 * t["weight"], 0.45 * L)
            style = (f"shape=singleArrow;html=1;direction=east;"
                     f"arrowWidth={1 / 1.9:.3f};"
                     f"arrowSize={head / L:.3f};"
                     f"fillColor={col};strokeColor={PAPER};strokeWidth=2.5;"
                     f"rotation={ang:.1f};")
            cell = ET.SubElement(root, "mxCell", id=f"tr{i}", value="",
                                 style=style, vertex="1", parent="1")
            ET.SubElement(cell, "mxGeometry",
                          x=str(round((x1 + x2) / 2 - L / 2, 1)),
                          y=str(round((y1 + y2) / 2 - t["weight"] * 0.95, 1)),
                          width=str(round(L, 1)),
                          height=str(round(t["weight"] * 1.9, 1))).set("as", "geometry")

        ET.indent(mx, space="  ")
        return ET.tostring(mx, encoding="unicode")

    # ---- draw.io BPMN ----
    # These style strings come from draw.io's own BPMN 2.0 shape library. There is no
    # drawio CLI on this machine, so they were authored without being opened -- the PNG
    # preview is rendered from our own SVG and does NOT check them. If a .drawio ever
    # opens with the wrong glyph in a circle or a diamond, this is where to look.
    _EVENT_OUTLINE = {"start": "standard", "intermediate": "eventInt", "end": "end"}
    _GW_SYMBOL = {"exclusive": "exclusiveGw", "parallel": "parallelGw",
                  "inclusive": "general", "complex": "complexGw", "event": "multiple"}
    # Our symbol names are the outline's words; draw.io's are its own.
    _EVENT_SYMBOL = {"parallel": "parallelMultiple"}
    _TASK_MARKER = {"manual": "manual", "script": "script", "rule": "businessRule"}

    def _drawio_bpmn(self, root, n, stroke):
        common = (f"html=1;fillColor={PAPER};strokeColor={stroke};fontColor={stroke};"
                  f"fontFamily={self.font};fontSize={n.get('size',13)};")
        if n["kind"] == "choreo":
            b = n["band"]
            for i, (val, yy, hh, fill) in enumerate((
                    (n["initiator"], n["y"], b, PAPER),
                    (n["label"], n["y"] + b, n["h"] - 2 * b, PAPER),
                    (n["recipient"], n["y"] + n["h"] - b, b, MANILA))):
                cell = ET.SubElement(root, "mxCell", id=f"{n['id']}b{i}", value=val,
                                     style=(f"rounded=0;whiteSpace=wrap;{common}"
                                            f"fillColor={fill};strokeWidth=1.4;"),
                                     vertex="1", parent="1")
                ET.SubElement(cell, "mxGeometry", x=str(n["x"]), y=str(yy),
                              width=str(n["w"]),
                              height=str(hh)).set("as", "geometry")
            return
        if n["kind"] == "task":
            style = f"rounded=1;arcSize=14;whiteSpace=wrap;{common}strokeWidth=1.6;"
            # Only the reference card's three extra markers reach for draw.io's own
            # BPMN task shape. Switching the whole family onto it would rewrite
            # every existing .drawio for no gain, and rebuilds must be byte-identical.
            if n.get("marker") in self._TASK_MARKER:
                style += (f"shape=mxgraph.bpmn.task;"
                          f"taskMarker={self._TASK_MARKER[n['marker']]};")
            if n.get("sub") == "loop":
                style += "isLoopStandard=1;"
            if n.get("double"):
                style += "bpmnShapeType=transaction;"
        elif n["kind"] == "event":
            sym = n.get("symbol") or "general"
            outline = ("eventNonint" if n.get("nonint")
                       else self._EVENT_OUTLINE[n["ekind"]])
            if n.get("filled") and n["ekind"] != "end":
                outline = "throwing"
            style = ("shape=mxgraph.bpmn.shape;perimeter=ellipsePerimeter;"
                     "verticalLabelPosition=bottom;verticalAlign=top;align=center;"
                     f"labelBackgroundColor=none;outlineConnect=0;outline={outline};"
                     f"symbol={self._EVENT_SYMBOL.get(sym, sym)};{common}")
        else:
            style = ("shape=mxgraph.bpmn.shape;perimeter=rhombusPerimeter;"
                     "verticalLabelPosition=bottom;verticalAlign=top;align=center;"
                     "labelBackgroundColor=none;outlineConnect=0;background=gateway;"
                     f"outline=none;symbol={self._GW_SYMBOL[n['gkind']]};{common}")
        cell = ET.SubElement(root, "mxCell", id=n["id"], value=n["label"],
                             style=style, vertex="1", parent="1")
        ET.SubElement(cell, "mxGeometry", x=str(n["x"]), y=str(n["y"]),
                      width=str(n["w"]), height=str(n["h"])).set("as", "geometry")
        # the task-type icon rides as its own small cell -- shape=message is a core
        # draw.io shape, so it is certain to open, unlike a task-marker style string
        if n["kind"] == "task" and n.get("marker") in ("send", "receive"):
            fill = stroke if n["marker"] == "send" else PAPER
            ic = ET.SubElement(root, "mxCell", id=f"{n['id']}i",
                               style=f"shape=message;html=1;fillColor={fill};"
                                     f"strokeColor={stroke};",
                               vertex="1", parent="1")
            ET.SubElement(ic, "mxGeometry", x=str(n["x"] + 7), y=str(n["y"] + 7),
                          width="14", height="10").set("as", "geometry")
        elif n["kind"] == "task" and n.get("marker") == "user":
            ic = ET.SubElement(root, "mxCell", id=f"{n['id']}i",
                               style=f"shape=actor;html=1;fillColor=none;"
                                     f"strokeColor={stroke};",
                               vertex="1", parent="1")
            ET.SubElement(ic, "mxGeometry", x=str(n["x"] + 7), y=str(n["y"] + 6),
                          width="12", height="13").set("as", "geometry")

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
