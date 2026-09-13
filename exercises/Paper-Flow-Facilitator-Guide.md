# Paper Flow — Facilitator Guide #

**Just Paper Hotels: the Guest Cycle.** Day 2, inside `## Flow and Reactive Programming`.
~100 minutes, in **three separate placements** — not one block.

In-person only. The design assumes a room with tables, and there is no remote fallback.

---

## The one rule ##

> **Every hand-off goes out-tray to in-tray. Nobody shouts across the office.**

Enforce it from the first minute and do not let it slide. It is the whole exercise: it is what makes the
hand-offs visible, and the hand-offs are where the fracture planes are. A table that lets one person tell
another something out loud has just hidden the boundary you are about to ask them to find.

Everything else — the notation, the failure cards, the FBP re-expression — is built on that one rule
having been obeyed for forty minutes.

---

## Where the three placements sit ##

| | placement in Day 2 §1 | rounds | min |
|---|---|---|---:|
| **Block 1 — on paper** | end of **movement A**, after *How Do We Deal with Errors?* | 1, 2, 3 | ~45 |
| **Block 2 — as a graph** | end of **movement C**, after the three FBP worked examples | 5, 6 | ~45 |
| **Round 4 — who is in charge?** | end of **movement D**, the section's closing slide | 4 | ~10 |

> ⚠ **Round 4 runs last, not fourth.** The number is a *name*, not a position — five presenter notes
> across the deck call it "round 4", so it kept the label when it moved to the section's close. The
> running order is **1, 2, 3 → 5, 6 → 4**. Say "who is in charge?" in the room, not the number.

**There is no round 0.** It used to recap material delivered an hour earlier. Each block's *see one* is
now the slides immediately before it, so the recap is a pointer — "you saw this ten minutes ago" — not a
retelling. Do not rebuild it.

### The thing that must not happen ###

**Delegates must not meet BPMN before any of this.** They invent a notation; Process Automation
formalises it afterwards. If someone in the room already knows BPMN and starts drawing pools, let them —
but do not put the notation on the screen, and do not name it.

---

## Before the day ##

### Print list ###

| item | quantity | source |
|---|---|---|
| Delegate brief | one per person | `Paper-Flow-Delegate-Brief.md` |
| Role cards | one per desk, per table | `Paper-Flow-Printables.md` §1 |
| Document cards | ~20 per table | `Paper-Flow-Printables.md` §2 |
| In-tray / out-tray sheets | two per desk | `Paper-Flow-Printables.md` §3 |
| Failure cards | one deck, cut up | `Paper-Flow-Printables.md` §4 |
| Notation key | one per table, or one per person | `resources/paper-notation-key.png` |

Everything is A4 and mono-safe. The palette was chosen to survive a greyscale office printer — `carbon`
and `annotation` differ in value, not just hue — so a black-and-white print still reads.

### Per table, not printed ###

- A flipchart or A2 sheet, and markers. Pens for everyone.
- **Optional and cheap: a pinboard sheet.** One sheet everyone at the table may read but nobody may
  remove from. It is a topic/stream against the in-tray's queue, and it makes queue-vs-stream physical
  the moment someone asks "how do two desks both get this?"

### Room ###

Tables of **4–6**, each table taking **one stage of the guest cycle**, all running in parallel. You
circulate, dealing failures.

**Five tables covers the cycle.** With fewer, drop stages from the *middle* and keep **Onboarding** and
**Departure** — Onboarding is the only stage where the catalogue gets made, and Departure is the only
stage with no worked answer, so it is where the room's own thinking has to carry.

With more than five tables, double up a stage. Two tables modelling Pre-Arrival differently is a good
debrief, not a problem.

---

## Block 1 — on paper (~45 min) ##

Hand-off slide: ***Now Do One — the Hotel, on Paper***.

Open by pointing at the four takeaway flows they have just been walked through, and at the guest-cycle
map. Then: *you have seen one. Now do one.* Hand out the brief and the notation key.

### Round 1 — Model it (20 min) ###

Each table draws the paper flow for its stage on the A2 sheet.

**Give them the assumptions, because slide 4 does.** Prior stages hand on:

| stage | what it may assume already exists |
|---|---|
| Hotel Onboarding | nothing — this is where the catalogue comes from |
| Pre-Arrival | a catalogue of hotels |
| Arrival | a booking |
| Occupancy | a key, and a room-service menu |
| Departure | the invoices filed during the stay |

**Occupancy is the one that stalls**, because "the guest stays in a room" is not a flow. Give the table
the concrete task from the deck: *make a purchase from Room Service.* That has a beginning and an end.

**Departure is the one with no worked answer**, and it is the collective piece in the debrief. Its task,
verbatim: *Departure is how I get my bill. Show how the flow of bills reaches my file.*

**Circulating prompts — use these, in this order of preference:**

- *Where does that piece of paper physically sit while it is waiting?* (finds the missing tray)
- *Who picks it up? How do they know it is there?* (finds the implicit poll)
- *What does that desk know that nobody else does?* (finds the file)
- *You just told them. Show me the tray.* (enforces the rule)
- *That desk is in a different building. Draw the bar.* (finds the boundary)

**What good looks like at 20 minutes:** desks as boxes with a labelled in-tray and out-tray, dashed
arrows for paper, solid arrows for phone or fax, a heavy bar wherever the flow crosses an organisational
boundary, and steps numbered in one ascending sequence. Do not chase perfection — round 2 will find the
holes faster than you can.

### Round 2 — Run it (10 min) ###

One person per desk. **Execute** the model with document cards. Paper physically moves from out-tray
sheet to in-tray sheet.

Missing messages and unstated assumptions surface within two minutes — that is the point, and it is why
this round is short. Tell them to **fix the model in pen** as they go, on the same sheet. The crossings-out
are evidence, not mess.

**Watch for the two failures that always happen:**

- **A desk with nothing in its in-tray, waiting.** Ask the table what is supposed to arrive, and from
  where. Usually a message was never drawn.
- **Someone reaching across the table.** Stop it, and make them name what they just skipped.

### Round 3 — Break it (10 min) ###

Deal **2–3 failure cards per table**. Tables draw the **error variant** of their flow as a second
artefact, beside the first.

The vocabulary is *How Do We Deal with Errors?*, which they saw ten minutes ago — the carbon copy, the
file, the resend, the retry. **This is recall, not invention**, and if a table is inventing new words,
point them back at that slide.

**Dealing the cards.** Match the card to the flow, do not deal at random:

| deal this | to a table whose flow has |
|---|---|
| *The request goes missing* | any fax or post hand-off — Onboarding, Pre-Arrival |
| *Make a carbon copy before you send, and file it* | any table that has just lost something |
| *No receipt came back — resend the fax* | a table that has already drawn a receipt |
| *This document was delivered twice* | deal it straight after the resend card, to the same table |
| *The night porter is on a break* | Arrival or Departure — a desk with opening hours |
| *This desk goes home* | any table that has drawn a file |
| *The guest checks out early, mid-flow* | Occupancy or Departure |
| *Two clerks work the same in-tray* | a table with a busy desk — Front Desk, Booking Team |
| *This in-tray holds only three documents* | a table whose flow has an obvious bottleneck |

Deal the **resend** card and the **delivered twice** card to the same table, in that order, about three
minutes apart. Watching a table cause its own duplicate is worth ten minutes of explanation, and it is
the cleanest motivation for idempotency in the whole course.

### Debrief (5 min) ###

**Reveal the worked flow for each table's stage.** Show the file, do not narrate it — they have just
spent forty minutes in the notation and can read it.

| stage | reveal |
|---|---|
| Hotel Onboarding | `resources/Hotel Onboarding.png` |
| Pre-Arrival | `resources/Pre-Arrival Guest Flow.png` |
| Arrival | `resources/Arrival.png` |
| Occupancy | `resources/Occupancy.png` |
| **Departure** | `resources/Departure.png` — **reveal this one last** |

**Departure is the collective piece.** The other four are "here is one way"; Departure has no answer in
the delegates' world until the room makes one. Ask the Departure table to walk theirs first, then show
ours as *a* reference, not *the* reference. If theirs is better, say so.

**Land the line, and land it here:**

> ▎ **ACID transactions take place at a desk. BASE takes place across desks.**

It works at this moment and nowhere else — the out-tray rule has just been enforced for forty minutes, so
"across desks" is a thing they have physically done, not a metaphor.

---

## Block 2 — as a graph (~45 min) ##

Hand-off slide: ***Now Do One — the Hotel, as a Graph***.

Runs at the end of movement C, after the three FBP worked examples. Same domain, new notation — that is
the whole task, and saying so up front prevents the table from redesigning the business.

### Round 5 — Re-express it (25 min) ###

Redraw **your own flow from block 1** in FBP: information packets, nodes, ports.

Four questions to hold them to, in this order:

1. **What are the information packets?** (usually: the documents they already drew)
2. **Where do the lookups live?** (the catalogue, the room list, the rate card)
3. **Where is state stored?** (the files — and the answer should make them uncomfortable)
4. **Which arcs must survive a crash?** (the ones crossing the heavy bar)

**The common wrong turn** is drawing the org chart again — one node per desk, and nothing learned. Push
with: *a node is a thing that transforms a packet, not a person. Which of your desks is actually two
nodes? Which two are one?*

### Round 6 — Join up (10 min) ###

Tables connect their graphs into one network, as *Worked Example — the Order Flow in FBP* does for the
takeaway. Physically: put the sheets on the floor or a long table in cycle order — Onboarding,
Pre-Arrival, Arrival, Occupancy, Departure — and draw the arcs between them.

Expect the joins not to line up. **That is the finding**, not a failure: the port one table drew as an
output is not the shape the next table expected as an input.

### Debrief (10 min) ###

The hand-offs **between** tables are the largest fracture planes of all — larger than anything inside a
single stage, and nobody designed them.

Close on:

> **You have drawn a distributed system, and nobody has said the word yet.**

---

## Round 4 — who is in charge? (~10 min) ##

Slide: ***So Who Is in Charge?***, the section's last. Runs at the end of movement D — **after** block 2,
an hour after block 1.

Re-run **your block 1 flow** twice:

1. **With a conductor** holding a routing slip, who tells each desk when to act. *(orchestration)*
2. **With none** — each desk acting on whatever is in its in-tray. *(choreography)*

Then two questions, and only these two:

- **Where did knowledge of the whole process live?**
- **Who had to change when a step was added?**

Do not name orchestration or choreography. Process Automation starts on the next slide and names them
both; Day 1 promised the room would *feel* the difference before either word was defined, and this is
where that promise is kept.

**Keep the routing slip.** It reappears twice in Process Automation — as the conductor in the
orchestration diagram, and by name in the Routing Slip pattern — and being able to say *this is literally
the slip you held an hour ago* is the cheapest explanation in the section.

---

## If it is running long ##

In priority order, because the total is ~100 minutes against a ~75-minute historical budget:

1. **Round 6 (Join up) to 5 minutes.** Lay the sheets out, walk the joins yourself, do not have them draw.
2. **Round 3 (Break it) to 6 minutes**, one failure card per table instead of two or three.
3. **Round 1 to 15 minutes.** Costs quality everywhere downstream; do it last.

**Do not cut round 2 (Run it).** It is the shortest round and it is the one that makes the model true.
And do not cut the block 1 debrief — the ACID/BASE line has nowhere else to land.

---

## Materials the exercise leans on ##

| artefact | what it is |
|---|---|
| `resources/paper-notation-key.png` | the legend and the one rule; doubles as the handout |
| `resources/paper-guest-cycle.png` | the five stages, and which of them hands what to the next |
| `resources/paper-worked-flows-montage.png` | the four takeaway flows, the *see one* |
| `resources/Paper Office.drawio` | the 2021 glyph and role-card sheet — phone, inbox, outbox, fax, desk |
| `resources/*Errors.drawio` | the failure vocabulary the cards use, in the notation |

**`Paper Office` belongs here, not on a slide.** It defines *roles*, which no slide in the deck teaches,
and it is not linked from any outline. It is exercise material.
