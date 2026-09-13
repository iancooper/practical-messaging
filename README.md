# Practical Messaging

Material to support my Practical Messaging Workshop's exercises. Note that this folder is not open source i.e. copyleft, but feel free to clone, browse the material, consume it, and do the exercises, whether or not you have attended the associated course.

Please contact me if your company would like a private presentation of this material

I am very open with my course content for my workshops; I recognize that not everyone has an employer with a budget for them to travel and join others for the taught material, or works with me and gets to join a course for free. Whilst it is not the same as "being there" just in case it helps any of you, the material is in GitHub. It does get change over time as I find better ways to express this.

I usually try a different thing every workshop, to see if some new ideas help folks. So there is likely to be a 'surprise' that is not in this material yet.

Lecture Content:

* You can find the content for both days here: https://github.com/iancooper/practical-messaging

Coding Exercises:

* The exercises in my Github under Practical-Messaging-X where X is the language name.
  * You can use C#, Java, Go, JavaScript or Python for the exercises
  * For example https://github.com/iancooper/Practical-Messaging-Sharp
* The exercise and solutions are in branches, not trunk
* On Day One the prerequisite is the ability to run Rabbit MQ.
* On Day Two there is one exercise using Kafka. 

## Prerequisites

**For the coding exercises** — RabbitMQ on Day One, Kafka for one exercise on Day Two. See *Coding
Exercises* above.

**For presenting or rebuilding the slides** — the decks are set in four typefaces and use no others.
All of them are vendored in this repo, under `tools/fonts/`:

* **IBM Plex Serif** — Regular, SemiBold, Italic. Slide titles
* **IBM Plex Sans** — Variable, Italic, SemiBold Italic. All body copy, and the labels on the BPMN drawings
* **IBM Plex Mono** — section kickers, code and tables
* **Caveat** — every handwritten callout, and the labels in every drawing except BPMN

Install all eight before opening a deck:

```bash
cp tools/fonts/*.ttf ~/Library/Fonts/          # macOS
cp tools/fonts/*.ttf ~/.local/share/fonts/ && fc-cache -f   # Linux
```

On Windows, select all eight, right-click, **Install**.

**Then quit PowerPoint completely and reopen it.** This part is not optional and it is the part that
catches people. Office reads its font list *when it launches*, so a font installed underneath a
running copy stays invisible to it — and nothing on screen tells you. PowerPoint still reports the
font as `Caveat` in the toolbar, because that is what the file asks for; it simply draws something
else. The callouts fall back to a wider face, wrap onto a line the slide has no room for, and are cut
in half by the figure underneath. The result reads as a short sentence rather than as a bug.

If a red callout on a slide does not look like handwriting, the fonts are not being used.
