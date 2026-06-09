"""
Renders the one table the whole project exists to produce.

    python -m src.report                      # uses data/runs/run.json
    python -m src.report path/to/run.json

Writes results/table.md and results/table.csv, and prints the table.
"""

import csv
import sys
from pathlib import Path

from src.schema import load_run
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


def render_markdown(run: dict, scores) -> str:
    prov = run.get("provenance", "unknown").upper()
    when = run.get("recorded_at") or "n/a"
    gen = run.get("generator", {})
    lines = []
    lines.append(f"# Who catches the error  ·  [{prov}]")
    lines.append("")
    lines.append(
        f"_Provenance: **{run.get('provenance','unknown')}**  ·  recorded: {when}  ·  "
        f"benchmark: {run.get('benchmark','n/a')}  ·  "
        f"generator: {gen.get('model','n/a')} (accuracy {gen.get('overall_accuracy','n/a')})_"
    )
    lines.append("")
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
    if prov == "ILLUSTRATIVE":
        lines.append("")
        lines.append(
            "> These figures are **illustrative**, generated from declared rates in "
            "`scripts/make_illustrative_fixture.py`. Run `src/record.py` against real models "
            "to replace them with measured results."
        )
    return "\n".join(lines) + "\n"


def write_csv(scores, path: Path) -> None:
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["reviewer", "n", "wrong_answers", "false_acceptance_rate",
                    "catch_rate", "false_rejection_rate", "agreement_on_error"])
        for s in scores:
            r = s.row()
            w.writerow([_label(s.name), r["n"], r["wrong_answers"], r["false_acceptance_rate"],
                        r["catch_rate"], r["false_rejection_rate"], r["agreement_on_error"]])


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
    write_csv(scores, RESULTS / "table.csv")

    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
