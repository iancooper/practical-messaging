# Backlog — what is outstanding #

**An index, not a source of truth.** Every line points at where the real detail lives.
`REDEVELOPMENT-PLAN.md` is the source of truth for the decks; **`code-rewrites.md` is a separate
workstream with its own brief**. If this file and the plan disagree, **the plan wins and this file
is stale**. Kept as a table on purpose — counts in prose go stale silently,
and a table you can read the length of does not.

Last reconciled against the repo: **2026-09-10**, after C4. **§C's two handouts are both built**, so
**nothing is left in §B or §C.** B7 closed as a clean negative, C3 and C4 are built.
**§G is the full-deck visual sweep — eleven findings.** G2, G3, G4, G6, G7, G8 and G10 are fixed; G9 was withdrawn on inspection; **G1 (the register, 30 slides) and G11 (the preview drops italic) are open.** B2 and B3 have no
action available. **§H holds Ian's two passes over the built decks** — 2026-09-10 (26 findings) and **2026-09-12 (16 more, §R3 — **Day 1 closed**)**; both worked, and the list is `REVIEW.md`. **§R3 opened G12; G13 was closed by Ian's ruling that the `side` slides' figure size is fine.**

**Where things stand.** Phases 1 and 2 are closed, and **Phase 3 has nothing actionable left**: §A, §B
and §C are all closed but for B2 and B3, which have no action available. What remains is §F — Ian's.
Both decks build clean from `outlines/` with an empty overflow report, Day 1 **138 slides** and Day 2
**153**; **99 figures** across twelve families plus **2 print cards** — 90 on slides, **9 in the two
handouts** — lint clean, `reads_at` **30 of 99**, and speaker notes ship into both `.pptx`. **Day 1's
figures sit at a median 91% of their Phase 2 label size with two under 85%, Day 2 at 96% with three.**
**The takeaway pack is complete**: `handouts/Routing-Patterns.md` and
`handouts/Managing-Asynchronous-APIs.md`, both signposted from the deck, both printable today. What is
left is below.

---

## A. ✅ Closed — the repo is operable ##

**Ian, 2026-09-09:** *"We are building tools to allow us to regenerate the decks from outlines, draw
diagrams etc. We may want to return later, update outlines, rebuild. That seems like we need a
CLAUDE.md file, some commands that we can use to trigger operations and some skills that they
invoke. I think we should build it as the next step, after a fresh session starts."*

**Done.** The operating knowledge is now **tracked**, and split three ways: `CLAUDE.md` is what is
true whether or not anything is invoked, a command is a verb you type, and a skill is the procedure
it loads. `PROMPT.md` stays what it always was — session state, untracked — but nothing load-bearing
lives only there any more.

| # | item | state |
|---|---|---|
| **A1** | `CLAUDE.md` | ✅ Tracked at the repo root. Read order, the pipeline, the tool inventory, the two registers and the palette, 14 rules that each cost real rework, and the working notes for this machine |
| **A2** | Slash commands | ✅ `.claude/commands/` — `/verify` (one pass, slow checks backgrounded) · `/build` · `/preview` (renders **and looks**) · `/figure` (rebuild, lint, `reads_at`, **and show the PNG**) · `/sheet` (offered, never published unasked) |
| **A3** | Skills | ✅ `.claude/skills/` — `deck-build` (the grammar, the builder, answering an overflow) · `figure-drawing` (the API, the legibility arithmetic, the composition test, what lint cannot see) · `review-sheet` (the five requirements, the etiquette, the seven sheets) |

**One thread stays open**, and it is recorded in the `review-sheet` skill rather than here: there is
still **no committed generator** for a review sheet. Each one has been written into a scratchpad and
died with the session. The next one written should go in `tools/` and be committed.

---

## B. Deck and artwork ##

| # | item | why it is not done | size | detail |
|---|---|---|---|---|
| **B1** | ✅ Reshape `boundary-what-crosses` | **Done 2026-09-09.** Application beside store, mirrored through the line: 1.57 : 1 becomes 2.60 : 1 and **82% becomes 96%**, the stage's own width and the cap. Nothing cut — three bullets, both refusals, both crosses. The trade is that §1's boundary rule now reads shorter than §3's | — | plan §8 item 23e, *One figure was at 82%* |
| **B2** | The other five figures under 85% | **No action available.** While a figure's canvas and its stage are both height-fitted, the percentage reduces to `stage_height × 2.2 / 12.4` and the aspect cancels out: nothing improves until the drawing is wider than ~2.57 : 1. Only a content change moves them | — | plan §8 item 23e. **The builder names them by file every run**, so there is no list to keep |
| **B3** | 30 of 90 figures under the 18pt floor | **18 are Ian's standing decision** — `bpmn_hotel`, `bpmn_shopping`, `paper_flow`; he scoped the re-sweep away from them. The other 12 are **clamp-bound**: a shape may not shrink below its own label, so the only lever is content, per figure | — | `python3 tools/reads_at.py --all`; F-items below for the standing decision |
| **B4** | ✅ Day 1 image-dump sweep | **Done 2026-09-09, and it is a clean negative.** Day 1 carries 49 images across 91 entries and **no entry holds more than one** — the defect Day 2's *Paper Workflow Illustrations* had cannot exist here. Day 2 still has 18 multi-image entries, all of them ruled on in plan §8 item 23e | — | plan §8 item 23e |
| **B5** | ✅ The load-bearing-line sweep, Day 1 §4 | **Done 2026-09-09.** Six candidates across §4.1–§4.4; §4.5 carries no presenter notes at all, so nothing can hide there. **Four promoted** — *Channels*, *Translate and Dispatch*, *Competing Consumers*, *Invalid Message Channel*. **Two were false positives the figures already answered**, and only rendering the slides showed it | — | plan §8 item 24 |
| **B6** | ✅ Stale cross-references, re-run | **Done 2026-09-09**, after B5. Four wrong: two on Day 1 (*the next slide is the bill*, which pointed at the wrong slide; *the last slide of this sub-section*, which the exercise slot displaced) and two on Day 2 (a count of five that is now seven, and *the next two slides* that are the second and third). All four now **name the slide** rather than count from it. **Re-run this after any structural change** | — | plan §8 item 24 |
| **B8** | ✅ Day 1's exercise slots | **Done 2026-09-09.** Ian ruled three slots; the RMQ pointer moved off §4.2 to close §4.3, and *Exercise Material — Failing Well* now closes §4.4. Day 1 is 91 entries, **137 slides** | — | `code-rewrites.md` §3.2 |
| **B7** | ✅ `(sNN)` markers vs the 2025 decks | **Done 2026-09-10, and the premise of this row was wrong.** The markers were never 2024-derived: `session-work/day1.txt` and `day2.txt` are byte-identical to a fresh extraction of the **2025** decks, and **all 215 images in `session-work/imgs/` hash to the 2025 decks at their own slide key and to the 2024 decks at none** — which is what plan §1 said all along. So there is nothing to diff *against*; the markers already refer to the newest decks. The two years do differ, and materially — Day 1 **139 → 138** slides with 131 slides' text changed, Day 2 **187 → 182** with 81 — so the old claim that Day 2 held *the same 112 images byte for byte* across years is false (2024 has 123 images, 25 of them found in no 2025 slide). **All 25 markers resolve:** Day 1's 15 land on slides whose titles match the marker text word for word, Day 2's 10 on picture slides with matching picture counts, and `s170`/`s171` are byte-identical to the resource they link | — | this row is the whole record |

---

## C. Handouts — ✅ both built ##

Both were **cut content that had been promised a home**, so neither was optional: a deck that says
"this is in your pack" and ships no pack is worse than one that never said it. **`handouts/` is a new
tracked directory** — Markdown, on `exercises/Paper-Flow-Delegate-Brief.md`'s precedent — and both
build to A4 with `pandoc X.md -o X.pdf --pdf-engine=weasyprint` **run from `handouts/`**.

| # | item | state | size | detail |
|---|---|---|---|---|
| **C1** | ✅ *Managing Asynchronous APIs* | **Done 2026-09-10.** `handouts/Managing-Asynchronous-APIs.md` — ~4,400 words from the QCon London 2026 deck, with the one-page index that turns a 40-minute narrative into a reference. **Its signpost already existed and already promised it**, so nothing was added to the deck. **⚑ Plan §6's "held back from the handout — still taught" note was stale and load-bearing:** D2-10 removed `## Versioning` from `DayTwo.md`, so Postel's Law, the Tolerant Reader and additive-vs-breaking were *handed to* the handout, not withheld from it — and the QCon source does not contain the tolerant-reader argument, so it was written here | — | plan §6 |
| **C2** | ✅ The routing-patterns handout | **Done 2026-09-09.** `handouts/Routing-Patterns.md` — ~2,250 words from `script/Patterns/*.md`, eight new figures (`eip_figures.py` 13 → 21), a one-page index, and a signpost on Day 2's *Further Reading — EIP* slide. **Ian ruled both open decisions:** redraw rather than cite Hohpe & Woolf, and signpost from Day 2's `## Next Steps` rather than Day 1 §4.5. The three routers contrast through red on *who holds the routing decision*, which is the handout's own finding | — | plan §10 |
| **C3** | ✅ A house stylesheet for the handouts | **Done 2026-09-10.** `handouts/print.css` — one sheet for the whole pack — plus `print.html` (a minimal pandoc template, because pandoc's stock one ships a `body { max-width: 36em }` that fights every print rule) and `handouts/build.sh`. `styles.md` at document sizes: **11pt on a 154mm measure**, Plex Serif headings in ink and carbon, the palette verbatim, asides as `comment` on `manila`. **Four defects the Markdown could not show, all found by looking at the PDF:** pandoc's `<colgroup>` gave a quarter of the page to a row number; `break-inside: avoid` on a long table left half a page blank; implicit_figures captioned every figure with the heading directly above it; and **WeasyPrint does not synthesise an oblique**, so every `*emphasis*` in both handouts was rendering upright — the three italic faces are vendored now, and the eleven families rebuilt byte-identical after. The PDFs are gitignored, like `build/` | — | this row is the whole record |
| **C4** | ✅ Does C1 want a figure? | **Done 2026-09-10. Yes, one.** `resources/asyncapi-virtuous-cycle.png` from a new twelfth family, `tools/asyncapi_figures.py` — `eip_figures.py` is the twenty-one Hohpe & Woolf replacements and a virtuous cycle is neither a pattern of theirs nor a slide of ours. It replaces the ASCII staircase; **red is the return, not the spec**, because the section's sting is its last paragraph. **⚑ Drawn twice.** A handout figure is fitted to a 154mm text block, so its **printed letter size is `154 / w`** and `reads_at` — which measures against a projector — passes it either way: the first draft was 852 wide and printed at ~9pt against the routing figures' ~14. Measured advances (*Provisioning* is 72.3 units) put the same content in **560**, at the pack's own size | — | this row is the whole record |

---

## D & E — moved out to `code-rewrites.md` ##

**Ian, 2026-09-09:** *"Let's move D, E out. We can handle the code rewrites separately… I will pick up
with the agent and old code locations. The timings will form part of that."*

| was | now |
|---|---|
| **D.** Day 1 coding-exercise rework | `code-rewrites.md` — a standalone brief for another agent |
| **E.** Timing (T-2 … T-5, and the unmeasured code blocks) | the same file, §5 |

**Why the timing went with it rather than staying here.** The two Day 1 code blocks are **160 minutes
of a 390-minute day, estimated and never measured**. T-2 … T-5, the four parked deck cuts, are worth
about **24 minutes between them**. Whatever the rewrite does to the exercises dominates every
deck-side lever, so the deck cuts stay parked until the exercise duration is known — cutting teaching
to pay for an estimate nobody has checked is the wrong order.

**Nothing in `exercises/` or `videos/` is the deck workstream's to change.** If a rename or a
restructure happens over there, `outlines/DayOne.md` names the exercise decks and videos by title and
will need the matching edit — that comes back here as a request, not as an edit made from that side.

---

## G. The full-deck visual sweep — 2026-09-10, findings not yet ruled on ##

**All 291 slides rendered and reviewed** — 33 nine-up contact sheets, ~25 slides at full size, plus five
mechanical checks run across **every** slide and all 101 figures. Nothing here was visible to
`build_deck.py`'s overflow report, to `lint_figures.py` or to `reads_at.py`; the overflow report is
still empty and lint is still clean. **Rule zero, applied to slides for the first time.**

| # | finding | size | detail |
|---|---|---|---|
| **G1** | **30 slides (10%) carry a 2021 import in a foreign register** — ✅ **scoped**, not started | **L** | Day 1 **5** — §4.4's producer side (`Transactional No Outbox`, `Transactional With Outbox`, `Log Tailing`, `State Change Capture`, `Inbox`), bright blue/orange/green, **sitting in the same sub-section as the redrawn consumer-side figures**. Day 2 **25** — the whole *Worked Flows* run, the FBP worked examples, and **all of *Putting It Together***: black-on-white value streams still stamped *29 SEP 2021*, tiny blue-and-black fax flows, purple-hexagon FBP graphs. **Against the standing instruction in the plan** — Ian: *"Let's redraw both runs. One thing I want to strive for is a consistent look and feel"* — beside which the plan already warns *"their `.png`s are 2021 black-on-white, so linking them keeps the old look."* **Several are illegible at slide size**: d2-137 and d2-140 carry ~4pt annotations, and `paper-worked-flows-montage` (d2-022) tiles four of them onto one slide. **Scoped 2026-09-10 into plan §14, on Ian's ruling *scope it, do not start it*: 19 distinct diagrams, every one with an editable source, ≈5.5 days, and NO new family needed** — four of the five groups use shapes `eip_figures`, `paper_flow` and `flow_reactive` already own. §14 names the order (Day 1's five first — cheapest, worst juxtaposition), the one group that is a better cut than a redraw (the two Lean value-stream maps), the one outlier that needs a decision before a redraw (`flowbased_order_all`, 180 elements), and **two typos the imports are shipping today** |
| **G2** | ✅ **10 slides say the same line twice** — the callout repeats the figure's own red note | — | Two are word for word: **d1-007**, **d1-011**. The other eight are close paraphrases — d1-018, d1-051, d1-103, d2-022, d2-035, d2-039, d2-060, d2-072. In most the **red note is the longer and better line**, so the callout is what should go; **d1-051 is the exception** — its callout carries a §4.4 forward reference the note does not. Dropping a callout also gives the figure back ~13 points. **Fixed 2026-09-10: seven callouts dropped, three reworded down to the part the figure does NOT say** — d1-051 keeps its §4.4 forward reference, d2-060 keeps *"You have just drawn a distributed system"*, and d2-072's *"Again."* became the cross-reference it was gesturing at. Callout counts 36 → 32 and 30 → 27; Day 1's figure median 90% → 91%, which is the ~13 points arriving |
| **G3** | ✅ **3 text-on-text collisions inside figures** | — | `grid-coupling` — *"a command message"* printed across *"a whole entity"*. `flow-bulkhead` — a long comment line runs straight through **both** node captions. **`lint_figures.py` cannot see any of them**: it measures a label against a *shape* and against arrow runs, never against another label. **Fixed 2026-09-10, both in FINAL units** — the only place either could be reasoned about. `grid-coupling`: the two points were 40 raw units apart, comfortable at 1060, but `_frame` compacts to 627 and text does not scale, so 40 raw arrived as **4**; the Stamp point is raised 27 raw, because the Control label's descenders sit **2.6 units** off the mid rule and cannot move down. **Labelling it `above` instead was tried and reverted** — it cleared the collision and then lay across the plot's top rule, lint's *other* blind spot, found only by looking at the PNG again. `flow-bulkhead`: three comment notes share a row, the side ones leaving a 390-unit gap, and the middle one's second line measured **460** — rewrapped to three lines that fit |
| **G4** | ✅ **6 slides whose body is the words "Section marker"** | — | d1-027, d1-080, d1-085, **d2-005**, d2-062, d2-129. Scaffolding that went up on screen — rule 2 in spirit. **d2-005 was the first teaching slide of Day Two.** **Fixed 2026-09-10, Ian ruling on all six wordings.** Four are now a claim rather than an agenda, which is how the rest of the deck opens a sub-section; d2-062 only lost the prefix, its second sentence was already teaching content; and **d2-005 lost the line entirely**, leaving its callout alone on the slide — which is exactly what that slide's own presenter note asks for (*"that question, alone on a slide … the line is the question, not the agenda"*), and it renders |
| **G5** | **Day 1's Closing is a stub** | S | *Further Reading* reads **"Pointers for going deeper."** and lists nothing, where Day 2 closes with four proper reading slides and their covers. The *Closing* divider is also the only one in either deck with no sub-line |
| **G6** | ✅ **d1-025's divider sub-line restates its own title** | — | *"4.1 What Is a Message?"* over *"What is a message?"*. The only one of the 19 dividers that does it. **Fixed 2026-09-10** — the sub-line now names what the section teaches, *"Header and body — and whether you are expressing intent or reporting a fact"*, which is the shape every other section's sub-line uses |
| **G7** | ✅ **d2-148's URL is clipped and runs under the photo panel** | — | `(jonasboner.com/resources/Reactive_Microservices_Architect` — cut mid-word, no closing bracket, unusable. **The builder already guards the kicker against exactly this and warns on stderr; body text had no equivalent guard.** Rule 11. **Fixed 2026-09-10, both halves:** the URL is now prose a delegate can type, and `Type.wrap` warns once per over-wide word — with 0.05in of slack, because a table cell pads beyond its measured column and "Out-Only" sitting 0.02in over renders whole. **⚑ `Type.wrap`'s docstring claimed a long word "shows up in the overflow report" and that was false**: overflow measures HEIGHT, and a word running off the right costs no height |
| **G8** | ✅ **Two dashed-arrow conventions in one deck** | — | The taught notation key (**d2-010**, ours) draws *dashed = paper moving* in **carbon**; the imported 2021 flows draw it in **red**; and the BPMN mapping table on **d2-080** tells the room *"a red dashed arrow between an out-tray and an in-tray"*. Checked: `exercises/Paper-Flow-Delegate-Brief.md` line 35 says only *dashed / solid* and names no colour, so **the brief is not in conflict** — CLAUDE.md rule 13's own example slightly overstates it. **Fixed 2026-09-10:** d2-080's row now reads *"a dashed arrow"*. The column head is *what you drew*, so it describes the delegates' own paper, where the brief names no colour and the pens are whatever is on the table — naming red there was over-specifying, and it contradicted the key the deck taught seventy slides earlier. **The 2021 imports still draw it red; that is G1's to settle, not this row's** |
| **G9** | ⊘ Minor, listed for completeness — **and it does not survive inspection** | — | **Closed with no change 2026-09-10, and the finding was mine to withdraw.** *4 slides carry two callouts* (d1-008, d1-022, d1-101, d2-006) — but **`styles.md`'s "one idea in red" rule is about a FIGURE**, and says nothing about how many callouts a slide may carry. Rendered, each pair is two different ideas: a practical aside and the section's conclusion on d1-008, an epigraph and a claim on d2-006. Changing them would be imposing a rule that is not written down. **d1-030** is a one-line slide, and it is a legitimate lead-in: it names the three message types that d1-031 then defines. Folding it away would remove a slide and reopen a closed timing pass for a marginal gain |

| **G10** | ✅ **Nested emphasis printed its own asterisks on the slide** | — | `**bold with *emphasis* inside**` — `_INLINE`'s `\*\*.+?\*\*` alternative matches first and swallows the inner pair, so the run kept the markup and *"Do you need the answer \*now\*?"* went up on **d1-109** exactly like that. Nine across both outlines: **2 on slide bodies, 7 in speaker notes**. **Fixed 2026-09-10 in the parser, not in the nine lines** — the bold branch now re-parses its contents and ORs the bold on, which the run tuple and `emit_pptx` have always supported. Found while fixing G7, not by the sweep |
| **G11** | **The PNG preview drops italic silently** | S | `emit_pptx` sets `r.font.italic`; the SVG preview path reads only the bold flag and picks a weight, so **every italic in either deck renders roman in a preview**. The whole G-sweep was therefore blind to italics. It also contradicts `CLAUDE.md`'s pipeline claim — the two renderers share a layout precisely so they *cannot* be previews of different decks, and on this one axis they are. **Now fixable**: the italic faces were vendored for the handouts in C3, so it is a `_FONT_FILES` entry plus a family switch in the preview's text path. Not started — it needs rule 5's byte-identical rebuild afterwards |

**What the sweep did NOT find**, which is worth recording: no overflow, no missing image, no broken
cross-reference, no figure family off-style, and no defect at all in `queues_streams`, `conversations`,
`eip_figures`, `bpmn_hotel`, `bpmn_shopping` or `integration_styles`. **The redrawn families are clean.**

---

## H. Ian's first pass over the built decks — 2026-09-10 ##

**The detail is in `REVIEW.md`, and that file is the work list.** Twenty-six findings from reading
the rendered Day 1 deck: five builder changes that land on **both** days, twenty-one Day 1 content
rows, and a narrow Day 2 pass afterwards. Ian: *"That's enough for a first pass at Day One."*

| # | the shape of it | size | state |
|---|---|---|---|
| **H1** | ✅ **§R0 — the builder, all five done.** A folio bottom-left on every slide but the cover; **one text box per block instead of one per line**, which fixed all four reported overflows in one change; progressive disclosure grouped by idea — 230 clicks on Day 1, 221 on Day 2, `--no-animation` to turn it off; and `#layout: side`, a fourth arrangement. **The animation could not be checked here** — no PowerPoint on this machine, and a malformed `p:timing` refuses to open rather than degrading. **Settled 2026-09-12: Ian read four slides out of the built deck, so it opens and the timing part is accepted.** What is still unconfirmed is only how it *behaves* — that a click advances one group, not one shape | M–L | ✅ |
| **H2** | ✅ **§R1 — Day 1 content, all 21 rows.** Day 1 **138 → 136 slides**, four figures added (2 pump, 2 reference-data), §4.1 rebuilt with two tables and both broker models, §4.5 **13 → 6**, §Conversations re-ordered pattern-by-pattern with **Out-In** put back, and the AI-ism sweep run against the 2025 deck as the test of what is Ian's. **Nine cross-references re-anchored** after the restructure, plus four more that were stale before it | L | ✅ |
| **H3** | **§R2 — Day 2, all four rows.** R2-1 (text boxes) and R2-2 (AI-isms) ✅. **R2-3: Ian, 2026-09-10 — do not roll `#layout: side` out to Day 2**, ask per slide when he reviews it. Measured first: 23 eligible entries, median figure **96% → 53%**, **all 23** under 85%, 7 needing text cut to notes, and 8 of them BPMN, the one family already at the type floor. **R2-4: drop *annotated*.** §*Putting It Together* promised a pattern-name layer **none of its ten figures carries**; all ten are used twice, and their `.excalidraw` / `.drawio` sources cannot be rendered here, so annotating means redrawing — **G1's job, not this row's.** Four titles and five alt lines corrected instead | M | ✅ |

**Both of H2's blocking questions were put to Ian on 2026-09-10 and both were answered**: the full §4.5
restructure, and the builder inferring reveal groups rather than a marker in the outline.

**§H's first pass is closed.** Both of its last two rows were ruled on by Ian on 2026-09-10: R2-3 *no
roll-out, ask per slide*, R2-4 *drop `annotated`*. **⚑ R2-4 handed G1 two named jobs** — slides **138
and 141** carry ~4pt annotations (plan §14.3) and **138 and 144 ship typos** (§14.2), and retitling
touched none of it.

**✅ §R3 — his second pass over Day 1, 2026-09-12, sixteen rows, all applied. Ian has closed Day 1:**
*"With that, I suspect we close out the review on Day One."* Day 1 **136 → 129 slides**, and **Day 2 is
next**. Three AI-isms; five entries merged to one slide each on `#layout: side`; the timeout sequence
dropped from *In-Out*; the transitive-dependencies picture redrawn from the 2025 **Day 2** deck, where it
is a native table with leader lines and carries no extracted image. **⚑ Four of the fourteen were one
number** — the callout reserved 1.06em where Caveat's ink extent is 1.260em, so **108 callouts across
both decks** sat 0.067in too close to whatever came next, 73 of them under an opaque picture.
**Invisible in the preview by construction** — it draws the lines itself at the same 1.06. **Verified by Ian in the built deck, 2026-09-12.**

**§R3 measured one thing and put it to Ian, and he ruled on it.** **Every `#layout: side` slide reads
at 8.9–12.8pt in the room against an 18pt floor** — thirteen of them now, because the half-stage is 6.1in
where every figure was measured at 12.4. **Ian, 2026-09-12: *"I think that is fine."*** So the floor
does not apply to a `side` slide, and that exception is now written into `styles.md` and `CLAUDE.md`
rule 7 rather than left to be rediscovered.

| | | | |
|---|---|---|---|
| **G12** | **`reads_at.py` does not know about `#layout: side`** | S | It reports the full-width number for thirteen slides that are not laid out that way — 18.0pt for figures the room gets at 9.5. **Ian's ruling makes this less urgent, not wrong**: the size is agreed, but the legibility check still prints a number nobody should act on, and the next person to run it has no way to tell which thirteen rows are fiction. It should read `#layout:` from the outline, as `side_cost.py` already does |
| **G13** | ~~Re-lay the four `qs-*` figures for the half-stage~~ | — | **✅ Closed 2026-09-12 without work.** It existed only to bring those four back to the 18pt floor, and Ian ruled the current size fine. Reopen only if he changes his mind on a specific slide — `tools/side_cost.py 1 --slide N` is the measurement |

**New tool: `tools/deck_index.py`.** Ian reviews by slide number and the slide number is not the
outline entry number — 91 entries build 138 slides. It runs the real layout and prints the map.

---

## F. On Ian's desk — not ours to do ##

| # | item | state |
|---|---|---|
| **F1** | Export the order-taking photograph | *phone / card machine / order pad*, Day 2 §Flow, *Three different media, one notation*. He offered. **The last class-A marker in either deck**, and the only `#image:` line left anywhere. Checked: it is in neither the 2024 nor the 2025 deck |
| **F2** | `cp tools/fonts/*.ttf ~/Library/Fonts/` | **Live, not future.** The built decks name IBM Plex Serif / Sans / Mono and Caveat, and **PowerPoint substitutes until they are installed** — so the first thing he sees would not be the deck we built. His machine, his call |
| **F3** | Three review sheets awaiting him | **The Artwork Sheet** (56 figures, part-reviewed — two findings came back and were applied, the rest he has not been through), **The Legibility Floor**, **Muted Is For Lines**. Sheet 7 (*Four Composed, Two Printed*) has been reviewed and both its calls answered |
| **F4** | Two unlinked files he dropped in | **Half closed 2026-09-10.** Ian: *"Swap Folder Stack onto The Desk."* Done — `outlines/DayTwo.md:156` now links `resources/Folder Stack.jpg`. **⚑ Worth knowing: the two files are the same photograph.** 463×441 against 464×443, both 150 dpi, corner backgrounds identical at 82% pure white, no watermark on either — so the *cleaner file* note this row used to carry does not survive measurement. The swap stands because he asked for it; nothing was gained or lost by it. `photo-manila-folders.jpg` is now unreferenced. **`Manila Envelope.jpg` is still linked nowhere** and matches plan §8 6a's interdepartment envelope — still his |
| **F6** | The photograph set has never been audited for licensing | **One watermarked Getty/Comstock comp was found and drawn out** (Day 2 §2's desk). The other photographs came out of the 2024/2025 decks the same way and **no one has checked the rest.** Not ours to decide — Ian owns what ships — but worth a sweep before the pack goes out |
| **F5** | RPC's red | **Closed unless he reopens it.** Raised twice on *Four Answers, One Stage* and answered neither time; he approved the pass around it. Will not be raised a third time |

---

## What is closed ##

Recorded so nothing here gets re-opened by accident.

| | |
|---|---|
| **Phase 1** | Every review item D1-1…D1-11, D2-1…D2-10, T-0 and T-1, each with its own commit and a rationale block in plan §9 or §11 |
| **Phase 2** | 90 figures across eleven families; `[external]` is 0; both days have 0 pending markers; Day 1 fully annotated. Only F1 remains |
| **The timing pass** | Plan §11, done and closed |
| **The seven overflowing slides** | Five splits, three cuts; the report is empty and nothing was shrunk |
| **The multi-figure question** | Plan §8 item 23e. Four composed, **one of which Ian split back on review** — and that reversal is the sharpest finding of the exercise |
| **The two delegate reference cards** | Plan §8 item 8. One per pack, both built |
| **The Paper Flow exercise** | Plan §7, built and wired |
| **The tooling job (§A)** | `CLAUDE.md`, five commands and three skills. The operating knowledge is tracked now, not session state |
