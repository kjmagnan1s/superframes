---
name: superframes
description: Pre-production workflow for high-quality HyperFrames videos — the HeyGen builder process (assets-first project folder, frame.md aesthetic source, key-events table, static storyboard keyframes, template/component reuse, studio iteration). Use this BEFORE authoring any HyperFrames composition, and whenever the user wants a launch video, product/feature announcement, "turn this website/PR/repo into a video," a polished motion-graphics piece, or says "make a video about X." Use it whenever the goal is a crisp, on-brand video rather than a quick one-off — it sets up the work so the hyperframes skill can author it well. Pairs with (does not replace) the hyperframes and hyperframes-cli skills. Trigger even when the user doesn't say "HyperFrames" by name, as long as they want an AI-built video with real production quality.
---

# Superframes

The `hyperframes` skill knows HOW to write a composition (data attributes,
timeline contract, animation rules). **Superframes is the layer above it: the
production process the HeyGen team uses to get great videos fast.** Most weak
HyperFrames output comes from skipping straight to "make me a video" with no
assets, no aesthetic source, and no storyboard. This skill front-loads that
work so the first render is already close.

Use `hyperframes` for authoring mechanics and `hyperframes-cli` for CLI
commands. Superframes orchestrates them and the open-source templates.

## The five pillars

1. **Set up before you prompt.** A project folder full of real context and
   assets beats any clever prompt. The agent can only match an aesthetic it can
   see.
2. **One aesthetic source: a frame.md.** Lock brand + motion intent in a single
   `frame.md` (the video-native evolution of `design.md`) and feed it
   everywhere. Exactly one — competing sources muddy the look.
3. **Storyboard before you animate.** Settle the words in a key-events table,
   then lock the look with one static HTML keyframe per scene. Iterate there —
   it is seconds per loop, not minutes.
4. **Reuse, don't rebuild.** Every HyperFrames video is code. Pull components
   and whole effects from HeyGen's open-source launch videos and from your own
   past projects. Net-new is slower and less likely to work first try.
5. **Last-mile in the studio.** Open the preview studio and nudge text,
   position, and timing by hand. Those edits become code the agent can read, so
   you and the agent stay in sync without re-prompting.

## Pick the entry path first

Before any of the workflow below, choose how the project starts — the fastest
correct path wins:

- **There's a website/landing page** → use the `website-to-video` skill
  ("Use my website, make me a launch video" / give it the URL). It scrapes
  assets, writes a `design.md`, storyboards, and one-shots a draft. This is also
  the best worked example to read if you're new — it shows the whole pipeline.
- **It's a GitHub PR or recent commits** → use the `pr-to-video` skill (HeyGen
  ships this; "look at my commits for the last 7 days and make a recap video").
- **It's music-driven** → use the audio-reactive path (the `hyperframes` skill's
  audio-reactive reference). HeyGen also ships a dedicated `music-to-video` skill
  upstream — check whether it's installed before hand-rolling.
- **None of the above (a feature, an idea, a launch with no page yet)** → run
  the manual workflow below. This is Jake's launch process and is the heart of
  this skill.

Whatever the path, the pillars and anti-patterns still apply.

## The manual workflow

### 1. Build the project folder (assets-first)

Create a dedicated folder and fill it with context BEFORE prompting:

- A short context doc — a README of the feature, the announcement text, the
  exact messaging/claims you want said. Ground the copy in real material.
- Real assets: logo, brand colors, Figma exports, UI screenshots, product
  shots. Screenshot the actual UI you're announcing.
- Reference examples you like — frames from other videos, stills, links. If you
  can already picture a few frames of the video, put those references in.
- Exactly **one** aesthetic source (the `frame.md`, next step).

Why: the agent matches what it can see. More real assets up front = a closer
match on the first pass and far less back-and-forth.

### 2. Create the aesthetic source — frame.md

`design.md` is a brand guideline built for **web pages** (colors, fonts, hex
codes; the agent takes spatial liberties). `frame.md` is the **video-native**
reformat: it tells the agent to maximize the frame, go larger, and lean on
motion — because video is a temporal medium, not a scrollable page.

Use the **`frame-md` skill** to produce it — it wraps HyperFrames' open-source
frame.md presets and overlay procedure (pick the closest preset, overlay the
brand's atoms, adapt the treatments), sourcing atoms from a design.md, a
`website-to-video` capture, or raw brand inputs. A frame.md is a per-brand
artifact: build it once, reuse across every video for that brand. Skip the
hyperframes.dev/design online tool — it's login-gated and does nothing the
`frame-md` skill can't.

The existing `hyperframes` "Visual Identity Gate" expects a DESIGN.md /
visual-style. A `frame.md` satisfies that gate and is strictly better for video
— point the gate at it.

### 3. Write the key-events table (settle the words)

Point the agent at the project folder and the `frame.md`, then ask for a
**table of key events**: a scene-by-scene breakdown — for each scene, what gets
said and a one-line description of what's on screen.

Refine the **copy** here, and only the copy. This is the meat of the story.
Push back on lines ("that should say X", "help me brainstorm the hook") before a
single pixel is animated — fixing words now is free; fixing them after
animation is expensive.

### 4. Lock the look — storyboard.html (static keyframes)

From the key-events table, have the agent build a `storyboard.html`: **one
static frame per scene**, each showing that scene's most visually dense moment,
styled from the `frame.md` and from references pulled out of the launch-video
repos (step 6). No animation yet.

Why this is the highest-leverage step: a full 45s+ composition takes minutes to
generate. A static frame takes ~1-2 minutes. Iterate on the static frames until
the aesthetic is right ("the hook needs more contrast", "shrink this stat"),
THEN animate. This is "Layout Before Animation" from the hyperframes skill,
applied to the whole video at once. See
[references/storyboard-workflow.md](references/storyboard-workflow.md) for exact
prompts.

### 5. Promote to a full composition + open the studio

Once the storyboard is approved: "turn this into a full HyperFrames video and
open it in the HyperFrames studio." Each storyboard frame becomes a scene. From
here, authoring is the `hyperframes` skill's job — hand off to it for the
timeline, transitions, captions, TTS, and the lint/validate/render loop
(`hyperframes-cli`).

### 6. Reuse components and effects

Before building anything net-new, look for it in the open-source launch videos
or your own past projects:

- "Pull the [prompt box / text reveal / lower-third] from [that video] for my
  intro."
- "I love the text animation in [launch video]; grab it and adapt it here."

You don't read the (agent-written, huge) code yourself — point the agent at the
cloned repos and let it extract. See
[references/template-reuse.md](references/template-reuse.md) for the local repo
paths, the component catalog, and the release-video replication workflow.

### 7. Iterate in the studio, then export

- Open the studio with `npx hyperframes preview` (run `npx hyperframes lint`
  first — it catches missing `data-composition-id`, overlapping tracks, and
  unregistered timelines before you preview). Drag elements, edit
  text/font/color/motion curves by hand.
  Edits become code, so the agent sees the diff — use the studio for the tiny
  changes you can't describe, and chat for structural ones.
- Export to MP4 (default), MOV, or WebM. For compositing motion graphics into a
  pro editor (Premiere/Resolve), export a **transparent-background WebM**. You
  can also export as a website for an interactive player.

## Anti-patterns (why videos come out weak)

- **The "PPT video."** Slides with a fade between them. Nobody watches a
  launch past 5 seconds of that. Drive it with motion and timing.
- **Designing a video like a web page (spatial vs temporal).** On a page the
  eye scans and chooses where to look; in video the eye stays center and
  information is fed over time. Maximize the frame, fewer-bigger elements, let
  motion carry hierarchy. This is the whole reason `frame.md` exists.
- **Skipping the storyboard.** Burning a long full-composition render only to
  find the aesthetic is wrong. Lock it on static frames first.
- **Building net-new every time.** Slower and more bug-prone than adapting a
  proven component.
- **More than one aesthetic source.** Two design files = a muddled look. One
  `frame.md`.
- **Hand-editing the raw generated code.** It's agent-written and huge. Use the
  studio UI or tell the agent what to change.

## Model and cost notes

- Use a top-tier frontier model for the best quality (strong visual reasoning
  also lets it clip source video to timestamps, match references, etc.).
- Gemini is the quality-to-cost pick (HeyGen's own internal agent runs on it).
- TTS defaults to a free local model the agent auto-downloads; connect HeyGen or
  ElevenLabs only when you want premium voices.

## References

- The **`frame-md` skill** — owns frame.md creation (HyperFrames' open-source
  presets + the overlay procedure). superframes delegates step 2 to it.
- [references/storyboard-workflow.md](references/storyboard-workflow.md) —
  key-events table + storyboard.html, exact prompts, the iterate-on-static loop.
- [references/template-reuse.md](references/template-reuse.md) — local clone
  paths, the launch-video repos, component catalog, release-video replication.
- [references/source-notes.md](references/source-notes.md) — provenance: the two
  transcripts and the repo list this skill distills.
