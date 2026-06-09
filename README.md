# You Cannot Govern AI with AI — the measurement behind it

A small, offline, reproducible test of one claim: an AI reviewer drawn from the
same model family as the system it checks will approve that system's own errors.
A reviewer from a different company helps, but not enough. A check that uses no
model at all catches what both of them miss.

**Live demo:** open `index.html` (or the published page) and walk through it in about thirty seconds.
**The full argument:** [Siraj, Issue 7 — You Cannot Govern AI with AI](https://www.linkedin.com/newsletters/siraj-7439351927420780544/)

This repository is the evidence behind that issue. The demo is for everyone; the
code is for anyone who wants to check the work.

## The result

Each reviewer judges the same set of answers, where a graph-verified benchmark
already knows which answers are correct. The number that matters is
**false-acceptance**: of the answers that are actually wrong, how many did the
reviewer approve?

| Reviewer | False-acceptance | Catch rate |
|---|---:|---:|
| Same-family AI judge | highest | lowest |
| Different-company AI judge | lower | higher |
| Ground-truth check (no model) | 0% | 100% |

The rows are ordered so that diversity increases downward, and false-acceptance
falls as it does. The non-model check sits at zero by construction, because it
compares the answer to the source rather than to another model's opinion. That
gap between the top row and the bottom is the whole point: the fix is not a
smarter model, it is a different *kind* of check.

The exact figures live in [`results/table.md`](results/table.md), stamped with
their provenance.

## Provenance: illustrative vs. measured

This repo ships with **illustrative** data so it runs the moment you clone it,
with no API keys and no spend. Those numbers are generated deterministically
from declared rates in [`scripts/make_illustrative_fixture.py`](scripts/make_illustrative_fixture.py),
chosen to sit near the range Agus Sudjianto reports in *When the Judge Is Wrong*.
They demonstrate the method. They are not a measurement, and the table says so
every time it prints.

To produce **measured** numbers, run [`src/record.py`](src/record.py) once
against real models (Anthropic and OpenAI) over the FinStructBench benchmark.
It writes a new `run.json` stamped `measured`, and every output upgrades with no
other change. The recorder is the only part of this project that ever touches a
model API.

## Run it (offline, no keys)

```bash
pip install -r requirements.txt
make fixture     # writes the illustrative data/runs/run.json
make score       # writes results/table.{md,csv} and prints the table
make test        # runs the scorer's tests
```

## Record real results (needs keys, once)

```bash
pip install -r requirements-record.txt
export ANTHROPIC_API_KEY=...   OPENAI_API_KEY=...
python -m src.record --instance model_validation --limit 60
make score
```

## How it fits together

```
FinStructBench  ->  generator answers  ->  reviewers judge  ->  scorer  ->  one table
(graph-verified     (a mix of right         (same-family,        (false-
 ground truth)       and wrong)              cross-family,        acceptance
                                             non-model check)     per reviewer)
```

- [`src/score.py`](src/score.py) — the scoring logic. Pure functions, fully tested. This is the part that has to be correct.
- [`src/schema.py`](src/schema.py) — loads a run file; synthesizes the non-model ground-truth row.
- [`src/report.py`](src/report.py) — renders the table to markdown and CSV.
- [`src/record.py`](src/record.py) — calls the models, once, to produce measured data.
- [`index.html`](index.html) — the click-to-run demo. Reads the same verdict format the scorer reads, so the picture and the numbers cannot disagree.

## What this is, and what it is not

It **is** a demonstration that same-lineage AI reviewers share blind spots, that
a different vendor only partly closes the gap, and that a non-model check against
ground truth is what actually recovers independent review.

It is **not**:

- **A quality benchmark of any model.** It measures whether a reviewer catches
  errors, not how good any model is. No model here is being ranked or endorsed.
- **A measurement, in its shipped state.** The default data is illustrative and
  labelled as such. Believe the numbers only when the table reads `measured`.
- **A one-time guarantee.** A control that passes today can drift tomorrow as
  sources go stale and models change underneath it. Verification is point-in-time;
  governing the controls over their life is a separate, organizational job.
- **The whole of governance.** Many high-exposure decisions have no oracle to
  check them against. Verification shrinks the ungoverned surface; it does not
  remove it. What is left needs a named human with the authority to own the call.

A note on reproducibility: model calls are not perfectly deterministic across
providers or versions, so a measured run is a snapshot. Record with pinned model
versions and report across several runs rather than trusting a single number.

## Credit

The ground-truth approach and the benchmark come from Agus Sudjianto and Wingyan
Lau, *FinStructBench*, and the framing from Sudjianto's *When the Judge Is Wrong*
(2026). This project is the operator-side complement: where that work measures
how far a same-distribution judge gets you, this measures how much each kind of
diversity — a different model, then a different mechanism — recovers.

## License

MIT. See [LICENSE](LICENSE).
