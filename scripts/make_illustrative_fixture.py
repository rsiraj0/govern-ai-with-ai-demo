"""
Generates a clearly-labelled ILLUSTRATIVE run so the repo and the demo work
before anyone has API keys. The numbers are not measured. They are produced
deterministically from the rates declared below, chosen to sit near the range
Sudjianto reports in "When the Judge Is Wrong" (false-acceptance roughly a
third for a same-family judge with the source in hand).

Replace this with real output by running:  python -m src.record

Run:  python scripts/make_illustrative_fixture.py
"""

import json
import random
from pathlib import Path

# ---- declared illustrative rates (NOT measurements) -----------------------
N = 60
GENERATOR_ACCURACY = 0.58          # share of answers that are correct

SAME_FAMILY_FAR = 0.32             # accepts ~1/3 of wrong answers
SAME_FAMILY_FRR = 0.05             # rarely rejects a correct one

CROSS_FAMILY_FAR = 0.20            # a different lab helps, but not enough
CROSS_FAMILY_FRR = 0.07

SEED = 7
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "runs" / "run.json"


def main() -> None:
    rng = random.Random(SEED)
    items = []
    for i in range(N):
        qid = f"q{i+1:03d}"
        truth_correct = rng.random() < GENERATOR_ACCURACY

        if truth_correct:
            same = rng.random() >= SAME_FAMILY_FRR      # usually accept a correct answer
            cross = rng.random() >= CROSS_FAMILY_FRR
        else:
            same = rng.random() < SAME_FAMILY_FAR       # sometimes accept a wrong answer
            cross = rng.random() < CROSS_FAMILY_FAR

        items.append({
            "qid": qid,
            "truth_correct": truth_correct,
            "verdicts": {"same_family": same, "cross_family": cross},
        })

    run = {
        "provenance": "illustrative",
        "recorded_at": None,
        "benchmark": "FinStructBench (illustrative stand-in; not a real run)",
        "generator": {"model": "illustrative", "overall_accuracy": GENERATOR_ACCURACY},
        "judges": ["same_family", "cross_family"],
        "judge_models": {"same_family": "illustrative", "cross_family": "illustrative"},
        "items": items,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(run, indent=2))
    print(f"wrote {OUT} with {N} illustrative items (seed={SEED})")


if __name__ == "__main__":
    main()
