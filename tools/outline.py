#!/usr/bin/env python3
"""Parse `outlines/DayOne.md` / `DayTwo.md` into the structure the deck builder needs.

    python3 tools/outline.py                  # both days, a structural summary
    python3 tools/outline.py outlines/DayOne.md --slide "Slide: Robust — Guaranteed Delivery"

**Why this is its own module.** The outlines are the single build input for Phase 3 and
they are also read by `lint_figures`-style checks, the timing model and the image
audits. Parsing them in three places is how the three drift apart, so the grammar
lives here once and `build_deck.py` consumes the result.

**The grammar, which is a house dialect of Markdown and not CommonMark.** Plan §1
documents it; this is the implementation.

    # Title                  the deck title, once
    ## Section               a teaching section
    #group: <title>          a run of slides inside a section -- NOT an entry, not counted
    #reveal: bullets         one click PER BULLET on this entry, overriding R0-4's rule
                             that a bullet run is one idea. Opt-in, like `#layout:`
    #divider: <one-line>     OPTS THE GROUP ABOVE INTO A DIVIDER SLIDE, and is the
                             line it carries. Must follow a `#group:`. Opt-in on
                             purpose: `DayTwo.md` has six groups and Ian named four
    ### Slide: <name>        an entry. `###` is reserved for slides and nothing else
    *blurb*                  italic line under a `##`, the section's own summary
    - bullet                 body; nested by two-space indent
    1. numbered              body, an ordered list
    | a | b |                a table
    ▎ text                   a CALLOUT -- the line the presenter says aloud
    #image: <alt>  [→ resources/x.png]      a figure, resolved or still pending
    #note: <text>            a build note. **Never reaches the deck.**
    Presenter notes: <text>  speaker notes, and they DO ship -- plan §12
    ```lang ... ```          a code listing
    > quote                  a block quotation

**⚑ Soft wrapping is the thing that catches you out.** The outlines are written to a
~110-column measure, so a bullet, a paragraph, a callout and a presenter note all
routinely continue on the following line with no marker at all. A parser that treats
every line as its own block produces four-word bullets and loses half the prose. Every
block here therefore accumulates continuation lines until a line that *starts* a new
block, and joins them with a single space.

**`#note:` is stripped and `Presenter notes:` is kept**, which is the asymmetry plan
§12 exists to enforce: presenter notes become the speaker notes of the generated deck,
so anything backward-looking in them ships to whoever delivers the course.
"""

import io
import os
import re
import sys

# A line that ends the block being accumulated. Everything else continues it.
_STARTERS = re.compile(
    r"^(#{1,3} |#image:|#group:|#divider:|#note:|#layout:|#reveal:|Presenter notes:|▎|```|\||>\s|---\s*$|\s*[-*] |\s*\d+\. )")

# **A link may name more than one file.** Five Day 2 markers give the render AND its
# editable source -- `[→ resources/x.png, resources/FBP x.drawio]` -- and one ends in
# the prose "+ related". The FIRST path is the picture; everything after it is
# provenance for whoever edits it.
_IMAGE_LINK = re.compile(r"\[→\s*(resources/[^,\]]+?)\s*(?:,[^\]]*)?\]")
_PENDING = re.compile(r"☐|^#image:\s*NEW")


class Block:
    """One piece of a slide: prose, bullets, callout, table, code, image or quote."""

    def __init__(self, kind, **kw):
        self.kind = kind
        self.__dict__.update(kw)

    def __repr__(self):
        return f"<{self.kind} {str(self.__dict__.get('text', ''))[:40]!r}>"


class Slide:
    def __init__(self, title, section, group=None):
        self.title = title
        self.section = section
        self.group = group
        self.blocks = []
        self.notes = []          # presenter-note paragraphs, in order
        self.layout = None       # `#layout:` -- None means the builder decides
        self.reveal = None       # `#reveal:` -- None means R0-4's inferred grouping

    @property
    def images(self):
        return [b for b in self.blocks if b.kind == "image"]

    @property
    def callouts(self):
        return [b for b in self.blocks if b.kind == "callout"]

    @property
    def body(self):
        """Everything that competes for room on the left-hand column."""
        return [b for b in self.blocks if b.kind != "image"]

    def __repr__(self):
        return f"<Slide {self.title!r} {len(self.blocks)} blocks>"


class Section:
    def __init__(self, name):
        self.name = name
        self.slides = []
        self._pending = []       # every paragraph before the section's first `###`

    @property
    def blurb(self):
        """The section's own summary line.

        **It is the *italic* paragraph, not the first one.** Several sections open
        with a couple of paragraphs of framing before their first slide, so "the first
        thing after the heading" picks up prose and "the last thing" picks up whatever
        happened to end the run -- both were tried and both were wrong on four
        sections. The convention plan §1 records is that the summary is set in
        italics, so that is what this looks for."""
        for b in self._pending:
            t = b.text.strip()
            if t.startswith("*") and t.endswith("*") and not t.startswith("**"):
                return t.strip("*").strip()
        return ""


class Deck:
    def __init__(self, title):
        self.title = title
        self.intro = []          # the lead paragraphs before the first `##`
        self.sections = []
        # **`#group:` sets the kicker; a divider SLIDE is opt-in.** Keyed
        # `(section name, group title)` because a group title is only unique within
        # its section, and the value is the one line the card carries.
        self.dividers = {}

    @property
    def slides(self):
        return [s for sec in self.sections for s in sec.slides]


def _flush(buf, target, kind, **kw):
    """Join a soft-wrapped block and append it. Returns a fresh buffer."""
    if buf:
        text = " ".join(x.strip() for x in buf if x.strip())
        if text:
            target.append(Block(kind, text=text, **kw))
    return []


def parse(path):
    lines = io.open(path, encoding="utf-8").read().split("\n")
    deck = None
    section = None
    slide = None
    group = None

    buf, buf_kind, buf_kw = [], "prose", {}
    in_code, code_lang, code_lines = False, "", []
    in_notes = False
    skip_note = False        # inside a multi-line `#note:` -- see below
    table = None

    def target():
        """Where a finished block goes: a slide, else the section blurb, else intro."""
        if in_notes and slide is not None:
            return slide.notes
        if slide is not None:
            return slide.blocks
        if section is not None:
            return section._pending      # -> becomes the blurb, see close()
        return deck.intro if deck else None

    def close():
        nonlocal buf, table
        t = target()
        if table is not None and t is not None:
            t.append(table)
            table = None
        if t is not None:
            buf = _flush(buf, t, buf_kind, **buf_kw)
        else:
            buf = []
        # The line under a `##` is the section's own summary; `_pending` keeps every
        # paragraph seen before the first `###` and `Section.blurb` picks the right
        # one. It must NOT be resolved here -- `close()` runs on every blank line, so
        # doing it here let the last paragraph overwrite the first.

    for raw in lines:
        line = raw.rstrip()

        # ---- fenced code: verbatim, and nothing inside it is parsed --------------
        if line.startswith("```"):
            if in_code:
                t = target()
                if t is not None:
                    t.append(Block("code", text="\n".join(code_lines), lang=code_lang))
                in_code, code_lines = False, []
            else:
                close()
                in_code = True
                code_lang = line[3:].strip()
            continue
        if in_code:
            code_lines.append(raw)
            continue

        if not line.strip():
            close()
            skip_note = False
            continue

        starts = bool(_STARTERS.match(line))

        # **A `#note:` runs to the blank line, not to the end of its first line.**
        # Skipping only the marker line let every continuation fall through as body
        # prose, so build state shipped INTO the deck -- "wire the specific file
        # references in during Phase 3" was on a slide. That is the exact failure plan
        # §12 and rule 1 exist to prevent, and it was invisible until something tried
        # to render the outlines.
        if skip_note and not starts:
            continue
        skip_note = False

        # ---- structure ----------------------------------------------------------
        if line.startswith("# "):
            close()
            deck = Deck(line[2:].strip())
            section, slide, in_notes = None, None, False
            continue

        if line.startswith("## "):
            close()
            section = Section(line[3:].strip())
            deck.sections.append(section)
            slide, group, in_notes = None, None, False
            continue

        if line.startswith("### "):
            close()
            title = line[4:].strip()
            # every entry is written "Slide: X"; the prefix is scaffolding, not a title
            title = re.sub(r"^Slide:\s*", "", title)
            slide = Slide(title, section.name if section else "", group)
            section.slides.append(slide)
            in_notes = False
            continue

        if line.startswith("#group:"):
            close()
            group = line[len("#group:"):].strip()
            in_notes = False
            continue

        # **A group divider is opt-in, and this line is what opts it in.** Four of
        # `DayTwo.md`'s six groups get one (Ian, 2026-09-12); the two *Worked Flows*
        # groups do not, so generating a card for every group would be wrong. The
        # text is the card's own line -- the movement in one sentence -- and it is
        # NOT provenance, so rule 2 still holds.
        if line.startswith("#divider:"):
            close()
            text = line[len("#divider:"):].strip()
            if group is None:
                sys.stderr.write(
                    f"  ! #divider: with no #group: above it, ignored: {text[:50]!r}\n")
            else:
                deck.dividers[(section.name if section else "", group)] = text
            in_notes = False
            continue

        # **`#layout:` overrides the builder's choice of arrangement for ONE entry.**
        # The default is `styles.md`'s, and the default is right: a labelled drawing at
        # full content width reads at ~97% of the size Phase 2 measured it at, and half
        # a slide costs it about half of that. `side` says the argument and the picture
        # have to be looked at together anyway, so the entry is worth the trade. It is
        # a build directive like `#image:` and never reaches the deck.
        if line.startswith("#layout:"):
            close()
            in_notes = False
            want = line[len("#layout:"):].strip().lower()
            if want not in ("side", "figure", "split"):
                print(f"  ! {path}: unknown #layout: {want!r} — ignored", file=sys.stderr)
            elif slide is not None:
                slide.layout = want
            continue

        # **`#reveal:` overrides the builder's INFERRED reveal grouping for one entry.**
        # R0-4's rule -- Ian's, 2026-09-10 -- is that a run of bullets with no lead-in
        # is one idea and so one click, which is right nearly everywhere: five bullets
        # elaborating one point should not cost five clicks. It is wrong where the
        # bullets ARE the ideas, and the case that found it is R4-3, where Ian asked for
        # Day 2's four movements "as bullet points (progressively disclosed)".
        #
        # Opt-in per entry, exactly like `#layout:`, and for the same reason: the
        # default stays inferred, so this is not the outline annotating 286 slides.
        if line.startswith("#reveal:"):
            close()
            in_notes = False
            want = line[len("#reveal:"):].strip().lower()
            if want != "bullets":
                print(f"  ! {path}: unknown #reveal: {want!r} — ignored", file=sys.stderr)
            elif slide is not None:
                slide.reveal = want
            continue

        if line.startswith("#note:"):
            # build state, never the deck. Plan §12.
            close()
            in_notes = False
            skip_note = True
            continue

        if line.startswith("#image:"):
            close()
            in_notes = False
            rest = line[len("#image:"):].strip()
            m = _IMAGE_LINK.search(rest)
            alt = _IMAGE_LINK.sub("", rest).strip()
            if slide is not None:
                src = m.group(1).strip() if m else None
                if src:
                    src = re.sub(r"\s*\+\s*related$", "", src).strip()
                slide.blocks.append(Block(
                    "image", text=alt, src=src,
                    pending=bool(_PENDING.search(rest))))
            continue

        if line.startswith("Presenter notes:"):
            close()
            in_notes = True
            buf, buf_kind, buf_kw = [line[len("Presenter notes:"):].strip()], "prose", {}
            continue

        if line.startswith("---"):
            close()
            in_notes = False
            continue

        if line.startswith("▎"):
            close()
            buf, buf_kind, buf_kw = [line[1:].strip()], "callout", {}
            continue

        # ---- tables: accumulated whole, so a row is never a paragraph -----------
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if table is None:
                close()
                table = Block("table", rows=[], head=None)
            if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
                table.head = table.rows.pop() if table.rows else None
            else:
                table.rows.append(cells)
            continue
        if table is not None:
            t = target()
            if t is not None:
                t.append(table)
            table = None

        if line.startswith("> "):
            close()
            buf, buf_kind, buf_kw = [line[2:].strip()], "quote", {}
            continue

        m = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", line)
        if m:
            close()
            indent, marker, text = m.group(1), m.group(2), m.group(3)
            buf, buf_kind = [text], "bullet"
            buf_kw = {"level": len(indent) // 2,
                      "ordered": marker not in ("-", "*")}
            continue

        # ---- a plain line: either a new paragraph or the rest of the last block --
        if starts:
            close()
        if buf:
            buf.append(line)                     # soft-wrapped continuation
        else:
            buf, buf_kind, buf_kw = [line], "prose", {}

    close()
    if in_code and code_lines:
        print(f"  ! {path}: unterminated code fence", file=sys.stderr)
    return deck


# ---- inline markup -----------------------------------------------------------

_INLINE = re.compile(r"(\*\*.+?\*\*|\*[^*]+?\*|`[^`]+?`)", re.S)


def runs(text):
    """Split a line into (text, bold, italic, mono) runs.

    PowerPoint has no Markdown, so the emphasis has to survive as run properties or
    it is lost -- and the outlines lean on **bold** hard: it is how a bullet says
    which three words are the point. `code` becomes Plex Mono, which is the same
    decision `styles.md` makes for listings."""
    out = []
    for part in _INLINE.split(text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            # **Recurse, because `**bold with *emphasis* inside**` is a thing people
            # write and the flat version printed the asterisks on the slide.**
            # `_INLINE`'s `\*\*.+?\*\*` alternative matches first and swallows the
            # inner pair, so "Do you need the answer *now*?" went up on d1-109
            # exactly like that. bold+italic is representable -- the run tuple
            # carries both flags and `emit_pptx` sets both -- so the fix is to
            # re-parse the inside and OR the bold on.
            for t, _b, i, m in runs(part[2:-2]):
                out.append((t, True, i, m))
        elif part.startswith("`") and part.endswith("`") and len(part) > 2:
            out.append((part[1:-1], False, False, True))
        elif (part.startswith("*") and part.endswith("*") and len(part) > 2
              and not part.startswith("**")):
            out.append((part[1:-1], False, True, False))
        else:
            out.append((part, False, False, False))
    return out


def plain(text):
    """The text with its markup removed -- what a width measurement should see."""
    return "".join(r[0] for r in runs(text))


def main(argv):
    want = None
    if "--slide" in argv:
        i = argv.index("--slide")
        want = argv[i + 1] if i + 1 < len(argv) else None
        argv = argv[:i] + argv[i + 2:]
    paths = [a for a in argv if not a.startswith("--")] or \
        ["outlines/DayOne.md", "outlines/DayTwo.md"]
    for p in paths:
        deck = parse(p)
        print(f"\n=== {deck.title}  ({p})")
        print(f"    {len(deck.sections)} sections, {len(deck.slides)} slides, "
              f"{sum(len(s.images) for s in deck.slides)} images, "
              f"{sum(len(s.callouts) for s in deck.slides)} callouts")
        for sec in deck.sections:
            if want:
                continue
            kinds = {}
            for s in sec.slides:
                for b in s.blocks:
                    kinds[b.kind] = kinds.get(b.kind, 0) + 1
            body = "  ".join(f"{k} {v}" for k, v in sorted(kinds.items()))
            print(f"  {sec.name:<42} {len(sec.slides):>3} slides   {body}")
        if want:
            for s in deck.slides:
                if want.lower() in s.title.lower():
                    print(f"\n  --- {s.title}   [{s.section}"
                          + (f" / {s.group}" if s.group else "") + "]")
                    for b in s.blocks:
                        if b.kind == "table":
                            print(f"      table head={b.head} rows={len(b.rows)}")
                        else:
                            print(f"      {b.kind:8} {plain(getattr(b, 'text', ''))[:96]}")
                    for n in s.notes:
                        print(f"      NOTE     {plain(n.text)[:96]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
