# Practical Messaging — Day Two

A 101 guide to messaging. Ian Cooper. (X, BlueSky and Hachyderm: ICooper)

Day Two moves from the single message to the **flow**. It opens on **Flow and Reactive Programming** — how paper offices ran a distributed system with no `main`, why call-and-return breaks at service scale, dataflow and flow-based programming, and reactive architectures — puts delegates through a **paper-modelling exercise in two blocks, inside that section**, and closes on process automation: BPMN, orchestration vs. choreography, durable execution, and workflow engines.

*Day One now owns the whole of the single message: message-exchange patterns and fault repair in `## Conversations`, and message design — fat vs. skinny, reference data and event shape — in `## Designing Messages`. Versioning and observability are **not taught**; both are signposted in `## Next Steps`, versioning via the Managing Asynchronous APIs takeaway handout.*

---

## Why Event-Driven?

*Two slides. Day 1 taught the mechanics; this says what they were for, and hands into the design day.*

### Slide: Easy to Change, and Robust

You will hear four reasons to distribute a system — **performance and scalability**, **availability**,
**maintainability**, and applications that are **inherently distributed**. Strip the architecture words
away and two properties are what you are actually buying:

- **Easy to change** — ship a part without shipping the whole. *Independent deployability.* One team
  decides its own release candidate and is in production in hours, not at the end of a two-week release
  everyone had to agree a date for.
- **Robust** — keep working when something you depend on is not. *Guaranteed delivery.*

Both are bought with the same mechanism: **messages** — which is what yesterday was about.

▎ Two properties, one mechanism. Independent deployability is the prize; everything else is about not
giving it back.

Presenter notes: **Day 1 built the machinery; this is the first time the room is told what it was for.**
That order is deliberate — the argument used to open Day 1 and it was preamble there, in front of people
who had not yet seen a single mechanism. Here they have seen all of them, so it reads as a summing-up
rather than a promise. Say the four reasons, then say that all four reduce to two properties, and put the
two words on the board — they are the spine of today. **Deliberately not here:** the case *for
microservices*. The property is what matters and there is more than one way to buy it; a 2016 argument
about decomposing monoliths is not what this room needs in 2026. If someone asks, the honest answer is
that microservices are one example, they are not free, and yesterday was the bill. **Do not mention
Reactive** — it is ninety minutes away and it lands better as recognition.

### Slide: So How Do You Design One?

Yesterday answered *how do I send and receive reliably*. Today asks the harder question:

- **What shape is the system**, once no one call-and-returns its way through the whole use case?
- **Who is in charge** — and does anyone need to be?
- **Where does the work live** when a request is not a thread waiting for a reply?

You already know the cost side. Temporal coupling multiplies outages; store and forward converts a
failure into a delay. **That trade is settled.** What is not settled is what the system *looks like* when
you take it seriously — and that is today.

▎ Messaging doesn't remove the outage; it converts a failure into a delay. Now: what does a system built
that way actually look like?

Presenter notes: **This is the hand-off slide, and it should take two minutes.** Do not re-derive the
availability arithmetic — Day 1 §Coupling *Must We Both Be Up?* did it with a number (0.999⁴ = 0.996) and
the room owns it. Name it and move. The three questions are the three movements of the next section in
disguise, so do not answer any of them; the next slide is a section marker whose whole content is the
second question. If the room is cold first thing in the morning, the fastest warm-up is to ask what they
built yesterday and let somebody describe the outbox out loud.

---

## Flow and Reactive Programming

*The opening section of Day Two. Four movements: **A — how the office did it** (paper workflows: the
frame, the desk, the worked flows and their failures — the exercise's *see one*, closing with delegates
drawing the hotel's). **B — how would you build that?** (call and return, at object scale and at service
scale, ending in the distributed monolith — the wrong answer, offered second). **C — the formalism**
(dataflow, then flow-based programming; the same flows again as a graph, closing with delegates redrawing
theirs). **D — the name** (Reactive, which is what you have been building since yesterday morning).*

**Section goal:** stop drawing your system as call-and-return, and start drawing it as flow — and know
what that buys.

**The order is deliberate.** Flow comes first, on paper, before software is mentioned at all. Only
once delegates can draw a flow do we ask *how does this look in software?* — and call-and-return is then
the **failed answer** to a question they already have, rather than an opening complaint about a system
they have not yet been given an alternative to.

#note: This section is **load-bearing for the Paper Flow exercise**, which no longer runs after it but
**inside it**, in two blocks. Movement A teaches the desk / in-tray / out-tray notation and
the failure vocabulary, then hands straight to **block 1** — delegates draw the hotel on paper and break
it. Movement C teaches nodes, ports and lookups and works both flows as graphs, then hands to **block
2** — delegates redraw their own flow as a graph. Movement D closes on **round 4** (*who is in charge?*),
which is the hand-off into Process Automation. So each block's *see one* is the movement immediately
before it, and there is no long recap: round 0 shrinks to a pointer at slides the room has just seen.

---

### Slide: Flow and Reactive Programming

Section marker.

▎ Everything in this section is one question: *what is in charge?*

Presenter notes: **The first teaching slide of Day Two**, straight off *So How Do You Design One?*, which
asked *who is in charge — and does anyone need to be?* This marker is that question, alone on a slide. It
has to earn the room's attention in one line, and the line is the question, not the agenda. Do not list
the movements. The route is: watch an office do it with no
one in charge, do it yourself, then discover that the way you already build software puts somebody in
charge whether you wanted it or not.

---

#group: Movement A — How the Office Did It

### Slide: Paper Workflows

▎ "My life looked good on paper — where, in fact, almost all of it was being lived." — Martin Amis

Before computers, offices ran large distributed systems on paper. They handled concurrency, failure,
recovery and scale — and there was **no `main`**. Nobody held the whole process. Every desk did one
thing, and it did it because something arrived in its in-tray.

▎ The office was a distributed system with no god object. It worked for two hundred years.

Presenter notes: **The day opens here, before any software is mentioned.** This is not nostalgia and not a
metaphor — it is a worked example of the thing the whole section is about, and delegates have to be able
to draw in its notation within the hour. Resist any urge to say "of course, in software we…"; the movement
ends by *asking* that, and movement B answers it badly on purpose.

### Slide: The Frame

#image: photo — mailroom pigeonhole shelves stuffed with sorted mail and parcels
#image: photo — a worker pushing a mail-delivery cart through an office
#image: photo — an office desk with overflowing IN and OUT trays and a phone

In a mail room, **the frame** was the rack of pigeonholes: mail was sorted into it by floor, then a
worker took a cart round and delivered it.

- The frame creates **channels** you post to.
- Contents are delivered to whoever subscribes to that pigeonhole.
- The sender does not wait, and does not know who collects.

▎ That is a broker. We have been building one since Day 1.

Presenter notes: Direct callback to Day 1 §4 — channels, endpoints, the message pump. Say the words *this is a broker* out loud; the physical picture is what makes the pattern stick for people who have only ever seen it as a Docker container.

### Slide: The Desk — In-Tray, Out-Tray, File

**The notation for the rest of the day.** A desk is drawn as a box with three things:

- an **in-tray** — work that has arrived and not yet been done;
- an **out-tray** — work finished here and not yet collected;
- a **file** — what this desk knows, written down, because the clerk goes home at five.

Rules of the notation:

- A heavy vertical bar is an **organisational boundary**.
- Numbered steps show sequence. Red dashed arrows are paper moving; solid arrows are phone or fax.
- **Every hand-off goes out-tray to in-tray.** Nobody shouts across the office.

Two devices worth naming, because they are patterns you already know:

- **The order wheel.** A new order is clipped on and the wheel turned from the server's side to the
  kitchen's; completed orders turn back. Orders are made and returned **in sequence** — a queue, with
  the ordering guarantee made out of plywood.
- **The carbon-copy memo.** Writing on it creates a copy underneath. You keep a copy of everything you
  send; and you can read a file's message history to reconstruct its current state. That is the
  **outbox**, and it is event sourcing.

#image: notation key — the desk (in-tray, out-tray, file), the boundary bar, red-dashed vs. solid arrows, numbered steps, and the out-tray-to-in-tray rule drawn as two desks  [→ resources/paper-notation-key.png]
#image: photo — a large stack of manila file folders and papers
#image: photo — an order wheel in a restaurant kitchen  [⚑ Ian to supply — the only one of the three devices with no image in the deck]
#image: photo — a multi-part carbon-copy (NCR) form pad

Presenter notes: **New slide.** The notation was previously never taught — it was demonstrated in passing across a dozen unlabelled photographs. It has to be explicit now, because delegates draw in it within the hour and the exercise's hard rule (*every hand-off through a tray*) is what makes the fracture planes visible. The out-tray-to-in-tray rule is the whole exercise in one line.

#group: The Worked Flows — Just Paper Takeaway

### Slide: Worked Flow — Restaurant Onboarding

**Just Paper Takeaway.** Signing up a new restaurant, as paper: the value stream first, then the flow.

- Who the desks are: Restaurant Owner, Sales Team, Fax Operator, Chef, Catalogue Maker.
- Where the organisational boundary falls.
- Every hand-off annotated *Put X in Outbox* / *Take X from Inbox*.

#image: value-stream map — restaurant onboarding  [→ resources/Restaurant Onboarding Value Stream.drawio.png]
#image: flow diagram — restaurant onboarding  [→ resources/Restaurant Onboarding.drawio.png]

Presenter notes: **This is the first of four *see one* flows, and the slowest.** It is the diagram
delegates reproduce for the hotel in block 1, and the structural twin of Hotel Onboarding. Point at the
boundary bar and at two trays explicitly; those are the only two pieces of notation they need to start.
Walk the value stream first and the flow second, and say why: the value stream says *what the customer
gets*, the flow says *who has to do what to whom*. **Ask the room where the waiting is** before you show
the flow — the answer is always "at the boundary", which is the point.

### Slide: Worked Flow — Customer Order

**The customer orders.** The first flow that crosses into the customer's world, and the first with more
than one channel in it.

- The value stream for the order side of the business, end to end.
- Order taking is **phone, card machine and order pad** — three channels, one flow, and none of them
  is a computer.
- The order pad is the in-tray; the pad's carbon copy is the outbox; the till roll is the file.

▎ Three different media, one notation. The notation does not care what the arrow is made of.

#image: value-stream map — order flow  [→ resources/Order Flow Value Stream.drawio.png]
#image: photo — order taking (phone / card machine / order pad)
#image: flow diagram — customer order  [→ resources/Customer Order.drawio.png]

Presenter notes: Pace picks up now the notation is known — one diagram, walked, but briskly. The useful
observation here is the **channel heterogeneity**: a phone call is a synchronous conversation, the order
pad is a queue, the card machine is a third-party request/response. Delegates will hit exactly this in
the hotel — the guest phones, the booking form is paper, the card is a terminal. Name it so they are not
surprised by it in block 1.

### Slide: Worked Flow — Order Placement

**The order reaches the restaurant.** This is the flow with the external participant — the restaurant is
another organisation, on the far side of the heavy bar, reachable only by fax.

- The fax is a **send with no immediate answer**. The order goes out; the desk moves on.
- The state has to be **filed** before the fax goes, because the answer arrives minutes later and
  possibly to a different clerk.
- The reference number written on the fax is what matches the answer back to the file.

▎ Store, send, and be able to pick it up again. Two hundred years before anyone called it a saga.

#image: flow diagram — order placement  [→ resources/Order Placement.drawio.png]

Presenter notes: **The load-bearing flow of the four.** Storage, correlation and hand-off across an
organisational boundary are all here in paper form, and movement C re-expresses exactly this flow as a
graph — so what you say here is what the FBP worked example calls storage and correlation id. Do not use
those words yet. Say *file it before you send it* and *write the reference number on the fax*, and let
movement C supply the vocabulary for what the room already saw.

### Slide: Worked Flow — Order Confirmation

**The restaurant confirms back.** The reply arrives on its own, later, with no one waiting for it.

- Nobody blocked. The clerk who sent the fax did other work; the confirmation is picked up from an
  in-tray like anything else.
- The confirmation is matched to the filed order by its reference number, and only then does the
  customer get told.
- Put the four flows side by side: **no desk knows more than its own step, and there is no coordinator.**

▎ Four flows, no `main`. Every desk is doing exactly one thing, because something landed in its in-tray.

#image: flow diagram — order confirmation  [→ resources/Order Confirmation.drawio.png]
#image: montage — the four takeaway flow diagrams together  [→ resources/paper-worked-flows-montage.png]

Presenter notes: Land the montage — it is the close of the *see one* and the reason the four flows were
walked separately. **Ask the room the movement's question here:** if you were asked to build this, how
would you draw it? Take answers; they will describe an orchestrator or a set of services with a gateway
in front. Do not correct them — write it on a flipchart and leave it up through the exercise, because that is
movement B, and it is more powerful as their answer than as yours.

### Slide: How Do We Deal with Errors?

Paper had failure modes, and it had answers, and they are our answers.

| what goes wrong | what the office did | what we call it |
|---|---|---|
| the request goes missing | resend the fax | retry, In-Out-Retry |
| we don't know if it arrived | if no receipt, retry sending | at-least-once |
| we need to know what we sent | make a carbon copy before you send | the **outbox** |
| we need it after we go home | file the copy | durable state |
| it arrived twice | check the file before acting | idempotency, the **inbox** |

#image: flow diagram — restaurant onboarding errors  [→ resources/Restaurant Onboarding Errors.drawio.png]
#image: screenshot — a Fax Call Log table with error status codes highlighted
#image: flow diagram — customer order errors  [→ resources/Customer Order Errors.drawio.png]
#image: flow diagram — order placement errors  [→ resources/Order Placement Errors.drawio.png]

Presenter notes: This is the **failure vocabulary the exercise's failure cards use** — deliberately the same words, so round 3 is recall and not invention. The carbon copy *is* the outbox; the resend *is* the retry. The Fax Call Log is the good bit: a real error-status table, i.e. someone had to build observability for paper too. **This is the last slide before block 1**, so end on the table, not the diagrams: those five rows are what the failure cards will deal out.

#note: *ACID takes place at a desk; BASE takes place across desks* is **deliberately not spent here** —
it is the punch line of the Paper Flow debrief in block 1. Do not use it in this section.

### Slide: Now Do One — the Hotel, on Paper

You have seen the takeaway's four flows, and you have seen them fail.

**Now draw the hotel's.**

- One stage of the guest cycle per table — Onboarding, Pre-Arrival, Arrival, Occupancy, Departure.
- **Hard rule: every hand-off goes out-tray to in-tray.** Nobody shouts across the office.
- Then run it with cards, one person per desk. Then we break it.

#image: 'DON'T PANIC' in red on black (Hitchhiker's Guide reference)

Presenter notes: **Hand-off into Paper Flow block 1 (~45 minutes) — rounds 1, 2 and 3.** See
REDEVELOPMENT-PLAN §7. There is no round-0 recap any more: the *see one* is the four slides they have
just watched, so point back at *Worked Flow — Restaurant Onboarding* and start. Land *ACID takes place at
a desk; BASE takes place across desks* in this block's debrief — it is the payoff for the hard rule.
Delegates must **not** meet BPMN before the exercise; they are inventing a notation, and Process
Automation formalises it at the end of the day.

---

#group: Movement B — How Would You Build That?

### Slide: Object-Oriented Programming

You have now drawn a flow twice — once watching, once yourselves. Asked to *build* it, almost everyone
reaches for the same tool first. It is still on the flipchart from before the exercise, so let us name it
properly before we test it.

A class has a **role** with **responsibilities**; we capture responsibilities as behaviours; we
encapsulate the data those behaviours need inside the object; roles may be inherited via dynamic
dispatch.

#image: hand-drawn OO diagram — a class with role/responsibilities, encapsulated data, inheritance via dynamic dispatch, message passing

Presenter notes: Deliberately uncontroversial — everyone in the room has this, and they proposed it themselves before the exercise. Read their flipchart back to them first. It is here to be named, because the next three slides are about what happens when you scale it up and point it at a flow. **Movement B is the wrong answer, delivered fairly**: do not sneer at it, and do not tip the ending.

### Slide: Call and Return, and the God Object

- **Call and return.** `main` is the entry point. It invokes objects, which invoke other objects and
  return to their caller. Control is passed down a stack and handed back.
- **The god object.** The danger is one object — `Cart`, usually — that controls all the others. High
  behavioural coupling: it knows the whole use case, so it changes whenever any step of the use case
  changes.

▎ Somebody has to be in charge, and in call and return it is always `main`.

#image: hand-drawn call-and-return diagram — Main invoking Cart, Restaurant, Account, Menu, Payment, Order, Delivery objects

Presenter notes: A system passes control between classes to meet a use case, via message passing — "call and return" from `main` on down. **Contrast it directly with the flows they drew this morning**: no desk in the takeaway knew the whole process; `main` knows nothing else. Hold the phrase *knowledge of the whole process lives in one place*; movement D and the exercise's round 4 both come back to it.

### Slide: SOA Is OO at Macro Scale

**SOA** creates OO-like components: a service has a role and responsibilities exposed as
operations, and encapsulates the data those operations need. This is the Web Services approach — OO
as an architectural principle.

- Same idea, bigger unit: role, responsibilities, encapsulated data.
- We are taking the view that **microservices are SOA 3.0** — most of the best practice still applies.

▎ "A service should represent a self-contained functionality that corresponds to a real-world business
activity." — Nicolai Josuttis, *SOA in Practice*

#image: hand-drawn service-orientation diagram — a WSDL service with endpoint, binding, operations, input/output messages

Presenter notes: SOA takes objects to a macro scale. The Josuttis quote is the standard against which the next slide fails: he says align the service with a *business activity*. The next slide shows what you get when you align it with an *entity* instead. **A desk is a business activity** — the takeaway flows already satisfied Josuttis, which is worth saying out loud here rather than at the end.

#note: **This is the only place the Josuttis quote is read out.** It belongs here, where it is the
yardstick *Feature Envy* fails against — do not reintroduce it in Process Automation.

### Slide: Feature Envy — You Built a Distributed Monolith

- We expose significant **resources** and the operations you can perform on them — usually CRUD.
  Entity services: `Cart`, `Restaurant`, `Account`, `Menu`, `Payment`, `Order`, `Delivery`.
- **Feature envy.** Domain logic has to coordinate across those resources, so it ends up on the client,
  in the API gateway, or in the `Cart` service — anywhere but in the individual services.
- Because we made OO large, we reached for call and return via a `main` method at the API gateway.

▎ The gateway is `main`. You have distributed the objects and kept the god object.

#image: hand-drawn entity-services diagram — Device → API Gateway → Cart, Restaurant, Account, Menu, Payment, Order, Delivery

Presenter notes: **This is the slide the movement exists for, and it is now an answer rather than an opening complaint.** The room proposed this shape an hour ago; here is what it costs. The distributed monolith is not a failure of nerve, it is what call-and-return *becomes* when you distribute it — and it gives back exactly the independent deployability this morning's opener called "the prize". **End on the comparison, not on a question:** you drew a flow this morning with no coordinator, and then you built one with a coordinator in the middle. So what would it take to build what you actually drew? Movement C is the answer.

---

#group: Movement C — The Formalism

### Slide: Data Flow Programming

**Dataflow programming** conceptualises a program as a directed graph: operations are **nodes**,
connected by **arcs** through which data flows. A node performs its operation when its input data is
available — not when someone calls it.

- Nothing is in charge. There is no `main`.
- You already use one: the Unix command line. Pipes and filters.

▎ In call and return, control moves and data sits still. In dataflow, data moves and control sits still.

#image: hand-drawn dataflow graph — nodes/vertices connected by arcs, with operation and data annotations

Presenter notes: Perhaps the oldest expression of the reactive approach, and **the formal version of the paper flow they drew themselves an hour ago** — say that in the first sentence, because it is the whole reason this movement lands where it does. Unlike OO — where state is co-located with behaviour in the node — data *moves between* transformations along arcs. **The desk is a node; the tray is an arc; the file is the node's state.** Draw that mapping on the board and leave it up for the rest of the movement.

### Slide: Nodes, Ports and Firing

A node is a **black box** with **ports**.

- It is **activated** — *fired* — when a packet arrives on an input port's arc.
- It computes.
- As a black box, it reports what happened by raising an event on an **output port**, which others may
  react to.
- Generally a node is **single-threaded**. Concurrency comes from having many nodes, not from one node
  doing many things.

**Packets are just data.** No special requirements — primitive or compound values travelling between
ports.

▎ It is *reactive* because it fires in response to an event.

#image: hand-drawn diagram — a dataflow node as a black box with input/output ports (activate → process → push)
#image: hand-drawn diagram — two nodes passing data packets between ports

Presenter notes: Single-threaded-node / concurrency-from-many-nodes is the clerk rule: one clerk does one document at a time, and you get throughput by hiring clerks. Every delegate has just enacted this with cards.

### Slide: Capacity, Backpressure and Node Lifetime

- **Node lifetime.** In classic dataflow a node lives from activation until it has pushed its answer.
  Push = something arrived and there is work to do. Pull = a sink asked for work.
- **Capacity.** We do not activate a node to read input if there is no space on its output. Links with
  infinite capacity exist only in theory.
- Therefore: **backpressure**. A full buffer means either slow the producer, or drop data.

#image: hand-drawn diagram — an arc/link pipe with buffers for pipelining; push/pull, synchronous/asynchronous

Presenter notes: Arcs connect nodes; buffered arcs allow asynchrony — a node can push its output onto the buffer while the downstream node is still busy, which is what enables parallelism. Throughput is then limited by the slowest node. None of this is *required* for dataflow: a synchronous, unbuffered, single-threaded pipeline is a valid dataflow program. Push is a hot source you listen to (mouse clicks); pull means nothing is generated until a sink pulls the chain. Introduce backpressure and load-shedding as the two available answers here — movement D turns them into a decision. If a table got *"this in-tray holds only three documents"* in block 1, this is their card, named.

### Slide: Flow-Based Programming

▎ "Everything flows and nothing stays." — Heraclitus

**Flow-Based Programming (FBP)** is a subclass of dataflow. Where dataflow *may* be synchronous, FBP
always is not:

- **Always asynchronous.**
- **Multiple input ports** per component.
- **Bounded buffers**, and therefore backpressure when they fill. A component can test whether it can
  send to `out`, and decide whether to halt or ignore.
- **Node lifetime:** a component keeps running while there is work on an input queue, and **suspends**
  rather than terminates when there is none.

#image: hand-drawn FBP diagram — a component with in/out ports, an information packet, and a connector
#image: hand-drawn FBP diagram — packet lifetime and process-and-wait annotations
#image: hand-drawn FBP diagram — multiple writers on an in-port, single writer on an out-port, multiple ports

Presenter notes: Merged from three slides. The deltas from dataflow are the whole content — do not re-teach dataflow. Suspend-not-terminate is the one to dwell on: it is the message pump from Day 1 §4.3, described from the other side — and it is the clerk who stays at the desk all day rather than being hired per document.

### Slide: FBP — Initial Information Packets

An **IIP** is a packet a component receives at start-up rather than from an upstream component —
configuration, or a starting value. Control packets bracket a stream into groups.

#image: hand-drawn FBP diagram — an initial information packet (iip_in) and control-packet bracketing

Presenter notes: MQTT **retained messages** are a way of emulating the IIP idea — the broker holds the last value on a topic so a late subscriber gets state immediately rather than waiting for the next publish. Same problem: how does a node that just started know anything? The paper answer is the standing instruction pinned above the desk.

### Slide: FBP — Where Do Lookups Live?

A component needs data it was not sent. Two answers, and it is the same choice as Day 1 §6.2 *Reference
Data*.

- **Ask for it.** Add a lookup port: query out, pause, response in. The component stops until the answer
  comes back — **the walk of shame**. On-demand, and now you are temporally coupled to whoever answers.
- **Build it in advance.** A **Build Lookup** node listens to the stream that owns the data and
  maintains a table the working component reads locally. In-advance — no pause, no temporal coupling, and
  the copy is behind by a broker hop.

▎ Same decision as reference data, drawn as a graph — and the same answer: hold the copy.

#image: hand-drawn FBP diagram — components A and B; does A need data from another node?
#image: hand-drawn FBP diagram — components A and B with lookup ports (query / pause / response) — the 'walk of shame'
#image: hand-drawn FBP diagram — a 'Build Lookup' node listening to A, pre-caching a lookup table for B

Presenter notes: This is the direct callback to Day 1 §6.2 *Reference Data* — on-demand versus in-advance, and the CAP cost of each. Delegates met the decision in prose at the end of Day 1 and meet it as a picture now. **Give the same verdict:** the Build Lookup node is the recommended shape; the lookup port is what you use when the data cannot be replicated. The paper form is the Catalogue Maker: a desk whose whole job is keeping a local copy current so nobody has to walk.

#group: The Worked Flows Again — as Graphs

### Slide: Worked Example — Onboarding in FBP

**The first flow you saw on paper, drawn as a graph.** Request/response with an external participant who
is a fax machine.

- **Storage.** A component takes work from the `request_details` port but cannot forward to
  `restaurant_details` without an answer from `fax_in` — so we store the workflow state, in case we
  crash before the response arrives. *That is filing it before you send it.*
- **Correlation.** To match the response to that saved state we send a **correlation id** on the packet
  to `fax_out`; the restaurant returns it on the packet from `fax_in`; we use it to look up the stored
  workflow. *That is the reference number written on the fax.*
- **Lookup.** We build a store from packets raised by another component, to act as the lookup table for
  information needed to process a request. *That is the Catalogue Maker.*

▎ Nothing here was invented. It was named.

#image: hand-drawn FBP 'Onboard Restaurant' flow  [→ resources/flowbased_onboard_restaurant.png, resources/FBP Onboard Restaurant.drawio]

Presenter notes: **Walk the paper diagram and the graph side by side if the room allows it** — the point
of the movement is that they are the same drawing. Storage, correlation and lookup are the three things
the paper flow already had: the file, the reference number on the fax, and the catalogue. Say each pair
out loud; the italic lines on the slide are there so delegates can do the mapping themselves afterwards.
**This is the diagram *Putting It Together* annotates** at the end of the day, so leave it clean here — the
exchange-pattern labels are that section's job, not this one's.

### Slide: Worked Example — the Order Flow in FBP

**Order, placement and confirmation as one graph.** The three flows delegates saw separately on paper
compose into a single network — which is the thing paper could not show you.

- **Order Food** — the order enters the network. Ports in, packets out; nobody is called.
- **Order Placement** — the fax hand-off across the organisational boundary, the same store-and-correlate
  shape as onboarding.
- **The whole network.** Put them together and the confirmation is just another packet arriving on
  another port. There is no step at which anything is "in charge".

▎ Three flows on paper. One graph. The composition was always there — paper just could not draw it.

#image: hand-drawn FBP 'Order Food' flow  [→ resources/flowbased_order_food.excalidraw, resources/FBP Order Food.drawio]
#image: hand-drawn FBP 'Order Placement' flow  [→ resources/flowbased_order_placement.png, resources/FBP Order Placement.drawio]
#image: hand-drawn FBP overall 'Order Flow'  [→ resources/flowbased_order_all.png]

Presenter notes: The **composition** is the content here, and it is the argument for the notation: four
separate sheets of paper turn out to be one network, because the arcs were always the same arcs. This is
also the slide that makes block 2 tractable — delegates redraw their own stage and the tables' graphs
then join up in the debrief exactly as these do. **Do not rush the overall diagram**; it is the one they
are about to imitate.

### Slide: Worked Example — When It Fails, and What the Arcs Really Are

**The error variant, as a graph.** The same failures from *How Do We Deal with Errors?* — the request
goes missing, no receipt comes back, the same document arrives twice — expressed in ports and packets.

- Retry is a packet sent again on the same port; the correlation id is what stops it being a second
  order.
- The stored workflow is what makes retry safe, because the answer can arrive after a crash.
- The failure is **local to a node**. The graph does not unwind; the packet waits.

Then the last move of the movement: **make the arcs middleware and the nodes processes.**

▎ An arc that survives a crash is a queue. A node that survives a crash is a service. You have just
drawn a distributed system.

#image: hand-drawn FBP 'Order Food Errors' flow  [→ resources/flowbased_order_food_errors.png, resources/FBP Order Food Failure.drawio]
#image: hand-drawn FBP diagram — nodes as processes connected by Message-Oriented Middleware (MoM)

Presenter notes: **The summit of movements A and C.** Two beats, and the second is the hinge into
movement D — do not let the failure discussion eat it. The MoM diagram is where the whole section turns:
everything delegates have drawn on paper and in graphs becomes the thing Day 1 spent a day building.
Deliberately **do not say "Reactive"** here; movement D is the reveal.

### Slide: Now Do One — the Hotel, as a Graph

You have seen the takeaway flow four ways: **as paper**, **as errors on paper**, **as a graph**, and
**as a graph that fails**.

**Now draw the hotel's as a graph.**

- Your own flow from this morning, re-expressed: information packets, nodes, ports.
- Where do the lookups live? Where is state stored? Which arcs must survive a crash?
- Then join your graph to the next table's.

#image: 'DON'T PANIC' in red on black (Hitchhiker's Guide reference)

Presenter notes: **Hand-off into Paper Flow block 2 (~45 minutes)** — the FBP re-expression, which was
the closing task of the original exercise deck (s009) and never had room. See REDEVELOPMENT-PLAN §7.
Delegates redraw the stage they modelled in block 1, so there is no new domain to absorb; the work is
purely the change of notation, which is the point. The debrief joins the tables' graphs into one network,
mirroring the *Order Flow in FBP* slide — and the hand-offs *between* tables are the largest fracture
planes of all. Still **no BPMN**.

---

#group: Movement D — The Name

### Slide: Reactive Architectures

Section marker. Reactive derives from **reactive programming**, not from OO.

Presenter notes: The room has now drawn the same system four times, in two notations, and made it fail.
Movement D adds no new mechanism — it supplies the name, and shows that somebody published it in 2014.

### Slide: The Reactive Manifesto

Published September 2014 by Jonas Bonér, with Erik Meijer, Martin Odersky, Greg Young, Martin Thompson,
Roland Kuhn, James Ward and Guillaume Bort. It defines an architectural style — **Reactive
Applications**. Write applications that:

- **react to events** — the event-driven nature enables everything else;
- **react to load** — scalability rather than single-user performance;
- **react to failure** — resilient systems that recover at all levels;
- **react to users** — combine the above into an interactive experience.

Four traits: **Responsive** (responds in a timely manner), **Resilient** (stays responsive in the
presence of failure), **Elastic** (stays responsive under varying workload), **Message Driven** (relies
on asynchronous message passing). — reactivemanifesto.org

**You have met two of these already, under other names.**

- **Resilient** is what we called **robust** on Day 1: stay working when something you depend on is not.
- And *easy to change* is in the manifesto's own words: "Systems built as Reactive Systems are more
  flexible, loosely-coupled and scalable. This makes them easier to develop and **amenable to
  change**."
- **Elastic** and **Responsive** are the two Day 1 did not have names for.
- **Message Driven** is the mechanism — the same one, all the way through.

▎ Two properties, one mechanism. Somebody wrote it down in 2014.

Presenter notes: **This is the payoff of *Easy to Change, and Robust*, and neither day has said the word "Reactive" before now, so it lands as recognition rather than repetition.** One caveat since the timing pass: the two properties are now named **this morning** rather than yesterday, so the gap is ninety minutes, not a day — the recognition is weaker and you have to work for it. **Ask the room to give you the two properties back from memory before you show the mapping**, and do not re-read the opener's wording. Present the manifesto as their own two properties, already published, with two more added. Also: **not just the actor model** — these ideas have expression well beyond it, and following Helland, many implementations are possible.

### Slide: Reactive Traits — Value, Form, Means

A useful way to read the four traits:

- **Responsive** is the **value** — the thing the user actually gets.
- **Resilient** and **Elastic** are the **form** — the shape that delivers it under failure and load.
- **Message Driven** is the **means** — how the form is achieved.

**Attribution.** This is a **gloss, not manifesto text.** The manifesto names the four traits and says
Message Driven is the foundation the others rest on, but it never assigns value / form / means. The
split is how Bonér has presented it in talks, and it is a defensible reading — say so on the slide
rather than letting it read as a quotation.

Presenter notes: Fixed attribution — the old slide showed four words and three labels with no source, which reads as if quoting. If you would rather not carry someone else's gloss, this is the most cuttable slide in the movement; the manifesto slide above stands on its own.

### Slide: Message Passing

**Message passing** is an asynchronous method of communication: both parties need not be simultaneously
present. Mail is delivered to a **mailbox** of some form, for later retrieval.

#image: hand-drawn diagram — a component with incoming and outgoing message arrows (asynchronous message passing)

Presenter notes: Message passing invokes behaviour on a computer. In contrast to calling a program by name, it uses an object model to separate the general function from the specific implementation — the invoker sends a message and relies on the object to select and execute the code. The justifications fall into two categories: encapsulation and distribution. Point back at the frame: a mailbox is a pigeonhole.

### Slide: Microservices Are Reactive Architectures

We separate data from behaviour, activate a component in response to work being on a queue, process it,
and send an outgoing message. That is a node with ports. That is a desk with trays.

- A component's inputs are commands and events; its outputs are events.
- Nobody holds the whole process. There is no gateway `main`.

▎ **This morning called independent deployability the prize. This is how you stop giving it back.**

#image: hand-drawn message-passing diagram — a component with in-request / out-request / out-result ports (command vs event)

Presenter notes: **Close the loop explicitly** — name *Easy to Change, and Robust* from this morning's opener out loud. The through-line to draw on the board: call and return puts knowledge of the whole use case in one place, so one place has to change every time the use case does; flow puts each step in its own component reacting to its own input, so a new step is a new subscriber. Reactive architectures derive from reactive programming, not OO — "everything flows". This is also the slide that answers movement B: the distributed monolith was entity services with a gateway `main`; this is the same distribution with the god object removed.

### Slide: Partitioning and Dataflow

- **Partition to exploit parallelism** — find the tasks that could run concurrently and give each its
  own component.
- **Coordinate dataflow** — "orchestrate a continuous steady flow of information", dividing the system
  by **behaviour**, not by structure.

▎ Divide by verb, not by noun. Entity services divide by noun — that is Feature Envy.

#image: hand-drawn FBP diagram — Checkout and Take Payment components with purchase / priced / payment-due messages

Presenter notes: The direct answer to movement B. Reactive inherits from dataflow: conceive the application as a graph of nodes operating on data flowing through it. It shines for data-driven applications composed from components in workflows — let components subscribe to each other's event streams and consume published facts asynchronously, on demand. **Every desk in the paper office was a verb**: Take Order, Send Fax, Make Catalogue. That is why the office had no god object and the gateway does.

### Slide: Bulkheads

In a synchronous conversation both parties must be up, so a fault **propagates** back up the chain and
we are brittle. In an asynchronous conversation it does not: the work queues up instead.

- The sender sends and returns immediately, whether or not the receiver is up.
- Messages wait until the receiver asks for them; results go to a queue for collection.
- The failure is contained in one compartment — a **bulkhead**.

▎ The outage became a delay, not a failure. Again.

#image: hand-drawn FBP diagram — Take Payment crossed out; work queues up on a fault (the bulkhead)

Presenter notes: This slide absorbs the cut *SOA — Faults Propagate* — the fault propagation claim is made here, where it is immediately answered, instead of standing alone. And the callout is Day 1 §Coupling's central argument arriving for the third time: availabilities multiply only under temporal coupling; store-and-forward breaks the chain. This requires storage and retransmission — usually Message-Oriented Middleware. If a table drew *"the night porter is on a break"* in block 1, this is that card with a name on it.

### Slide: When the Pipe Fills — Backpressure or Load-Shedding

Buffers are finite, so when a consumer cannot keep up something has to give. There are exactly two
answers, and it is a **decision**, not a default.

| | **Backpressure** | **Load-shedding** |
|---|---|---|
| what happens | slow the producer down | discard messages |
| what you lose | latency | data |
| choose when | data loss is unacceptable and extra latency is tolerable | volume is high and you only need a sample |
| example | blocking retry against a database you cannot reach | 1,000 metrics a second when 10 meets the SLA |

- **Backpressure** is the producer feeling backward pressure from the pipe, forcing it to slow until the
  pressure alleviates. Blocking retry creates it as a side effect: retrying a connection slows
  consumption, which fills the queue, which slows the producer.
- **Load-shedding** can discriminate — prioritise, and discard only the less valuable data.

#image: hand-drawn message-passing diagram — push vs pull, with backpressure annotations on the ports
#image: hand-drawn message-passing diagram — load-shedding, dropping messages on a fault

Presenter notes: Merged from two slides. The idea was introduced as a mechanism back in *Capacity, Backpressure and Node Lifetime*; here it becomes the choice. Worth asking the room which one their current system does — the answer is usually "neither, it falls over", which is a third option nobody chooses on purpose.

### Slide: Putting Reactive Together

The pieces, and how they compose.

- **Message passing** decouples in time — the bulkhead.
- **Backpressure and load-shedding** handle a consumer that cannot keep up.
- **Circuit breaker** handles a downstream that is failing rather than slow: stop consuming, stop
  hammering it, resume when it recovers.
- **Scale out, not up** — a supervisor fans work out to worker instances; that is elasticity, and it is
  competing consumers from Day 1 §4.3.

▎ Responsive under failure, responsive under load. The traits are these mechanisms.

#image: hand-drawn message-passing diagram — circuit breaker: stop consuming on a fault
#image: hand-drawn 'scale out not up' diagram — a Supervisor fanning out to Worker instances
#image: hand-drawn 'scale out not up' diagram — Supervisor to Workers with scale-out and fault regions

Presenter notes: The circuit-breaker and scale-out diagrams used to be orphaned images under a "recap" heading and were never really taught. Give them a sentence each. Land the callout: Resilient and Elastic are not aspirations, they are the four mechanisms on this slide.

### Slide: So Who Is in Charge?

The section opened on one question. Here it is again, and now you can answer it — but answer it with
people, not slides.

**Take your flow from this morning and run it twice.**

- **With a conductor.** One person holds a routing slip and tells each desk when to act.
- **With none.** Every desk acts on what is in its in-tray, and nothing else.

Then: **where did knowledge of the whole process live?** And **who had to change when we added a step?**

▎ You have just invented orchestration and choreography. The next section gives them their names — and a
notation.

Presenter notes: **Paper Flow round 4, ~10 minutes, and the hand-off into Process Automation** — it sits
here rather than at the end of block 2 so its payoff does not go cold across the whole of movement D. See
REDEVELOPMENT-PLAN §7. **Nothing anywhere in the course has planted these two words, deliberately** — so
do not call back to anything. Let the room invent the distinction here, and give it the names only after
they have run it both ways. Delegates still must **not** have met BPMN — they are about to be shown that the
thing they just enacted has a standard notation, which only works if it is a reveal.

---

## Process Automation

### Slide: Your Flow, in the Standard Notation

▎ You drew this an hour ago. Here it is again, in a notation the rest of the industry already reads.

**Pre-Arrival, as you modelled it on paper — and the same flow as BPMN.** Same three participants, same
hand-offs, same numbered steps:

| what you drew | what it is called |
|---|---|
| a desk | a **task**, sitting in a **lane** |
| the heavy vertical bar | a **pool** boundary |
| a red dashed arrow between an out-tray and an in-tray | a **message flow** |
| a numbered step from one desk to the next inside the bar | a **sequence flow** |
| a folder | the state a task reads and writes |
| the conductor holding the routing slip | the **process**, and its **token** |

Nothing new happens in this section. It gives names to what the room already built.

#image: side by side: the Pre-Arrival paper flow as delegates have it, and the same flow as a BPMN collaboration — three pools, Guest / Just Paper Hotels (Booking Team, Fax Operator) / The Hotel  [→ resources/bpmn-your-flow-side-by-side.png]

Presenter notes: **This slide exists to keep the promise made on the previous one.** Delegates have just run their own flow with a conductor and without one, and were told that the next section gives those two things their names *and a notation* — so do not open on BPMN primitives, open on their own drawing. Put the paper version up alone first and ask what a stranger could not tell from it; then reveal the BPMN. **The mapping table is the teaching move: they already have every concept, they lack only the vocabulary.** The primitives on the next two slides then arrive as *what you needed in order to draw that*, rather than as a legend to be memorised. Do not read the table out — walk the diagram and point at each pair.

### Slide: BPMN

**BPMN** (Business Process Management and Notation) is a visual language for diagramming business processes clearly, in a standardized and comprehensive way.

- A **start event** begins a flow; an **end event** terminates it (and may throw a message).
- **Sequence flow** arrows show the path of execution.
- An **event** begins, ends, or interrupts a flow; a **task** is where work gets done.

#image: BPMN diagram — an 'Order Food' process (Enter Location, Choose Restaurant, Add Menu Choices, Checkout) ending with a message event  [→ resources/bpmn-ordering-flow.png]

Presenter notes: Second example, and deliberately the *takeaway* domain rather than the hotel — the see-one, so the room gets the notation twice over on two flows it already knows. It is also an editable resource, which the hotel diagrams are not.

### Slide: BPMN — The Elements

A BPMN diagram is six things: **Start Event**, **End Event**, **Activity** (Task or Sub-process), **Gateway**, **Event**, and the arrows that join them.

There are two kinds of arrow, and the difference between them is what the rest of this section is about:

- **Sequence Flow** — control moving *within* one participant. **The token follows it.**
- **Message Flow** — a message crossing *between* participants. **No token crosses it.**

▎ Sequence flow is what happens at a desk. Message flow is what happens between desks.

#image: BPMN diagram — two pools; in the first, start event, task, message event, a parallel gateway splitting to two tasks, merge gateway, end event, with each element named; a message flow from the second pool into the message event  [→ resources/bpmn-elements.png]

Presenter notes: **The load-bearing line is the token one**, so say it out loud: it is *ACID at a desk, BASE across desks* from block 1's debrief, in BPMN's own vocabulary, and it is the distinction that makes orchestration-vs-choreography obvious twelve slides from now rather than arbitrary.

### Slide: BPMN — Tasks, Events and Gateways

Three of the six have variants. They are reference, not material:

- **Tasks** — atomic activities: Generic, **Service** (uses a service), **Receive** (waits for a message), **Send**, **User** (human, via software), Manual (human, not via software), Business Rule, Script. Markers: Loop, Transaction.
- **Events** — start, end, or interrupt a flow: None, **Message**, **Time**, Signal, **Compensation**, Conditional, Escalation, Parallel, Cancel.
- **Gateways** — branch and converge sequence flow: **Exclusive** (X, one path), Inclusive, **Parallel** (+, split/join), Complex, Event-based (an event picks the path).

▎ Six of them do nearly all the work: **Service** and **Receive** tasks, **Message** and **Timer** events, **Exclusive** and **Parallel** gateways.

#image: the six BPMN elements this deck actually uses — Service and Receive tasks, Message and Timer events, Exclusive and Parallel gateways, each glyph named and glossed in one line  [→ resources/bpmn-the-six.png]

Presenter notes: **Do not read the lists.** Teach the six on the figure — they are the only ones used anywhere in this deck, and every diagram in this section is built from them, which is the point worth making out loud. The bolded entries in the three bullet lists are those same six. Everything else is on the reference card in the pack: a lookup table wants to be in the delegate's hand, not on the screen — the same test that sent Managing Asynchronous APIs and the routing patterns to handouts.

#note: ☐ **Delegate reference card** — the full task, event and gateway legends on one A4 side, in the pack, and now their only home. Phase 3 layout job, not a redraw: `Task Types.drawio`, `Event Types.drawio` and `Gateway Types.drawio` are editable, and for print the plain black-on-white reads fine.

### Slide: Workflow Patterns

*Workflow Patterns* — van der Aalst, ter Hofstede, Kiepuszewski, Barros (2000): 5 basic + 15 advanced patterns. *Workflow Control-Flow Patterns: A Revised View* — van der Aalst, Mulyar, Russell, ter Hofstede (2007): 23 new patterns.

Presenter notes: The five that follow are the ones the closing slide, *Implementing Workflow Patterns*, maps onto the three implementation styles — so the vocabulary is load-bearing, not trivia. Every one of the five is somewhere in the flow the room drew this morning; say that, and the five slides become recognition rather than definition.

### Slide: Pattern 1 — Sequence

One activity follows another. BPMN: connect two tasks with a sequence-flow arrow. Easy to model and execute. Example (Booking Team): Take the Call → Create Booking Request.


#image: BPMN diagram, two tasks in the Booking Team lane: Take the Call → Create Booking Request  [→ resources/bpmn-hotel-p1-sequence.png]

### Slide: Pattern 2 — Parallel Split

One path splits into two or more concurrent branches. BPMN: a **Parallel Gateway** (+) forks. Example: once the hotel accepts, Take Payment + Prepare Booking Confirmation.


#image: BPMN diagram: Booking Accepted, a parallel gateway splitting to Take Payment and Prepare Booking Confirmation  [→ resources/bpmn-hotel-p2-parallel-split.png]

### Slide: Pattern 3 — Synchronization (Join)

Wait until multiple concurrent branches complete. BPMN: a **Parallel Gateway** joins. Example: the guest is not told until payment has cleared *and* the confirmation is ready.


#image: BPMN diagram: Take Payment and Prepare Booking Confirmation merging into a parallel join, then Confirm to Guest  [→ resources/bpmn-hotel-p3-join.png]

### Slide: Pattern 4 — Exclusive Choice

Choose one path based on a condition. BPMN: an **Exclusive Gateway** (X) with condition expressions. Example (Concierge): Check Availability → Accept Booking **X** Reject Booking.


#image: BPMN diagram: a message start, Check Availability, exclusive gateway to Accept Booking or Reject Booking  [→ resources/bpmn-hotel-p4-exclusive-choice.png]

Presenter notes: This one is drawn on their own paper flow already — *Respond with Booking Accept/Reject*, step 7. Point at it.

### Slide: Pattern 5 — Simple Merge

Merge non-concurrent paths back into one. BPMN: a converging sequence flow — no gateway needed if no synchronization is required. Example (Guest): the confirmation arrives, or the guest gets tired of waiting and chases; either way, Check the Booking → Pack for the Trip.


#image: BPMN diagram: a message event (Confirmation Received) and a timer event (Chase the Agency) converging on Check the Booking with no gateway, then Pack for the Trip  [→ resources/bpmn-hotel-p5-simple-merge.png]

### Slide: Process = Orchestration

A **Process** describes a sequence/flow of activities. In BPMN it is a graph of flow elements (a sequence flow of activities, events, gateways).

A Process is an **orchestration** — focused on a **single participant's perspective**:

- The sequence flow represents control of a process. Like writing your own script.
- The **token** represents state for an instance.
- Control flow, state and decisions are **all local to the orchestrator**.
- Generally a process orchestration lives within an address space (not distributed) — an embedded workflow or an external process manager, often a state machine or a workflow engine.

#image: BPMN diagram — a Checkout Basket process (Create Basket, Validate Choice, Price Basket, Validate Delivery/Payment)  [→ resources/bpmn-shopping-as-sequence.png]

Presenter notes: This is the conductor from round 4 — one person, holding the routing slip, who knows the whole process. Name the callback; the room enacted it forty minutes ago.

### Slide: Tokens

- A **token** represents an instance of a process.
- A token flows down the process; it is the state of the process for that instance.

#image: BPMN collaboration — Customer and Shopping pools with message flows (Begin Shopping, Basket Price, Valid Basket)  [→ resources/bpmn-shopping-collaboration.png]

### Slide: Hotel Example — BPMN Orchestration (Guest Pool)

The guest's journey as an orchestration.


#image: BPMN diagram, the Guest pool: phone the agency, wait for the confirmation, chase on a timer, then pay — or book elsewhere  [→ resources/bpmn-hotel-guest-pool.png]

Presenter notes: In the demo we emulate this with HTTP calls (same as web/mobile). It's "in process" — we manage the token and its state through the flow. We show where we wait to receive a message. Debugging: we pause awaiting a message from another system, and can't see how the received values were set, or why we do/don't receive a message — for that we'd need the sender.

### Slide: Hotel Example — BPMN Orchestration (Just Paper Hotels Pool)

The agency as an orchestration, initiated by a message. Two lanes: **Booking Team** and **Fax Operator**.


#image: BPMN diagram, the Just Paper Hotels pool with Booking Team and Fax Operator lanes: create the booking request, fax it, receive accept/reject, take payment, confirm  [→ resources/bpmn-hotel-agency-pool.png]

Presenter notes: We send messages to act (message icon) and wait to receive messages (start and end). Same debugging blind-spot — to debug the flow to the guest we'd need breakpoints in both, which is fine if we own both, but not if they belong to different teams (we'd have to deploy their code). **This is the pool delegates modelled**, so let them tell you what belongs in each lane before you show it.

### Slide: Hotel Example — BPMN Orchestration (The Hotel Pool)

The hotel as an orchestration, initiated by a message. Lanes: **Concierge** and **Front Desk**.


#image: BPMN diagram, The Hotel pool with Concierge and Front Desk lanes: take the booking request from the inbox, Check Availability, exclusive gateway to Accept or Reject  [→ resources/bpmn-hotel-hotel-pool.png]

Presenter notes: Same pattern — send messages to act, wait to receive. To debug the flow across the agency and the guest we'd need breakpoints in all three. Fastest of the three slides: the shape is now familiar, which is the point of showing it a third time.

### Slide: Hotel Example — Pools and Lanes

#image: BPMN diagram, one pool with five lanes (Guest / Booking Team / Fax Operator / Concierge / Front Desk) — the construction that does not work, everything sequence flow and nothing crossing a boundary  [→ resources/bpmn-hotel-pools-and-lanes.png]

Presenter notes: Multiple pools (Guest, Just Paper Hotels, The Hotel) with message flows (booking request, fax to the hotel, accept/reject back, confirmation to the guest). We want to examine the *interaction* from a neutral perspective, but modelling it as one pool with lanes doesn't work well — some tasks reference interaction (waiting for the hotel's answer, taking payment), others are oblivious to partners (checking the room list, packing). It is not semantically correct because message events always refer to messages received from *outside*. **This is the heavy vertical bar from the paper notation, drawn properly** — and the failure of one-pool-with-lanes is exactly why the bar was there.

### Slide: Collaboration and Choreography

- A **Collaboration** has multiple participants, and is focused on **how they interact**.
- The message exchange between participants in a collaboration is a **Choreography** — generally the flow of messages between participants; within each orchestrated process there are message events caught or raised.
- Processes *react* to what happens in the choreography — no one owns it (it has no tokens or state of its own).

Interaction can happen two ways:

- **Within a workflow engine** — but this creates coupling, and both participants must run in the engine.
- **Via an API** — from an event-driven perspective, this is the model we care about.

#image: BPMN collaboration — Customer and Shopping pools with message flows  [→ resources/bpmn-shopping-collaboration.png]

Presenter notes: The two interaction options are the half that matters — **"both participants must run in the engine"** is the coupling argument from Day 1 §Coupling arriving at process scale.

### Slide: Pools and Lanes

- A **Pool** is a participant in a collaboration (a role or an organization). Not required for the main internal pool (the modeler's own org); required for other organizations' processes.
- A **Lane** distinguishes sequences of activities within a pool. White box = can see process; black box = cannot.
- Activities within the pool are organised by sequence flow.

#image: BPMN collaboration — Customer and Shopping pools with labelled pools/lanes and message flows  [→ resources/bpmn-shopping-collaboration.png]

Presenter notes: **Black box is the load-bearing word.** The Hotel is a black box to the agency — you see the messages, never the process — which is what makes the fracture plane in block 1 a *real* boundary rather than a drawing convention.

### Slide: Just Paper Hotels Collaboration

The full collaboration diagram for the hotel example.

#image: BPMN diagram, three pools (Guest, Just Paper Hotels, The Hotel) in a full collaboration with all message flows  [→ resources/bpmn-hotel-collaboration.png]

### Slide: Choreography and Conversation

- A **Choreography** describes a sequence/flow of activities *between* participants — a graph of flow elements (a message flow of activities, events, gateways). It is focused on the interaction across participants, **like describing a dance**: no single owner of the flow, no centralized control, and no access to anyone's shared internal state. It defines **who talks to whom, in what order**.
- A **Conversation** is a logical association of messages that can all be correlated. **Correlation Keys** associate messages in the same conversation (may be existing message data); the first task in a conversation *must* populate the conversation id.

#image: BPMN diagram — a horizontal flow with Customer/Shopping lane labels per task and message events  [→ resources/bpmn-shopping-choreography.png]

Presenter notes: **The dance and the no-shared-state line are what to land here.** The correlation key is not new: it is the booking reference written on the fax so the answer can be matched to the request, and it is the same id that becomes a trace id in `## Next Steps`.

### Slide: Hotel Example — BPMN Choreography

The booking choreography — the flow of messages between participants.


#image: BPMN choreography diagram: four choreography tasks across Guest, Just Paper Hotels and The Hotel, each banded with who speaks and who is spoken to  [→ resources/bpmn-hotel-choreography.png]

Presenter notes: Even this simple interaction produces a set of messages flowing between participants. Choreography is what happens "between" — it has no explicit owner. When flow leaves your application (or workflow engine) it "goes blind": the **event horizon**. You understand your workflow — it's in your code — but debugging becomes hard because at times nothing happens that's supposed to, and you struggle to know why. **This is round 4 with no conductor**, drawn.

### Slide: Messaging and Eventing (Orchestration vs. Choreography)

A common EDA notion: *messaging (commands) is orchestration; eventing is choreography.*

- It is **not** a helpful rule.
- Choreography is the flow of control and information *between* orchestrations — frequently out of process, and can use messaging or eventing as required.
- An orchestration is a sequence with attendant session state (token) — frequently not distributed, within an executable process. A **routing slip** is a distributed orchestration that uses message attributes as the engine of application state.

### Slide: Event Chaining

A sensible balance of orchestrated bounded contexts and choreography between them reduces event chaining. But **Event Pinball** can still be a problem between orchestrated services.

- **In-Out (or Robust In-Only):** explicit transfer of control reduces the "pinball effect" — creates causality by awaiting a response (send a *command* and wait for a response, not an event).
- **Out-Only:** often better at the *termination* of a workflow, or to broadcast intermediate states with no expectation of response.

### Slide: Allocating Responsibility for Collaborations

- **Commands / Messaging** — transfer of control/data; typically delegating responsibility for part of a workflow. In-Out (expected to return); In-Only (not expected to return, but may on error → Robust In-Only).
- **Events** — communicate the outcome of a workflow (complete, or a milestone broadcast). Out-Only (no expected return).
- **Workflow code is glue** — glue does not execute the domain (it is not the behaviour); it *calls* something that has the behaviour.

### Slide: Orchestration vs. Choreography — Summary

| Aspect | Orchestration | Choreography |
|---|---|---|
| Control | Centralized (one participant) | Decentralized (shared) |
| BPMN Shape | Inside a Pool | Between Pools |
| Perspective | One party's process | Multi-party message exchange |
| Data Access | Internal | Shared messages |
| Execution Tool | API calls, handlers, workflow engine | Messaging protocol |
| Example | The agency coordinates payment and the hotel booking | Guest + Agency + Hotel interact |

Presenter notes: Implementation paths depend on model type — embedded logic (orchestration) vs. API contracts/events (choreography). Clear boundaries → better automation decisions and a clearer division between messaging and eventing. **Close the first half here** on round 4's two questions — where did knowledge of the whole process live, and who had to change when a step was added — because the two columns of this table are the two answers.

---

### Slide: Tentative Operations

A conversation that spans more than a request and a response: the requestor may not know whether the provider can succeed, and may not want to proceed without knowing.

- `reserve()` — the requestor asks if the operation is possible and reserves the resources; the provider reserves the resource (usually with a timeout) and awaits commit or rollback (`reservation()`).
- On success → `commit()` → `acknowledge()` (allocate the reserved capacity).
- On failure → `rollback()` → `freed()` (free the reserved capacity).

**The booking, exactly:** the agency asks the hotel to `reserve()` a room. The hotel holds it **with a timeout**, so it can sell the room to someone else if we go quiet. Guest pays inside the limit → `commit()` → `acknowledge()`, the room is allocated. Guest abandons, or the card is declined → `rollback()` → `freed()`.

Presenter notes: **This is the bridge into durable execution**, and the hotel makes the bridge shorter: reserve/commit/rollback is a conversation with a *lifetime* — someone has to remember the reservation exists, honour its timeout, and drive it to commit or rollback **even across a restart**. That requirement is what the rest of this section is about. Two failure cards land here — *the guest checks out early, mid-flow* and *this desk goes home; anything not written into a file is forgotten*.

### Slide: Durable Execution

Long-running processes must:

- Survive restarts.
- Handle retries and failures.
- Resume after waiting (e.g. for payment or the hotel's answer).

Durable execution = we **persist activity state** to indicate which steps are complete, when we're awaiting an event, etc.

### Slide: Activities and Resources

Broadly, a software component manages **activities** and **resources** (Pat Helland).

- **Resources:** domain concepts we manage — hotels, rooms, guests.
- **Activities:** one or more sequences for our interaction with resources.
- As the token moves through the sequence we update resources *and* the activity (to indicate progress).
- The implementation question: **where does activity state live, and who updates it?**

Presenter notes: **That last line is the question the next five slides answer**, and it is the most directly useful material on either day — four mechanisms, in ascending order of how much machinery you take on. Put it on the board and leave it there.

### Slide: Activities and Resources — Worked Example

- **Booking Team → Hotel:** `reserve()` a room → `reservation()` (waiting for response).
- **Booking Team → Payment Provider:** `take payment()` → `payment taken()` (waiting for response).
- **Activity** (usually a service task) — glue code that calls domain logic internally or messages another app; could be a framework, a bespoke state machine, or pipes and filters.
- **Resources** — code/data managing shared items coordinated across activities (room inventory, rate plans) — our domain model.
- Our workflow stores the token state (where are we in the flow?), and there is a choreography — the messages we exchange with other participants running their own flows.

Presenter notes: Per Helland — each entity must remember state about its partners on a partner-by-partner basis; call this an **activity**. An entity may have many activities if it interacts with many partners.

### Slide: Handlers + Activity State Updates

Handlers process events (change resources) and update activity state.

- Durable because state is stored (e.g. a database), but control flow is **implicit** — activity state is often implicit (e.g. within an aggregate).
- Great for simple workflows, but logic becomes scattered across handlers.
- Becomes complex with split/join/choice/merge (not a sequence), and with retry / circuit breakers / compensation.
- Relies on **guaranteed delivery** (store work for retry unless ack'd) and **Transactional Messaging (Outbox)**.

#image: C# code screenshot — an async order handler using a transaction, postbox and the outbox pattern

Presenter notes: Baseline automation. E.g. a `BookingRequestedHandler` looks up the booking and sets state = AwaitingHotel. Handlers process events and update persistent state; durable via stored state, but control flow is implicit — logic scatters across handlers. **Walk the transaction and the postbox on the code screenshot**, because the outbox is Day 1 §4.4 arriving with a job to do.

### Slide: State Machine + Activity State Updates

When handler interaction becomes complex, make the activity **explicit**.

- A **State Machine** represents the activity and triggers actions on transitions.
- Transitions are caused by receiving a message.
- The handler loads the state machine for the conversation id, triggers the transition denoted by the message, and runs the associated code.
- Save the new state and ack the message.

#image: C# code screenshot — an OrderStateMachine (MassTransit) with Initially/During states and transitions

Presenter notes: States e.g. Requested → SentToHotel → Accepted → Paid → Confirmed; transitions triggered by events/commands; implemented via the state pattern, switch statements, or a library (e.g. Stateless). Durable via persisted state + event log. Benefits: predictable, easier to visualize/test, avoids duplication across handlers. Drawback: no concurrency or waiting logic. **Walk the Initially/During states on the code screenshot.**

### Slide: Routing Slip + Activity State Updates

To **distribute** steps in the sequence, transport the activity state *in the message*.

- A **routing slip** is an envelope carrying activity state (next step, context, etc.) — "Message As the Engine of Application State".
- The handler updates state when work is done, forwards according to the slip, then acks.
- Complex if "next" is dynamic routing (the code must understand how to execute).
- Complex because you distribute the steps — hard to observe (OpenTelemetry).

Presenter notes: **This is literally the conductor's routing slip from round 4** — the one artefact the room has already held in its hands. Say so; it is the cheapest explanation in the section.

### Slide: Workflow Engines + Activity State Updates

When we want more than state transitions (split, join, merge, choice), use a **workflow engine**.

- Explicitly models a sequence of activities and gateways; may support BPMN (or a proprietary language) with visual modelling.
- A step receives the token; the step is **glue** — invokes domain action, calls another service, sends a message.
- A **job scheduler** provides durable execution; typically any instance can resume a paused job (distributed).
- A step may wait for an event or timer to resume — the handler equivalent, or triggered by the handler calling the engine.

Presenter notes: External orchestrators — Temporal, Camunda, Azure Logic Apps, AWS Step Functions. Support wait states (await BookingAccepted), parallel branches, timeouts, retries, visual modeling. Durable by design (execution state + workflow history stored); suited to complex, distributed systems. Example steps: PlaceBookingWithHotel → WaitForHotelResponse → TakePayment → WaitForPaymentCleared → ConfirmToGuest — which is the BPMN from the front of this section, now executable.

### Slide: Compensation, Four Ways

You cannot roll back across desks. So for every "do", you write an "undo" — and the four mechanisms differ only in **where the undo lives**.

| mechanism | where the undo lives | what triggers it | the catch |
|---|---|---|---|
| **Handlers** | a fallback handler per step | a **fault message** — In-Only needs a dedicated fault channel used only for compensation; In-Out marks the response as a fault, not a success | retry first, compensate only after X failures; the undo logic scatters exactly like the do logic |
| **State Machine** | a transition to a faulted state, then a compensating flow back to *safe* | the same fault message, but it drives a transition | run **all** fault transitions to safe *before* acking the fault message; needs durable execution, so a restart mid-fault resumes |
| **Routing Slip** | the slip's **fault next** — the reverse of the step just completed | context on the envelope flips to "faulted" and the slip runs backwards | the slip must carry the undo route as well as the do route |
| **Workflow Engine** | a **compensation event** linked to the task | retry handles technical faults; a *business* error (card declined) is a modelled branch on a gateway | with no catch, the workflow rolls back to the last wait state or terminates |

▎ This is the **Saga**. Four costumes, one idea.

#image: BPMN fragment: Take Payment with an attached compensation event, associated to Refund the Card  [→ resources/bpmn-compensation-fragment.png]

Presenter notes: **One argument, four costumes — as a table the repetition becomes the point.** The Saga name comes from a 1980s paper on long-lived database transactions, and messaging frameworks that say "saga" almost always mean the state-machine row. **The distinction to land is business error vs. technical error** — retry is for technical, a gateway branch is for business, and confusing the two is how teams end up retrying a declined card forty times. (Ruecker, *Practical Process Automation*.) On the hotel: the undo for *reserve a room* is *release the room*; the undo for *take payment* is *refund*. Ask the room which of the four they would use, and why.

### Slide: Workflow Engines — Embedded, External, and the Lessons from SOA

Weighing engines embedded in a service against external orchestrators.

- **External orchestration is not an anti-pattern**, but it requires care.
- Keep core domain logic **inside** services; let the engine coordinate *outcomes*, not fine-grained steps.
- Consider choreography, or a local embedded orchestration, where autonomy matters more than visibility.

Presenter notes: The failure mode is **anaemic services**: all domain logic migrates into the engine and the services become passive executors of workflow directives. That is the ESB, rebuilt, and it sets up the next slide.

### Slide: Smart Endpoints, Dumb Pipes

ESB products often include sophisticated routing, choreography, transformation, and business rules. The microservice community favours the alternative: **smart endpoints and dumb pipes**. (martinfowler.com/articles/microservices.html)

Presenter notes: Microservices promote smart services and minimal messaging infrastructure. This is the closing argument of the section, and it is Day 1 §2's coupling argument at process scale: put the process in the pipe and every participant is coupled to the pipe.

### Slide: Implementing Workflow Patterns

How the basic patterns map onto the three implementation styles:

| Pattern | Handlers Only | State Machine | Workflow Engine |
|---|---|---|---|
| Sequence | Chain message handlers | State transitions (A→B→C) | Sequential steps |
| Parallel Split | Trigger multiple handlers | ⚠️ Complex manual coordination | Parallel branches with fork/join |
| Synchronization | Wait for multiple states | ⚠️ Hard without orchestration | Join after parallel branches |
| Compensation | Fallback handler | Saga | Implicit |
| Exclusive Choice | Conditional in handler | State transition on input | Conditional branching |
| Simple Merge | Trigger single follow-up | Re-entrant transition or rehydration | Multiple incoming flows, OR gateway |

Presenter notes: The rows are the five patterns from the front of the section plus compensation — so this table closes a loop opened twenty-five slides ago, and the two ⚠️ cells are the whole argument for when to stop hand-rolling and pick up an engine.

---

## Putting It Together

### Slide: Putting It Together

Section marker: revisiting the fax workflow — the takeaway *see one* — through the lens of the patterns, annotating each interaction with its messaging/eventing exchange pattern.

### Slide: Fax Workflow — Annotated (Storage & Correlation)

The flow-based fax workflow, now labelled with exchange patterns:

- **Storage:** store workflow state in case we crash before receiving a response.
- **Correlation:** use a correlation id sent to `fax_out` and returned via `fax_in` to look up the stored workflow.
- Interactions annotated: Messaging (In-Only, In-Only, Out-Only, In-Out) and Eventing.

#image: (s167) collaboration diagram — restaurant onboarding (fax/phone steps, new catalogue)  [→ resources/Restaurant Onboarding.drawio.png]
#image: (s168) FBP 'Onboard Restaurant' flow, annotated with Messaging/Eventing (In-Only/Out-Only/In-Out)  [→ resources/flowbased_onboard_restaurant.png]

### Slide: Lookup Store — Annotated

Building a lookup store from IPs raised by another component, annotated: Messaging (Out-Only, In-Only, In-Only, In-Out) and Eventing.

#image: (s169) collaboration diagram — order taking (phone order, card machine, eventual consistency)  [→ resources/Customer Order.drawio.png]
#image: (s170) FBP 'Order Food' flow, annotated with exchange patterns  [→ resources/flowbased_order_food.excalidraw]

### Slide: Fault Path — Annotated

The workflow's fault path annotated as Messaging with **Message Triggers Fault**.

#image: (s171) collaboration diagram — order-taking errors (invalid card, outbox)  [→ resources/Customer Order Errors.drawio.png]
#image: (s172) FBP 'Order Food Errors' flow, annotated with Message-Triggers-Fault  [→ resources/flowbased_order_food_errors.png]

### Slide: Full Flow — Annotated

The complete flow annotated with its mix of Messaging (In-Only, In-Out ×3) and Eventing (Out-Only) exchanges.

#image: (s173) collaboration diagram — order placement (fax operators create/accept order, book driver)  [→ resources/Order Placement.drawio.png]
#image: (s174) FBP 'Order Placement' flow, annotated with exchange patterns  [→ resources/flowbased_order_placement.png]

### Slide: Putting It Together — Recap

Final visual recap tying the exchange patterns back to the worked example.

#image: (s175) composite — an 'Order Confirmation' collaboration diagram plus thumbnails of the other flows  [→ resources/Order Confirmation.drawio.png + related]
#image: (s176) FBP overall 'Order Flow' — Qualify Restaurant through Cook Food and Book Courier  [→ resources/flowbased_order_all.png]

---

## Next Steps

*What we did not cover, and where it lives.*

### Slide: Describing and Versioning Your Messages — the Handout

Everything about the *contract* rather than the message: how you publish what your endpoints are, and how
you change a message you have already published.

- **Describing endpoints** — the ABCs: Address, Binding, Contract. AsyncAPI, CloudEvents, xRegistry, and
  the tooling around them (EventCatalog, Backstage, AsyncAPI Studio).
- **Versioning** — Postel's Law and the **Tolerant Reader**; additive change vs. breaking change; why a
  breaking change means a new message type.
- **Schema and registries** — JSON Schema vs. Avro vs. Protobuf; schema registries and compatibility
  modes (backward / forward / full / none).

▎ Be strict when sending and tolerant when receiving. The rest is in the handout.

Presenter notes: **Hand the *Managing Asynchronous APIs* handout out here** (see plan §6 — built from the QCon London 2026 deck). Give Postel's Law thirty seconds out loud, because it is the one line that changes behaviour, and point at the handout for everything else. The two days have taught them what to put in a message and how to move it reliably; this is how they publish and evolve it, and it is reference material rather than a decision to rehearse. Worth naming the case study — MeX at Just Eat Takeaway, 2,048 message schemas — so it reads as a real-world artefact and not an appendix.

### Slide: Observability

You cannot debug a flow by reading one service's logs. A message crosses process boundaries, so the trace
has to cross them too.

- **OpenTelemetry** carries trace and span ids in the **message header** — the same envelope as the
  correlation id from the fax workflow.
- One trace spans producer, broker and every consumer, so you can see the whole conversation.
- This is the observability story for everything the two days built: the pump, the outbox, the DLQ, and
  the flows delegates drew on paper.

Presenter notes: One slide, deliberately. The correlation id has been on the table since the Paper Flow exercise's document cards — this is where it grows up into a trace. Show one screenshot of a real trace across a broker if there is time; the picture does the work.

### Slide: Further Reading — Reactive Microservices

*Reactive Microservices Architecture* — Jonas Bonér. (jonasboner.com/resources/Reactive_Microservices_Architecture.pdf)


#image: book cover — 'Reactive Microservices Architecture' by Jonas Bonér (O'Reilly)

### Slide: Further Reading — Practical Process Automation

*Practical Process Automation* — Bernd Ruecker. (processautomationbook.com)


#image: book cover — 'Practical Process Automation' by Bernd Ruecker (O'Reilly)

### Slide: Further Reading — EDA Visuals

Serverless Land — event-driven architecture visuals. (serverlessland.com/event-driven-architecture/visuals)


#image: screenshot — the Serverless Land 'EDA Visuals' page of event-driven architecture cards

### Slide: Further Reading — Enterprise Integration Patterns

Gregor Hohpe. (enterpriseintegrationpatterns.com/gregor.html)


#image: book cover — 'Enterprise Integration Patterns' by Gregor Hohpe and Bobby Woolf

### Slide: Q&A

Questions and discussion.
