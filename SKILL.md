---
name: superframes
description: Builds the plan and storyboard for a HyperFrames video before anything is animated - an assets-first project folder, one frame.md, a key-events table, static keyframes in storyboard.html, and reuse of HeyGen's open-source launch components - then hands off to the hyperframes skill for authoring. Use it for launch, product, or feature videos built in HyperFrames and for talking-head edits that carry HyperFrames scenes or overlays, including when the user says "make a video about X", "storyboard this", or wants a polished motion-graphics piece. Use it instead of hyperframes-studio whenever the job is planning and storyboarding a new video; hyperframes-studio is for live edits inside an open Studio project, and hyperframes or hyperframes-cli take over for composition authoring and CLI commands once the storyboard is approved.
---

# Superframes

**Owner layer:** if `local/OWNER.md` exists in this skill's folder, read it
first. It holds the owner's look, gates, defaults, and tooling, and it overrides
the defaults here.

The `hyperframes` skill knows how to write a composition. Superframes is the
production process in front of it, distilled from how HeyGen builds its launch
videos: real assets first, one aesthetic source, words settled in a table, the
look settled on static frames, proven components reused. Weak HyperFrames output
almost always skipped those steps.

## Pick the entry path

- **A website or landing page exists:** run `/product-launch-video` (through
  `/hyperframes` routing). Its capture writes `capture/extracted/tokens.json`,
  then it builds `frame.md` from a preset.
- **Music-driven:** use the audio-reactive reference in the `hyperframes` skill.
- **Anything else** (a feature, an idea, a PR or a week of commits, a talking-head
  video with HyperFrames scenes): run the workflow below. For a PR or commits,
  the diff and commit log are the context doc in step 1.

The anti-patterns at the bottom apply on every path.

## Workflow

### 1. Fill the project folder before planning

- A context doc: the feature README, the announcement text, the exact claims.
  For a talking-head video, read the script as well as the transcript; numbers
  and prompts the speaker didn't say aloud often belong on screen.
- Real assets: logo, brand colors, UI screenshots, product shots. Check the
  project folder for screenshots the user already dropped in.
- References: frames or stills of looks to match.
- Exactly one aesthetic source, the `frame.md` (step 2).

Claude matches what it can see, so more real assets up front means fewer rounds.

### 2. One frame.md

Use the `frame-md` skill to produce it. A frame.md is per brand: build it once
and reuse it. When the brand already has a preset, use it and skip the picker.
Skip the hyperframes.dev/design web tool; it is login-gated and does nothing
`frame-md` can't.

### 3. Key-events table (settle the words)

One row per scene: what is said and a one-line note on what is on screen. Shape
it with [references/prompt-craft.md](references/prompt-craft.md) (narrative
skeleton and pacing); read its first two sections before drafting. Refine only
the copy here. Fixing words now is free; after animation it is expensive.

Optional Jev checks (cheap, advisory, never rewrite a line; details in
[references/jev-scoring.md](references/jev-scoring.md)):

- `python3 scripts/jev_keyevents.py <table.md> --total <seconds>`: weak rows,
  merge candidates, narrative slot, and pacing fit per row.
- `python3 scripts/jev_audit.py <BRIEF.md> <table.md>`: the plan against the
  text-checkable anti-patterns. Default: run it once before step 4.

### 4. Storyboard (lock the look)

Build one static frame per scene in `storyboard.html`, each showing the scene's
densest moment, styled from the `frame.md`. No animation. Iterate here; a static
frame takes a minute or two, a full composition takes many.

For the HyperFrames run itself, write `BRIEF.md` with `storyboard: yes` so the
upstream review loop pauses on the board. That is the upstream contract in
`brief-format.md` in the `hyperframes` skill's references: `flow` (`automation` or
`companion`) plus `storyboard: yes` derives `mode: collaborative`
(`brief-contract.md` § 1). Default: `storyboard: yes`. Use `storyboard: no`
only when the user explicitly asks for a hands-off run.

Mechanics (file shapes, real-footage beat stills, serving, the review message):
[references/storyboard-workflow.md](references/storyboard-workflow.md). Preview it
over a local HTTP server (`python3 -m http.server` in the storyboard folder);
Chrome can't open `file://` pages.

### 5. Rough render, then the full composition

When the storyboard is approved, start the build right away. Turn each
storyboard frame into a scene and render a quick rough pass first
(`--quality draft`) so timing and layout problems show before the full build.
From here, authoring is the `hyperframes` skill's job and CLI work (lint,
validate, preview, render) is `hyperframes-cli`'s.

### 6. Reuse before building

Before building anything net-new, find it in HeyGen's launch videos, the
registry, or your own past projects, and adapt it to the `frame.md`. Repo paths,
the catalog, and reuse prompts:
[references/template-reuse.md](references/template-reuse.md).
`python3 scripts/jev_templates.py --brief "..." [--kind launches|components|blocks|examples]`
ranks the catalog against the brief so Claude opens three or four folders, not
all fourteen. It ranks descriptions; judge the bones by eye.

### 7. Studio polish and export

Small nudges (text, position, timing) go through the HyperFrames studio, where
edits become code Claude can read. Structural changes go through chat.

Export MP4 by default. For anything transparent (overlays to composite), render
`--format mov`, not WebM: WebM often comes out `yuv420p` with no real alpha.
Confirm with
`ffprobe -v error -select_streams v:0 -show_entries stream=pix_fmt -of csv=p=0 <file>`;
anything not `yuva*` has no alpha, so rebuild it.

## Anti-patterns

`scripts/jev_audit.py` checks the text-checkable ones; the rest need eyes.

- **The PPT video:** slides with a fade between them. Drive it with motion and timing.
- **Designing a video like a web page:** in video the eye stays center and
  information arrives over time. Fewer, bigger elements; let motion carry hierarchy.
- **Skipping the storyboard:** a long render that shows the look was wrong.
- **Building net-new every time:** slower and buggier than adapting a proven component.
- **More than one aesthetic source:** two design files muddy the look.
- **Hand-editing the generated code:** it is huge. Use the studio or describe the change.

## References

- [references/storyboard-workflow.md](references/storyboard-workflow.md): key-events
  table and storyboard mechanics, storyboards over real footage, the review message.
- [references/prompt-craft.md](references/prompt-craft.md): narrative skeleton,
  pacing numbers, transition grammar, signature moves, prompting vocabulary.
- [references/template-reuse.md](references/template-reuse.md): launch-video repos,
  component catalog, replicating a release video.
- [references/jev-scoring.md](references/jev-scoring.md): what the Jev scripts
  decide, their thresholds, and what stays a human call.
- [references/source-notes.md](references/source-notes.md): provenance of the
  HeyGen sources this skill distills.
- The `frame-md` skill owns frame.md creation.
- Maintainers: `scripts/pre-push` guards pushes against secrets and personal
  data; run `./scripts/install-hooks.sh` once after cloning.
