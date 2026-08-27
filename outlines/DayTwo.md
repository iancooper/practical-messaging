# Practical Messaging — Day Two

A 101 guide to messaging. Ian Cooper. (X, BlueSky and Hachyderm: ICooper)

Day Two moves from single messages to *conversations*: the message-exchange patterns between participants, how faults are repaired, fat vs. skinny messages and reference data, then the shift to reactive thinking (dataflow and flow-based programming, reactive architectures) and finally process automation — BPMN, orchestration vs. choreography, durable execution, and workflow engines.

---

## Conversations

*From messages to conversations — In & Out.*

### Slide: Messaging Participants

An application acts as either a **requestor** or a **provider**.

- A message is sent over a **channel** — a virtual pipe (topic, routing key).
- A message has a **header** (metadata) and a **body** (data).
- A channel is **unidirectional** (one way).
- Prefer *requestor/provider* over *producer/consumer* for conversation patterns, because they indicate role.

Presenter notes: The problem with producer/consumer is that the *consumer* of a message might be the one exposing operations (receiving a command), or the *producer* might be the one exposing operations (sending a notification). Thinking in requestor/provider makes the role clear — are you providing the API or using it?

### Slide: Messaging Participants — Example

- **Provider (Store Information):** manages stores for our ecommerce site.
- **Requestor (Search):** registers a store and optimizes for fast lookup on key search terms.
- Message: indicates new store details (`changedstore()`).

### Slide: In-Only (Fire and Forget)

Under **In-Only**, the requestor sends a request to the provider but does not seek acknowledgment of completion. Typically called *fire-and-forget*.

### Slide: In-Only — Example

- **Requestor (cashier):** has a paid-for basket it wants to turn into an order.
- **Provider (order placement):** raises an order (`place order()`).
- Typically used where we are finished with our part in a flow and transferring control — we need no response because we are done.

### Slide: Out-Only (Notification)

Under **Out-Only**, the requestor subscribes to the provider; an operation is triggered by receipt of a message, but it does not acknowledge the message back to the provider. Typically called a *notification*.

### Slide: Out-Only — Publish-Subscribe Example

Out-Only *is* the Publish-Subscribe pattern: a producer is not aware of its consumers; the notification has loose coupling.

- **Provider (Store Information):** manages stores; raises `changedstore()`.
- Multiple requestors subscribe: **Search** (fast lookup), **Availability** (factors for whether a store is open), **Pick-Up Locations** (where couriers pick up, and restrictions).

### Slide: In-Out (Request-Reaction)

Under **In-Out**, the provider receives a request on one channel and returns a response (from the triggered operation) on a *separate* channel.

The provider sets a **correlation id** (conversation id) in the request header, and returns it in the response header, so replies over a separate channel can be correlated.

### Slide: In-Out — Request-Reaction (Command-Acknowledgement)

In-Out supports Request-Response / Command-Acknowledgement: a requestor triggers an operation on the provider and gets a response.

- **Requestor (Basket):** manages items for purchase. Sends `checkout()` — a command asking the cashier to price a basket.
- **Provider (Cashier):** takes payment for the agreed amount and turns a basket into an order; replies `successfulpayment()`.

Presenter notes: This has behavioural (control) coupling.

### Slide: In-Out — Query-Result

In-Out supports Query-Result: a requestor triggers a query and gets a result.

- **Requestor (Basket):** sends `getdeliveryfees()` — a query for delivery fees for this basket.
- **Provider (Delivery):** determines the fee based on store and items; replies `deliverfee()`.

Presenter notes: This has behavioural (control) coupling.

### Slide: In-Out — Subscribe-Notify

In-Out coupled with Out-Only supports Subscribe-Notify: a requestor asks to subscribe (start/stop) to a provider.

- `subscribe()` → provider manages a list of subscribers → optional `confirm()`/`confirmed()` (note the role switch).
- Then Out-Only `notification()` messages flow; a `stop()` ends them.

Presenter notes: This has behavioural (control) coupling.

### Slide: Blocking In-Out (Request-Reply)

The requestor provides a unique **Reply-To** channel in the request header; the provider uses it for the response, letting the requestor look up the suspended workflow — so a correlation id is not required.

- To resume, we need a way to identify the suspended workflow.
- The requestor *may block* on the Reply-To channel while awaiting the reply.

### Slide: Out-In (Solicit-Response)

Under **Out-In**, a provider solicits a response from a subscriber and awaits confirmation; the subscriber confirms receipt of the provider's solicitation.

### Slide: Out-In — Example

- **Provider (Delivery):** assigns delivery requests to drivers; queries whether a courier is available (`solicit()`), usually followed by notifications of available work.
- **Requestor (Courier):** offers to take jobs depending on location and busyness (`ready()`).

### Slide: Messaging vs. Eventing — Patterns Map (Messaging)

**Messaging** — has intent; request an answer (Query), transfer of control (Command), transfer of value; part of a workflow/conversation; concerned with the future. Patterns:

- In-Only (fire and forget)
- In-Out (request-reaction)

#image: two UML-style pattern diagrams — In-Only (fire-and-forget) and In-Out (request-reaction), requestor/provider  [→ resources/'Practical Messaging - Day 2 - 2024 - 25.png' + '...- 29.png' — exported slide images]

### Slide: Messaging vs. Eventing — Patterns Map (Eventing)

**Eventing** — provides facts; things you report on; no expectations; history/context; concerned with the past. Pattern:

- Out-Only (notification)

#image: UML-style diagram — the Out-Only (notification) pattern, requestor to provider  [→ resources/'Practical Messaging - Day 2 - 2024 - 27.png' — exported slide image]

---

## Repair and Clarification

*What guarantees does a provider make about communicating faults?*

### Slide: Repair and Clarification

The requestor triggers an operation on the provider by sending a message. We must consider a fault being triggered by that operation. The question: what guarantees does the provider make to the requestor about communicating any faults?

### Slide: No Fault

Under **No Fault**, the provider makes no attempt to communicate triggered faults to the requestor. From the requestor's perspective, faults are the provider's application issue, not its concern.

### Slide: No Fault — Example

- **Search** cannot add a store to its results after `changedstore()`, but makes no attempt to tell **Store Information**.
- Most likely we fix consistency issues out-of-band via logs or error reports.

Presenter notes: This is "good enough" in many cases.

### Slide: Message Triggers Fault (Robust In-Only)

Under **Message Triggers Fault**, the provider propagates faults from the operation back to the triggering requestor via a message.

- The fault message goes in the opposite direction, back to the requestor.
- Assumes the requestor can act on receipt of the fault, but does not normally take a (success) response.

Presenter notes: The key: there is no existing subsequent message to replace with a fault, but we still want to communicate faults back.

### Slide: Message Triggers Fault — Example

- **Requestor (cashier):** `place order()`.
- **Provider (order placement):** if it cannot place the order due to a fault, raises `fault()`.
- The requestor doesn't acknowledge success, but on a fault may need to take other action such as a refund.

### Slide: Fault Replaces Message

Under **Fault Replaces Message**, the provider propagates faults by switching to a fault flow — replacing any message *after the first* with a fault. The requestor handles the error; the fault replaces the existing response (`reaction()` → `fault()`).

Presenter notes: Any message in the conversation after the first may indicate a fault instead of the normal outcome.

### Slide: Fault Replaces Message (Robust In-Out) — Example

- **Pricer → Payment Provider:** `take payment()`.
- On failure the payment provider signals `payment error()` back to the pricer.
- Assumes the pricer can orchestrate a new flow (ask for an alternate payment method, or cancel the order). The message should indicate *why* payment failed — a provider issue, or an invalid card / insufficient funds.

### Slide: In-Out-Retry

The requestor may not receive an expected response. What can it do?

- Set a **timeout** within which to receive a response.
- **Retry** if no response arrives within that window (`greet()` → `greet()` → `acknowledge()`).
- Because we might send twice, the provider operation must be **idempotent**, or the consumer must **de-duplicate** already-seen messages.


#image: icon — a stopwatch/timer (the retry timeout)

### Slide: Tentative Operations

The requestor may not know whether the provider can succeed, and may not want to proceed without knowing.

- `reserve()` — the requestor asks if the operation is possible and reserves the resources; the provider reserves the resource (usually with a timeout) and awaits commit or rollback (`reservation()`).
- On success → `commit()` → `acknowledge()` (allocate the reserved capacity).
- On failure → `rollback()` → `freed()` (free the reserved capacity).

### Slide: Tentative Operations — Example

- **Basket → Warehouse:** `reserve()` stock (Fault-Replaces-Message could apply if out of stock).
- Warehouse reserves the stock with a timeout so others can buy it if we don't.
- If the customer pays before the limit → `commit()` → `acknowledge()` (allocate stock).
- If the basket doesn't complete → `rollback()` → `freed()`.

---

## Fat & Skinny

*How much data does a message carry?*

### Slide: Fat Message

With a **Fat Message**, the requestor sends across all the *external* information a provider may need to perform the operation.

- The requestor provides all external information the provider needs to act.
- The resulting document message may be large (a **Claim Check** can help).

### Slide: Fat Message — Example

- **Order Fulfilment → Courier Assignment:** the request provides delivery and pickup address, size, weights, etc. of the order.

### Slide: Fat Message — Transitive Dependencies

A purchase-order message that inlines customer and restaurant data illustrates the cost:

- The order data has the *lifetime of the message*; its schema changes if the purchase order changes.
- Customer data is a **transitive dependency** — its lifetime is the Customer's; a Customer schema change may force a message change.
- Restaurant data is likewise a transitive dependency on the Restaurant schema.

### Slide: Skinny Message

With a **Skinny Message**, the requestor provides only information unique to the event and assumes the provider has, or can obtain, the other information.

- The resulting notification message is normally skinny.

### Slide: Skinny Message — Example

- **Order Notification → Courier Assignment:** notifies that there is an order, inlining only order-unique data — not reference data like weights or addresses.
- Courier Assignment must source the missing information (weights, addresses) from elsewhere.

### Slide: Skinny Message — Normalized

The purchase-order message carries `CustomerId` and `RestaurantId` instead of inlined data:

- Use an **Id** where the data does not share the message's lifetime; assume the requestor obtains the data out-of-band.
- These ids must be looked up with other providers (Customer, Restaurant).

### Slide: Skinny Message using Reference Data

The requestor assumes **Provider A** has a local cache of data from **Provider B** it can use to look up identifiers in the skinny message.

- Data that leaves Provider B via an API is **Reference Data**: immutable, versioned, stale.
- It can be cached locally to Provider A to avoid frequent lookups (`cache lookup()`).

### Slide: Skinny Message via REST/RPC

On a cache miss, Provider A fetches the data from Provider B synchronously.

- Look up missing data in the local reference-data cache (may specify identity *and* version).
- On a miss, request from Provider B and store in the cache (`request()`/`reply()`/`cache write()`).
- The cache chooses **Availability over Consistency**, *except* on a miss.
- On a miss, this is **Consistency over Availability** (CAP): A's uptime becomes that of A & B — if B fails, A fails.

### Slide: Skinny Message — Reference Data via ECST (Event-Carried State Transfer)

Provider B pushes state changes to A ahead of time, so A rarely needs a synchronous lookup.

- The upstream provider raises a **notification** when its own entity state changes (Out-Only / pub-sub).
- The downstream provider subscribes and writes to its local cache (`cache write()`); later requests hit the cache.
- CAP: this chooses **Availability over Consistency** — accept stale data rather than risk failure due to a partition.

### Slide: Skinny Message using Reference Data — Example

- **Order Fulfilment → Courier Assignment:** the request omits restaurant pickup address; we assume Courier Assignment obtained it from Restaurant Information.
- Look up the restaurant in the local cache by **id and version**.
- If we have the restaurant but not the version, apply **backpressure** and retry the order after a delay.

---

## Domain, Summary & Sequence

*How events communicate state changes, and how ordering is handled.*

### Slide: Domain or Delta Event

An approach to Pub-Sub where the provider communicates **granular** state changes to its requestors.

- Messages are usually named as a past participle after the causing command (e.g. `BasketItemRemoved`, `BasketItemAdded`).
- Cannot use a **Datatype Channel** — domain events for the observable must be *ordered on the same channel* and have different schemas. This burdens the requestor to multiplex handling of the events.

### Slide: Summary or Snapshot Event

An approach to Pub-Sub where the provider communicates a **summary** of state changes.

- The message is **versioned** and contains metadata describing the cause(s) of changes; usually named after the observable (e.g. `BasketChanged`).
- *Can* use a Datatype Channel — there is just one schema for a snapshot of the observable.

### Slide: If Later, Stream

**If Later** lets us use a versioned Summary Event to ignore ordering errors.

- Consumer reads v1 of 12345 and handles it; reads v3 and applies it (later than v1); reads v2 and **discards** it (earlier than the already-applied v3).
- Even on a stream, non-blocking retry or guaranteed delivery via an outbox can produce out-of-order messages; If-Later also lets us shed load.
- We *cannot* use If-Later with a Domain Event — those must all be applied. With Domain Events we can only use a blocking retry and cannot shed load.


#image: diagram — a stream of versioned message envelopes (12345 v1..v3) read by a consumer applying 'if later'

Presenter notes: Publish complete new versions rather than deltas, then apply "write if later" — with v0, we can write v2 even without seeing v1, because v2 is later and either overwrites or includes v1's changes; we can then safely discard v1.

### Slide: If Later, Queue

If-Later also lets messages be processed out-of-order with a queue and competing consumers.

- One consumer expects/writes v1 while another writes v2; **read-past** lets them proceed.
- A queue normally processes messages (not events), so this applies only where we use a queue.
- If a message *must* be ordered (e.g. a series of commands), use requeue-with-delay or a sequencer to re-order.


#image: diagram — a queue of versioned message envelopes with two competing consumers and read-past

### Slide: Public and Private Providers

An approach to Pub-Sub where a **public** provider communicates with collaborators in other domains via a **Summary Event** aggregated from the domain events of **private** providers.

- Private providers raise granular `event()`s.
- The public provider republishes a versioned `summary()` with metadata describing the cause(s) of changes.

---

## Flow

### Slide: Flow

Section marker: from patterns to whole workflows.

### Slide: Paper Workflows

▎ "My life looked good on paper — where, in fact, almost all of it was being lived." — Martin Amis

We motivate flow by looking at how paper-based office workflows already embodied messaging ideas.

### Slide: Two Axes — Discrete/Series and Skinny/Fat

A framing diagram positioning message styles:

- Messaging / Discrete Event — discrete, immediately actioned; **skinny**.
- Series Event (Document) — series, supports action; **fat**.


#image: two interdepartmental delivery envelopes (illustrating discrete/skinny vs. series/fat)

### Slide: The Frame (Broker Analogy)


#image: photo — an office desk with overflowing IN and OUT trays and a phone (the 'frame' / mail sorting)

Presenter notes: In a mail room, "the frame" was how we sorted mail by floor, then delivered by a worker with a cart. In essence this is what a **broker** does — creates channels you send messages to, that are delivered to subscribers.

### Slide: Paper Workflow Illustrations

A sequence of visual slides walking through a paper office workflow (mail sorting, the order wheel, carbon-copy memos) as physical analogues of messaging concepts.

Presenter notes highlights:
- **Order wheel:** a restaurant device to track orders — a new order is clipped on and turned from the server side round to the kitchen; completed orders turn back to the server. Orders are made and returned in sequence.
- **Carbon-copy memo:** writing creates a copy in the carbon paper underneath — ensuring you keep a copy of any message sent, and letting you read the message history on a file to understand current state.
- Later illustrations pose the question: *how do we deal with errors?*

#image: (s54) photo — a large stack of manila file folders and papers
#image: (s56) photo — a worker pushing a mail-delivery cart through an office
#image: (s57) photo — mailroom pigeonhole shelves stuffed with sorted mail and parcels
#image: (s59) value-stream map — restaurant onboarding  [→ resources/Restaurant Onboarding Value Stream.drawio.png]
#image: (s60) flow diagram — restaurant onboarding  [→ resources/Restaurant Onboarding.drawio.png]
#image: (s61) value-stream map — order flow  [→ resources/Order Flow Value Stream.drawio.png]
#image: (s62) flow diagram — customer order  [→ resources/Customer Order.drawio.png]
#image: (s63) photo — order taking (phone / card machine / order pad)
#image: (s64) flow diagram — order placement  [→ resources/Order Placement.drawio.png]
#image: (s65) flow diagram — order confirmation  [→ resources/Order Confirmation.drawio.png]
#image: (s66) montage of the flow diagrams (onboarding, customer order, order confirmation, order placement)  [→ resources/Order Confirmation.drawio.png + related]
#image: (s67) photo — a multi-part carbon-copy (NCR) form pad, stamped 'DO NOT USE'
#image: (s68) flow diagram — restaurant onboarding errors  [→ resources/Restaurant Onboarding Errors.drawio.png]
#image: (s69) screenshot — a Fax Call Log table with error status codes highlighted
#image: (s70) flow diagram — customer order errors  [→ resources/Customer Order Errors.drawio.png]
#image: (s71) flow diagram — order placement errors  [→ resources/Order Placement Errors.drawio.png]
#note: (s58) not an image — the SOA 'what is a microservice?' quote (Josuttis) also appears here; see Process Automation

---

## Reactive Programming

### Slide: Reactive Programming

Section marker: a different paradigm from call-and-return OO.

### Slide: Object-Oriented Programming


#image: hand-drawn OO diagram — a class with role/responsibilities, encapsulated data, inheritance via dynamic dispatch, message passing

Presenter notes: A class has a role with responsibilities; we capture responsibilities as behaviors; we encapsulate the data those behaviors need within the object; roles may be inherited via dynamic dispatch.

### Slide: OO — Call and Return, and the God Object

- **Call and Return:** `main` is the entry point; it uses message passing to invoke objects, which invoke other objects and return to their caller.
- **God Object:** the danger is a "god" object (e.g. `Cart`) that controls all the others — a high degree of behavioural coupling.


#image: hand-drawn call-and-return diagram — Main invoking Cart, Restaurant, Account, Menu, Payment, Order, Delivery objects

Presenter notes: A system passes control between classes to meet a use case, via message passing — "call and return" from `main` on down.

### Slide: Data Flow Programming

**Dataflow Programming** conceptualizes a program as a directed graph: operations are **nodes**, connected by **arcs** through which data flows. A node performs its operation when input data is available.


#image: hand-drawn dataflow graph — nodes/vertices connected by arcs, with operation and data annotations

Presenter notes: Perhaps the oldest expression of the reactive approach. Unlike OO (state co-located with behavior in nodes), data *moves between* transformations via arcs. Example: Unix CLI, pipes and filters.

### Slide: Dataflow — Nodes, Ports and Firing


#image: hand-drawn diagram — a dataflow node as a black box with input/output ports (activate → process → push)

Presenter notes: A node has an input port; it is activated ("fired") when an event arrives on the input port's arc; it responds with computation; as a black box it signals what happened by raising an event on an output port (to which others may react). It is *reactive* because it fires in response to an event. Generally a node is single-threaded.

### Slide: Dataflow — Packets


#image: hand-drawn diagram — two nodes passing data packets (primitive/compound values) between ports

Presenter notes: No special requirements about packets — they are just data.

### Slide: Dataflow — Capacity, Backpressure, Node Lifetime

- **Node Lifetime:** in "classic" dataflow, a node lives from activation (push: work to do; pull: work requested) until it has pushed the answer.
- **Capacity:** we don't activate a node to read input if there's no space on the output (infinite-capacity links exist only in theory). This creates **backpressure**.


#image: hand-drawn diagram — an arc/link pipe with buffers for pipelining; push/pull, synchronous/asynchronous

Presenter notes: Arcs/links connect nodes. Buffered links allow asynchrony (raise output onto the buffer even while downstream is busy), enabling parallelism — throughput limited by the slowest node. Not required for dataflow: a synchronous, unbuffered, single-threaded pipeline is valid. Push = hot source (e.g. mouse clicks) we listen to; pull = nothing generated until a sink pulls the chain. A full buffer → backpressure or load shedding.

### Slide: Flow Based Programming

▎ "Everything flows and nothing stays." — Heraclitus

**Flow-Based Programming (FBP)** is a subclass of dataflow. While DFP can be synchronous or asynchronous, FBP is *always asynchronous*. FBP allows multiple input ports, has bounded buffers, and applies backpressure when buffers fill.


#image: hand-drawn FBP diagram — a component with in/out ports, an information packet, and a connector

### Slide: FBP — Node Lifetime

In flow-based programming a node can remain running while there is work on an input queue, and can *suspend* (rather than terminate) if there's no work on its connector.


#image: hand-drawn FBP diagram — a component with in/out ports; packet lifetime and process-and-wait annotations

### Slide: FBP — Initial Information Packets (IIP)


#image: hand-drawn FBP diagram — an initial information packet (iip_in) and control-packet bracketing

Presenter notes: MQTT Retained Messages are a way of emulating the IIP idea.

### Slide: FBP — Capacity

In flow-based programming a component can test whether it can send to `out`, and if not, decide whether to halt or ignore.


#image: hand-drawn FBP diagram — multiple writers on an in-port, single writer on an out-port, multiple ports
#image: (s86) hand-drawn FBP diagram — components A and B; does A need data from another node?
#image: (s87) hand-drawn FBP diagram — components A and B with lookup ports (query / pause / response) — the 'walk of shame'
#image: (s88) hand-drawn FBP diagram — a 'Build Lookup' node listening to A, pre-caching a lookup table for B
#image: (s89) hand-drawn FBP diagram — nodes as processes connected by Message-Oriented Middleware (MoM)

### Slide: FBP — Worked Example (Fax Workflow)

A flow-based example of a request/response workflow with external participants:

- **Storage:** request details may need storage to be reliable — a component takes work from the `request_details` port but can't forward to `restaurant_details` without an answer from `fax_in`, so we store the workflow state in case we crash before the response.
- **Correlation:** to match the response to saved state we use a **correlation id**, sent on the IP to `fax_out` and returned by the restaurant on the IP from `fax_in`; we use it to look up the stored workflow.
- **Lookup:** we can build a store from IPs raised by another component to act as a lookup table for information needed to process a request.

#image: (s91) hand-drawn FBP 'Onboard Restaurant' flow  [→ resources/flowbased_onboard_restaurant.png]
#image: (s92) hand-drawn FBP 'Order Food' flow  [→ resources/flowbased_order_food.excalidraw]
#image: (s93) hand-drawn FBP 'Order Food Errors' flow  [→ resources/flowbased_order_food_errors.png]
#image: (s94) hand-drawn FBP 'Order Placement' flow  [→ resources/flowbased_order_placement.png]
#image: (s95) hand-drawn FBP overall 'Order Flow'  [→ resources/flowbased_order_all.png]

### Slide: SOA Architectures

Section marker: services as macro-scale objects.

### Slide: SOA & OO

**SOA** creates OO-like components: they encapsulate their data and expose behavior coupled to that data (the Web Services approach).


#image: hand-drawn service-orientation diagram — a WSDL service with endpoint, binding, operations, input/output messages

Presenter notes: SOA takes objects to a macro scale — a service has a role and responsibilities exposed via operations/behaviors, and encapsulates its associated data. This is OO as an architectural principle.

### Slide: SOA — Feature Envy Anti-Pattern

- **SOA & OO:** we expose significant resources and operations upon them (often CRUD).
- **Feature Envy:** because domain logic must coordinate across resources, it ends up on the client, the API Gateway, or the Cart service — *not* in individual services. An anti-pattern.


#image: hand-drawn entity-services diagram — Device → API Gateway → Cart, Restaurant, Account, Menu, Payment, Order, Delivery

Presenter notes: Making OO large tempts "call and return" via a `main` method at the API gateway — effectively a distributed monolith driven from the gateway. Is there a better paradigm?

### Slide: SOA — Faults Propagate (RPC)

- **RPC** is a synchronous conversation — both parties must be active during the call.
- **Faults Propagate:** with a synchronous service, a fault propagates, making us brittle.


#image: hand-drawn entity-services diagram illustrating synchronous RPC faults propagating up the chain

### Slide: Reactive Architectures

Section marker: reactive derives from reactive programming, not OO.

### Slide: The Reactive Manifesto

Published September 2014 by Jonas Bonér (with Erik Meijer, Martin Odersky, Greg Young, Martin Thompson, Roland Kuhn, James Ward, Guillaume Bort). Defines the **Reactive Applications** architectural style — write applications that:

- **React to events** — event-driven nature enables the other qualities.
- **React to load** — scalability over single-user performance.
- **React to failure** — resilient systems that recover at all levels.
- **React to users** — combine the above for an interactive experience.

Traits: **Responsive** (timely), **Resilient** (stays responsive under failure), **Elastic** (stays responsive under varying load), **Message Driven** (asynchronous message passing). (reactivemanifesto.org)

Presenter notes: Not just the actor model — these ideas have expression beyond it (following Helland, many implementations are possible).

### Slide: Reactive Traits — Value, Form, Means

Framing the manifesto's traits: **Responsive** = value; **Resilient / Elastic** = form; **Message Driven** = means.

### Slide: Message Passing

**Message Passing** is an asynchronous method of communication — both parties need not be simultaneously present; mail is delivered to a "mailbox" for later retrieval.


#image: hand-drawn diagram — a component with incoming and outgoing message arrows (asynchronous message passing)

Presenter notes: Message passing invokes behavior on a computer; rather than calling a program by name, it uses an object model to distinguish general function from specific implementation — the invoker sends a message and relies on the object to select and execute the code. Justifications: encapsulation and distribution.

### Slide: Microservices Are Reactive Architectures


#image: hand-drawn message-passing diagram — a component with in-request / out-request / out-result ports (command vs event)

Presenter notes: Reactive architectures derive from reactive programming, not OO — "everything flows". We separate data from behavior, activate a component in response to work on a queue, process it, and send an outgoing message.

### Slide: Reactive Principles — Partitioning and Dataflow

- **Partitioning:** partition to exploit parallelism — tasks that could run concurrently.
- **Coordinate Dataflow:** "orchestrate a continuous steady flow of information", dividing by behavior, not structure.


#image: hand-drawn FBP diagram — Checkout and Take Payment components with purchase / priced / payment-due messages

Presenter notes: Reactive inherits from dataflow — conceive the application as a graph of nodes operating on data flowing through. Reactive shines for data-driven applications composed from components in workflows; let components subscribe to each other's event streams and consume asynchronously published facts on demand.

### Slide: Bulkheads

In an asynchronous conversation a fault does **not** propagate back up the chain — we have a **bulkhead** protecting us against failure.


#image: hand-drawn FBP diagram — Take Payment crossed out; work queues up on a fault (the bulkhead)

Presenter notes: With async message passing the receiver can be down or busy when the sender sends — like a function call that returns immediately. Messages queue until the receiver requests them; results go to a queue for pickup. Requires storage/retransmission capability, usually via middleware (Message-Oriented Middleware, MOM).

### Slide: Backpressure (Blocking Retry)

**Blocking Retry** — e.g. repeatedly retrying when we can't connect to a DB — creates backpressure by slowing consumption.


#image: hand-drawn message-passing diagram — push vs pull, with backpressure annotations on the ports

Presenter notes: With no/full buffers, something must give: slow the producer (**backpressure**) or discard data (**load-shedding**). Backpressure is the producer feeling backward pressure from the pipe, forcing it to slow until pressure alleviates — good when data loss is unacceptable and extra latency is tolerable.

### Slide: Load-Shedding


#image: hand-drawn message-passing diagram — load-shedding, dropping messages on a fault

Presenter notes: Load-shedding discards data to keep up — great for high-velocity metrics (receive 1000/s but need only 10/s to meet an SLA). Can prioritize intelligently to discard only less-valuable data.

### Slide: Putting Reactive Together

A recap of how the reactive pieces (message passing, bulkheads, backpressure, load-shedding) combine.


#image: (s109) hand-drawn message-passing diagram — circuit breaker: stop consuming on a fault
#image: (s110) hand-drawn 'scale out not up' diagram — a Supervisor fanning out to Worker instances
#image: (s111) hand-drawn 'scale out not up' diagram — Supervisor to Workers with scale-out and fault regions

### Slide: Exercise Material — Flow

Readme, slides. The **Flow** exercise.


#image: 'DON'T PANIC' in red on black (Hitchhiker's Guide reference)

---

## Process Automation

### Slide: What is a Microservice? (SOA 3.0)

"SOA is focused on business processes… a service should represent a self-contained functionality that corresponds to a real-world business activity." — Nicolai M. Josuttis, *SOA in Practice*.

Presenter notes: We treat microservices as SOA 3.0, so most best practice still applies. The key is service **alignment with a business process or activity** — this workstream is about how that alignment improves productivity (not just fault-tolerance through isolation). Amplified next by the entity-service anti-pattern.

### Slide: BPMN

**BPMN** (Business Process Management and Notation) is a visual language for diagramming business processes clearly, in a standardized and comprehensive way.

- A **start event** begins a flow; an **end event** terminates it (and may throw a message).
- **Sequence flow** arrows show the path of execution.
- An **event** begins, ends, or interrupts a flow; a **task** is where work gets done.

#image: BPMN diagram — an 'Order Food' process (Enter Location, Choose Restaurant, Add Menu Choices, Checkout) ending with a message event  [→ resources/BPMN Ordering Flow.drawio.png]

### Slide: BPMN — Basic Elements

A BPMN diagram consists of: **Start Event**, **End Event**, **Sequence Flow**, **Activity** (Task / Sub-process), **Event**, and **Gateway**.

#image: BPMN diagram — start event, task, gateway splitting to two parallel tasks, merge gateway, end event  [→ resources/BPMN Elements.drawio.png]

### Slide: BPMN — Tasks

A **task** is an atomic activity (cannot be broken down further):

- Generic, Service (uses a service), Receive (waits for a message), Send (sends a message), User (human completion via software), Manual (human completion not via software), Business Rule (rules engine), Script (executes code).
- Markers: Loop, Transaction.

#image: BPMN legend — task/activity icon variants (service, message, user, manual, business rule, script, loop, transaction)  [→ resources/Task Types.drawio.png]

### Slide: BPMN — Events

An **event** happens within a flow — starts it, ends it, or interrupts it:

- None, Message, Time, Signal, Compensation, Conditional, Escalation, Parallel, Cancel.

#image: BPMN legend — event-circle variants (message, timer, signal, escalation, compensation, cancel, etc.)  [→ resources/Event Types.drawio.png]

### Slide: BPMN — Gateways

A **gateway** controls how sequence flow branches and converges:

- Exclusive (one alternative path), Inclusive (alternatives, possibly parallel), Parallel (split/join), Complex (complex expression), Event (an event picks the path).

#image: BPMN legend — gateway-diamond variants (exclusive, inclusive, parallel, complex, event-based)  [→ resources/Gateway Types.drawio.png]

### Slide: BPMN — Connecting Objects

- **Sequence Flow** and **Message Flow** connect activities.

### Slide: Workflow Patterns

*Workflow Patterns* — van der Aalst, ter Hofstede, Kiepuszewski, Barros (2000): 5 basic + 15 advanced patterns. *Workflow Control-Flow Patterns: A Revised View* — van der Aalst, Mulyar, Russell, ter Hofstede (2007): 23 new patterns.

### Slide: Pattern 1 — Sequence

One activity follows another. BPMN: connect two tasks with a sequence-flow arrow. Easy to model and execute. Example (Customer): Browse Pizza → Add Pizza to Basket.


#image: BPMN diagram — two user tasks: Browse Pizzas → Add Pizza to Basket

### Slide: Pattern 2 — Parallel Split

One path splits into two or more concurrent branches. BPMN: a **Parallel Gateway** (+) forks. Example: Assign Courier + Cook Pizza.


#image: BPMN diagram — Accept Order, a parallel gateway splitting to Cook Pizza and Assign Courier

### Slide: Pattern 3 — Synchronization (Join)

Wait until multiple concurrent branches complete. BPMN: a **Parallel Gateway** joins. Example: Assign Courier + Cook Pizza.


#image: BPMN diagram — Cook Pizza and Assign Courier merging into a parallel join gateway

### Slide: Pattern 4 — Exclusive Choice

Choose one path based on a condition. BPMN: an **Exclusive Gateway** (X) with condition expressions. Example: Check Availability → Accept Order **X** Reject Order.


#image: BPMN diagram — a message start, Check Stock, exclusive gateway to Reject or Accept Order

### Slide: Pattern 5 — Simple Merge

Merge non-concurrent paths back into one. BPMN: a converging sequence flow — no gateway needed if no synchronization is required. Example: multiple paths lead to Eat Pizza.


#image: BPMN diagram — timer/message events for Pizza Received, Check Delivery Status, Eat Pizza

### Slide: Process = Orchestration

A **Process** describes a sequence/flow of activities. In BPMN it is a graph of flow elements (a sequence flow of activities, events, gateways).

A Process is an **orchestration**:

- The sequence flow represents control of a process.
- The **token** represents state for an instance.
- Generally a process orchestration lives within an address space (not distributed) — an embedded workflow or an external process manager.

#image: BPMN diagram — a Checkout Basket process (Create Basket, Validate Choice, Price Basket, Validate Delivery/Payment)  [→ resources/Shopping Flow As Sequence.drawio.png]

### Slide: What is Orchestration?

Focused on a single participant's perspective.

- Like writing your own script.
- Includes control flow, state, and decisions.
- All logic is local to the orchestrator.
- Often implemented via state machines or workflow engines.

### Slide: Tokens

- A **token** represents an instance of a process.
- A token flows down the process; it is the state of the process for that instance.

#image: BPMN collaboration — Customer and Shopping pools with message flows (Begin Shopping, Basket Price, Valid Basket)  [→ resources/Shopping Flow with Pools.drawio.png]

### Slide: Pizza Example — BPMN Orchestration (Customer Pool)

The customer journey as an orchestration.




#image: BPMN diagram — the Customer-lane pizza-ordering flow with reorder, rejection, delivery-status timer, cancellation  [no source in resources/ — the pizza BPMN family (Browse Pizzas / Cook Pizza / Assign Courier) is not in resources/; resources/Shopping Flow*.drawio is the *food-delivery* flow (Enter Location / Choose Restaurant / Add Menu Choices), a different diagram]

Presenter notes: In the demo we emulate this with HTTP calls (same as web/mobile). It's "in process" — we manage the token and its state through the flow. We show where we wait to receive a message. Debugging: we pause awaiting a message from another system, and can't see how the received values were set, or why we do/don't receive a message — for that we'd need the sender.

### Slide: Pizza Example — BPMN Orchestration (Pizza Shop Pool)

The pizza shop as an orchestration, initiated by a message.




#image: BPMN diagram — the Pizza Shop pool with Kitchen and Dispatch lanes (cooking and courier assignment)  [no source in resources/ — the pizza BPMN family (Browse Pizzas / Cook Pizza / Assign Courier) is not in resources/; resources/Shopping Flow*.drawio is the *food-delivery* flow (Enter Location / Choose Restaurant / Add Menu Choices), a different diagram]

Presenter notes: We send messages to act (message icon) and wait to receive messages (start and end). Same debugging blind-spot — to debug the flow to the customer we'd need breakpoints in both, which is fine if we own both, but not if they belong to different teams (we'd have to deploy their code).

### Slide: Pizza Example — BPMN Orchestration (Courier Pool)

The courier as an orchestration, initiated by a message.




#image: BPMN diagram — the Courier lane, Check Availability gateway to Reject/Accept Job, collect and deliver  [no source in resources/ — the pizza BPMN family (Browse Pizzas / Cook Pizza / Assign Courier) is not in resources/; resources/Shopping Flow*.drawio is the *food-delivery* flow (Enter Location / Choose Restaurant / Add Menu Choices), a different diagram]

Presenter notes: Same pattern — send messages to act, wait to receive. To debug the flow to the pizza shop and customer we'd need breakpoints in all of them.

### Slide: Pizza Example — Pools and Lanes




#image: BPMN diagram — a large multi-lane (Customer/Kitchen/Dispatch/Courier) collaboration with cross-lane message flows  [no source in resources/ — the pizza BPMN family (Browse Pizzas / Cook Pizza / Assign Courier) is not in resources/; resources/Shopping Flow*.drawio is the *food-delivery* flow (Enter Location / Choose Restaurant / Add Menu Choices), a different diagram]

Presenter notes: Multiple pools (Pizza Shop, Courier, Customer App) with message flows (App→Shop order; Shop→Courier pickup request; Courier→Shop ready; Shop→Courier pizza ready). We want to examine the *interaction* from a neutral perspective, but modelling it as one pool with lanes doesn't work well — some tasks reference interaction (waiting for delivery, collecting money), others are oblivious to partners (baking, eating). It is not semantically correct because message events always refer to messages received from *outside*.

### Slide: Collaboration and Choreography

- A **Collaboration** has multiple participants.
- The message exchange between participants in a collaboration is a **Choreography** — generally the flow of messages between participants; within each orchestrated process there are message events caught or raised.
- Processes *react* to what happens in the choreography — no one owns it (it has no tokens or state of its own).

#image: BPMN collaboration — Customer and Shopping pools with message flows  [→ resources/Shopping Flow with Pools.drawio.png]

### Slide: What is Collaboration?

Focused on how participants interact.

- Interaction might be within a workflow engine — but this creates coupling, and both participants must run in the engine.
- Interaction might be via an API — from an event-driven perspective, we are most interested in this model.

### Slide: Pools and Lanes

- A **Pool** is a participant in a collaboration (a role or an organization). Not required for the main internal pool (the modeler's own org); required for other organizations' processes.
- A **Lane** distinguishes sequences of activities within a pool. White box = can see process; black box = cannot.
- Activities within the pool are organised by sequence flow.

#image: BPMN collaboration — Customer and Shopping pools with labelled pools/lanes and message flows  [→ resources/Shopping Flow with Pools.drawio.png]

### Slide: Pizza Shop Collaboration

A collaboration diagram for the pizza-shop example.

#image: BPMN diagram — three pools (Customer, Pizza Shop, Courier) in a full collaboration with many message flows  [no source in resources/ — the pizza BPMN family (Browse Pizzas / Cook Pizza / Assign Courier) is not in resources/; resources/Shopping Flow*.drawio is the *food-delivery* flow (Enter Location / Choose Restaurant / Add Menu Choices), a different diagram]

### Slide: Choreography and Conversation

- A **Choreography** describes a sequence/flow of activities *between* participants — a graph of flow elements (a message flow of activities, events, gateways).
- A **Conversation** is a logical association of messages that can all be correlated. **Correlation Keys** associate messages in the same conversation (may be existing message data); the first task in a conversation *must* populate the conversation id.

#image: BPMN diagram — a horizontal flow with Customer/Shopping lane labels per task and message events  [→ resources/Shopping Choreography.drawio.png]

### Slide: What is Choreography?

Focused on interactions across multiple participants.

- Like describing a dance — no single owner of the flow.
- Defines who talks to whom, in what order.
- No centralized control.
- Cannot access shared internal data/state.

### Slide: Pizza Example — BPMN Choreography

The pizza-order choreography — the flow of messages between participants.




#image: BPMN choreography diagram — the pizza-order flow as message events across Customer, Pizza Shop, Courier  [no source in resources/ — resources/Shopping Choreography.drawio.png is the *shopping-basket* choreography (Begin Shopping / Add Item / Basket Price), not the pizza one]

Presenter notes: Even this simple interaction produces a set of messages flowing between participants. Choreography is what happens "between" — it has no explicit owner. When flow leaves your application (or workflow engine) it "goes blind": the **event horizon**. You understand your workflow — it's in your code — but debugging becomes hard because at times nothing happens that's supposed to, and you struggle to know why.

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
| Example | Pizza Shop coordinates cook + courier | Customer + Shop + Courier interact |

Presenter notes: Implementation paths depend on model type — embedded logic (orchestration) vs. API contracts/events (choreography). Clear boundaries → better automation decisions and a clearer division between messaging and eventing.

---

### Slide: Durable Execution

Long-running processes must:

- Survive restarts.
- Handle retries and failures.
- Resume after waiting (e.g. for payment or a courier).

Durable execution = we **persist activity state** to indicate which steps are complete, when we're awaiting an event, etc.

### Slide: Activities and Resources

Broadly, a software component manages **activities** and **resources** (Pat Helland).

- **Resources:** domain concepts we manage — restaurants, couriers, customers.
- **Activities:** one or more sequences for our interaction with resources.
- As the token moves through the sequence we update resources *and* the activity (to indicate progress).
- The implementation question: **where does activity state live, and who updates it?**

### Slide: Activities and Resources — Worked Example

- **Cashier → Pricer:** `get pricing details()` → `item price()` (waiting for response).
- **Cashier → Payment Provider:** `take payment()` → `payment taken()` (waiting for response).
- **Activity** (usually a service task) — glue code that calls domain logic internally or messages another app; could be a framework, a bespoke state machine, or pipes and filters.
- **Resources** — code/data managing shared items coordinated across activities (inventory widgets, truck space) — our domain model.
- Our workflow stores the token state (where are we in the flow?), and there is a choreography — the messages we exchange with other participants running their own flows.

Presenter notes: Per Helland — each entity must remember state about its partners on a partner-by-partner basis; call this an **activity**. An entity may have many activities if it interacts with many partners.

### Slide: Handlers + Activity State Updates

Handlers process events (change resources) and update activity state.

- Durable because state is stored (e.g. a database), but control flow is **implicit** — activity state is often implicit (e.g. within an aggregate).
- Great for simple workflows, but logic becomes scattered across handlers.
- Becomes complex with split/join/choice/merge (not a sequence), and with retry / circuit breakers / compensation.
- Relies on **guaranteed delivery** (store work for retry unless ack'd) and **Transactional Messaging (Outbox)**.

Presenter notes: Baseline automation. E.g. an `OrderReceivedHandler` looks up the order and sets state = Preparing. Handlers process events and update persistent state; durable via stored state, but control flow is implicit — logic scatters across handlers.

### Slide: Handlers — Illustration

A diagram of the handler-based approach.


#image: C# code screenshot — an async order handler using a transaction, postbox and the outbox pattern

### Slide: (Fault) Handlers + Activity State Updates

How do we handle **compensation** flows with handlers?

- **Fault Message:** for reliable In-Only, a dedicated fault channel is required (used only for compensation); for In-Out, the response-channel message should indicate fault, not success.
- May retry the handler, and only after X failures run the fallback.
- On fault, run a "fallback handler" that initiates compensating action — reverse actions so far; write an "undo" for each "do".
- A straightforward approach: send a fault message back upstream and undo on receipt.

Presenter notes: The **Saga** pattern — long-running transactions in distributed systems; when you can't roll back, you undo. Name from a 1980s paper on long-lived DB transactions. BPMN supports this via compensation events linking tasks with undo tasks; a workflow engine executes the necessary undo actions. (Ruecker, *Practical Process Automation*.)

### Slide: State Machine + Activity State Updates

When handler interaction becomes complex, make the activity **explicit**.

- A **State Machine** represents the activity and triggers actions on transitions.
- Transitions are caused by receiving a message.
- The handler loads the state machine for the conversation id, triggers the transition denoted by the message, and runs the associated code.
- Save the new state and ack the message.

Presenter notes: States e.g. Received → Preparing → Ready → OutForDelivery → Delivered; transitions triggered by events/commands; implemented via the state pattern, switch statements, or a library (e.g. Stateless); durable via persisted state + event log. Benefits: predictable, easier to visualize/test, avoids duplication across handlers. Drawback: no concurrency or waiting logic.

### Slide: State Machine — Illustration

A diagram of the state-machine approach.


#image: C# code screenshot — an OrderStateMachine (MassTransit) with Initially/During states and transitions

### Slide: (Fault) State Machine + Activity State Updates

How do we handle compensation with a state machine?

- The "saga" pattern in messaging frameworks is typically a state machine — it guarantees that on a fault, the machine transitions back to "safe".
- Implementations run all fault transitions to safe *before* acking the fault message.
- May retry the transition, and only after X failures run compensation.
- On fault, transition to a faulted state and initiate a compensating flow to "safe" (reverse actions; write an "undo" for each "do").
- Requires **durable execution** — if we fault partway, on restart we resume.

Presenter notes: As above — the Saga undoes rather than rolls back; BPMN compensation events link tasks with undo tasks. (Ruecker, *Practical Process Automation*.)

### Slide: Routing Slip + Activity State Updates

To **distribute** steps in the sequence, transport the activity state *in the message*.

- A **routing slip** is an envelope carrying activity state (next step, context, etc.) — "Message As the Engine of Application State".
- The handler updates state when work is done, forwards according to the slip, then acks.
- Complex if "next" is dynamic routing (the code must understand how to execute).
- Complex because you distribute the steps — hard to observe (OpenTelemetry).

### Slide: (Fault) Routing Slip + Activity State Updates

How do we handle compensation with a routing slip?

- "Next" is now the *fault* next from this step — what we need to reverse.
- Context is "faulted".
- The handler updates state when work is done, forwards according to the slip, then acks.

### Slide: Workflow Engines + Activity State Updates

When we want more than state transitions (split, join, merge, choice), use a **workflow engine**.

- Explicitly models a sequence of activities and gateways; may support BPMN (or a proprietary language) with visual modelling.
- A step receives the token; the step is **glue** — invokes domain action, calls another service, sends a message.
- A **job scheduler** provides durable execution; typically any instance can resume a paused job (distributed).
- A step may wait for an event or timer to resume — the handler equivalent, or triggered by the handler calling the engine.

Presenter notes: External orchestrators — Temporal, Camunda, Azure Logic Apps, AWS Step Functions. Support wait states (await PizzaReady), parallel branches, timeouts, retries, visual modeling. Durable by design (execution state + workflow history stored); suited to complex, distributed systems. Example steps: StartCookingPizza → WaitForPizzaReady → DispatchCourier → WaitForPickup → MarkAsDelivered.

### Slide: (Fault) Workflow Engines + Activity State Updates

How do we handle compensation with a workflow engine?

- Is the error a **business** error or a **technical** error?
- A **retry** frequently handles technical faults. If retry fails and a catch is present, a fallback runs; with no catch, the workflow rolls back to the last wait state or terminates.
- A known **business** error (e.g. card declined) is usually modelled explicitly as a branch via a gateway.

### Slide: Embedded vs. External Workflow Engines

Weighing engines embedded in a service against external orchestrators.

### Slide: Workflow Engines — Lessons from SOA

Presenter notes: External orchestration is not an anti-pattern, but requires care. Keep core domain logic inside services; let the workflow engine coordinate *outcomes*, not fine-grained steps; consider choreography or local orchestration for autonomy.

### Slide: Smart Endpoints, Dumb Pipes

ESB products often include sophisticated routing, choreography, transformation, and business rules. The microservice community favours the alternative: **smart endpoints and dumb pipes**. (martinfowler.com/articles/microservices.html)

Presenter notes: Microservices promote smart services and minimal messaging infrastructure. External workflow engines risk **anaemic services** — all domain logic moves out, and services become passive executors of workflow directives.

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

---

## Putting It Together

### Slide: Putting It Together

Section marker: revisiting the fax/pizza workflow through the lens of the patterns, annotating each interaction with its messaging/eventing exchange pattern.

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
