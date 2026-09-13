#!/usr/bin/env python3
"""Build an artwork review sheet -- the page Ian reviews figures on.

**Ian cannot see a PNG in a terminal, and he reviews by looking.** Every finding on
this work so far arrived through one of these pages, so a batch of artwork is not
reviewed until one has been up.

Seven sheets were built before this file existed, each one written into a scratchpad
and lost with its session (`BACKLOG.md` A3). What a sheet has to do has been stable
across all seven, so it lives here now:

1. **Every image is inlined as a base64 data URI.** The artifact CSP blocks local
   files and external images, and a linked image is simply *not there*, with no
   visible error and nothing in the console a reader would see.
2. **The page is set in `styles.md`'s palette and faces**, so the red on the page is
   the red in the figures. A sheet in some other red is asking about a colour it is
   not showing.
3. **Every claim carries an address** -- `A1`, `A1.2`. Ian reads line by line and
   pushes back by line number; both rulings on sheet 7 came back by address.
4. **The plates stay light in both themes.** A slide is paper. A slide shown on a
   dark ground is not the artefact being reviewed, so the plate pins its own
   background against `prefers-color-scheme: dark` *and* `[data-theme="dark"]`.
5. **The sheet says what is being asked.** A sheet that shows work without naming the
   decision gets looked at and not answered.

Usage:

    python3 tools/review_sheet.py <spec.json> -o <out.html>

The spec is JSON, and the shapes are:

    {
      "title":    "Short Stable Name",        # the <title>, and the artifact's name
      "kicker":   "PRACTICAL MESSAGING",
      "standfirst": "one paragraph: what the batch is",
      "asks":     ["the decision, stated as a question", ...],
      "sections": [
        {"id": "A", "title": "...", "blurb": "...",
         "items": [
            {"title": "...",
             "plates":  [{"src": "path.png", "caption": "..."}, ...],
             "argues":  "what the figure argues, one line",
             "red":     "its one idea in red",
             "rows":    [["label", "value"], ...],       # numbers, optional
             "question":"stated as a question",          # optional, renders in annotation
             "verdict": {"state": "kept|reverted|open", "text": "..."}   # optional
            }, ...]}
      ]
    }

Addresses are generated, not written: item *n* of section `A` is `A1`, and its plates
are `A1.1`, `A1.2`. Add `"verdict"` after a ruling comes back and republish the same
artifact, so the page records what was decided rather than what was asked.
"""

import base64
import json
import mimetypes
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# styles.md, and it is the authority. Where this disagrees with the deck, the deck is
# what Ian is looking at -- fix this file.
PALETTE = {
    "ink": "#181B1F",
    "paper": "#FDFCFA",
    "carbon": "#1D4E6B",
    "annotation": "#C0453B",
    "manila": "#F3EFE6",
    "rule": "#E0D9C8",
    "muted": "#8A8578",
    "comment": "#2F5D3A",
}


def data_uri(path):
    """Inline a file as a base64 data URI. Requirement 1, and the one that has
    silently emptied a sheet when it was skipped."""
    full = path if os.path.isabs(path) else os.path.join(ROOT, path)
    if not os.path.exists(full):
        raise SystemExit("review_sheet: no such image: %s" % full)
    mime = mimetypes.guess_type(full)[0] or "image/png"
    with open(full, "rb") as fh:
        return "data:%s;base64,%s" % (mime, base64.b64encode(fh.read()).decode("ascii"))


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def plain(s):
    """Strip the inline markers, for an `alt` attribute -- a screen reader should not
    be read the asterisks."""
    return esc(str(s).replace("**", "").replace("*", "").replace("`", ""))


def rich(s):
    """`code`, **bold** and *italic*, in that order, on already-escaped text."""
    out, i = [], 0
    s = esc(s)
    for mark, tag in (("`", "code"), ("**", "strong"), ("*", "em")):
        parts, s2, open_ = s.split(mark), [], False
        for n, part in enumerate(parts):
            if n:
                s2.append("<%s%s>" % ("" if not open_ else "/", tag))
                open_ = not open_
            s2.append(part)
        if open_:                       # an odd delimiter count: leave it alone
            s = mark.join(parts)
        else:
            s = "".join(s2)
    del out, i
    return s


CSS = """
:root {
  --ink:%(ink)s; --paper:%(paper)s; --carbon:%(carbon)s; --annotation:%(annotation)s;
  --manila:%(manila)s; --rule:%(rule)s; --muted:%(muted)s; --comment:%(comment)s;
  --ground:#F7F5F0; --panel:%(paper)s; --hair:%(rule)s; --body:%(ink)s;
  --dim:#5C5F63;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --ground:#14171A; --panel:#1B1F23; --hair:#33383D; --body:#E8E4DC;
    --dim:#9BA1A7; --carbon:#7FB3D0; --annotation:#E0776C; --comment:#7FAE8B;
    --muted:#8A8578; --manila:#26292D;
  }
}
:root[data-theme="dark"] {
  --ground:#14171A; --panel:#1B1F23; --hair:#33383D; --body:#E8E4DC;
  --dim:#9BA1A7; --carbon:#7FB3D0; --annotation:#E0776C; --comment:#7FAE8B;
  --muted:#8A8578; --manila:#26292D;
}

* { box-sizing:border-box; }
body {
  margin:0; background:var(--ground); color:var(--body);
  font-family:"IBM Plex Sans","Helvetica Neue",Arial,sans-serif;
  font-size:16px; line-height:1.55;
}
.wrap { max-width:1180px; margin:0 auto; padding:48px 28px 96px; }

.kicker {
  font-family:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
  font-size:12px; letter-spacing:.18em; text-transform:uppercase;
  color:var(--carbon); margin:0 0 10px;
}
h1 {
  font-family:"IBM Plex Serif",Georgia,"Times New Roman",serif; font-weight:600;
  font-size:clamp(30px,4.2vw,44px); line-height:1.12; margin:0 0 18px;
  text-wrap:balance; color:var(--body);
}
.standfirst { max-width:66ch; font-size:17px; margin:0 0 26px; color:var(--body); }

.asks {
  border-left:4px solid var(--annotation); padding:2px 0 2px 18px;
  margin:0 0 44px; display:flex; flex-direction:column; gap:10px;
}
.asks p {
  margin:0; font-family:"Caveat","Bradley Hand",cursive; font-size:25px;
  line-height:1.3; color:var(--annotation);
}

h2 {
  font-family:"IBM Plex Serif",Georgia,serif; font-weight:600; font-size:25px;
  margin:56px 0 6px; color:var(--body); text-wrap:balance;
}
h2 .sec {
  font-family:"IBM Plex Mono",ui-monospace,monospace; font-size:15px;
  color:var(--carbon); margin-right:12px; letter-spacing:.06em;
}
.blurb { max-width:66ch; color:var(--dim); margin:0 0 8px; }

.item { border-top:1px solid var(--hair); padding:26px 0 4px; }
.item-head { display:flex; align-items:baseline; gap:12px; flex-wrap:wrap; }
.addr {
  font-family:"IBM Plex Mono",ui-monospace,monospace; font-size:13px;
  color:var(--carbon); letter-spacing:.06em; font-weight:600;
}
h3 {
  font-family:"IBM Plex Serif",Georgia,serif; font-weight:600; font-size:20px;
  margin:0; color:var(--body);
}
.argues { max-width:66ch; margin:8px 0 0; }
.red {
  font-family:"Caveat","Bradley Hand",cursive; font-size:23px; line-height:1.3;
  color:var(--annotation); margin:10px 0 0;
}

.plates { display:flex; flex-direction:column; gap:18px; margin:20px 0 0; }
figure { margin:0; }
/* Requirement 4: a slide is paper, in either theme. */
.plate {
  background:%(paper)s; border:1px solid var(--hair); border-radius:2px;
  padding:0; overflow:hidden; line-height:0;
}
.plate img { width:100%%; height:auto; display:block; }
figcaption {
  font-family:"IBM Plex Mono",ui-monospace,monospace; font-size:12px;
  letter-spacing:.04em; color:var(--dim); margin-top:7px; line-height:1.5;
}
figcaption .pa { color:var(--carbon); font-weight:600; margin-right:8px; }

.rows { margin:16px 0 0; border-collapse:collapse; font-size:15px; }
.rows td { padding:4px 20px 4px 0; vertical-align:top; }
.rows td:first-child { color:var(--dim); white-space:nowrap; }
.rows td:last-child { font-variant-numeric:tabular-nums; }

.q {
  margin:18px 0 0; padding:12px 16px; border:1px dashed var(--annotation);
  border-radius:2px; color:var(--annotation); max-width:70ch;
}
.q .addr { color:var(--annotation); margin-right:10px; }

.verdict { margin:16px 0 0; padding:10px 14px; border-radius:2px; max-width:70ch;
  border-left:4px solid var(--comment); background:var(--manila); }
.verdict.reverted { border-left-color:var(--annotation); }
.verdict.open { border-left-color:var(--muted); }
.verdict .state {
  font-family:"IBM Plex Mono",ui-monospace,monospace; font-size:12px;
  letter-spacing:.1em; text-transform:uppercase; color:var(--comment);
  margin-right:10px;
}
.verdict.reverted .state { color:var(--annotation); }
.verdict.open .state { color:var(--muted); }

code { font-family:"IBM Plex Mono",ui-monospace,monospace; font-size:.92em; }
footer {
  margin-top:70px; padding-top:16px; border-top:1px solid var(--hair);
  font-family:"IBM Plex Mono",ui-monospace,monospace; font-size:12px;
  color:var(--dim); letter-spacing:.03em;
}
@media (prefers-reduced-motion:reduce) { * { animation:none !important; transition:none !important; } }
""" % PALETTE


def build(spec):
    out = []
    a = out.append
    a('<title>%s</title>' % esc(spec["title"]))
    a('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
      'family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;600&'
      'family=IBM+Plex+Serif:wght@600&family=Caveat:wght@400;600&display=swap">')
    a('<style>%s</style>' % CSS)
    a('<div class="wrap">')
    a('<p class="kicker">%s</p>' % esc(spec.get("kicker", "PRACTICAL MESSAGING")))
    a('<h1>%s</h1>' % esc(spec["title"]))
    a('<p class="standfirst">%s</p>' % rich(spec["standfirst"]))
    if spec.get("asks"):
        a('<div class="asks">')
        for q in spec["asks"]:
            a('<p>%s</p>' % rich(q))
        a('</div>')

    for sec in spec["sections"]:
        sid = sec["id"]
        a('<h2><span class="sec">%s</span>%s</h2>' % (esc(sid), esc(sec["title"])))
        if sec.get("blurb"):
            a('<p class="blurb">%s</p>' % rich(sec["blurb"]))
        for n, item in enumerate(sec["items"], 1):
            addr = "%s%d" % (sid, n)
            a('<div class="item">')
            a('<div class="item-head"><span class="addr">%s</span><h3>%s</h3></div>'
              % (esc(addr), esc(item["title"])))
            if item.get("argues"):
                a('<p class="argues">%s</p>' % rich(item["argues"]))
            if item.get("red"):
                a('<p class="red">%s</p>' % rich(item["red"]))
            if item.get("plates"):
                a('<div class="plates">')
                for m, plate in enumerate(item["plates"], 1):
                    paddr = "%s.%d" % (addr, m)
                    a('<figure>')
                    a('<div class="plate"><img alt="%s" src="%s"></div>'
                      % (plain(plate.get("caption", item["title"])), data_uri(plate["src"])))
                    a('<figcaption><span class="pa">%s</span>%s</figcaption>'
                      % (esc(paddr), rich(plate.get("caption", ""))))
                    a('</figure>')
                a('</div>')
            if item.get("rows"):
                a('<table class="rows">')
                for label, value in item["rows"]:
                    a('<tr><td>%s</td><td>%s</td></tr>' % (rich(label), rich(value)))
                a('</table>')
            if item.get("question"):
                a('<p class="q"><span class="addr">%s?</span>%s</p>'
                  % (esc(addr), rich(item["question"])))
            if item.get("verdict"):
                v = item["verdict"]
                a('<p class="verdict %s"><span class="state">%s</span>%s</p>'
                  % (esc(v.get("state", "open")), esc(v.get("state", "open")),
                     rich(v.get("text", ""))))
            a('</div>')

    a('<footer>%s</footer>' % rich(spec.get("footer", "")))
    a('</div>')
    return "\n".join(out) + "\n"


def main(argv):
    if len(argv) < 2:
        raise SystemExit(__doc__)
    spec_path = argv[1]
    out_path = None
    if "-o" in argv:
        out_path = argv[argv.index("-o") + 1]
    with open(spec_path, encoding="utf-8") as fh:
        spec = json.load(fh)
    html = build(spec)
    if out_path:
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(html)
        kb = len(html.encode("utf-8")) / 1024.0
        print("  %s  %.0f KB" % (out_path, kb))
        if kb > 15000:
            print("  ! over the 16MB artifact ceiling -- shrink or drop a plate",
                  file=sys.stderr)
    else:
        sys.stdout.write(html)


if __name__ == "__main__":
    main(sys.argv)
