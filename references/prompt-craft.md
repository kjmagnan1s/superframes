# Prompt craft — what makes a HyperFrames launch video good

Two sources, both **HyperFrames / HeyGen**: the patterns below are distilled from
their open-source launch videos (9 analyzed: cloud-render, claude-paper, spacex,
variables, inspector, timeline, pr-to-video, frame-md-launch-storyboard,
website-to-hyperframes), and the vocabulary tables are from their **prompting
guide** (hyperframes.heygen.com/guides/prompting). Use this when writing the
key-events table, the storyboard, and the prompts that drive authoring. The
`frame.md` (via the `frame-md` skill) carries the look; this carries the motion,
pacing, and structure.

## The narrative skeleton

Launches follow **Before-After-Bridge** (problem → turn → payoff), not a feature
list. The recurring beat order:

1. **Hook / cold open (≈4-5s).** Open *inside a real interface mid-action*, not on
   a title card. A typed prompt, a kinetic thesis line ("Why do AI videos look
   like slides?"), or a concrete pain. Typing starts by ~0.6s.
2. **Problem / diagnosis.** Make the pain visceral and *diegetic* (a real render
   crawling at 1%, a real PR that's painful to read). Never a bullet list.
3. **The turn / text beat.** One thesis line, one hero per frame ("Don't get
   blocked by your machine.").
4. **Product reveal + how-it-works.** The longest-dwell scenes (10-13s) — show the
   real flow, real UI, real output.
5. **Proof / payoff.** The result, often a number ("All 6 finished", "$1.0T").
6. **Closer / endcard.** Real logo + a literal CTA command line; resolve the
   product brand up to its parent; footage keeps playing underneath.

Two valid variants: **persistent-chat-as-film** (one chat window grows across
every scene, never a fresh card) and **kinetic text-essay** (a run of typographic
statements interleaved with product proof; see inspector, variables).

## Pacing (real numbers)

- **Total:** 30-60s. Short product launches ~30-40s; conversational/explainer ~40-60s.
- **Scenes:** 8-10 top-level.
- **Beats:** 2-7s for narrative scenes. **Hooks short** (~4-5s). **Connective
  micro-beats very short** (<1.5s; one montage runs sub-second cards at 0.15/0.33/0.67s).
  **Hero/demo scenes hold longest** (10-13s). **Closers hold 2.7-8s** — give the
  wordmark room.
- Open fast, vary the rhythm (don't make every beat the same length), let the
  demo breathe, let the ending land.

## Transition grammar

A small, intentional vocabulary, placed by meaning (not decoration):

| Transition | Motion | Use it for |
|---|---|---|
| **cut-the-curve** | lateral 0.2-0.3s shove + opacity | moving *within* one world (chat beat → chat beat, into a text beat) |
| **zoom-through** | push into an element on Z, next scene zooms in behind (`scale:1.8, blur(12px)`) | *entering the payoff / product world*; brand-to-parent endcard |
| **morph** | one continuous reshape, no cut | *crossing* problem-world → product-world (connector card morphs into the chat window) |
| **hard cut** | none | match-cut on an *identical* frame (one scene's bare end-state = next scene's start-state) so a sequence reads as one continuous shot |

Rule of thumb: **lateral/calm moves within a world; Z-axis/energetic moves
(morph, zoom-through) cross worlds.** Let the **background lead** — it makes a
larger x/y/scale/hue move ~0.1s before the foreground follows.

## Signature moves (the repeatable quality)

- **Typewriter prompt** with a colored caret that rises and taps ↵, flashing its
  color on the keypress.
- **Persistent chat window that accumulates history** across scenes (one window
  growing, never reset). Keep the assistant's accent color *inside* its window only.
- **Real terminal / pipeline code, never fake "job pills."** A highlight scans a
  real ASCII log line-by-line. Diegetic, honest proof beats decoration.
- **One-hero text beats:** staggered word entry (`stagger: .055, power4.out`), a
  **single gradient accent word**, exit as a downward waterfall.
- **Kinetic count-up numerals** for stat reveals (digit-stack driven by `onUpdate`).
- **Camera push / zoom-through into a grid** of finished work; a column clears and
  the logo reveals into the gap.
- **Match-on-identical-frame cuts** to stitch multi-scene runs into one shot.

## Openings & closings

- **Open** inside a live interface mid-action (or on a kinetic typed thesis), never
  a static title. Type by ~0.6s; land a synchronized SFX (~0.9s).
- **Close** on a *real logo SVG* (not a hand-built wordmark) + a literal CTA command
  line (`npx skills add heygen-com/hyperframes`, a URL). Resolve the product brand
  up to its parent with a zoom-through. Keep footage playing under the endcard.

## Prompting vocabulary (from the HyperFrames guide)

Describe motion and tone in these adjectives; the agent maps them to concrete
eases and styles, so similar prompts stay coherent.

**Motion → ease** (richer than the base hyperframes 4-tier map — prefer these):

| Word | Ease | Feel |
|---|---|---|
| smooth | `power2.out` | natural deceleration |
| snappy | `power4.out` | quick, decisive |
| bouncy | `back.out` | overshoots then settles |
| springy | `elastic.out` | oscillates into place |
| dramatic | `expo.out` | fast start, long glide |
| dreamy | `sine.inOut` | slow, symmetrical |

Timing: fast 0.2s (energy) · medium 0.4s (professional) · slow 0.6s (luxury) ·
very slow 1-2s (cinematic).

**Caption tone:** Hype (heavy weight, scale-pop, 72-96px) · Corporate (clean sans,
fade+slide, 56-72px) · Tutorial (mono, typewriter, 48-64px) · Storytelling (serif,
slow fade, 44-56px) · Social (rounded, bounce, 56-80px).

**Transition by energy:** Calm = blur crossfade / cross-warp morph · Medium = push
slide / whip pan · High = zoom-through / glitch burn.

**Marker highlight:** `highlight` (sweep, key phrases) · `circle` (single words) ·
`burst` (hype moments) · `scribble` (crossing out) · `sketchout` (rectangle callout).

**Render quality:** `draft` (iterate) · `standard` (review) · `high` (final).

**Prompt shapes:** *cold start* — state duration, aspect, mood, key elements.
*warm start* — give a URL/doc/CSV/transcript to synthesize (stronger output).
*iterate* — small targeted edits after the first render ("make the title 2x
bigger", "add a fade-out"), not a re-prompt.

## The anti-PPT discipline

What separates these from slideware, as directives:

- **Master timeline owns only the seams.** Each scene is a self-contained, paused,
  seek-safe GSAP timeline registered to `window.__timelines[id]`; the root hides
  every later scene at t=0 so nothing flashes, and drives only the 0.2-0.5s seams.
- **One world, modulated** — not a new visual world every beat. Modulate density,
  hue, and the background across scenes; keep the ground constant.
- **Render-safe:** autoplay off; drive Lottie/video frames via a GSAP `onUpdate`
  over the beat; media carries `data-start`/`data-duration`/`data-track-index` so
  it's seekable, not wall-clock.
- **Contact-sheet first:** lock static 16:9 keyframes before any motion (this is
  the storyboard step — see storyboard-workflow.md).
- **Diegetic, honest proof:** real terminal logs, real persisting chat, real screen
  captures. Don't fake the product.
- **Synchronized SFX** choreographed to the motion (type/paste/click/whoosh/chime),
  each a discrete cue with exact timing.
- **A single gradient accent** as the only color on otherwise restrained frames.
- **Heavy display type**, negative letter-spacing, ~0.9 line-height, with a serif
  for thesis words. Editorial, not Calibri.
