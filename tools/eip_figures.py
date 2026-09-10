#!/usr/bin/env python3
"""The 12 EIP figures that replace the Hohpe & Woolf images in outlines/DayOne.md.

One script for the whole set, so the figures stay a family: same canvas widths, same
label voice, same convention for what red means. Regenerate all of them with

    python3 tools/eip_figures.py            # -> resources/eip-*.drawio + .png
    python3 tools/eip_figures.py --list     # names only

Conventions held across the set, from styles.md:
  * carbon arrows carry flow, ink carries structure, and RED MARKS ONE IDEA per figure
  * every figure states its idea in a red note -- the sentence the presenter says out loud
  * a muted note names the pattern element where the name is the thing being taught
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagram import Diagram, ANNOTATION, COMMENT, MUTED, INK, CARBON      # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources")

FIGURES = {}


def figure(name):
    def wrap(fn):
        FIGURES[name] = fn
        return fn
    return wrap


# ---- the section opener ------------------------------------------------------

@figure("eip-the-big-picture")
def the_big_picture():
    """§4's opener, *The Big Picture* -- the map the other twelve figures hang off.

    **It is a composition over this family's vocabulary, not new vocabulary.** Domain
    code, a messaging gateway, a channel, an endpoint with a pump: every one of those
    is drawn somewhere in the twelve, and this figure's whole job is to put them on one
    line so the room can see where each of the day's questions lands. Nothing here may
    invent a shape the rest of the section does not use.

    **It carries §4's build order, because the slide has nothing else on it.** The body
    is one sentence -- *a map of the messaging patterns we will cover across the day* --
    and the section's own `#note` says the ordering is the point: what is the unit, how
    do I send and receive one, how do I keep receiving, how do I stop losing them, what
    kind of broker am I on. So the itinerary is drawn, as a list rather than as a strip
    of columns: **five columns of 18pt text do not fit in 890 units.** Text does not
    scale when `compact` runs, so a five-column strip leaves 178 units a column and the
    shortest of these questions is wider than that. A list is not a compromise here, it
    is the only shape that fits the floor.

    **The message is opened up, because §4.1's own slide has no picture at all.**
    *Message Construction* is body text and a presenter note, so header-and-body is
    introduced here or nowhere.

    The marker this replaces also named a *channel adapter*. It is not drawn: the deck
    never teaches the pattern, and a shape on the map that no later slide picks up is a
    promise the section does not keep.
    """
    d = Diagram("The Big Picture", w=1440, h=700)
    d.note(720, 46, "every pattern today hangs off this one line", ANNOTATION, 21)

    d.group(40, 140, 440, 190, "the sending application")
    dom1 = d.box(68, 190, 175, 100, "Domain\ncode")
    gw = d.box(277, 190, 175, 100, "Messaging\nGateway")
    pipe = d.pipe(570, 216, 300, 76)
    msg = d.msg(700, 238, w=40, h=32)
    d.group(960, 140, 440, 190, "the receiving application")
    ep = d.box(988, 190, 175, 100, "Endpoint\n+ pump")
    dom2 = d.box(1197, 190, 175, 100, "Domain\ncode")

    d.arrow(dom1, gw, sides=("r", "l"))
    d.arrow(gw, pipe, sides=("r", "l"))
    d.arrow(pipe, ep, sides=("r", "l"))
    d.arrow(ep, dom2, sides=("r", "l"))
    d.note(720, 186, "a channel", INK, 18)

    # the unit, opened up. Tied to the envelope it magnifies rather than floated near
    # it, because a blow-up that is not joined to its original is just a second message
    header = d.box(150, 440, 220, 52, "header")
    d.box(150, 492, 220, 74, "body")
    # down the outside and in from the left, not straight down onto the box: a riser
    # landing on the header's top edge runs through the caption that names it, and a
    # tie is one of the things `lint_figures.py` cannot measure a note against
    d.attach(msg, header, sides=("b", "l"),
             via=[(720, 380), (100, 380), (100, 466)])
    d.note(260, 420, "a message", INK, 18)

    d.note(620, 436, "and this is the order we meet it in", COMMENT, 18,
           anchor="start")
    for i, (num, q) in enumerate((
            ("4.1", "what is a message?"),
            ("4.2", "how do I send one, and receive one?"),
            ("4.3", "how do I keep receiving?"),
            ("4.4", "how do I stop losing them?"),
            ("4.5", "what kind of broker am I on?"))):
        y = 486 + i * 36
        d.note(620, y, num, INK, 18, anchor="start")
        d.note(700, y, q, COMMENT, 18, anchor="start")

    # compacted here rather than in `figure()`: the other twelve are 460-600 units wide
    # and already read at 27-35 real points, so this is the one figure in the family
    # that needs it. 890 is where the 18pt diagram floor meets the 18pt body floor.
    return d.compact(890)


# ---- 4.2 Channels and endpoints ---------------------------------------------

@figure("eip-point-to-point")
def point_to_point():
    """Sender, channel, one receiver. The idea is exclusivity, not topology."""
    d = Diagram("Point-to-Point Channel", w=460, h=220)
    snd = d.box(24, 84, 108, 58, "Sender")
    pipe = d.pipe(180, 96, 108, 32)
    for i in range(3):
        d.msg(196 + i * 30, 105, w=20, h=14)
    rcv = d.box(332, 84, 108, 58, "Receiver")
    d.arrow(snd, pipe, sides=("r", "l"))
    d.arrow(pipe, rcv, sides=("r", "l"))
    d.note(234, 68, "each message goes to exactly one receiver", ANNOTATION, 17)
    d.note(234, 160, "point-to-point channel", INK, 14)
    d.note(234, 196, "add receivers and they still do not need to coordinate", COMMENT, 14)
    return d


@figure("eip-publish-subscribe")
def publish_subscribe():
    """One input channel, an output channel per subscriber, a copy on each."""
    d = Diagram("Publish-Subscribe Channel", w=470, h=300)
    pub = d.box(20, 126, 104, 58, "Publisher")
    inp = d.pipe(158, 140, 76, 30)
    d.msg(184, 148, w=20, h=14)
    d.arrow(pub, inp, sides=("r", "l"))
    subs, outs = [], []
    for i, y in enumerate((40, 126, 212)):
        out = d.pipe(276, y + 14, 60, 26)
        d.msg(294, y + 20, w=18, h=13, accent=True)
        sub = d.box(360, y, 96, 54, f"Subscriber {i + 1}")
        outs.append(out)
        subs.append(sub)
        d.arrow(inp, out, sides=("r", "l"))
        d.arrow(out, sub, sides=("r", "l"))
    d.note(196, 118, "one input", INK, 14)
    d.note(306, 288, "an output channel per subscriber", INK, 14)
    d.note(300, 22, "a copy for every subscriber", ANNOTATION, 17)
    return d


@figure("eip-datatype-channel")
def datatype_channel():
    """A channel per schema -- so the channel is what tells you the type."""
    d = Diagram("Datatype Channel", w=470, h=290)
    snd = d.box(20, 110, 104, 58, "Sender")
    rcv = d.box(352, 110, 100, 58, "Receiver")
    for y, label in ((54, "Query"), (126, "Price Quote"), (198, "Purchase Order")):
        pipe = d.pipe(182, y, 108, 26)
        d.msg(206, y + 6, w=18, h=13)
        d.arrow(snd, pipe, sides=("r", "l"))
        d.arrow(pipe, rcv, sides=("r", "l"))
        d.note(236, y + 44, label, COMMENT, 15)
    d.note(236, 30, "one schema per channel", ANNOTATION, 17)
    d.note(236, 272, "so the consumer never has to inspect a message to know how to read it",
           COMMENT, 14)
    return d


@figure("eip-message-endpoint")
def message_endpoint():
    """The seam between application code and the messaging system."""
    d = Diagram("Message Endpoint", w=470, h=266)
    d.group(20, 74, 168, 112, "your application")
    app = d.box(36, 108, 136, 54, "Domain\ncode")
    end = d.box(220, 108, 116, 54, "Message\nEndpoint", accent=True)
    pipe = d.pipe(370, 122, 84, 26)
    d.arrow(app, end, sides=("r", "l"))
    d.arrow(end, pipe, sides=("r", "l"))
    d.note(412, 166, "channel", INK, 14)
    d.note(235, 42, "the endpoint is where the application\n"
                    "interoperates with others via messaging", ANNOTATION, 17)
    d.note(278, 226, "it makes the message and sends it -- and on the way back,\n"
                     "takes the contents out and hands them over", COMMENT, 14)
    return d


@figure("eip-messaging-gateway")
def messaging_gateway():
    """The gateway sits inside the endpoint; only it knows the broker."""
    d = Diagram("Messaging Gateway", w=490, h=250)
    app = d.box(18, 106, 96, 56, "Domain\ncode")
    d.group(142, 76, 226, 116, "message endpoint")
    pump = d.box(156, 108, 92, 52, "Pump\n+ Mapper")
    gw = d.box(266, 108, 88, 52, "Messaging\nGateway", accent=True)
    mw = d.box(398, 106, 76, 56, "Broker")
    d.arrow(app, pump, sides=("r", "l"))
    d.arrow(pump, gw, sides=("r", "l"))
    d.arrow(gw, mw, sides=("r", "l"))
    d.note(244, 38, "the only component that knows which broker this is",
           ANNOTATION, 17)
    d.note(244, 226, "swap the broker and nothing to the left of the gateway changes",
           COMMENT, 14)
    return d


# ---- 4.3 The message pump ----------------------------------------------------

# ---- 4.3 The message pump ----------------------------------------------------
#
# **These two share a spine on purpose.** Both draw Get -> Translate -> Dispatch ->
# Handle at the same four x positions, and they differ only in what hangs off it and
# what is red -- the failure routes on one, the two registries on the other. Ian, on
# the 2025 deck's slides 58 and 59: *"this was once visual, I think that works better
# than the text… it works better separate from #41 but needs to be visual."* Separate,
# and recognisably the same drawing twice, is what makes the second one cheap to read.

_PUMP_X = (50, 260, 470, 680)          # the four stages, shared by both figures
_PUMP_W = 150


def _pump_row(d, y, h=70):
    """The four stages and the arrows between them. Returns them in order."""
    names = ("Get\nMessage", "Translate\nMessage", "Dispatch\nMessage",
             "Handle\nMessage")
    boxes = [d.box(x, y, _PUMP_W, h, n) for x, n in zip(_PUMP_X, names)]
    for a, b in zip(boxes, boxes[1:]):
        d.arrow(a, b, sides=("r", "l"))
    return boxes


@figure("eip-message-pump")
def message_pump():
    """§4.3's opener. Four stages, and each one fails in its own way.

    **Red is the four failure routes, not the loop.** The loop is what makes it a
    pump and it is drawn, but the slide's whole second half is the error routing, and
    a room that takes only the red away should take *every stage has somewhere to put
    what it cannot do*. The happy path is carbon, which is this family's convention.

    **The failure descriptions are notes, not arrow labels.** An arrow label on a
    vertical run is centred **on** the stroke -- `lint_figures.py` has a check for
    exactly that -- and four of them would each need nudging into a neighbour. Set as
    two-line notes in the gaps between the risers, they sit where there is room.

    Dispatch and Handle both end at the Error Log in the original, but drawing the
    second route needs a second anchor on Handle's bottom edge and there is only one.
    So Handle draws the **recoverable** case, which is the one with a mechanism, and
    an ink note under the Error Log carries the other. Faithful, and four arrows.
    """
    d = Diagram("The Message Pump", w=890, h=400)
    d.note(445, 26, "every stage has somewhere to put what it cannot do",
           ANNOTATION, 21)

    get, trn, dsp, hnd = _pump_row(d, 96)
    d.arrow(hnd, get, "until cancelled", sides=("t", "t"),
            via=[(755, 66), (125, 66)], ly=-4)

    dlq = d.box(16, 286, 168, 70, "Dead Letter\nChannel")
    inv = d.box(216, 286, 188, 70, "Invalid Message\nChannel")
    log = d.box(452, 286, 150, 70, "Error Log")
    rq = d.box(664, 286, 182, 70, "Requeue,\nto a limit")

    for src, dst in ((get, dlq), (trn, inv), (dsp, log), (hnd, rq)):
        d.arrow(src, dst, accent=True, sides=("b", "t"))

    d.note(180, 210, "failure to\ndeliver", ANNOTATION, 14)
    d.note(390, 210, "failure to\nunderstand", ANNOTATION, 14)
    d.note(600, 210, "failure to\ndispatch", ANNOTATION, 14)
    d.note(812, 210, "the handler\nthrew", ANNOTATION, 14)

    d.note(527, 378, "unrecoverable handler errors too", COMMENT, 14)
    return d


@figure("eip-translate-and-dispatch")
def translate_and_dispatch():
    """The same spine, with the two registries that drive its middle two stages.

    **Red is the Message Mapper Registry alone.** The presenter note calls the mapper
    the seam the exercises are checked against -- *if a handler's signature has a
    broker type in it, the mapper has not finished its job* -- and the Handler Registry
    is the ordinary half of the pair. Reddening both would say they are the same kind
    of thing, and the section spends its time on one of them.
    """
    d = Diagram("Translate and Dispatch", w=890, h=340)
    d.note(445, 26, "no broker type reaches your handler -- the mapper is the seam",
           ANNOTATION, 21)

    _, trn, dsp, _ = _pump_row(d, 82)

    mapper = d.box(196, 212, 228, 74, "Message Mapper\nRegistry", accent=True)
    handler = d.box(468, 212, 196, 74, "Handler\nRegistry")
    d.arrow(trn, mapper, accent=True, sides=("b", "t"))
    d.arrow(dsp, handler, sides=("b", "t"))

    # **No arrow labels here.** "look up the mapper" and "look up the handler" say
    # what the box each arrow points at already says, and the only room for the second
    # one put it under *Handle Message*, where it read as labelling the wrong box. The
    # slide's own new fact goes in their place instead: the handler is yours.
    d.note(755, 190, "your code", INK, 14)
    d.note(445, 320, "the domain never sees a message format, and the messaging "
                     "code never sees a domain type", COMMENT, 14)
    return d


@figure("eip-polling-consumer")
def polling_consumer():
    """The consumer asks. Red is on the asking."""
    d = Diagram("Polling Consumer", w=580, h=250)
    pipe = d.pipe(34, 112, 118, 30)
    d.msg(64, 120, w=20, h=14)
    pump = d.box(412, 100, 128, 56, "Message\nPump")
    d.arrow(pump, pipe, "receive()", accent=True,
            via=[(476, 58), (93, 58)], sides=("t", "t"))
    d.arrow(pipe, pump, "a message, or nothing", sides=("r", "l"), ly=-2)
    d.note(93, 168, "channel", INK, 14)
    d.note(290, 216, "holds a thread even when the channel is empty --\n"
                     "but needs no connection held open", COMMENT, 14)
    d.note(290, 26, "the consumer asks", ANNOTATION, 17)
    return d


@figure("eip-event-driven-consumer")
def event_driven_consumer():
    """The broker calls. Red is on the call -- the mirror of Polling Consumer."""
    d = Diagram("Event-Driven Consumer", w=580, h=250)
    pipe = d.pipe(34, 112, 118, 30)
    d.msg(64, 120, w=20, h=14)
    pump = d.box(412, 100, 128, 56, "Message\nPump")
    d.arrow(pump, pipe, "register callback", dashed=True, muted=True,
            via=[(476, 58), (93, 58)], sides=("t", "t"))
    d.arrow(pipe, pump, "on message", accent=True, sides=("r", "l"), ly=-2)
    d.note(93, 168, "channel", INK, 14)
    d.note(290, 216, "no thread while idle -- but the connection stays open,\n"
                     "and the broker sets the pace", COMMENT, 14)
    d.note(290, 26, "the broker calls", ANNOTATION, 17)
    return d


@figure("eip-service-activator")
def service_activator():
    """The line between the messaging code and your code. Red IS the line."""
    d = Diagram("Service Activator", w=600, h=250)
    pipe = d.pipe(14, 112, 58, 28)
    d.group(94, 74, 236, 124, "messaging gateway -- written once")
    pump = d.box(108, 112, 96, 54, "Message\nPump")
    mapper = d.box(222, 112, 96, 54, "Message\nMapper")
    act = d.box(368, 112, 112, 54, "Service\nActivator", accent=True)
    d.group(508, 74, 84, 124, "your code")
    handler = d.box(518, 112, 66, 54, "Handler")
    d.arrow(pipe, pump, sides=("r", "l"))
    d.arrow(pump, mapper, sides=("r", "l"))
    d.arrow(mapper, act, sides=("r", "l"))
    d.arrow(act, handler, sides=("r", "l"))
    d.note(43, 158, "channel", INK, 14)
    d.note(400, 40, "the handler never learns it was a message", ANNOTATION, 17)
    d.note(300, 228, "a domain type in, a return or a throw out -- "
                     "no channel, no headers, no ack", COMMENT, 14)
    return d


@figure("eip-message-dispatcher")
def message_dispatcher():
    """Competing consumers. Red is on throughput, not on exclusivity."""
    d = Diagram("Competing Consumers", w=460, h=310)
    pipe = d.pipe(24, 134, 158, 40)
    for i in range(4):
        d.msg(44 + i * 30, 146, w=20, h=15)
    a = d.box(304, 44, 128, 56, "Consumer")
    b = d.box(304, 126, 128, 56, "Consumer")
    c = d.box(304, 208, 128, 56, "Consumer", accent=True)
    d.arrow(pipe, a, "1", sides=("r", "l"), ly=-2)
    d.arrow(pipe, b, "2", sides=("r", "l"), ly=-2)
    d.arrow(pipe, c, "3", accent=True, sides=("r", "l"), ly=-2)
    d.note(103, 208, "arriving faster than one\nconsumer can drain", COMMENT, 14)
    d.note(240, 24, "add consumers until you consume faster than they arrive",
           ANNOTATION, 17)
    d.note(240, 292, "the cost: lock-and-read-past means order is no longer preserved",
           COMMENT, 14)
    return d


# ---- 4.4 When the pump fails -------------------------------------------------

@figure("eip-invalid-message-channel")
def invalid_message_channel():
    """Delivered, not understood. The RECEIVER diverts -- that is the whole
    distinction from Dead Letter, so the divert starts at the receiver."""
    d = Diagram("Invalid Message Channel", w=470, h=300)
    snd = d.box(20, 70, 100, 54, "Sender")
    pipe = d.pipe(162, 84, 92, 26)
    d.msg(184, 90, w=18, h=13)
    rcv = d.box(306, 70, 128, 54, "Receiver")
    d.arrow(snd, pipe, sides=("r", "l"))
    d.arrow(pipe, rcv, sides=("r", "l"))
    inv = d.pipe(288, 210, 164, 28, accent=True)
    d.msg(316, 217, w=18, h=13, accent=True)
    d.arrow(rcv, inv, "cannot read it", accent=True, sides=("b", "t"), lx=-62)
    d.note(370, 264, "invalid message channel", INK, 14)
    d.note(235, 34, "it arrived -- the receiver just cannot understand it",
           ANNOTATION, 17)
    d.note(150, 188, "a well-formed message that\nmerely fails is an application\n"
                     "error, not an invalid one", COMMENT, 14)
    return d


@figure("eip-dead-letter-channel")
def dead_letter_channel():
    """Could not be delivered. The BROKER diverts, and the receiver never sees it."""
    d = Diagram("Dead Letter Channel", w=470, h=300)
    snd = d.box(20, 70, 100, 54, "Sender")
    pipe = d.pipe(168, 84, 108, 26)
    d.msg(192, 90, w=18, h=13)
    rcv = d.box(330, 70, 110, 54, "Receiver")
    d.arrow(snd, pipe, sides=("r", "l"))
    d.arrow(pipe, rcv, "never arrives", dashed=True, muted=True, sides=("r", "l"), lx=-24, ly=-18)
    dlq = d.pipe(156, 210, 164, 28, accent=True)
    d.msg(184, 217, w=18, h=13, accent=True)
    # the divert runs vertically, so a centred label is struck through by its own
    # arrow -- push it clear rather than nudge it
    d.arrow(pipe, dlq, "gave up after N tries", accent=True, sides=("b", "t"), lx=-88)
    d.note(238, 264, "dead letter channel", INK, 14)
    d.note(235, 34, "the broker could not deliver it, so the broker puts it aside",
           ANNOTATION, 17)
    d.note(385, 150, "the receiver never\nsaw this one", COMMENT, 14)
    return d


# ---- 6.2 Message design ------------------------------------------------------

@figure("eip-get-on-demand")
def get_on_demand():
    """§6.2's first answer to reference data: call back for it.

    **This and `eip-ecst` contrast through red, which is why they are drawn as a
    pair** -- same canvas, same three-shape row, opposite reds. Here the red is the
    synchronous round trip on the miss path, because the callout is *"a cache miss is
    a temporal coupling you did not plan for"*; there the red is a store that is never
    called at all. A reader who takes only the red off the two pages has §6.2's
    recommendation.

    The hit path is carbon and the miss path is red **on one drawing**, because the
    slide's argument is that the two paths trade opposite ways -- availability over
    consistency on a hit, consistency over availability on a miss -- and splitting them
    would lose the fact that it is one cache.

    The reply is routed under both boxes rather than doubled up beside the request:
    two arrows between one pair of shapes put their labels on top of each other.
    """
    d = Diagram("Get It On Demand", w=580, h=310)
    d.note(290, 32, "on a miss, A is up only while B is up", ANNOTATION, 17)

    cache = d.cylinder(24, 90, 124, 62, "reference\ncache")
    a = d.box(224, 90, 124, 62, "Provider A")
    b = d.box(424, 90, 132, 62, "Provider B")

    d.arrow(a, cache, "look up", sides=("l", "r"), ly=-16)
    d.arrow(a, b, "request()", accent=True, sides=("r", "l"), ly=-16)
    d.arrow(b, a, "reply()", accent=True, sides=("b", "b"),
            via=[(490, 198), (286, 198)], ly=26)

    d.note(86, 174, "a hit is served here", INK, 14)
    d.note(290, 264, "on a hit: possibly-stale data, and you stay up\n"
                     "on a miss: the availabilities multiply again", COMMENT, 14)
    return d


@figure("eip-ecst")
def ecst():
    """§6.2's recommendation: the state arrives before anyone needs it.

    **The red is the store, and there is deliberately no arrow out of it.** A read of
    your own database is not worth drawing, and a line there would sit exactly where
    `eip-get-on-demand` has its round trip -- which is the comparison the two figures
    exist to make. The absence is the argument, so the red note carries it and the
    geometry does not.

    ⚑ **Three defects, all found by looking and none of them anything the linter
    measures.** The first draft drew that read as a loop out of the store back into
    Provider A: it arrived at the same edge as the channel's own arrow, so the two
    heads merged and the figure appeared to say the local copy fed the channel. It also
    pushed `cache write()` off the right-hand edge. And `state changed` as an ARROW
    label was centred on a 56-unit run between the pipe and the box, so it lay across
    whichever of the two it was nudged towards -- it is a note under the channel now,
    with the pattern name above it. The canvas went 520 -> 580 to give `cache write()`
    somewhere to stand that is neither on the box nor on the cylinder.
    """
    d = Diagram("Event-Carried State Transfer", w=580, h=330)
    d.note(290, 32, "every read is local -- nothing here calls anyone", ANNOTATION, 17)

    b = d.box(24, 96, 124, 62, "Provider B")
    pipe = d.pipe(192, 112, 120, 30)
    d.msg(222, 119, w=18, h=13)
    a = d.box(368, 96, 132, 62, "Provider A")
    local = d.cylinder(372, 208, 124, 56, "local copy", accent=True)

    d.arrow(b, pipe, sides=("r", "l"))
    d.arrow(pipe, a, sides=("r", "l"))
    d.arrow(a, local, "cache write()", sides=("b", "t"), lx=84, ly=14)

    d.note(252, 88, "Out-Only", INK, 14)
    d.note(252, 176, "state changed", INK, 14)
    d.note(160, 254, "stale by the age of the last event --\n"
                     "and there is no miss path to be slow on", COMMENT, 14)
    return d


@figure("eip-content-enricher")
def content_enricher():
    """The enricher moves the lookup. Red is on the lookup, because that is
    the callout: it did not go away."""
    d = Diagram("Content Enricher", w=480, h=332)
    src = d.box(16, 96, 116, 58, "Order\nAccountId")
    enr = d.box(184, 96, 116, 58, "Content\nEnricher")
    out = d.box(352, 96, 116, 58, "Order\n+ address")
    db = d.cylinder(198, 222, 90, 58, "Customer")
    d.arrow(src, enr, sides=("r", "l"))
    d.arrow(enr, out, sides=("r", "l"))
    d.arrow(enr, db, "read the address", accent=True, sides=("b", "t"), lx=64)
    d.note(242, 34, "the lookup did not go away -- it moved here", ANNOTATION, 17)
    d.note(74, 180, "incomplete", INK, 14)
    d.note(410, 180, "complete", INK, 14)
    d.note(240, 300, "and now the shipping consumer depends on the enricher too --\n"
                     "the same availability sum, one hop further away", COMMENT, 14)
    return d


# ---- The routing handout -----------------------------------------------------
#
# The eight patterns Day 1 SS4.6 Pipelines used to teach, cut by review item D1-9 and
# promised a takeaway handout instead (plan SS10). They are in this family rather than
# a family of their own because Content Enricher -- the ninth pattern of that set, and
# the one that stayed on Day 1 -- is already here: a handout drawn in a second voice
# would read as somebody else's material stapled to the pack.
#
# **The three routers contrast through red, and that is the whole sub-set.** All three
# answer one question -- *who decides where this message goes* -- and the red says who:
# Content Based Router reds the ROUTER, because the rules are in it; Dynamic Router
# reds the CONTROL CHANNEL, because the consumers put them there; Recipient List reds
# the LIST ON THE MESSAGE, because the publisher wrote it. A reader who takes only the
# red from those three pages has the distinction the prose spends 550 words on.
#
# Splitter and Aggregator pair the same way and carry the same three parts across both
# pages, so the second figure is visibly the first one run backwards.


@figure("eip-pipes-and-filters")
def pipes_and_filters():
    """The chain. Red is on composability, because that is the pattern's claim.

    **The three filters are Decrypt, Enrich and Translate rather than Hohpe's own
    Decrypt / Authenticate / De-Dup**, for two reasons. They are the three the script
    names (*encrypt/decrypt, enrich the content, transform the format*), and two of the
    three are patterns the reader meets elsewhere in the pack -- Content Enricher on
    Day 1, Message Translator on the next page of this handout -- so the chain is built
    out of things they already have names for. "Authenticate" is also the longest label
    in the set and this is the one figure in the family tight enough for that to bind.
    """
    d = Diagram("Pipes and Filters", w=940, h=290)
    src = d.box(16, 110, 104, 56, "Publisher")
    stages, pipes = [], []
    for x, label, w in ((214, "Decrypt", 100), (408, "Enrich", 100),
                        (602, "Translate", 112)):
        pipes.append(d.pipe(x - 72, 124, 50, 28))
        stages.append(d.box(x, 110, w, 56, label))
    pipes.append(d.pipe(736, 124, 50, 28))
    snk = d.box(808, 110, 104, 56, "Consumer")

    chain = [src, pipes[0], stages[0], pipes[1], stages[1],
             pipes[2], stages[2], pipes[3], snk]
    for a, b in zip(chain, chain[1:]):
        d.arrow(a, b, sides=("r", "l"))

    d.note(470, 36, "each filter reads a channel and writes a channel -- "
                    "so they chain", ANNOTATION, 17)
    # all three role names on one row: "filters" set above the middle box read as
    # naming Enrich rather than the three of them
    d.note(68, 196, "source", INK, 14)
    d.note(470, 196, "filters", INK, 14)
    d.note(860, 196, "sink", INK, 14)
    d.note(470, 248, "each pipe is a channel -- and the pipeline's throughput "
                     "is the slowest filter's", COMMENT, 14)
    return d.compact(890)


@figure("eip-message-translator")
def message_translator():
    """A filter that changes the schema and nothing else.

    Drawn on `eip-content-enricher`'s composition on purpose -- three boxes, same
    widths, same x positions. They are the two filters the reader meets as filters,
    and the enricher adds a field where the translator changes a shape; laying them
    out identically is what makes that the only difference on the page.
    """
    d = Diagram("Message Translator", w=480, h=300)
    src = d.box(16, 96, 116, 58, "Order\nv2")
    tr = d.box(184, 96, 116, 58, "Message\nTranslator")
    out = d.box(352, 96, 116, 58, "Order\nv1")
    d.arrow(src, tr, sides=("r", "l"))
    d.arrow(tr, out, sides=("r", "l"))
    d.note(242, 34, "the same message, in a schema the consumer can read",
           ANNOTATION, 17)
    d.note(74, 180, "as published", INK, 14)
    d.note(410, 180, "as consumed", INK, 14)
    d.note(240, 254, "often temporary -- retire it once the\n"
                     "consumer accepts the publisher's schema", COMMENT, 14)
    return d


@figure("eip-content-based-router")
def content_based_router():
    """Router 1 of 3. **Red is the router itself**, because the rules live in it --
    which is also why it becomes the maintenance hot-spot the caveat warns about."""
    d = Diagram("Content Based Router", w=560, h=330)
    inp = d.pipe(16, 142, 88, 28)
    d.msg(38, 149, w=20, h=14)
    rtr = d.box(148, 128, 126, 58, "Content\nBased Router", accent=True)
    d.arrow(inp, rtr, sides=("r", "l"))
    for y, label in ((64, "Widget\nInventory"), (220, "Gadget\nInventory")):
        pipe = d.pipe(318, y, 80, 26)
        d.msg(340, y + 6, w=18, h=13)
        dest = d.box(430, y - 22, 112, 54, label)
        d.arrow(rtr, pipe, sides=("r", "l"))
        d.arrow(pipe, dest, sides=("r", "l"))
    d.note(300, 26, "the router reads the message to decide where it goes",
           ANNOTATION, 17)
    d.note(62, 194, "one channel in", INK, 14)
    d.note(358, 158, "a channel per outcome", INK, 14)
    d.note(280, 300, "the router has to know every destination --\n"
                     "which is what makes it a place you keep going back to",
           COMMENT, 14)
    return d


@figure("eip-dynamic-router")
def dynamic_router():
    """Router 2 of 3. **Red is the control channel**, not the router -- the mirror of
    Content Based Router, where red was the router and the consumers were mute. The
    rules are the same rules; what moved is who wrote them."""
    d = Diagram("Dynamic Router", w=600, h=380)
    inp = d.pipe(16, 140, 84, 28)
    d.msg(38, 147, w=20, h=14)
    rtr = d.box(146, 126, 126, 58, "Dynamic\nRouter")
    d.arrow(inp, rtr, sides=("r", "l"))
    dests = []
    for y, label in ((62, "Consumer A"), (212, "Consumer B")):
        pipe = d.pipe(322, y + 14, 76, 26)
        dest = d.box(430, y, 124, 54, label)
        dests.append(dest)
        d.arrow(rtr, pipe, sides=("r", "l"))
        d.arrow(pipe, dest, sides=("r", "l"))
    # round the bottom rather than diagonally: a straight run from B's foot to the
    # router's foot passes through pipe B and its own label
    d.arrow(dests[1], rtr, "send me anything over 500", accent=True,
            via=[(492, 300), (209, 300)], sides=("b", "b"))
    d.note(300, 26, "the consumers tell the router what to send them",
           ANNOTATION, 17)
    d.note(350, 332, "a control channel", INK, 14)
    d.note(300, 364, "if two rules match the router must choose -- "
                     "last one wins, or it is really a recipient list", COMMENT, 14)
    return d


@figure("eip-recipient-list")
def recipient_list():
    """Router 3 of 3. **Red is the list on the message**, because here it is the
    publisher that decides -- neither the router's rules nor the consumers'.

    B is skipped on purpose. Three channels with all three taken is a fan-out and
    reads as publish-subscribe; the pattern only becomes visible when one of the
    channels that exists does not get a copy.
    """
    # the gap between Publisher and the list is set by the red label, not by the
    # drawing: "to: A and C" is the one idea on the page and it has to sit in clear
    # paper. 112 units of gap for an 18pt label that measures about 90
    d = Diagram("Recipient List", w=620, h=356)
    pub = d.box(16, 148, 112, 58, "Publisher")
    rl = d.box(240, 148, 130, 58, "Recipient\nList")
    d.arrow(pub, rl, "to: A and C", accent=True, sides=("r", "l"), ly=-2)
    for y, name, taken in ((54, "A", True), (140, "B", False), (226, "C", True)):
        pipe = d.pipe(410, y + 13, 76, 24)
        dest = d.box(512, y, 86, 50, name)
        d.arrow(pipe, dest, sides=("r", "l"))
        if taken:
            d.msg(430, y + 18, w=18, h=13, accent=True)
            d.arrow(rl, pipe, sides=("r", "l"))
    d.note(310, 26, "the publisher names who gets it -- like the To list on an email",
           ANNOTATION, 17)
    d.note(448, 306, "a channel per recipient", INK, 14)
    d.note(310, 340, "invert it -- let consumers register via a control channel --\n"
                     "and you have publish-subscribe on point-to-point middleware",
           COMMENT, 14)
    return d


@figure("eip-splitter")
def splitter():
    """One in, one per part out. Red is the fan-out.

    The three parts are `line 1..3` here and again on `eip-aggregator`, and the two
    figures are the same drawing reflected, so the pair reads as one movement out and
    back rather than as two unrelated pictures.
    """
    d = Diagram("Splitter", w=460, h=366)
    order = d.box(16, 134, 116, 58, "Order\n3 lines")
    spl = d.box(180, 134, 104, 58, "Splitter")
    d.arrow(order, spl, sides=("r", "l"))
    for y, label in ((60, "line 1"), (148, "line 2"), (236, "line 3")):
        pipe = d.pipe(330, y, 76, 24)
        d.msg(352, y + 5, w=20, h=14, accent=True)
        d.arrow(spl, pipe, sides=("r", "l"))
        d.note(368, y + 44, label, INK, 14)
    d.note(230, 26, "one message in, one message per part out", ANNOTATION, 17)
    d.note(230, 320, "and now you can watch the batch drain --\n"
                     "instead of waiting for all-or-nothing", COMMENT, 14)
    return d


@figure("eip-aggregator")
def aggregator():
    """`eip-splitter` run backwards, with the same three parts. Red is the **buffer**,
    not the fan-in: what an aggregator does that a plain consumer does not is wait."""
    d = Diagram("Aggregator", w=490, h=366)
    agg = d.box(166, 134, 124, 58, "Aggregator")
    # line 3 is drawn as an empty channel on purpose: "2 of 3" is the whole idea, and
    # three envelopes with a buffer saying 2 of 3 contradicts it on the page
    for y, label, arrived in ((60, "line 1", True), (148, "line 2", True),
                              (236, "line 3", False)):
        pipe = d.pipe(16, y, 76, 24)
        if arrived:
            d.msg(38, y + 5, w=20, h=14)
        d.arrow(pipe, agg, sides=("r", "l"))
        d.note(54, y + 44, label, INK, 14)
    buf = d.box(168, 232, 120, 56, "holding\n2 of 3", accent=True)
    d.attach(agg, buf, sides=("b", "t"))
    out = d.box(346, 134, 128, 58, "Order\ncomplete")
    d.arrow(agg, out, sides=("r", "l"))
    d.note(244, 26, "it holds the parts until the set is complete", ANNOTATION, 17)
    d.note(228, 326, "a correlation id says which parts belong together --\n"
                     "the count says when it has them all", COMMENT, 14)
    return d


@figure("eip-resequencer")
def resequencer():
    """Red is the buffer again, and deliberately: a Resequencer is an Aggregator that
    releases as it goes rather than at the end, so the two figures share their red.
    The numbers in the channels carry the outcome, which is why the red note is free
    to state the mechanism instead."""
    d = Diagram("Resequencer", w=560, h=340)
    # The pipes are deep enough to carry each number BELOW its own envelope. A label
    # passed to `msg` lands under the flap and the flap strikes it through -- invisible
    # in the source, and the numbers are the whole figure.
    #
    # ⚑ A pipe's mouth is an ellipse centred ON x with `rx = h/3`, so a deep pipe
    # reaches h/3 to the LEFT of the x it was given -- and `_extent` does not count it,
    # so it is cropped rather than reported. At h=60 that is 20 units, which is why
    # these start at 36 and not at the family's usual 16.
    for x0, seqn in ((36, ("3", "1", "2")), (376, ("1", "2", "3"))):
        pipe = d.pipe(x0, 112, 148, 60)
        for i, n in enumerate(seqn):
            d.msg(x0 + 12 + i * 44, 118, w=36, h=22)
            d.note(x0 + 30 + i * 44, 162, n, INK, 14)
        if x0 == 36:
            inp = pipe
        else:
            out = pipe
    seq = d.box(214, 114, 128, 58, "Resequencer")
    buf = d.box(226, 206, 104, 48, "buffer", accent=True)
    d.attach(seq, buf, sides=("b", "t"))
    d.arrow(inp, seq, sides=("r", "l"))
    d.arrow(seq, out, sides=("r", "l"))
    d.note(278, 26, "the buffer holds what arrived early, until its turn comes",
           ANNOTATION, 17)
    d.note(110, 200, "as they arrive", INK, 14)
    d.note(450, 200, "as they are needed", INK, 14)
    d.note(278, 296, "competing consumers, retries and parallel branches\n"
                     "all de-order a channel", COMMENT, 14)
    return d


def main(argv):
    if "--list" in argv:
        for name in FIGURES:
            print(name)
        return 0
    only = [a for a in argv if not a.startswith("--")]
    for name, fn in FIGURES.items():
        if only and name not in only:
            continue
        d = fn()
        drawio, png = d.save(os.path.join(OUT, name))
        print(f"  {name:<32} {d.w}x{d.h}  {os.path.getsize(png):>7,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
