#!/usr/bin/env python3
"""Shortlist which existing template or component to reuse, with Jev.

The mindset this skill is built on: "I try to not make things net-new if I can."
The cost of that mindset is that someone has to read ~14 launch folders and ~50
registry components against the brief every time. That match is a scoring job
over a candidate list that already exists in `references/template-reuse.md`.

Jev reads the one-line characterization of each candidate and the brief. It has
never seen any of these videos, so it can only match on what the catalog SAYS.
Treat the shortlist as "open these four first", never as a decision — the pick
is the layout bones, and bones are judged by eye.

Usage:
    python scripts/jev_templates.py --brief "45s launch video for a CLI that ..."
    python scripts/jev_templates.py --brief-file BRIEF.md --top 6
    python scripts/jev_templates.py --brief "..." --kind components

`--kind` is launches (default), components, blocks, examples, or all.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from jev import Jev, JevError, noul, score  # noqa: E402

CATALOG = Path(__file__).resolve().parent.parent / "references" / "template-reuse.md"

QUESTIONS = {
    "fit": score(
        "How well the candidate matches what this brief needs, judging only from the candidate's "
        "own description",
        ["Wrong kind of thing entirely", "Same medium, wrong character",
         "Close enough to adapt", "Made for exactly this"],
    ),
    "effort": score(
        "How little work it would take to re-skin this candidate for the brief rather than build "
        "net-new",
        ["A rebuild wearing its name", "Heavy surgery",
         "Swap the brand atoms and the copy", "Drop the brief's content straight in"],
    ),
    "over_reach": noul(
        "Would reaching for this candidate pull in heavy effects the brief never asked for?"),
}

WEIGHTS = {"fit": 1.5, "effort": 1.0}
OVER_REACH_PENALTY = 1.0

BULLET = re.compile(r"^\s*[-*]\s+(?P<body>.+)$")
NAMES = re.compile(r"`([^`]+)`")


def parse_catalog(text: str, kind: str) -> dict[str, str]:
    """Pull `name` → description out of the catalog's bullet lists.

    A bullet can name several candidates at once ("`a`, `b`, `c` — feature
    launches"); each gets the shared description, because that is genuinely all
    the catalog says about them.
    """
    headings = {
        "launches": "launch-video library",
        "components": "registry/components",
        "blocks": "registry/blocks",
        "examples": "registry/examples",
    }
    want = None if kind == "all" else headings[kind]
    out: dict[str, str] = {}
    section = ""
    for raw in text.splitlines():
        if raw.startswith("#"):
            section = raw.lower()
            continue
        m = BULLET.match(raw)
        if not m:
            continue
        body = m.group("body")
        scope = section + " " + body.lower()
        if want and want not in scope:
            continue
        names = NAMES.findall(body)
        if not names:
            continue
        desc = NAMES.sub("", body)
        desc = re.sub(r"^[\s,—–-]+", "", desc).strip(" .,—–-")
        for n in names:
            n = n.strip()
            if n and n not in out:
                out[n] = desc or "(the catalog gives no description for this one)"
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Jev reuse shortlist for superframes")
    ap.add_argument("--brief", type=str, default=None)
    ap.add_argument("--brief-file", type=Path, default=None)
    ap.add_argument("--kind", choices=["launches", "components", "blocks", "examples", "all"],
                    default="launches")
    ap.add_argument("--catalog", type=Path, default=CATALOG)
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--json", type=Path, default=None)
    args = ap.parse_args()

    brief = args.brief or (args.brief_file.read_text(encoding="utf-8") if args.brief_file else None)
    if not brief:
        sys.exit("pass --brief or --brief-file")
    if not args.catalog.exists():
        sys.exit(f"no catalog at {args.catalog}")

    cands = parse_catalog(args.catalog.read_text(encoding="utf-8"), args.kind)
    if not cands:
        sys.exit(f"no {args.kind} candidates parsed from {args.catalog}")

    states = {
        name: (f"The brief:\n{brief.strip()}\n\n"
               f"The candidate to judge:\n{name} — {desc}")
        for name, desc in cands.items()
    }

    jev = Jev()
    try:
        scored = jev.batch(states, QUESTIONS, progress=True)
    except JevError as e:
        sys.exit(f"jev unavailable: {e}")

    rows = []
    for name, a in scored.items():
        if jev.missing_keys(a, WEIGHTS):
            continue
        t = jev.weighted(a, WEIGHTS)
        if "over_reach" in a:
            t -= OVER_REACH_PENALTY * float(a["over_reach"].value)
        rows.append({"name": name, "desc": cands[name], "total": round(t, 3),
                     "scores": {k: round(float(v.value), 3) for k, v in a.items()}})
    rows.sort(key=lambda r: r["total"], reverse=True)
    missing = [n for n in cands if n not in scored]

    print(f"\n{len(rows)} {args.kind} candidates scored against the brief\n")
    print(f"{'total':>6} {'fit':>5} {'effort':>7} {'reach':>6}  candidate")
    for r in rows[:args.top]:
        s = r["scores"]
        print(f"{r['total']:>6.2f} {s.get('fit', 0):>5.2f} {s.get('effort', 0):>7.2f} "
              f"{s.get('over_reach', 0):>6.2f}  {r['name']}")
        print(f"                              {r['desc'][:76]}")
    if len(rows) > args.top:
        print(f"\n({len(rows) - args.top} more in --json; raise --top to see them)")
    if missing:
        print(f"\n⚠️ {len(missing)} candidates failed to score: {', '.join(missing[:6])}")
    print("\nOpen the top few and look. Jev matched catalog DESCRIPTIONS, not videos —")
    print("the pick is the layout bones, and bones are judged by eye.")
    print(f"\n{jev.usage_line()}")

    if args.json:
        args.json.write_text(json.dumps(
            {"brief": brief, "kind": args.kind, "weights": WEIGHTS,
             "candidates": rows, "unscored": missing, "jev": jev.usage_dict()}, indent=2))
        print(f"wrote {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
