# Backlog — what is outstanding #

**An index, not a source of truth.** Every line points at where the real detail lives.
`REDEVELOPMENT-PLAN.md` is the source of truth for the decks; **`code-rewrites.md` is a separate
workstream with its own brief**. If this file and the plan disagree, **the plan wins and this file
is stale**. Kept as a table on purpose — counts in prose go stale silently,
and a table you can read the length of does not.

Last reconciled against the repo: **2026-09-10**, after C4. **§C's two handouts are both built**, so
**nothing is left in §B or §C.** B7 closed as a clean negative, C3 and C4 are built.
**§G is new** — the full-deck visual sweep, nine findings, none of them ruled on yet. B2 and B3 have no
action available.

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
| **G1** | **30 slides (10%) carry a 2021 import in a foreign register** | **L** | Day 1 **5** — §4.4's producer side (`Transactional No Outbox`, `Transactional With Outbox`, `Log Tailing`, `State Change Capture`, `Inbox`), bright blue/orange/green, **sitting in the same sub-section as the redrawn consumer-side figures**. Day 2 **25** — the whole *Worked Flows* run, the FBP worked examples, and **all of *Putting It Together***: black-on-white value streams still stamped *29 SEP 2021*, tiny blue-and-black fax flows, purple-hexagon FBP graphs. **Against the standing instruction in the plan** — Ian: *"Let's redraw both runs. One thing I want to strive for is a consistent look and feel"* — beside which the plan already warns *"their `.png`s are 2021 black-on-white, so linking them keeps the old look."* **Several are illegible at slide size**: d2-137 and d2-140 carry ~4pt annotations, and `paper-worked-flows-montage` (d2-022) tiles four of them onto one slide |
| **G2** | **10 slides say the same line twice** — the callout repeats the figure's own red note | S | Two are word for word: **d1-007**, **d1-011**. The other eight are close paraphrases — d1-018, d1-051, d1-103, d2-022, d2-035, d2-039, d2-060, d2-072. In most the **red note is the longer and better line**, so the callout is what should go; **d1-051 is the exception** — its callout carries a §4.4 forward reference the note does not. Dropping a callout also gives the figure back ~13 points |
| **G3** | **3 text-on-text collisions inside figures** | S | `grid-coupling` — *"a command message"* printed across *"a whole entity"*. `flow-bulkhead` — a long comment line runs straight through **both** node captions. **`lint_figures.py` cannot see any of them**: it measures a label against a *shape* and against arrow runs, never against another label |
| **G4** | **6 slides whose body is the words "Section marker"** | S | d1-027, d1-080, d1-085, **d2-005**, d2-062, d2-129. Scaffolding that went up on screen — rule 2 in spirit. **d2-005 is the first teaching slide of Day Two** |
| **G5** | **Day 1's Closing is a stub** | S | *Further Reading* reads **"Pointers for going deeper."** and lists nothing, where Day 2 closes with four proper reading slides and their covers. The *Closing* divider is also the only one in either deck with no sub-line |
| **G6** | ✅ **d1-025's divider sub-line restates its own title** | — | *"4.1 What Is a Message?"* over *"What is a message?"*. The only one of the 19 dividers that does it. **Fixed 2026-09-10** — the sub-line now names what the section teaches, *"Header and body — and whether you are expressing intent or reporting a fact"*, which is the shape every other section's sub-line uses |
| **G7** | ✅ **d2-148's URL is clipped and runs under the photo panel** | — | `(jonasboner.com/resources/Reactive_Microservices_Architect` — cut mid-word, no closing bracket, unusable. **The builder already guards the kicker against exactly this and warns on stderr; body text had no equivalent guard.** Rule 11. **Fixed 2026-09-10, both halves:** the URL is now prose a delegate can type, and `Type.wrap` warns once per over-wide word — with 0.05in of slack, because a table cell pads beyond its measured column and "Out-Only" sitting 0.02in over renders whole. **⚑ `Type.wrap`'s docstring claimed a long word "shows up in the overflow report" and that was false**: overflow measures HEIGHT, and a word running off the right costs no height |
| **G8** | **Two dashed-arrow conventions in one deck** | S | The taught notation key (**d2-010**, ours) draws *dashed = paper moving* in **carbon**; the imported 2021 flows draw it in **red**; and the BPMN mapping table on **d2-080** tells the room *"a red dashed arrow between an out-tray and an in-tray"*. Checked: `exercises/Paper-Flow-Delegate-Brief.md` line 35 says only *dashed / solid* and names no colour, so **the brief is not in conflict** — CLAUDE.md rule 13's own example slightly overstates it |
| **G9** | Minor, listed for completeness | XS | **4 slides carry two callouts** (d1-008, d1-022, d1-101, d2-006) where the register is meant to mark *the one thing*; **d1-030** is a one-line slide that reads as the lead-in to d1-031 |

**What the sweep did NOT find**, which is worth recording: no overflow, no missing image, no broken
cross-reference, no figure family off-style, and no defect at all in `queues_streams`, `conversations`,
`eip_figures`, `bpmn_hotel`, `bpmn_shopping` or `integration_styles`. **The redrawn families are clean.**

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
