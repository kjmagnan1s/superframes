# superframes

A pre-production **workflow** skill for [HyperFrames](https://github.com/heygen-com/hyperframes),
the HTML-based video engine for AI agents by HeyGen. `superframes` is the process
layer in front of authoring: it takes you from a brand and a brief to a locked
storyboard (assets → one frame.md → key-events table → static keyframes →
template reuse → studio iteration), then hands off to HyperFrames to author the
composition.

## Built on HyperFrames

This skill distills the workflow the HeyGen team uses — from their public
builder-workflow webinar, their launch-video interview, and their open-source
repos — into a repeatable Claude Code skill. All of the underlying engine,
concepts, and templates are HyperFrames' work. **Full credit to the HyperFrames /
HeyGen team.**

- HyperFrames: https://github.com/heygen-com/hyperframes
- Launch-video templates: https://github.com/heygen-com/hyperframes-launches

## The skill stack

- **`frame-md`** — build the per-brand design system once (one `frame.md`, reused
  across every video): https://github.com/heygen-com (see the `frame-md` repo).
- **`superframes`** — this skill: the per-video production workflow.
- **`hyperframes` / `hyperframes-cli`** — HeyGen's authoring engine + CLI that
  this workflow hands off to.

Scope: `frame-md` runs once per brand; `superframes` runs once per video and
consumes the brand's `frame.md`; `hyperframes` authors the composition.

## Install

Copy this folder into `~/.claude/skills/superframes/` (or install it as a plugin
skill). Invoke it when you start a HyperFrames video.

## Credit & license

Engine, concepts, tooling, and templates: **HyperFrames / HeyGen**
(https://github.com/heygen-com). This repo is original workflow documentation
describing how to use their public, open-source system, provided as-is.
