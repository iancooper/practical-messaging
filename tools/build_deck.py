#!/usr/bin/env python3
"""Phase 3 — build the two `.pptx` decks from `outlines/`, to `styles.md`.

    python3 tools/build_deck.py                 # both days -> build/
    python3 tools/build_deck.py --day 1
    python3 tools/build_deck.py --report        # measure only, write nothing
    python3 tools/build_deck.py --day 1 --preview 3,17,40    # PNGs of those slides
    python3 tools/build_deck.py --day 1 --preview all

**`styles.md` is the spec and this is its implementation.** Canvas, type, sizes,
palette and the left-text / right-panel layout all come from there; where this file
makes a decision `styles.md` does not, the reason is in a comment and the decision
belongs back in `styles.md` once Ian has seen it.

**⚑ Layout is computed once, into draw-ops, and two back ends consume it.** `layout()`
returns a flat list of `("text" | "rect" | "image" | "table", …)` and `_Pptx` /
`_Svg` render it. That is the same move `diagram.py` makes for `.drawio` and `.png`,
and for the same reason: **there is no PowerPoint on this machine**, so the only way
to see a slide before shipping it is to render it here — and a preview that re-derives
the layout is a preview of a different deck. `PROMPT.md` rule 2 is *look at the PNG*;
this is what makes that possible for 174 slides nobody can open.

**The overflow report is a deliverable, not a diagnostic.** `styles.md`: *"Expect the
floor to force content off crowded slides. That is intended -- it will find the slides
doing too much, and it is a content decision as much as a design one."* So this builder
**never shrinks type to make content fit**. It lays the slide out at the floor, measures
what did not fit, and prints it. The list that comes out is a content queue for Ian.

**⚑ Two registers, two scales -- the same trap as the diagrams.** Caveat's x-height is
0.400em against Plex Sans's 0.516, so **18pt of Plex reads as 23pt of Caveat**. The
`styles.md` body floor of 18pt is a *Plex* measure; a callout set at 18pt Caveat would
sit a fifth below the floor while appearing to obey it. `CALLOUT_PT` is therefore 24.
This is `PROMPT.md` rule 14 -- never compare the two registers by point number -- and it
applies to slides exactly as it applies to figures.

**Fonts do not need to be installed to build.** The `.pptx` names them and PowerPoint
resolves them at open time; `tools/fonts/` is what this script measures and previews
with. But the deck will render in a fallback face until
`cp tools/fonts/*.ttf ~/Library/Fonts/` has been run -- Ian's machine, Ian's call, and
`styles.md` §Open tracks it.
"""

import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outline as O                                              # noqa: E402
from diagram import _Outliner                                    # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(REPO, "tools", "fonts")
OUT_DIR = os.path.join(REPO, "build")

# ---- the spec, from styles.md ------------------------------------------------

W_IN, H_IN = 13.333, 7.5                     # 16:9

INK        = "#181B1F"
PAPER      = "#FDFCFA"
CARBON     = "#1D4E6B"
ANNOTATION = "#C0453B"
MANILA     = "#F3EFE6"
RULE       = "#E0D9C8"
COMMENT    = "#2F5D3A"

SERIF = "IBM Plex Serif SemiBold"   # the face name the OS exposes for the 600 weight
SANS  = "IBM Plex Sans"
MONO  = "IBM Plex Mono"
HAND  = "Caveat"

_FILES = {
    SERIF: "IBMPlexSerif-SemiBold.ttf",
    "IBM Plex Serif": "IBMPlexSerif-Regular.ttf",
    SANS:  "IBMPlexSans-Variable.ttf",
    MONO:  "IBMPlexMono-Regular.ttf",
    HAND:  "Caveat.ttf",
}

TITLE_PT   = 29
KICKER_PT  = 12
BODY_PT    = 18        # the floor. styles.md: nothing below 16, sub-items may be 16.
SUB_PT     = 16
CALLOUT_PT = 24        # 18pt of Plex in Caveat's x-height -- see the module docstring
TABLE_PT   = 15
CODE_PT    = 15

LEAD = 1.24            # line spacing, multiples of the point size

M_L, M_R, M_T, M_B = 0.78, 0.62, 0.42, 0.46
GUTTER = 0.38

# One warning per offending word rather than per slide -- see Type.wrap.
_WIDE = set()
CONTENT_W = W_IN - M_L - M_R
TEXT_W = (CONTENT_W - GUTTER) * 1.15 / 2.0
PANEL_W = (CONTENT_W - GUTTER) * 0.85 / 2.0
PANEL_X = M_L + TEXT_W + GUTTER
PANEL_PAD = 0.15


def _in(pt):
    return pt / 72.0


# ---- measurement -------------------------------------------------------------

class Type:
    """Advance widths from the real font files, so overflow is measured and not guessed.

    **Uses the glyph set's own width rather than `hmtx`.** Plex Sans is a variable
    font: `hmtx` carries only the default instance, so a bold run measured through it
    comes out at the regular width and every dense bulleted slide reads as fitting when
    it does not. `glyphSet[name].width` applies the variation."""

    _cache = {}

    @classmethod
    def _gs(cls, family, weight):
        key = (family, weight)
        if key not in cls._cache:
            from fontTools.ttLib import TTFont
            font = TTFont(os.path.join(FONT_DIR, _FILES[family]),
                          fontNumber=0, lazy=True)
            axes = {a.axisTag for a in font["fvar"].axes} if "fvar" in font else set()
            gs = (font.getGlyphSet(location={"wght": weight})
                  if "wght" in axes else font.getGlyphSet())
            cls._cache[key] = (gs, font.getBestCmap(), font["head"].unitsPerEm)
        return cls._cache[key]

    @classmethod
    def width(cls, text, family, pt, bold=False, track=0.0):
        """Width in INCHES, with optional letter tracking in em."""
        gs, cmap, upem = cls._gs(family, 600 if bold else 400)
        total = 0.0
        for ch in text:
            g = gs[cmap.get(ord(ch)) or ".notdef"]
            total += getattr(g, "width", 0)
        return (total / upem + track * len(text)) * pt / 72.0

    @classmethod
    def tokens(cls, runs):
        """Flatten runs to (word, bold, italic, mono, space_before).

        **The space has to be tracked separately from the word**, because the emphasis
        boundary and the word boundary are not the same place. `**bold**, then` splits
        into a bold run ending at the comma and a plain run starting with it, so a
        wrapper that re-inserts a space between every pair of runs writes `bold ,` —
        and one that inserts none writes `the workand`. Neither is recoverable later."""
        import re as _re
        out, pending = [], False
        for text, b, i, m in runs:
            for part in _re.split(r"(\s+)", text):
                if not part:
                    continue
                if part.isspace():
                    pending = True
                else:
                    out.append((part, b, i, m, pending))
                    pending = False
        return out

    @classmethod
    def wrap(cls, runs, width_in, family, pt, track=0.0):
        """Greedy word wrap -> lines, each a list of merged (text, bold, italic, mono).

        Breaks on spaces only, so a single word wider than the measure is left long
        and runs out of its column.

        **⚑ It does NOT show up in the overflow report**, whatever this docstring used
        to claim: overflow measures the block's HEIGHT against the slide, and a word
        running off the right-hand side costs no height at all. On a slide with a
        figure or photograph the body column is only 6.21in wide, so the long word
        runs UNDER the panel and is cut mid-word -- which is how
        `jonasboner.com/resources/Reactive_Microservices_Architecture.pdf` shipped on
        Day 2 as `...Reactive_Microservices_Architect`, with no closing bracket and no
        way for a delegate to type it. A clipped label looks like a short label.

        So it warns, once per offending word, exactly as `_kicker` does. **The fix is
        the content** -- shorten the URL -- not a smaller size and not a hyphen."""
        lines, cur, cur_w = [], [], 0.0
        for word, b, i, m, sp in cls.tokens(runs):
            fam = MONO if m else family
            piece = (" " if (sp and cur) else "") + word
            w = cls.width(piece, fam, pt, b, track)
            # 0.05in of slack: a table cell pads beyond its measured column, so
            # "Out-Only" sitting 0.02in over renders whole. A guard that cries wolf
            # gets ignored, which is worse than not having one.
            if (cls.width(word, fam, pt, b, track) > width_in + 0.05
                    and word not in _WIDE):
                _WIDE.add(word)
                print(f"  ! word wider than its {width_in:.2f}in column by "
                      f"{cls.width(word, fam, pt, b, track) - width_in:.2f}in — it will "
                      f"run out of the column and, on a slide with a panel, be cut "
                      f"mid-word: {word!r}", file=sys.stderr)
            if cur and cur_w + w > width_in:
                lines.append(cur)
                cur, cur_w = [(word, b, i, m)], cls.width(word, fam, pt, b, track)
            else:
                cur.append((piece, b, i, m))
                cur_w += w
        if cur:
            lines.append(cur)
        return [cls._merge(l) for l in lines] or [[("", False, False, False)]]

    @staticmethod
    def _merge(line):
        """Adjacent pieces in the same style become one run — fewer shapes in the
        `.pptx`, and fewer glyph batches in the preview."""
        out = []
        for text, b, i, m in line:
            if out and out[-1][1:] == (b, i, m):
                out[-1] = (out[-1][0] + text, b, i, m)
            else:
                out.append((text, b, i, m))
        return out


# ---- draw-ops ----------------------------------------------------------------
#
# A slide is a list of these. Everything below `layout()` is geometry; everything
# in a back end is translation. Neither back end may compute a position.

def Text(x, y, runs, family, pt, colour, track=0.0, align="l"):
    """One LINE of text. `y` is the baseline. Runs are (text, bold, italic, mono)."""
    return ("text", dict(x=x, y=y, runs=runs, family=family, pt=pt,
                         colour=colour, track=track, align=align))


def Rect(x, y, w, h, fill=None, line=None, lw=1.0):
    return ("rect", dict(x=x, y=y, w=w, h=h, fill=fill, line=line, lw=lw))


def Image(x, y, w, h, path):
    return ("image", dict(x=x, y=y, w=w, h=h, path=path))


def Table(x, y, w, cols, rows, head):
    """`cols` are column widths in inches; `rows` are dicts of
    {h, cells: [[line-of-runs, …], …]} — already wrapped by `plan_table`."""
    return ("table", dict(x=x, y=y, w=w, cols=cols, rows=rows, head=head))


CELL_PAD = 0.09
CELL_LEAD = 1.18


def plan_table(raw_rows, head, w):
    """Column widths from the content, and every cell wrapped to its column.

    **Equal columns are wrong for these tables.** The outlines' tables are mostly a
    narrow label column against two or three wide prose ones -- `Must We Both Be Up?`
    has *Shape* / *Both present?* against a list of six brokers -- so an even split
    starves the column that carries the sentence and the last one runs off the slide.
    Widths are therefore proportional to the widest natural cell in each column, and
    the cells are wrapped HERE rather than in a back end, so the PowerPoint table and
    the preview agree about how tall the row is.

    **⚑ But proportional alone starves the label column, and it does it silently.**
    The natural width of a prose column is the whole unwrapped sentence, so on a table
    whose last column is a paragraph the scale factor is small -- and a *narrow* column
    is scaled by the same factor, down past the width of the one word it holds. On
    `Faults, by Pattern` that rendered `Out-Only` as "Out-" and **both** `In-Only` and
    `In-Out` as "In-O", on the one slide whose entire argument is per-pattern. So every
    column also gets a **min-content floor** -- its longest unbreakable word -- and only
    the slack above that floor is shared out proportionally. A column can be squeezed to
    wrapping, never to clipping."""
    ncol = max(len(r) for r in raw_rows)
    nat = [0.0] * ncol      # widest cell unwrapped -- what the column would like
    mini = [0.0] * ncol     # longest single word  -- what it cannot go below
    for ri, row in enumerate(raw_rows):
        for ci in range(ncol):
            txt = row[ci] if ci < len(row) else ""
            bold = bool(ri == 0 and head)
            nat[ci] = max(nat[ci], Type.width(O.plain(txt), SANS, TABLE_PT, bold))
            for word, b, i, m, _ in Type.tokens(O.runs(txt)):
                mini[ci] = max(mini[ci], Type.width(word, MONO if m else SANS,
                                                    TABLE_PT, b or bold))
    mini = [min(mi, na) for mi, na in zip(mini, nat)]

    avail = w - 2 * CELL_PAD * ncol
    if sum(nat) <= avail or sum(mini) >= avail:
        # everything fits at its natural width, or nothing does. The second case is a
        # table too wide to set at all, and it is the one remaining way a word can be
        # clipped -- so it says so rather than going quiet, because a clipped label
        # looks like a short label and nothing downstream can tell the difference.
        if sum(mini) >= avail:
            sys.stderr.write(
                f"    ⚑ table will clip: its longest words need {sum(mini):.1f}in "
                f"of {avail:.1f}in -- shorten a heading or drop a column\n")
        k = avail / max(sum(nat), 1e-6)
        cols = [n * k + 2 * CELL_PAD for n in nat]
    else:
        slack = avail - sum(mini)
        want = [max(na - mi, 0.0) for na, mi in zip(nat, mini)]
        k = slack / max(sum(want), 1e-6)
        cols = [mi + wa * k + 2 * CELL_PAD for mi, wa in zip(mini, want)]

    rows = []
    for ri, row in enumerate(raw_rows):
        cells, lines_max = [], 1
        for ci in range(ncol):
            txt = row[ci] if ci < len(row) else ""
            runs = O.runs(txt)
            if ri == 0 and head:
                runs = [(t, True, i, m) for t, b, i, m in runs]
            lines = Type.wrap(runs, cols[ci] - 2 * CELL_PAD, SANS, TABLE_PT)
            cells.append(lines)
            lines_max = max(lines_max, len(lines))
        rows.append(dict(h=lines_max * _in(TABLE_PT) * CELL_LEAD + 2 * CELL_PAD,
                         cells=cells))
    return cols, rows


# ---- layout ------------------------------------------------------------------

# Phase 2 measured every label with the figure displayed this wide. `reads_at.py`'s
# 890-unit reference is the same number seen from the other side: 890 canvas units
# across 12.4 inches. Plan §8 items 9 and 10.
REFERENCE_IN = 12.4


def path_of(b):
    return os.path.join(REPO, b.src)


class Laid:
    """A laid-out slide: its ops, plus what did not fit."""

    def __init__(self, slide, kind):
        self.slide = slide
        self.kind = kind
        self.ops = []
        self.overflow = 0.0      # inches the body wanted beyond the room it had
        self.notes = []
        self.split = False       # True when one outline entry became two slides
        self.figures = []        # (src, rendered_w_in, canvas_w, canvas_h)

    def reads_at(self):
        """For each drawn figure, the fraction of its Phase 2 label size that
        survives at the size it is actually rendered here."""
        out = []
        for src, pw, cw, ch in self.figures:
            eff = max(cw, 2.2 * ch)
            out.append((src, pw, (pw / cw) * eff / REFERENCE_IN))
        return out

    def __iadd__(self, op):
        self.ops.append(op)
        return self


def _lines(runs, w, family, pt, x, y, colour, lead=LEAD, track=0.0):
    """Wrap and emit a block of text. Returns (ops, height in inches).

    `y` is the TOP of the block; the first baseline sits 0.80em below it, which is
    about the cap height and keeps a block's visual top where the caller put it."""
    wrapped = Type.wrap(runs, w, family, pt, track)
    ops, cy = [], y + _in(pt) * 0.80
    for line in wrapped:
        ops.append(Text(x, cy, line, family, pt, colour, track))
        cy += _in(pt) * lead
    return ops, len(wrapped) * _in(pt) * lead


class Deck:
    def __init__(self, deck, day):
        self.deck = deck
        self.day = day
        self.slides = []          # list[Laid]
        self.compare = []         # entries whose figures were shown one at a time
        self._kicker_warned = set()   # one line per offending title, not per slide

    # -- chrome ----------------------------------------------------------------
    def _ground(self, laid, colour=PAPER):
        laid += Rect(0, 0, W_IN, H_IN, fill=colour)

    # The right-hand panel starts here, and the kicker is drawn full-bleed across
    # the top -- so a long `#group:` title runs UNDER a photograph rather than
    # wrapping. Nothing downstream can tell: it looks like a short kicker.
    PANEL_X = M_L + CONTENT_W * 0.52

    def _kicker(self, laid, text):
        # **A squeezed layout has to say so.** Same rule the table columns learned:
        # a clipped label looks like a short label, and no reader of the outline can
        # see the difference. Measured against the panel edge rather than the slide,
        # because any slide in a group may carry a figure.
        up = text.upper()
        adv = _Outliner.outline(up, MONO, KICKER_PT, 0, 0, "start")[1]
        w = (adv + 0.16 * KICKER_PT * max(0, len(up) - 1)) / 72.0
        if M_L + w > self.PANEL_X and up not in self._kicker_warned:
            self._kicker_warned.add(up)
            print(f"  ! kicker runs under the figure panel by "
                  f"{M_L + w - self.PANEL_X:.2f}in: {text!r}", file=sys.stderr)
        laid += Text(M_L, M_T + _in(KICKER_PT) * 0.80,
                     [(up, False, False, False)], MONO, KICKER_PT,
                     CARBON, track=0.16)
        return M_T + _in(KICKER_PT) * 1.70

    def _title(self, laid, text, y, w, pt=TITLE_PT):
        ops, h = _lines(O.runs(text), w, SERIF, pt, M_L, y, INK, lead=1.14)
        for o in ops:
            laid += o
        return y + h + 0.20

    # -- the three slide kinds -------------------------------------------------
    def title_slide(self):
        laid = Laid(None, "title")
        self._ground(laid)
        ops, h = _lines(O.runs(self.deck.title), CONTENT_W - 0.4, SERIF, 44,
                        M_L + 0.32, 2.30, INK, lead=1.12)
        # the bar is cut to the title it marks -- a fixed length reads as a stray rule
        # the moment the title is one line rather than two
        laid += Rect(M_L, 2.30 + 0.04, 0.085, h - 0.06, fill=ANNOTATION)
        for o in ops:
            laid += o
        if self.deck.intro:
            ops, _ = _lines(O.runs(O.plain(self.deck.intro[0].text)),
                            CONTENT_W * 0.60, SANS, BODY_PT, M_L + 0.32, 4.30, COMMENT)
            for o in ops:
                laid += o
        self.slides.append(laid)

    def section_slide(self, sec):
        laid = Laid(None, "section")
        self._ground(laid, MANILA)
        laid += Rect(0, 0, W_IN, 0.10, fill=ANNOTATION)
        self._kicker(laid, self.deck.title)
        y = self._title(laid, sec.name, 2.60, CONTENT_W * 0.78, pt=40)
        if sec.blurb:
            ops, _ = _lines(O.runs(sec.blurb), CONTENT_W * 0.60, SANS, BODY_PT,
                            M_L, y, COMMENT)
            for o in ops:
                laid += o
        self.slides.append(laid)

    # A photograph tolerates being small; a drawing with labels in it does not. That
    # is the whole distinction the layout turns on, and the file extension carries it:
    # every photograph in `resources/` is a `.jpg` and every drawing is a `.png`.
    @staticmethod
    def _is_photo(b):
        return b.src.lower().endswith((".jpg", ".jpeg"))

    # Below this, a body is short enough to sit above a full-width figure without
    # squeezing it; above it, the slide becomes a text slide and a figure slide.
    FIGURE_SLIDE_BODY_MAX = 1.15

    def content_slide(self, sl):
        """One outline entry becomes one slide -- or two, when it carries both an
        argument and a labelled figure.

        **Why a figure gets its own slide.** `styles.md`'s panel gives a drawing about
        4.6 inches. Phase 2 sized every label so the figure reads at 18pt displayed
        about 12.4 inches wide (plan §8 items 9, 10, 18, 19), so a figure in the panel
        reads at 37-53% of the size it was measured at -- 7 to 9 real points. Ian's
        call, 2026-09-08: **the figure leads.** Full content width restores it to about
        97%, which is the number Phase 2 spent three passes earning.

        **The callout travels with the picture and the bullets do not.** A callout is
        the one line the presenter says aloud about what is on the screen; the bullets
        are the argument that gets to it. So when an entry has to split, the argument
        goes on the first slide and the callout stands with the figure on the second.

        Photographs stay in the panel. They are not carrying 18pt labels."""
        imgs = [b for b in sl.images if b.src]
        figs = [b for b in imgs if not self._is_photo(b)]
        photos = [b for b in imgs if self._is_photo(b)]
        if not figs:
            self._text_slide(sl, sl.blocks, photos)
            return

        callouts = [b for b in sl.blocks if b.kind == "callout"]
        argument = [b for b in sl.blocks
                    if b.kind not in ("image", "callout")]
        # measure the argument against a throw-away slide to decide whether it fits
        probe = Laid(sl, "probe")
        h = self._body(probe, argument, M_L, 0.0, CONTENT_W)

        # **One labelled figure per slide.** Two figures sharing the stage each get
        # about half its linear size, which is the same 50% tax the panel charged and
        # the reason `conversations.py` merged three 2021 exports into ONE figure
        # rather than showing three. Where a slide really needs two pictures compared,
        # the answer is a composed figure -- a Phase 2 job -- so those are reported.
        first = True
        if h <= self.FIGURE_SLIDE_BODY_MAX and len(figs) == 1:
            self._figure_slide(sl, figs, argument + callouts, photos)
            return
        if argument or photos:
            self._text_slide(sl, argument, photos, split=True)
            first = False
        for i, f in enumerate(figs):
            self._figure_slide(sl, [f], callouts if i == 0 else [], [],
                               split=not (first and len(figs) == 1))
        if len(figs) > 1:
            self.compare.append((sl, len(figs)))

    def _text_slide(self, sl, blocks, photos, split=False):
        laid = Laid(sl, "content")
        laid.split = split
        self._ground(laid)
        y = self._kicker(laid, sl.group or sl.section)
        w = TEXT_W if photos else CONTENT_W
        y = self._title(laid, sl.title, y, w)
        avail = H_IN - M_B - y
        used = self._body(laid, blocks, M_L, y, w)
        if used > avail + 0.01:
            laid.overflow = used - avail
        if photos:
            self._panel(laid, photos, sl)
        self.slides.append(laid)

    def _figure_slide(self, sl, figs, above, photos, split=False):
        """Title, whatever short text belongs with the picture, then the picture --
        as wide as the slide will allow."""
        laid = Laid(sl, "figure")
        laid.split = split
        self._ground(laid)
        y = self._kicker(laid, sl.group or sl.section)
        y = self._title(laid, sl.title, y, CONTENT_W)
        if above:
            y += self._body(laid, above, M_L, y, CONTENT_W) + 0.10
        self._stage(laid, figs + photos, y)
        self.slides.append(laid)

    def _stage(self, laid, imgs, y):
        """The full-width figure stage. One picture fills it; several share it, and
        the report says what that costs."""
        x, w = M_L, CONTENT_W
        h = H_IN - M_B - y
        if h < 1.0:                       # nothing left to draw in
            laid.notes.append(f"no room for the figure: {h:.2f}in left under the text")
            return
        n = len(imgs)
        cols = 1 if n == 1 else (2 if n <= 4 else 3)
        rows = (n + cols - 1) // cols
        cw = (w - PANEL_PAD * (cols - 1)) / cols
        ch = (h - PANEL_PAD * (rows - 1)) / rows
        placed = []
        for i, b in enumerate(imgs):
            path = os.path.join(REPO, b.src)
            from PIL import Image as PImage, UnidentifiedImageError
            try:
                with PImage.open(path) as im:
                    iw, ih = im.size
            except (FileNotFoundError, UnidentifiedImageError):
                laid.notes.append(f"missing render: {b.src}")
                continue
            k = min(cw / iw, ch / ih)
            placed.append((b, iw * k, ih * k, k, iw, ih))
        for i, (b, pw, ph, k, iw, ih) in enumerate(placed):
            c, r = i % cols, i // cols
            laid += Image(x + c * (cw + PANEL_PAD) + (cw - pw) / 2,
                          y + r * (ch + PANEL_PAD) + (ch - ph) / 2, pw, ph, path_of(b))
            if not self._is_photo(b):
                laid.figures.append((b.src, pw, iw / 3.0, ih / 3.0))

    # -- body ------------------------------------------------------------------
    def _body(self, laid, blocks, x, y, w):
        cy = y
        for b in blocks:
            if b.kind == "image":
                continue
            if b.kind == "bullet":
                lvl = getattr(b, "level", 0)
                pt = SUB_PT if lvl else BODY_PT
                ind = 0.32 * lvl
                hang = 0.27
                cy += _in(7)
                # The marker is its own op at the block's left edge and the text hangs
                # to its right on EVERY line, so a wrapped bullet stays a block instead
                # of running back under its own marker.
                ops, h = _lines(O.runs(b.text), w - ind - hang, SANS, pt,
                                x + ind + hang, cy, INK)
                laid += Text(x + ind, cy + _in(pt) * 0.80,
                             [("\u2013" if lvl else "\u2022", False, False, False)],
                             SANS, pt, CARBON)
                for o in ops:
                    laid += o
                cy += h
            elif b.kind == "callout":
                cy += _in(13)
                laid += Rect(x, cy + 0.03, 0.055, _in(CALLOUT_PT) * 1.06 *
                             len(Type.wrap(O.runs(b.text), w - 0.30, HAND, CALLOUT_PT)),
                             fill=ANNOTATION)
                ops, h = _lines(O.runs(b.text), w - 0.30, HAND, CALLOUT_PT,
                                x + 0.24, cy, ANNOTATION, lead=1.06)
                for o in ops:
                    laid += o
                cy += h + _in(4)
            elif b.kind == "quote":
                cy += _in(10)
                laid += Rect(x, cy + 0.03, 0.03,
                             _in(BODY_PT) * LEAD *
                             len(Type.wrap(O.runs(b.text), w - 0.34, SANS, BODY_PT)),
                             fill=RULE)
                ops, h = _lines(O.runs(b.text), w - 0.34, SANS, BODY_PT,
                                x + 0.30, cy, COMMENT)
                for o in ops:
                    laid += o
                cy += h
            elif b.kind == "code":
                cy += _in(7)
                rows = b.text.split("\n")
                laid += Rect(x, cy - 0.06, w, len(rows) * _in(CODE_PT) * 1.30 + 0.12,
                             fill=MANILA, line=RULE, lw=0.8)
                for raw in rows:
                    laid += Text(x + 0.12, cy + _in(CODE_PT) * 0.80,
                                 [(raw, False, False, False)], MONO, CODE_PT, CARBON)
                    cy += _in(CODE_PT) * 1.30
                cy += 0.10
            elif b.kind == "table":
                cy += 0.12
                raw = ([b.head] if b.head else []) + b.rows
                cols, rows = plan_table(raw, b.head, w)
                laid += Table(x, cy, w, cols, rows, b.head)
                cy += sum(r["h"] for r in rows) + 0.16
            else:
                cy += _in(9)
                ops, h = _lines(O.runs(b.text), w, SANS, BODY_PT, x, cy, INK)
                for o in ops:
                    laid += o
                cy += h
        return cy - y

    # -- the figure panel ------------------------------------------------------
    def _panel(self, laid, imgs, sl):
        """One figure fills the panel. Two or more share it -- and that costs the room.

        **A figure fitted into half a panel reads at half its size**, which is the same
        arithmetic `tools/reads_at.py` applies to a whole slide. Phase 2 spent a session
        getting labels to 18 real points; a slide showing four of those at once throws
        it away. The builder lays them out and **reports it** rather than pretending."""
        px, py = PANEL_X, M_T
        pw, ph = PANEL_W, H_IN - M_T - M_B
        laid += Rect(px, py, pw, ph, fill=MANILA, line=RULE, lw=1.0)
        n = len(imgs)
        cols, rows = (2, (n + 1) // 2) if n >= 3 else (1, n)
        cw = (pw - PANEL_PAD * (cols + 1)) / cols
        ch = (ph - PANEL_PAD * (rows + 1)) / rows
        for i, b in enumerate(imgs):
            path = os.path.join(REPO, b.src)
            from PIL import Image as PImage, UnidentifiedImageError
            try:
                with PImage.open(path) as im:
                    iw, ih = im.size
            except (FileNotFoundError, UnidentifiedImageError):
                # a marker may point at an editable SOURCE rather than a render --
                # `.drawio`, `.excalidraw`. Those links look resolved to every count
                # in the repo, which is exactly how one stayed unrendered through the
                # whole of Phase 2. Report, do not crash, and do not silently skip.
                laid.notes.append(f"missing render: {b.src}")
                continue
            k = min(cw / iw, ch / ih)
            w, h = iw * k, ih * k
            c, r = i % cols, i // cols
            laid += Image(px + PANEL_PAD + c * (cw + PANEL_PAD) + (cw - w) / 2,
                          py + PANEL_PAD + r * (ch + PANEL_PAD) + (ch - h) / 2,
                          w, h, path)
            if not b.src.lower().endswith((".jpg", ".jpeg")):
                laid.figures.append((b.src, w, iw / 3.0, ih / 3.0))
        if n > 1:
            k = 1.0 / max(cols, rows)
            laid.notes.append(
                f"{n} figures in one panel — each is fitted to about {k*100:.0f}% "
                f"of its linear size, so its labels read at about {k*100:.0f}% too")

    def run(self):
        self.title_slide()
        for sec in self.deck.sections:
            if not sec.slides:
                continue
            self.section_slide(sec)
            for sl in sec.slides:
                self.content_slide(sl)
        return self


# ---- back end: PowerPoint ----------------------------------------------------

def _rgb(h):
    from pptx.dml.color import RGBColor
    return RGBColor.from_string(h.lstrip("#"))


def emit_pptx(laid_deck, path):
    from pptx import Presentation
    from pptx.util import Inches, Pt

    prs = Presentation()
    prs.slide_width = Inches(W_IN)
    prs.slide_height = Inches(H_IN)
    blank = prs.slide_layouts[6]

    for laid in laid_deck.slides:
        s = prs.slides.add_slide(blank)
        for kind, a in laid.ops:
            if kind == "rect":
                sh = s.shapes.add_shape(1, Inches(a["x"]), Inches(a["y"]),
                                        Inches(a["w"]), Inches(a["h"]))
                if a["fill"]:
                    sh.fill.solid()
                    sh.fill.fore_color.rgb = _rgb(a["fill"])
                else:
                    sh.fill.background()
                if a["line"]:
                    sh.line.color.rgb = _rgb(a["line"])
                    sh.line.width = Pt(a["lw"])
                else:
                    sh.line.fill.background()
                sh.shadow.inherit = False
            elif kind == "image":
                s.shapes.add_picture(a["path"], Inches(a["x"]), Inches(a["y"]),
                                     Inches(a["w"]), Inches(a["h"]))
            elif kind == "text":
                # one text box per LINE: the layout already wrapped, and letting
                # PowerPoint re-wrap would put the deck somewhere the preview is not
                h = _in(a["pt"]) * 1.5
                box = s.shapes.add_textbox(Inches(a["x"]), Inches(a["y"] - _in(a["pt"]) * 0.80),
                                           Inches(W_IN), Inches(h))
                tf = box.text_frame
                tf.word_wrap = False
                tf.margin_left = tf.margin_right = 0
                tf.margin_top = tf.margin_bottom = 0
                p = tf.paragraphs[0]
                p.line_spacing = 1.0
                for text, b, i, m in a["runs"]:
                    r = p.add_run()
                    r.text = text
                    r.font.name = MONO if m else a["family"]
                    r.font.size = Pt(a["pt"] - (1 if m else 0))
                    r.font.bold = bool(b)
                    r.font.italic = bool(i)
                    r.font.color.rgb = _rgb(a["colour"])
                    if a["track"]:
                        r.font._rPr.set("spc", str(int(a["track"] * a["pt"] * 100)))
            elif kind == "table":
                rows, cols, head = a["rows"], a["cols"], a["head"]
                shape = s.shapes.add_table(
                    len(rows), len(cols), Inches(a["x"]), Inches(a["y"]),
                    Inches(sum(cols)), Inches(sum(r["h"] for r in rows)))
                tbl = shape.table
                tbl.first_row = bool(head)
                tbl.horz_banding = False
                for ci, cw in enumerate(cols):
                    tbl.columns[ci].width = Inches(cw)
                for ri, row in enumerate(rows):
                    tbl.rows[ri].height = Inches(row["h"])
                    for ci in range(len(cols)):
                        cell = tbl.cell(ri, ci)
                        cell.margin_left = cell.margin_right = Inches(CELL_PAD)
                        cell.margin_top = cell.margin_bottom = Inches(0.03)
                        cell.fill.solid()
                        cell.fill.fore_color.rgb = _rgb(
                            MANILA if (ri == 0 and head) else PAPER)
                        tp = cell.text_frame.paragraphs[0]
                        tp.line_spacing = CELL_LEAD
                        # the layout already wrapped, so the cell is written as one
                        # run sequence and PowerPoint re-wraps to the same width
                        flat = [t for line in row["cells"][ci] for t in line]
                        for t, bo, it, mo in Type._merge(flat):
                            r = tp.add_run()
                            r.text = t
                            r.font.name = MONO if mo else SANS
                            r.font.size = Pt(TABLE_PT - (1 if mo else 0))
                            r.font.bold = bool(bo)
                            r.font.italic = bool(it)
                            r.font.color.rgb = _rgb(INK)
        if laid.slide is not None and laid.slide.notes:
            s.notes_slide.notes_text_frame.text = "\n\n".join(
                O.plain(n.text) for n in laid.slide.notes)
    prs.save(path)
    return path


# ---- back end: SVG preview ---------------------------------------------------

SCALE = 96          # px per inch in the preview


def _esc(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def emit_svg(laid, path_png):
    """Render one laid-out slide, with text outlined to paths so no font install is
    needed — the same trick, and the same reason, as `diagram.py`."""
    W, H = W_IN * SCALE, H_IN * SCALE
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" '
         f'xmlns:xlink="http://www.w3.org/1999/xlink" width="{W:.0f}" '
         f'height="{H:.0f}" viewBox="0 0 {W:.0f} {H:.0f}">']
    for kind, a in laid.ops:
        if kind == "rect":
            fill = a["fill"] or "none"
            stroke = f'stroke="{a["line"]}" stroke-width="{a["lw"]}"' if a["line"] else ""
            o.append(f'<rect x="{a["x"]*SCALE:.1f}" y="{a["y"]*SCALE:.1f}" '
                     f'width="{a["w"]*SCALE:.1f}" height="{a["h"]*SCALE:.1f}" '
                     f'fill="{fill}" {stroke}/>')
        elif kind == "image":
            import base64
            # **The MIME type comes from the extension.** Declaring a JPEG as
            # `image/png` makes librsvg drop it silently -- three photographs
            # disappeared from one panel and the slide still looked plausible.
            ext = os.path.splitext(a["path"])[1].lower()
            mime = {".jpg": "jpeg", ".jpeg": "jpeg", ".gif": "gif"}.get(ext, "png")
            with open(a["path"], "rb") as fh:
                b64 = base64.b64encode(fh.read()).decode()
            o.append(f'<image x="{a["x"]*SCALE:.1f}" y="{a["y"]*SCALE:.1f}" '
                     f'width="{a["w"]*SCALE:.1f}" height="{a["h"]*SCALE:.1f}" '
                     f'preserveAspectRatio="xMidYMid meet" '
                     f'xlink:href="data:image/{mime};base64,{b64}"/>')
        elif kind == "text":
            x = a["x"] * SCALE
            y = a["y"] * SCALE
            for text, b, i, m in a["runs"]:
                fam = MONO if m else a["family"]
                pt = (a["pt"] - (1 if m else 0)) * SCALE / 72.0
                wt = 600 if b else 400
                if a["track"]:
                    for ch in text:
                        d, adv = _Outliner.outline(ch, fam, pt, x, y, "start",
                                                   weight=wt if fam == SANS else None)
                        if d:
                            o.append(f'<path d="{d}" fill="{a["colour"]}"/>')
                        x += adv + a["track"] * pt
                else:
                    d, adv = _Outliner.outline(text, fam, pt, x, y, "start",
                                               weight=wt if fam == SANS else None)
                    if d:
                        o.append(f'<path d="{d}" fill="{a["colour"]}"/>')
                    x += adv
        elif kind == "table":
            rows, cols, head = a["rows"], a["cols"], a["head"]
            ry = a["y"]
            for ri, row in enumerate(rows):
                cx = a["x"]
                for ci, cw in enumerate(cols):
                    o.append(f'<rect x="{cx*SCALE:.1f}" y="{ry*SCALE:.1f}" '
                             f'width="{cw*SCALE:.1f}" height="{row["h"]*SCALE:.1f}" '
                             f'fill="{MANILA if (ri==0 and head) else PAPER}" '
                             f'stroke="{RULE}" stroke-width="0.8"/>')
                    pt = TABLE_PT * SCALE / 72.0
                    ty = (ry + CELL_PAD) * SCALE + pt * 0.80
                    for line in row["cells"][ci]:
                        tx = (cx + CELL_PAD) * SCALE
                        for t, b, i, m in line:
                            d, adv = _Outliner.outline(
                                t, MONO if m else SANS, pt, tx, ty, "start",
                                weight=600 if b else 400)
                            if d:
                                o.append(f'<path d="{d}" fill="{INK}"/>')
                            tx += adv
                        ty += pt * CELL_LEAD
                    cx += cw
                ry += row["h"]
    o.append("</svg>")
    svg = "\n".join(o)
    with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False,
                                     encoding="utf-8") as fh:
        fh.write(svg)
        tmp = fh.name
    try:
        subprocess.run(["rsvg-convert", "-o", path_png, tmp], check=True)
    finally:
        os.unlink(tmp)
    return path_png


# ---- drive -------------------------------------------------------------------

def build(md, day):
    return Deck(O.parse(md), day).run()


def main(argv):
    days = {"1": "outlines/DayOne.md", "2": "outlines/DayTwo.md"}
    want = argv[argv.index("--day") + 1] if "--day" in argv else None
    preview = argv[argv.index("--preview") + 1] if "--preview" in argv else None
    write = "--report" not in argv

    for d, p in days.items():
        if want and d != want:
            continue
        deck = build(os.path.join(REPO, p), d)
        over = [l for l in deck.slides if l.overflow > 0.01]
        multi = [(l, n) for l in deck.slides for n in l.notes if "in one panel" in n]
        missing = [(l, n) for l in deck.slides for n in l.notes if n.startswith("missing")]

        if write:
            os.makedirs(OUT_DIR, exist_ok=True)
            out = os.path.join(OUT_DIR, f"Practical Messaging - Day {d}.pptx")
            emit_pptx(deck, out)
            where = f"  ->  {os.path.relpath(out, REPO)}"
        else:
            where = "  (not written)"
        print(f"\n=== Day {d}: {len(deck.slides)} slides{where}")

        if over:
            print(f"    ⚑ {len(over)} slides overflow at the {BODY_PT}pt floor "
                  f"— content decisions, not layout ones:")
            for l in sorted(over, key=lambda l: -l.overflow):
                print(f"      {l.overflow:5.2f}in over   "
                      f"{l.slide.section[:22]:<24} {l.slide.title[:46]}")
        if multi:
            print(f"    {len(multi)} slides group photographs in a panel:")
            for l, n in multi:
                print(f"      {l.slide.section[:22]:<24} {l.slide.title[:38]}")
        if deck.compare:
            print(f"    ⚑ {len(deck.compare)} entries carry more than one figure and "
                  f"now show them one per slide — a composed figure would be better "
                  f"where the reader has to compare:")
            for sl, n in deck.compare:
                print(f"      {n} figures   {sl.section[:22]:<24} {sl.title[:40]}")

        # what the room actually gets, against what Phase 2 measured
        small = []
        for l in deck.slides:
            for src, pw, frac in l.reads_at():
                if frac < 0.85:
                    small.append((l, src, pw, frac))
        splits = sum(1 for l in deck.slides if l.split) // 2
        best = [frac for l in deck.slides for _s, _w, frac in l.reads_at()]
        if best:
            print(f"    figures: {len(best)} placed, "
                  f"{sum(1 for f in best if f >= 0.85)} at 85%+ of their Phase 2 "
                  f"label size (median {sorted(best)[len(best)//2]*100:.0f}%)"
                  + (f"; {splits} entries became two slides" if splits else ""))
        if small:
            print(f"    ⚑ {len(small)} figures still land under 85%:")
            for l, src, pw, frac in sorted(small, key=lambda t: t[3])[:12]:
                print(f"      {frac*100:3.0f}%  {pw:4.1f}in  "
                      f"{os.path.basename(src)[:34]:<36} {l.slide.title[:30]}")
        for l, n in missing:
            print(f"    ! {l.slide.title[:50]}: {n}")

        if preview:
            os.makedirs(os.path.join(OUT_DIR, "preview"), exist_ok=True)
            if preview == "all":
                idx = range(len(deck.slides))
            elif preview == "over":
                idx = [i for i, l in enumerate(deck.slides) if l.overflow > 0.01]
            else:
                idx = [int(x) for x in preview.split(",")]
            for i in idx:
                png = os.path.join(OUT_DIR, "preview", f"day{d}-{i:03d}.png")
                emit_svg(deck.slides[i], png)
            print(f"    previews: {len(list(idx))} -> build/preview/")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
