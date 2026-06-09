# Who catches the error  ·  [ILLUSTRATIVE]

_Provenance: **illustrative**  ·  recorded: n/a  ·  benchmark: FinStructBench (illustrative stand-in; not a real run)  ·  generator: illustrative (accuracy 0.58)_

| Reviewer | Items | Wrong answers | False-acceptance | Catch rate | False-rejection |
|---|---:|---:|---:|---:|---:|
| Same-family AI judge | 60 | 25 | 36% | 64% | 9% |
| Different-company AI judge | 60 | 25 | 16% | 84% | 11% |
| Ground-truth check (no model) | 60 | 25 | 0% | 100% | 0% |

False-acceptance is the share of *wrong* answers the reviewer approved. Lower is better; the rows are ordered so diversity increases downward.

> These figures are **illustrative**, generated from declared rates in `scripts/make_illustrative_fixture.py`. Run `src/record.py` against real models to replace them with measured results.
