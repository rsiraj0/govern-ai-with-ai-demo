# Who catches the error

_Provenance: **illustrative**  ·  recorded: n/a  ·  benchmark: FinStructBench (illustrative stand-in; not a real run)_

| Reviewer | Approves wrong answers | Catches the error |
|---|---|---|
| Same-family AI judge | Often | Misses most of them |
| Different-company AI judge | Sometimes | Catches more of them |
| Ground-truth check (no model) | Never | Catches all of them |

This run is **illustrative**, so the table shows the pattern rather than figures. The same-lineage reviewer approves the most errors, a different-company model helps, and the non-model check against ground truth catches them all by construction.

> To produce measured percentages, run `src/record.py` against real models. The illustrative inputs come from `scripts/make_illustrative_fixture.py`.
