# Storyboard workflow — settle words, then lock the look

Two artifacts sit between "I have a project folder" and "render the video": a
**key-events table** (the words) and a **storyboard** of static keyframes (the
look). Both are cheap to iterate; the full composition is not. Getting these
right is the single biggest lever on quality and speed.

## Step A — the key-events table (the words)

Point the agent at the project folder and the `frame.md`, then:

> "Read everything in this folder and the frame.md, then give me a **table of
> key events** for a ~Ns video: one row per scene with what we SAY and a
> one-line note on what's ON SCREEN."

Then refine **only the copy**. This is the meat of the story — the hook, the
claims, the closing line. Push back here: "scene 2 should say X", "help me
brainstorm three hooks", "cut scene 5, merge it into 4." Fixing words now is
free; rewriting after animation throws away work.

Keep the table as a markdown file in the project folder so the storyboard and
final composition both trace back to it.

## Step B — the storyboard (the look)

From the approved table, have the agent build a **static** storyboard — no
animation yet:

> "From the key-events table, build a `storyboard.html`: one static frame per
> scene, each showing that scene's most visually DENSE moment. Use the frame.md
> for the look and pull references from the launch-video repos. No GSAP yet."

This is "Layout Before Animation" (from the `hyperframes` skill) applied to the
whole film at once. A full 45s+ composition takes minutes to generate; a static
keyframe set takes ~1-2 minutes. So you iterate on the look here — "the hook
needs more contrast", "this stat is too small", "wrong font on scene 3" — until
the aesthetic is locked, THEN animate. You avoid burning a long render on the
wrong direction.

### Two storyboard shapes (both real)
- **One file, all scenes** — `storyboard.html` with a stack of `.scene` blocks.
  Quick to scan the whole film. (Example:
  `github.com/heygen-com/hyperframes-launches/variables-launch/storyboard.html`.)
- **Per-scene "contact sheets"** — one file per scene for dense scenes.
  (Examples: `variables-launch/STORYBOARD-SCENE-05.html`,
  `frame-md-launch-storyboard/scene-02-contact-sheet.html`,
  `scene-03-contact-sheet.html`.)

Use the single file by default; split out a per-scene contact sheet only for a
scene that's too busy to read in the stack.

## Step C — promote to a full composition

Once the storyboard is approved:

> "Turn this storyboard into a full HyperFrames video and open it in the
> HyperFrames studio."

Each storyboard frame becomes a scene. Authoring now belongs to the
`hyperframes` skill (timeline contract, entrance/exit rules, transitions,
captions, TTS) and `hyperframes-cli` (lint / validate / preview / render). Hand
off — don't re-derive the mechanics here.

## Why this order matters
- Words wrong + look right = a polished video that says the wrong thing.
- Look wrong + words right = a long render you throw away.
- Settling each on its cheap artifact first means the expensive step (the full
  animated composition) runs once, mostly right.

## Reference
The canonical end-to-end demo HeyGen shipped is
`github.com/heygen-com/hyperframes-launches/frame-md-launch-storyboard/` — it
contains the frame.md, the storyboard contact sheets, the compositions, a
`HANDOFF.md`, and the final render. Read it when you want to see the whole flow
in one place.
