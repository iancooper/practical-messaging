#!/usr/bin/env python3
"""Phase 3 — build the two `.pptx` decks from `outlines/`, to `styles.md`.

    python3 tools/build_deck.py                 # both days -> build/
    python3 tools/build_deck.py --day 1
    python3 tools/build_deck.py --report        # measure only, write nothing
    python3 tools/build_deck.py --no-animation  # no progressive disclosure
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

# **How much narrower a callout is assumed to set in a SUBSTITUTED face.** Ian, 2026-09-12,
# on Day 2 slides 7 and 82: a callout overlapping the prose under it, and a callout clipped
# by the diagram under it. Both clear in the preview AND in the layout -- slide 7 reserves
# 0.534in -- so the error is in PowerPoint, and it is not `_first_baseline`: Caveat's lift at
# 24pt/1.06 is 0.808em against the 0.80em assumed, which is 0.008em.
#
# It is `BACKLOG.md` F2. Caveat is not installed on his machine, PowerPoint substitutes a
# wider face, and the callout wraps to a second line -- into a reserve computed for one. R0-2
# turned `word_wrap` on, which is what converted Day 1's *runs off the right of the slide*
# into *grows down into whatever is below*, so this is R0-3's residual rather than a new bug.
#
# **Ian's chosen fix is to install the fonts**, which no builder change can substitute for:
# a wider face is also the WRONG face, and nothing here can make a fallback look like
# handwriting. This number only makes the risk visible so it is never diagnosed from scratch
# again. **It is a guard, not a measurement.** There is no way to measure the substitute
# without PowerPoint, so it is calibrated on the only evidence there is: the two callouts
# Ian saw overlap, at 93.7% and **90.6%** of their measure. 0.92 caught the first and missed
# the second, so the substitute is at least ~11% wider than Caveat and this is 0.90.
SUBST_W = 0.90
TABLE_PT   = 15
CODE_PT    = 15
FOLIO_PT   = 10        # the slide number. Quieter than the kicker on purpose

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

# The fourth arrangement -- `#layout: side`. Ian, 2026-09-10, on six §4.4 slides:
# *"shrink the diagram… put the text on the left… It's too weird to read the words,
# then show the diagram here."* The drawing gets the larger half, because it is the
# half that carries type.
SIDE_TEXT_W = (CONTENT_W - GUTTER) * 0.47
SIDE_FIG_W  = (CONTENT_W - GUTTER) * 0.53
SIDE_FIG_X  = M_L + SIDE_TEXT_W + GUTTER
# Where the drawing sits in the half-stage, as a fraction of the slack above it. 0.5
# is true centre and reads low; see `_side_slide`.
SIDE_FIG_RISE = 0.40


def _in(pt):
    return pt / 72.0


def _op_top(kind, a):
    """The topmost inch of a draw-op, for asking what sits under something.

    Every op but `text` is placed by its top-left. `text` is placed by its
    BASELINE, so its top is a font-ascent above that -- the same 0.80em the
    layout uses to put a baseline inside a box. Approximate on purpose: this
    decides whether two things are a line apart, not where a glyph starts."""
    if kind == "text":
        return a["y"] - _in(a["pt"]) * 0.80
    return a["y"]


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

def Text(x, y, runs, family, pt, colour, track=0.0, align="l", block=None):
    """One LINE of text. `y` is the baseline. Runs are (text, bold, italic, mono).

    **`block` is the paragraph this line came out of**, shared by every line of it and
    `None` for a line that was never part of one -- the kicker, the folio, a bullet's
    marker, a row of a code listing. The SVG preview ignores it and draws line by line;
    `emit_pptx` uses it to write **one text box per paragraph** instead of one per
    line. See `_block` for why that matters and what it costs."""
    return ("text", dict(x=x, y=y, runs=runs, family=family, pt=pt,
                         colour=colour, track=track, align=align, block=block))


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
        cells, flat, lines_max = [], [], 1
        for ci in range(ncol):
            txt = row[ci] if ci < len(row) else ""
            runs = O.runs(txt)
            if ri == 0 and head:
                runs = [(t, True, i, m) for t, b, i, m in runs]
            lines = Type.wrap(runs, cols[ci] - 2 * CELL_PAD, SANS, TABLE_PT)
            cells.append(lines)
            # **`cells` is wrapped, `flat` is not, and the back ends want different
            # ones.** The preview draws the wrapped lines; PowerPoint is given the
            # cell whole and re-wraps it to the same column. Flattening `cells` to
            # get the second one LOSES A SPACE at every break, because `wrap` carries
            # each word's leading space inside its own piece and the word that starts
            # a line has none -- so `we need to know what we sent` was written into
            # the `.pptx` as `we need to knowwhat we sent`, and `State Machine` as
            # `StateMachine`, one unbreakable token in a narrow column. 51 of them
            # across 37 cells in both decks, and **invisible in the preview**, which
            # draws the lines separately and so always read correctly.
            #
            # Re-inserting a space at each boundary is NOT the fix: `wrap` breaks
            # before the current word whether or not that word had a space in front
            # of it, and `**bold**, then` puts `bold` and `,` on one line with no
            # space between them -- a break there would write `bold ,`. The space is
            # only safe where it was never removed, so keep the unwrapped runs.
            flat.append(Type._merge(runs))
            lines_max = max(lines_max, len(lines))
        rows.append(dict(h=lines_max * _in(TABLE_PT) * CELL_LEAD + 2 * CELL_PAD,
                         cells=cells, flat=flat))
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
        self.layered = []        # (src, layer count) for any `+ layers` picture
        # **Callouts a substituted face would push onto an extra line**, as
        # (text, lines, reserved_bottom_in). Whether that is a DEFECT depends on
        # what ends up underneath, which is not known until the slide is laid
        # out -- so the test is deferred to `_callout_collisions`.
        self.callouts = []
        # **What to call a slide that has no outline entry.** `deck_index` is how Ian
        # turns a slide number into something addressable, and a group divider with
        # no entry printed as a bare `[group]` -- unreviewable. Set by `group_slide`.
        self.label = None
        self.label_section = None
        # **Progressive disclosure, grouped by idea.** 0 is what is on screen before
        # the first click -- the ground, the kicker, the title, the folio. Everything
        # above 0 is a click. `_body` decides the grouping; see `_reveals`.
        self.step = 0

    def reads_at(self):
        """For each drawn figure, the fraction of its Phase 2 label size that
        survives at the size it is actually rendered here."""
        out = []
        for src, pw, cw, ch in self.figures:
            eff = max(cw, 2.2 * ch)
            out.append((src, pw, (pw / cw) * eff / REFERENCE_IN))
        return out

    def __iadd__(self, op):
        op[1]["step"] = self.step
        self.ops.append(op)
        return self

    def reveals(self):
        """How many clicks this slide takes. 0 means it is all there at once."""
        return max((a.get("step", 0) for _k, a in self.ops), default=0)


def _linebox(family):
    """The line box the FONT asks for, in ems -- `hhea` ascent to descent.

    **This is the number PowerPoint will not go below.** `LEAD` and the callout's 1.06
    are *inter-line* spacing, chosen for how a block looks; they are not a promise that
    the last line's descenders fit inside them. Caveat's glyphs span **1.260em** and the callout
    reserved 1.06 -- so every callout under-reserved 0.200em, and whatever the layout
    put next went 0.067in too high. On a text slide that lands on the following
    paragraph; on a figure slide the picture is opaque and simply covers it.

    **Invisible in the preview by construction**, because the preview draws the lines
    itself at the same 1.06 and so agrees with the layout. Ian found it from the
    rendered deck on slides 50, 58, 76 and 113 of Day 1."""
    key = ("_lb", family)
    if key not in Type._cache:
        from fontTools.ttLib import TTFont
        f = TTFont(os.path.join(FONT_DIR, _FILES[family]), fontNumber=0, lazy=True)
        h, upem = f["hhea"], f["head"].unitsPerEm
        Type._cache[key] = (h.ascent - h.descent) / upem
    return Type._cache[key]


def _reserve(family, lead):
    """How much the LAST line of a block reserves, in ems.

    **Caveat only, and that is a decision rather than an oversight.** Both leads sit
    under their font's ink extent -- the callout's 1.06 against Caveat's 1.260, the
    body's `LEAD` 1.24 against Plex's 1.300 -- but they are not the same size of wrong.
    Caveat is short by 0.200em and has collided four times in a built deck; Plex is
    short by 0.060em and never has, because body blocks carry an explicit gap before
    the next one while a figure is laid straight onto the stage. Raising Plex as well
    costs four slides their fit for a margin nothing has reported.
    **`styles.md`: Caveat never carries body copy**, so keying on the family keys on
    exactly the blocks at risk."""
    return max(lead, _linebox(family)) if family == HAND else lead


def _lines(runs, w, family, pt, x, y, colour, lead=LEAD, track=0.0):
    """Wrap and emit a block of text. Returns (ops, height in inches).

    `y` is the TOP of the block; the first baseline sits 0.80em below it, which is
    about the cap height and keeps a block's visual top where the caller put it.

    Every line carries the same `block` dict, so the two back ends can disagree about
    granularity without disagreeing about layout: the preview draws the lines, the
    `.pptx` draws the paragraph."""
    wrapped = Type.wrap(runs, w, family, pt, track)
    block = dict(runs=Type._merge(list(runs)), w=w, lead=lead, n=len(wrapped))
    ops, cy = [], y + _in(pt) * 0.80
    for line in wrapped:
        ops.append(Text(x, cy, line, family, pt, colour, track, block=block))
        cy += _in(pt) * lead
    # **The last line is reserved at the font's own line box, not at `lead`.** Inter-line
    # spacing stays `lead` -- that is a look, and Caveat's 1.06 is deliberately tight --
    # but the block cannot claim to end before its descenders do. See `_linebox`.
    return ops, ((len(wrapped) - 1) * lead + _reserve(family, lead)) * _in(pt)


class Deck:
    def __init__(self, deck, day):
        self.deck = deck
        self.day = day
        self.slides = []          # list[Laid]
        self.compare = []         # entries whose figures were shown one at a time
        self._kicker_warned = set()   # one line per offending title, not per slide
        self._callout_warned = set()  # one line per callout, not per slide it lands on

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

    def _folio(self, laid, n):
        """The slide number, bottom left.

        **Ian reviews by slide number**, and until this existed the only way to name a
        slide in a review was to describe it. It sits in the bottom margin -- below
        `H_IN - M_B`, which is where `_stage` stops the figure -- so it cannot collide
        with anything the layout placed. Plex Mono like the kicker, carbon like the
        kicker, two points smaller: it is an address, not a piece of the slide."""
        laid.step = 0                       # chrome, not a reveal
        laid += Text(M_L, H_IN - 0.20, [(str(n), False, False, False)],
                     MONO, FOLIO_PT, CARBON, track=0.10)

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

    def group_slide(self, sec, group, line):
        """A `#group:` divider -- the quiet card. **Deliberately not a section.**

        Ian, 2026-09-12, asked for a header on each of Day 2's four movements. A
        `#group:` had never made a slide: it sets the kicker and nothing else, and
        `run()` called `section_slide()` once per `##` only.

        **The whole design problem is that it must NOT look like a `##` divider**, or
        the room reads *Movement B* as a new section when it is one beat inside *Flow
        and Reactive Programming*. A section card is manila, carries a 0.10in red bar
        and sets its title at 40pt; this one is **paper, no bar, and 29pt** -- the same
        weight as any slide title -- so it reads as a pause, not a boundary. Ian chose
        this shape over manila-without-the-bar and over a 40pt rule, both of which kept
        too much of the section card's weight.

        **The eyebrow is CARBON, not muted**, though the mock-up that was agreed said
        muted: `styles.md` puts muted at 3.6:1 on paper and reserves it for lines, not
        letters. Carbon is also the right answer on its own terms -- the four-colour
        rule gives carbon to *where does it go?*, and `Movement A` is an address.

        The group title splits on the em dash into that address and the title proper;
        a group with no dash just sets a title."""
        laid = Laid(None, "group")
        laid.label, laid.label_section = group, sec.name
        self._ground(laid, PAPER)
        self._kicker(laid, sec.name)
        label, _, name = group.partition("—")
        label, name = label.strip(), name.strip()
        y = 2.60
        if name:
            laid += Text(M_L, y, [(label.upper(), False, False, False)],
                         MONO, KICKER_PT, CARBON, track=0.16)
            y += _in(KICKER_PT) * 1.70
        else:
            name = label
        y = self._title(laid, name, y, CONTENT_W * 0.78)
        ops, _ = _lines(O.runs(line), CONTENT_W * 0.60, SANS, BODY_PT,
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
        # `#layout: side` overrides everything below it: one slide, argument on the
        # left, the drawing on the right. It is opt-in per entry and it is a real
        # trade -- see `_side_slide` and the size the builder reports for it.
        if sl.layout == "side" and len(figs) == 1:
            self._side_slide(sl, figs[0], argument + callouts, photos)
            return
        # **`#layout: figure` forces the one-slide stack** -- title, the argument
        # across the full width, then the drawing across the full width under it.
        # It is the same arrangement `_figure_slide` gives a short entry; the flag
        # just overrides FIGURE_SLIDE_BODY_MAX, which is a threshold and not a rule.
        # Ian, 2026-09-12, ruling on the BPMN `side` merges: *"move it below the text,
        # you have more space with greater width to make it larger"*. The drawing keeps
        # the full 12.4in, so it loses only the height the argument takes -- and a wide,
        # short figure was fitted by WIDTH, so it loses nothing at all.
        if sl.layout == "figure" and len(figs) == 1:
            self._figure_slide(sl, figs, argument + callouts, photos)
            return
        # `#layout: split` forces the other way: argument and drawing on separate
        # slides, for an entry the threshold would have combined.
        if sl.layout == "split" and len(figs) == 1:
            self._text_slide(sl, argument, photos, split=True)
            self._figure_slide(sl, figs, callouts, [], split=True)
            return
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
            laid.step += 1
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
        laid.step += 1                      # the picture is its own reveal
        self._stage(laid, figs + photos, y)
        self.slides.append(laid)

    def _side_slide(self, sl, fig, blocks, photos):
        """Title full width, then the argument on the left and the drawing on the right.

        **This is the arrangement `styles.md` argues against**, and it is opt-in for
        that reason. The figure-leads default exists because Phase 2 sized every label
        to read at 18pt with the drawing about 12.4in wide, and half a slide takes most
        of that back. Ian asked for it on six §4.4 slides where the words and the
        picture are one thought -- *"It's too weird to read the words, then show the
        diagram here"* -- so the builder does it and **reports what each one cost**,
        rather than absorbing the loss quietly. If a slide's text will not fit beside
        the picture, the answer is Ian's: *"move some text to notes."*"""
        laid = Laid(sl, "side")
        self._ground(laid)
        y = self._kicker(laid, sl.group or sl.section)
        y = self._title(laid, sl.title, y, CONTENT_W)
        avail = H_IN - M_B - y
        used = self._body(laid, blocks, M_L, y, SIDE_TEXT_W)
        if used > avail + 0.01:
            laid.overflow = used - avail
        laid.step += 1                      # the picture is its own reveal
        # **The drawing sits optically centred, not mathematically centred.** A short
        # figure exactly halfway down a tall stage reads as LOW, because the text
        # beside it starts at the top and the eye takes the pair as one block. Ian,
        # 2026-09-12, on *BPMN -- The Elements*: *"move it up slightly so the top edge
        # is more aligned with the text 'There are two kinds of arrow'. That looks to
        # be one row of height."* On that slide 0.40 puts it within a few points of
        # where he asked, and unlike centring it on the argument -- which was the first
        # attempt and overshot by two lines -- it degrades safely: a figure that fills
        # the stage does not move at all.
        self._stage(laid, [fig] + photos, y, x=SIDE_FIG_X, w=SIDE_FIG_W,
                    optical=SIDE_FIG_RISE)
        self.slides.append(laid)

    def _stage(self, laid, imgs, y, x=None, w=None, optical=None):
        """The full-width figure stage. One picture fills it; several share it, and
        the report says what that costs.

        `optical` replaces the 0.5 in the vertical centring of a single picture, so
        `_side_slide` can seat its drawing a little above true centre. Only the
        POSITION changes; the picture is still sized against the whole stage."""
        x = M_L if x is None else x
        w = CONTENT_W if w is None else w
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
            dy = (ch - ph) / 2
            if optical is not None and len(placed) == 1:
                dy = min(max((ch - ph) * optical, 0.0), max(ch - ph, 0.0))
            ix = x + c * (cw + PANEL_PAD) + (cw - pw) / 2
            iy = y + r * (ch + PANEL_PAD) + dy
            laid += Image(ix, iy, pw, ph, path_of(b))
            if not self._is_photo(b):
                laid.figures.append((b.src, pw, iw / 3.0, ih / 3.0))
            if getattr(b, "layers", False):
                self._layers(laid, b, ix, iy, pw, ph)

    # **This is how a figure gets animated without the builder animating INSIDE one.**
    # `REVIEW.md` R4-13 recorded that as the blocker -- `<p:timing>` groups by outline
    # block, not by parts of a picture -- and it is true and stays true. What moves is
    # where the parts live: the family renders each click as its own TRANSPARENT PNG on
    # the base's canvas, and they are stacked here at the base's exact rect with a step
    # each. To `_timing` they are simply seven more image ops in seven more reveal
    # groups, which it has always been able to do.
    #
    # Same rect, same scale, no re-fitting: a layer shares the base's canvas, so fitting
    # it independently would drift it off the drawing it annotates.
    def _layers(self, laid, b, x, y, w, h):
        stem, ext = os.path.splitext(os.path.join(REPO, b.src))
        n = 0
        while True:
            nxt = f"{stem}-l{n + 1}{ext}"
            if not os.path.exists(nxt):
                break
            n += 1
            laid.step += 1
            laid += Image(x, y, w, h, nxt)
        if n:
            laid.layered.append((b.src, n))
        else:
            laid.notes.append(f"`+ layers` but no {os.path.basename(stem)}-l1{ext}")

    # -- body ------------------------------------------------------------------
    #
    # **The reveal grouping, and it is inferred rather than written.** Ian ruled on
    # it 2026-09-10, against a `#reveal` marker in the outline: *"grouped by idea, not
    # naively one transition per paragraph"* -- and the grouping the outline already
    # expresses is the right one. A lead-in paragraph and the bullets under it are one
    # idea and arrive together; a table, a code listing, a quotation or a callout is
    # its own; a run of bullets with no lead-in is one step, not five.
    #
    # A slide whose grouping is wrong is fixed in PowerPoint, per shape, which is what
    # one text box per paragraph (R0-2) bought.
    @staticmethod
    def _reveals(prev, kind, per_bullet=False):
        """True when `kind` opens a new reveal step after a block of `prev`.

        `per_bullet` is `#reveal: bullets` -- see the note on the directive in
        `outline.py`. The inferred rule folds a bullet run into one idea, which is
        wrong where the bullets *are* the ideas."""
        if per_bullet and kind == "bullet":
            return True
        return not (kind == "bullet" and prev in ("prose", "bullet"))

    def _body(self, laid, blocks, x, y, w):
        cy = y
        prev = None
        per_bullet = (laid.slide is not None
                      and getattr(laid.slide, "reveal", None) == "bullets")
        for b in blocks:
            if b.kind == "image":
                continue
            if self._reveals(prev, b.kind, per_bullet):
                laid.step += 1
            prev = b.kind
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
                runs, meas = O.runs(b.text), w - 0.30
                n = len(Type.wrap(runs, meas, HAND, CALLOUT_PT))
                # **The reserve is n lines of Caveat, and a substituted face may need
                # n + 1.** Everything below this callout is then 1.06em too high. See
                # SUBST_W: the fix is installing the font, and this is the warning.
                if len(Type.wrap(runs, meas * SUBST_W, HAND, CALLOUT_PT)) > n:
                    laid.callouts.append((O.plain(b.text), n,
                                          cy + _in(CALLOUT_PT) * 1.06 * n))
                laid += Rect(x, cy + 0.03, 0.055, _in(CALLOUT_PT) * 1.06 * n,
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

    def _callout_collisions(self, laid, folio):
        """Name the callouts a substituted Caveat would drive into something.

        **The wrap is not the defect; the collision is.** Ian's 2026-09-12 pass
        proved both halves of that. Three warned slides were clean because the
        callout was the last thing on them and the extra line grew into empty
        space, and one real collision -- Day 1 slide 46 -- was never warned at
        all. So the question is how much CLEARANCE the callout has, which no
        amount of measuring its width can answer and which is not known until
        the slide is laid out. Hence: recorded in `_body`, judged here.

        **⚑ `SUBST_W` is one number and the substitute is a different FACE.**
        A scalar cannot rank per-glyph widths, so this list is the callouts
        *at risk*, never a prediction of which will break. It got four of five
        right on Ian's machine and made the fifth look like a separate bug.

        Called before `_folio` so the folio is not mistaken for what is below.
        """
        extra = _in(CALLOUT_PT) * 1.06
        for text, n, bottom in laid.callouts:
            if text in self._callout_warned:
                continue
            below = [t for t in (_op_top(k, a) for k, a in laid.ops)
                     if t >= bottom - 0.01]
            if not below:
                continue                      # grows into empty space; not a defect
            clear = min(below) - bottom
            if clear >= extra:
                continue                      # the reserve already absorbs a line
            self._callout_warned.add(text)
            print(f"  ! slide {folio}: callout would wrap {n} → {n + 1} lines in a "
                  f"face {1 / SUBST_W - 1:.0%} wider than Caveat, and has only "
                  f"{clear:.3f}in of clearance against the {extra:.3f}in that costs "
                  f"— it will be cut by what is below it on any machine where "
                  f"Caveat is missing OR the app has not been restarted since it "
                  f"was installed (BACKLOG F2): {text[:48]!r}", file=sys.stderr)

    def run(self):
        self.title_slide()
        for sec in self.deck.sections:
            if not sec.slides:
                continue
            self.section_slide(sec)
            # **The divider goes in where the group CHANGES**, which is the only place
            # the group boundary exists: a `#group:` is carried on each slide it
            # covers, not as an entry in the list. Opt-in, so a group with no
            # `#divider:` line still just sets the kicker.
            prev_group = None
            for sl in sec.slides:
                if sl.group != prev_group:
                    line = self.deck.dividers.get((sec.name, sl.group))
                    if line:
                        self.group_slide(sec, sl.group, line)
                    prev_group = sl.group
                self.content_slide(sl)
        # **Numbered here, not in the slide builders**, because the number is a
        # position in the deck and no builder knows one. The title slide is left
        # blank -- a cover with a "1" on it reads as a mistake -- so the folio on
        # every other slide is its own 1-based index and matches `deck_index.py`.
        for n, laid in enumerate(self.slides, 1):
            self._callout_collisions(laid, n)
            if laid.kind != "title":
                self._folio(laid, n)
        return self


# ---- back end: PowerPoint ----------------------------------------------------

def _rgb(h):
    from pptx.dml.color import RGBColor
    return RGBColor.from_string(h.lstrip("#"))


def _first_baseline(family, pt, lead):
    """How far below a text box's top PowerPoint puts the FIRST baseline, in inches.

    **This is the price of one text box per paragraph.** With one box per line the
    baseline was ours to place; with a paragraph in a box, PowerPoint places every
    line but the first *relative to* the first, and the first relative to the top.

    With exact line spacing (`a:lnSpc/a:spcPts`) it gives each line a box of exactly
    that height and sits the text in it in the font's own ascent : descent ratio. So
    the first baseline lands at `asc / (asc - desc) * lead` ems, where the metrics are
    the font's `hhea` -- 1.025 / -0.275 for all three Plex faces, 0.960 / -0.300 for
    Caveat. At the body's 18pt / 1.24 that is 0.978em against the 0.80em the layout
    assumed, so the box is lifted 0.18em; at the callout's 24pt Caveat / 1.06 it is
    0.808em and the lift is almost nothing.

    **⚑ This is a model of PowerPoint, not a measurement of it** -- there is no
    PowerPoint on this machine. If the decks open with every paragraph sitting a few
    points low or high, this function is the one place to correct it, and the error
    will be the same fraction of an em everywhere."""
    from fontTools.ttLib import TTFont
    key = ("_vm", family)
    if key not in Type._cache:
        f = TTFont(os.path.join(FONT_DIR, _FILES[family]), fontNumber=0, lazy=True)
        h, upem = f["hhea"], f["head"].unitsPerEm
        Type._cache[key] = h.ascent / (h.ascent - h.descent)
    return _in(pt) * Type._cache[key] * lead


def _timing(clicks):
    """The `<p:timing>` element for one slide: one click per list of shape ids.

    **Progressive disclosure, and PowerPoint has no API for it.** `python-pptx` does
    not model animation at all, so this writes the part by hand. It is the plainest
    construct PowerPoint itself emits -- an `entr` effect that `p:set`s
    `style.visibility` to `visible` -- because this is the one thing in the build that
    **cannot be checked on this machine.** There is no PowerPoint here to open the
    result in, and a malformed `p:timing` does not degrade, it makes the file refuse
    to open. So: nothing clever, ids allocated strictly in document order, and every
    `spid` asserted against the shapes actually written before the part is attached.

    The first shape of a click is `clickEffect`; the rest are `withEffect` and arrive
    with it. That is what makes a group a group.
    """
    from pptx.oxml import parse_xml
    from pptx.oxml.ns import nsdecls

    n = [2]                       # 1 is tmRoot, 2 is the main sequence

    def nxt():
        n[0] += 1
        return n[0]

    out = []
    for ids in clicks:
        effects = []
        for i, sid in enumerate(ids):
            eid, sid_tn = nxt(), None
            sid_tn = nxt()
            effects.append(
                f'<p:par><p:cTn id="{eid}" presetID="1" presetClass="entr" '
                f'presetSubtype="0" fill="hold" grpId="0" '
                f'nodeType="{"clickEffect" if i == 0 else "withEffect"}">'
                f'<p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
                f'<p:set><p:cBhvr><p:cTn id="{sid_tn}" dur="1" fill="hold">'
                f'<p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
                f'<p:tgtEl><p:spTgt spid="{sid}"/></p:tgtEl>'
                f'<p:attrNameLst><p:attrName>style.visibility</p:attrName>'
                f'</p:attrNameLst></p:cBhvr><p:to><p:strVal val="visible"/></p:to>'
                f'</p:set></p:childTnLst></p:cTn></p:par>')
        outer, inner = nxt(), nxt()
        out.append(
            f'<p:par><p:cTn id="{outer}" fill="hold">'
            f'<p:stCondLst><p:cond delay="indefinite"/></p:stCondLst><p:childTnLst>'
            f'<p:par><p:cTn id="{inner}" fill="hold">'
            f'<p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
            + "".join(effects) +
            '</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>')

    return parse_xml(
        f'<p:timing {nsdecls("p", "a")}><p:tnLst><p:par>'
        f'<p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">'
        f'<p:childTnLst><p:seq concurrent="1" nextAc="seek">'
        f'<p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
        + "".join(out) +
        '</p:childTnLst></p:cTn>'
        '<p:prevCondLst><p:cond evt="onPrev" delay="0">'
        '<p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
        '<p:nextCondLst><p:cond evt="onNext" delay="0">'
        '<p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>'
        '</p:seq></p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>')


def emit_pptx(laid_deck, path, animate=True):
    from pptx import Presentation
    from pptx.util import Inches, Pt

    prs = Presentation()
    prs.slide_width = Inches(W_IN)
    prs.slide_height = Inches(H_IN)
    blank = prs.slide_layouts[6]

    for laid in laid_deck.slides:
        s = prs.slides.add_slide(blank)
        done = set()          # blocks already written, so a paragraph gets one box
        steps = {}            # reveal step -> shape ids, in document order
        for kind, a in laid.ops:
            sh = None
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
                sh = s.shapes.add_picture(a["path"], Inches(a["x"]), Inches(a["y"]),
                                          Inches(a["w"]), Inches(a["h"]))
            elif kind == "text":
                # **One text box per PARAGRAPH, not per line.** Ian, 2026-09-10:
                # *"a paragraph is split into three text boxes. This will make it hard
                # to add animation for progressive disclosure… we want text box per
                # paragraph, bullet, or heading."*
                #
                # This file used to write one box per wrapped line with
                # `word_wrap = False`, on the reasoning that the layout had already
                # wrapped and letting PowerPoint re-wrap would put the deck somewhere
                # the preview is not. **That reasoning cost four slides.** A box with
                # wrapping off does not merely keep the line -- it lets it run off the
                # right-hand edge of the slide, and with the house fonts not installed
                # (`BACKLOG.md` F2) PowerPoint substitutes a wider face and every long
                # callout did exactly that. Wrapping to the measured width degrades;
                # not wrapping does not. The table cells already made this trade.
                blk = a.get("block")
                if blk is not None:
                    if id(blk) in done:
                        continue          # a later line of a paragraph already written
                    done.add(id(blk))
                    runs, ww, lead, n = blk["runs"], blk["w"], blk["lead"], blk["n"]
                else:
                    runs, ww, lead, n = a["runs"], None, 1.0, 1
                top = a["y"] - (_first_baseline(a["family"], a["pt"], lead)
                                if blk is not None else _in(a["pt"]) * 0.80)
                sh = box = s.shapes.add_textbox(
                    Inches(a["x"]), Inches(top),
                    Inches(ww if ww is not None else W_IN),
                    Inches(_in(a["pt"]) * lead * n + 0.02))
                tf = box.text_frame
                tf.word_wrap = ww is not None
                tf.margin_left = tf.margin_right = 0
                tf.margin_top = tf.margin_bottom = 0
                p = tf.paragraphs[0]
                p.line_spacing = Pt(a["pt"] * lead) if blk is not None else 1.0
                for text, b, i, m in runs:
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
                sh = shape = s.shapes.add_table(
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
                        # run sequence and PowerPoint re-wraps to the same width --
                        # from `flat`, the UNWRAPPED runs, not by re-joining the
                        # wrapped lines, which drops the space at every break
                        for t, bo, it, mo in row["flat"][ci]:
                            r = tp.add_run()
                            r.text = t
                            r.font.name = MONO if mo else SANS
                            r.font.size = Pt(TABLE_PT - (1 if mo else 0))
                            r.font.bold = bool(bo)
                            r.font.italic = bool(it)
                            r.font.color.rgb = _rgb(INK)
            if sh is not None and a.get("step"):
                steps.setdefault(a["step"], []).append(sh.shape_id)

        # **Every spid is asserted against a shape that was actually written.** A
        # `p:timing` naming a shape that is not there does not degrade -- PowerPoint
        # refuses the file -- and there is no PowerPoint here to find that out on.
        if animate and steps:
            live = {sp.shape_id for sp in s.shapes}
            clicks = [[i for i in steps[k] if i in live]
                      for k in sorted(steps)]
            clicks = [c for c in clicks if c]
            if clicks:
                s._element.append(_timing(clicks))

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
    animate = "--no-animation" not in argv

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
            emit_pptx(deck, out, animate=animate)
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
        rev = [l.reveals() for l in deck.slides if l.reveals()]
        if rev and animate:
            print(f"    progressive disclosure: {len(rev)} of {len(deck.slides)} "
                  f"slides build in {sum(rev)} clicks, grouped by idea "
                  f"(median {sorted(rev)[len(rev)//2]} a slide, most {max(rev)})")

        side = [l for l in deck.slides if l.kind == "side"]
        if side:
            print(f"    {len(side)} slides put the text beside the drawing "
                  f"(`#layout: side`) — what that costs each one:")
            for l in side:
                for src, pw, frac in l.reads_at():
                    print(f"      {frac*100:3.0f}%  {pw:4.1f}in  "
                          f"{os.path.basename(src)[:34]:<36} {l.slide.title[:30]}")

        # `#layout: figure` and `#layout: split` are overrides too, and an override
        # nobody can see is one nobody re-examines. The `side` block above says what
        # its slides cost; these two say only that they were forced, because a forced
        # stack costs the drawing nothing in width -- only the height the text takes.
        forced = [l for l in deck.slides
                  if l.slide is not None                # section and divider cards
                  and l.slide.layout in ("figure", "split") and l.kind != "content"]
        if forced:
            print(f"    {len(forced)} slides take their arrangement from `#layout:` "
                  f"rather than the body-height threshold:")
            for l in forced:
                print(f"      {l.slide.layout:<7} {l.slide.section[:22]:<24} "
                      f"{l.slide.title[:40]}")

        # **Name every `+ layers` picture and what it costs in clicks**, for the same
        # reason `#layout:` is named: the arrangement came from a flag in the outline
        # rather than from the builder's own rules, so the report has to say so or the
        # click total is unaccountable.
        layered = [(l, src, n) for l in deck.slides
                   for src, n in getattr(l, "layered", [])]
        if layered:
            print(f"    {len(layered)} figure(s) are disclosed a layer at a time "
                  f"(`+ layers`), adding {sum(n for _l, _s, n in layered)} clicks:")
            for l, src, n in layered:
                print(f"      {n} layers  {os.path.basename(src):<34} "
                      f"{(l.slide.title if l.slide else '')[:34]}")

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
