# Paper Flow — Printable Materials #

Everything here is **A4 and mono-safe**. The palette survives a greyscale office printer, because
`carbon` and `annotation` differ in value and not only in hue.

**It has to travel.** No special kit, no pre-printed pads, nothing that cannot be run off in a hotel
business centre the morning of.

| § | item | quantity | form |
|---|---|---|---|
| 1 | Role cards | one per desk, per table | this file, cut up |
| 2 | Document cards | ~20 per table | `resources/paper-document-card.png`, 4-up |
| 3 | In-tray / out-tray sheets | two per desk | `resources/paper-tray-sheets.png`, 2-up |
| 4 | Failure cards | one deck for the room | this file, cut up |
| 5 | Notation key | one per table | `resources/paper-notation-key.png` |

---

## 1. Role cards ##

One per desk. Print, cut, and put the card **on the desk it names** — a delegate should be able to look
down and see what they are and what they do.

Each card is: **the desk's name**, then *what this desk does*, then **what it knows** — because the third
line is the file, and the file is the thing tables forget to draw.

### Hotel Onboarding ###

| desk | does | knows |
|---|---|---|
| **Hotel Manager** *(outside the agency)* | wants their hotel in our catalogue; answers questions about rooms and rates | their own rooms and rates |
| **Sales Team** | takes the enquiry, asks the hotel for details, hands the reply on | which hotels are being onboarded, and how far each has got |
| **Fax Operator** | sends and receives faxes; nothing else | the fax call log — what was sent, and whether a receipt came back |
| **Concierge** *(hotel side)* | compiles the hotel's room rates and returns them | the hotel's rate card |
| **Catalogue Maker** | adds an accepted hotel to the catalogue and republishes it | **the catalogue** |

### Pre-Arrival ###

| desk | does | knows |
|---|---|---|
| **Tourist** *(outside the agency)* | phones to book a stay; pays | where they want to go, and when |
| **Booking Team** | takes the call, creates a booking request, takes payment, confirms | the booking file — every request and its state |
| **Fax Operator** | faxes the request to the hotel; receives the accept or reject | the fax call log |
| **Concierge** *(hotel side)* | takes the request, checks the room list, accepts or rejects | **the room list** |

### Arrival ###

| desk | does | knows |
|---|---|---|
| **Guest** | arrives, presents credentials, receives a key | their own booking reference |
| **Front Desk** | files the booking confirmation, looks up the booking, requests and issues a key | **the guest stay file**, and which keys are out |

### Occupancy ###

| desk | does | knows |
|---|---|---|
| **Guest** | orders from room service; receives food and an invoice | their room number |
| **Concierge** | takes the room-service order and passes it to the kitchen | orders in progress |
| **Kitchen** | makes the food, sends it up, raises an invoice | the menu, and what has been cooked |
| **Front Desk** | files the room-service invoice against the guest | **the guest stay file** |

### Departure ###

| desk | does | knows |
|---|---|---|
| **Guest** | asks to check out, settles the bill, hands the key back | nothing but their room number |
| **Front Desk** | takes the stay file, totals the invoices, issues the bill, files the receipt | **the guest stay file** |
| **Housekeeping** | takes the room back and returns it to the room list | which rooms are ready |

> **Spare card, for any table that needs a sixth person:** **Post Room** — collects from every out-tray
> and delivers to every in-tray, twice a day. Nothing else. Giving a table a post room is the cheapest way
> to make latency visible, and it turns an abstract in-tray into a real one.

---

## 2. Document cards ##

Print `resources/paper-document-card.png` **four to an A4 sheet**, cut into half-A5. About 20 per table;
they will use more than you expect in round 2.

**The header strip is not decoration.** Three boxes across the top:

```
  TYPE                CORRELATION ID           REPLY-TO
```

It makes delegates use a correlation id without being told to, and it makes *reply-to* a property of the
document rather than a thing everybody just knows. In round 3 both become load-bearing: the correlation
id is how you tell a duplicate from a new request, and reply-to is why a resend goes to the right desk.

**Do not explain the header strip up front.** Let a table hit the problem in round 2 — two documents in an
in-tray and no way to tell which request one of them answers — and then point at the box they left blank.

---

## 3. In-tray and out-tray sheets ##

Print `resources/paper-tray-sheets.png`, **two to an A4 sheet**, cut in half. Two per desk.

A tray is a sheet of paper you put paper on. That is the entire mechanism, and its cheapness is the point
— you are asking a room to believe that a queue is a physical place, and a labelled sheet of A4 is more
convincing than a slide.

Lay them out so the **out-tray is on the desk's right and the in-tray on its left**, and orient tables so
one desk's out-tray is next to the next desk's in-tray. The geography does half the teaching.

---

## 4. Failure cards ##

Print one deck for the room, cut up. You deal 2–3 per table in round 3; the facilitator guide has the
table of which card suits which flow.

Each card is the instruction the table follows. **What it teaches is on the card too** — but on the back,
or in small print at the foot, because a table that reads "idempotency" before it draws the duplicate has
been robbed of the finding.

| # | the card says | it teaches |
|---|---|---|
| 1 | **The request goes missing.** It was sent. It never arrived. Nobody noticed for two days. | timeout, retry, In-Out-Retry |
| 2 | **Make a carbon copy before you send, and file it.** From now on, every document you send, you keep a copy of. | the **outbox** |
| 3 | **No receipt came back. Resend the fax.** | at-least-once — and therefore duplicates downstream |
| 4 | **This document was delivered twice.** Both copies are in the in-tray. Both look valid. | idempotency, de-duplication, the **inbox** |
| 5 | **The night porter is on a break.** This desk stops for two minutes. Everything else keeps running. | store-and-forward; the in-tray absorbs the outage; availability traded for latency |
| 6 | **This desk goes home.** Anything not written into a file is forgotten. | durable state — and Durable Execution, directly |
| 7 | **The guest checks out early, mid-flow.** Work already done for the rest of their stay has to be undone. | compensation, rollback, Tentative Operations |
| 8 | **Two clerks work the same in-tray.** They both reach in at once. | competing consumers — and what happens to ordering |
| 9 | **This in-tray holds only three documents.** A fourth cannot be put down. | capacity and backpressure — the FBP callback |

**Cards 3 and 4 are a pair.** Deal 3, wait about three minutes, then deal 4 to the same table. A table
that has just caused its own duplicate needs no further explanation of why idempotency exists.

---

## 5. The pinboard sheet — optional, and worth it ##

One sheet per table that **everyone may read and nobody may remove from**. Pin it up, or tape it to the
middle of the table.

It is a topic against the in-tray's queue, and it costs one sheet of paper. The moment someone asks *"how
do two desks both get this?"* — and someone always does, usually in round 2 — the answer is already on
the table.

Write at the top: **PINBOARD — read it as often as you like. Do not take it down.**
