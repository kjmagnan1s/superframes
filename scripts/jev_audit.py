#!/usr/bin/env python3
"""Audit a plan against this skill's own anti-patterns, with Jev.

SKILL.md lists six named ways videos come out weak, and prompt-craft.md lists
the anti-PPT discipline. Nothing in the workflow ever runs a draft against
either list — they are the most obviously unexploited rubric here. Each item is
a yes/no question about a plan, which is exactly what `noul` answers.

Give it the key-events table, or the brief, or both. It reads text: it cannot
tell you whether the RENDER looks like a slide deck, only whether the PLAN
reads like one. The two visual items in the list are named and skipped rather
than faked.

Usage:
    python scripts/jev_audit.py key-events.md
    python scripts/jev_audit.py BRIEF.md key-events.md --threshold 0.55
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from jev import Jev, JevError, noul  # noqa: E402

# SKILL.md § Anti-patterns, plus the text-checkable half of prompt-craft.md
# § The anti-PPT discipline. Each is phrased so YES means the plan has the
# problem.
CHECKS = {
    "ppt_video": (
        "Does this plan read like a slide deck — each scene dumping its whole content at once "
        "and then holding still, instead of revealing across its duration?",
        "The 'PPT video'. Build the whole shot; reveal across the full duration."),
    "spatial_not_temporal": (
        "Is this plan laid out like a web page — sections stacked by topic — rather than as a "
        "sequence in time where each beat sets up the next?",
        "Designing a video like a web page. Video is temporal, not spatial."),
    "many_worlds": (
        "Does this plan invent a new visual world for nearly every beat, instead of one world "
        "modulated across the piece?",
        "More than one aesthetic source / a new world every beat. One world, modulated."),
    "net_new": (
        "Does this plan describe building effects and scenes from scratch that an existing launch "
        "video or registry component would plainly already cover?",
        "Building net-new every time. Look in the launches and the registry first."),
    "faked_proof": (
        "Does this plan show fabricated proof — invented logs, mock job pills, made-up numbers, a "
        "product that does not do what the frame implies?",
        "Not diegetic. Real terminal logs, real chat, real captures. Don't fake the product."),
    "narration_on_screen": (
        "Does this plan put sentences of narration on screen as visible text, rather than short "
        "hero words, stats or commands?",
        "Visible text is short motion-graphics copy, never a sentence from the narration."),
    "no_hero": (
        "Do any scenes in this plan lack a single clear hero element, putting several competing "
        "focal points in one frame?",
        "One hero per frame."),
    "flat_rhythm": (
        "Does this plan give every beat about the same length, instead of opening fast, letting the "
        "demo breathe and letting the ending land?",
        "Vary the rhythm. Hooks short, hero scenes long, closers land."),
    "title_card_open": (
        "Does this plan open on a title card or a logo rather than inside a real interface "
        "mid-action?",
        "Open inside a real interface mid-action, not on a title card."),
    "no_payoff": (
        "Does this plan end without a concrete result — a number, a finished state, a literal "
        "command the viewer can run?",
        "Proof / payoff and a literal CTA command line."),
}

# Named and deliberately NOT asked: these need eyes on a frame.
VISUAL_ONLY = [
    "Skipping the storyboard — a static keyframe per scene, approved in the browser. "
    "No text score substitutes for the gate.",
    "Hand-editing the raw generated code, and whether the frames actually READ — contrast, "
    "type size, density, legibility at playback size.",
]


def main() -> int:
    ap = argparse.ArgumentParser(description="Jev anti-pattern audit for superframes")
    ap.add_argument("files", type=Path, nargs="+", help="brief and/or key-events table")
    ap.add_argument("--threshold", type=float, default=0.55)
    args = ap.parse_args()

    blobs = []
    for f in args.files:
        if not f.exists():
            sys.exit(f"no such file: {f}")
        blobs.append(f"--- {f.name} ---\n{f.read_text(encoding='utf-8')}")
    plan = "\n\n".join(blobs)

    jev = Jev()
    # One state, many questions — this is a whole-plan read, not a per-row pass,
    # so it is a single call.
    try:
        answers = jev.ask(plan, {k: noul(q) for k, (q, _) in CHECKS.items()})
    except JevError as e:
        sys.exit(f"jev unavailable: {e}")

    rows = sorted(
        ((k, float(v.value), jev.decisiveness(v)) for k, v in answers.items()),
        key=lambda r: r[1], reverse=True)
    hits = [r for r in rows if r[1] >= args.threshold]

    print(f"\nanti-pattern audit of {', '.join(f.name for f in args.files)}")
    print(f"{len(hits)} of {len(rows)} checks fired at p ≥ {args.threshold:.2f}\n")
    for k, p, conf in rows:
        mark = "⚠️" if p >= args.threshold else "  "
        print(f" {mark} {p:.2f}  {k}")
        if p >= args.threshold:
            print(f"        → {CHECKS[k][1]}")
    missing = [k for k in CHECKS if k not in answers]
    if missing:
        print(f"\n⚠️ these checks did not score and were NOT run: {', '.join(missing)}")
    print("\nNot checked here — these need eyes on a frame:")
    for v in VISUAL_ONLY:
        print(f"  · {v}")
    print(f"\n{jev.usage_line()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
