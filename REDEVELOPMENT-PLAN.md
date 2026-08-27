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
| **Day 1 deck** | `Practical Messaging - Day 1 - 2025.pptx` (138 slides) | outline rebuilt to 91 entries |
| **Day 2 deck** | `Practical Messaging -  Day 2 - 2025.pptx` (182 slides, note the double space) | outline rebuilt to 112 entries |
| **AsyncAPI handout** | QCon London 2026 deck (43 slides) | to assemble — §6 |

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

Current: **Day 1 = 91 entries** with two code exercises; **Day 2 = 112** with one paper exercise.
Day 2 is the bigger day on slide count, but Process Automation (50, 45% of the day) is still to be cut
— that is the relief valve.

Why the split holds on content, not just counts: Conversations + Repair continues Day 1's build order
directly — *you can send and receive reliably, now what exchange do you build with it*. Fat & Skinny +
Domain/Summary is about what is **in** the message and how state propagates, which leads into Flow.

### Section goals agreed so far

| section | goal |
|---|---|
| Day 1 §1 Distributed Systems | *set up the problems messaging solves* — not: justify distributing. Framed as **easy to change + robust**, see below |
| Day 1 §4 Messaging Patterns | a **build order**, not a catalogue — see below |
| Day 1 §5 Conversations | *choose the right exchange pattern* — pick between In-Only / Out-Only / In-Out / Out-In and know what each commits you to in coupling terms |
| Day 2 §1 Designing Messages | *decide what goes in a message* — choose what to put in it, and know how the receiver gets whatever you left out and what that costs in availability |

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

## 4. Day 1 work queue — `outlines/DayOne.md`, 6 sections, 91 entries

| # | Section | entries | P1 | P2 | P3 |
|---|---|---:|---|---|---|
| 1 | Distributed Systems | 10 | ✅ reframed on *easy to change + robust*; Task Queues promoted | ☐ | ☐ |
| 2 | Coupling | 4 | ✅ rebuilt on two axes | ☐ 1 new grid diagram | ☐ |
| 3 | Integration Styles | 5 | ✅ split into 4 style slides + trade-offs on the grid | ☐ reuse §2 grid artwork | ☐ |
| 4 | **Messaging Patterns** | **52** | ✅ rebuilt as a build order | ☐ 20 EIP redraws | ☐ merge scripts |
| 4a | · The Big Picture | 1 | ☐ reframe as build order | | |
| 4b | · 4.1 What Is a Message? | 6 | | | |
| 4c | · 4.2 Sending and Receiving | 7 | +RMQ Quick Start | | |
| 4d | · 4.3 The Message Pump | 6 | | | |
| 4e | · **4.4 Guaranteed Delivery** | **10** | **new sub-topic** | | |
| 4f | · 4.5 Queues and Streams | 13 | +Kafka Quick Start | | |
| 4g | · 4.6 Pipelines | 9 | routing kept as content | | |
| 5 | **Conversations** *(moved from Day 2)* | **15** | ✅ 25 → 15, rebuilt as a decision | ☐ 1 new grid + reuse §2 grid | ☐ |
| 6 | Observability | 3 | ☐ | ☐ | ☐ |
| 7 | Closing | 2 | ☐ | ☐ | ☐ |
| — | ~~Managing Asynchronous APIs~~ | 31 | ✅ **→ handout**; 4 versioning slides → Day 2 | | |

Day 1 is **Messaging Patterns (52, 57%)** then **Conversations (15, 16%)**, with 19 slides of framing
in front and 5 of wrap-up behind.

---

## 5. Day 2 work queue — `outlines/DayTwo.md`, 4 real sections, 112 entries

| # | Section | entries | P1 | P2 | P3 |
|---|---|---:|---|---|---|
| 1 | **Designing Messages** | 19 | ✅ rebuilt on the lifetime rule | ☐ 2 If-Later diagrams | ☐ |
| 1a | · Fat and Skinny Messages | 5 | goal: *decide what goes in a message* | | |
| 1b | · Reference Data | 4 | on-demand vs. in-advance, CAP cost on-slide | | |
| 1c | · Event Shape | 6 | +**Why ECST Needs Snapshots** (new) | | |
| 1d | · Versioning *(moved from Day 1)* | 4 | +**What You Inlined Is What You Version** (new) | | |
| 2 | **Flow and Reactive Programming** | 32 | ☐ ← **next work item** | ☐ | ☐ |
| 2a | · Flow (paper workflows, the frame) | 5 | on-ramp, not its own section; also the exercise's *see one* | | |
| 2b | · Reactive Programming | 27 | **☐ close the Day 1 loop — see below** | | |

**When reviewing 2b, three things are already owed to it:**

1. **Pay off Day 1's plant.** Day 1 §1 now frames everything as *easy to change* + *robust*, deliberately
   without naming Reactive. *The Reactive Manifesto* slide should land as recognition: **Resilient** is
   their "robust"; *amenable to change* is their "easy to change", in the manifesto's own words; and
   **Elastic** and **Responsive** are the two they did not have names for yet.
2. **Close the loop on the slide that already exists.** *Microservices Are Reactive Architectures* should
   call back explicitly to Day 1 §1's *Easy to Change — Independent Deployability*.
3. **Fix an attribution.** The *Reactive Traits — Value, Form, Means* slide asserts a mapping the
   manifesto does not itself make — the manifesto names four traits and makes Message Driven the
   mechanism, but never assigns value/form/means. It is a defensible gloss and it is how Bonér has
   presented it, but the slide currently reads as if quoting. Attribute it.
| 3 | **Paper Flow** exercise | 9 | ✅ run-of-show settled (§7) | ☐ Guest Cycle replacement; `Departure.drawio` | ☐ restructure deck + wire into README |
| 4 | **Process Automation** | 50 | ☐ **needs cutting** — 45% of the day; **+ pizza → hotel redraw** | ☐ ~11 BPMN redraws | ☐ |
| 4a | · Tentative Operations *(moved from Repair)* | 2 | ✅ bridge into Durable Execution | | |
| 5 | Putting It Together | 6 | ☐ | ☐ | ☐ |
| 6 | Next Steps | 5 | ☐ | ☐ | ☐ |

**The balance problem that remains:** Process Automation at 50 entries is 45% of Day 2 and is entirely
lecture — which is exactly what the modelling exercise should relieve.

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

**It already exists.** `exercises/Paper Flow.pptx` is tracked, 9 slides, and is **not** referenced from
`exercises/README DAY TWO.md` — built but never wired into the running order. Extract:
`session-work/paperflow.txt`, images at `session-work/imgs/paperflow-sNNN-M.png`.

### What is already there — do not rebuild it

- **Domain: the hotel guest cycle** — Pre-Arrival, Arrival, Occupancy, Departure, plus Hotel Onboarding.
- **A consistent visual language, and it is ours.** Desks drawn as boxes with an **in-tray and an
  out-tray**; a heavy vertical bar for the **organisational boundary**; numbered steps; red dashed
  arrows for paper movement; solid arrows for phone/fax channels; folders for filed state.
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

### Run-of-show — ~75 min

Placed **after Reactive Programming, before Process Automation**: delegates need the FBP vocabulary for
the third artefact, and must **not** yet have BPMN — so they invent a notation and the next section
formalises it. Round 4 must land immediately before Process Automation or its payoff goes cold.

| round | min | what happens |
|---|---:|---|
| **0 — See one** | 10 | Recap the desk / in-tray / out-tray notation on **Restaurant Onboarding**, its error variant, and its FBP re-expression. Land *ACID at a desk, BASE across desks*. |
| **1 — Model it** | 20 | **One stage of the guest cycle per table** — Onboarding, Pre-Arrival, Arrival, Occupancy, Departure. Hard rule: **every hand-off goes through an out-tray and an in-tray**, no shouting across desks. That rule is what makes the fracture planes visible. |
| **2 — Run it** | 10 | *Execute* the model with cards, one person per desk. Missing messages and unstated assumptions surface within two minutes. Fix the model in pen. |
| **3 — Break it** | 15 | Deal 2–3 failure cards per table. Tables draw the **error variant** of their flow — the second artefact. |
| **4 — Who is in charge?** | 10 | Re-run **with a conductor** holding a routing slip (orchestration), then **with none**, each desk acting on its in-tray (choreography). Compare: where did knowledge of the whole process live? Who had to change when a step was added? |
| **Debrief** | 10 | Reveal the worked flow for each table's stage — four exist, **Departure does not**, so it is the collective piece. Then assemble: the hand-offs *between* tables are the largest fracture planes of all. Close on the FBP re-expression and *you have just drawn what the next section shows you in BPMN*. |

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

### ☐ TODO — build (design settled; build queued behind the Day 2 section reviews)

1. ☐ **Facilitator guide** — run-of-show, timings, circulating prompts, debrief questions, reveal order.
   Tracked, e.g. `exercises/Paper-Flow-Facilitator-Guide.md`.
2. ☐ **Delegate brief** — scenario, roles, the in-tray/out-tray rule, the three artefacts expected.
3. ☐ **Printable materials** — role cards, document cards, failure cards, tray sheets.
4. ☐ **`resources/Departure.drawio`** — reference answer for the one stage with no worked flow, in the
   same notation as the other four.
5. ☐ **Rebuild `Paper Flow.pptx`** — the *takeaway* flows become the worked example up front; the four
   **hotel** flows move behind the exercise as the debrief reveal. As it stands the deck shows the
   hotel answers before the task, which see-one/do-one makes wrong.
6. ☐ Replace the third-party *Guest Cycle* infographic (s003, setupmyhotel.com).
7. ☐ Wire it into `exercises/README DAY TWO.md` — absent today.

Minor: the Pre-Arrival diagram (s006) repeats step numbers 4/6/7 either side of the boundary — check
whether that is deliberate concurrency or a slip.

### Knock-on: Process Automation moves to the hotel

**Decided 2026-08-27, deferred by Ian to the Process Automation review. Do not start it early.**

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

1. **Two-axis grid** — *what are we coupled about* × *must we both be up* — with gRPC / command-message
   / shared-database / whole-entity-event plotted (Day 1 §2 Coupling, final slide). **Ian to draw.**
2. **The same grid** re-plotted with File Transfer / Shared Database / RPC / Messaging (Day 1 §3) — same
   artwork, so the call-back is visual and not just verbal.
3. **The same grid again** with the four exchange patterns, Blocking In-Out alone in the temporally-
   coupled quadrant (Day 1 §5 *Choosing an Exchange Pattern*).
4. **2×2 exchange-pattern grid** — who speaks first × is there a reply (Day 1 §5). New drawing.
5. **20 EIP figure replacements** (Day 1 §4) — currently Hohpe & Woolf's own illustrations. Biggest
   single item in the budget; decides whether the material looks like ours or assembled.
6. **2 If-Later diagrams** — versioned envelopes on a stream, and on a queue with competing consumers
   and read-past (Day 2 §1).
7. **`resources/Departure.drawio`** and the *Guest Cycle* replacement (Day 2 Paper Flow).
8. **~11 BPMN redraws**, pizza → hotel (Day 2 Process Automation).

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
- 20 Day 1 figures are **Hohpe & Woolf EIP book figures**, annotated in the outline with canonical URLs.
  Third-party; professional training material should replace them with our own.

### `#image:` annotation state

| file | `#image:` lines | `[→ resources/…]` | `[no source …]` | `[external …]` | unannotated |
|---|---|---|---|---|---|
| `outlines/DayOne.md` | 62 | 5 | 0 | 20 | 37 |
| `outlines/DayTwo.md` | 92 | 37 | 6 | 0 | 49 |

The unannotated ones are photos, logos, book covers, screenshots and hand-drawn diagrams. Annotating in
bulk was rejected — the slide-number → outline-entry mapping does not align automatically, because
consolidated entries break the 1:1. Do it per section during Phase 2.

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
