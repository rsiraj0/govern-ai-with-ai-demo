"""
record.py  --  the ONLY part of this project that calls model APIs.

It runs once, produces data/runs/run.json, and then never needs to run again:
the scorer and the web demo both replay that file offline. Until someone runs
this, the repo ships a clearly-labelled illustrative fixture instead.

What it does:
  1. Loads questions and graph-verified ground truth from FinStructBench.
  2. Asks a GENERATOR model to answer each question (a deliberate mix of right
     and wrong, exactly what we want to test against).
  3. Asks two JUDGE models to accept or reject each answer:
       - same_family : same lab/family as the generator
       - cross_family: a different lab's model
  4. Marks each answer correct/incorrect using the FinStructBench graph baseline.
  5. Writes run.json with provenance = "measured".

Requirements (install only when you actually record):
    pip install -r requirements-record.txt
    export ANTHROPIC_API_KEY=...    OPENAI_API_KEY=...

Usage:
    python -m src.record --instance model_validation --limit 60 --out data/runs/run.json

This file is intentionally written to fail loudly and early if keys or packages
are missing, so it is obvious what is needed. No network call is made on import.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

# Model identifiers are read from the environment so the recorder does not hard-code
# a specific version. Set these to the exact models you want on record.
GENERATOR_MODEL = os.environ.get("GENERATOR_MODEL", "claude-sonnet-4")
SAME_FAMILY_JUDGE = os.environ.get("SAME_FAMILY_JUDGE", "claude-opus-4-6")     # same family as generator
CROSS_FAMILY_JUDGE = os.environ.get("CROSS_FAMILY_JUDGE", "gpt-5")             # different lab

JUDGE_SYSTEM = (
    "You are reviewing an answer to a question about a financial document. "
    "Decide only whether the answer is correct. Reply with a single word: "
    "ACCEPT if the answer is correct, REJECT if it is not."
)


def _require(pkg: str):
    try:
        return __import__(pkg)
    except ImportError:
        sys.exit(
            f"missing package '{pkg}'. Install recording extras first:\n"
            f"    pip install -r requirements-record.txt"
        )


def _require_key(var: str):
    if not os.environ.get(var):
        sys.exit(f"missing environment variable {var}. Export it before recording.")


def load_questions(instance: str, limit: int | None):
    """Returns a list of (qid, question_text, gold_answer) from FinStructBench."""
    _require("finstructbench")
    from finstructbench import Benchmark, get_instance_path  # type: ignore

    bench = Benchmark(get_instance_path(instance))
    # Graph-only run gives provably-correct gold answers (no LLM in the ground-truth loop).
    truth = bench.run()  # see FinStructBench docs for the result shape
    rows = []
    for i, q in enumerate(truth.questions):           # adapt attribute names to the installed version
        rows.append((q.id, q.text, q.gold_answer))
        if limit and len(rows) >= limit:
            break
    return rows


def anthropic_answer(client, model: str, prompt: str, system: str | None = None) -> str:
    msg = client.messages.create(
        model=model, max_tokens=512,
        system=system or "Answer the question about the financial document concisely.",
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(b.text for b in msg.content if getattr(b, "type", "") == "text").strip()


def openai_answer(client, model: str, prompt: str, system: str) -> str:
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content.strip()


def is_accept(verdict_text: str) -> bool:
    return verdict_text.strip().upper().startswith("ACCEPT")


def grade(gold: str, candidate: str) -> bool:
    """Graph-verified correctness. Exact, normalised match against the gold answer.
    Replace with FinStructBench's own grader if you prefer its tolerance rules."""
    norm = lambda s: " ".join(str(s).lower().split())
    return norm(gold) == norm(candidate)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--instance", default="model_validation")
    ap.add_argument("--limit", type=int, default=60)
    ap.add_argument("--out", default="data/runs/run.json")
    args = ap.parse_args(argv[1:])

    _require_key("ANTHROPIC_API_KEY")
    _require_key("OPENAI_API_KEY")
    anthropic = _require("anthropic")
    openai = _require("openai")

    a_client = anthropic.Anthropic()
    o_client = openai.OpenAI()

    questions = load_questions(args.instance, args.limit)
    items = []
    for qid, qtext, gold in questions:
        # 1. generator answers
        answer = anthropic_answer(a_client, GENERATOR_MODEL, qtext)
        truth_correct = grade(gold, answer)

        review_prompt = f"Question:\n{qtext}\n\nAnswer under review:\n{answer}"
        same = is_accept(anthropic_answer(a_client, SAME_FAMILY_JUDGE, review_prompt, JUDGE_SYSTEM))
        cross = is_accept(openai_answer(o_client, CROSS_FAMILY_JUDGE, review_prompt, JUDGE_SYSTEM))

        items.append({
            "qid": qid,
            "truth_correct": truth_correct,
            "verdicts": {"same_family": same, "cross_family": cross},
        })

    run = {
        "provenance": "measured",
        "recorded_at": dt.date.today().isoformat(),
        "benchmark": f"FinStructBench ({args.instance})",
        "generator": {"model": GENERATOR_MODEL,
                      "overall_accuracy": round(sum(i["truth_correct"] for i in items) / len(items), 3)},
        "judges": ["same_family", "cross_family"],
        "judge_models": {"same_family": SAME_FAMILY_JUDGE, "cross_family": CROSS_FAMILY_JUDGE},
        "items": items,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(run, indent=2))
    print(f"wrote {out} with {len(items)} items (provenance: measured)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
