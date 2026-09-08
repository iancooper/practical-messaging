#!/usr/bin/env python3
"""Day 2 §*Flow and Reactive Programming* -- the OO/dataflow/FBP/Reactive run.

    python3 tools/flow_reactive.py                  # rebuild all
    python3 tools/flow_reactive.py flow-bulkhead
    python3 tools/flow_reactive.py --list

**Run 2 of the redraw.** Twenty-five figures across one section, and the section is
an argument in two halves, so the run has exactly **two vocabularies** and never
mixes them:

  * **Movement B -- the wrong answer.** Objects and services are **boxes**, joined by
    **call arrows**. Somebody is in charge, and you can see who: every arrow starts
    at a caller.
  * **Movements C and D -- the answer.** Nodes are **hexagons with ports**
    (`Diagram.node`), packets are **dashed squares** (`Diagram.packet`), and an arc is
    a plain carbon arrow -- a *buffered* arc is a `pipe` with packets in it, which is
    run 1's queue glyph, because a bounded buffer is a queue.

That split is not decoration: it is the section's claim. A reader who sees a hexagon
knows nothing is in charge, and a reader who sees a box knows something is.

Constants, so twenty-five drawings cannot drift:

  * **Data flows left to right.** In-ports on the left, out-ports on the right,
    nothing crosses a node to reach a port. `Diagram.node` owns this.
  * **A store is a cylinder**, tied to its owner with a dashed muted line.
  * **One idea in red per figure**, stated as a red note at the top -- the sentence
    the presenter says out loud -- and a muted note at the bottom for the caveat.
  * **Paired figures contrast through red.** The class and the service red the same
    thing (encapsulated data) because *same idea, bigger unit* is the argument;
    the gateway is red in *Entity Services* and its **absence** is red in
    *Partitioning*; the lookup port reds the pause, Build Lookup reds its absence;
    backpressure reds the slowing, load-shedding reds the discarding.

Hand-drawn register, like the rest of the deck outside BPMN.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagram import Diagram, ANNOTATION, COMMENT, MUTED, INK, CARBON      # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "resources")
FIGURES = {}

# Every figure in this run is compacted to this width before it is written. The label
# floor is in canvas units and the figure is scaled to fit its slide, so a wide canvas
# is not more detail -- it is smaller type in the room. 890 is where the 18pt diagram
# floor meets the deck's 18pt body floor at full slide width. `Diagram.compact` shrinks
# the distances and leaves the type alone; see its docstring.
TARGET_W = 890


def figure(name):
    """Register a figure -- and compact it on the way out.

    **The compaction belongs here, not in `main()`.** Put it in `main()` and
    `lint_figures.py` measures the geometry as it was written rather than as it is
    rendered, which is exactly what happened: a note lying across a hexagon was
    invisible to the linter for as long as the two disagreed. One definition, and
    everything downstream sees the same drawing.
    """
    def wrap(fn):
        def build():
            return fn().compact(TARGET_W)
        build.__doc__ = fn.__doc__
        build.__name__ = fn.__name__
        FIGURES[name] = build
        return fn
    return wrap


# ---- helpers the whole run shares -------------------------------------------

def idea(d, text):
    """The red sentence at the top of every figure -- the one the presenter says."""
    d.note(d.w / 2, 44, text, ANNOTATION, 19)


# a foot comment longer than this is wrapped. Text does not scale when `compact()`
# shrinks a figure, so one long line sets the floor on how narrow the figure can get --
# five of these were wide enough to block the whole run. 640 units is about 90
# characters of Caveat at the 18pt floor, which is a sane measure to read anyway.
CAVEAT_MEASURE = 640


def caveat(d, text, y=None):
    """The muted note at the foot: what the figure does not say.

    **It wraps itself**, because every figure in this run gets `compact()`ed and a
    caveat is the longest text on most of them. Wrapping here rather than by hand in
    thirty-odd call sites means a reworded caveat cannot quietly re-block the run.
    """
    def wrap(measure):
        lines, line = [], ""
        for word in text.split(" "):
            trial = f"{line} {word}".strip()
            if line and d._advance(dict(kind="note", label=trial, size=18)) > measure:
                lines.append(line)
                line = word
            else:
                line = trial
        return lines + [line]

    n = len(wrap(CAVEAT_MEASURE))
    # ...then pull the measure in as far as it will go without needing another line,
    # so the lines come out even. A greedy wrap at a fixed width leaves a two-word
    # orphan on the last line often enough to be worth the four lines of search.
    lo, hi = 0, CAVEAT_MEASURE
    while hi - lo > 4:
        mid = (lo + hi) / 2
        if len(wrap(mid)) > n:
            lo = mid
        else:
            hi = mid
    d.note(d.w / 2, y if y is not None else d.h - 26, "\n".join(wrap(hi)), COMMENT, 15)


def pkt_on(d, x, port, label="", accent=False, w=30, h=26):
    """A packet sitting on a port's own line.

    Centring it on the port rather than on a y you typed means the arc between them
    is horizontal -- run 1 lost time to arrows that were one or two units off level
    and looked like mistakes."""
    py = port["y"] + port["h"] / 2
    return d.packet(x, py - h / 2, w=w, h=h, label=label, accent=accent)


# ---- Movement B: the wrong answer, in boxes ---------------------------------

@figure("flow-oo-class")
def oo_class():
    """*Object-Oriented Programming.* Deliberately uncontroversial -- the room
    proposed this before the exercise -- so the figure names the parts and argues
    only one thing: the data is inside.

    **The message arrow lands on the behaviours, not on the class box.** Aiming at
    the box's mid-left put the arrowhead beside the fields, which draws the opposite
    of what the red note says."""
    d = Diagram("Object-Oriented Programming", w=1060, h=546)
    idea(d, "the data lives inside the object, and only the object’s own "
            "behaviours may touch it")

    base = d.box(384, 104, 220, 56, "Base Class", size=17)

    X, Y, W = 344, 226, 300
    cls = d.box(X, Y, W, 218, "")
    d.note(X + W / 2, Y + 30, "Order", INK, 18)
    d.rule(X, Y + 46, W, INK, 1.3)
    for i, f in enumerate(("- items", "- total")):
        d.note(X + 22, Y + 82 + i * 28, f, ANNOTATION, 16, anchor="start")
    d.rule(X, Y + 124, W, INK, 1.3)
    for i, m in enumerate(("+ addItem(line)", "+ checkout()")):
        d.note(X + 22, Y + 160 + i * 28, m, INK, 16, anchor="start")

    # the label rides in the gap between the class and its base: `ly` is text-space and
    # does not scale, so at the effective-width target a centred label sat on the base
    # class's own bottom edge
    d.arrow(cls, base, "inherits", sides=("t", "b"), lx=42, ly=8)
    d.note(X + W + 30, Y + 74, "private — nobody\noutside reaches in",
           ANNOTATION, 15, anchor="start")
    d.note(X + W + 30, Y + 168, "the responsibilities\nthe role carries",
           COMMENT, 15, anchor="start")
    d.note(624, 116, "the behaviour that answers a message\n"
                     "may come from the base class:\ndynamic dispatch",
           COMMENT, 15, anchor="start")

    caller = d.box(80, 386, 200, 76, "another object", size=17)
    d.arrow(caller, (X, Y + 176))
    d.note(180, 336, "a message — the behaviour to run,\nand what to run it on",
           CARBON, 15)

    caveat(d, "this is the tool everyone reaches for first, and nothing here is "
              "wrong yet — the next three slides scale it up")
    return d


@figure("flow-call-and-return")
def call_and_return():
    """*Call and Return, and the God Object.* The red is `Cart`, not `main`: `main`
    being the entry point is unremarkable, and what costs you is that one object in
    the middle ends up knowing every step."""
    d = Diagram("Call and Return, and the God Object", w=1240, h=640)
    idea(d, "every step of the use case passes through one object — "
            "so it changes whenever any step does")

    main = d.group(250, 92, 740, 56, "main — the entry point", dashed=True)
    cart = d.box(540, 264, 180, 88, "Cart", accent=True, size=17)

    ring = {}
    for name, (x, y) in (("Restaurant", (200, 254)), ("Account", (900, 254)),
                         ("Menu", (300, 458)), ("Payment", (540, 500)),
                         ("Order", (790, 458)), ("Delivery", (1030, 458))):
        ring[name] = d.box(x, y, 160, 74, name, size=17)

    # main fans out, so both calls need their own exit point: the automatic choice
    # puts them on the same bottom-centre and the Account call then cuts the figure
    d.arrow((630, 148), cart, sides=(None, "t"))
    d.arrow((980, 148), ring["Account"], sides=(None, "t"))
    d.arrow(cart, ring["Restaurant"], sides=("l", "r"))
    d.arrow(cart, ring["Account"], sides=("r", "l"))
    d.arrow(cart, ring["Menu"], sides=("b", "t"), via=[(560, 420)])
    d.arrow(cart, ring["Payment"], sides=("b", "t"))
    d.arrow(cart, ring["Order"], sides=("b", "t"), via=[(700, 420)])
    d.arrow(ring["Order"], ring["Delivery"], sides=("r", "l"))

    d.note(196, 216, "each arrow is a call, and control\n"
                     "returns the way it came", COMMENT, 15, anchor="start")
    caveat(d, "no desk in this morning's takeaway knew the whole process. "
              "Cart knows all of it.")
    return d


@figure("flow-soa-service")
def soa_service():
    """*SOA Is OO at Macro Scale.* The red is deliberately the **same** red as the
    class figure -- the encapsulated data -- because *same idea, bigger unit* is the
    only claim the slide makes. Josuttis is the yardstick the next figure fails.

    **The store sits to the right of the operations, not below them**, so the return
    message can be routed under the service without crossing the tie between a
    service and its own data."""
    # **The service stands 70 units further right, and `operations` is 80 wider, than
    # the drawing needs.** Both are legibility, not layout. The gap between the
    # Consumer and the Service's dashed edge has to hold `input message` -- 84 units of
    # type that does not shrink -- with clearance at both ends, and the operation list
    # has to sit wholly INSIDE its box or it reads as lying across the stroke. At the
    # effective-width target neither was true. This figure is fitted by its height, so
    # the width it spends to fix both is free.
    d = Diagram("SOA Is OO at Macro Scale", w=1240, h=540)
    idea(d, "same idea, a bigger unit: operations, and the data those operations "
            "need, shut away behind them")

    d.group(520, 132, 680, 340, "Service")
    ops = d.box(570, 190, 380, 112, "operations", size=17)
    d.note(760, 282, "placeOrder · cancelOrder · trackOrder", INK, 14)
    # 18 units higher than the operations box's own mid-line, to open the gap the
    # note below it needs. Pushing the NOTE down instead put its third line across the
    # Service container's dashed foot -- which `lint_figures.py` does not see, because
    # a note inside a container is normally exactly what a container is for.
    store = d.cylinder(970, 282, 180, 88, "its own data", accent=True)
    d.attach(ops, store, sides=("r", "l"))

    con = d.box(110, 198, 200, 96, "Consumer", size=17)
    # centred, this label lands on the Service container's own border
    d.arrow(con, ops, "input message", sides=("r", "l"), lx=-32, ly=-12)
    d.arrow(ops, con, "output message", sides=("b", "b"),
            via=[(670, 400), (210, 400)], ly=24, lx=-6)

    # below the return path, not beside it: the riser out of the service crosses
    # x=210, which is exactly where a note anchored at the Consumer's left edge sits
    d.note(110, 452, "endpoint — where it lives\nbinding — how you talk to it",
           COMMENT, 15, anchor="start")
    d.note(1060, 429, "an implementation detail:\nyou reach it only through\nan operation",
           COMMENT, 14)
    caveat(d, "“a service should represent a self-contained functionality that "
              "corresponds to a real-world business activity” — and a desk is a "
              "business activity")
    return d


@figure("flow-entity-services")
def entity_services():
    """*Feature Envy -- You Built a Distributed Monolith.* Deliberately the
    call-and-return figure again with a gateway where `main` was: the shape being
    recognisable is the argument, so the ring keeps its positions.

    The gateway is the one thing in red, and *Partitioning and Dataflow* later reds
    the space where it is not -- which is the pair that answers this slide."""
    d = Diagram("Feature Envy — You Built a Distributed Monolith", w=1240, h=730)
    idea(d, "you distributed the objects and kept the god object — "
            "the gateway is `main`")

    d.phone(586, 88, 68, 104)
    d.note(566, 142, "Device", INK, 17, anchor="end")
    gw = d.box(250, 236, 740, 58, "API Gateway", accent=True, size=17)
    d.arrow((620, 192), gw, sides=(None, "t"))

    cart = d.box(540, 372, 180, 84, "Cart", size=17)
    ring = {}
    for name, (x, y) in (("Restaurant", (200, 366)), ("Account", (900, 366)),
                         ("Menu", (300, 552)), ("Payment", (540, 590)),
                         ("Order", (790, 552)), ("Delivery", (1030, 552))):
        ring[name] = d.box(x, y, 160, 72, name, size=17)

    d.arrow((630, 294), cart, sides=(None, "t"))
    d.arrow((980, 294), ring["Account"], sides=(None, "t"))
    d.arrow(cart, ring["Restaurant"], sides=("l", "r"))
    d.arrow(cart, ring["Account"], sides=("r", "l"))
    d.arrow(cart, ring["Menu"], sides=("b", "t"), via=[(560, 516)])
    d.arrow(cart, ring["Payment"], sides=("b", "t"))
    d.arrow(cart, ring["Order"], sides=("b", "t"), via=[(700, 516)])
    d.arrow(ring["Order"], ring["Delivery"], sides=("r", "l"))

    d.note(196, 476, "entity services: a resource each,\nand CRUD on it",
           COMMENT, 15, anchor="start")
    d.note(1044, 476, "the domain logic has to live\nsomewhere, and it is not here",
           COMMENT, 15, anchor="end")
    caveat(d, "this is what call and return becomes when you distribute it — "
              "and it hands back the independent deployability this morning "
              "called the prize", y=700)
    return d


# ---- Movement C: the formalism, in hexagons and packets ---------------------

@figure("flow-dataflow-graph")
def dataflow_graph():
    """*Data Flow Programming.* The nodes carry ports even though this figure is
    about the graph, because it is the same glyph as every figure after it -- a node
    that loses its ports here and grows them two slides later teaches the shape
    twice."""
    d = Diagram("Data Flow Programming", w=1200, h=560)
    idea(d, "a node runs because a packet arrived on its input — "
            "nothing calls it, and there is no `main`")

    a = d.node(110, 224, 160, 100, "read", ins=("",), outs=("",))
    b = d.node(360, 224, 160, 100, "split", ins=("",), outs=("", ""), accent=True)
    c = d.node(620, 118, 160, 100, "price", ins=("",), outs=("",))
    e = d.node(620, 330, 160, 100, "tax", ins=("",), outs=("",))
    f = d.node(880, 224, 160, 100, "total", ins=("",), outs=("",))

    d.arrow(a["ports"]["out0"], b["ports"]["in0"], sides=("r", "l"))
    d.arrow(b["ports"]["out0"], c["ports"]["in0"], sides=("r", "l"))
    d.arrow(b["ports"]["out1"], e["ports"]["in0"], sides=("r", "l"))
    d.arrow(c["ports"]["out0"], f["ports"]["in0"], sides=("r", "l"))
    d.arrow(e["ports"]["out0"], f["ports"]["in0"], sides=("r", "l"))

    d.note(440, 196, "fires when its input arrives", ANNOTATION, 15)
    d.note(190, 358, "a node —\nan operation", INK, 15)
    d.note(600, 484, "an arc — where the data moves", INK, 15)
    d.arrow((586, 462), (566, 352), muted=True)
    caveat(d, "in call and return, control moves and data sits still. Here it is the "
              "other way round — and you already use one: pipes and filters.")
    return d


@figure("flow-node-ports")
def node_ports():
    """*Nodes, Ports and Firing*, first of two. The three phases run along the bottom
    as a dotted strip under the part of the drawing each one belongs to, so the
    reader sees *when* each happens rather than reading a list."""
    d = Diagram("Nodes, Ports and Firing", w=1140, h=500)
    idea(d, "it is reactive because it fires in response to an event — "
            "a packet arriving is the event")

    n = d.node(420, 130, 300, 172, "a black box", ins=("in",), outs=("out",),
               accent_ports=("in",))
    p_in = pkt_on(d, 210, n["ports"]["in"], accent=True)
    p_out = pkt_on(d, 900, n["ports"]["out"])
    d.arrow(p_in, n["ports"]["in"], sides=("r", "l"), accent=True)
    d.arrow(n["ports"]["out"], p_out, sides=("r", "l"))

    d.note(570, 254, "you do not see inside it,\nand it does not see out",
           COMMENT, 14)

    for x0, w0, label in ((196, 240, "activation — it fires"),
                          (452, 236, "process, and make an answer"),
                          (716, 236, "push the answer out")):
        d.rule(x0, 356, w0, MUTED, 1.6)
        d.note(x0 + w0 / 2, 382, label,
               ANNOTATION if "activation" in label else INK, 15)

    d.note(570, 442, "generally a node is single-threaded: one clerk does one "
                     "document at a time.\nThroughput comes from having many "
                     "nodes, not from one node doing many things.", COMMENT, 15)
    return d


@figure("flow-two-nodes")
def two_nodes():
    """*Nodes, Ports and Firing*, second of two. Paired with the figure above through
    red: that one reds the firing, this one reds what crosses -- and what crosses is
    the whole of the contract between two nodes."""
    d = Diagram("Two Nodes Passing Packets", w=1180, h=440)
    idea(d, "the only thing that crosses between two nodes is data — "
            "no call, no return, no stack")

    a = d.node(200, 148, 220, 132, "price", ins=("in",), outs=("out",))
    b = d.node(760, 148, 220, 132, "total", ins=("in",), outs=("out",))

    p0 = pkt_on(d, 60, a["ports"]["in"], accent=True)
    p1 = pkt_on(d, 575, a["ports"]["out"], accent=True)
    p2 = pkt_on(d, 1090, b["ports"]["out"], accent=True)
    d.arrow(p0, a["ports"]["in"], sides=("r", "l"))
    d.arrow(a["ports"]["out"], p1, sides=("r", "l"))
    d.arrow(p1, b["ports"]["in"], sides=("r", "l"))
    d.arrow(b["ports"]["out"], p2, sides=("r", "l"))

    d.note(590, 274, "a packet", ANNOTATION, 15)
    d.note(590, 342, "just data: a primitive or a compound value, and it may\n"
                     "carry other packets inside it", COMMENT, 15)
    caveat(d, "neither node knows who wrote the packet or who will read the next "
              "one — it knows the name of a port")
    return d


@figure("flow-arc-buffers")
def arc_buffers():
    """*Capacity, Backpressure and Node Lifetime.* The buffered arc is drawn as run
    1's `pipe` with packets in it, deliberately: a bounded buffer **is** a queue, and
    a reader who met the pipe yesterday should not have to be told twice."""
    d = Diagram("Capacity, Backpressure and Node Lifetime", w=1200, h=512)
    idea(d, "we do not fire a node to read its input if there is no space on its "
            "output — a full buffer is the whole of backpressure")

    a = d.node(90, 190, 200, 130, "price", ins=("in",), outs=("out",))
    b = d.node(910, 190, 200, 130, "total", ins=("in",), outs=("out",))

    pipe = d.pipe(360, 222, 470, 66, accent=True)
    for i in range(4):
        d.packet(400 + i * 100, 242, w=30, h=26, accent=True)
    d.arrow(a["ports"]["out"], pipe, sides=("r", "l"))
    d.arrow(pipe, b["ports"]["in"], sides=("r", "l"))

    d.note(595, 190, "the arc: a pipe with a capacity, and it is full",
           ANNOTATION, 15)
    d.note(160, 366, "push — something arrived\nand there is work to do",
           INK, 15)
    d.note(1010, 366, "pull — a sink asked\nfor work", INK, 15)
    d.note(595, 372, "buffers are what let the two run at once: price can push\n"
                     "while total is still busy. Throughput is then the slowest node.",
           COMMENT, 15)
    caveat(d, "links with infinite capacity exist only in theory, so when the buffer "
              "fills there are exactly two answers: slow the producer, or drop data")
    return d


@figure("flow-fbp-component")
def fbp_component():
    """*Flow-Based Programming*, first of three -- the vocabulary figure.

    The red is the one FBP-specific claim on it: a component knows the **name of a
    port** and nothing about the connector behind it. That is what lets an arc turn
    into a queue two slides later without the component noticing, so it is worth the
    red even on a naming slide."""
    d = Diagram("Flow-Based Programming — Component, Port, Packet", w=1200, h=500)
    idea(d, "a component knows the name of a port and nothing about what is behind "
            "it — so the connector can be swapped for anything")

    n = d.node(450, 180, 300, 156, "Take Order", ins=("in",), outs=("out",),
               accent_ports=("in", "out"))
    p_in = pkt_on(d, 190, n["ports"]["in"], label="IP")
    p_out = pkt_on(d, 980, n["ports"]["out"], label="IP")
    d.arrow(p_in, n["ports"]["in"], sides=("r", "l"))
    d.arrow(n["ports"]["out"], p_out, sides=("r", "l"))

    d.note(600, 384, "the component — where the behaviour lives", INK, 15)
    d.note(190, 336, "an information packet:\nan independent, structured\n"
                     "piece of information", INK, 15)
    d.note(1000, 336, "a connector:\na bounded pipe\nof packets", INK, 15)
    # the ports carry the red themselves rather than a note with a leader line:
    # every pointer aimed at a port either crossed the hexagon or struck through the
    # port's own label, which sits immediately above the dot
    d.note(600, 152, "the port — a named point where a connection makes contact",
           INK, 15)
    caveat(d, "in OO the object holds the state; in FBP the state is in the packet, "
              "and it is out there on a connector rather than in storage")
    return d


@figure("flow-fbp-lifetime")
def fbp_lifetime():
    """*Flow-Based Programming*, second of three -- lifetime.

    Red is on **suspend, not terminate**, which the presenter notes single out: it is
    Day 1's message pump described from the other side, and it is the clerk who stays
    at the desk rather than being hired per document."""
    d = Diagram("Flow-Based Programming — Packet Lifetime", w=1200, h=520)
    idea(d, "a component suspends when there is no work — it does not terminate, "
            "and it is not started per packet")

    n = d.node(450, 178, 300, 150, "Take Order", ins=("in",), outs=("out",))
    p_in = pkt_on(d, 190, n["ports"]["in"], label="IP")
    p_out = pkt_on(d, 980, n["ports"]["out"], label="IP")
    d.arrow(p_in, n["ports"]["in"], sides=("r", "l"))
    d.arrow(n["ports"]["out"], p_out, sides=("r", "l"))

    # each bracket runs from the packet to the port that ends it, so the gap between
    # them is exactly the component's own span — which is the point of the figure
    d.rule(190, 132, 260, MUTED, 1.6)
    d.note(320, 118, "this packet's lifetime", INK, 15)
    d.rule(750, 132, 300, MUTED, 1.6)
    d.note(900, 118, "and this one's — a different packet", INK, 15)

    d.rule(450, 372, 300, ANNOTATION, 2.0)
    d.note(600, 400, "process, then wait", ANNOTATION, 16)
    d.icon(600, 352, "clock", accent=True, r=12)

    d.note(600, 448, "consuming a packet destroys it; sending one creates a new "
                     "one. The component outlives both.", COMMENT, 15)
    caveat(d, "this is the message pump from Day 1, described from the other side "
              "of the loop")
    return d


@figure("flow-fbp-ports")
def fbp_ports():
    """*Flow-Based Programming*, third of three -- the port rules.

    The asymmetry is the content, so the red is on the **single writer** rule: many
    connections may arrive on an in-port, which is how you sequence work, but an
    out-port has exactly one, which is what makes a component's output a fact rather
    than a negotiation."""
    d = Diagram("Flow-Based Programming — Ports and Writers", w=1240, h=540)
    idea(d, "many writers may share an in-port; an out-port has exactly one — "
            "so what leaves a component is never contended")

    n = d.node(470, 196, 300, 200, "Take Order",
               ins=("in", "alt_in"), outs=("out", "other_out"),
               accent_ports=("out", "other_out"))
    a, b = n["ports"]["in"], n["ports"]["alt_in"]
    for i, p in enumerate((a, a, b)):
        src = d.packet(150, 210 + i * 70, w=30, h=26)
        d.arrow(src, p, sides=("r", "l"), via=[(330, 223 + i * 70)])
    for name in ("out", "other_out"):
        port = n["ports"][name]
        dst = pkt_on(d, 1000, port, accent=True)
        d.arrow(port, dst, sides=("r", "l"), accent=True)

    d.note(240, 430, "multiple connections may arrive\non one in-port — that is how\n"
                     "you sequence work", COMMENT, 15)
    d.note(1010, 430, "one connection each,\nand only one", ANNOTATION, 15)
    caveat(d, "a component may have as many ports as it needs; the rule is about "
              "writers, not about how many ports there are")
    return d


@figure("flow-fbp-iip")
def fbp_iip():
    """*FBP -- Initial Information Packets.* Red on the IIP itself, because the
    question the slide answers is *how does a node that has just started know
    anything?* -- and the answer arrives on a port of its own."""
    d = Diagram("FBP — Initial Information Packets", w=1220, h=470)
    idea(d, "a node that has just started knows nothing — the IIP is the standing "
            "instruction pinned above the desk")

    n = d.node(600, 176, 280, 160, "Price Order", ins=("iip_in", "in"),
               outs=("out",), accent_ports=("iip_in",))
    iip = pkt_on(d, 330, n["ports"]["iip_in"], label="IIP", accent=True, w=38)
    d.arrow(iip, n["ports"]["iip_in"], sides=("r", "l"), accent=True)

    y = n["ports"]["in"]["y"] + n["ports"]["in"]["h"] / 2
    for i, lab in enumerate(("CP", "IP", "IP", "CP")):
        d.packet(180 + i * 74, y - 13, w=44, h=26, label=lab)
    d.arrow((476, y), n["ports"]["in"], sides=(None, "l"))
    d.rule(180, y + 30, 296, MUTED, 1.6)
    d.note(328, y + 58, "control packets bracket a stream into groups", COMMENT, 15)

    p_out = pkt_on(d, 980, n["ports"]["out"])
    d.arrow(n["ports"]["out"], p_out, sides=("r", "l"))

    d.note(330, 138, "configuration, or a starting value —\nread once, at start-up",
           ANNOTATION, 15)
    caveat(d, "MQTT retained messages are the same idea: the broker holds the last "
              "value on a topic so a late subscriber gets state immediately")
    return d


@figure("flow-lookup-question")
def lookup_question():
    """*FBP -- Where Do Lookups Live?*, first of three: the question.

    **Drawn against the slide, not the old marker.** The 2021 caption asked whether
    *A* needs data from another node; the slide, and both figures that answer it, put
    the need on **B** -- so B is the one that stops. Getting that backwards would
    have every arrow in the next two figures pointing the wrong way."""
    d = Diagram("FBP — Where Do Lookups Live?", w=1160, h=520)
    idea(d, "B has to act on something only A knows — and nothing arriving on B's "
            "in-port carries it")

    a = d.node(560, 128, 210, 118, "A", ins=("in",), outs=("out",))
    b = d.node(300, 340, 210, 118, "B", ins=("in",), outs=("out",))
    for n, xin, xout in ((a, 380, 850), (b, 120, 590)):
        d.arrow(pkt_on(d, xin, n["ports"]["in0"]), n["ports"]["in0"],
                sides=("r", "l"))
        d.arrow(n["ports"]["out0"], pkt_on(d, xout, n["ports"]["out0"]),
                sides=("r", "l"))

    # run 1's way of drawing a thing that is not there: the arc is dashed and
    # struck out, because a solid red arrow would assert the connection exists
    d.arrow(a, b, accent=True, dashed=True, sides=("b", "t"))
    d.icon(535, 293, "cross", accent=True, r=14)
    d.note(800, 300, "A knows something B will need,\nand there is no arc that "
                     "brings it", COMMENT, 15)
    caveat(d, "two answers, and it is the same choice as Day 1's reference data: "
              "ask for it on demand, or hold a copy made in advance")
    return d


@figure("flow-lookup-port")
def lookup_port():
    """*Where Do Lookups Live?*, second of three: the lookup port.

    Red is the **pause** -- the walk of shame -- and the next figure reds its
    absence. That pair is the argument, so neither figure may red anything else.

    **The response takes the long way round on purpose.** A query leaves on an
    out-port and an answer arrives on an in-port, so with ports fixed left-in /
    right-out the reply has to travel back across the whole drawing. That is not a
    routing accident, it is the round trip B is paying for, and shortening it by
    putting an in-port on the right would hide the cost."""
    d = Diagram("FBP — the Lookup Port", w=1240, h=700)
    idea(d, "B stops until A answers — on demand, and now B is only as available "
            "as A is")

    a = d.node(700, 128, 240, 150, "A", ins=("in", "in_lookup"),
               outs=("out", "out_result"))
    b = d.node(180, 400, 240, 150, "B", ins=("in", "in_result"),
               outs=("out", "out_lookup"))

    d.arrow(pkt_on(d, 40, b["ports"]["in"]), b["ports"]["in"], sides=("r", "l"))
    d.arrow(b["ports"]["out"], pkt_on(d, 470, b["ports"]["out"]), sides=("r", "l"))
    d.arrow(pkt_on(d, 480, a["ports"]["in"]), a["ports"]["in"], sides=("r", "l"))
    d.arrow(a["ports"]["out"], pkt_on(d, 1000, a["ports"]["out"]), sides=("r", "l"))

    d.arrow(b["ports"]["out_lookup"], a["ports"]["in_lookup"], "query",
            sides=("r", "l"), via=[(600, 500), (600, 228)], lx=44)
    d.arrow(a["ports"]["out_result"], b["ports"]["in_result"], "response",
            sides=("r", "l"),
            via=[(1080, 228), (1080, 620), (100, 620), (100, 500)], ly=-10)

    d.icon(150, 332, "clock", accent=True, r=14)
    d.note(178, 338, "B is paused here — the walk of shame", ANNOTATION, 16,
           anchor="start")
    caveat(d, "use it when the data cannot be replicated. Otherwise you have just "
              "coupled B's availability to A's, which is the thing Day 1 spent a "
              "day undoing.", y=674)
    return d


@figure("flow-lookup-build")
def lookup_build():
    """*Where Do Lookups Live?*, third of three: Build Lookup.

    The pair to the figure above, and the red is deliberately on the **absence of a
    pause**: B reads a table that is already there, so there is nothing to draw
    waiting for. Same convention as run 1's two *no such thing* figures.

    **The read does not arrive on a port.** It is not a packet -- it is B reading a
    local table -- so it enters the top of the node rather than an in-port, and the
    note says as much. Routing it into an in-port would have made it the long way
    round again, which is the very thing this figure is contrasting with."""
    d = Diagram("FBP — the Build Lookup Node", w=1160, h=600)
    idea(d, "a node whose whole job is keeping a local copy current, so nobody has "
            "to walk — that is the Catalogue Maker")

    a = d.node(140, 128, 190, 112, "A", ins=("in",), outs=("out",))
    bl = d.node(430, 128, 230, 112, "Build Lookup", ins=("in",), outs=("out",))
    tbl = d.cylinder(800, 132, 200, 104, "lookup table")
    b = d.node(430, 380, 230, 112, "B", ins=("in",), outs=("out",))

    d.arrow(pkt_on(d, 40, a["ports"]["in0"]), a["ports"]["in0"], sides=("r", "l"))
    d.arrow(a["ports"]["out0"], bl["ports"]["in0"], sides=("r", "l"))
    d.arrow(bl["ports"]["out0"], tbl, sides=("r", "l"))
    d.arrow(pkt_on(d, 250, b["ports"]["in0"]), b["ports"]["in0"], sides=("r", "l"))
    d.arrow(b["ports"]["out0"], pkt_on(d, 760, b["ports"]["out0"]), sides=("r", "l"))

    d.arrow(tbl, b, "read locally — no pause", accent=True, sides=("b", "t"),
            via=[(900, 320), (545, 320)], ly=-8)

    d.note(235, 282, "A publishes what it\nknows, as it changes", COMMENT, 15)
    d.note(545, 282, "listens to A, and keeps\nthe table current", COMMENT, 15)
    # above the cylinder, not below it: the read leaves the cylinder's bottom centre
    # and any note under it is on the line
    d.note(900, 104, "the copy, held where B needs it", COMMENT, 15)
    d.note(545, 540, "not a packet on a port — a table B reads, so nothing waits",
           COMMENT, 15)
    caveat(d, "in advance rather than on demand: no temporal coupling, and the copy "
              "is behind by one broker hop — which is the trade you are making",
           y=578)
    return d


@figure("flow-nodes-as-processes")
def nodes_as_processes():
    """*When It Fails, and What the Arcs Really Are*, second beat -- the hinge of the
    whole section. Nothing new is drawn: the arcs become middleware and the nodes
    become processes, and the graph is otherwise the graph they already have."""
    d = Diagram("Nodes as Processes over Middleware", w=1280, h=520)
    idea(d, "an arc that survives a crash is a queue; a node that survives a crash "
            "is a service")

    # the pipe starts clear of the process boundary: at 40 units its mouth ellipse
    # sat on the dashed border and swallowed the out-port's label
    xs = (110, 560, 1010)
    names = ("Take Order", "Take Payment", "Place Order")
    nodes = []
    for x, name in zip(xs, names):
        # 46 units of left padding, not 26: an in-port's label is set to the left of
        # its dot and was sitting on the process boundary
        d.group(x - 46, 168, 256, 176, "process")
        nodes.append(d.node(x, 202, 184, 116, name, ins=("in",), outs=("out",)))

    for lhs, rhs in zip(nodes, nodes[1:]):
        pipe = d.pipe(lhs["ports"]["out0"]["x"] + 66, 228, 140, 62, accent=True)
        d.packet(pipe["x"] + 30, 246, w=30, h=26)
        d.packet(pipe["x"] + 80, 246, w=30, h=26)
        d.arrow(lhs["ports"]["out0"], pipe, sides=("r", "l"))
        d.arrow(pipe, rhs["ports"]["in0"], sides=("r", "l"))

    d.note(640, 386, "message-oriented middleware", ANNOTATION, 16)
    d.note(640, 424, "the connector was always external — the component only ever "
                     "knew a port name,\nso making it a broker changes nothing "
                     "inside the component", COMMENT, 15)
    caveat(d, "everything the room drew on paper this morning, and as a graph an "
              "hour ago, is the thing Day 1 spent a day building")
    return d


# ---- Movement D: the name ---------------------------------------------------

@figure("flow-message-passing")
def message_passing():
    """*Message Passing.* The red is the **mailbox**: without something in the
    middle that holds the message, "both parties need not be simultaneously present"
    is just a claim. The pigeonhole frame from movement A is the callback."""
    d = Diagram("Message Passing", w=1200, h=500)
    idea(d, "both parties need not be present at the same time — because something "
            "in the middle holds the message")

    a = d.node(90, 172, 210, 128, "sender", ins=("in",), outs=("out",))
    b = d.node(890, 172, 210, 128, "receiver", ins=("in",), outs=("out",))
    box = d.pipe(430, 204, 320, 64, accent=True)
    for i in range(3):
        d.packet(480 + i * 72, 223, w=30, h=26)
    d.arrow(a["ports"]["out0"], box, sides=("r", "l"))
    d.arrow(box, b["ports"]["in0"], sides=("r", "l"))

    d.note(590, 176, "a mailbox", ANNOTATION, 16)
    d.note(195, 336, "sends, and carries on —\nit does not wait", COMMENT, 15)
    d.note(995, 347, "collects when it is\nready, not when the\nsender was", COMMENT, 15)
    d.note(590, 340, "mail is delivered to a mailbox of some form,\n"
                     "for later retrieval — the frame, from this morning", COMMENT, 15)
    caveat(d, "an asynchronous method of communication: the invoker sends, and "
              "relies on the receiver to select and run the code that answers it")
    return d


@figure("flow-command-event-ports")
def command_event_ports():
    """*Microservices Are Reactive Architectures.* Three ports, and the red is on
    **out-result**, because that is the asymmetry: what comes in may be an
    instruction, what goes out is only ever a fact somebody else may react to."""
    d = Diagram("Commands In, Events Out", w=1220, h=520)
    idea(d, "a component's inputs are commands and events; its outputs are events — "
            "and nobody is waiting on them")

    n = d.node(470, 196, 280, 190, "Take Payment",
               ins=("in-request",), outs=("out-request", "out-result"),
               accent_ports=("out-result",))

    d.arrow(pkt_on(d, 190, n["ports"]["in-request"]), n["ports"]["in-request"],
            sides=("r", "l"))
    d.arrow(n["ports"]["out-request"],
            pkt_on(d, 970, n["ports"]["out-request"]), sides=("r", "l"))
    p = pkt_on(d, 970, n["ports"]["out-result"], accent=True)
    d.arrow(n["ports"]["out-result"], p, sides=("r", "l"), accent=True)

    d.note(210, 342, "a command: something\nI am being told to do", INK, 15)
    d.note(985, 208, "a request to somebody else —\nstill nobody is called", COMMENT,
           15, anchor="start")
    d.note(985, 382, "a fact: something I know,\nfor whoever cares", ANNOTATION, 15,
           anchor="start")
    d.note(610, 436, "separate the data from the behaviour, act on what is on the "
                     "queue,\nand send what happened", COMMENT, 15)
    caveat(d, "that is a node with ports. That is a desk with trays. Nobody holds "
              "the whole process, and there is no gateway `main`.")
    return d


@figure("flow-partition-checkout")
def partition_checkout():
    """*Partitioning and Dataflow.* The direct answer to *Feature Envy*, and the red
    is deliberately the **empty space where the gateway was** -- that figure reds a
    gateway, this one reds its absence, and the two are meant to be recognised as the
    same drawing with the coordinator removed."""
    d = Diagram("Partitioning and Dataflow", w=1280, h=510)
    idea(d, "divide by verb, not by noun — Checkout and Take Payment are things "
            "the business does, not things it stores")

    a = d.node(320, 260, 240, 132, "Checkout", ins=("in",), outs=("out",))
    b = d.node(880, 260, 240, 132, "Take Payment", ins=("in",), outs=("out",))

    p0 = pkt_on(d, 120, a["ports"]["in0"])
    p1 = pkt_on(d, 690, a["ports"]["out0"])
    p2 = pkt_on(d, 1180, b["ports"]["out0"])
    d.arrow(p0, a["ports"]["in0"], sides=("r", "l"))
    d.arrow(a["ports"]["out0"], p1, sides=("r", "l"))
    d.arrow(p1, b["ports"]["in0"], sides=("r", "l"))
    d.arrow(b["ports"]["out0"], p2, sides=("r", "l"))

    # the packet names sit a row above the port labels, not level with them: at 17pt
    # bold the last "out" runs straight into "payment due"
    d.note(135, 282, "purchase", INK, 15, anchor="middle")
    d.note(705, 282, "priced", INK, 15, anchor="middle")
    d.note(1195, 282, "payment due", INK, 15, anchor="middle")

    d.group(320, 128, 800, 60, "", dashed=True, accent=True)
    d.note(720, 160, "no gateway. no `main`. nothing here is in charge.",
           ANNOTATION, 17)

    d.note(620, 442, "entity services divide by noun — Cart, Payment, Order — and "
                     "then the verbs have\nnowhere to live but the gateway. Every "
                     "desk in the paper office was a verb.", COMMENT, 15)
    return d


@figure("flow-bulkhead")
def bulkhead():
    """*Bulkheads.* The red is the **waiting work**, not the fault: an outage that
    becomes a delay is the claim, and the packets stacked on the arc are what makes
    it a delay. The cross stays in ink so it does not compete."""
    d = Diagram("Bulkheads", w=1220, h=540)
    idea(d, "the outage became a delay, not a failure — the work simply waits")

    a = d.node(90, 220, 220, 132, "Checkout", ins=("in",), outs=("out",))
    # the name sits above the hexagon, not in it: a full-size cross over a labelled
    # component strikes through its own label
    b = d.node(900, 220, 220, 132, "", ins=("in",), outs=("out",))
    d.note(1010, 202, "Take Payment", INK, 17)

    pipe = d.pipe(430, 254, 380, 64, accent=True)
    for i in range(4):
        d.packet(462 + i * 84, 273, w=30, h=26, accent=True)
    d.arrow(a["ports"]["out0"], pipe, sides=("r", "l"))
    d.arrow(pipe, b["ports"]["in0"], sides=("r", "l"))
    d.icon(1010, 286, "cross", r=44)

    d.note(620, 226, "the work queues up", ANNOTATION, 16)
    d.note(195, 396, "sends, and returns\nimmediately — whether or\n"
                     "not the receiver is up", COMMENT, 15)
    d.note(1010, 396, "down, and nothing\nupstream knows", COMMENT, 15)
    d.note(620, 400, "the failure is contained in one compartment: a bulkhead.\n"
                     "In a synchronous conversation it would have propagated back "
                     "up the chain.", COMMENT, 15)
    caveat(d, "availabilities multiply only under temporal coupling — "
              "store-and-forward breaks the chain")
    return d


@figure("flow-backpressure")
def backpressure():
    """*When the Pipe Fills*, first of the pair. Red is on the **signal going back
    up the chain** -- the only thing on the slide that is not already on *Capacity,
    Backpressure and Node Lifetime*, and the thing load-shedding does instead."""
    d = Diagram("Backpressure", w=1220, h=560)
    idea(d, "the producer feels the pipe pushing back, and slows down — "
            "you pay in latency, and lose nothing")

    a = d.node(90, 190, 210, 132, "producer", ins=("in",), outs=("out",))
    b = d.node(910, 190, 210, 132, "consumer", ins=("in",), outs=("out",))
    pipe = d.pipe(420, 224, 380, 64)
    for i in range(4):
        d.packet(452 + i * 84, 243, w=30, h=26)
    d.arrow(a["ports"]["out0"], pipe, sides=("r", "l"))
    d.arrow(pipe, b["ports"]["in0"], sides=("r", "l"))

    d.arrow(b, a, "slow down", accent=True, sides=("b", "b"),
            via=[(1015, 404), (195, 404)], ly=26)
    d.note(610, 196, "full", INK, 15)

    d.note(195, 470, "push — the middleware calls\nus as messages arrive",
           INK, 15)
    d.note(1015, 470, "pull — we poll, so we\ncontrol the rate", INK, 15)
    d.note(610, 470, "blocking retry creates it as a side effect: retrying a\n"
                     "connection slows consumption, which fills the queue",
           COMMENT, 15)
    caveat(d, "choose it when data loss is unacceptable and the extra latency is "
              "tolerable")
    return d


@figure("flow-load-shedding")
def load_shedding():
    """*When the Pipe Fills*, second of the pair, and the contrast is carried by
    red: backpressure reds a signal travelling **back**, this reds packets leaving
    the drawing altogether. Same geometry either side, so the difference is the only
    thing that moves."""
    d = Diagram("Load-Shedding", w=1220, h=560)
    idea(d, "or discard, and keep up — you pay in data, and lose nothing else")

    a = d.node(90, 190, 210, 132, "producer", ins=("in",), outs=("out",))
    b = d.node(910, 190, 210, 132, "consumer", ins=("in",), outs=("out",))
    pipe = d.pipe(420, 224, 380, 64)
    for i in range(2):
        d.packet(452 + i * 84, 243, w=30, h=26)
    d.arrow(a["ports"]["out0"], pipe, sides=("r", "l"))
    d.arrow(pipe, b["ports"]["in0"], sides=("r", "l"))

    for i in range(2):
        x = 620 + i * 84
        d.packet(x, 372, w=30, h=26, accent=True)
        d.arrow((x + 15, 300), (x + 15, 364), accent=True)
        d.icon(x + 15, 424, "cross", accent=True, r=13)
    d.note(830, 400, "dropped, on purpose", ANNOTATION, 16, anchor="start")

    d.note(195, 470, "still sending at full rate —\nnobody asked it to stop",
           COMMENT, 15)
    d.note(1015, 470, "keeps up, on a sample\nof the traffic", COMMENT, 15)
    d.note(560, 488, "and it can discriminate: prioritise,\nand throw away only "
                     "the cheap data", COMMENT, 15)
    caveat(d, "choose it when volume is high and a sample will do — a thousand "
              "metrics a second when ten meets the SLA")
    return d


@figure("flow-circuit-breaker")
def circuit_breaker():
    """*Putting Reactive Together*, first of three. The distinction worth drawing is
    that a circuit breaker answers a downstream that is **failing** rather than slow,
    so the red is on the consumer's own decision to stop reading -- not on the fault.

    **Queue, consumer, downstream, in that order left to right.** The first pass put
    the consumer on the left with its work to the right of it, which had the feed
    arrow running backwards through the consumer's own label and the outbound call
    crossing the queue."""
    d = Diagram("Circuit Breaker", w=1240, h=470)
    idea(d, "stop consuming, so you stop hammering something that is already down — "
            "and let one through now and then to see")

    pipe = d.pipe(100, 230, 290, 64)
    for i in range(3):
        d.packet(140 + i * 76, 249, w=30, h=26)
    cons = d.node(520, 196, 230, 132, "consumer", ins=("in",), outs=("out",),
                  accent_ports=("in",))
    prov = d.node(950, 196, 230, 132, "", ins=("in",), outs=("out",))
    d.note(1065, 178, "payment provider", INK, 17)
    d.icon(1065, 262, "cross", r=42)

    d.arrow(pipe, cons["ports"]["in0"], sides=("r", "l"), accent=True)
    d.arrow(cons["ports"]["out0"], prov["ports"]["in0"], sides=("r", "l"))
    d.icon(455, 214, "lock", accent=True, r=15)
    d.note(455, 364, "open — we have stopped\nreading altogether", ANNOTATION, 15)
    d.icon(850, 214, "clock", r=14)
    d.note(850, 322, "one trial call, every\nso often", COMMENT, 15)

    d.note(245, 196, "the work waits, as it did on the bulkhead", COMMENT, 15)
    caveat(d, "the bulkhead answers a downstream that is down; the circuit breaker "
              "answers one that is down and being retried into the ground")
    return d


@figure("flow-scale-out")
def scale_out():
    """*Putting Reactive Together*, second of three. Red is on the **added worker**:
    scaling out is one more identical instance and nothing else, and that is what
    makes elasticity a property of the shape rather than a feature you build."""
    d = Diagram("Scale Out, Not Up", w=1300, h=580)
    idea(d, "elasticity is one more identical worker on the same in-port — "
            "which is competing consumers, from Day 1")

    sup = d.node(110, 240, 220, 132, "Supervisor", ins=("in",), outs=("out",))
    d.arrow(pkt_on(d, 30, sup["ports"]["in0"]), sup["ports"]["in0"],
            sides=("r", "l"))

    for y, accent in ((172, False), (400, True)):
        w = d.node(660, y, 220, 128, "Worker", ins=("in",), outs=("out",),
                   accent=accent)
        d.arrow(sup["ports"]["out0"], w["ports"]["in0"], sides=("r", "l"),
                via=[(500, 306), (500, y + 64)])
        d.arrow(w["ports"]["out0"], pkt_on(d, 950, w["ports"]["out0"]),
                sides=("r", "l"))

    # anchored start, clear of the out packet: centred here they sat on top of it
    d.note(1010, 230, "identical: same code,\nsame in-port name", COMMENT, 15,
           anchor="start")
    d.note(1010, 452, "add one, and throughput goes up.\nNothing else changes.",
           ANNOTATION, 15, anchor="start")
    d.note(220, 428, "fans work out — it does\nnot know how many\nworkers there are",
           COMMENT, 15)
    caveat(d, "scale out, not up: twelve-factor, and the same competing consumers "
              "the queue gave you yesterday")
    return d


@figure("flow-scale-out-fault")
def scale_out_fault():
    """*Putting Reactive Together*, third of three -- the same drawing with a fault
    in it, so the pair reads as one figure and its consequence. Red is the **fault
    region**: the point is what does *not* happen to the other worker.

    The failed worker's name sits above its hexagon rather than inside it, for the
    same reason as the bulkhead's -- a full-size cross strikes through its own
    label."""
    d = Diagram("Scale Out — and a Fault", w=1300, h=650)
    idea(d, "one worker fails and the others do not notice — that is what resilient "
            "and elastic look like on the same drawing")

    sup = d.node(110, 240, 220, 132, "Supervisor", ins=("in",), outs=("out",))
    d.arrow(pkt_on(d, 30, sup["ports"]["in0"]), sup["ports"]["in0"],
            sides=("r", "l"))

    d.group(608, 372, 336, 190, "fault", accent=True)
    for y, dead in ((172, False), (416, True)):
        w = d.node(660, y, 220, 128, "" if dead else "Worker",
                   ins=("in",), outs=("out",))
        d.arrow(sup["ports"]["out0"], w["ports"]["in0"], sides=("r", "l"),
                via=[(500, 306), (500, y + 64)])
        if dead:
            d.note(770, 398, "Worker", INK, 17)
            d.icon(770, y + 64, "cross", accent=True, r=40)
        else:
            d.arrow(w["ports"]["out0"], pkt_on(d, 950, w["ports"]["out0"]),
                    sides=("r", "l"))

    d.note(1010, 230, "still working, still delivering", COMMENT, 15, anchor="start")
    d.note(980, 480, "its work goes back on the\nqueue and another worker\ntakes it",
           COMMENT, 15, anchor="start")
    d.note(220, 425, "the Supervisor replaces it —\nit was never holding\n"
                     "anything the worker knew", COMMENT, 15)
    caveat(d, "resilient and elastic are not aspirations. They are message passing, "
              "backpressure, a circuit breaker and this.", y=616)
    return d


def main(argv):
    if "--list" in argv:
        for n in FIGURES:
            print(n)
        return 0
    only = [a for a in argv if not a.startswith("--")]
    for name, fn in FIGURES.items():
        if only and name not in only:
            continue
        dg = fn()
        _, png = dg.save(os.path.join(OUT, name))
        print(f"  {name:<28} {dg.w}x{dg.h}  {os.path.getsize(png):>8,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
