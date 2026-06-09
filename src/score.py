"""
Scores reviewer verdicts against ground truth.

Vocabulary:
  truth_correct : from the benchmark's graph baseline. True = the generated answer is CORRECT.
  judge_accept  : from a reviewer.                     True = the reviewer ACCEPTS the answer.

The number that proves the thesis is the false-acceptance rate (FAR):
of the answers that are actually WRONG, how many did the reviewer ACCEPT?
A same-family judge should post the highest FAR. A non-model check against
ground truth posts FAR = 0 by construction and anchors the table.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    qid: str
    truth_correct: bool      # graph baseline: is the generated answer correct?
    judge_accept: bool       # reviewer: did it accept the answer?


@dataclass(frozen=True)
class JudgeScore:
    name: str
    n: int
    n_wrong: int             # answers that are actually wrong (the population that matters)
    n_correct: int
    false_acceptance_rate: float   # accepted | wrong   -> the headline
    catch_rate: float              # rejected | wrong   -> 1 - FAR
    false_rejection_rate: float    # rejected | correct -> the cost of the reviewer
    agreement_on_error: float      # share of all items where reviewer accepts a wrong answer

    def row(self) -> dict:
        return {
            "judge": self.name,
            "n": self.n,
            "wrong_answers": self.n_wrong,
            "false_acceptance_rate": round(self.false_acceptance_rate, 3),
            "catch_rate": round(self.catch_rate, 3),
            "false_rejection_rate": round(self.false_rejection_rate, 3),
            "agreement_on_error": round(self.agreement_on_error, 3),
        }


def score_judge(name: str, items: list[Item]) -> JudgeScore:
    if not items:
        raise ValueError(f"no items for judge {name!r}")

    n = len(items)
    wrong = [it for it in items if not it.truth_correct]
    correct = [it for it in items if it.truth_correct]

    n_wrong = len(wrong)
    n_correct = len(correct)

    accepted_wrong = sum(1 for it in wrong if it.judge_accept)
    rejected_correct = sum(1 for it in correct if not it.judge_accept)

    far = accepted_wrong / n_wrong if n_wrong else 0.0
    catch = 1.0 - far if n_wrong else 1.0
    frr = rejected_correct / n_correct if n_correct else 0.0
    agreement_on_error = accepted_wrong / n

    return JudgeScore(
        name=name,
        n=n,
        n_wrong=n_wrong,
        n_correct=n_correct,
        false_acceptance_rate=far,
        catch_rate=catch,
        false_rejection_rate=frr,
        agreement_on_error=agreement_on_error,
    )


def score_all(verdicts_by_judge: dict[str, list[Item]]) -> list[JudgeScore]:
    """Order is meaningful: the table reads top to bottom as diversity increases."""
    return [score_judge(name, items) for name, items in verdicts_by_judge.items()]
