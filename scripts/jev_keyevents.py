#!/usr/bin/env python3
"""Score a key-events table with Jev — before a single pixel is animated.

Step 3 of this skill produces a markdown table, one row per scene: what we SAY
and a one-line note on what's ON SCREEN. Then step 3 says refine only the copy,
and push back — "cut scene 5, merge it into 4". That push-back is the same
judgment repeated over 8-10 rows, which is what Jev is for.

What it scores, per row:
  - does the row earn its place, or is it connective tissue
  - is it a near-duplicate of its neighbour (merge candidate)
  - which narrative-skeleton slot it occupies (prompt-craft.md § The narrative
    skeleton — hook / problem / turn / reveal / proof / closer)
  - whether its planned duration fits that slot's pacing band

It writes nothing and it has seen nothing. The storyboard approval gate is
unchanged: a human approves the static keyframes in a browser, and no score
here substitutes for that.

Input: the key-events markdown table. Any pipe table works; the script finds the
columns that look like scene / say / on-screen / duration.

Usage:
    python scripts/jev_keyevents.py key-events.md
    python scripts/jev_keyevents.py key-events.md --total 45 --json out.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from jev import Jev, JevError, choice, noul, score  # noqa: E402

# prompt-craft.md § The narrative skeleton
SLOTS = {
    "hook": "Hook or cold open — opens inside a real interface mid-action",
    "problem": "Problem or diagnosis — makes the pain visceral and diegetic",
    "turn": "The turn — one thesis line, one hero per frame",
    "reveal": "Product reveal and how-it-works — the real flow, real UI, real output",
    "proof": "Proof or payoff — the result, often a number",
    "closer": "Closer or endcard — real logo and a literal CTA",
}

# prompt-craft.md § Pacing (real numbers), as (low, high) seconds per slot.
BANDS = {
    "hook": (4.0, 5.0),
    "problem": (2.0, 7.0),
    "turn": (1.0, 7.0),
    "reveal": (10.0, 13.0),
    "proof": (2.0, 7.0),
    "closer": (2.7, 8.0),
}

QUESTIONS = {
    "earns_place": score(
        "How much the marked scene earns its place in a 30-60 second video",
        ["Cut it, nothing is lost", "Connective tissue between two real scenes",
         "Carries real content", "The video does not work without it"],
    ),
    "one_idea": score(
        "How well the marked scene holds exactly one idea",
        ["It is three scenes wearing one row", "Two ideas competing",
         "One idea with a tangent", "Exactly one idea, one hero"],
    ),
    "diegetic": score(
        "How much the marked scene shows a real thing happening versus telling the viewer about it",
        ["A bulleted list of claims", "A title card with words",
         "A described interface", "A real interface mid-action"],
    ),
    "merge_with_previous": noul(
        "Would the marked scene be stronger merged into the scene before it, because the two make "
        "one point?"),
    "slot": choice("Which slot of the narrative skeleton the marked scene occupies", SLOTS),
}

WEIGHTS = {"earns_place": 1.5, "one_idea": 1.0, "diegetic": 1.0}

# Weak rows are flagged RELATIVE to the rest of the table, not against an
# absolute number. Measured on a sample 7-scene table, totals landed between
# 4.71 and 8.46 — an absolute floor either fires on everything or nothing,
# because the scale depends on how strong the table is overall. What the skill
# actually wants to know is which rows are the weakest ONES HERE. A flag means
# "argue about this row", never "cut this row".
WEAK_FRACTION = 0.75  # of the median row total

SPLIT = re.compile(r"\s*\|\s*")
DUR = re.compile(r"(\d+(?:\.\d+)?)\s*s\b")


def parse_table(text: str) -> list[dict]:
    """Pull rows out of the first markdown pipe table with 2+ columns."""
    rows, header = [], None
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c for c in SPLIT.split(line.strip().strip("|"))]
        if set("".join(cells)) <= set("-: "):
            continue
        if header is None:
            header = [c.strip().lower() for c in cells]
            continue
        rows.append(dict(zip(header, [c.strip() for c in cells])))
    if not rows:
        raise SystemExit("no markdown table rows found — pass the key-events table")
    return rows


def pick(row: dict, *names: str) -> str:
    for n in names:
        for k, v in row.items():
            if n in k:
                return v
    return ""


def main() -> int:
    ap = argparse.ArgumentParser(description="Score a key-events table with Jev")
    ap.add_argument("table", type=Path)
    ap.add_argument("--total", type=float, default=None,
                    help="intended total runtime in seconds, for the pacing check")
    ap.add_argument("--json", type=Path, default=None)
    args = ap.parse_args()

    rows = parse_table(args.table.read_text(encoding="utf-8"))
    states = {}
    for i, r in enumerate(rows):
        say = pick(r, "say", "vo", "narration", "copy", "line")
        onscreen = pick(r, "on screen", "on-screen", "visual", "screen")
        prev = pick(rows[i - 1], "say", "vo", "narration", "copy", "line") if i else "(none)"
        # Position is a strong cue for the narrative slot and Jev is weak at
        # indirection, so state it outright rather than making it infer ordering.
        states[f"r{i:02d}"] = (
            f"This is scene {i + 1} of {len(rows)} in a short video.\n"
            f"Previous scene said: {prev}\n"
            f">>> THE MARKED SCENE says: {say}\n"
            f">>> and on screen: {onscreen}")

    jev = Jev()
    try:
        scored = jev.batch(states, QUESTIONS, progress=True)
    except JevError as e:
        sys.exit(f"jev unavailable: {e}")

    out = []
    for i, r in enumerate(rows):
        a = scored.get(f"r{i:02d}", {})
        if jev.missing_keys(a, WEIGHTS):
            out.append({"row": i + 1, "raw": r, "total": None,
                        "note": "did not score — read this row yourself"})
            continue
        total = jev.weighted(a, WEIGHTS)
        slot = a["slot"].value if "slot" in a else None
        dur_txt = pick(r, "dur", "length", "time", "sec")
        m = DUR.search(dur_txt) or DUR.search(pick(r, "on screen", "visual"))
        dur = float(m.group(1)) if m else None
        pacing = None
        if slot in BANDS and dur is not None:
            lo, hi = BANDS[slot]
            if dur < lo:
                pacing = f"short for a {slot} ({dur:.1f}s vs {lo:.1f}-{hi:.1f}s)"
            elif dur > hi:
                pacing = f"long for a {slot} ({dur:.1f}s vs {lo:.1f}-{hi:.1f}s)"
        flags = []
        if float(a.get("merge_with_previous", type("x", (), {"value": 0})).value) >= 0.6:
            flags.append("merge candidate")
        if jev.unsure_keys(a, ["slot"]):
            flags.append("slot unclear")
        if pacing:
            flags.append(pacing)
        out.append({
            "row": i + 1, "raw": r, "slot": slot, "duration": dur,
            "total": round(total, 3),
            "scores": {k: (v.value if v.kind == "choice" else round(float(v.value), 3))
                       for k, v in a.items()},
            "flags": flags,
        })

    # Relative weakness pass, now that every row has a total.
    totals = sorted(o["total"] for o in out if o.get("total") is not None)
    median = totals[len(totals) // 2] if totals else 0.0
    for o in out:
        if o.get("total") is not None and o["total"] < WEAK_FRACTION * median:
            o["flags"].insert(0, f"weakest rows here (vs median {median:.2f}) — argue about it")

    seen_slots = [o.get("slot") for o in out]
    missing = [s for s in SLOTS if s not in seen_slots]

    print(f"\n{len(out)} scenes scored from {args.table}")
    print(f"{'#':>3} {'slot':<9} {'score':>6}  flags / line")
    for o in out:
        line = pick(o["raw"], "say", "vo", "narration", "copy", "line")[:54]
        tot = f"{o['total']:.2f}" if o.get("total") is not None else "—"
        print(f"{o['row']:>3} {str(o.get('slot') or '?'):<9} {tot:>6}  "
              f"{('; '.join(o.get('flags') or [])) or '—'}")
        print(f"                       {line}")
    if missing:
        print(f"\nnarrative skeleton — no scene occupies: {', '.join(missing)}")
        print("  (a missing slot is a question, not an error: not every piece needs all six)")
    if args.total and len(out) not in range(8, 11):
        print(f"\nscene count is {len(out)}; prompt-craft.md § Pacing wants 8-10 top-level scenes")
    print("\nThis is a shortlist to argue with. Refine the COPY here, per the skill —")
    print("and the storyboard gate still runs on static keyframes, judged by a human.")
    print(f"\n{jev.usage_line()}")

    if args.json:
        args.json.write_text(json.dumps(
            {"table": str(args.table), "weights": WEIGHTS, "weak_fraction": WEAK_FRACTION,
             "scenes": out, "missing_slots": missing, "jev": jev.usage_dict()}, indent=2))
        print(f"wrote {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
