"""
Renders the one table the whole project exists to produce.

    python -m src.report                      # uses data/runs/run.json
    python -m src.report path/to/run.json

Writes results/table.md and results/table.csv, and prints the table.
"""

import csv
import sys
from pathlib import Path

from src.schema import load_run, GROUND_TRUTH
from src.score import score_all

LABELS = {
    "same_family": "Same-family AI judge",
    "cross_family": "Different-company AI judge",
    "ground_truth": "Ground-truth check (no model)",
}

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RUN = ROOT / "data" / "runs" / "run.json"
RESULTS = ROOT / "results"


def _label(name: str) -> str:
    return LABELS.get(name, name)


def _is_measured(run: dict) -> bool:
    return run.get("provenance") == "measured"


def _qualitative(scores) -> dict:
    """Plain-words pattern for illustrative runs, so no fabricated precision is shown.
    Labels follow the actual ordering of the scores, not hard-coded assumptions."""
    models = [s for s in scores if s.name != GROUND_TRUTH]
    ranked = sorted(models, key=lambda s: s.false_acceptance_rate, reverse=True)
    tiers = [("Often", "Misses most of them"),
             ("Sometimes", "Catches more of them"),
             ("Sometimes", "Catches some of them")]
    labels = {}
    for i, s in enumerate(ranked):
        labels[s.name] = tiers[min(i, len(tiers) - 1)]
    for s in scores:
        if s.name == GROUND_TRUTH:
            labels[s.name] = ("Never", "Catches all of them")
    return labels


def render_markdown(run: dict, scores) -> str:
    prov = run.get("provenance", "unknown")
    when = run.get("recorded_at") or "n/a"
    gen = run.get("generator", {})
    lines = ["# Who catches the error", ""]
    lines.append(
        f"_Provenance: **{prov}**  ·  recorded: {when}  ·  benchmark: {run.get('benchmark','n/a')}_"
    )
    lines.append("")

    if _is_measured(run):
        lines.append("| Reviewer | Items | Wrong answers | False-acceptance | Catch rate | False-rejection |")
        lines.append("|---|---:|---:|---:|---:|---:|")
        for s in scores:
            lines.append(
                f"| {_label(s.name)} | {s.n} | {s.n_wrong} | "
                f"{s.false_acceptance_rate:.0%} | {s.catch_rate:.0%} | {s.false_rejection_rate:.0%} |"
            )
        lines.append("")
        lines.append(
            "False-acceptance is the share of *wrong* answers the reviewer approved. "
            "Lower is better; the rows are ordered so diversity increases downward."
        )
    else:
        labels = _qualitative(scores)
        lines.append("| Reviewer | Approves wrong answers | Catches the error |")
        lines.append("|---|---|---|")
        for s in scores:
            approves, catches = labels[s.name]
            lines.append(f"| {_label(s.name)} | {approves} | {catches} |")
        lines.append("")
        lines.append(
            "This run is **illustrative**, so the table shows the pattern rather than figures. "
            "The same-lineage reviewer approves the most errors, a different-company model helps, "
            "and the non-model check against ground truth catches them all by construction."
        )
        lines.append("")
        lines.append(
            "> To produce measured percentages, run `src/record.py` against real models. "
            "The illustrative inputs come from `scripts/make_illustrative_fixture.py`."
        )
    return "\n".join(lines) + "\n"


def write_csv(run: dict, scores, path: Path) -> None:
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        if _is_measured(run):
            w.writerow(["reviewer", "n", "wrong_answers", "false_acceptance_rate",
                        "catch_rate", "false_rejection_rate", "agreement_on_error"])
            for s in scores:
                r = s.row()
                w.writerow([_label(s.name), r["n"], r["wrong_answers"], r["false_acceptance_rate"],
                            r["catch_rate"], r["false_rejection_rate"], r["agreement_on_error"]])
        else:
            labels = _qualitative(scores)
            w.writerow(["reviewer", "approves_wrong_answers", "catches_the_error", "provenance"])
            for s in scores:
                approves, catches = labels[s.name]
                w.writerow([_label(s.name), approves, catches, "illustrative"])


def main(argv: list[str]) -> int:
    run_path = Path(argv[1]) if len(argv) > 1 else DEFAULT_RUN
    if not run_path.exists():
        print(f"run file not found: {run_path}\nrun `make fixture` first.", file=sys.stderr)
        return 1

    run, verdicts = load_run(str(run_path))
    scores = score_all(verdicts)

    RESULTS.mkdir(exist_ok=True)
    md = render_markdown(run, scores)
    (RESULTS / "table.md").write_text(md)
    write_csv(run, scores, RESULTS / "table.csv")

    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
