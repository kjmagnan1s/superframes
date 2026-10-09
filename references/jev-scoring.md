# Jev scoring in superframes — what it decides, and what it must never decide

All three scripts are optional, advisory tools. None is a required step.

Jev is TypeSafe's System One decision model. It scores, classifies and picks from
lists you hand it. It writes nothing and **it cannot see anything**.

This skill's whole premise is that words get settled before pixels. Jev fits
there and only there: the key-events table, the reuse catalog, and the
anti-pattern list are all text, all enumerated, and all judged the same way over
and over.

## The three scripts

| Script | Serves | Decides | Does NOT |
| --- | --- | --- | --- |
| `scripts/jev_keyevents.py <table.md>` | step 3 | per-scene: does the row earn its place, is it a merge candidate, which narrative slot, does its duration fit that slot's band | pick the densest moment, judge a frame, replace the copy pass |
| `scripts/jev_templates.py --brief "…"` | step 6 | ranks launch folders / registry components by catalog-description fit and re-skin effort | tell you the layout bones are right — open them and look |
| `scripts/jev_audit.py <files…>` | before step 4 (default), optionally again before render | runs the plan against the anti-patterns that are checkable in text | judge whether the RENDER looks like a slide deck |

`scripts/jev.py` is the shared client (stdlib only). It reads `TYPESAFE_API_KEY`
from the environment, or from the macOS Keychain entry of that name.
`python3 scripts/jev.py --selftest` confirms the key and the API.

## Hard boundaries

**The storyboard gate does not move.** A human approves the static keyframes. No
score here is an input to that gate; these scripts run before it, on the words.

**Everything visual stays visual.** The densest moment within a scene, whether a
scene is too busy to read in the stack, contrast, type size, preset picking by
eye, mood boards, studio nudging — none of it goes to Jev. A text score that
appears to answer one of these is answering a different question.

**Jev never writes.** Not a hook, not a line, not a scene description. The copy
pass in step 3 is still a conversation. Jev tells you which row to argue about.

## Thresholds, honestly

- `jev_keyevents.WEAK_FRACTION = 0.75` of the table's median row total. Relative,
  not absolute: on a sample 7-scene table, row totals ran 4.7–8.5, so any fixed
  floor either fires on everything or nothing. The scale depends on how strong
  the table is overall, and the useful question is which rows are weakest *here*.
- `jev_audit` fires at p ≥ 0.55; `jev_templates` has no threshold, it ranks.
- **None of these are backtested.** A threshold earns trust when it is set from
  a shipped result (for example, a take picker's margin set from a finished
  edit). Nothing in this skill has that ground truth yet. Until a few finished videos are compared against what these scripts
  proposed, treat every number as a starting point and every flag as "look at
  this", never "do this".

## Where Jev's confidence lies to you

`confidence` on a `score` question comes back low (0.00–0.41 measured) even when
the answer is obviously right, and `noul` returns it as `null` outright. Gating
on it flags 100% of rows. Use `jev.decisiveness()` for yes/no questions and
compare candidates by margin for rankings. The docstring of
`Jev.unsure_keys` in `scripts/jev.py` has the measured account.

## Cost

$0.042 per million input tokens, output free. Scoring a 7-scene table cost
$0.0002; the whole 11-folder reuse catalog cost $0.0002; the anti-pattern audit
is one call at $0.00003. There is no reason to sample or skip.
