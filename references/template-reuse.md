# Template & component reuse

The core mindset (Jake, HeyGen): **"I try to not make things net-new if I
can."** Every HyperFrames video is code, so a proven component drops into a new
video, re-skinned by a different `frame.md`, faster and more reliably than
building from scratch. The generated code is huge: don't read a launch folder
whole. Open the composition that holds the effect and pull just that piece.

## Where the templates live

HeyGen open-sources these under **github.com/heygen-com**. Clone any locally for
offline reference (the main `hyperframes` repo carries ~1GB of LFS video, so
clone it with `GIT_LFS_SKIP_SMUDGE=1` to skip the media you don't need):

| Repo | What it is |
|---|---|
| `heygen-com/hyperframes` | The framework. `registry/` = the component catalog; `skills/` = every shipped skill; `examples/`, `packages/`. |
| `heygen-com/hyperframes-launches` | **The template gold** — full source of HeyGen's launch videos. |
| `heygen-com/skills` | HeyGen agent skills (avatar / translate / video). |
| `heygen-com/hyperframes-vercel-template` | Preview + render on Vercel. |
| `tonbistudio/hyperframes-prompts` | Community prompt patterns. |

## The launch-video library (full, re-skinnable compositions)

`github.com/heygen-com/hyperframes-launches/` — each folder is a complete video you
can lift whole effects or whole structures from:

- `frame-md-launch-storyboard` — the canonical frame.md → storyboard → render
  demo. Start here.
- `cloud-render-launch` — two-brand (interface vs product) system; terminal UI.
- `claude-paper-launch` — Claude Paper cream aesthetic + voiceover pipeline.
- `inspector-launch` — the studio Inspector; UI-product feel.
- `variables-launch` — has storyboards (single + per-scene contact sheets).
- `pr-to-video-launch`, `timeline-launch`, `sfx-music-launch`,
  `website-to-hyperframes` — feature launches; good for product-UI motion.
- `spacex-launch`, `texture-launch-video`, `vfx-heygen-combined`,
  `HF-heygen-stripe` — heavier VFX / brand-pastiche looks.

Each typically contains: `index.html`, `compositions/`, a `frame.md` or
`DESIGN.md`, `assets/`, and often voiceover/transcript files — i.e. a working
reference for the whole pipeline, not just one trick.

## The component catalog (`hyperframes/registry/`)

Browse `registry.json` (homepage: hyperframes.heygen.com), or the folders:

- **`registry/components/`** — drop-in effects & overlays: `caption-*` (karaoke,
  kinetic-slam, neon-glow, gradient-fill, glitch-rgb, matrix-decode,
  particle-burst, pill-karaoke, weight-shift, …), `grain-overlay`,
  `motion-blur`, `parallax-zoom`/`parallax-unzoom`, `shimmer-sweep`,
  `morph-text`, `texture-mask-text`, `grid-pixelate-wipe`, `vignette`.
- **`registry/blocks/`** — larger building blocks: `app-showcase`,
  `code-snippet-*` (dozens of terminal themes — apple-terminal, monokai,
  solarized, dark/light-2026, …), `code-diff`, `code-typing`, `code-morph`,
  `code-3d-extrude`, `code-scroll`, `data-chart`, `cinematic-zoom`,
  `apple-money-count`, `chromatic-radial-split`, `cross-warp-morph`.
- **`registry/examples/`** — full example comps: `warm-grain`, `play-mode`,
  `swiss-grid`, `vignelli`, `decision-tree`, `kinetic-type`, `product-promo`,
  `nyt-graph`.

The installed `hyperframes-registry` skill is the tool for pulling these in by
name — prefer it over hand-copying when adding a catalog component. You can also
**scaffold straight from an example**: `npx hyperframes init my-video --example
warm-grain` starts a new project from a catalog example instead of a blank file.

## Reuse prompts that work

- "Pull the `<code-diff / lower-third / prompt-box>` from
  `github.com/heygen-com/hyperframes-launches/<launch>/` and adapt it to my
  frame.md."
- "I love the text animation in `<launch>`; grab that one for my intro."
- "Add the `caption-pill-karaoke` component from the registry and style it from
  my frame.md."
- "Use `frame-md-launch-storyboard` as the structural reference for this film."

## Replicating a release video
HeyGen open-sources every launch video and posts release notes in
`hyperframes/releases/` (`v0.6.x.md`). When a launch video nails a look you
want: identify the matching folder in `hyperframes-launches/`, point the agent
at it, swap in your `frame.md` and your key-events table, and let it re-skin the
structure. That's how the same prompt-box component became three visually
distinct launch videos.
