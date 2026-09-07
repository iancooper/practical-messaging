#!/usr/bin/env python3
"""The four Day 1 drawings that show an *application*, not a pattern -- plan §8 class D.

    python3 tools/app_shapes.py                     # rebuild all four
    python3 tools/app_shapes.py boundary-one-service
    python3 tools/app_shapes.py --list

**Why these four are one family.** Everywhere else Day 1 draws a *pattern* -- one idea,
stripped to the two or three shapes that carry it. These four draw a **shape you could
build**: processes with private data, talking over channels. §1's pair is the premise;
§4.3's pair is the first time the deck says *this is what it looks like in your
codebase*. They share one helper, `service()`, so a process and its private store are
drawn the same way in all four -- which matters more here than in a pattern figure,
because the whole subject is what is inside a boundary and what is not.

**The boundary vocabulary is already taught, and this family must not invent a third
version of it.** Two families draw it already:

  * `coupling_grids.coupling-scale-boundary` -- a heavy ink rule *across* Myers' scale,
    with Content and Common struck out above it.
  * `integration_styles._frame()` -- a dashed container per process, and a **vertical
    ink rule** between them labelled *the process boundary*.

So the settled reading is **dashed box = a process, ink rule = the boundary between
two of them**, and this family uses exactly that. §1 comes *before* §3 in the deck, so
these two figures are where the room meets the glyph for the first time; §3 then reuses
it without re-teaching it.

**The §1 pair contrasts through red, the way every pair in the deck does.** The slide
has three bullets and the pair splits them:

  * **one-service** reds *reaching into private data* -- the first two bullets. The
    boundary is what stops the reach, so the cross sits **on the rule**. That is the
    same claim `coupling-scale-boundary` makes as a scale and `style-shared-database`
    makes as a counter-example.
  * **two-services** reds *the shared transaction* -- the third, and the load-bearing
    line of both days. A transaction is a scope, so it is drawn as a scope: a red
    dashed container round both stores, crossed where it meets the boundary.

Getting those the other way round would make the two figures the same picture twice.

Hand-drawn register, like the rest of Day 1.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagram import Diagram, ANNOTATION, COMMENT, MUTED, INK      # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources")
FIGURES = {}

# Every figure here is compacted to this width before it is written. The label floor is
# in canvas units and the figure is scaled to fit its slide, so a wide canvas is not
# more detail -- it is smaller type in the room. 890 is where the 18pt diagram floor
# meets the deck's 18pt body floor at full slide width.
TARGET_W = 890

# the shared stage, borrowed from `integration_styles` on purpose -- §1 and §3 argue
# about the same line and should not draw it at two different heights
MID = 500
BT = 108                          # where the boundary rule starts, under its own name


def figure(name):
    """Register a figure -- and compact it on the way out.

    **The compaction belongs here, not in `main()`.** Put it in `main()` and
    `lint_figures.py` measures the geometry as it was written rather than as it is
    rendered, and a label sitting on a stroke stays invisible for as long as the two
    disagree.
    """
    def wrap(fn):
        def build():
            return fn().compact(TARGET_W)
        build.__doc__ = fn.__doc__
        build.__name__ = fn.__name__
        FIGURES[name] = build
        return fn
    return wrap


def service(d, x, y, w, h, process, app, store=None, app_h=88, store_w=180,
            tie=True):
    """A process: a dashed container, the application inside it, and -- where the
    figure is about ownership -- the store that only it can reach.

    **The store is drawn inside the container, always.** That is the whole argument of
    §1, and a figure that puts a database outside the box it belongs to has conceded it
    before the presenter opens their mouth. It cost a first draft of `two-services`,
    where the red transaction scope was drawn as a container holding both stores --
    which is a tidy picture of the wrong claim. Returns (app, store)."""
    d.group(x, y, w, h, process)
    box = d.box(x + 30, y + 46, w - 60, app_h, app)
    cyl = None
    if store:
        cyl = d.cylinder(x + (w - store_w) / 2, y + 94 + app_h, store_w, 80, store)
        if tie:
            d.attach(box, cyl, sides=("b", "t"))
    return box, cyl


def boundary(d, bottom):
    """The vertical ink rule, named above it. `bottom` is the figure's decision, not
    the frame's: the line has to reach whatever crosses it and stop before the caption
    that names the apparatus. Nothing may be centred on MID inside its span."""
    d.note(MID, 100, "the process boundary", INK, 18)
    d.rule(MID, BT, 0, INK, 2.6, h=bottom - BT)


@figure("boundary-one-service")
def boundary_one_service():
    """§1 *Messages In, Private Data, No Shared Transaction*, first picture. One
    service, one channel in, and one thing that is refused.

    **The cross sits on the boundary rule, not on the database.** What stops the reach
    is the boundary, and that is the sentence the whole section is built on -- put the
    cross on the store and the figure says *this database is locked*, which is a
    different and much weaker claim.
    """
    d = Diagram("Messages In, Private Data", w=1000, h=520)
    d.note(MID, 44, "the only thing that crosses is a message", ANNOTATION, 21)
    boundary(d, 400)

    other, _ = service(d, 40, 124, 380, 176, "another process", "Application")
    app, orders = service(d, 580, 124, 380, 300, "the Orders service", "Application",
                          store="Orders")

    pipe = d.pipe(440, 186, 120, 56)
    d.msg(487, 200, w=26, h=20)
    d.arrow(other, pipe, sides=("r", "l"))
    d.arrow(pipe, app, sides=("r", "l"))
    # The channel is deliberately not captioned. Anything centred on MID under the
    # pipe is struck through by the rule -- the trap `_frame(bb=)` exists for in
    # `integration_styles` -- and here the rule cannot stop short, because it has to
    # reach the cross. The word "channel" arrives properly in §4.2 anyway; §1's
    # subject is the boundary, not the vocabulary.

    # the refusal. It leaves the other process, runs under both containers and is
    # stopped where it meets the line -- so the boundary is visibly what refuses it.
    d.arrow(other, orders, "read its tables", accent=True, dashed=True,
            via=[(230, 360)], sides=("b", "l"), lx=-110)
    d.icon(MID, 360, "cross", accent=True, r=17)

    d.note(MID, 452, "the data behind the boundary is private — a request describes "
                     "the work,", COMMENT, 18)
    d.note(MID, 480, "not the shape of the data inside", COMMENT, 18)
    return d


@figure("boundary-two-services")
def boundary_two_services():
    """§1's second picture, and the load-bearing line of both days: **no transaction
    spans two services.**

    A transaction is a *scope*, so it is drawn as one -- and the scope is drawn **over**
    the two services rather than instead of them, because each store has to stay inside
    the process that owns it. The first draft put both cylinders inside the red box and
    nothing else, which is a tidy picture of a claim §1 spends the previous figure
    denying.

    **Two channels, not one.** A channel is one-way -- the fact §Conversations spends a
    slide on -- and drawing it here costs nothing and saves that slide an assertion.
    Both runs are horizontal and anchored to bare points rather than to the boxes'
    midpoints: `sides=("r", "l")` puts both arrows on the same edge centre and the pair
    comes out as a bowtie.
    """
    d = Diagram("Two Services, One Boundary", w=1000, h=610)
    d.note(MID, 44, "no transaction spans the two", ANNOTATION, 21)
    boundary(d, 490)

    # no ties here: containment already says who owns the store, and the tie ran
    # straight through the red scope's own label, which is the defect the whole
    # legibility pass was about. `one-service` keeps its tie, because there the reader
    # has to see that the application reaches the store and the outsider does not.
    service(d, 40, 124, 380, 330, "the Ordering service", "Ordering",
            store="Orders", app_h=120, tie=False)
    service(d, 580, 124, 380, 330, "the Shipping service", "Shipping",
            store="Shipments", app_h=120, tie=False)

    out = d.pipe(440, 172, 120, 48)
    d.msg(487, 184, w=26, h=20)
    back = d.pipe(440, 240, 120, 48)
    d.msg(487, 252, w=26, h=20)
    d.arrow((390, 196), out, sides=(None, "l"))
    d.arrow(out, (610, 196), sides=("r", None))
    d.arrow((610, 264), back, sides=(None, "r"))
    d.arrow(back, (390, 264), sides=("l", None))

    # The scope that cannot be had, drawn across the two services rather than in place
    # of them. It crosses the boundary rule, and the cross lands where the two meet.
    # Its top edge is 42 units above the stores rather than level with them: a group's
    # own label is set at the top LEFT, and at 336 it lay straight across the Orders
    # cylinder -- which `lint_figures.py` cannot see, because it measures notes against
    # nodes and a group's label is neither.
    d.group(96, 296, 808, 168, "one transaction across both", accent=True)
    d.icon(MID, 378, "cross", accent=True, r=19)

    d.note(MID, 528, "so you communicate through multiple messages over time", COMMENT, 18)
    d.note(MID, 558, "and consistency stops being something you declare", COMMENT, 18)
    d.note(MID, 586, "and becomes something you design", COMMENT, 18)
    return d


@figure("task-queue-shape")
def task_queue_shape():
    """§4.3 *Worked Example — the Task Queue*. The pump and competing consumers as an
    application shape, and the first time the deck draws something you could build.

    **One dashed container round the whole thing, and one database.** The slide's
    callout is *one team, one service, one queue — robustness without reorganising the
    company*, and that is a claim about where the boundary is **not**. §1 has just spent
    two figures on a boundary between two services with a store each; this is the same
    vocabulary saying the opposite thing, so the two halves share a store and sit inside
    one container. Drawing a boundary here would teach the room to reach for a new
    service every time a request is slow, which is exactly what the callout denies.

    Red is on the **return**, because that is what is bought. The queue is not the
    point; the queue is how.

    **The gaps between the boxes are load-bearing, not whitespace.** Every arrow here
    is labelled, an arrow label is centred on its own run, and it does not scale when
    `compact` runs -- so a 150-unit label needs a 190-unit gap or `lint_figures.py`
    reports it sitting on the box it leaves. That is what set the x positions.
    """
    d = Diagram("The Task Queue", w=1500, h=700)
    d.note(750, 46, "the web server returns before the work is done — "
                    "and the work is not lost, it waits", ANNOTATION, 21)

    d.group(25, 100, 1450, 480, "one service, one team — no new boundary")
    d.box(60, 206, 170, 96, "Browser")
    web = d.box(400, 200, 210, 108, "Web Server")
    pipe = d.pipe(900, 210, 220, 84)
    for i in range(4):
        d.msg(918 + i * 50, 236, w=30, h=24)
    workers = [d.box(1210, y, 200, 84, "Worker") for y in (146, 242, 338)]
    store = d.cylinder(760, 460, 240, 96, "one database")

    d.arrow((230, 228), (400, 228), "a request")
    d.arrow((400, 282), (230, 282), "returns now", accent=True)
    d.arrow(web, pipe, "enqueue the work", sides=("r", "l"), ly=-8)
    for w in workers:
        d.arrow(pipe, w, sides=("r", "l"))
    # both halves reach the same store -- that IS the "one service" claim, and it is
    # why the store sits between them rather than under the web server
    d.attach(web, store, sides=("b", "l"), via=[(505, 508)])
    d.attach(workers[2], store, sides=("b", "r"), via=[(1310, 508)])

    d.note(1010, 190, "a channel", INK, 18)
    # A name, so ink -- and it sits ABOVE the three boxes. Under them it was centred on
    # the same x as the tie running down to the store, which put a dashed hairline
    # between the two words. `lint_figures.py` cannot see that: it measures notes
    # against nodes, and an edge is neither.
    d.note(1310, 120, "competing consumers", INK, 18)
    d.note(750, 618, "the web server stays responsive when the backend is slow, "
                     "overwhelmed or down —", COMMENT, 18)
    d.note(750, 646, "add consumers until you drain faster than the work arrives",
           COMMENT, 18)
    return d


@figure("task-queue-http")
def task_queue_http():
    """§4.3 *Task Queue — HTTP Flow*. The same shape again, in the protocol everyone in
    the room already ships.

    **What the picture adds that the bullets cannot is that there are two paths.** The
    client posts to one place and comes back to a *different* one, while the work
    travels a path the client never sees. Drawing the four steps in a row would just
    restate the slide -- which is the failure the 2021 exports were full of -- so the
    work path runs across the top, the client's read path runs along the bottom, and
    the KV store is the only thing both of them touch.

    Red is on the 202, because that is the promise, and §4.4 opens by pointing out that
    nothing so far actually keeps it.

    **The worker's two outputs leave downwards and are told apart by route, not by
    label.** A vertical run puts its own label straight through itself -- `_mid` takes
    the middle segment -- so the one that needs saying gets a horizontal leg to say it
    on, and the one that does not is captioned underneath what it produces.
    """
    d = Diagram("The Task Queue over HTTP", w=1360, h=650)
    d.note(680, 46, "202 says: we have your work, and we will not lose it",
           ANNOTATION, 21)

    client = d.box(60, 176, 190, 100, "Client")
    web = d.box(420, 176, 210, 100, "Web Server")
    pipe = d.pipe(780, 186, 220, 84)
    d.msg(812, 212, w=30, h=24)
    d.msg(872, 212, w=30, h=24)
    worker = d.box(1090, 176, 200, 100, "Worker")
    kv = d.cylinder(700, 430, 220, 92, "progress\n(a KV store)")
    order = d.cylinder(1080, 430, 220, 92, "the order itself")

    d.arrow((250, 200), (420, 200), "POST the work")
    d.arrow((420, 252), (250, 252), "202 + Location", accent=True)
    d.arrow(web, pipe, "enqueue it", sides=("r", "l"), ly=-8)
    d.arrow(pipe, worker, sides=("r", "l"))
    d.arrow(worker, kv, "notes progress as it goes", sides=("b", "t"),
            via=[(1120, 340), (810, 340)])
    d.arrow(worker, order, sides=("b", "t"))
    d.arrow(client, kv, "GET the progress page", sides=("b", "l"), via=[(155, 476)])

    d.note(890, 168, "a work item, waiting", INK, 18)
    d.note(1190, 560, "created at a sustainable pace —\n404 until it exists",
           COMMENT, 18)
    d.note(400, 600, "guaranteed delivery with no new infrastructure,\n"
                     "in a protocol the room already ships", COMMENT, 18)
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
        print(f"  {name:<26} {dg.w}x{dg.h}  {os.path.getsize(png):>8,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
