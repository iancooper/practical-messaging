# Just Paper Hotels #

**It is 1985. There are no computers.**

You work for *Just Paper Hotels*, a booking agency. Guests phone you to book a stay; hotels send you
their room rates by fax; everything anyone knows is written on a piece of paper, and every piece of paper
is somewhere specific.

Your table has **one stage of the guest cycle**. Your job is to draw how the paper actually moves.

---

## The one rule ##

> **Every hand-off goes out-tray to in-tray. Nobody shouts across the office.**

If a desk needs to tell another desk something, it writes it down, puts it in its **out-tray**, and the
other desk **takes it from its in-tray**. No exceptions, including when it is obviously easier not to.

This will feel pedantic for about five minutes and then it will start showing you things.

---

## The notation ##

You have a key. It is six things:

| glyph | means |
|---|---|
| a desk | someone who does work; draw it as a box |
| an **in-tray** | work that has arrived and is not done yet |
| an **out-tray** | work finished here, not yet collected |
| a **file** | what this desk knows, written down, because the clerk goes home at five |
| a **heavy bar** | an organisational boundary — a different company, or a different building |
| **red dashed** / **solid** arrows | paper moving / a phone call or a fax |

**Number your steps** in one ascending sequence — 1, 2, 3 — in the order the *arrows* run, not per desk.
No repeats and no gaps. If two things genuinely happen at the same time, draw **one number branching to
two arrows**; do not use the same number twice.

That is the whole notation. You are allowed to invent more of it if you need to.

---

## Your stage ##

Five tables, five stages. You may assume the stages before yours already happened, and that they handed
you what is listed here.

| stage | what you are modelling | you may assume |
|---|---|---|
| **Hotel Onboarding** | how a hotel gets into our catalogue | nothing — this is where the catalogue comes from |
| **Pre-Arrival** | booking a stay | a catalogue of hotels |
| **Arrival** | check-in at the desk | a booking |
| **Occupancy** | *making a purchase from Room Service* | a key, and a room-service menu |
| **Departure** | *how I get my bill — show how the flow of bills reaches my file* | the invoices filed during the stay |

**Occupancy:** "the guest stays in a room" is not a flow. Model the room-service purchase; it has a
beginning and an end.

**Departure:** there is no worked example of this one anywhere. Yours is the first.

---

## What you will produce ##

Three artefacts, across the session. You are shown one of each for a different business first.

| # | when | what |
|---|---|---|
| 1 | round 1 | **the paper flow** — your stage, as desks, trays, files and arrows |
| 2 | round 3 | **the error variant** — the same flow when things go wrong |
| 3 | round 5 | **the graph** — the same flow again, re-expressed as a network |

---

## The rounds ##

### Round 1 — Model it (20 min) ###

Draw your stage on the A2 sheet. Every desk gets a name, an in-tray and an out-tray. Every hand-off gets
an arrow and a number.

Three questions worth asking yourselves as you go:

- **Where does that piece of paper physically sit while it is waiting?**
- **Who picks it up, and how do they know it is there?**
- **What does that desk know that nobody else does?** — that is a file.

### Round 2 — Run it (10 min) ###

One person per desk. **Execute** your model with document cards: fill one in, put it in the out-tray
sheet, and the next desk takes it from their in-tray sheet.

You will find something missing within two minutes. **Fix the model in pen** as you go — the crossings-out
are the interesting part.

### Round 3 — Break it (10 min) ###

You will be dealt two or three **failure cards**. Each one is something that goes wrong in a paper office.

Draw the **error variant** of your flow beside the original: what does the office do about it?

The vocabulary is the one you saw ten minutes ago — *make a carbon copy of the request*, *file the copy*,
*if no receipt, retry sending the fax*. You are not inventing new ideas here; you are applying the ones
the takeaway already uses.

### Round 5 — Re-express it (25 min) ###

Same flow, new notation: a **graph**. Information packets, nodes, ports.

- **What are the information packets?**
- **Where do the lookups live?**
- **Where is state stored?**
- **Which arcs must survive a crash?**

Same domain, same flow. Only the notation changes — resist the urge to redesign the business.

**A node is a thing that transforms a packet, not a person.** If your graph looks exactly like your org
chart, one of your desks is probably two nodes, or two of them are one.

### Round 6 — Join up (10 min) ###

Put your sheet with the others in cycle order and draw the arcs between the tables.

The joins will not line up. That is the finding.

### Round 4 — who is in charge? ###

Later in the day, you will run your block 1 flow twice: once with a **conductor** holding a routing slip
who tells each desk when to act, and once with **nobody** — each desk simply acting on whatever is in its
in-tray.

Two questions:

- Where did knowledge of the whole process live?
- Who had to change when a step was added?

---

## One thing that is deliberately missing ##

Nobody is going to give you a standard notation for this. You are going to invent one, and then later in
the day you will be shown that the rest of the industry already agreed on something very close to it.

That order is on purpose. Draw it your way first.
