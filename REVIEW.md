# Review — Ian's first pass over the built decks #

**Ian, 2026-09-10, on the rendered Day 1 deck:** *"First, this a great first pass."* Then
twenty-six findings. This file is the **work list**, worked top to bottom. **§R1 and §R2 are closed; §R3 is Ian's
second pass over the rebuilt Day 1 deck.**

**Day 1 first, then a Day 2 pass** for the two findings that are not Day-1-specific — the text-box
split and the AI-isms. Ian reviews Day 2 by hand after that.

**§R1 and §R2's thirty rows closed 2026-09-10.** The last two were Ian's own: **R2-3** — Day 2 does
*not* get a blanket `#layout: side`, he names slides one at a time when he reviews it — and **R2-4** —
§*Putting It Together* drops *annotated* rather than growing ten new figures. **What R2-4 handed on
rather than fixed is in `BACKLOG.md` G1**: slides **138** and **141** carry ~4pt annotations, and **138**
and **144** ship typos.

**§R3 opened 2026-09-12 — fourteen rows, all applied.** Day 1 **136 → 131 slides**.

> **Read `BACKLOG.md` for everything else that is outstanding.** This file is only this review.
> When a row here closes it closes here; `BACKLOG.md` §H carries one line pointing at this file.

---

## How to find a slide by its number ##

Ian numbers by the **1-based slide number in the built `.pptx`**, which is not the outline entry
number — 91 Day 1 entries become 138 slides, because 32 of them split into an argument and a
picture. The index is:

```bash
python3 tools/deck_index.py 1        # 1-based slide no. -> kind, section, title, figure
python3 tools/deck_index.py 1 --slide 63
```

**Every number below is a slide number in the deck as Ian reviewed it** — commit `495fd20`,
Day 1 at 138 slides. They will move as this list is worked, which is why every row also names its
**outline anchor**, and the anchor is what to trust.

---

## §R0 — the builder. Three of these are Ian's, one is mine ##

These are not content, and every one of them lands on **both** decks. Do these first: two of the
Day 1 content rows below cannot be answered until R0-2 and R0-4 exist.

| # | the ask | size | state |
|---|---|---|---|
| **R0-1** | **Slide numbers, bottom left.** *"Let's put numbers in the bottom left of slides, so we can easily refer to them."* A chrome op on every slide but the title slide, drawn like the kicker. **This is what makes every other row in this file addressable**, so it goes first | S | ✅ |
| **R0-2** | **One text box per block, and let it wrap.** *"On #3, I note that a paragraph is split into three text boxes. This will make it hard to add animation for progressive disclosure… We also don't want to have a single text box per page, because that also defeats progressive disclosure, we want text box per paragraph, bullet, or heading."* `emit_pptx` currently writes **one text box per wrapped LINE** with `word_wrap = False` — the comment says *"the layout already wrapped, and letting PowerPoint re-wrap would put the deck somewhere the preview is not"*. The **table cells already take the other option** and re-wrap to the measured width; bodies should too. **⚑ This is also the fix for all four of Ian's "overflows"** — see R0-3 | M | ✅ |
| **R0-3** | **The four overflows are one bug, and it is R0-2's.** #4, #61, #63 and #72 are **all callouts**, all Caveat, and **all four wrap correctly in the preview**. They run off the slide in PowerPoint because the box is `Inches(W_IN)` wide with `word_wrap = False`: a line that is 11.7in of Caveat is wider than the slide in whatever face PowerPoint substitutes (**`BACKLOG.md` F2 — the fonts are not installed on Ian's machine**). Fix R0-2 and these four fix themselves. **Verify all four after R0-2 rather than editing the four lines** | — | ✅ |
| **R0-4** | **Progressive disclosure, grouped by idea.** *"We also want animation for that disclosure (you should be able to edit this), but grouped by idea, not naively one transition per paragraph."* python-pptx has no animation API, so this is `<p:timing>` XML written into the slide part. **Ian ruled 2026-09-10: the builder infers it, no outline change.** A lead-in paragraph plus the bullet run under it is one step; a table, code block, quotation or callout is its own; the picture is its own. Built. **⚑ It is the one thing in the build that cannot be checked here** — there is no PowerPoint on this machine and a malformed `p:timing` makes a file refuse to open rather than degrade. Every `spid` is asserted against a shape actually written, ids are unique and in document order, and both decks reopen; `--no-animation` turns it off. **Ian should open a deck early** | L | ✅ |
| **R0-5** | **A fourth arrangement: text left, drawing right.** Not asked for by name, but **eight of Ian's rows need it** — #56/57, #58/59, #60/61, #62, #64/65, #68/69 — all the same instruction: *"shrink the diagram… put the text on the left"*. The builder has three arrangements today and the figure-leads one exists **because `styles.md`'s panel costs a drawing 47–63% of its label size**. Ian is overriding that for these slides knowingly. **Report what each one actually costs when the row is done**, per figure, and let him keep or revert it. **Built as `#layout: side`**, opt-in per entry, text 47% / drawing 53% of the content width. **What the six cost, and this is Ian's to keep or revert:** Dual-Write **49%**, Log Tailing **49%**, Invalid Message **69%**, Dead Letter **69%**, Outbox **71%**, State Change Capture **71%** — against 85–101% before. The two at 49% are wide 2021 imports fitted by width; the redrawn EIP pair hold up best | M | ✅ |

---

## §R1 — Day 1 content, in Ian's order ##

| # | slide(s) | outline anchor | the ask | size | state |
|---|---|---|---|---|---|
| **R1-1** | **#5** | `### Slide: Robust — Guaranteed Delivery` (:45) | *"'The other thing a boundary buys, and it is the cheaper of the two.' is stilted AI language, try to rewrite in my style. Broadly, try to remove AI-ism from text you generated as opposed to picked from original docs."* **Two jobs**: this line, and then a **sweep of Day 1 for prose that is ours rather than lifted**. `session-work/day1.txt` is the 2025 deck and is what "original docs" means — a line that appears there is his and stays | M | ✅ |
| **R1-2** | **#28 + #29** | `### Slide: Messaging and Events` (:301), `### Slide: Messaging vs. Eventing…` (:306) | *"On #28, I don't think this is doing enough work, it could be combined with #29. On #29, I think the comparison between Messaging and Eventing is better rendered as a table, see the original."* #28 is one sentence. Fold it in as the lead-in and **make #29 a table** | S | ✅ |
| **R1-3** | **#30** | `### Slide: Discrete vs. Series…` (:314) | *"I think Discrete vs Series would be better as a table."* Two bullets of paired attributes — they are a table pretending to be a list | S | ✅ |
| **R1-4** | **#31 + #32** | `### Slide: Message Types` (:322), `### Slide: Command / Document / Event Messages` (:327) | *"On #31, I don't think this is doing enough work and can be combined with #32."* Same shape as R1-2: #31 is one sentence naming the three, #32 defines them | S | ✅ |
| **R1-5** | **#41** | `### Slide: The Message Pump` (:419) | *"this was once visual, I think that works better than the text."* **It was**: 2025 deck slide 58 draws *Get → Translate → Dispatch → Handle* with the four error routes hanging off it (`session-work/day1.txt`). **A new figure**, and the error-routing prose becomes its labels | M | ✅ |
| **R1-6** | **#42** | `### Slide: Translate and Dispatch` (:433) | *"again this was once visual, I think it works better separate from #41 but needs to be visual."* 2025 deck slide 59 — the same four-stage pump with **Message Mapper Registry** and **Handler Registry** hanging off Translate and Dispatch. A second figure, deliberately **not** merged with R1-5's | M | ✅ |
| **R1-7** | **#47 → three slides** | `### Slide: Competing Consumers` (:494) | *"the split between how this works in streams and queues is full of AI-ism and badly described. We want three things."* **(a)** a general statement, and Ian wrote it: *"If the Rate of Arrival of messages (RoA) exceeds the Rate of Consumption (RoC) your channel will back up and the age of any message in the channel will increase. At some point the time a message waits in the channel will become unacceptable. You solve this problem by competing consumers, but the implementation differs between streams and queues."* **(b)** a queue slide with a diagram — *"locking (this item is being processed) and read-past, pick up the next item, but sacrifice ordering."* **(c)** a stream slide with a diagram — *"we partition by a key, and each partition has a consumer, and we retain ordering, but have no delay or read-past."* **⚑ Do R1-15 (§4.5) and this row together** — they are the same repetition seen from two ends | L | ✅ |
| **R1-8** | **#56 + #57** | `### Slide: The Dual-Write Problem` (:607) | *"shrink the diagram on #57 and combine with the text. It's too weird to read the words, then show the diagram here."* Needs **R0-5** | S | ✅ |
| **R1-9** | **#58 + #59** | `### Slide: Outbox` (:620) | *"move the text lines 'But look at what we just bought:' / 'We can fail after the send and before marking it Sent.' / 'The sweeper then finds it Pending and sends it again.' to presenter notes. Put the text on the left, and move the diagram from #59 here and shrink it… If needed move more of the text to notes to fit."* Needs **R0-5**. **⚑ The presenter note already says the duplicate is the question the Inbox answers** — check the move does not say it twice | S | ✅ |
| **R1-10** | **#60 + #61** | `### Slide: Log Tailing…` (:644) | *"move the diagram to the right on #60, text to the left on #60, shrink diagram, move some text to notes if needed. Split is weird."* Needs **R0-5**. The overflow half of this row is **R0-3** | S | ✅ |
| **R1-11** | **#62** | `### Slide: State Change Capture` (:674) | *"follow the changes on #58 and #60 and put diagram on the right (shrink) and text on left."* Already a single slide; it is the *arrangement* that changes. Needs **R0-5** | S | ✅ |
| **R1-12** | **#63 → two slides** | `### Slide: When the Handler Fails — Ack and Nack` (:686) | *"Split into two slides."* First keeps everything **through** *"…at-least-once stops being a slogan on the consumer side."* Second starts at *"But not acking is not a strategy, it is a question"* — **and is rewritten**, because Ian says the framing is wrong: *"On not ack we have options, not questions: **Requeue** ⇒ put this message back on the queue; **Reject** ⇒ don't process this message, drop it (either skip on a stream or delete on a queue). On a requeue we tend to set a policy for how many times, exceed that and you go to the DLQ. On a reject, if it is a badly formed message it goes to an invalid message queue. By policy we might send a well-formed message to the DLQ immediately on a reject."* **⚑ This changes what the next three slides are the answers to** — the `#note:` at :711 and the presenter note both say "three questions" and both need the same edit | M | ✅ |
| **R1-13** | **#64 + #65** | `### Slide: Invalid Message Channel` (:721) | *"Shrink the diagram, combine into one slide."* Needs **R0-5** | S | ✅ |
| **R1-14** | **#66, #67** | `### Slide: Requeue with Delay` (:739) | *"On #67, we should be clear that this is a queue, not a stream. On #66 we should note that only queues support requeue with delay via their locking mechanism. A stream must use another method to put a message onto the stream again, after a delay, such as a scheduler, and doing so will de-order the stream."* **The `#note:` at :752 already says "say queue here"** — Ian wants it *on the slide*, not in a build note. **New content**, and it is the stream half | S | ✅ |
| **R1-15** | **#68 + #69** | `### Slide: Dead Letter Channel` (:757) | *"Shrink the diagram, combine into one slide."* Needs **R0-5** | S | ✅ |
| **R1-16** | **#72** | `### Slide: What Your Broker Actually Gives You` (:794) | The overflow. **R0-3** — no content edit expected. **Verified 2026-09-10, all four**: each callout is now one box with `wrap="square"`, right edge **12.65in** on a 13.33in slide (Log Tailing's is 6.15, it is a `side` slide). No content was edited on any of the four | — | ✅ |
| **R1-17** | **§4.5, all of it** | `## 4.5 Queues and Streams` (:837) | *"there is repetition here, between the competing consumers and error discussions in slides above. Perhaps this is not a separate section, but needs to be combined into the material above as 'how this works for queues, how this works for streams', otherwise this will flow badly on the day by repeating ideas."* **The largest row in the file.** §4.5 is 18 slides and 11 figures; the overlap is with §4.3's *Competing Consumers* (R1-7) and §4.4's error slides (R1-12 … R1-15). **⚑ Structural — re-run the cross-reference sweep after it** (`BACKLOG.md` B6), and **`exercises/Quick-Start-Kafka.pptx` is wired to land in §4.5** (the `#note:` at :841), so a dissolved §4.5 has to say where the Kafka exercise goes. **Put the proposed shape to Ian before cutting** | L | ✅ |
| **R1-18** | **#94–#96** | `### Slide: Messaging Participants` (:978), `### Slide: Messaging or Eventing?` (:996) | *"This repeats the conversation from earlier, around #29. Again, let's combine into the earlier conversation."* #96's table **is** #29's table. Note the section goal at :975 and the figure `conversation-messaging-or-eventing.png` — decide what survives where | M | ✅ |
| **R1-19** | **#99–#111** | `### Slide: In-Only…` (:1029) through `### Slide: Choosing an Exchange Pattern` (:1181) | *"On #99-101 we describe three of the patterns. On #103 to #109 we redescribe the patterns. **We miss a whole pattern.** After the table, we should talk about each pattern, with all the information for it, and then at the end summarize error flows #102, and choices #110 and #111."* The missing one is **Out-In** — #99–101 are In-Only, Out-Only, In-Out. **Target shape:** the 2×2 (#97/98), then **one block per pattern with everything about it folded in** — In-Out absorbs #103 (timeout), #105 (command or query), #107 (blocking); Out-Only absorbs #106 (subscribe-notify); Out-In absorbs #108/109 — then **Faults, by Pattern** (#102), then **Choosing** (#110/111) | L | ✅ |
| **R1-20** | **#120** | `### Slide: Get It On Demand — REST/RPC` (:1298) | *"we are missing a diagram here, and we have diagrams for content enricher, let's put the diagram back."* A new `eip_figures` drawing — the consumer calling back for the data it was not sent | M | ✅ |
| **R1-21** | **#123** | `### Slide: Get It In Advance — ECST…` (:1333) | *"we are missing a diagram here and we have a diagram for content enricher, let's put the diagram back."* A second new drawing — the state arriving **on** the event, so there is no call back | M | ✅ |

---

## §R2 — the Day 2 pass ##

**Ian: *"Some of these points (such as text splitting and AI-ism) will apply to day two, but let's do
Day One first, then make a pass at Day Two for these issues before I manually review."*** So §R2
starts only when §R1 is closed, and it is deliberately **narrow** — it is not a second full review.

| # | the ask | size | state |
|---|---|---|---|
| **R2-1** | **Text splitting** — R0-1, R0-2 and R0-4 are builder changes and land on Day 2 for free. **Verify, do not assume**: render Day 2 and look, and re-check the callouts in particular, because that is where every Day 1 overflow was | S | ✅ |
| **R2-2** | **AI-ism** — the same sweep as R1-1, over `outlines/DayTwo.md`. `session-work/day2.txt` is the 2025 deck and is the test of what is Ian's | M | ✅ |
| **R2-4** | **⚑ Found while doing R2-2.** §*Putting It Together* (slides 130–145) promised an **annotation layer that is not in the artwork** — four titles ended *"— Annotated"* and four `#image:` alt lines said *"annotated with exchange patterns"*, and **not one of the ten figures carries a single pattern name.** Verified rather than inherited: **all ten appear exactly twice in `DayTwo.md`** — once where the flow is first taught (:188–:502), once here (:1177–:1211) — so an annotated version has to be a **new file**, and the sources are five `.excalidraw` and five `.drawio`, **neither of which this machine can render**, so *annotate* means *redraw in `tools/`*, i.e. G1. **Ian, 2026-09-10: drop *annotated*, leave it the spoken walk-through it already is.** Four titles renamed, five alt lines corrected — the fifth was *"composite … plus thumbnails of the other flows"* on slide 144, and **opening it showed one collaboration diagram and no thumbnails**, the same defect found the same way. R2-2's bodies already said only what is on screen and are unchanged. **⚑ What this does NOT fix, and G1 must:** plan §14.3 measures slides **138 and 141** at roughly 4pt, and **138 and 144 carry typos that ship today** | M | ✅ |
| **R2-3** | **Ian, 2026-09-10: do not roll it out — ask per slide.** Measured before asking, by building Day 2 twice: **38 entries split today, 23 carry exactly one figure** and so are eligible (`_side_slide` is guarded on one figure). Wholesale, the median figure goes **96% → 53%**, **all 23** land under 85%, and **7 need text cut to notes** (*Compensation, Four Ways* by 5.26in). **8 of the 23 are BPMN** — the one family already at the type floor (rule 6), where 49% is not a shrink. The two worst are *The Frame* (88→26%) and *The Desk* (101→29%), both because the slide also carries photographs, so the figure shares the half-stage at 3.0in not 6.1. **Day 2 keeps figure-leads. When Ian reviews Day 2 by slide he names the slides he wants text-left on, and each gets one `#layout: side` line** with the cost reported by name, as on Day 1 | — | ✅ |

---

## What this review did NOT ask for ##

Recorded so it does not get done by accident, and so the next session does not re-derive it.

- **Nothing about the 2021 imports' register** (`BACKLOG.md` G1). Five of them are the figures in
  R1-8 … R1-11 and R1-14, and Ian's instruction there is to **shrink and reposition**, not redraw.
  G1 stays scoped-and-not-started.
- **Nothing about `styles.md`.** The palette, the type scale and the two registers are not in scope.
- **No new sections and no cuts to §1, §2, §3, §6.1 or §6.3** beyond R1-1's prose sweep.


---

## §R3 — Ian's second pass over Day 1 ##

**2026-09-12, against the rebuilt deck.** Fourteen rows. **⚑ Ian numbers by the slide numbers he was
reading, which were the 136-slide build**; Day 1 is **131** now, so every number below 31 is unchanged
and everything above it has moved. The rows are anchored on **entry titles**, which did not move.

| # | slide (his) | the ask | state |
|---|---|---|---|
| **R3-1** | **7** | *"The opener said exactly this… That slide was the mechanism. This is what it bought you."* — AI-ism. Three sentences for one point, two of them about a previous slide | ✅ |
| **R3-2** | **10** | *"There is a second axis, and interacting between processes is what forces it on you."* — AI-ism. Announces an axis, then states it. Now *"The second axis is **time**."* | ✅ |
| **R3-3** | **14** | *"Hold that thought — the last slide of this section is about everything you did not get with it."* — AI-ism. A forward reference is presenter guidance; the entry had **no presenter note at all** and now has a specific one, checked against *Why Messaging* rather than paraphrased | ✅ |
| **R3-4** | **31 + 32** | *Queues Contain Tasks* — shrink and merge. *"Too hard to talk to the text, then repeat on the slide"* | ✅ |
| **R3-5** | **33 + 34** | *Streams Contain Facts* — merge, and drop four lines that are **on the image anyway**. **Three of the four are**: the offset store, the bookmark-on-restart sentence nearly verbatim, and *facts are an inverse database*. **The clause that is not** — *navigate the offsets to compute a point-in-time position* — went to the notes. The callout was not on the image either, but it **restated the two slide titles**, so it earned the cut | ✅ |
| **R3-6** | **50** | Text hidden under the picture. **⚑ Not a content row — see R3-14.** Ian quoted slide 58's callout against this slide; 50's own is *"Your handler is not a message handler…"*. The defect is real on both | ✅ |
| **R3-7** | **53 + 54** | *Competing Consumers on a Queue* — merge; *"Read-past buys you throughput. It spends your ordering to do it."* to the notes | ✅ |
| **R3-8** | **55 + 56** | *Competing Consumers on a Stream* — merge; *"On a queue you spend ordering to buy throughput…"* to the notes | ✅ |
| **R3-9** | **58** | The picture clips the callout. **R3-14** | ✅ |
| **R3-10** | **76** | The picture clips the callout. **R3-14** | ✅ |
| **R3-11** | **77 + 78** | *Inbox (Idempotency)* — shrink and merge | ✅ |
| **R3-12** | **101** | *"Drop. The other pattern slides are only text, and I don't think that this diagram adds."* `conversation-timeout` is now **placed zero times** — kept in `resources/` and in the family, not deleted | ✅ |
| **R3-13** | **111** | *"The original deck has a diagram for transitive dependencies… let's redraw and add it, probably on its own slide for space."* **It is Day 2 2025 slide 37, not Day 1** — and it has **no extracted image**, because the original is a native table plus text boxes and leader lines. Read out of the archived `.pptx` shape by shape and redrawn as `eip-fat-message-transitive` | ✅ |
| **R3-14** | **113** | The callout overlaps the prose. **⚑ This, R3-6, R3-9 and R3-10 are one number.** `_lines` reserved `n × pt × lead`, and the callout's `lead` is 1.06 against Caveat's 1.260em ink extent — so every callout claimed to end **0.200em before its descenders did**, and whatever came next sat 0.067in too high. **108 callouts across both decks**, 73 of them under an opaque picture. Fixed in `_reserve`; inter-line spacing is untouched | ✅ |

### What §R3 turned up that Ian did not ask about ###

- **⚑ Every `#layout: side` slide reads at 8.9–12.8pt against an 18pt floor.** Eleven of them now. The
  half-stage is **6.1in** where Phase 2 measured 12.4. **`reads_at.py` cannot see it** — it measures
  against the full-width stage and knows nothing about the arrangement, and it reports all four
  `queues_streams` figures at exactly 18.0pt. The four `qs-*` figures are **ours**, so re-laying each
  into a narrower, taller canvas brings them back to the floor at 6.1in. **Not done — Ian has not asked
  for it, and it is figure work.**
- **The preview could not have shown R3-14**, by construction: it draws the lines itself at the same
  1.06, so it agreed with the layout and always had. That is the fourth thing the `.pptx` does that the
  preview cannot show.
- **⚑ R3-14 is unverifiable on this machine.** There is no PowerPoint here. Slides 50, 58, 76 and 113
  need re-opening.
