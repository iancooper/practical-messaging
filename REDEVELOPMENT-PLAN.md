# Practical Messaging — Redevelopment Plan

Working plan for the redevelopment of the two-day *Practical Messaging* course.
Tracked on branch `deck-redevelopment`. **This document is the single source of truth for decisions
and outstanding work.** `PROMPT.md` (untracked) holds only session state and points here.

These are working notes for us, not client-facing material — the judgements in them are blunt on
purpose.

---

## 1. Scope

Three artefacts:

| artefact | source | state |
|---|---|---|
| **Day 1 deck** | `Practical Messaging - Day 1 - 2025.pptx` (138 slides) | outline rebuilt to **96** entries |
| **Day 2 deck** | `Practical Messaging -  Day 2 - 2025.pptx` (182 slides, note the double space) | outline rebuilt to **97** entries |
| **AsyncAPI handout** | QCon London 2026 deck (43 slides) | to assemble — §6 |
| **Routing-patterns handout** | old Day 1 §4.6 + `script/Patterns/*.md` | to assemble — §10 |

Working style: **outline in Markdown first**, then rebuild the deck from the outline. The outlines in
`outlines/` are the working artefact — edit those, not the pptx.

**Exercises and code examples are a separate track.** The one exception is the **Paper Flow** exercise
(§7), which is a deck-shaping decision — it takes the slot Managing Asynchronous APIs vacates — and so
is planned here.

### Outline conventions

- `#` = deck title, `##` = section header, `###` = individual slide (`### Slide: <title>`)
- Body prose + bullet lists as needed
- `▎ ` prefix = an on-slide callout / pull-quote (punch-line text boxes)
- `Presenter notes:` label = speaker notes carried over from the deck
- `#image: <description>  [<source annotation>]` = the slide was mainly an image
- `#note: ...` = a non-image annotation
- a fenced ```` ```csharp ```` block = code shown **on the slide**, set as text in Plex Mono per
  `styles.md`, never as a screenshot. A listing has to be cut to what a room can read: a 39-line
  screenshot scaled to a 16:9 slide comes out at about seven points. First used in Day 2
  §Process Automation.
- `#group: <title>` = a group divider *within* a sub-topic — a run of slides that belong together. Not a
  slide, so it is not counted; `###` stays reserved for entries. First used in Day 1 §4.4 (D1-8).

---

## 2. Method — three phases, run per section

### Phase 1 — Review the content
1. Ask Ian what the **goal** of the section is (what should a delegate be able to do or decide after it?).
2. Review the current outline content against that goal.
3. Propose changes — cuts, re-orderings, missing ideas, slides that carry no weight.
4. Discuss how to make it better before touching anything.

### Phase 2 — Image requirements
1. List the images the revised section needs.
2. Split them: **what Ian draws** vs. **what AI generates**.
3. Create them.

### Phase 3 — Rebuild the deck
Rebuild from the outline. Improve look and feel — it should read as **professional training material**,
not a personal deck.

---

## 3. Decisions

### The shape of the two days (settled 2026-08-27)

Day 1 is **the message**; Day 2 is **the flow**.

1. **Design material moved forward.** Conversations + Repair (25 entries, rebuilt to 15) moved to Day 1.
   Fat & Skinny + Domain/Summary stayed on Day 2 as the on-ramp to Flow.
2. **Managing Asynchronous APIs became a takeaway handout**, not taught material (§6).
3. **A paper-modelling exercise took its Day 2 slot** — found to already exist (§7).

Current (**Phase 1 complete on both days**, 2026-08-29): **Day 1 = 96 entries** with two code
exercises; **Day 2 = 84** with one paper exercise, run in two blocks and a closing round *inside* §1.

**✅ The timing pass is done (2026-09-01) — see §11.** It found the opposite of what the entry counts
suggested. Day 2, the day we spent D2-10 cutting, **fits with room to spare**. **Day 1 was over by ~53
minutes** — because D1-9 moved *Designing Messages* (16 entries) onto it and nothing came off to pay for
it. **T-0 took 19 of those minutes** by moving Day 1's *why* preamble to Day 2, and **T-1 another 5**; Day 1
is now **419 of 390** and Day 2 **354 of 390** — **773 of 780 across the pair**. Ian then **closed the
pass** (§11): Day 1 running over into the top of Day 2 is how the course already runs, and Day 2's slack
is where it lands. T-2 … T-5 are **parked, not cancelled**.

Why the split holds on content, not just counts: Conversations + Repair continues Day 1's build order
directly — *you can send and receive reliably, now what exchange do you build with it*. Fat & Skinny +
Domain/Summary is about what is **in** the message and how state propagates, which leads into Flow.

### Section goals agreed so far

| section | goal |
|---|---|
| Day 1 §1 Distributed Systems | *set up the problems messaging solves* — and **stop there**. Two properties wanted (easy to change + robust), what independent deployability commits you to, and the bill. The answer is messaging, and §2 → §3 → §4 give it |
| Day 1 §2 Coupling → §3 Integration Styles | *why messaging is our preferred option* — the process boundary prevents Content and Common; the message chooses among Control / Stamp / Data; and being between processes forces the temporal trade. The four styles are then scored on what each hands back |
| Day 1 §4 Messaging Patterns | a **build order**, not a catalogue — see below |
| Day 1 §5 Conversations | *choose the right exchange pattern* — pick between In-Only / Out-Only / In-Out / Out-In and know what each commits you to in coupling terms |
| Day 2 §1 Designing Messages | *decide what goes in a message* — choose what to put in it, and know how the receiver gets whatever you left out and what that costs in availability |
| Day 1 §6 Designing Messages *(moved from Day 2)* | *decide what goes in a message* — as above; it now closes Day 1 rather than opening Day 2 |
| Day 2 §1 Flow and Reactive | *stop drawing your system as call-and-return* — draw it as flow instead, and know what that buys. Also arms the Paper Flow exercise |

### Teaching decisions

- **Day 1 opens on two properties, not on microservices** (2026-08-27). We want to be **easy to change**
  (independent deployability) and **robust** (guaranteed delivery). Microservices are *one* way to buy
  the first and are not free; **task queues buy the second with no reorganisation at all**. Both are
  bought with messages. The microservices-justification framing is dated — in 2026 nobody in the room
  needs persuading microservices exist, and the section's own agreed goal already said *not: justify
  distributing*.
- **This plants a Day 2 payoff — do not spend it early.** The Reactive Manifesto (2014) names the second
  property **Resilient**, and claims the first in its own words: *"Systems built as Reactive Systems are
  more flexible, loosely-coupled and scalable. This makes them easier to develop and amenable to
  change."* Day 1 must **not** mention Reactive; Day 2 should land as recognition, not repetition.
- **The course's central argument**, established in §1 and paid off in §2: availabilities multiply only
  when the chain is *temporally* coupled. Store-and-forward with guaranteed delivery breaks that — the
  outage becomes a delay, not a failure. Availability loss traded for latency variance.
- **§4 Messaging Patterns is a BUILD ORDER** — the sequence someone from an HTTP background needs to
  write messaging code and make it reliable: 4.1 What Is a Message? → 4.2 Sending and Receiving →
  4.3 The Message Pump → **4.4 Guaranteed Delivery (new)** → 4.5 Queues and Streams → 4.6 Pipelines.
- **Audience assumption for §4:** comes from an HTTP background; does not know how to write messaging
  code or make it reliable.
- **The lifetime rule is a RULE, not a heuristic** (Ian) — *if the data does not share the message's
  lifetime, put an id in the message, not the data*. On top of it, **be pragmatic**: exactly as with a
  database you may denormalise a common lookup, but it is a decision you should be able to justify, and
  you then own a stale copy and someone else's schema.
- **Day 1 is the whole of the single message; Day 2 is the flow** (settled 2026-08-28, item D1-9). Day 1
  now runs the build order to §4.5 Queues and Streams, then the two decisions you make with it: §5
  **Conversations** (which exchange) and §6 **Designing Messages** (what goes in it). Day 2 opens at the
  level of whole flows. Ian: this "better completes the picture on how to send and receive, ahead of Day
  2's switch to the higher level".
- **Three things were dropped to buy exercise time** (2026-08-28, Ian). **§4.6 Pipelines** → the
  routing-patterns handout (§10), keeping only *Content Enricher*, which moved into §6.2 Reference Data as
  the drawn form of the on-demand lookup. **Versioning** and **Observability** → one pointer slide each in
  Day 2 `## Next Steps`. All three are things a delegate can read; none is a decision we can rehearse in
  the room, which is what the two days are for.
- **Deck + script are to be MERGED.** Delegates mostly read rather than watch, so `script/Patterns/*.md`
  (22 files, 4,287 words, near-1:1 with the EIP slides) becomes the slide body during Phase 3. Only
  *Translate and Dispatch* has no script. `script/RMQ/*.md` (9 files, 783 words) merges with
  `exercises/Quick-Start-RMQ.pptx` in §4.2.

### Exercise arc

| where | broker | what delegates do |
|---|---|---|
| Day 1 §4.2 | RabbitMQ | channels and endpoints on real infrastructure |
| Day 1 §4.4 | RabbitMQ | build reliability where most of it is **native** |
| Day 1 §4.5 | Kafka | get the *same guarantees* where almost **none** of it is native |
| Day 2, after Reactive, before Process Automation | paper | **model, run and break a flow** — *Paper Flow*, §7 |

Routing patterns stay as **content** (deck + `script/Patterns`); hands-on time moves to **reliable
messaging over queue and stream**. `exercises/Quick-Start-Kafka.pptx` lands in §4.5.

### Heading levels are a known inaccuracy — fix in Phase 3

Both outlines use `##` for sub-topics as well as sections.

- **Day 1:** the spine runs from `## Messaging Patterns` down to `## Conversations`; the intervening
  `##` headings (4.1 … 4.6) are sub-topics, not sections.
- **Day 2:** eight `##` headings, four real sections — Designing Messages (Fat and Skinny / Reference
  Data / Event Shape / Versioning), Flow and Reactive Programming, Process Automation, Close.

Two of the Day 2 merges are **load-bearing, not cosmetic**:

- **Repair was not a separate topic** — it was the fault column of the same table. Robust In-Only,
  Robust In-Out and In-Out-Retry are the MEPs from Conversations with a fault path bolted on. Folded in
  during the Conversations rebuild.
- **Flow is not a section** — it is the on-ramp to Reactive. Paper workflows → dataflow → FBP is one
  argument, and the Fax Workflow worked example inside Reactive is the same one *Putting It Together*
  annotates at the end of the day.

---

## 4. Day 1 work queue — `outlines/DayOne.md`, 7 sections, 96 entries

> **§9 (review queue, 2026-08-28) is fully applied to Day 1 — D1-1 … D1-11 are all done.** The rows below
> are current. Everything still outstanding in §9 is on Day 2.

| # | Section | entries | P1 | P2 | P3 |
|---|---|---:|---|---|---|
| 1 | **The Process Boundary** *(was Distributed Systems)* | **2** | ✅ **T-0 (2026-09-01): 7 → 2.** The *why* went to Day 2; the boundary + guaranteed delivery compressed into an opener | ☐ | ☐ |
| 2 | Coupling | **4** | ✅ D1-7; **T-0 dropped *Why It Matters*** and moved the 0.999⁴ arithmetic into *Must We Both Be Up?* | ✅ `grid-coupling` + `coupling-scale-boundary` | ☐ |
| 3 | Integration Styles | 5 | ✅ D1-7: each style scored on what it hands back; closes on *Why Messaging* | ✅ §2 grid re-plotted + 4 `style-*` figures (item 9) | ☐ |
| 4 | **Messaging Patterns** | **46** | ✅ build order; −9 §4.6, +2 task queue, +1 D1-8 | ☐ 12 EIP redraws | ☐ merge scripts |
| 4a | · The Big Picture | 1 | ☐ reframe as build order | | |
| 4b | · 4.1 What Is a Message? | 6 | | | |
| 4c | · 4.2 Sending and Receiving | 7 | +RMQ Quick Start | | |
| 4d | · 4.3 The Message Pump | **8** | +*Task Queue* worked example & HTTP flow, from §1 (D1-6) | | |
| 4e | · **4.4 Guaranteed Delivery** | **11** | ✅ D1-8: producer / consumer / broker, +*Ack and Nack* | | |
| 4f | · 4.5 Queues and Streams | 13 | +Kafka Quick Start | | |
| 5 | **Conversations** *(moved from Day 2)* | **13** | ✅ 25 → 15, rebuilt as a decision; **T-1: fault slides 3 → 1** | ☐ 1 new grid + reuse §2 grid | ☐ |
| 6 | **Designing Messages** *(moved from Day 2)* | **16** | ✅ moved by D1-9; **☐ D1-10 outstanding** | ☐ 2 If-Later diagrams; 1 EIP redraw | ☐ |
| 6a | · 6.1 Fat and Skinny Messages | 5 | ✅ rebuilt on the lifetime rule | | |
| 6b | · 6.2 Reference Data | 5 | ✅ D1-10: ECST rewritten as **the recommendation**; +*Content Enricher* | | |
| 6c | · 6.3 Event Shape | 6 | ✅ +*Why ECST Needs Snapshots* | | |
| 7 | Closing | 2 | ☐ | ☐ | ☐ |
| — | ~~4.6 Pipelines~~ | 9 | ✅ **→ routing handout (§10)**; *Content Enricher* kept, → §6.2 | | |
| — | ~~Observability~~ | 3 | ✅ **dropped**; one pointer slide in Day 2 `## Next Steps` | | |
| — | ~~Managing Asynchronous APIs~~ | 31 | ✅ **→ handout (§6)** | | |

Day 1 is **Messaging Patterns (46, 52%)**, then the two decisions — **Conversations (13)** and
**Designing Messages (16)** — with **11** slides of framing in front and 2 of wrap-up behind. **88 entries**
after T-0 and T-1.

---

## 5. Day 2 work queue — `outlines/DayTwo.md`, 4 sections, 86 entries

> **Superseded by §9 (review queue, 2026-08-28/29). All of D2-1 … D2-10 are done.** Day 2 is **84
> entries**: Process Automation cut 50 → 37, the pizza example redrawn to the hotel, and the Josuttis
> collision resolved in §1's favour. Phase 1 on Day 2 is complete.

| # | Section | entries | P1 | P2 | P3 |
|---|---|---:|---|---|---|
| 0 | **Why Event-Driven?** | **2** | ✅ **new, T-0 (2026-09-01)** — the *why* moved off Day 1; opens the day ahead of Flow | ☐ | ☐ |
| — | ~~Designing Messages~~ | 15 | ✅ **→ Day 1 §6** (D1-9) | | |
| — | ~~Versioning~~ | 4 | ✅ **dropped**; one pointer slide in `## Next Steps` | | |
| 1 | **Flow and Reactive Programming** | **34** | ✅ 32 → 28 → 34; movements reordered, exercise split across it (D2-3…D2-8) | ☐ 3 new/redrawn | ☐ |
| 1a | · A — How the Office Did It | 9 | paper; the **see one**, four flows one slide each; ends in **exercise block 1** | | |
| 1b | · B — How Would You Build That? | 4 | OO / SOA / Feature Envy — the **failed answer**, offered second | | |
| 1c | · C — The Formalism | 10 | dataflow → FBP; both flows as graphs; ends in **exercise block 2** | | |
| 1d | · D — The Name | 10 | ✅ all three Day 1 debts paid; closes on **round 4** into Process Automation | | |

**It now leads the day** (D2-2), so its opener has to open Day 2. **D2-3 … D2-8 reworked it** — see §9.

**Section goal (agreed 2026-08-28):** *stop drawing your system as call-and-return, and start drawing it
as flow — and know what that buys.*

### What changed in the §2 rebuild

> **Partly superseded by D2-3 … D2-8 (§9).** The merges, cuts and promotions below all stand. What no
> longer holds is the **movement order** — D2-5 inverted it again, so paper leads and OO/SOA is the failed
> answer — and the ***see one* slide list**, which D2-3 expanded from two slides to four. Read the four
> bullets below as the state after the §2 rebuild, not as current.

**The argument order was inverted.** It ran paper → OO → dataflow → FBP → *back to OO at service scale
(SOA)* → Reactive — making the "call and return doesn't scale" argument twice, twenty slides apart. The
SOA block **moved to the front and merged with OO**, so the antagonist is stated once, at both scales, and
everything after it is the answer:

- **A — Call and Return.** OO → *Call and Return, and the God Object* → *SOA Is OO at Macro Scale* →
  *Feature Envy — You Built a Distributed Monolith*. Ends on **the gateway is `main`**, and the deck's
  own question, *is there a better paradigm?*
- **B — Paper Workflows.** Answers it with a photograph: the office was a distributed system with no god
  object.
- **C — Dataflow and FBP.** The formalism, and the same four flows again as a graph.
- **D — Reactive.** The name for what they have been building since Day 1.

**The *see one* is now actually taught.** The old *Paper Workflow Illustrations* slide was a single entry
holding **17 unlabelled images**. Split into four real slides — *The Frame*, **· *The Desk — In-Tray,
Out-Tray, File* (new)**, *Worked Flow — Restaurant Onboarding*, *Worked Flows — Order, Placement,
Confirmation* — plus *How Do We Deal with Errors?* as a table mapping each paper failure to its pattern
name. **(D2-3 has since split the compressed slide into three, one flow each.)** The notation (boundary bar, numbered steps, red dashed = paper, trays, files) had **never been
stated**; it is now, because delegates draw in it within the hour. The error slide deliberately uses the
same words as the exercise's **failure cards**, so round 3 is recall, not invention.

**Cuts (−4 net).** *SOA — Faults Propagate* — Day 1 §1 owns fault propagation, and the idea returns in D
as the thing **Bulkheads** fix, where it does work instead of repeating. *Two Axes — Discrete/Series and
Skinny/Fat* — Day 2 §1 owns it now. *Dataflow — Packets* merged into *Nodes, Ports and Firing*. *FBP —
Node Lifetime* and *FBP — Capacity* merged into *Flow-Based Programming*. *Backpressure* + *Load-Shedding*
merged into one decision slide, **When the Pipe Fills**. Two of the four section markers dropped.

**Promoted.** *FBP — Where Do Lookups Live?* — three substantive diagrams (the lookup-port "walk of
shame", the *Build Lookup* pre-cache node) were buried under a heading about buffers. It is the direct
graph-shaped restatement of §1 *Reference Data*: on-demand vs. in-advance, and the CAP cost of each.
*Putting Reactive Together* also absorbed its own three orphaned images — circuit breaker, and
supervisor/scale-out — which were never taught.

**The three Day 1 debts are paid** — all three were listed here and are now in the outline:

1. ✅ *The Reactive Manifesto* lands as **recognition**: Resilient is Day 1's *robust*; *amenable to
   change* is Day 1's *easy to change* in the manifesto's own words; Elastic and Responsive are the two
   Day 1 had no names for. Callout: **two properties, one mechanism — somebody wrote it down in 2014.**
2. ✅ *Microservices Are Reactive Architectures* now calls back explicitly to Day 1 §1 *Easy to Change —
   Independent Deployability*: **"Day 1 called independent deployability the whole prize. This is how you
   stop giving it back."**
3. ✅ *Reactive Traits — Value, Form, Means* is attributed on the slide as **Bonér's gloss, not manifesto
   text**. Flagged in its notes as the most cuttable slide in the movement if Ian would rather not carry
   someone else's reading.

**Open item for the Process Automation review:** the **Josuttis quote** is now a callout on §2 *SOA Is OO
at Macro Scale* (where it is the yardstick Feature Envy fails against) **and** a standalone opening slide
of Process Automation. One of the two has to go.
| 2 | **Paper Flow** exercise | 9 | ✅ **run-of-show resettled (D2-4 / D2-7)** — two blocks + a closing round, ~100 min; §7 rewritten | ☐ Guest Cycle replacement; `Departure.drawio` | ☐ restructure deck + wire into README |
| 3 | **Process Automation** | **37** | ✅ 50 → 37 (D2-10); opens on *their* model; pizza → hotel | ☐ ~12 BPMN redraws + reference card | ☐ |
| 3a | · front half — notation to choreography | 22 | ✅ 28 → 22; legends 5→2, three *What is X?* merges | | |
| 3b | · back half — durable execution | 15 | ✅ 22 → 15; four `(Fault)` → one table; 2 illustrations absorbed | | |
| 4 | Putting It Together | 6 | ✅ reviewed with D2-10 — kept whole, 4 annotated flows + recap | ☐ | ☐ |
| 5 | Next Steps | **7** | ✅ +2 pointer slides (D2-1); reviewed with D2-10 | ☐ | ☐ |

**The balance problem is closed.** D1-9 took 19 entries off Day 2 but took nothing off Process
Automation; D2-3…D2-8 then added 6 back to §1, leaving Process Automation at **52% of the day** (50 of
97), entirely lecture, and owing the exercise 25 minutes. **D2-10 cut it to 37 of 84 — 44%** — and the 13
entries removed are worth roughly the 25 minutes owed. §1 is now the larger half of the day by teaching
time, which is the right way round: it is the half with the exercise in it.

---

## 6. The AsyncAPI handout

Source: `/Users/ian.cooper/Google Drive/My Drive/Presentations/AsyncAPI/Managing-AsyncAPIs-QCon-2026.pptx`
(43 slides). Extracted text: `session-work/qcon-asyncapi.txt`.

It is a **superset** of the old course §5 and a better treatment — §5 was an inventory, the QCon deck
has an argument. It opens on **The ABCs of Endpoints** (Address + Binding + Contract), the same frame
§5 used, then runs three pillars:

- **Discovery** — finding producers / finding consumers, prior art (OpenAPI, GraphQL, gRPC), AsyncAPI,
  xRegistry, CloudEvents (required/optional attributes, runtime discovery, binary vs. structured
  bindings), tooling (EventCatalog, Backstage, AsyncAPI Studio, VS Code extension).
- **Governance** — contract coupling as an Open Host Service, JSON Schema vs. Avro vs. Protobuf, schema
  registries, compatibility modes (backward / forward / full / none), safe vs. breaking evolution.
- **Provisioning** — spec-driven vs. TicketOps, code generation, schema-registration automation,
  infrastructure from bindings, documentation generation.

…then *Bringing It Together*, the **MeX at Just Eat Takeaway** case study (2,048 message schemas, 22K+
commits/year, AWS + Confluent Cloud, Marmot data catalog, Pulumi), and an honest *what's still hard*.

**Held back from the handout — still taught.** Postel's Law, Tolerant Reader, additive change, breaking
change. That is **design** material with real decisions in it — it answers *how do I change a message I
have already published*, which is a message-design question, not a tooling question. Now `## Versioning`
in `DayTwo.md`. The QCon deck's *Schema Evolution* slide covers the registry-enforced side but not the
tolerant-reader argument.

☐ **Handout work:** the QCon deck is a 40-minute conference narrative. As a takeaway it wants a
one-page index up front so it reads as a reference rather than a talk.

---

## 7. Paper Flow — the Day 2 exercise

> **Run-of-show resettled with Ian, 2026-08-28 (D2-4 / D2-7).** The exercise no longer runs as one block
> after the section — it runs **inside** it, in two blocks and a closing round, hooked to the two worked
> examples. The table below is the current design. Everything else here — the domain, the notation, the
> see-one/do-one split, the failure cards, the materials list and the build TODO — is unchanged.

**It already exists.** `exercises/Paper Flow.pptx` is tracked, 9 slides, and is **not** referenced from
`exercises/README DAY TWO.md` — built but never wired into the running order. Extract:
`session-work/paperflow.txt`, images at `session-work/imgs/paperflow-sNNN-M.png`.

### What is already there — do not rebuild it

- **Domain: the hotel guest cycle** — Pre-Arrival, Arrival, Occupancy, Departure, plus Hotel Onboarding.
- **A consistent visual language, and it is ours.** Desks drawn as boxes with an **in-tray and an
  out-tray**; a heavy vertical bar for the **organisational boundary**; numbered steps; red dashed
  arrows for paper movement; solid arrows for phone/fax channels; folders for filed state.
- **Step numbering — settled with Ian 2026-09-02.** **One global ascending sequence per flow, no repeats,
  no gaps**, counting every numbered marker in the order the arrows run — *not* per participant, and *not*
  reused across a boundary to imply concurrency. Where two things genuinely happen at once, show it
  **structurally** (one step branching to two), because "same number = same step" is the only rule a
  delegate can apply without being told. This was already the house norm: **6 of the 8 flows were
  clean**; see the survey below.
- **Four worked reference flows** — Hotel Onboarding (s005), Pre-Arrival (s006), Arrival (s007),
  Occupancy (s008). Every hand-off annotated *Put X in Outbox* / *Take X from Inbox*.
- **Departure deliberately not drawn** — s004 sets it as the delegate task: *"Departure is how I get my
  bill. Show how the flow of bills reaches my file."*
- **The framing, which is the best thing in the deck:** paper flow → partition the system → Team
  Topologies **fracture planes** → they fall on hand-offs, inbox to outbox →

  ▎ *"ACID transactions take place at a desk; BASE takes place across desks."*
- **A closing task (s009):** take one step and re-express it in FBP — information packets, nodes, ports,
  where the lookups are, where state is stored, which messaging patterns.

### Settled with Ian (2026-08-27)

- **In-person only.** No remote fallback; the design assumes a room with tables.
- **"See one, do one."** The *taught* worked example is **Just Paper Takeaway**; the *exercise* is
  **Just Paper Hotels — the Guest Flow**.
- **~75 minutes** — what Managing Asynchronous APIs used to take, so the swap is time-neutral.

### The resources already support the arc

The two families are **the same diagram with different nouns**, deliberately: the takeaway flows say
*"Use Just Paper Takeaway"*, the hotel flows *"Use Just Paper Hotels"*. Restaurant Onboarding and Hotel
Onboarding are structurally identical — Restaurant Owner / Sales Team / Fax Operator / Chef / Catalogue
Maker against Hotel Manager / Sales Team / Fax Operator / Concierge / Catalogue Maker.

| | **See one** — Just Paper Takeaway | **Do one** — Just Paper Hotels |
|---|---|---|
| paper flow | Restaurant Onboarding, Customer Order, Order Placement, Order Confirmation | Hotel Onboarding, Pre-Arrival, Arrival, Occupancy — **Departure not drawn** |
| error variant | Restaurant Onboarding Errors, Customer Order Errors, Order Placement Errors | **none — delegates produce it** |
| FBP re-expression | FBP Onboard Restaurant, FBP Order Food, FBP Order Placement, FBP Order Food Failure | **none — delegates produce it** |
| also available | Event Storming (Phase I/II) and Promises variants of each | — |

So delegates are shown three artefacts per flow and asked to produce the same three for theirs.

The existing error diagrams already teach the failure vocabulary in this notation — *"Request goes
missing"*, *"Make a carbon copy of the request"*, *"File the copy of the request"*, *"Resend"*, *"If no
receipt, retry sending fax"*. **The failure cards use that language**, not a parallel one: the carbon
copy *is* the outbox, the resend *is* the retry.

### Run-of-show — ~100 min, in three placements

**Settled with Ian, 2026-08-28.** Two ~45-minute blocks plus a ~10-minute closing round, each placed
immediately after the material it depends on, inside `## Flow and Reactive Programming`:

| block | where it sits in Day 2 §1 | min |
|---|---|---:|
| **1 — on paper** | end of **movement A**, after *How Do We Deal with Errors?* | ~45 |
| **2 — as a graph** | end of **movement C**, after the three FBP worked examples | ~45 |
| **round 4 — who is in charge?** | end of **movement D**, as the section's closing slide | ~10 |

**There is no round 0 any more.** It existed to recap material delivered an hour earlier; each block's
*see one* is now the slides immediately before it, so the recap is a pointer, not a retelling. *ACID
takes place at a desk; BASE takes place across desks* moves into **block 1's debrief**, where the
out-tray rule has just been enforced for forty minutes.

**Block 1 — on paper (~45 min).** Hand-off slide: *Now Do One — the Hotel, on Paper*.

| round | min | what happens |
|---|---:|---|
| **1 — Model it** | 20 | **One stage of the guest cycle per table** — Onboarding, Pre-Arrival, Arrival, Occupancy, Departure. Hard rule: **every hand-off goes through an out-tray and an in-tray**, no shouting across desks. That rule is what makes the fracture planes visible. |
| **2 — Run it** | 10 | *Execute* the model with cards, one person per desk. Missing messages and unstated assumptions surface within two minutes. Fix the model in pen. |
| **3 — Break it** | 10 | Deal 2–3 failure cards per table. Tables draw the **error variant** of their flow — the second artefact. The vocabulary is *How Do We Deal with Errors?*, which they saw ten minutes ago. |
| **Debrief** | 5 | Reveal the worked flow for each table's stage — four exist, **Departure does not**, so it is the collective piece. Land *ACID at a desk, BASE across desks*. |

**Block 2 — as a graph (~45 min).** Hand-off slide: *Now Do One — the Hotel, as a Graph*.

| round | min | what happens |
|---|---:|---|
| **5 — Re-express it** | 25 | Redraw your own flow from block 1 in FBP: information packets, nodes, ports. Where do the lookups live? Where is state stored? Which arcs must survive a crash? Same domain, new notation — that is the whole task. |
| **6 — Join up** | 10 | Tables connect their graphs into one network, as *Worked Example — the Order Flow in FBP* does for the takeaway. |
| **Debrief** | 10 | The hand-offs *between* tables are the largest fracture planes of all. Close on: you have drawn a distributed system, and nobody has said the word yet. |

**Round 4 — who is in charge? (~10 min).** Slide: *So Who Is in Charge?*, the section's last.

Re-run **your block 1 flow with a conductor** holding a routing slip (orchestration), then **with none**,
each desk acting on its in-tray (choreography). Compare: where did knowledge of the whole process live?
Who had to change when a step was added? It stays here, an hour after block 1, because its payoff is
**Process Automation**, which starts on the next slide — and Day 1 §1 *Collaboration — Orchestration and
Choreography* promised the room would feel the difference before either word was defined.

**Unchanged:** delegates must **not** meet BPMN before any of this. They invent a notation; Process
Automation formalises it.

**The cost.** ~100 minutes against the ~75 budgeted. **The 25 came out of Process Automation**, which
D2-10 cut from 50 entries to 37 — roughly the right amount of time, and it was over-long by every other
measure too. Settled 2026-08-29.

### Failure cards

| card | what it teaches |
|---|---|
| *The request goes missing* | timeout, retry, In-Out-Retry — as in Restaurant Onboarding Errors |
| *Make a carbon copy before you send, and file it* | the **outbox**; the pattern the deck already draws |
| *No receipt came back — resend the fax* | at-least-once, and therefore duplicates downstream |
| *This document was delivered twice* | idempotency, de-duplication, the Inbox pattern |
| *The night porter is on a break — this desk stops for two minutes* | store-and-forward; the in-tray absorbs the outage; availability traded for latency |
| *This desk goes home. Anything not written into a file is forgotten* | durable state — motivates Durable Execution directly |
| *The guest checks out early, mid-flow* | compensation, rollback, Tentative Operations |
| *Two clerks work the same in-tray* | competing consumers, and what happens to ordering |
| *This in-tray holds only three documents* | capacity and backpressure — the FBP callback |

### Materials — A4-printable, no special kit (it has to travel)

- Role cards: desk name + what this desk does.
- **Document cards** — half-A5, header strip (*type / correlation id / reply-to*) above a body area.
  The header strip is not decoration: it makes delegates use a correlation id without being told.
- In-tray / out-tray = two labelled A4 sheets per desk. A tray is a sheet you put paper on.
- Failure cards, printed and cut up.
- Flipchart/A2 sheet + markers per table.
- Optional, cheap: a **pinboard sheet** everyone may read but nobody may remove from — a topic/stream,
  against the in-tray's queue. Makes queue-vs-stream physical.

**Group size:** tables of 4–6, each table one stage of the cycle, running in parallel; facilitator
circulates dealing failures. Five tables covers the cycle; fewer, and drop stages from the middle,
keeping Onboarding and Departure.

### ☐ TODO — build

**Scope corrected by Ian, 2026-09-02.** These were previously parked behind "the deferred `exercises/`
phase". That was a misreading, and Ian corrected it: *"Day One includes some coding exercises for RMQ and
Kafka. Those are a separate task. But for Day Two, please do work on these."* So **the Paper Flow
exercise materials below are in scope now** — the guide, the brief, the printables, the `.pptx` rebuild
and the wiring. What stays deferred is the **coding** exercise material (`Quick-Start-RMQ`,
`Quick-Start-Kafka`, the pattern exercise decks and the two `README DAY *.md` code sections), which is
its own task.

*Working assumption, stated rather than asked:* `exercises/README DAY TWO.md` is today entirely about the
**Kafka/streams coding** exercises, so item 7 adds the Paper Flow to it without touching the code
sections. If the intent was for the Day 2 coding material to be in scope too, that is a bigger job and
worth saying so.

1. ✅ **Facilitator guide** — **built 2026-09-02**, `exercises/Paper-Flow-Facilitator-Guide.md`.
   Run-of-show, per-round circulating prompts, the failure-card deal (which card suits which flow, and
   why 3 and 4 go to the same table three minutes apart), the reveal order, and a cut-list for when it
   overruns.

   **It flags the round-numbering trap.** Round 4 runs **last**, after block 2 — it kept its number when
   it moved to the section's close, and **five presenter notes across `outlines/DayTwo.md` call it "round
   4"**, so renumbering would break all five. The guide states the running order as **1, 2, 3 → 5, 6 →
   4** and tells the facilitator to say *"who is in charge?"* in the room rather than a number.
2. ✅ **Delegate brief** — **built 2026-09-02**, `exercises/Paper-Flow-Delegate-Brief.md`. Scenario, the
   one rule, the notation in six glyphs, the per-stage assumption table taken from slide 4, and the three
   artefacts. It closes by naming what is deliberately withheld — *nobody is going to give you a standard
   notation; you will invent one, and later be shown the industry already agreed on something close* —
   because a delegate who notices the gap and is told it is deliberate stops trying to fill it.
3. ✅ **Printable materials** — **built 2026-09-02**, `exercises/Paper-Flow-Printables.md`, plus two
   drawn sheets where the design is the teaching and text would not do it:
   `resources/paper-document-card.png` (4-up on A4) and `resources/paper-tray-sheets.png` (2-up).

   Role cards carry **three** lines, not two — name, *what this desk does*, and **what it knows**, because
   the third line is the file and the file is what tables forget to draw. The document card's header strip
   (*type / correlation id / reply-to*) is left **deliberately unexplained**: a table hits the problem in
   round 2 — two documents in an in-tray, no way to tell which request one of them answers — and then you
   point at the box they left blank.

   `diagram.py` gained a `rule` element for this: a plain hairline, because `arrow` always draws a head
   and a line you write on must not have one.
4. ✅ **`resources/Departure.drawio`** — **built 2026-09-02**, `tools/paper_flow.py`. Reference answer for
   the one stage with no worked flow, on the **settled numbering rule** above. Five desk-turns, matching
   Occupancy's granularity: **1** guest asks to check out (solid — spoken, no paper) · **2** Front Desk
   takes the stay file, totals the invoices, puts the bill out · **3** guest settles and hands the key
   back · **4** Front Desk files the receipt and puts *room vacated* out · **5** Housekeeping returns the
   room to the Room List. Shape agreed with Ian before drawing.

   **Step 3 is where the numbering rule earns its keep.** Settling the bill and returning the key are one
   turn, so they are drawn **structurally** — one number branching to two arrows — not as two steps and
   not as a repeated number. The reference answer therefore demonstrates the rule it is asking delegates
   to follow.

   **It answers the question slide 4 actually asks** — *"show how the flow of bills reaches my file"* — by
   drawing the Guest Stay File with a **muted** stub above it captioned *filed here all week — that is
   Occupancy's flow*. Muted marks context from the previous stage; red is reserved for this flow's own
   paper. **Do NOT wire it into `outlines/DayTwo.md`** (plan §8 rule 9): it is revealed in block 1's
   debrief, and putting it in front of the room before the task destroys see-one/do-one.
5. ✅ **`Paper Flow.pptx` restructured — 2026-09-02.** 9 slides → 12, and the defect is fixed: the four
   hotel flows sat **immediately after the task slide**, so the deck put the answers in front of the room
   before the work.

   | | slide |
   |---:|---|
   | 1 | Paper Flow — Partitioning our System |
   | 2 | Create a Paper Flow |
   | 3 | **The Guest Cycle** — ours, replacing the setupmyhotel.com infographic |
   | 4 | **The notation key** — new here, and it belongs *before* the task |
   | 5 | Pick One Step and Model As A Paper Flow — **the task** |
   | 6 | **Debrief — the Worked Flows** — a divider whose body reads *"Do not show these until the tables have drawn their own"* |
   | 7–10 | Hotel Onboarding · Pre-Arrival · Arrival · Occupancy — **moved behind the task** |
   | 11 | **Departure** — new, and revealed last |
   | 12 | What Would This Look Like? — block 2's FBP task |

   **The takeaway *see one* is not duplicated here.** Movement A of `outlines/DayTwo.md` already walks the
   four takeaway flows and the montage, so this deck carries only what the main deck does not: the
   notation, the per-stage task detail, and the reveals.

   **Nor is the framing duplicated.** *Now Do One — the Hotel, on Paper*, *…as a Graph* and *So Who Is in
   Charge?* live in the main deck; this one is the exercise's own reference material, projected while the
   tables work.

   **Speaker notes were written for all six new or changed slides**, and they are instructions to the
   presenter — the reveal protocol, what to point at in each flow, and why Occupancy is shown immediately
   before Departure (its last step files the invoice into the very file Departure opens).
6. ✅ Replace the third-party *Guest Cycle* infographic (s003, setupmyhotel.com) — **built 2026-09-02**
   as `resources/paper-guest-cycle.png`, `tools/paper_flow.py`.

   **Ours says two things theirs does not, and both are load-bearing.** The original shows four peer
   stages; ours puts **Hotel Onboarding outside the loop** — the guest is not there for it, it is how a
   hotel is in the catalogue at all — because the exercise runs *five* tables against a *four*-stage
   cycle, and pretending Onboarding is a guest-cycle stage is the confusion that would cause. And the red
   idea: **every stage hands the next one a piece of paper**, drawn as the artefact between each pair —
   catalogue, booking, key, invoices, which slide 4 names verbatim. The cycle is a chain of hand-offs
   before anyone has drawn a desk, which is the exercise's whole thesis arriving one slide early.

   *Departure is the delegates' task* is deliberately **not** marked on it — that is slide 4's point, and
   a second red idea would cost this one its own.
7. ✅ Wired into `exercises/README DAY TWO.md` — **2026-09-02**. Its own section at the top, above the
   code exercises, saying plainly that this is the one Day 2 exercise that is **not code**, is in-person
   only, needs printing before the day, and must run **before** Process Automation. It was easy to miss
   precisely because there is nothing to clone. The README's coding sections are untouched.

**✅ Resolved 2026-09-02 — it was a slip, and Pre-Arrival is renumbered.** Ian: *"probably an error
derived from building this from the Just Paper Takeaway material."* Survey of all eight paper flows:

| flow | steps as found | verdict |
|---|---|---|
| Restaurant Onboarding · Order Placement · Order Confirmation · Hotel Onboarding · Occupancy | clean 1..n | ✅ |
| **Customer Order** | `1,1,2,3,4,5,6` | ✅ **left alone deliberately — not the same defect**, see below |
| **Arrival** | `1,2,3,4,5,5` | ✅ **fixed** — *Issue Key* 5 → 6; the key desk must take the request before it can issue the key |
| **Pre-Arrival Guest Flow** | `1,2,4,4,5,5,6,6,7,7,8` — `3` absent, four values doubled | ✅ **renumbered 1..11** |

The concurrency reading was tested and fails: under it a shared number means "at the same time", but the
old `6` paired the agency *taking from an inbox* with the hotel *putting into an outbox* — which the
notation's own hard rule makes strictly sequential. The new order was derived from the **arrow graph**
in the file, not from position on the page.

**✅ The renders are consistent again, without needing draw.io.** `tools/repatch_steps.py` repaints just
the step numbers of a paper-flow PNG from its `.drawio`: it finds the blue `#3333FF` glyph clusters,
matches each to a numbered cell by position, paints the old glyph out and redraws the new value in
**Helvetica** — draw.io's own default face, which librsvg *can* reach here — at the same centre, size and
colour. Nothing else in the image is touched, and a real draw.io export would supersede it and agree.
`bpmn-your-flow-side-by-side` was rebuilt after, since it embeds the render.

**Why `Customer Order` was left alone.** Its two `1`s are not a slip: they are **the same artefact — the
New Catalogue — held on both sides of the boundary**, one copy each for the customer and the order taker.
That is consistent with the rule (*same number = same step*), and it is load-bearing for the slide's own
*"Eventual Consistency?"* callout — *sometimes customers have an out-of-date catalogue, so we validate
their order against our latest one*. Renumbering them would make the catalogue read as two different
documents and break that point. **Left as-is on purpose; raise it with Ian if it ever looks wrong.**

### Knock-on: Process Automation moves to the hotel

**✅ Decided 2026-08-27, confirmed and executed 2026-08-29 as part of D2-10 (§9).** The mapping below is
what was applied; the outline entries carry `☐ REDRAW (hotel)` markers for Phase 2.

Day 2 then runs on one domain: takeaway is the *taught* example, hotel is what delegates *do*, and
Process Automation formalises **their** model in BPMN rather than a third unrelated domain.

*Scope — ~11 entries mention pizza:* six **Pizza Example** slides (BPMN Orchestration ×3 pools, Pools
and Lanes, Pizza Shop Collaboration, BPMN Choreography); four **workflow-pattern** examples (Browse
Pizzas → Add Pizza to Basket; Cook Pizza + Assign Courier, twice; Pizza Received / Eat Pizza); the
Orchestration vs. Choreography summary row; and *Putting It Together*'s "fax/pizza workflow" marker.

*The mapping is already in the paper flow.* **Pre-Arrival** has exactly three participants, which
become the three pools:

| pizza pool | hotel pool | lanes |
|---|---|---|
| Customer | **Guest** (Tourist) | — |
| Pizza Shop | **Just Paper Hotels** (the agency) | Booking Team, Fax Operator |
| Courier | **The Hotel** | Concierge, Front Desk |

That is the same flow delegates model in round 1, so the section becomes *here is your model in the
standard notation*.

*Cost check:* the pizza BPMN family has **no editable source**, so it is redraw-or-redraw. But
`resources/` holds editable BPMN drawio for the adjacent food-ordering domain — `BPMN Ordering
Flow.drawio`, `BPMN Ordering Flow Pools.drawio`, `Shopping Flow.drawio`, `Shopping Flow with
Pools.drawio`, `Shopping Flow As Sequence.drawio` — different diagrams, but a starting structure rather
than a blank canvas.

---

## 8. Phase 2 — images

### Required so far

1–4. **✅ The grids — built 2026-09-02**, `tools/coupling_grids.py`. **Ian: *"Let's draw all the others
   too."*** `grid-coupling` (§2) · `grid-integration-styles` (§3) · `grid-exchange-patterns` (§5
   *Choosing an Exchange Pattern*) · `grid-exchange-2x2` (§5 *The Four Exchange Patterns*).

   **The first three are literally one drawing.** `_frame()` draws the axes; the three figures differ only
   in what is plotted on them. The outline demands exactly that — *"reuse the same grid artwork so the
   call-back is visual, not just verbal"* — and the §5 presenter note says delegates should be able to
   draw it from memory by the end of the day. Edit the frame and all three move together.

   **Two judgements worth checking.** On §3, **Messaging is drawn as a span, not a point**, because the
   table's entry for it is *your choice*; that is the difference between it and File Transfer, which
   lands in the same cell and cannot move out of it, and the slide's closing callout is exactly that.
   On §5, the four decoupled patterns stack in the **Control** column while Out-Only sits out at **Data**,
   which follows the slide's own table — *the event schema* is the loosest thing there.

   **`grid-exchange-2x2` is deliberately not the same drawing**: it is a definition, not a plot. Its red
   is spent on *In and Out are named from the provider's side*, which is the one thing the room gets
   backwards — and the axis labels are useless to anyone holding the direction the wrong way round.
5. **✅ 12 EIP figure replacements** (Day 1 §4 and §6.2) — **built 2026-09-01**, drawn to `styles.md` and
   linked into the outline. Was 20; the **8 routing figures left with §4.6** to the handout (§10), and
   *Content Enricher* stayed and was redrawn with the rest. Whether the handout carries its own artwork or
   cites the originals is still a handout-build decision. `tools/eip_figures.py` holds all 12 as one
   script — regenerate the set with `python3 tools/eip_figures.py`. **No Hohpe & Woolf figure remains in
   either outline.**
6. **✅ The 2 If-Later diagrams — built 2026-09-02**, `tools/if_later.py`. **The last unbuilt drawing in
   §8.** `if-later-stream` and `if-later-queue`, Day 1 §6.3.

   **They are a pair, and they contrast through red** — the convention the 12 EIP figures set. Both
   slides describe the same trick (a versioned Summary Event means a later message supersedes an earlier
   one) but spend it on different problems, so each figure reds the mechanism *its own* slide introduces:
   **stream** reds the **discard**, **queue** reds the **read-past**. The wrong way round would make them
   look like one picture drawn twice, which is what the section is trying not to be.

   **Read order is drawn, not implied.** Both lay the envelopes out left to right in the order the
   consumer takes them and say so on the figure, because the natural EIP reading — nearest the consumer
   is next — gives the opposite answer, and which message was seen when is the entire point of both
   slides.

   **Found while building: `diagram.py` now warns on a missing glyph.** `12345 → v3` rendered the arrow
   as a hollow `.notdef` box — invisible in the source, visible only in the PNG, exactly the class of
   defect rule 2 exists for. The outliner now prints the face, the character and the codepoint at build
   time. **Caveat has no arrows and no maths**; a sweep of all 45 figures found that one and nothing
   else.
6a. **Day 2 §2 — three items. (a) and (c) built 2026-09-02**; `tools/paper_flow.py` holds them.

   (a) **✅ The notation key** — `resources/paper-notation-key.png`. A legend for every glyph the slide
   teaches, plus the out-tray-to-in-tray rule drawn as two desks, which is the red idea. Hand-drawn
   register (unlike the BPMN family): delegates reproduce this with a pen within the hour, so it has to
   look like something a person could draw. Sized to stand alone as the exercise handout.

   **Found while building it: `resources/Paper Office.drawio` (2021, editable) is already a partial
   notation key** — phone / inbox / outbox / fax / chair / desk, plus Call Taker / Worker / Fax Operator
   role cards. **It is not linked from any outline.** It does not cover the three things this slide leans
   on — the **file**, the **boundary bar**, and **red-dashed vs. solid arrows** — so the new key is a
   build, not a relink; but its glyph vocabulary was matched deliberately, so the two read as one hand.
   **`Paper Office` belongs with the Paper Flow exercise materials (§7), not on this slide** — it defines
   roles, which this slide does not teach. Place it there when §7's materials are built.

   (b) **✅ The order wheel — it was already in the deck. 2026-09-02.**
   `session-work/imgs/day2-s063-1.jpg` → `resources/photo-order-wheel.jpg`: a kitchen order wheel with
   tickets clipped round the rim and one being clipped on, which is the slide's sentence exactly.

   **This was a wrong blocker, and it is the third of the same kind.** *"The only one of the three
   physical devices with no image in the deck, and not something we can produce"* was never checked
   against the extracted masters — it put work on Ian's desk that was never his, and he is the one who
   asked *"any reason why you can't … use the existing picture?"* Rule 4 of the hand-off exists for
   precisely this and was not applied. **The `session-work/imgs/` set is 215 images and is not searchable
   by filename — the photos are `dayN-sNNN-M`, so you have to look at them.**

   **Found in the same sweep, all unlinked and all worth knowing about:** a **1984 OE Division routing
   sheet** (`day2-s056-1`) — a real routing slip, for the slide whose note says *"this is literally the
   conductor's routing slip"*; an **interdepartment delivery envelope** with its ruled been-to list
   (`day2-s053-1`); a **mail cart** (`day2-s054-2`), which is the facilitator guide's spare *Post Room*
   role; a **fax machine** (`day2-s057-1`); the **Fax Call Log** (`day2-s069-1`); and **mailroom
   pigeonholes** (`day2-s055-1`).

   (d) **✅ The carbon-copy pad** — same sweep. `day2-s067-1.jpg` → `resources/photo-carbon-copy-pad.jpg`,
   a multi-part NCR form with the top sheet peeled back to show the copies beneath.

   (e) **✅ The licensing problem is drawn out. 2026-09-02.** The *office desk with overflowing IN and OUT
   trays* photo (`day2-s054-1`, Day 2 §2) was a **watermarked Getty / Comstock comp** — watermark, agency
   name and asset id all visible in the image that was in the deck, the same class of problem as the
   Hohpe & Woolf figures and the setupmyhotel infographic. Ian: *"Let's draw it."*
   `resources/paper-the-desk.png`.

   **It carries no red note, deliberately.** It sits beside two photographs as one of three establishing
   images at the top of the day, and it is not making an argument — the section opener does that. The
   BPMN workflow-pattern figures carry none for the same reason. The one editorial choice in it is that
   **the in-tray overflows and the out-tray does not**, which is true and is the reason a queue is a
   place rather than an event.

   (c) **✅ The *Worked Flows* montage** — `resources/paper-worked-flows-montage.png`. Composition, not
   drawing: the four takeaway flows embedded 2×2 as data URIs, so the montage does not depend on the
   sources staying put. Note the naming mismatch it exposes — *Customer Order.drawio* is captioned
   *"Order Taking"* inside the artwork. The outline's name won; the source was left alone.
7. **✅ `resources/Departure.drawio` and the *Guest Cycle* replacement — built 2026-09-02.** Both live in
   `tools/paper_flow.py`; §7's TODO 4 and 6 carry the design reasoning. Both target
   **`exercises/Paper Flow.pptx`**, not `outlines/DayTwo.md` — Departure is a facilitator reference
   answer and must not be wired into the outline at all (rule 9); the Guest Cycle map is slide 3.

   **`Departure` follows the bare-`.png` convention** the other four hotel flows use
   (`Arrival.png`, not `Arrival.drawio.png`), so the five stages sit together in `resources/`.

   **A new glyph, `doc`.** `tools/diagram.py` gained a bare sheet of paper — the artefact in flight,
   before it lands in a tray or a file. The tray already drew one *in* its tray; `doc` is the same sheet
   on its own, which is what the guest cycle's hand-offs are made of.
7a. **✅ The coupling scale with a process boundary across it — built 2026-09-02**,
   `resources/coupling-scale-boundary.png`.

   **Drawn vertically, and that is the whole point.** Myers' scale runs top to bottom, tightest first,
   with the boundary as a horizontal line across it — so *above the line* and *below the line* are
   literal, and the two kinds of coupling you can no longer have are literally out of reach. The flat
   left-to-right scale this replaces (s27) cannot show a boundary taking anything off the table, which is
   what the section is for.
8. **✅ All 13 BPMN drawings — built 2026-09-01.** `tools/bpmn_hotel.py` holds them; regenerate with
   `python3 tools/bpmn_hotel.py`. Covers the five workflow-pattern examples,
   the three orchestration pools (Guest / Just Paper Hotels / The Hotel), *Pools and Lanes*, the
   collaboration, the choreography and the compensation fragment. Step names were taken from the
   delegates' own `resources/Pre-Arrival Guest Flow.drawio`, so the BPMN says back to the room what it
   wrote on paper. None of the pizza originals had an editable source, so nothing was lost.

   **✅ Including the side-by-side** (*Your Flow, in the Standard Notation*), which embeds the delegates'
   own `resources/Pre-Arrival Guest Flow.png` beside a compact BPMN collaboration. It is the only Phase 2
   figure that embeds an existing artefact rather than drawing it, and it has to be: the slide's promise
   is *you drew this an hour ago*, so the left half must be the thing the room actually made. The image is
   embedded as a data URI in both outputs, so neither file depends on the original staying put.

   **Filename trap, cost an hour.** This figure was first recorded as blocked because no
   `Pre-Arrival Guest Flow.drawio.png` exists — the convention most of `resources/` uses. The render is at
   **`Pre-Arrival Guest Flow.png`**, the bare form. `resources/` uses both conventions; check for both
   before concluding a source is missing.

   **⚑ Watch at rehearsal:** in the composite the paper half is ~4.3in wide on a 16:9 slide, so its
   labels are small. The presenter note already says to show the paper version **alone first**, then
   reveal the BPMN — so the composite is the recognition moment, not the reading one. If it does not carry
   the room, the fix is to split it across two slides rather than to enlarge it.

   **☐ And one layout job:** the BPMN **delegate reference card**, one A4 side carrying the task / event /
   gateway legends, whose three drawio sources already exist. Its own outline note calls it a Phase 3
   item, so it stays there.

9. **✅ The 4 Integration Styles figures — built 2026-09-07.** `tools/integration_styles.py`;
   `style-file-transfer`, `style-shared-database`, `style-rpc`, `style-messaging`, Day 1 §3, replacing the
   2021 exports s32–s35. **This closes class C** of the annotation survey below.

   **They share a stage, because the section is a scoring and not a tour.** `_frame()` draws the same set
   every time — the process boundary down the middle, a process container either side — and each figure
   only puts its own apparatus on it. That is the same device as `coupling_grids._frame()`, and for the
   same reason: §3 does not compare four mechanisms, it asks all four the same question and then plots the
   answers on §2's grid. Four differently-composed drawings would make the reader re-learn the layout
   before they could compare anything.

   **The boundary is drawn, not implied**, and it is §2's line turned on its side — `coupling-scale-boundary`
   runs it across Myers' scale to take Content and Common off the table; here it runs between two
   processes. It is what makes Shared Database an argument rather than an illustration: its cylinder is
   the only apparatus a *reader* on the far side reaches through, and the rule runs visibly through it.

   **The reds are the two axes.** File Transfer reds the file, Shared Database the schema, Messaging the
   message — three figures reddening what the two sides agree *about*. RPC reds the **clock**, because it
   is the only one that also loses on *when*. So the family's red, read across four slides, is the grid the
   section ends on. RPC's control coupling is carried in carbon instead, on the arrow label
   `PlaceOrder(order)` and the comment under it, which is where it actually lives.

   **Messaging is deliberately File Transfer's drawing again** — same two boxes in the same places — because
   the two land in the same cell of the grid and *Why Messaging* is about to say so. What differs is the
   three lines under the channel: a command, a whole-entity event, or only what the receiver needs, each
   with the coupling it buys. That is the section's punchline, and it is the one style where the drawing
   has a choice in it.

   **The 2021 originals each carried three paragraphs of blue commentary** because the slides underneath
   them were bare. D1-7 rewrote those slides to carry the argument as bullets, so the figures do not repeat
   it; what the drawings keep is only what a picture can say better than a line of text.

   **What only showed up in the PNG**, per rule 2: a 2.6pt ink rule down the middle strikes through *any*
   centred label, so every mechanism caption had to move below the rule's end and `_frame(bb=)` became a
   per-figure decision; `_mid()` takes the middle *segment* of a polyline, so Shared Database's `reads`
   label sat on the vertical run while `writes` sat on the horizontal one, and the pair stopped mirroring
   until a redundant waypoint was added purely to move the label; and `writes a message` landed inside the
   pipe's mouth ellipse — the same defect run 2 hit — and was shortened to `writes it`.

10. **✅ One 18pt floor, and what the floor turned out not to guarantee — 2026-09-07.** Ian, on the
   Integration Styles sheet: *"The images and their text are only using the top half of the slide, and we
   could make the text larger for the comments than it is at present, for readability."*

   **The immediate fix is one floor.** `CONTENT_PT` and `ASIDE_PT` were 17 and 16; both are **18**, the
   same number as the deck's body floor. Content and commentary are now the same size and only the
   *colour* separates them — which is what §Settled 7 decided in principle and then only half applied.
   The old pair said "secondary" twice, in size and in hue, and charged for it twice.

   **The finding underneath it is bigger, and it is the fifth of the same shape.** The floor is expressed
   in **canvas units**, and a figure is scaled to fit its slide — so what "18pt" means across a room
   depends entirely on how wide the canvas is. Measured across the nine families:

   | family | canvas width | what 18pt reads as, full slide width |
   |---|---:|---:|
   | `eip_figures` | 460–600 | 27–35 pt |
   | `coupling_grids` | 980–1060 | 15–16 pt |
   | `integration_styles` (was 1200) | 1000 | 16 pt |
   | `queues_streams` | 1080–1360 | 12–15 pt |
   | `flow_reactive` | 1060–1300 | 12–15 pt |

   **A three-fold spread under one number.** `styles.md` claims *a diagram label is no more legible than
   a bullet*, and only the small-canvas families have ever met it. At full slide width a label reads at
   roughly `18 × 890 / w` real points, so **w ≈ 890 is where the diagram floor meets the 18pt body
   floor**, and everything wider is under it.

   **Aspect is the second half of it.** A 16:9 slide leaves about 2.2 : 1 of usable area. A figure wider
   than that is fitted by width; anything squarer is fitted by *height*, and every label shrinks again.
   So adding a row of content to a wide figure costs legibility twice. That is why the four Integration
   Styles figures went **1200 → 1000 wide** rather than simply gaining a bigger number: the width change
   is what took their commentary from ~12 real points to ~16.

   **☐ Not swept.** Narrowing `queues_streams` and `flow_reactive` to ~900 would re-lay out 36 figures,
   including ones on sheets Ian has already approved. It is a real job and a real decision, and it is
   his. Recorded here rather than done.

   **The sweep that *was* done cost three fixes and found four defects** — `eip-publish-subscribe`'s
   subscriber boxes had been cut to fit 15pt text; `eip-polling-consumer` and `eip-event-driven-consumer`
   had no room between pipe and pump for a label at 18pt and went 460 → 580 wide; and three foot comments
   had grown off their canvases, one of which (`bpmn-hotel-p3-join`) was already off before the sweep.
   **`lint_figures.py` gained two checks for exactly those classes** — free notes against the canvas
   edges, and edge labels against container borders — and the second immediately found a third
   pre-existing defect in `flow-soa-service`. Neither class had ever been checked.

11. **✅ File Transfer and Messaging take back the "out of the box" argument — 2026-09-07.** Ian:
   *"Messaging repeats File Transfer's composition, but the fix is asking what does the locking,
   partitioning etc. However, we have lost some of that information, which we probably should take back,
   to improve the idea that messaging simply provides 'out of the box' solutions to many file transfer
   questions."*

   Both figures now end on the **same four questions in the same four columns**, and only the answers
   change: *none · you do · nothing says · you decide* against *the channel · the broker · an ack · poll,
   or be pushed*. `QUESTIONS` and `_strip()` are module-level so the two cannot drift, because the two
   strips being identical bar one row **is** the comparison.

   **This makes the repeated composition deliberate.** Two slides that look alike with one row of words
   different is a comparison; two slides that look alike for no reason is a mistake. Ian confirmed the
   boundary stays on all four in the same note, so the shared stage is settled.

   **It restores what the rewrite dropped.** The 2021 exports carried this in their blue commentary
   boxes — *"the consumer has to decide how often to poll"*, *"if there are multiple consumers, then the
   consumer needs to lock the file"* — and D1-7 moved that reasoning into the slides' bullets and out of
   the pictures. The bullets carry the *coupling* argument; nothing carried the *services* argument in
   picture form until now.

   **☐ One thing not done: Kafka.** Ian's aside — *"Kafka shows its file transfer origins clearly with
   offsets and records"* — is a genuinely good line, but §3 is nine slides before *Queues and Streams*
   and the section's own `#note:` already forbids naming Reactive early for the same reason. **It belongs
   in a presenter note on §4.5's Kafka material, as the call-back**, not on the §3 figure. Not written
   yet; do it when §4.5 is next touched.

   **The three coupling glosses came out of the Messaging figure to make room** — *a command is control
   coupled*, and so on. They restated the slide's own bullets word for word, which is the failure the
   2021 exports were full of, and `grid-integration-styles` already makes that point better by drawing
   Messaging as a span rather than a point.

12. **✅ The narrowing — done 2026-09-07.** Ian, answering item 10's open offer: *"We should review them
   as we already noted that the In/Out labels were too small."* **`queues_streams` (11) and
   `flow_reactive` (25) are compacted to 890 units** and their labels now read at **17–19 real points**
   against 12–15 before.

   **The reason he gave is the point.** `43ecdd7` had already raised `flow_reactive`'s port names to the
   floor and the file recorded that finding as closed — but the floor was in canvas units, so raising it
   never reached the room. **A finding closed against a floor that does not hold is not closed.** He
   remembered; we had not.

   **The mechanism is `Diagram.compact(target)`.** Measured first: there are almost no internal gaps to
   reclaim, and compressing the empty runs alone would have made six figures *wider*, so the shapes had
   to shrink. But the box labels had roughly 3× slack, so 35 of the 36 could reach 890 with no label
   outgrowing its shape. It scales the **geometry**, leaves the type alone, and crops. Three bounds:
   a shape may not go below its own label (`flow-fbp-component` stops at 950 for its `IP` packet); one
   long line of text does not scale at all, so `compact` **names it on stderr** rather than shrinking the
   drawing to nothing around it; and `K_FLOOR = 0.55`. Marks — lock, clock, tick, cross — are moved but
   not resized, because shrinking a mark is the same error as shrinking a label.

   **What it cost, and what that says about the linter.** Ten labels needed re-nudging, because `lx`/`ly`
   are text-space offsets that do not scale. Five notes needed more clearance, because a fixed gap
   between a note and a shape shrinks while the text does not. **`lint_figures.py` went from three checks
   to six** and found defects in four other families on the way — three arrow labels struck through by a
   vertical arrow in `bpmn_shopping`, `eip_figures`, `if_later` and `paper_flow`, **two of them on sheets
   Ian had already approved**. The new checks are `note-on-shape` (a note *across* a stroke — a note
   *inside* a shape is a technique, not a defect), `on-its-line`, `on-a-line` and `on-border`.

   **And one structural lesson: the compaction belongs in the family's `figure` decorator, not in
   `main()`.** With it in `main()`, `lint_figures.py` measured the geometry as written rather than as
   rendered, and a note lying across a hexagon was invisible for as long as the two disagreed.

   **☐ Still wide, and not swept.** `if_later` (1120, 14.3pt), `coupling_grids` (980–1060, 15–16pt) and
   `integration_styles` (1000, 16.1pt) are hand-drawn and could take the same treatment — 11 figures.
   `paper_flow` embeds rasters and feeds printables, and the BPMN pair is a different register at its own
   scale, so neither should be swept without a separate look. **Offer, do not assume.**
   — **✅ the 11 are done, item 13.**

13. **✅ The narrowing, finished — 2026-09-07.** Ian set the order: *"when we restart let's do the 11
   figures then class D."* `coupling_grids` (5), `integration_styles` (4) and `if_later` (2) now carry
   `TARGET_W = 890` and compact in their own `figure` decorator, exactly as item 12's two families do.
   **All five hand-drawn families are at 890 and read at 18 real points**; `grid-exchange-2x2` stops at
   876, bound by its own row glosses, which is `compact` doing what it is meant to do. The two BPMN
   families and `paper_flow` are untouched and still want a separate decision.

   **The recipe transferred with no surprises, and the warning in the hand-off was wrong about which
   figure would bind.** `integration_styles._strip()` was expected to be the constraint — four absolute
   columns at `COL_X` with unscalable question text between them — and it was not: the four columns are
   220 units apart and the longest answer is 100 wide, so 0.85 of the distance still leaves a gap.
   `COL_X` and the strip rule are untouched.

   **Three labels needed moving afterwards, and all three were the same defect item 12 names:** a fixed
   gap in canvas units, closing while the type stays put.
   - `style-rpc` — `PlaceOrder(order)` had `lx=-94` to clear the boundary rule at `MID`, and at 890 that
     pushed it onto the Stub it starts from. Now `-75`, mid-way between the two things it must clear.
     **`lint_figures.py` found this one**; the other two it cannot see, because neither check measures a
     label against a `rule`.
   - `grid-coupling` — *with a what-to-do flag*'s descenders came down through the 2.4pt *must we both be
     up?* rule. The point moved 268 → 248: **where a point sits inside a band carries nothing**, so
     height is free to spend and the label is not. It had been one unit clear at 1060, which is to say
     it was already wrong and the compaction only made it visible.
   - `grid-coupling` — *gRPC with a flat DTO* reached the Data column's own border, so it wraps to two
     lines. Every other plotted label already fits its column.

   **The linter's blind spot is now known and worth writing down: `note-on-shape` skips `rule`s**, so a
   label lying across a gridline, a boundary or an axis is invisible to it — which is precisely the
   defect a compaction produces on a figure whose structure *is* rules. On these five families, look at
   the PNG for the rules specifically.

14. **✅ Class D, and the end of Phase 2 drawing — 2026-09-07.** The last nine unannotated `#image:`
   lines. **Six became figures, two became links, and the ninth is the order-taking photograph**, which
   is class A and Ian's to export. **Day 1 is now fully annotated: 49 of 49.** Day 2 stands at 87 of 88.

   **`tools/app_shapes.py` — four figures, one new family.** §1's process-boundary pair and §4.3's
   task-queue pair. They are one family because they are the only Day 1 drawings that show an
   *application you could build* rather than a pattern, and they share `service()`: a dashed container,
   the application, and the store only it can reach.

   **The boundary vocabulary was already taught twice, so this family borrowed it rather than inventing
   a third.** `coupling-scale-boundary` draws it as an ink rule across Myers' scale;
   `integration_styles._frame()` as a vertical ink rule between two dashed containers. **Dashed box = a
   process, ink rule = the boundary.** §1 runs before §3 in the deck, so these two figures are where the
   room now meets the glyph and §3 reuses it without re-teaching it — which is the right way round, and
   was not true before.

   **§4.3 then says the opposite thing with the same vocabulary, deliberately.** `task-queue-shape` puts
   browser, web server, channel and three competing consumers inside **one** container over **one**
   database, because the slide's callout is *one team, one service, one queue — robustness without
   reorganising the company*. Drawing a boundary there would teach the room to cut a new service every
   time a request is slow, which is exactly what the callout denies. **The same glyphs arguing both ways
   is the point**; it is why the four are one script.

   **`eip-the-big-picture`** joins `eip_figures.py` as §4's opener. It is a composition over that
   family's own vocabulary and invents nothing: the 2021 marker also named a *channel adapter*, which is
   **not drawn**, because the deck never teaches the pattern and a shape on the map that no later slide
   picks up is a promise the section does not keep. It also carries §4's build order, because the slide's
   entire body is one sentence, and the message is opened into header and body **because §4.1's own
   slide has no picture at all**.

   **`tools/conversations.py` — one figure, and it names its own gap.** The marker asked for a stopwatch
   icon; the slide's callout is *a timeout does not tell you the request failed, it tells you that you do
   not know*, and an icon cannot say that. What says it is the three things still possible when the clock
   runs out, which is also why the next bullet demands idempotence. **Time runs down the page** — a
   vocabulary choice, not a register one; the lifelines are muted 1.1pt hairlines and deliberately
   nothing like the 2.6pt ink boundary.

   **Two findings came out of the sweep, both of them stale content nobody had re-read:**
   - **§Messaging Patterns' `#note` advertised a cut sub-topic.** Its build order listed **six**
     questions — the sixth *how do I process in stages?* — against §4's **five** sub-topics. §4.6
     Pipelines left for the routing handout (§10) and the note was never updated. Fixed, and the figure
     draws the five. *Counts in prose go stale silently.*
   - **§Conversations still shows three 2021 whole-slide exports** —
     `Practical Messaging - Day 2 - 2024 - 25/27/29.png`, complete with their old titles, red commentary
     boxes and a footer. They are *linked*, so they never appeared as work outstanding, and they are the
     last three pictures on Day 1 that are not ours. **`tools/conversations.py` is where their redraws
     would go. Offer, do not assume.**

   **And a defect in Ian's own code screenshot, which is his call and not ours.** See the item under
   *For Ian* below.

15. **⚑ For Ian — the `Handlers + Activity State Updates` code screenshot. Superseded by item 17, which
   is the fix he asked for; kept because it is what was found.** `day2-s152-1.png` had three things
   wrong with it, and the
   presenter note says *walk the transaction and the postbox on the code screenshot*:
   - both branches of the `if (canMake)` deposit **`OrderAccepted`**; the `else` presumably wants
     `OrderRejected`, and as drawn the slide teaches a bug;
   - the `catch` logs *"Exception thrown handling Add Greeting request"* and both `return`s call
     `base.HandleAsync(addGreeting, …)`, where `addGreeting` is not a parameter of this method — leftovers
     from a different sample, so it would not compile;
   - the `return` inside the `catch` makes `ClearOutboxAsync` unreachable on the failure path, which is
     arguably right but reads as an accident next to the second `return` below it.

   **Left linked at the time, because re-authoring code on a slide is a content decision.** Ian asked for
   it the same day; **item 17 is what that turned into**, and the answer was not a prettier picture — it
   was that code on a slide is *text*, and that no rendering saves a 39-line listing on a 16:9 slide.

16. **✅ The 2021 §Conversations exports are redrawn — 2026-09-07.** Ian asked for item 14's first
   finding. `Practical Messaging - Day 2 - 2024 - 25/27/29.png` are unlinked and
   **`conversation-messaging-or-eventing` replaces all three**. Day 1 falls 49 → **48** `#image:` lines,
   all linked.

   **Three images became one, and that is a legibility decision rather than a tidy-up.** Two figures side
   by side on a 16:9 slide are each fitted to about half its width, so an 890-unit canvas would read at
   **nine** real points instead of eighteen. **Splitting a figure across a slide halves its type** —
   the same arithmetic as item 10, applied to figure *count* rather than canvas width. `bpmn-the-six`
   made the same trade for the same reason.

   **One pair of participants, three exchanges down them.** The 2021 set drew the same two boxes three
   times on three slides, so the reader had to re-establish who was who before comparing anything. Here
   they are established once. **Requestor stays on the left in all three, including Out-Only** — it is
   tempting to swap the boxes so the eventing arrow still points right, and that would destroy the
   figure, because the claim is that *the arrow turns round* and an arrow only turns round against
   something that does not. Red is on the notification for the same reason.

   **`participants()` moved into the module**, so both figures draw the two boxes and their lifelines the
   same way. It is a pure extraction: `conversation-timeout` re-rendered byte-identical.

   **☐ A fourth 2021 export is sitting in `resources/` linked to nothing** —
   `Practical Messaging - Day 2 - 2024 - 34.png`, *Out-In (Solicit-Response)*. The **Out-In slide has no
   picture**, and Out-In is deliberately not on this figure, because *Messaging or Eventing?*'s own table
   does not list it. Whether that slide wants one is a separate question. The three replaced files are
   left in `resources/` rather than deleted — they are the 2021 originals, and unlinking them is
   reversible in a way that deleting is not.

17. **✅ Code on a slide is text, not a screenshot — 2026-09-07.** Ian asked for item 15. The fix turned
   out to be larger than the bugs, and the arithmetic is why.

   **A 39-line screenshot on a 16:9 slide reads at about seven points.** `day2-s152-1.png` is 2112×1674,
   an aspect of 1.26:1 against the roughly 2.2:1 a slide gives you, so it is fitted by **height** and
   uses about half the width. Item 10's rule, one step further: **aspect can cost more than width.** No
   amount of re-rendering fixes that — the only fix is fewer lines.

   **And `styles.md` had already settled the register**: *Plex Mono replaces Consolas for code*. So code
   belongs in the outline as **text**, where Phase 3 sets it at the body floor and it never gets scaled
   like a picture at all. Both `#image:` lines are now fenced ```` ```csharp ```` blocks; §1's outline
   conventions carry the new rule; Day 2 falls 88 → **86** `#image:` lines. The two copies added to
   `resources/` are removed, and the masters stay in `session-work/imgs/`.

   **⚑ Re-authoring the listings is a content change, and here is every edit, because Ian should be able
   to veto any of them:**
   - **`OrderAccepted` in the `else` branch → `OrderRejected`.** The original deposited the same message
     on both branches of `if (canMake)`. Unambiguous.
   - **`addGreeting` → `order`, and the log message with it.** The `catch` logged *"Exception thrown
     handling Add Greeting request"* and both `return`s called `base.HandleAsync(addGreeting, …)`, which
     is not a parameter of the method. Leftovers from another sample; it would not compile.
   - **The `catch` now rolls back and `throw`s** rather than returning down the handler pipeline. This is
     the one **judgement call**: the slide's own bullet is *relies on guaranteed delivery — store work
     for retry unless ack'd*, and a handler that swallows the exception and returns normally gets the
     message ack'd and the work lost. Returning was arguably a fourth bug; it is at least a
     contradiction of the bullet above it.
   - **`cancellationToken` → `ct`,** so the longest line fits a slide measure.
   - **Cut from 39 lines to 16** — the transaction, the state change, the deposit inside it, the commit,
     the rollback, and the outbox cleared outside. The `cookRequests` / `deliveryRequests` writes came
     out: they sat after the commit inside the `try` and are a different subject.
   - **State machine: `Init<DebitAccount>` on `queue:stock-check` → `Init<CheckStock>`.** A debit on a
     stock-check queue between `OnOrderSubmitted` and `PendingStock` is incoherent; the original's
     `// Calls debit` comment suggests it was pasted from a payments sample. **Least certain of these —
     if the flow really does debit there, the queue name is what is wrong instead.** Cut from 35 lines
     to 16.

   **Both presenter notes said *"on the code screenshot"* and have been rewritten**, because presenter
   notes ship to whoever delivers the course and would have pointed at something that no longer exists.

18. **⚑ "Compacted to 890" is not the same as "reads at 18", and 65 of 92 figures are under the floor.**
   Measured 2026-09-07, with `tools/reads_at.py`, which is committed so this is checkable rather than
   asserted. **This is the sixth finding's shape for the third time: a floor closed against a rule that
   only half held.**

   **The rule has two halves and the sweep only used one.** Item 9 gave the width half — a label reads at
   `size × 890 / w`. Item 10 gave the other half and it was never put into the target: **a 16:9 slide
   leaves about 2.2 : 1 of usable area, and a figure squarer than that is fitted by HEIGHT**, so the
   width it was drawn at stops mattering. The number that counts is

       reads_at  =  caveat-equivalent size  ×  890 / max(w, 2.2 × h)

   and 890 is only "the floor" for a figure that is already wider than 2.2:1. Every family swept to 890
   contains figures that are not.

   | family | figs | worst label | | family | figs | worst label |
   |---|---:|---:|---|---|---:|---:|
   | `eip_figures` | 13 | 16.1 pt | | `bpmn_hotel` | 13 | **8.7 pt** |
   | `coupling_grids` | 5 | 12.3 pt | | `bpmn_shopping` | 6 | 10.1 pt |
   | `if_later` | 2 | 14.9 pt | | `paper_flow` | 7 | **7.7 pt** |
   | `queues_streams` | 11 | 11.9 pt | | `flow_reactive` | 25 | 11.3 pt |
   | `integration_styles` | 4 | 13.4 pt | | `app_shapes` | 4 | 12.5 pt |
   | `conversations` | 2 | 14.1 pt | | | | |

   **The sweep was still worth doing** — `grid-coupling` was at 8.4 before it and is at 12.3 now, and Ian
   approved the result by eye. What is wrong is the *claim*, which this file and the hand-off both made:
   890 buys 18 points only for a wide figure.

   **☐ So the answer on the three unswept families is "not this way" — Ian, 2026-09-07: leave it if it
   does not make sense to fix.** Compacting them to 890 would help and would not be enough:
   `bpmn_shopping`'s worst goes 10.1 → about 15.5, `bpmn_hotel`'s 8.7 → about 12.1, and two `paper_flow`
   figures cannot move at all — `paper-worked-flows-montage` embeds rasters `compact` does not scale, and
   `paper-tray-sheets` is **0.70 : 1**, taller than it is wide, where width is not the variable in the
   first place. **The lever for a height-fitted figure is rows, not units**, and cutting rows is a content
   decision per figure rather than a sweep.

   **Run `python3 tools/reads_at.py` before saying a family is done.** `lint_figures.py` measures labels
   against shapes; this measures them against the room, and nothing else does.

### ✅ 19. `compact` targets the effective width, and the eight swept families were re-swept

**Ian, 2026-09-08, asked which scope:** *swept eight only* — change the rule, re-sweep the families that
were already claimed done, and leave `bpmn_hotel`, `bpmn_shopping` and `paper_flow` alone as he had
already said. **Done, and item 18's warning is now discharged for those eight.**

**`Diagram.compact(target)` now means the effective width**, `max(w, 2.2 × h)`, which is the number
`tools/reads_at.py` measures. The bisection predicate and the "cannot reach" diagnostic both moved with
it, and the diagnostic now tells the two failures apart: a **width-bound** figure names its longest label
and says wrap it; a **height-bound** one says *cut rows, not units*, because naming a label there would
send the next reader to fix the wrong thing.

**The result, measured, not asserted:**

| | before | after |
|---|---:|---:|
| figures under the 18pt floor | 65 of 92 | **33 of 93** |
| worst label in the swept eight | 11.3 pt | **14.1 pt** |
| figures in the swept eight at exactly 18.0 | — | **32 of 47** |
| `lint_figures.py` | clean | **clean** |

The 33 remaining are 15 in the swept eight — mostly 16–18 pt, bound by the label-fit clamp, which is the
honest floor — and 18 in the three families he asked us to leave. **A figure that lands short now is
short because its own type will not let it shrink further, not because the target was the wrong number.**

**⚑ What the harder compaction cost, and it is the number to expect next time.** `k` went from about 0.85
to about 0.6, and **lint went from clean to 19 findings in 11 figures** — every one a label that no longer
fitted a gap the geometry had closed around it. All 19 are fixed. Two more were invisible to lint and
found by eye on the PNGs. The four ways they were fixed, in the order to reach for them:

1. **Spend width on a height-fitted figure — it is free.** Once the target is `max(w, 2.2 × h)`, a figure
   squarer than 2.2:1 is bound by its height, so widening it costs *no legibility at all*. `task-queue-http`
   opened its Client→Web Server gap from 170 to 250 units, `qs-queue-tasks` moved its consumers 80 further
   out, `flow-soa-service` moved the Service 70 right and widened `operations` by 80. **Reach for this
   before shortening a label.**
2. **Nudge `lx` / `ly`, in post-compaction units.** They are text-space and do not scale, so they are the
   one thing that must be re-measured every time the target changes — `style-rpc`'s `PlaceOrder(order)`
   has now moved on all three sweeps (−94 → −75 → −60) and carries a comment saying so.
3. **Move a note away from the shape it had been sitting politely beside.** Five in `flow_reactive`: the
   gap shrank, the type did not.
4. **Fix the shape, where the shape was wrong.** See item 20.

### ✅ 20. A cylinder's label belongs in its body, not across its rim

Found by eye on `task-queue-http` after the re-sweep, and it was **never right** — the compaction only
made it visible, which is item 13's lesson again: *a compaction is a good detector of a layout that was
never right.*

`Diagram` centred every node label on the whole shape. A cylinder's interior starts **below its top
ellipse**, at `y + 2ry`, so a two-line label's first line ran straight through the rim. Three figures
were doing it: `task-queue-http`'s *progress / (a KV store)* and both `if_later` replicas.

**`lint_figures.py` cannot see this and still cannot.** It measures a label against its shape's *box*, and
a rim is not one — the same blind spot as `kind == "rule"`. **Look at the PNG.**

Fixed in `diagram.py`, so it holds for every cylinder ever drawn; `task-queue-http`'s went 92 → 124 tall
as well, because at the target its body was 35 units for 38 units of type. All eleven families rebuilt and
re-linted after the change.

### ✅ 21. Out-In has a picture, and it is a third `conversations` figure

**Ian, 2026-09-08: draw it** rather than link the unused 2021 export
(`resources/Practical Messaging - Day 2 - 2024 - 34.png`, still unlinked) or leave the slide bare.

`conversation-out-in` — one provider soliciting **two** couriers down three lifelines. Two would have made
it In-Out with the roles swapped, which is mechanically true and teaches nothing the previous slide has
not; *who is willing* needs more than one candidate on the page to be a question at all. The first
`ready()` lands inside the solicitation's lifetime, the second after the clock, and **red is on the expiry
only** — the second courier is not red for being unavailable, because it was not: it answered, after the
work was gone, which is the slide's own *timeout, not availability* distinction.

The nouns are the slide's (Delivery, Courier A/B) rather than Requestor/Provider, because this slide
teaches through its example; the roles still hold their sides, so the arrow still leaves from the right
exactly as it does for Out-Only. `participants()` became `lifelines()`, taking any number of parties —
boxes first, then rules, so adding a third did not reorder the two figures already there.

**Day 1 is 49 images, 49 linked.**

### ✅ 22. The four 2021 worked flows no longer draw paper in red

**Ian, 2026-09-08: recolour them.** `tools/repaint_paper_reds.py`, and it needed no draw.io re-export —
which is what made it an offer rather than a blocker (rules §4).

The two red layers are two distinct pixel values, so they separate cleanly:

| was | is | what it is |
|---|---|---|
| `#CC0000` — `strokeColor` on `endArrow=open;dashed=1` | `CARBON` | paper moving — **the notation conflict itself** |
| `#ff6666` — `<font color>` on text cells | `COMMENT` | the commentary layer the delegates wrote on top |

**Checked before choosing the second mapping:** the role names — *Hungry Customer*, *Order Taker* — are
already **black** in these files, and every salmon string is a remark or an action gloss sitting on a desk
rather than the desk's own name. So *a name is ink, a remark is comment green* is satisfied by mapping the
whole salmon layer to green; there is no name hiding in it. **`#FF3333` is deliberately untouched** — it is
a `fillColor` on `mxgraph.citrix.document` glyphs and does not read as red in the export at all.

**Both the `.drawio` and the `.png` are patched**, so the editable master and the render agree; without
that, the next person to open the file in draw.io and export it would put the red back. Antialiasing is
un-blended against the paper and re-blended with the new colour at the same alpha, so strokes keep their
shape instead of growing a fringe — 0.3–2.0% of pixels per file. `paper-worked-flows-montage` was rebuilt
after, since it embeds them as data URIs.

### 23. Phase 3 — the deck builds, the figure leads, and seven slides are over the floor

**2026-09-08.** `tools/outline.py` parses the outlines; `tools/build_deck.py` lays them out to
`styles.md` and writes both `.pptx`. Day 1 **135 slides**, Day 2 **151**, from 88 + 86 entries.
Commits `ef3f720`, `6009add`, `e095ad7`.

#### 23a. ✅ The figure leads — the panel and the floor were incompatible

**Two decisions settled with Ian months apart, and nobody had put them side by side.** `styles.md`
§Canvas puts the diagram in a panel at 0.85 of 2.0 of the content width — **4.6 inches**. Items 9, 10,
18 and 19 sized every label so the figure reads at 18pt displayed **12.4 inches** wide. Measured, a
figure in the panel reads at **37–53%** of the size it was measured at: an 18.0pt label at 7–9 real
points, on **84 of the 106 slides that carry a picture**. That is the whole legibility programme undone.

**Ian's call: the figure leads.** A slide whose picture is a *drawing* gives it the full content width;
**photographs keep the panel**, because a photograph tolerates being small and a labelled drawing does
not — and the file extension carries the distinction, every photograph in `resources/` being a `.jpg`
and every drawing a `.png`.

| | in the panel | figure-led |
|---|---:|---:|
| Day 1 figures at 85%+ of their Phase 2 size | — | **44 of 47**, median 91% |
| Day 2 figures at 85%+ | — | **71 of 74**, median 96% |
| slides over the 18pt body floor | 22 | **7** |

**The callout travels with the picture; the bullets do not.** A callout is the one line the presenter
says aloud about what is on screen, so when an entry splits it stands with the figure and the argument
goes on the first slide. Both keep the same title. **An entry only splits when its argument will not fit
in 1.15in above the figure** — past that the figure drops below 85% and the split has bought nothing.
**No content moves and none is lost, so §11's timings are untouched:** the presenter advances once more,
they do not say more.

**One labelled figure per slide.** Two on a stage each take about half its linear size — the same tax the
panel charged, and the reason `conversations.py` merged three 2021 exports into one figure. **17 entries
carry more than one figure and now show them in sequence; ☐ which of those are genuine comparisons is
Ian's call**, and where the reader must hold two side by side the answer is a composed figure, which is
Phase 2 work.

Six figures still land under 85%, between 74 and 82. **Three of the six are in the BPMN families Ian
asked us to leave unswept** (item 18), so they were short of the floor before this layout existed.

#### 23b. ✅ Seven slides overflow, and Ian approved a fix for each

`styles.md`: *"Expect the floor to force content off crowded slides. That is intended."* So the builder
**never shrinks type** — it lays out at the floor, measures the overshoot and reports it. Ian reviewed
the seven and **agreed to all seven, 2026-09-08**. Four splits, three cuts; only one takes content out of
the deck.

| slide | over | agreed |
|---|---:|---|
| D1 *Get It In Advance — ECST* | 3.56in | split into three entries at its own seams — the mechanism, *Why it holds up in practice*, *Be honest about the trade*. Nothing cut |
| D1 *Faults, by Pattern* | 1.81in | the *Examples.* paragraph moves to presenter notes |
| D1 *Must We Both Be Up?* | 1.26in | drop the second callout; the table's **Options** row moves to the delegate reference card; fold the lead-in into the first bullet |
| D2 *The Desk — In-Tray, Out-Tray, File* | 3.68in | split; *Two Devices You Already Know* takes the order wheel and the carbon-copy memo, and their two photographs go with them |
| D2 *Handlers + Activity State Updates* | 1.85in | split: bullets, then the listing. The listing is already trimmed to the sixteen lines its own `#note:` specifies |
| D2 *State Machine + Activity State Updates* | 1.50in | the same split |
| D2 *The Reactive Manifesto* | 1.02in | the author list moves to presenter notes |

**☐ Not applied yet.** They are outline edits, and items 1, 4, 5 and 6 add four `### Slide:` entries, so
§3's counts and §8's image budget move with them (rule 11).

#### 23c. ✅ Two defects only a consumer could find

**`#note:` blocks were leaking into slides.** The parser skipped the marker line but not its
continuation lines, so three slides carried build instructions to ourselves at 18pt — *Service Activator*
ended with *"wire the specific file references in during Phase 3"*. §12 exists to stop exactly this, and
it had been failing from the other direction: the provenance was correctly marked and the reader was
wrong. `grep '#note:'` finds the marker and reads as clean; **the leak is on the lines after it.**

**`flowbased_order_food` had no render.** Two Day 2 slides linked the `.excalidraw` **source**, so every
count in the repo read them as linked and Phase 2 never saw them outstanding — the same blindness the
three 2021 exports exploited. Rule 4: the picture was already in the old deck as `day2-s170-1.png`, so
it was a copy and a relink rather than a job for Ian. **Five further markers name two paths**, the render
and its editable source; the parser takes the first.

### ✅ Resolved 2026-09-02 — the three BPMN legend sheets

**Ian: *"Agree"*** — one figure of the six that matter; the full legends go to the delegate reference card.

`resources/bpmn-the-six.png` replaces **three** `#image:` lines with one, so Day 2 falls 90 → 88 images
and 49 → 47 linked. Service and Receive tasks, Message and Timer events, Exclusive and Parallel gateways,
each glyph named and glossed in a line.

**The slide had been asking for this all along.** Its callout is already *"Six of them do nearly all the
work"*, its presenter note is *"do not read the lists"*, and its own `#note:` sends the full legends to a
reference card — *a lookup table wants to be in the delegate's hand, not on the screen*. Three lookup
tables projected on a wall were doing the exact opposite of what the slide says out loud.

**It was also the cheap option, which is worth recording because it usually is not.** Drawing the three
legends faithfully needed roughly fifteen more BPMN symbols in `diagram.py` — manual, business rule,
script, loop and transaction markers; signal, escalation, conditional, error, cancel, link and terminate
events; inclusive, complex and event-based gateways — every one used on that one slide and nowhere else in
either day. All six on the new figure already existed in the tool, **because all six are what the hotel
and shopping families are built from**. That is the same fact the callout is making, and now the figure
makes it too.

**The reference card is unaffected and still Phase 3.** `Task Types.drawio`, `Event Types.drawio` and
`Gateway Types.drawio` stay as they are: they are editable, they are now the legends' only home, and for
**print** the plain black-on-white reads fine. It is a layout job, not a redraw.

### What sources exist

- **`session-work/imgs/dayN-sNNN-M.png` are the masters** for most of the deck. Many hand-drawn
  (excalidraw-style) diagrams have **no editable source** — not in `resources/`, not on this machine.
  Those get redrawn.
- **The paper-flow family is a big exception.** Every paper-flow diagram on Day 2 *does* have an
  editable `.drawio` source: `Hotel Onboarding`, `Pre-Arrival Guest Flow`, `Arrival`, `Occupancy`,
  `Paper Office`, `Restaurant Onboarding`, `Customer Order`, `Order Placement`, `Order Confirmation`,
  all three `* Errors` variants, the four `FBP *` re-expressions, and the Event Storming and Promises
  variants. Verified by matching `resource_text_index.py` labels against the extracted slide images.
  **Phase 2 for the Flow section and Paper Flow is editing, not redrawing.**
- **The Day 1 MEP diagrams are native PowerPoint shapes**, not embedded images (`draws=`, `pics=[]` for
  Day 2 s003–s020 in the original). Phase 2 there is **restyling**, not redrawing.
- `resources/` holds older, clean drawio versions of several concepts (`OO Basics`, `FBP Basics`,
  `FBP IP`, `FBP Ports and Connectors`, `FBP Network`, `FBP Service`, `FBP Sub Networks`,
  `OO vs. FBP Service`, `Task Queues*`, `Composite Microservice`) — different drawings, same ideas,
  usable as a starting point.
- **The Hohpe & Woolf EIP figures are gone.** 20 Day 1 figures were third-party book illustrations; 8 left
  with §4.6 to the routing handout and the remaining 12 were redrawn (item 5). The canonical URLs are in
  git history if a figure ever needs checking against the original.

### `#image:` annotation state

**Re-measured 2026-09-07, after the Integration Styles four.** **Both days have zero pending markers**,
and have had since 2026-09-02. The counts below are the ones the hand-off's verification block prints;
**re-measure rather than trusting them**, because this table has gone stale between sessions before.

| file | `#image:` lines | `[→ resources/…]` | `[external / EIP]` | pending `☐`/NEW | unannotated |
|---|---|---:|---:|---:|---:|
| `outlines/DayOne.md` | **49** | **49** | 0 | **0** | **0** |
| `outlines/DayTwo.md` | **88** | **87** | 0 | **0** | **1** |

**Re-measured again after class D, 2026-09-07. Day 1 is fully annotated**, and the one line left on Day 2
is the order-taking photograph, which is Ian's export.

Day 1 fell 62 → 49 as §4.6 left for the handout and T-0 cut the preamble; its `[external]` count fell
20 → 12 for the same reason, and **those 12 were the EIP redraw budget (item 5), now built** — which is
why Day 1's `[→ resources/…]` column moved 7 → 19 and `[external]` is 0. Day 2's six `[no source …]`
markers are gone — D2-10 replaced the pizza family with `☐ REDRAW (hotel)`, and **those 12 are now
built** (item 8), which is why Day 2's linked column moved 34 → 47 and its pending column 13 → **0**.
The only `☐` left anywhere on Day 2 is the reference card, and that is a `#note:`, not an image.

**The unannotated lines are the hidden bulk of Phase 2**, and they are larger than the redraw list was.
Their masters are the extracted `session-work/imgs/dayN-sNNN-M.png`. Annotating in bulk was rejected —
the slide-number → outline-entry mapping does not align automatically, because consolidated entries break
the 1:1. **Do it per section.**

### ⚑ They are not one job — surveyed 2026-09-02

Calling them "61 unannotated lines" hid the fact that they are **three different jobs with three
different answers**, and only one of them is mechanical.

| class | count | left | what it needs |
|---|---:|---:|---|
| **A — link only** | ~18 | **1** | photos, book covers, screenshots, the *DON'T PANIC* motif, an icon. Find the master, copy to `resources/`, link. No visual decision. The one left is the order-taking photograph — **Ian's export**. |
| **B — the two hand-drawn families** | ~36 | **0** | Day 1 §4.5 *Queues and Streams* (11, run 1) and Day 2's OO/FBP run (25, run 2). **Both done.** |
| **C — Integration Styles, s32–s35** | 4 | **0** | ✅ **built 2026-09-07** — `tools/integration_styles.py`, four figures on one shared stage. Item 9 above. |
| **D — the rest** | ~9 | **0** | ✅ **done 2026-09-07** — item 14 below. Six drawn (`app_shapes` ×4, `eip-the-big-picture`, `conversation-timeout`), two linked, and the last one is class A's. |

**✅ A is under way. 7 done 2026-09-02** — Day 2 §Next Steps' four (`cover-reactive-microservices`,
`cover-practical-process-automation`, `screenshot-eda-visuals`,
`cover-enterprise-integration-patterns`) and three from the order-wheel sweep
(`photo-mailroom-pigeonholes`, `photo-mail-cart`, `screenshot-fax-call-log`). Every one was **opened and
looked at** before linking, not matched by filename.

**✅ One of the two "missing" masters was there. 2026-09-03.** *A large stack of manila file folders and
papers* is `day2-s053-2.jpg` — the second image on a slide whose first image had already been looked at,
which is how it was missed. Also found in the same pass: **`DON'T PANIC`** (`day2-s113-1.jpg`, identical
to `day1-s090-1.jpg`), which is **one file serving four markers** across both days.

**☐ One master genuinely is not there** — *order taking (phone / card machine / order pad)*, Day 2 §Flow,
on the *Three different media, one notation* slide. **All 14 Day 2 `.jpg`s and all 6 Day 1 `.jpg`s have
now been opened**; the photos in this deck are all `.jpg`, and none of them is this. **Ian offered to
export it from the deck** — that is the right next step, and it is a real ask this time, not an
unchecked one.

### ☐ B is a decision, not a task — for Ian

**~36 hand-drawn diagrams in two runs**: Day 1 §4.5 *Queues and Streams* (queues, streams, offsets,
partitions, consumer groups, replay, the comparison grid) and Day 2's *Flow and Reactive* run (OO,
call-and-return, service orientation, entity services, the dataflow and FBP series, ports, lookups,
backpressure, load shedding, circuit breaker, supervisors).

**The deck now holds 45 figures in the Field Guide register.** If these ~36 stay as 2021 excalidraw, the
two longest technical runs on each day are in the old look — which is exactly the problem the BPMN
restyle was for, at four times the scale.

**Editable sources exist for part of it and are worth checking before any estimate**: `FBP Basics`,
`FBP IP`, `FBP Ports and Connectors`, `FBP Network`, `FBP Service`, `FBP Sub Networks`, `OO Basics`,
`OO Service`, `OO vs. FBP Service`, `Composite Microservice`, `Task Queues`, `Task Queues Moving Parts`,
`No Task Queues`, `Stream Log Tailing`, `Kafka-Partition-Log`, `SQS-Queue-Visibility`,
`SQS-Group-Queue-Visibility`, `Entity Stream`. §8 already records these as *different drawings, same
ideas* — a starting point, not a swap. **And their `.png`s are 2021 black-on-white, so linking them keeps
the old look; only a redraw through `diagram.py` changes it.**

**✅ Ian: *"Let's redraw both runs. One thing I want to strive for is a consistent look and feel."***

**Run 1 of 2 done — Day 1 §4.5, 2026-09-03.** `tools/queues_streams.py`, 11 figures, and §4.4's requeue
diagram is built in the same family so the queue a reader meets in §4.4 is the queue they meet in §4.5.
Day 1 unannotated falls 21 → 10.

**Consistency was enforced structurally, not by eye.** The section is one long comparison, so the run
uses one pair of shapes and never varies them: a queue is always `pipe` + loose `msg` envelopes, a stream
is always a `log` of contiguous numbered cells. Ten slides argue queue-versus-stream, and if both were a
pipe with envelopes the room would have to be *told* the difference every time instead of seeing it.
`lock` / `clock` / `tick` / `cross` mean exactly one thing each and are the only icons in the run.

**Two layout rules are enforced in the `queue()` helper rather than per figure**, which is what actually
keeps eleven drawings looking like one set:

  * **a lock sits on its envelope's top-left corner**, because arrows leave an envelope from the top or
    bottom and a centred padlock lands exactly on the one that goes up;
  * **the head of the queue is the right-hand envelope**, nearest the consumers. The first pass locked
    the left-hand one and every arrow then had to cross the whole queue to reach a consumer — the drawing
    was fighting its own reading direction. Messages enter at the capped left end and leave at the right.

**`diagram.py` gained `log` and `icon`** for this run, and both are shared with run 2.

**✅ Run 2 done — Day 2 §*Flow and Reactive Programming*, 2026-09-03.** `tools/flow_reactive.py`,
**25 figures**, which is every unannotated marker in the section. Day 2 unannotated falls 28 → 3, and the
three that remained were the order-taking photograph (Ian's export, still open) and the two C# code
screenshots, which became fenced code blocks in item 17 rather than pictures.

**The run has two vocabularies, and the split is the section's own argument.** Movement B — the wrong
answer — is **boxes joined by call arrows**: somebody is in charge and you can see who, because every
arrow starts at a caller. Movements C and D are **hexagons with ports, and dashed-square packets**. A
reader who sees a hexagon knows nothing is in charge; a reader who sees a box knows something is. Mixing
them would have thrown away the one contrast the section is built on.

**Two elements went into `diagram.py` rather than into the figure script**, for the same reason `queue()`
went into run 1's:

  * **`node(x, y, w, h, label, ins=, outs=)`** — the component glyph, a hexagon with named ports.
    Twenty-five figures draw it. It owns the reading direction (**in-ports left, out-ports right, data
    flows left to right**), and its left and right vertices are flattened into short vertical edges so a
    port always lands on a stroke however many there are. Ports come back keyed by name *and*
    positionally (`in0`, `out1`, …), so nothing ever aims at the hexagon's own edge.
  * **`packet(...)`** — an information packet, a dashed rounded square. Deliberately **not** the `msg`
    envelope: an envelope is a message on a channel and the EIP and queue families own it, while an IP is
    a value in flight between ports with a lifetime that ends when a component consumes it.

**A dataflow node and an FBP component are the same glyph on purpose.** The outline says FBP is a
subclass of dataflow and the deltas are the content; drawing them differently would argue they are
different things.

**Red pairs figures across the run**, as it does in the EIP set: the class and the service red the same
thing (encapsulated data), because *same idea, bigger unit* is the whole claim; the gateway is red in
*Feature Envy* and **its absence** is red in *Partitioning and Dataflow*, drawn as the empty dashed bar
where the gateway bar sat; the lookup port reds the pause, Build Lookup reds the absence of one;
backpressure reds a signal travelling back, load-shedding reds packets leaving the drawing.

**Defects that were invisible in the source and only showed up in the PNG** — the same lesson as every
batch before it: a leader line aimed at a port crossed the hexagon body, and when re-aimed struck through
the port's own label (fixed by reddening the ports themselves instead of annotating them); a full-size
cross over a named component struck through its own name, twice (fixed by moving the name above the
hexagon); the circuit-breaker figure was laid out consumer-first, so the feed arrow ran backwards through
the consumer's label and the outbound call crossed the queue; a pipe's mouth ellipse sat on a process
boundary and swallowed an out-port label; and the lookup response crossed the query until it was routed
the long way round — which turned out to be the honest drawing, because the round trip is the cost the
figure is about.

**`diagram.py`'s change is additive**: all seven existing families rebuild byte-identical, and
`flow_reactive.py` rebuilds byte-identical too.

### Settled 2026-09-01 — how Phase 2 is built

2, 3 and 4 below were open questions; the answers held for the 12 EIP figures and should hold for the rest.

1. **✅ Division of labour — settled, and the *Ian to draw* set is empty.** Items 1–4 and 7a were held
   back on the reasoning that they are *arguments rather than illustrations*. That was recorded before
   the tooling had drawn anything and it did not survive contact with 37 figures: `bpmn-elements`, the
   guest cycle and Departure are all arguments too, and every figure carries one red idea because
   `styles.md` requires it. Ian reopened it — *"any reason why you can't draw these?"* — and there was
   none. **All five are built.** The honest residue of the old reasoning is that they are conceptual
   enough to want a **hard review**, which is a different thing from being undrawable.

   **Everything in §8 is now built, and Phase 2's drawing is finished.** Both days have zero pending
   `#image:` markers; **Day 1 is fully annotated at 49 of 49** and Day 2 stands at **87 of 88**, the one
   line left being the order-taking photograph, which is Ian's export. (Unannotated was 61 when this was
   written; runs 1 and 2 of the redraw took 36, the class-A sweep and Integration Styles took most of
   the rest, and class D — item 14 — took the last nine.)

   **91 figures across eleven families**, all of them linted clean: 13 EIP · 5 conceptual grids · 2
   If-Later · 11 Queues and Streams · 4 Integration Styles · 4 application shapes · 1 conversation
   (Day 1) · 13 hotel BPMN · 6 legacy-BPMN redraws · 7 Paper Flow · 25 Flow and Reactive (Day 2).
2. **Format and pipeline — settled.** `tools/diagram.py` emits **both** the editable `.drawio` and a `.png`
   preview from one definition, so the two cannot drift. That answers the trap in the original options:
   `.drawio` alone had no local renderer, and SVG alone was not editable. See `tools/README.md`.
3. **Where output lives — settled.** `resources/eip-<name>.drawio` + `.png`, linked into the outline as
   `[→ resources/<name>.png]`.
4. **Order — settled.** Day 1 §4's 12 EIP replacements went first, as the biggest single item and the one
   that decides whether the material looks like ours; the Day 2 BPMN family followed, and **Day 2 now has
   no pending `#image:` markers at all**. Next: item 6a (the paper-flow notation key, the order-wheel
   photograph, the Worked Flows montage), then the If-Later pair, then the 68 unannotated lines per
   section.

5. **Two registers, settled by the content.** Phase 2 artwork is hand-drawn (`sketch=1`, Caveat labels)
   **except BPMN**, which is straight-stroked with Plex Sans labels. The reason is in the section itself:
   *Your Flow, in the Standard Notation* puts the delegates' hand-drawn paper flow beside the same flow in
   BPMN, and a hand-drawn BPMN collapses that contrast. BPMN keeps the Field Guide palette, so the section
   still belongs to the deck, and Caveat then reads as **our annotation on top of a standard diagram**.

   **✅ Approved by Ian, 2026-09-02**, on the BPMN review sheet: *"This family is straight-stroked and set
   in Plex Sans => agreed"*. The decision had been made without asking him, and it stands.

   **Knock-on, ✅ approved and queued 2026-09-02** — Ian: *"yes, let's restyle the others too"*. The **8**
   legacy BPMN images the outline still links (`BPMN Elements`,
   `BPMN Ordering Flow`, `Shopping Flow As Sequence`, `Shopping Flow with Pools`, `Shopping Choreography`
   and the three legend sheets — `Task Types`, `Event Types`, `Gateway Types`) are plain black-on-white
   draw.io. Until they are brought onto the palette the section mixes two BPMN looks.

   **✅ All 8 are done, 2026-09-02** — `tools/bpmn_shopping.py`, a family script like the other two.
   **Six figures replace eight images**, because `bpmn-the-six` stands in for all three legend sheets:
   `bpmn-elements` · `bpmn-ordering-flow` · `bpmn-shopping-as-sequence` · `bpmn-shopping-collaboration`
   (which three slides share) · `bpmn-shopping-choreography` · `bpmn-the-six`. The outline links are
   repointed; the 2021 sources are left in `resources/` untouched, and git history holds them either way.

   **Correction: all 8 are redraws, not restyles.** The earlier "7 of the 8 are an edit to `strokeColor` /
   `fontFamily`" was optimistic and is wrong. **Checked, not assumed:** there is no `drawio`, `soffice` or
   `inkscape` on this machine, so a style edit to a `.drawio` cannot regenerate its `.png` — and the
   `.png` is what the deck shows. Drawing through `diagram.py` emits both from one definition, which is
   the reason that tool exists. `Shopping Choreography` having no source turned out not to be the
   distinguishing fact.

   **Two are improved rather than copied, both because the slide's own text asked for it.**
   *BPMN — The Elements* is a slide whose body is **two kinds of arrow** and whose callout is *sequence
   flow is what happens at a desk; message flow is what happens between desks* — and the original picture
   had no message flow on it at all, and no labels. The redraw names the six elements and adds a second
   participant so the message flow has somewhere to come from. The *Choreography* original reads
   **"Bakset Validated"**, a typo that would go up on a screen, and reuses *Review Price* for two
   different messages — careless on a slide about correlating messages; the second is now
   *Basket Checked*.

   **The three legend sheets were held for a decision, and Ian took it** — see below.

   **`diagram.py` gained two things here.** `msg` takes `label_pos="above"` / `"below"`, so a BPMN message
   name is set as a **node label in Plex Sans** rather than as a `note`, which is always Caveat: on a
   choreography those names are the notation's own content, not our annotation on top of it. And a
   multi-line `"above"` label now stacks upward instead of half over the element it names.

6. **✅ The label-size sweep — settled 2026-09-07, and the floor is now enforced in code.**
   Ian, closing the previous session: *"I think a number of labels have come out too small, which makes
   them hard to read and it looks like a general problem that we might want to adjust."* He was right, and
   two instances had already been fixed one at a time — the stream offsets (12 → 17 bold ink) and the port
   names (14 → 17 bold). The sizes had been set per element as each family was built and never reconciled.

   **The finding that decided it: the two registers were never on the same scale.** IBM Plex Sans's
   x-height is `0.516`em against Caveat's `0.400` (OS/2 `sxHeight`, both faces at 1000upm), so **13pt of
   Plex reads across a room as 17pt of Caveat**. The survey that framed this as "BPMN has the smallest
   labels in the deck" was comparing point numbers across two faces; measured by x-height, BPMN was the
   one family already at the floor, and the hand-drawn register was the one that had drifted. Re-surveyed
   in Caveat-equivalent points, **255 labels across 58 figures** sat under the rule — including **46 pieces
   of diagram content written as ink `note`s at 15–16pt** (the grid axis names, *Settle Up*, *File the
   Receipt*, *Total the Invoices*), which the per-element survey could not see at all because they are not
   element labels.

   **Both sweeps were trialled across all 81 figures before anything was changed**, and measured rather
   than eyeballed: a sweep of *both* registers cost 3 labels wider than their own shape and 5 new
   edge-label collisions (4 of them BPMN — *Pay for the Booking* stops fitting its task box, *room free*
   and *hotel full* land on the message markers); the hand-register sweep cost 1 and 2.

   **Ian chose the hand register only.** BPMN keeps the scale it was drawn at, including the two crowded
   figures that squeeze a task to 10–11pt on purpose; only its **edge labels move, 12 → 13pt**, which is
   its own face's equivalent of the 17pt floor. Four figures needed a geometry nudge afterwards
   (`flow-fbp-iip`, `qs-queue-tasks`, `Departure`, `bpmn-hotel-guest-pool`), and **62 of the 81 figures
   moved.**

   **The rule is now enforced rather than remembered.** `Diagram._legible()` runs at the top of both
   serialisers and raises every label to its floor — 17pt for anything that names something in the
   drawing, 14pt for a muted remark of ours — so a figure cannot quietly ship at 13pt again, and the
   `.drawio` and the `.png` cannot disagree about a size. `_edge_pt` does the same for edge labels, which
   were the one text no figure could override and the smallest thing on the slide.

7. **✅ The commentary colour — settled 2026-09-07, second review pass.** Ian, on the swept figures:
   *"The gray text which tells you what is going on, such as 'this is a queue, not a stream', is small,
   but also feint. I think we might find this isn't just about a different font size or bold, but making
   it a more readable colour such as green."* He was right on both counts, and it is measurable: `muted`
   `#8A8578` is **3.59:1** against the paper — the only colour in the palette under the 4.5:1 threshold,
   where ink is 16.9, carbon 8.7 and annotation 4.9.

   **`muted` is now for lines, not letters.** All 220 grey notes, plus group names and the labels on
   muted edges, move to a new `COMMENT` token — **`#2F5D3A`, 7.45:1**. `muted` keeps the hairlines,
   gridlines and dashed ties, where being faint is the job.

   **The size half of the fix is the same insight one step further.** The deck was saying "secondary"
   twice — small *and* faint — and paying for it twice. With hue carrying it, the aside floor rises
   **14 → 16**, one step under content's 17 rather than three.

   **52 notes turned out not to be commentary at all** and are now ink at 17. The test applied was:
   *would removing this note leave something in the picture unnamed?* `tightest` and `loosest` are the
   ends of the scale; `fire and forget` / `notification` / `solicit-response` are the names of the four
   patterns in the cells; `partition 0`, `TYPE / CORRELATION ID / REPLY-TO`, `a desk`, the FBP
   vocabulary labels and the channel names all name something. Borderline cases were **left** as
   commentary on purpose: commentary is legible now, so leaving one there costs little, while promoting
   a sentence to ink makes the figure shout.

   **A side effect worth recording.** To a deuteranope, annotation red already renders as olive
   `#7B7B33` and the old muted grey as `#868678` — 1.21:1 apart, effectively the same colour. The deck
   already had a red-green problem and nobody had looked; the comment green pulls the pair to 1.77:1.
   It is an improvement, not a regression, but the separation that actually carries is **position and
   size** — the red idea is 19pt at the top of the figure — not hue.

   **`coupling-scale-boundary` also gave its two struck-out names their weight back.** *Content* and
   *Common* are what that slide is about, and greying them as well as ruling them through in red said it
   twice and cost the two most important words on the figure their legibility.

8. **✅ Paper Flow's red — settled 2026-09-07.** Ian, on the commentary colour: *"we might want a
   different colour for artefacts (blue?) over comments (green)"*. The artefact half ran into something
   the deck already teaches: `paper-notation-key`, `Paper-Flow-Delegate-Brief.md` and the facilitator
   guide all said **red dashed = paper moving, solid = a phone call or a fax**, so blue was already the
   phone call and red was a *notation* rather than an idea. The cost of that was concrete —
   **`Departure` carried seven red arrows**, so red marked nothing on it.

   **Settled: paper moves in carbon, and red is spent once.** The dash already separates paper from a
   phone call; the hue was saying it twice. Departure's red now sits on *take the stay file*, which is
   what its red sentence is about. `paper-notation-key`'s legend, the delegate brief and the facilitator
   guide are updated together — the convention is taught, so it cannot change in the figures alone.

   **`paper-guest-cycle` keeps four red arrows on purpose.** Its single red idea *is* the hand-offs —
   *every stage hands the next one a piece of paper* — so one idea is drawn four times. Dash carries the
   notation, red carries the emphasis, and the two compose.

   **⚑ Knock-on for Ian, checked not assumed.** The four worked-flow images on
   `paper-worked-flows-montage` are 2021 draw.io exports that still draw paper in red, so they now
   disagree with the key beside them. This is **not** blocked on a re-export: in those PNGs the arrows
   are `#CC0000` and the commentary text `#FF6666`, two distinct values, so a colour remap can separate
   them here in the way `repatch_steps.py` already repaints step numbers. It is left undone because
   recolouring the delegates' own 2021 session artefacts is a content decision, not a tidy-up.

---

## 9. Decision and rationale log

Newest first. Records **why**, including reasoning that changed no file — git history covers what
changed in the outlines, not this.

### 2026-08-27 — Day 1 §1 reframed on "easy to change + robust"; Task Queues promoted
Ian's question: do Task Queues still earn their weight, given they were there to show messaging is
useful *without* microservices — and is the microservices framing still the right driver? Two findings.
**Task Queues had lost their job to their position**: at slide 7 of 10, sandwiched between the
microservice anatomy slides, they read as a microservices pattern, the opposite of their point. And
**§1 was still off its own agreed goal** — the goal says *not: justify distributing*, but two full
slides were doing exactly that via the monolith branch-and-merge argument. Ian's reframe finishes a job
that was half-done when *Product Mode* was cut. Checked the manifesto rather than paraphrasing it: it
names four traits (Responsive, Resilient, Elastic, Message Driven) and its own preamble says reactive
systems are *"easier to develop and amenable to change"* — so **both** halves of Ian's framing are
literally in it, and the Day 1 plant pays off on Day 2 with no stretching. Changes, 10 entries in and
10 out: new **Easy to Change, and Robust** framing slide at position 2; *Monoliths Do Not Scale* and
*Microservices Let Us Scale* merged into **Easy to Change — Independent Deployability** with the two
diagrams as a before/after pair; **Task Queues moved up to position 4** and reframed as *robustness
without reorganising the company*; the 202 slide given the line that it is HTTP's own way of saying
store-and-forward. Third instance of the same pathology in this deck — the thesis was in the presenter
notes ("Independent deployability is the whole prize"), as the coupling verdict was in Conversations and
the lifetime rule in Designing Messages; promoted onto the slide. *No Cross-Service Transactions* and
*The Price of Distribution* untouched: the reframe sits in front of the locked-in argument, it does not
disturb it. Also fixed: the Fallacies table's cross-references were stale — two rows pointed at
*Managing Asynchronous APIs* (now a handout) and one at "Day 2 *Conversations*" (now Day 1 §5).

### 2026-08-27 — Day 2 §1 Designing Messages rebuilt (19 → 19, re-sequenced not cut)
Unlike Conversations this section was dense and well-argued; it needed joining up, not trimming. Goal:
*decide what goes in a message*. Four calls confirmed: the lifetime rule is a **rule**; the framing is
**inline / reference / replicate, per field**, with pragmatic denormalisation on top ("just like a Db");
both new slides are worth the space ("the story is missing here"); Tolerant Reader and Default Missing
Fields merge. Changes: **The Lifetime Rule promoted** from a bullet inside *Skinny Message — Normalized*
to the slide the section turns on; new opener framing message design as a **normalisation problem** (fat
= fully denormalised, skinny = fully normalised, neither extreme right); the **CAP cost moved out of the
bullets onto the slide** for both reference-data strategies — on-demand buys consistency over
availability and *A's uptime becomes A and B*, in-advance buys availability over consistency; two new
slides, **Why ECST Needs Snapshots** (you cannot replicate state from deltas without every one in order
— the join that makes If-Later possible) and **What You Inlined Is What You Version** (closes the loop
back to transitive dependencies); three example slides folded into their parents. Re-cut into four
sub-topics: Fat and Skinny Messages (5), Reference Data (4), Event Shape (6), Versioning (4).

### 2026-08-27 — Decided: Process Automation's pizza BPMN becomes hotel BPMN
Deferred to the Process Automation review, not started. Scoped at ~11 entries; the pool mapping is
already implicit in the Pre-Arrival paper flow (Guest / Just Paper Hotels / The Hotel replacing
Customer / Pizza Shop / Courier one-for-one), which makes the section formalise the delegates' own model.
Day 2 then runs on one domain end to end.

### 2026-08-27 — Paper Flow settled as "see one, do one", and a resource correction
Ian: the course is **in-person only**; the taught worked example is **Just Paper Takeaway** and the
exercise is **Just Paper Hotels — the Guest Flow**; **~75 min** is right because Managing Asynchronous
APIs took 60–75, so the swap is time-neutral. Checking `resources/` showed the arc is already resourced
and the two families are *the same diagram with different nouns*. The takeaway side has **three
artefacts per flow**; the hotel side has only the paper flow — so delegates are shown three and asked to
produce three. Failure cards rewritten into the error diagrams' own language rather than a parallel
vocabulary. Round 1 changed from all-tables-on-Departure to **one stage per table**: four stages have
worked reveals, Departure has none, and the hand-offs between tables are the largest fracture planes.
**Correction:** the "no editable source anywhere" claim does not hold for the paper-flow family — all of
it is editable `.drawio`. Also found: `Paper Flow.pptx` shows the hotel answers *before* the task, which
see-one/do-one makes wrong.

### 2026-08-27 — Paper Flow found to already exist; session designed rather than invented
`exercises/Paper Flow.pptx` is tracked, carries four worked reference flows in a consistent notation,
leaves Departure as the delegate task, and frames the whole thing as fracture planes. It is not
referenced from `README DAY TWO.md`, has no timings, and is a **drawing** exercise only. Designed a
~75-minute run-of-show that keeps all of that and adds the three rounds that make paper worth the slot:
**run it**, **break it**, and **who is in charge?** (orchestration vs. choreography — the round that
carries Process Automation). Placed after Reactive, before Process Automation, so delegates invent a
notation and the next section formalises it.

### 2026-08-27 — Day 1 §5 Conversations rebuilt (25 → 15) and the moves executed
Ian confirmed all four proposals: *Messaging or Eventing* moves to the **front**, Repair **folds into**
each pattern as its fault path, Tentative Operations **moves out** to Process Automation, and the deep
cut stands. New shape: frame (Participants / Messaging or Eventing? / new 2×2 grid), each pattern
immediately followed by its fault slide, closing on *Choosing an Exchange Pattern*. Two structural
fixes: **the coupling verdict is now on every pattern slide** (it was in the speaker notes on three of
fifteen) as a *coupled about / must you both be up* pair; and **Blocking In-Out is now the warning
slide** — the one pattern that puts temporal coupling back, undoing §1–§4 in a line of code, with the
legitimate case given so the answer is "when", not "never". Command-Ack and Query-Result merged. Also
found: the MEP diagrams are **native PowerPoint shapes**, so Phase 2 there is restyling. File moves in
the same pass. Day 1 = 91, Day 2 = 112.

### 2026-08-27 — Day 1 / Day 2 balance settled, and the shape of the workshop changed
Ian proposed turning *Managing Asynchronous APIs* into a takeaway handout backed by his QCon London 2026
deck, freeing the slot for a paper-modelling exercise. Checked the QCon deck rather than assuming: 43
slides, a **superset** of course §5 and a better treatment — three pillars, the same *ABCs of Endpoints*
frame, plus a MeX case study §5 has nothing like. Agreed: hand off ~26 slides, **keep the versioning
slides** as taught material and move them to Day 2, since that is message *design*, not tooling. Day
boundary resolved as a forward move rather than a swap. Day 2's headings confirmed to have the same
section-vs-sub-topic problem Day 1 had.

### 2026-08-27 — Day 1 §4 Messaging Patterns restructured into a build order
New **4.4 Guaranteed Delivery** (10 slides) pulling together producer-side (Dual-Write, Outbox, Inbox,
Log Tailing, State Change Capture) and consumer-side (DLQ, Invalid Message, Requeue with Delay)
reliability, closing on a new *What Your Broker Actually Gives You* slide (RMQ / SQS / Kafka
native-vs-backfilled matrix). Per Ian: Outbox now *poses* the duplicates question and Inbox answers it;
Log Tailing rewritten around the **anti-corruption layer** argument — CDC straight to the broker
publishes your table schema, which is common coupling wearing a message's clothes.

### 2026-08-27 — Day 1 §1 Distributed Systems reshaped to its agreed goal
12 → 10 slides in three movements (why we're distributed / what you now live with / the price).
*Product Mode* cut (org design, left over from when microservices needed justifying); *Example —
Microservices* folded in. "No Cross-Service Transactions" promoted as the load-bearing slide. "The Price
of Distribution" turned from a bare marker into the slide that reconciles the availability tension and
hands off to §Coupling. Fallacies given a third column mapping each to where the course answers it.

### 2026-08-26 — Day 1 §3 Integration Styles split from 1 consolidated entry into 5
Four style slides (File Transfer / Shared Database / RPC / Messaging), each carrying its diagram +
conversation + coupling verdict, plus a trade-offs slide plotting all four on the §2 grid. Confirmed
with Ian: Shared Database is **not** temporally coupled (writer and reader need never coincide) — its
problem is the shared mutable schema. Day 1 inventory corrected: 7 real sections, not 16.

### 2026-08-26 — Day 1 §2 Coupling rebuilt on two axes
One tight→loose scale replaced by two axes (what are we coupled *about* / must we both be *up*), a
why-it-matters opener tying back to Distributed Systems, and a grid slide that Integration Styles pays
off. Wikipedia paste removed from the notes — it defined temporal coupling as a *cohesion* problem,
contradicting the slides.

### 2026-08-26 — Resource matching closed
Negative result; 6 wrong pizza-BPMN links corrected; 20 EIP figures annotated with source URLs; plan
switched to the three-phase redevelopment above.

---

## 9. Agreed review queue — 2026-08-28

Ian's step-back review of the work so far. **These are agreed items to work through together, one at a
time — not a backlog to be cleared unilaterally.** Where an item contradicts something already built, the
item wins and the plan section above is stale until the item is worked.

**All items are ✅.** Each has a rationale block below. **Phase 1 is complete on both days.**

Three of these are **structural** and have knock-ons across both days — marked **⚑**. Read *Knock-ons* at
the end before starting any of them.

### Day 1

| # | item | what Ian said |
|---|---|---|
| **D1-1** ✅ | *Why Distribute?* | Doesn't earn its weight any more. The focus is *Easy to Change and Robust* — **don't bury the lead.** |
| **D1-2** ✅ | *Easy to Change — Independent Deployability* | Emphasise **independent deployability**; microservices are an **example** of it, not the thing itself. |
| **D1-3** ✅ | *Robust — Task Queues* | Rename to **Guaranteed Delivery** — that is the point being made. Task queues are an example of it. |
| **D1-4** ✅ | Three orphaned slides | *Microservice — Messages In, Private Data*, *Microservice — No Cross-Service Transactions* and *Collaboration — Orchestration and Choreography* are part of the **independent-deployability thread**, but Guaranteed Delivery now sits between them and orphans them. Regroup. |
| **D1-5** ✅ | *Fallacies of Distributed Computing* | May just restate *The Price of Distribution* — **which may well be the better slide**, and is the glue across the cost of independent deployability. |
| **D1-6 ⚑** ✅ | §1's shape | The question-then-answer ordering doesn't sit well with Task Queues, **which are an answer.** Phrase it as *we want independent deployability, but here are the problems*, and let the **next section be messaging as the answer.** **Task queues may go entirely** — unless they earn their place in Messaging Patterns. |
| **D1-7** ✅ | §2 Coupling → §3 Integration Styles | Coupling and independent deployability are **linked**: a **process boundary prevents Content and Common coupling**, but we cannot avoid **the other three — Control, Stamp, Data** — in the message we send. And because we now interact *between processes*, we must trade off **temporal** coupling too. That leads into the four integration styles and how each shows up in the coupling just discussed. **Goal: explain why messaging is our preferred option (reactive)** — and that file transfer is just messaging without support for locks, ordering, etc. |
| **D1-8** ✅ | §4.4 Guaranteed Delivery | Doesn't distinguish **producer** from **consumer** concerns. The **producer** cares about the **Outbox**, to guarantee a send. The **message pump** is where **Invalid Message, DLQ and Requeue-with-Delay** belong — they are mechanisms for handling a *failed message*. The **Inbox** is consumer side and part of the pump, but **matters more once we have the Outbox**. **Do not underestimate the pump conversation on errors**, and how it leads into DLQ / Invalid / Requeue (and Nack or Ack) — that conversation **makes parts of queue-vs-stream much easier later**. |
| **D1-9 ⚑** ✅ | §4.6 Pipelines, and the end of Day 1 | Pipelines **may not earn its weight on Day 1**. Put **§Conversations after Queues and Streams**, and bring **Fat and Skinny Messages, Reference Data and Event Shape over from Day 2**. That better completes the picture of *how to send and receive* ahead of Day 2's switch to the higher level. |
| **D1-10** ✅ | *Get It In Advance — ECST* (arrives with D1-9) | **Over-emphasises the problems.** In practice ECST is reliable and latency rarely causes actual issues, **particularly if you version the reference data**. It is **the better solution** than the synchronous lookup. Rewrite it as a recommendation, not a warning. |
| **D1-11** ✅ | §6 Observability | Lightweight, and orphaned by losing Managing Asynchronous APIs. **Dropped as taught material**; now one pointer slide in Day 2 `## Next Steps`. |

### Day 2

| # | item | what Ian said |
|---|---|---|
| **D2-1** ✅ | Versioning, and a new close | Versioning is orphaned away from the Managing Async APIs material. **Add a section at the end of Day 2 signposting further material**: *Describing Endpoints — Managing Async APIs*; *Schema — Versioning and Registries*; *Observability*. |
| **D2-2** ✅ | §1 becomes the lead | With Designing Messages moving to Day 1 (D1-9), **Flow and Reactive Programming leads Day 2.** Its opener has to open the day. |
| **D2-3** ✅ | *Worked Flows — Order, Placement, Confirmation* | These are the **see one** (hotel is the do one), so **we walk these flows in class**. **The slide count is too low** — expand; do not compress four flows into one slide. |
| **D2-4 ⚑** ✅ | *Now Do One* (paper) | **Do the paper flow for the hotel here** — in the Day 2 morning, straight after the paper worked flows. |
| **D2-5** ✅ | Movement order | Not sure about OO → Paper → Dataflow. **Go Paper Workflows → OO → Data Flow Programming**: show the paper way to understand flow (with the hotel exercise), then **ask how this looks in software**, then **point out the failure of OO to model it**, then lead into dataflow. |
| **D2-6** ✅ | *Worked Example — the Fax Workflow in FBP* | **Do not chop so much away.** We want **both** flows from paper re-expressed in FBP — Onboarding **and** Order / Placement / Confirmation. |
| **D2-7 ⚑** ✅ | *Now Do One* (FBP) | **Do the FBP flow for the hotel here** — a second do-one. |
| **D2-8** ✅ | Reactive | Comes after both do-ones, **to explain how it answers the question**. |
| **D2-9** ✅ | Pipes and Filters | Either explain it here — it helps with Process Automation — **or just drop it. Perhaps drop it for time.** **Dropped** — Day 2 gets no slide of its own. |
| **D2-10** ✅ | Process Automation and beyond | **Not reviewed yet.** Still to do, along with *Putting It Together* and *Next Steps*. **Done:** 50 → 37, opens on their own model, pizza → hotel. *Putting It Together* and *Next Steps* reviewed and kept. |

### ✅ D1-1 … D1-6 — done 2026-08-28

Worked as one pass, because piecemeal they contradict each other: D1-6 changes the section's shape, and
D1-3 (keep the slide, rename it) only resolves once D1-6 has said where the mechanism goes. **§1: 10 → 7
entries. Day 1: 95 → 94.**

**The section now stops at the problem.** Ian: *we want independent deployability, but here are the
problems, and then the next section is about messaging as the answer.* So §1 gives no answers; §2 Coupling
→ §3 Integration Styles → §4 Messaging Patterns do. Three movements: **what we want** (2), **what
independent deployability commits you to** (3), **the price and the second want** (2).

| item | what was done |
|---|---|
| **D1-1** | ***Why Distribute?* cut.** Its four forces are now one line on the opener — *"you will hear four reasons; strip the words away and two properties are left"*. Worth ten seconds, not a slide, and leading with them buried the lead. **The section opens on *Easy to Change, and Robust*.** The availability tension it used to set up is kept in the opener's notes and still settled on *The Price of Distribution*. |
| **D1-2** | ***Easy to Change — Independent Deployability* reframed.** It used to read "**The answer**: decompose into microservices", which made §1 an argument *for* microservices. Now: **what we want** → **what is in the way** → **microservices are one example of buying it**, explicitly *not the only way* and *not free*. |
| **D1-3** | ***Robust — Task Queues* → *Robust — Guaranteed Delivery*.** The property is the point; the task queue is an example. The slide keeps the *want* and the inoculation — *one team, one service, one queue; robustness without reorganising the company* — and gives up the mechanism. |
| **D1-4** | **Thread regrouped.** *Messages In / Private Data*, *No Cross-Service Transactions* and *Orchestration and Choreography* now run uninterrupted straight after *Independent Deployability*, with a new lead-in: *independent deployability needs a process boundary; the next three slides are what you have committed to by drawing one.* The task-queue material that split them is gone. |
| **D1-5** | ***Fallacies of Distributed Computing* dropped.** It restated *The Price of Distribution*, which makes the argument better and with a number, and which is now explicitly the section's glue and close. **Dropped entirely — see the correction below.** |
| **D1-6** ⚑ | **The two task-queue mechanism slides moved to §4.3**, after *Competing Consumers* — that is what they are a worked example of. Ian's condition was that task queues go *unless they look useful when we talk about messaging patterns*; they are, and §4.3 is where the parts finally have names. Carries a `#note:`: **D1-8 may want the 202 flow in §4.4 instead** — it is as much a guaranteed-delivery story as a pump story. Decide there. |

**Cut text:** `session-work/cut-section1.md`, plus git history.

**Correction (same day, Ian).** The first pass did not drop the Fallacies — it parked the whole table as a
"course map" `#note:` on §4 *The Big Picture*. Ian caught it: *are they not dropped?* They are. Relocating
a slide is not cutting it, and the justification for moving it defeated itself: if the table reads as a
syllabus only to someone who already knows the syllabus, that is as true at §4a, half an hour later, as it
was at §1. **Removed.** *The Big Picture* already carries the build-order map in its own `#note:`, in
vocabulary delegates have met; a second competing map was not an improvement. The text lives in
`session-work/cut-section1.md` and in git if it is ever wanted.

**Standing lesson:** when an item says *cut*, the test is whether the content still appears anywhere in
the deck — not whether it found a better home.

### ✅ D1-7 — done 2026-08-28

**§2 Coupling: 4 → 5. §3 Integration Styles: 5, rewritten.** The two now run as one argument, which is
what Ian asked for: *coupling and independent deployability are linked… that leads into the four
integration types, and how they show up on the coupling we have just discussed.*

**The load-bearing change is in §2.** *Axis 1* presented all five levels as a flat tight→loose scale,
which hid the thing that matters. It is now two slides:

- ***What the Process Boundary Already Bought You*** — **Content and Common are off the table.** There is
  no pointer into another process's memory, and separate processes with private data have no shared
  mutable store. This is the direct payoff of §1's *Messages In, Private Data* and *No Cross-Service
  Transactions* — the boundary is the mechanism, this is the return. Delivered as **good news**, right
  after §1's bill.
- ***What's Left Is in the Message*** — **Control, Stamp, Data: you cannot avoid picking one.** Callout:
  *the boundary chose the first two for you; the message is where you choose the third.* That is why §6
  *Designing Messages* exists.
- *Must We Both Be Up?* now says explicitly that interacting **between processes** is what forces the
  temporal axis on you.

**§3 now scores each style on what it hands back.** *Shared Database* gets the sharpest verdict —
**"the one style that hands back what the boundary bought you"**; it is a decision to un-draw the
boundary, not a shortcut past it. *RPC* is "the only style that loses on both axes at once", with a fair
word for when it is right.

**A real error was fixed on the *Messaging* slide.** It said "data coupling", which contradicted §2's own
examples — §2 plots a command message as *control* coupled and a whole-entity event as *stamp* coupled.
Corrected, and the correction turns out to be the argument: **messaging is the only style where the
coupling is a decision, not a property of the style.** The other three fix your position on the "about"
axis; messaging leaves it open, which is why §5 and §6 can exist at all.

**The section now ends on the goal.** The close was an open question — *if File Transfer and Messaging are
equally loosely coupled, why build the course on messaging?* — deferred to later. It is now answered on
the slide, in Ian's words: **file transfer is messaging with everything useful left as an exercise** —
ordering, locking and competing consumers, delivery guarantees, granularity and timeliness. Closing
callout: *only one style keeps everything the process boundary bought you, and lets you choose the rest.*
Both `#note:`s carry the reminder **not to say "Reactive"** — Day 2 needs it fresh.

**Cut text:** `session-work/cut-coupling-integration.md`.

### ✅ D1-8 — done 2026-08-28

**§4.4: 10 → 11 entries, in three groups.** Ian: *we don't really distinguish well here between producer
and consumer concerns.*

- **Producer — did the message actually get out?** Dual write → Outbox → Log Tailing (CDC) → State Change
  Capture.
- **Consumer — the pump, and the message it cannot ack.** *When the Handler Fails — Ack and Nack* (new) →
  Invalid Message → Requeue with Delay → Dead Letter → **Inbox**.
- **Then the bill:** *What Your Broker Actually Gives You*.

**The new slide is the one Ian asked for.** *Do not underestimate the pump conversation on errors, and how
that leads into DLQ, Invalid, Requeue — and Nack or Ack.* It gives the pump one lever (ack or don't), says
plainly that **there is no third option**, and turns the next three slides from a list of patterns into
answers to three questions: *is this ever going to work?* → Invalid; *might it work later?* → Requeue with
Delay; *have we tried enough?* → Dead Letter. It also plants the queue-vs-stream reveal explicitly —
**every mechanism on the next three slides needs per-message acknowledgement, and a stream has none** —
which is Ian's *that conversation makes parts of queue vs. stream much easier later*.

**Two moves that fixed broken order.** The **Inbox** left the producer group for the consumer group; it
had been sitting there with a presenter note explaining why it was out of place. **Dead Letter** now
*follows* Requeue with Delay rather than preceding it, so that Requeue's own "after a number of re-queues,
move to a dead-letter channel" is a forward reference instead of a backward one, and DLQ reads as the
terminal state it is. The Outbox's dangling duplicate is now deliberately left hanging — take answers from
the room, and pay it off on the consumer side.

**Parked question resolved: both task-queue slides stay in §4.3.** They are a pair — the architecture and
its HTTP face — and splitting them across sub-topics costs more than the filing gains. *Task Queue — HTTP
Flow* instead gained a callout pointing forward: **202 says we have your work and will not lose it; §4.4
is how you keep that promise.**

**New outline convention:** `#group: <title>` marks a run of slides inside a sub-topic. Not an entry, so
not counted; `###` stays reserved for slides. Documented in §1.

### ✅ D1-9 — done 2026-08-28

Settled with Ian and applied. **Day 1 = 95, Day 2 = 91.**

- **§4.6 Pipelines left Day 1** — 8 of its 9 entries became the **routing-patterns handout (§10)**.
  *Content Enricher* was kept and rehomed into **§6.2 Reference Data**, where it is the drawn form of the
  on-demand lookup, with a new callout: *the enricher does not remove the lookup, it moves it — and the
  availability sum moves with it.*
- **`## Conversations` now follows §4.5 Queues and Streams directly**, as Ian asked — nothing sits between
  them any more.
- **Designing Messages moved to Day 1 as §6**, sub-topics renumbered 6.1 / 6.2 / 6.3.
- **Versioning (Day 2, 4) and Observability (Day 1, 3) were dropped as taught material**, replaced by two
  pointer slides in Day 2 `## Next Steps` — *Describing and Versioning Your Messages — the Handout* and
  *Observability*. Ian: *these are what we drop to focus on the exercises.* The group carries a `#note:`
  saying to name the drop out loud rather than let it look like an oversight.
- **Cross-references fixed** both ways: both day intros, the Fallacies table's three rows, the §2 Coupling
  stamp-coupling note, and Day 2 §1's two callbacks to *Reference Data*.
- **Cut text preserved** in `session-work/cut-{versioning,pipelines,observability}.md` as well as git.

**D1-10 followed immediately** — see below.

### ✅ D1-10 — done 2026-08-28

*Get It In Advance — ECST* (Day 1 §6.2) is now written as **the recommendation**, not a warning. Ian: in
practice ECST is reliable, latency rarely causes actual issues, particularly if you version the reference
data, and it is the better solution than the synchronous lookup.

What the slide now says:

- **The default.** No miss path, so no synchronous call in the middle of a message flow.
- **Latency is not the problem people expect** — propagation is a broker hop, and this is *reference*
  data, which changes rarely.
- **Versioning is what makes it safe** — id and version, so a missing version is a **wait** rather than a
  wrong answer. The *Reference Data — Worked Example* slide is now labelled as the **proof** of that
  claim rather than an appendix, and gained a callout: *a missing version is a wait; a missing value would
  have been a wrong answer.*
- **The trade runs the other way from what delegates assume.** ECST is availability over consistency
  *boundedly* — you can measure how far behind you are. The synchronous lookup makes the same trade on a
  cache hit and then **reverses it on a miss**, when B is down and you are not. That is the sharpest line
  in the sub-topic.
- **The honest cost is operational, not correctness** — you own a subscription and must be able to
  rebuild the replica by replaying the stream.
- **When to still take the lookup:** the data genuinely cannot be replicated — too large, too sensitive,
  or it must be fresh at the instant of reading (authorisation, balance). Take the coupling knowingly and
  put a circuit breaker on it. Keeping one honest exception makes the recommendation stronger than a flat
  rule would.

**The same over-emphasis had leaked to two other slides and was corrected there too** — §6.3 *Why ECST
Needs Snapshots* ("ECST is *only tolerable* because of the snapshot event" → *ECST **works** because of
it*), and Day 2 §1 *FBP — Where Do Lookups Live?*, whose callout offered "a copy that might be wrong" and
now gives the same verdict as §6.2: **hold the copy.**

### ✅ D2-3 … D2-8 — done 2026-08-28

Worked as one pass. They contradict each other piecemeal: D2-5 moves the paper block to the front, which
changes what D2-3's worked flows are *for*; D2-4 and D2-7 put an exercise block at the end of two
different movements, which only has a meaning once D2-5 has said which movements those are; and D2-8's
"Reactive last" is a consequence rather than a move. **§1: 28 → 34 entries. Day 2: 91 → 97.**

**The hinge inverted (D2-5).** The section used to open on OO and call-and-return, end movement A on *is
there a better paradigm?*, and answer it with a photograph of a mail room. It now opens on the mail room.
Paper **poses** the question — *you have drawn a flow; how would you build it?* — and OO/SOA is the
**failed answer, offered second**. Ian: *show the paper way to understand flow (with the hotel exercise),
then ask how this looks in software, then point out the failure of OO to model it, then lead into
dataflow.*

Almost no slide text moved. What changed is four framing sentences:

- *Paper Workflows* stopped being "the answer to *is there a better paradigm?*" and became the day's
  opening.
- *Worked Flow — Order Confirmation* now closes the *see one* by **asking the room how they would build
  it**, and writing their answer on a flipchart.
- *Object-Oriented Programming* opens by **reading that flipchart back** — the room proposed this, it is
  not being imposed on them.
- *Feature Envy* stopped ending on an open question and now ends on the comparison: *you drew a flow with
  no coordinator this morning, then built one with a coordinator in the middle.*

**Movements renamed** to say what they do: **A — How the Office Did It**, **B — How Would You Build
That?**, **C — The Formalism**, **D — The Name**.

| item | what was done |
|---|---|
| **D2-3** | ***Worked Flows — Order, Placement, Confirmation* split into three.** It was one slide carrying six images and three flows; these are the exercise's *see one* and are **walked in class**. Now *Restaurant Onboarding*, *Customer Order*, *Order Placement*, *Order Confirmation* — one flow each, in the order the business runs them. The new slides earn their space rather than padding: **Customer Order** carries the **channel heterogeneity** point (phone, card machine, order pad — three media, one notation), which delegates hit immediately in the hotel; **Order Placement** is named the load-bearing flow and teaches *file it before you send it* and *write the reference number on the fax* **without naming storage or correlation**, so movement C can supply the vocabulary for something the room already saw; **Order Confirmation** lands the montage and asks the movement's question. |
| **D2-4** ⚑ | **Exercise block 1 placed at the end of movement A** — *Now Do One — the Hotel, on Paper*, ~45 min, rounds 1–3 plus debrief. |
| **D2-5** | **Movements reordered to A(paper) → B(OO) → C(dataflow/FBP) → D(reactive).** See above. |
| **D2-6** | ***Worked Example — the Fax Workflow in FBP* split into three**, mirroring the paper block: *Onboarding in FBP*, *the Order Flow in FBP*, *When It Fails, and What the Arcs Really Are*. Ian: *do not chop so much away.* One slide had held both flows, the failure variant and the MoM hinge across six images. The **Onboarding** slide now states each mechanism **beside its paper equivalent** in italics — storage *is* filing it before you send it, correlation id *is* the reference number on the fax, the lookup node *is* the Catalogue Maker — and closes on *nothing here was invented; it was named*. The **Order Flow** slide's content is the **composition**: three separate sheets of paper turn out to be one network, which is the thing paper could not draw and the shape block 2's debrief reproduces. |
| **D2-7** ⚑ | **Exercise block 2 placed at the end of movement C** — *Now Do One — the Hotel, as a Graph*, ~45 min. This was the original exercise deck's closing task (s009), which never had room. |
| **D2-8** | **Reactive is last**, after both do-ones, and its opener says so: the room has drawn the same system four times in two notations and made it fail; movement D adds no mechanism, it supplies the name. |

**The section now closes on round 4.** *Now Do One* — the old single hand-off into a 75-minute block —
became ***So Who Is in Charge?***, which re-asks the section marker's question and answers it with people
rather than slides: run your flow with a conductor, then with none. It is the hand-off into Process
Automation and keeps Day 1 §1's promise that delegates would *feel* the difference before either word was
defined. **Not a duplicate of Day 1 §1** — that slide names the two words, this makes the room live them.

**The exercise design was re-settled with Ian** (§7 rewritten): **~100 minutes**, as ~45 + ~45 + ~10,
against the ~75 budgeted. Round 3 (*break it*) went to block 1, next to the error vocabulary. **Round 0
was deleted** — it recapped material delivered an hour earlier, and each block's *see one* is now the
slides immediately before it. **The 25-minute overrun lands on Process Automation** (D2-10), which owes
an entry cut anyway; flagged rather than absorbed, because it commits that section before it is reviewed.

**Cross-references fixed:** the Day 2 intro paragraph (the exercise runs *inside* §1, in two blocks); the
*Putting It Together* pointer, which named the wrong FBP slide after the split and now sits on
*Onboarding in FBP* with an instruction to leave that diagram unannotated; and the OO slide's "they just
said this on the previous slide", which stopped being true once a 45-minute exercise moved in between.

**No cut text file.** Nothing was removed — the pass is a reorder, three splits and four rewritten framing
sentences. Git history covers the before state.

### ✅ D2-9 — done 2026-08-28

**Dropped. Day 2 gets no *Pipes and Filters* slide, and no outline change was needed** — there was never
one to remove. The question was only whether to add one before Process Automation. Ian: *drop it.*

**Why it costs nothing.** The mechanism is already taught three times over by the time Process Automation
opens:

- **The room enacts it** in exercise block 1 — desks, trays and a document moving between them.
- **Movement C formalises it** — *Nodes, Ports and Firing*, *Capacity, Backpressure and Node Lifetime*,
  *Flow-Based Programming*. Buffered arcs between single-threaded black boxes **is** pipes and filters;
  a slide naming it would re-teach what the delegates have already been given in a stronger form.
- **The pattern ships in the routing handout** (§10), where it is the first of the eight.

The name is not lost: *Data Flow Programming* already carries the line *"You already use one: the Unix
command line. Pipes and filters."* That aside was judged sufficient and left as it stands.

**Nothing downstream depends on it.** BPMN, the five workflow patterns and *Implementing Workflow
Patterns* never use the vocabulary. The only other occurrence in Day 2 is a passing clause in the
*Activities and Resources* definition — *"could be a framework, a bespoke state machine, or pipes and
filters"* — which reads fine as a gesture at something already met.

**Time.** Nil added, which is the point: Process Automation owes the exercise 25 minutes (D2-10) and this
was the one item that could have made that worse.

### ✅ D2-10 — done 2026-08-29

**Process Automation: 50 → 37 entries. Day 2: 97 → 84.** The section was 52% of the day and entirely
lecture; it is now 44%, and the 13 entries removed are worth roughly the **25 minutes it owed the paper
exercise** (§7). Settled with Ian as four decisions.

#### 1. The opening now keeps the promise made on the slide before it

*So Who Is in Charge?* ends §1 with **round 4** — the room runs its own flow with a conductor and without
one — and says *you have just invented orchestration and choreography; the next section gives them their
names, and a notation.* What actually opened the section was a **Josuttis SOA quote**, then BPMN defined
cold against a food-ordering diagram nobody had seen, then **five slides of icon legends**. That is a
notation reference manual and a cold start, not the promise being kept.

**New opening slide: *Your Flow, in the Standard Notation*.** The Pre-Arrival flow delegates drew in round
1, beside the same flow as a BPMN collaboration, and a mapping table: desk → task in a lane; the heavy
vertical bar → a pool boundary; a red dashed arrow between trays → a message flow; a numbered step inside
the bar → sequence flow; the conductor's routing slip → the process and its token. **They have every
concept and lack only the vocabulary** — so the primitives that follow arrive as *what you needed in order
to draw that*, not as a legend to memorise.

It **replaces** *What is a Microservice? (SOA 3.0)*, which settles the **Josuttis collision**: the quote
now appears once, on §1 *SOA Is OO at Macro Scale*, where it is the yardstick *Feature Envy* fails
against. §1 carries the service-alignment argument too, so nothing is lost.

#### 2. Pizza → hotel, in full

**Confirmed and executed** (decided 2026-08-27, deferred to this review — §7). Day 2 now runs on **one
domain**: takeaway is the *taught* example, hotel is what delegates *do*, and Process Automation
formalises **their** model rather than a third unrelated one. Pools: Customer → **Guest (Tourist)**, Pizza
Shop → **Just Paper Hotels** (Booking Team, Fax Operator), Courier → **The Hotel** (Concierge, Front Desk).

The five workflow-pattern examples were rewritten onto the booking flow — and they were already in it:
*Take the Call → Create Booking Request* (sequence); *Take Payment* ∥ *Prepare Confirmation* (split, then
join before the guest is told); ***Check Availability → Accept X Reject*** (exclusive choice) is literally
step 7 of the diagram they hold; confirmation-arrives **or** guest-chases-on-a-timer (simple merge).
*Tentative Operations* moved off a shopping basket onto the reservation, where `reserve()` / `commit()` /
`rollback()` is the actual conversation and the hotel's timeout is the reason durable execution exists.
Handler, state-machine and engine examples were renamed to match (`Requested → SentToHotel → Accepted →
Paid → Confirmed`). Costs nothing extra in Phase 2: **the pizza family had no editable source either way.**

#### 3. Front half, blocks A–E: 28 → 22

| what | why |
|---|---|
| **Five legend slides → two.** *Basic Elements* + *Connecting Objects* → **BPMN — The Elements**; *Tasks* + *Events* + *Gateways* → **BPMN — Tasks, Events and Gateways**, with a callout naming the **six** primitives this deck actually uses. | Three icon legends is a lookup table, and a lookup table belongs in the delegate's hand — the same test that sent Managing Async APIs and the routing patterns to handouts. The merge also **promoted the load-bearing line**, which was buried in the two-line *Connecting Objects* slide: **sequence flow carries the token, message flow does not.** That is *ACID at a desk, BASE across desks* in BPMN's vocabulary, and it makes orchestration-vs-choreography obvious twelve slides later instead of arbitrary. ☐ **New handout: a one-A4-side BPMN reference card**, carrying the full legends. |
| **Three *What is X?* slides merged away.** *What is Orchestration?* → *Process = Orchestration*; *What is Collaboration?* → *Collaboration and Choreography*; *What is Choreography?* → *Choreography and Conversation*. | Each restated the slide immediately before it in four or five bullets. Only three lines were worth keeping and all three were kept: *all logic is local to the orchestrator*; *both participants must run in the engine* (Day 1 §2's coupling argument at process scale); *like describing a dance — no owner, no shared state*. |

**Deliberately not cut:** the five pattern slides — *Implementing Workflow Patterns* maps that exact
vocabulary onto the three implementation styles twenty-five slides later, so it is load-bearing — and the
three orchestration-pool slides, which Ian kept as separate diagrams.

#### 4. Back half, blocks F–I: 22 → 15

This is the section's payload — *where does activity state live, and who updates it* — and the four
mechanism slides are untouched. The cut is all consolidation:

| what | why |
|---|---|
| **Four `(Fault) …` slides → one *Compensation, Four Ways* table**, a row per mechanism: where the undo lives, what triggers it, the catch. | It was the **same idea in four costumes** — you cannot roll back, so you write an undo for every do — made four times, twenty slides apart. As a table the repetition becomes the teaching point, and **Saga** gets named once rather than four times. It also puts **business error vs. technical error** in one place, which is the distinction that stops teams retrying a declined card forty times. |
| **Two `— Illustration` code screenshots absorbed** into *Handlers + Activity State Updates* and *State Machine + Activity State Updates*. | Each was a heading and one sentence over a screenshot of the slide before it. |
| ***Tentative Operations* + its *Example* merged.** | Two slides for one three-line protocol; the example is now three sentences on the same slide, and rewritten to the booking. |
| ***Embedded vs. External Workflow Engines* + *Workflow Engines — Lessons from SOA* merged.** | Two lines each, and the second was the argument the first was missing. The merged slide lands **anaemic services** — all domain logic migrating into the engine — which is the set-up for *Smart Endpoints, Dumb Pipes*. |

#### 5. Putting It Together and Next Steps — reviewed, kept

Both were in D2-10's scope and neither needed cutting. *Putting It Together* is six entries, four of them
the takeaway flows annotated with exchange patterns, every image sourced from an editable `resources/`
drawio — it is the payoff for §1's worked flows and it earns its length. One fix: its section marker said
*"the fax/pizza workflow"*; pizza was never in it, so it now reads *the fax workflow — the takeaway
see one*. *Next Steps* is seven entries, five of them pointer and further-reading slides, already rebuilt
by D2-1 / D1-11.

#### Correction made in the asking

The question offered *"Legends 4→1"* as the mechanism for a **−6** front-half cut, but there are **five**
legend slides, not four. The **−6 / to 22** arithmetic was honoured, so the legends went **5 → 2** rather
than 5 → 1. Taking them to a single slide would give −7 and a 21-entry front half; it remains available.

#### Left for Ian

**A fourth domain is still in the section.** *Process = Orchestration*, *Tokens*, *Collaboration and
Choreography*, *Pools and Lanes* and *Choreography and Conversation* all illustrate with the
**shopping-basket** diagrams (`resources/Shopping Flow*.drawio`, `Shopping Choreography.drawio`) — a
distinct domain from both takeaway and hotel. It was outside D2-10's agreed scope, so it was not touched.
Unlike the pizza family **these have editable sources**, so relabelling them to the booking is cheap. Worth
a decision in Phase 2.

**Cut text:** `session-work/cut-process-automation.before.md`, plus git history.

### Knock-ons to settle before starting the ⚑ items

**1. ✅ Settled — D1-9 rebalanced both days, and D2-10 finished the job.** Day 1 = 96, Day 2 = 97 after
D2-3…D2-8, then **84** after D2-10 cut Process Automation 50 → 37. Versioning did not follow the other
three; it was dropped.

**2. ✅ Settled — the exercise runs in three placements, ~100 min.** §7's run-of-show has been rewritten.
Block 1 (paper, ~45) ends movement A; block 2 (FBP, ~45) ends movement C; round 4 (~10) is the section's
last slide, immediately before Process Automation. Round 3 went to block 1; **round 0 was deleted**. Not
planted twice against Day 1 §1 — that slide names orchestration and choreography, round 4 makes the room
live the difference. **The 25-minute overrun was paid by Process Automation — D2-10 cut it 50 → 37.**

**3. ✅ Settled — Pipelines.** D1-9 sent Day 1's pipeline material, *Pipes and Filters* included, to the
routing handout (§10). **D2-9 settled it for Day 2 too: no slide.** Movement C already teaches the
mechanism and the handout carries the pattern.

**4. ✅ Settled — D2-5 reversed the movement order committed in `f6227ee`.** Paper leads; OO/SOA is the
failed answer. The content survived; four framing sentences changed. *Feature Envy — You Built a
Distributed Monolith* kept its job, and gained a better close.

---

## 10. The routing-patterns handout

**Created by review item D1-9 (2026-08-28).** Day 1 §4.6 Pipelines was 9 entries, every one of them a
Hohpe & Woolf figure slide, and 9 of the 20 EIP redraws in the Phase 2 budget. Ian: it does not earn its
weight on Day 1. It becomes a takeaway handout instead — the same treatment as Managing Asynchronous APIs.

**Contents — 8 patterns:** Pipes and Filters, Message Translator, Content Based Router, Dynamic Router,
Recipient List, Splitter, Aggregator, Resequencer.

**Not in it:** *Content Enricher*, which stayed on Day 1 in §6.2 Reference Data.

**The prose already exists.** `script/Patterns/*.md` is near-1:1 with these slides and was already slated
to become the slide body in Phase 3 — so for these eight it becomes the handout body instead. That is why
this cut is cheap: we are not throwing the material away, we are shipping it in the form it was already
written in.

**Cut text:** `session-work/cut-pipelines.md`, plus git history.

☐ **Handout work:**

1. ☐ Assemble from `script/Patterns/*.md` — check which of the eight have a script file and write any that
   do not.
2. ☐ Decide the artwork: redraw the 8 EIP figures, or cite Hohpe & Woolf's originals with attribution. A
   handout can legitimately cite; the deck could not, which is why they were in the redraw budget.
3. ☐ Frame it so it reads as reference rather than as slides that got cut — a one-page index up front,
   the same fix §6 needs.
4. ☐ Signpost it in the deck. It is *routing*, so it belongs either with §4.5 Queues and Streams or with
   the Day 2 `## Next Steps` group — decide when D1-8 / §4.4 is worked.

---

## 11. The timing pass — done and closed 2026-09-01

**The first time either day has been timed.** Flagged in §3 since 2026-08-27 and blocked on D2-10 until
Phase 1 closed.

### Settled with Ian

| | |
|---|---|
| **Teaching day** | 09:00–17:00, 1h lunch, 2 × 15m breaks → **390 min of teaching time** |
| **Day 1 exercises** | RMQ (§4.2) + Kafka (§4.5) ≈ **160 min** together — Ian's estimate, **never measured** |
| **Day 2 exercise** | Paper Flow ≈ **100 min** (§7, settled by D2-4 / D2-7) |
| **Pace** | varies by entry type, not one flat rate |

So the lecture budgets are **Day 1: 230 min** and **Day 2: 290 min**.

### The model — `session-work/timing.py`

Each `### ` entry is classified structurally and given a rate: **pointer/hand-off 1.0** (Q&A, further
reading, exercise material, section markers, *Now Do One*), **standard 2.5**, **diagram walk 3.0** (has an
image and real body text), **table 3.5** (a markdown table, because tables generate discussion). The total
is then scaled by **1.154**, calibrated against the one section whose real duration is known: the old
`## Managing Asynchronous APIs`, **31 entries at ~75 minutes** (§7), recovered from git at `3e875a3`. The
model scores it 65 raw, so everything is scaled up 15%.

**A prose-density model was tried first and abandoned.** Scoring entries by body + presenter-note length
gave 13 min for a *Distributed Systems* entry and **795 min for Day 1**. The flaw is worth recording:
**outline verbosity measures how much redevelopment an entry has had, not how long it takes to teach**,
and the presenter notes are full of *why this slide is here* meta-commentary that is never said aloud. The
anchor section scored thin only because nobody had rewritten it.

### The result

| | lecture | exercise | day | vs. 390 |
|---|---:|---:|---:|---|
| **Day 1** | **283** | 160 | **443** | **over by 53 min** |
| **Day 2** | **248** | 100 | **348** | **42 min spare** |

Day 1, by section — the cut queue is the top of this list:

| min | entries | section | |
|---:|---:|---|---|
| **48** | 15 | **Conversations** | biggest section on either day |
| **38** | 11 | 4.4 Guaranteed Delivery | rebuilt by D1-8 and coherent; low priority |
| **33** | 13 | **4.5 Queues and Streams** | six entries under 250 characters |
| **24** | 8 | 4.3 The Message Pump | |
| 22 | 7 | Distributed Systems | already cut by D1-1…D1-6 |
| 18 | 6 | 6.3 Event Shape | |
| 18 | 5 | Integration Styles | |
| 17 | 5 | Coupling | rebuilt by D1-7 |
| 17 | 7 | 4.2 Sending and Receiving | |
| 15 | 5 | 6.2 Reference Data | |
| 14 | 5 | 6.1 Fat and Skinny Messages | |
| 14 | 6 | 4.1 What Is a Message? | |
| 3 | 3 | Messaging Patterns + Closing | markers |

**Trust it to ±20%**, and no further. It rests on **one** observed duration, and the model was 13% low on
that one before calibration. **The single highest-value thing anyone can do is time the two Day 1 code
blocks on the next delivery** — 160 min is an estimate, and it is 41% of Day 1.

### Day 1 cut queue — ~53 min to find, ~19 found

Ian chose a **cut pass** over moving *Designing Messages* back to Day 2. Then, mid-pass, he named a
better first move than any of the seeded candidates:

> *One option here is to lose much of the initial pre-amble around distributed systems. Just go straight
> into discussing integration styles, and then messaging mechanics. Move any discussion of why into Day 2
> as a pre-cursor to the general topic of how we design event driven architecture.*
> …*we already found it dated from an era when microservices was an important conversation, but that's
> not so true now, so we could move this.*

#### ✅ T-0 — the preamble moves — done 2026-09-01

**Day 1: 96 → 90 entries, 443 → 424 min. Day 2: 84 → 86, 348 → 354.** Nineteen of the fifty-three minutes.

**What the section actually was.** `## Distributed Systems`, 7 entries / ~22 min, rebuilt only three days
earlier by D1-1 … D1-6. Reading it against §2 and §3 showed **five of the seven were *why* but two were
machinery**: §Coupling's *What the Process Boundary Already Bought You* says Content and Common come off
the table *"because §1's Messages In, Private Data and No Cross-Service Transactions"*, and §4.4 calls
back to the transaction rule by name. Those two could not simply leave.

| decision | what was done |
|---|---|
| **Compress, don't just cut** (Ian: *compress with 3, 4 into an opener, one or two slides*) | *Messages In, Private Data* + *No Cross-Service Transactions* → one slide, ***Messages In, Private Data, No Shared Transaction***. It is now **the first slide of the course**, which is right: its own notes always called it *"the load-bearing slide — everything the two days teach exists because this sentence is true."* |
| **Keep robust** (Ian) | *Robust — Guaranteed Delivery* stays on Day 1 as the second opener slide. It is the **inoculation** — nobody can file the course under "not for us, we're a monolith" — and §4.4 is the spine of the afternoon. Its "the second property" wording had to go, since the two-properties framing is now on Day 2. |
| **§Coupling's opener went too** | *Coupling — Why It Matters* was pure callback to *Independent Deployability*. With that gone it had no content, so §Coupling now opens on *What the Process Boundary Already Bought You* with one sentence of framing folded into its notes. |
| **The arithmetic stayed on Day 1** | 0.999⁴ = 0.996 was on *The Price of Distribution*, and was **cited forward** by §Coupling *Must We Both Be Up?* and §3 *RPC*. Moving it to Day 2 would have made both forward-reference the next day. It is now **on *Must We Both Be Up?* itself** — where it belongs, because it was always an argument about *temporal* coupling. |
| **Drop the older material rather than move it** (Ian) | The *Independent Deployability* slide's microservices apparatus — the monolith-branching timeline, the two-pizza team, the Cockcroft quote — **did not travel**. The property is kept on Day 2; the 2016 argument for it is not. ***Collaboration — Orchestration and Choreography* was dropped outright**: Day 2's round 4 makes the room live the distinction and Process Automation names it, so planting the words a day early stopped earning a slide. |

**New on Day 2: `## Why Event-Driven?`, 2 entries** — *Easy to Change, and Robust* (the two properties and
the prize, without the microservices case) and *So How Do You Design One?* (the hand-off into Flow). Day 1
now builds the machinery and Day 2 says what it was for, which is the better order: the argument was
preamble on Day 1 in front of people who had not yet seen a single mechanism.

**Adjusts D2-2**, which had settled that Flow's opener opens Day 2. It now opens the *teaching*, two
slides in, and its marker was rewritten to hand off from *So How Do You Design One?*.

**Nine cross-references were rewritten**, six on Day 2. The two that mattered: the *Reactive Manifesto*
payoff was built on the two properties being taught **a day** earlier and that gap is now **ninety
minutes**, so its notes now say to make the room recall them from memory rather than re-reading the
opener; and round 4's *So Who Is in Charge?* claimed to keep a promise made by a slide that no longer
exists, so it now says plainly that nothing has planted the words and the room should invent the
distinction cold.

**Cut text:** `session-work/cut-distributed-systems-preamble.md`,
`session-work/cut-coupling-why-it-matters.md`, plus git history.

#### ✅ T-1 — the fault slides fold — done 2026-09-01

**Conversations 15 → 13 entries, 48 → 44 min. Day 1: 424 → 419.** Five minutes, not the ten estimated —
see *what the estimate got wrong* below.

**Three of the four folded; the fourth was left standing.** *In-Only — What About Faults?*, *Out-Only —
Faults Are Not Available* and *In-Out — When the Reaction Is a Fault* are one argument told three times
with the pattern's name changed, and they became ***Faults, by Pattern***, a three-row table. But
***In-Out — When Nothing Comes Back*** is **not a fault story** — it is the *absence* of a message:
timeout, retry, idempotency, de-duplication, and the place the Inbox pattern from §4.4 earns its keep.
Folding it into a table of fault *types* would have lost the mechanism. It survives, renamed ***When
Nothing Comes Back at All*** so its subject is unmistakable.

**What the new slide has to carry.** *Choosing an Exchange Pattern* already has a `fault path` column
covering all five patterns, so a table of verdicts would have been pure duplication. The merged slide
therefore carries the **reasoning** — a `why` column — and the closing table stays as its recap:

- **Out-Only** — No Fault is *forced*: the provider does not know its subscribers, and if it did it would
  be coupled to them. **"You cannot have loose coupling and a fault path back. Pick one."**
- **In-Only** — a reverse channel, because there is no later message to replace. **Only if there is an
  action to take.**
- **In-Out** — Fault Replaces Message: same channel, same correlation id, same code path. A fault is a
  **response**, not an exception.

Taught loosest-first, the room watches the fault path *appear* as the coupling tightens — which is the
payoff of having put a coupling verdict on every pattern slide.

**A side benefit.** The three pattern slides — In-Only, Out-Only, In-Out — now run **consecutively**
instead of being interrupted by a fault slide each. That was not the goal, and it is the better ordering.

**One reference repaired:** *Out-Only* ended *"which is exactly why its fault story is the one on the next
slide"* — no longer true, since the fault treatment is now two slides later and covers all three.

**What the estimate got wrong.** §11 costed T-1 at ~10 min on a 4 → 1 fold. Two corrections: only three
slides could legitimately fold, and the merged slide is a **table**, which the model rates 3.5 against the
2.5 of each standard slide it replaced — so 7.5 units become 3.5, not 2.5 become 1. **Consolidating into
tables recovers less time than consolidating into prose**, which is worth remembering for T-2 and T-3.

**Cut text:** `session-work/cut-conversations-fault-slides.md`, plus git history.

### ⏸ T-2 … T-5 — parked 2026-09-01, and why

**Ian closed the timing pass here.** T-0 and T-1 are done; the remaining ~29 minutes are **not** to be
cut. His reasoning, and it holds:

> *We sometimes run over on the first day and then complete the material at the top of Day Two.
> Organizationally, keeping the two decks lets us psychologically switch on Day Two. We may find that
> later steps help us refine the exact timings anyway.*

**The arithmetic supports it rather than merely tolerating it.** Day 1 is over by 29 and Day 2 is under by
36 — so **the pair is 773 of 780 minutes**, seven to spare. The spill-over is not a fudge covering a deck
that does not fit; it is a deck that fits across the pair, with the slack sitting on the day that can
absorb it. **Day 2 must keep that slack**: it is now a designed relief valve, not spare capacity to spend.
Anything added to Day 2 spends Day 1's overrun.

**Two decks stay two decks.** Merging them would recover the boundary as usable time, and is explicitly
rejected: the break between decks is what lets the room psychologically switch on Day Two.

**Timings get refined by Phase 3, not by more cutting.** The model counts *outline entries*, and a
consolidated entry may become more than one slide when the deck is rebuilt. Phase 3 produces real slide
counts, which is a better basis than anything available now — and by then the two Day 1 code blocks may
have been measured, which matters more than all of T-2 … T-5 put together (they are 41% of Day 1 and have
never been timed).

**The items below are kept, not cancelled.** If Phase 3 shows Day 1 worse than the model says, this is
where to start — and T-1 showed the estimates are optimistic, because consolidating into a **table**
recovers less than consolidating into prose (the model rates a table 3.5 against a standard slide's 2.5).
Sizes below are therefore an upper bound.

| # | section | candidate | ~min |
|---|---|---|---:|
| **T-1** ✅ | Conversations | **Done 2026-09-01 — 3 → 1, not 4 → 1.** See below. | **−5** |
| **T-2** | 4.5 Queues and Streams (33 / 13) | **Two caption triples become two slides.** *Scaling Queues and Streams* (38 chars) + *Competing Consumers* (95) + *Partitions* (322) + *Consumer Groups* (150); and *Archive and Replay* (40) + *Queues — No Archive and Replay* (153) + *Streams — Archive and Replay* (95). Seven entries carrying almost no text — the **image-dump pattern** never checked on Day 1. Check first whether *Queues vs. Streams — Capability Matrix* already says it. 7 → 3. | ~10 |
| **T-3** | 4.3 The Message Pump (24 / 8) | **Thin slides merge.** *Translate and Dispatch* (131 chars) and *Competing Consumers* (86) are captions; *Worked Example — the Task Queue* and *Task Queue — HTTP Flow* are one example over two entries. **Do not touch *Service Activator*** — Ian reopened it once already. | ~7 |
| **T-4** | Conversations | **Two framing tables, one job?** *Messaging or Eventing?* and *Command or Query?* both classify the same exchange before it is chosen. Merge only if they genuinely overlap. | ~4 |
| **T-5** | 4.4 Guaranteed Delivery (38 / 11) | **Lowest priority — D1-8 is recent and Ian was emphatic about the pump/error conversation.** Only obvious candidate: *State Change Capture* (270 chars) folding into *Log Tailing*. | ~3 |

**Re-run `python3 session-work/timing.py`** if any of these is ever worked, or after any change that adds
material — it reads the outlines directly, so the budget line is always current. **Watch the pair total,
not the single day**: 780 minutes is the real budget.

---

## 12. Outline hygiene — cleaned 2026-09-01

**The outlines are build inputs, not a change log.** Before Phase 3 they carried the redevelopment's own
working state: 23 provenance `#note:` blocks and 25 presenter notes citing review-item codes, dates,
*"merged from"*, *"moved here from"*, *"used to read"*, and attributions.

**The reason to remove it is not tidiness.** Presenter notes become the **speaker notes in the generated
deck** — so *"Merged from three slides (D2-10)"* would have shipped to whoever presents the course.

### The rule

**Strip everything backward-looking. Keep everything forward-looking.**

| removed | kept |
|---|---|
| why a slide changed, when, and which review item did it | the 20 pending `☐` build markers |
| *"used to read…"*, *"was one slide carrying six images"* | 12 live `#note:` blocks — quick-start placement, *do not say "Reactive"*, the delegate reference card, *"split this table back if it is too dense"* |
| `**Cut text:** session-work/…` pointers | every word of delivery guidance, including the *reasons* a slide is taught a particular way |
| attributions (*"Ian:"*, *"(Ian)"*) | the substance of what was decided, rewritten as instruction rather than history |

Where a provenance clause carried teaching content, the content was **rewritten as instruction**, not
deleted — *"Reframed 2026-08-28 (review item D1-10). The slide used to hedge…"* became *"Teach this as the
recommendation, not a warning… do not hedge it with 'replicas go stale', that over-states the risk."*

**Verified:** entry counts and timings identical before and after — 88 / 86 entries, 419 / 354 min — so
only metadata was removed.

### Keep it this way

**Rationale belongs here and in commit messages, never in the outline.** This section is the standing
instruction; §9 and §11 are where the *why* for every change already lives.

---

## 13. Visual style — settled 2026-09-01

> **`styles.md` (tracked, repo root) is the authoritative spec.** This section records *why* the direction
> was chosen and what it changes; **it must not restate the spec** — same rule as PROMPT.md and this plan.

**Direction C, "Field Guide"** — a serious typographic frame with the hand-drawn work living inside it.
Chosen from three directions rendered side by side on the same real slide
(https://claude.ai/code/artifact/45339596-b57a-4132-9e3e-121599954c61).

**Why not the other two.** **A, Workshop** commits to the whiteboard entirely, but a hand face carrying
body copy is precisely what made the old deck read as personal. **B, Technical Manual** buys authority and
prints beautifully, but fights the paper-flow notation, which is hand-drawn *by design*. **C is the only
one that does not force a choice between authority and the notation the Paper Flow exercise depends on.**

**The hand-drawn quality was never the fault.** Delegates reproduce the in-tray / out-tray notation with a
pen, so the drawings have to look like something a person could draw. What was actually failing, measured
from both `.pptx` files rather than from impression:

| finding | detail |
|---|---|
| **4:3** | Both decks 10 × 7.5in — letterboxed on every modern screen |
| **Chalkboard everywhere** | 908 runs on Day 2, 398 on Day 1, carrying every heading *and* every body line |
| **8pt body** | 227 runs at 8pt on Day 1, 12pt next most common |

**Decisions taken, all recorded in `styles.md`:** 16:9; IBM Plex Serif / Sans / Mono with Caveat for
callouts and diagram labels **only, never body copy**; an 18pt body floor with 16pt permitted for
sub-items; and a palette taken from the Paper Flow notation rather than invented — annotation red is the
dashed arrows, carbon blue is the carbon copy, which **is** the outbox pattern the course teaches.

**Font licensing is closed.** IBM Plex and Caveat are both SIL OFL 1.1 — commercial training use,
PowerPoint embedding and printed handouts all permitted. Flagged as a risk at decision time.

**Consequence for Phase 2.** Format is `.drawio` XML, start point is the 12 EIP replacements (both settled
with Ian). `tools/diagram.py` emits the `.drawio` source and a `.png` preview from one definition, because
there is no drawio CLI here and hand-maintained previews would drift. See `tools/README.md`.

**The 18pt floor is a content decision as much as a design one** — expect it to force material off crowded
slides, and treat that as the floor doing its job rather than as a problem to route around.
