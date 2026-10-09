"""Shared Jev (TypeSafe System One) client.

Self-contained and stdlib-only, so this skill works without any other skill
or package on disk.

Jev is a decision model. It scores, classifies and picks from lists you supply.
It does NOT write text and it cannot see images. Every frame-level or visual
check in this skill stays with a vision model — see `references/jev-scoring.md`.

Design contract (do not break it):
  - One scored question per criterion. Never ask Jev for one holistic verdict.
  - Weights are applied HERE, in code, not by the model.
  - Anything under the confidence threshold routes to the user, it does not
    silently pick a side.

API: POST https://api.typesafe.ai/v1/systemone
Key: TYPESAFE_API_KEY env var, or the macOS Keychain entry of that name.
Pricing: $0.042 / M input tokens, output free. A call per phrase on a 3-minute
video costs a fraction of a cent, so batch nothing for cost reasons.

Usage as a library:

    from jev import Jev, score, noul, choice

    jev = Jev()
    questions = {
        "clean": score("How cleanly this line is delivered",
                       ["Broken, restarted mid-word", "Stumbles but finishes",
                        "Minor filler", "Clean and confident"]),
        "is_false_start": noul("Does this line abandon itself before finishing the thought?"),
    }
    results = jev.batch({"p1": "text of phrase one", "p2": "..."}, questions)
    print(results["p1"]["clean"].value, results["p1"]["clean"].confidence)
    print(jev.usage_line())

Self-test:
    python3 scripts/jev.py --selftest
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable

URL = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-latest"
INPUT_COST_PER_M = 0.042

# Below this, the call is not ours to make. Route the item to the user.
# NOT an accuracy claim: TypeSafe's own docs say thresholds must be evaluated
# on your own data, and low confidence often means acceptable alternatives
# split the probability mass. Backtest before trusting a number here.
DEFAULT_CONFIDENCE_FLOOR = 0.70


# --------------------------------------------------------------------------
# question builders
# --------------------------------------------------------------------------

def score(instructions: str, criteria: list[str]) -> dict:
    """An ordered ladder, worst first. 2-6 rungs. Returns a float in 0..len-1."""
    if not 2 <= len(criteria) <= 6:
        raise ValueError(f"score ladders want 2-6 rungs, got {len(criteria)}")
    return {"type": "score", "instructions": instructions, "criteria": list(criteria)}


def noul(instructions: str) -> dict:
    """A yes/no question. Returns a probability-ish float in 0..1."""
    return {"type": "noul", "instructions": instructions}


def choice(instructions: str, options: dict[str, str]) -> dict:
    """Pick one label. `options` maps label -> what that label means."""
    if len(options) < 2:
        raise ValueError("choice wants at least 2 options")
    return {"type": "choice", "instructions": instructions, "criteria": dict(options)}


# --------------------------------------------------------------------------
# results
# --------------------------------------------------------------------------

@dataclass
class Answer:
    key: str
    kind: str
    value: Any
    confidence: float | None
    probabilities: Any = None

    @property
    def sure(self) -> bool:
        return self.confidence is not None and self.confidence >= DEFAULT_CONFIDENCE_FLOOR

    def __float__(self) -> float:
        return float(self.value)


@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0
    calls: int = 0
    failures: int = 0
    seconds: float = 0.0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def add(self, u: dict) -> None:
        with self._lock:
            self.input_tokens += u.get("input_tokens", 0) or 0
            self.output_tokens += u.get("output_tokens", 0) or 0
            self.calls += 1

    def fail(self) -> None:
        with self._lock:
            self.failures += 1

    @property
    def cost(self) -> float:
        return self.input_tokens / 1_000_000 * INPUT_COST_PER_M


# --------------------------------------------------------------------------
# client
# --------------------------------------------------------------------------

class JevError(RuntimeError):
    pass


def _keychain_key() -> str:
    env = os.environ.get("TYPESAFE_API_KEY")
    if env:
        return env.strip()
    r = subprocess.run(
        ["security", "find-generic-password", "-s", "TYPESAFE_API_KEY", "-w"],
        capture_output=True, text=True,
    )
    key = r.stdout.strip()
    if not key:
        raise JevError(
            "no TYPESAFE_API_KEY. Expected the macOS Keychain entry:\n"
            "  security find-generic-password -s TYPESAFE_API_KEY -w\n"
            "or the TYPESAFE_API_KEY env var."
        )
    return key


class Jev:
    def __init__(self, key: str | None = None, workers: int = 8,
                 retries: int = 2, timeout: int = 60,
                 confidence_floor: float = DEFAULT_CONFIDENCE_FLOOR):
        self.key = key or _keychain_key()
        self.workers = workers
        self.retries = retries
        self.timeout = timeout
        self.confidence_floor = confidence_floor
        self.usage = Usage()

    # -- one call -----------------------------------------------------------

    def ask(self, state: str, questions: dict[str, dict]) -> dict[str, Answer]:
        """One state blob, N questions. Raises JevError after retries."""
        body = json.dumps({"state": state, "model": MODEL, "questions": questions}).encode()
        last = ""
        for attempt in range(self.retries + 1):
            req = urllib.request.Request(URL, data=body, headers={
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json",
            })
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    payload = json.load(r)
                break
            except urllib.error.HTTPError as e:
                detail = ""
                try:
                    detail = e.read().decode()[:400]
                except Exception:
                    pass
                last = f"HTTP {e.code} {detail}"
                # 4xx other than 429 will not get better by trying again
                if e.code != 429 and 400 <= e.code < 500:
                    self.usage.fail()
                    raise JevError(last) from e
            except Exception as e:  # timeouts, connection resets
                last = repr(e)
            if attempt < self.retries:
                time.sleep(1.5 * (attempt + 1))
        else:
            self.usage.fail()
            raise JevError(f"jev call failed after {self.retries + 1} tries: {last}")

        self.usage.add(payload.get("usage", {}) or {})
        return self._parse(payload, questions)

    def _parse(self, payload: dict, questions: dict[str, dict]) -> dict[str, Answer]:
        out: dict[str, Answer] = {}
        answers = payload.get("answers", {}) or {}
        for key, spec in questions.items():
            a = answers.get(key)
            if a is None:
                continue
            kind = spec["type"]
            value = a.get(kind, a.get("score", a.get("noul", a.get("choice"))))
            out[key] = Answer(
                key=key, kind=kind, value=value,
                confidence=a.get("confidence"),
                probabilities=a.get("probabilities"),
            )
        return out

    # -- many calls ---------------------------------------------------------

    def batch(self, states: dict[str, str], questions: dict[str, dict],
              on_error: Callable[[str, Exception], None] | None = None,
              progress: bool = False) -> dict[str, dict[str, Answer]]:
        """Same question set over many states, in parallel. Keys are preserved.
        Items that fail are simply absent from the result — callers must treat a
        missing key as "route to the user", never as a default answer."""
        results: dict[str, dict[str, Answer]] = {}
        lock = threading.Lock()
        t0 = time.time()
        done = 0
        total = len(states)

        def run(item: tuple[str, str]) -> None:
            nonlocal done
            name, state = item
            try:
                r = self.ask(state, questions)
            except Exception as e:
                if on_error:
                    on_error(name, e)
                else:
                    print(f"  jev FAIL {name}: {e}", file=sys.stderr)
                return
            with lock:
                results[name] = r
                done += 1
                if progress and (done % 10 == 0 or done == total):
                    print(f"  jev {done}/{total}", file=sys.stderr)

        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            list(pool.map(run, states.items()))
        self.usage.seconds += time.time() - t0
        return results

    # -- weighting ---------------------------------------------------------

    def weighted(self, answers: dict[str, Answer], weights: dict[str, float]) -> float:
        """Apply weights in code. Missing answers contribute nothing, which is
        why `missing_keys` exists — check it before you trust the total."""
        return sum(float(answers[k].value) * w for k, w in weights.items() if k in answers)

    @staticmethod
    def missing_keys(answers: dict[str, Answer], weights: dict[str, float]) -> list[str]:
        return [k for k in weights if k not in answers]

    def unsure_keys(self, answers: dict[str, Answer],
                    keys: Iterable[str] | None = None,
                    include_scores: bool = False) -> list[str]:
        """Which answers are too soft to act on.

        `score` answers are EXCLUDED by default, and that is deliberate.
        Measured on a shipped video project, Jev returns
        confidences of 0.0-0.36 on score questions whose values are obviously
        right (a false start scored 0.08 for completeness against 1.84 for its
        clean sibling). Confidence on a continuous score is not comparable to
        confidence on a label, so gating a ranking on it flags 100% of cases
        and the tool stops being useful. For a ranking, the decision-confidence
        signal is the MARGIN between the top two candidates — compute that at
        the call site. The floor here is for `noul` and `choice`, where the
        model is picking between named options and the number means something.
        """
        keys = list(keys) if keys is not None else list(answers)
        out = []
        for k in keys:
            if k not in answers:
                out.append(k)
                continue
            a = answers[k]
            if a.kind == "score" and not include_scores:
                continue
            conf = self.decisiveness(a)
            if conf is None or conf < self.confidence_floor:
                out.append(k)
        return out

    @staticmethod
    def decisiveness(a: Answer) -> float | None:
        """How firmly an answer commits, on 0..1.

        The API returns `confidence` for `choice` but leaves it null on `noul`
        (observed against jev-latest, 2026-09-19). For a yes/no the commitment
        IS the distance from the coin flip, so read it off the probability:
        0.91 and 0.09 are both decisive, 0.52 is not. Without this, every noul
        looks unsure and the ask-flag fires on everything."""
        if a.confidence is not None:
            return a.confidence
        if a.kind == "noul" and a.value is not None:
            return abs(float(a.value) - 0.5) * 2
        return None

    # -- reporting ---------------------------------------------------------

    def usage_line(self) -> str:
        u = self.usage
        return (f"jev: {u.calls} calls, {u.failures} failed, {u.input_tokens} input tokens, "
                f"${u.cost:.6f}, {u.seconds:.1f}s")

    def usage_dict(self) -> dict:
        u = self.usage
        return {"calls": u.calls, "failures": u.failures, "input_tokens": u.input_tokens,
                "output_tokens": u.output_tokens, "cost_usd": round(u.cost, 6),
                "seconds": round(u.seconds, 2), "model": MODEL,
                "confidence_floor": self.confidence_floor}


def write_result(path, payload: dict, jev: Jev | None = None) -> None:
    """Every Jev helper writes a JSON sidecar in the same shape: its own payload
    plus a `jev` usage block, so a session can account for the spend."""
    from pathlib import Path
    if jev is not None:
        payload = {**payload, "jev": jev.usage_dict()}
    Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")


# --------------------------------------------------------------------------
# self-test
# --------------------------------------------------------------------------

def _selftest() -> int:
    jev = Jev()
    qs = {
        "clean": score("How cleanly this line of spoken narration is delivered",
                       ["Abandoned mid-word", "Stumbles but finishes",
                        "Minor filler", "Clean and confident"]),
        "is_false_start": noul("Does this line abandon itself before finishing the thought?"),
        "beat": choice("Which beat of a short video this line belongs to", {
            "hook": "An opening line built to stop the scroll",
            "setup": "Framing or context before the payoff",
            "payoff": "The concrete result or demonstration",
            "cta": "A closing ask, e.g. follow me",
        }),
    }
    states = {
        "false_start": "Software is— software, uh, software is",
        "clean_hook": "Ninety percent of what a web agent does is completely wasted.",
        "cta": "If that was useful, follow me for more.",
    }
    res = jev.batch(states, qs)
    ok = True
    for name in states:
        if name not in res:
            print(f"FAIL: no answer for {name}")
            ok = False
            continue
        a = res[name]
        print(f"{name:<14} clean={float(a['clean'].value):.2f} "
              f"false_start={float(a['is_false_start'].value):.2f} "
              f"beat={a['beat'].value} conf={a['beat'].confidence}")
    print(jev.usage_line())
    if ok:
        # sanity, not accuracy: the obvious false start should out-score the clean hook
        fs = float(res["false_start"]["is_false_start"].value)
        ch = float(res["clean_hook"]["is_false_start"].value)
        print(f"\nsanity: false_start {fs:.2f} vs clean_hook {ch:.2f} -> "
              f"{'OK' if fs > ch else 'SUSPECT (check the ladders before trusting output)'}")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print(__doc__)
