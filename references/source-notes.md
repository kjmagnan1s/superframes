# Source notes — where superframes comes from

This skill distills two primary sources (captured 2026-06-23) plus the HeyGen
open-source repos. Kept here for provenance so future edits can trace a claim
back to its origin.

## Source 1 — builder-workflow webinar
"[HeyGen] Inside the builder workflow: How we use HyperFrames at HeyGen"
(HeyGen webinar, captured 2026-06-23).

Confirmed facts:
- HyperFrames = HTML-based video creation/editing layer for AI agents. Agents
  are natively better at HTML than React/Remotion; they can "see" the HTML.
- Setup before prompt: dedicated project folder with ALL assets upfront (logo,
  Figma, brand colors, website screenshots, exact messaging). More assets =
  closer aesthetic match on first pass.
- `design.md` describes a brand system, built for web agents. `frame.md` is the
  HyperFrames-specific variant optimized for video/motion. Generate at
  **hyperframes.dev/design**.
- Storyboard first (brain dump → scene plan). Refine COPY at the storyboard
  stage, not later in animation.
- Request a static HTML keyframe per scene before animating. Agent builds in
  1-2 min; lock the aesthetic before any rendering.
- Reuse compositions across projects — all videos are code. HeyGen open-sourced
  10-15 launch videos as referenceable templates; 50+ pre-built components.
- Always open the local preview studio: `npx @hyperframes latest preview`. Drag
  elements, edit text/font/color/motion without re-prompting. Saves tokens.
- Recommended starting point: "Turn this website into a video."
- Launched recently: PR-to-video, Music-to-video, cloud rendering. Coming:
  keyframes editor in studio, ChatGPT connector, slides-based product.

## Source 2 — YouTube interview (videoId iqb5Rd6KKr8)
Hosts/guests: Peter (host), Ben (VP Product Eng, HeyGen), Jake (PMM, HyperFrames).
Full transcript: pulled via ScrapeCreators, ~7k words. Speaker labels inferred.

Adds / sharpens:
- Jake's manual launch workflow (when there is no website to start from):
  1. New project folder → drop in context (e.g. a README about the feature).
  2. Add assets: UI screenshots + reference examples he likes ("I see a couple
     frames of this video already in my head, here they are").
  3. Add exactly ONE aesthetic source (design.md OR frame.md).
  4. Point agent at folder + design source → ask for a "table of key events"
     (scene-by-scene markdown). Refine the TEXT COPY here.
  5. Build a `storyboard.html` — one static frame per scene, the most visually
     dense moment, using references pulled from launch videos + the design
     system. Align on aesthetic fast before the (slow) full composition.
  6. Promote: "turn this into a full HyperFrames video and pull it up in the
     HyperFrames studio."
  7. Iterate in the studio; UI edits become code so the agent sees the diff.
- frame.md generation on hyperframes.dev/design: drop your design.md, the agent
  reformats it for video; or pick a near-match template, fine-tune palette /
  typography, preview, download the "design pack" (a frame.md).
- Reuse: "I try to not make things net new." Reused the same Claude prompt-box
  component across 3 launch videos with different frame.mds. Point the agent at
  the open-source repo; don't read the code yourself.
- Model choice: top-tier frontier model for best quality; Gemini for
  quality-to-cost (HeyGen's internal agent runs on Gemini).
- Audio: free local TTS model auto-downloads; optionally connect HeyGen /
  ElevenLabs.
- Media: can play an existing clip inside a composition; a strong model can
  auto-clip an MP4 to a timestamp range.
- Export: MP4 / MOV / WebM. Transparent WebM to composite motion graphics into
  Premiere etc. Can also export as a website (interactive player). (This skill
  renders transparent output as MOV instead: WebM often loses the alpha channel.)
- Anti-patterns: "PPT video" for launches (no one watches past 5s); designing a
  video like a webpage (spatial vs temporal aesthetics); hand-editing the raw
  generated code; skipping the storyboard; building net-new every time; adding
  more than one aesthetic source.

### Transcription caveats (flagged by the extractor — do not treat as verbatim)
- Garbled product/model names: "Pop/Cloud/Point Code" = Claude Code; "Haijan" =
  HeyGen; "Stable 5 / Fable 5 / GPT 5.5" = some top-tier model (treat as "use a
  top frontier model"); "design pack/scale" = skill/design pack.
- Clean domain in transcript: **hyperframes.dev/design**. Root domain otherwise
  ambiguous (`.ai` vs `.dev`).
- The interview did NOT state `npx`/`init`/`lint`/`render`/`tts` syntax — only
  the studio "Export" and "HyperFrames preview." CLI syntax in this skill comes
  from the installed hyperframes-cli skill, not the transcript.

## Source 3 — HeyGen open-source repos (github.com/heygen-com)
Key repos (clone any locally for reference):
- `hyperframes` (30.6k★) — the framework: skills, component catalog, packages.
- `hyperframes-launches` — open-source compositions behind HeyGen launch videos
  (the template gold; small repo).
- `skills` — HeyGen agent skills (avatar + video production).
- `website-to-hyperframes-demo`, `hyperframes-vercel-template`,
  `hyperframes-launch-video`.
- Community: `tonbistudio/hyperframes-prompts`, `nateherkai/hyperframes-student-kit`.
