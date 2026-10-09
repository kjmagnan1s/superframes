# Storyboard workflow: settle the words, then lock the look

Two cheap artifacts sit between the project folder and the render: the
**key-events table** (the words) and the **storyboard** (the look). The
storyboard is what the approval gate reviews; nothing animates until it passes.

## Key-events table

Read everything in the project folder and the `frame.md`, then write a markdown
table in the project folder, one row per scene: scene number, what is SAID, a
one-line note on what is ON SCREEN, and a target duration. Pacing and structure
come from `prompt-craft.md`.

Refine only the copy at this stage: the hook, the claims, the closing line. Cut
or merge rows here, not after animation. Flag any beat that drifts off the
video's one message; an off-topic tangent is easy to miss in a table and obvious
in a render.

## Storyboard file shapes

- **Default: one file.** `storyboard.html` with a stack of `.scene` blocks, one
  static frame per scene at its densest moment. Quick to scan the whole film.
- **Per-scene contact sheet** only for a scene too busy to read in the stack.

Examples in `github.com/heygen-com/hyperframes-launches`: `variables-launch/storyboard.html`,
`variables-launch/STORYBOARD-SCENE-05.html`,
`frame-md-launch-storyboard/scene-02-contact-sheet.html`.

When the brand already has an approved storyboard, start from it instead of
re-deriving the look, then change what this video needs.

## Storyboards over real footage

For a talking-head edit with overlays or HyperFrames scenes:

- Transcribe first so beats land on real words. Keep the storyboard in its own
  folder inside the project.
- One still per beat: a real frame grab at the beat timestamp with the planned
  overlay mock composited on it. A cut-only edit still gets beat stills that show
  the cut structure.
- Mark each beat's visual source (built in HTML, or a generated plate plus a
  build) so the review can approve that call too.
- Use the script, not just the transcript: on-screen data the speaker chose not
  to say aloud lives there.

## Serving and checking it

```bash
cd <storyboard folder> && python3 -m http.server 8000
```

Chrome can't open `file://` pages. Check the page in a browser yourself before
sending the link. Design-lint warnings on `storyboard.html` are about an
internal review page; ignore them rather than writing suppressions.

## The review message

Send the URL with a short numbered list of the open decisions (hook text, a
layout choice, a plate vs build call), so the reviewer can answer per number
("1 yes, 2 is okay, 3 cut it"). Those answers usually change the build. On
approval, start the build; don't park it behind other work.

## After approval

Each storyboard frame becomes a scene. Render a rough pass first
(`npx hyperframes render --quality draft`) so timing and layout problems show
before the full build. Authoring then belongs to the `hyperframes` skill and CLI
work to `hyperframes-cli`.

## Why this order

- Words wrong, look right: a polished video that says the wrong thing.
- Look wrong, words right: a long render thrown away.
- Settling each on its cheap artifact means the expensive full composition runs
  once, mostly right.

The canonical end-to-end example is
`github.com/heygen-com/hyperframes-launches/frame-md-launch-storyboard/`
(frame.md, contact sheets, compositions, `HANDOFF.md`, final render).
