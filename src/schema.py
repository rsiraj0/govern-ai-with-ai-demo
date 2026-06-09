"""
Loads a recorded run and turns it into the per-reviewer verdict lists the
scorer expects. One run file drives both this scorer and the web demo, so the
picture on the page and the numbers in the table cannot disagree.

Run-file shape (data/runs/run.json):

{
  "provenance": "illustrative" | "measured",
  "recorded_at": null | "2026-06-09",
  "benchmark": "FinStructBench ...",
  "generator": {"model": "...", "overall_accuracy": 0.58},
  "judges": ["same_family", "cross_family"],     # ordered, least diverse first
  "judge_models": {"same_family": "...", "cross_family": "..."},
  "items": [
    {"qid": "q001", "truth_correct": true, "verdicts": {"same_family": true, "cross_family": true}},
    ...
  ]
}
"""

import json

from src.score import Item

GROUND_TRUTH = "ground_truth"


def load_run(path: str):
    with open(path) as f:
        run = json.load(f)

    items = run["items"]
    judges = run["judges"]  # ordered list

    verdicts: dict[str, list[Item]] = {}
    for j in judges:
        verdicts[j] = [
            Item(qid=it["qid"], truth_correct=it["truth_correct"], judge_accept=it["verdicts"][j])
            for it in items
        ]

    # The non-model check accepts exactly the correct answers, so it is correct
    # by construction. It anchors the table at false-acceptance = 0.
    verdicts[GROUND_TRUTH] = [
        Item(qid=it["qid"], truth_correct=it["truth_correct"], judge_accept=it["truth_correct"])
        for it in items
    ]

    return run, verdicts
