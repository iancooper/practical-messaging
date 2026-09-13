#!/bin/sh
# Build the takeaway pack to A4 PDF.
#
#   ./build.sh            # both handouts
#   ./build.sh Routing-Patterns
#
# MUST be run from handouts/ -- the figure paths in the Markdown, the font
# paths in print.css and the stylesheet link are all relative to this
# directory. The script cds to its own location so that holds either way.
#
# A handout is proved by BUILDING it, not by reading it. Three defects are
# invisible in Markdown and every one has shipped here: pandoc drops the
# leading "N. " when it makes a heading id, so ](#1-discovery) is a dead link;
# a preformatted block wraps past ~62 monospace columns; and an arrow glyph
# inside one falls out of the monospace face and destroys the alignment.
# LOOK AT THE PDF.
#
# implicit_figures is OFF on purpose: every image in the pack has its pattern
# name as alt text and sits directly under a heading of the same name, so the
# generated <figcaption> said it twice. Write an explicit <figure> if a figure
# ever needs a caption of its own -- print.css still styles one.

set -eu
cd "$(dirname "$0")"

if [ "$#" -gt 0 ]; then
  set -- "$@"
else
  set -- Routing-Patterns Managing-Asynchronous-APIs
fi

for name; do
  name=${name%.md}
  printf '%-32s' "$name.pdf"
  pandoc "$name.md" \
    --from=markdown-implicit_figures \
    --to=html5 \
    --standalone \
    --template=print.html \
    --css=print.css \
    --pdf-engine=weasyprint \
    --metadata title="$name" \
    -o "$name.pdf" 2>&1 |
      grep -v 'WARNING: Ignored `text-rendering' || true
  printf '%s bytes\n' "$(wc -c < "$name.pdf" | tr -d ' ')"
done
