from src.score import Item, score_judge


def _items(rows):  # rows: list of (truth_correct, judge_accept)
    return [Item(qid=str(i), truth_correct=t, judge_accept=a)
            for i, (t, a) in enumerate(rows)]


def test_perfect_judge_catches_every_wrong_answer():
    s = score_judge("perfect", _items([(True, True), (True, True),
                                        (False, False), (False, False)]))
    assert s.false_acceptance_rate == 0.0
    assert s.catch_rate == 1.0
    assert s.false_rejection_rate == 0.0


def test_rubber_stamp_judge_accepts_everything():
    s = score_judge("rubber_stamp", _items([(True, True), (False, True),
                                            (False, True), (True, True)]))
    assert s.false_acceptance_rate == 1.0
    assert s.catch_rate == 0.0
    assert s.agreement_on_error == 0.5   # 2 of 4 items are accepted-wrong


def test_far_population_is_wrong_answers_only():
    # 1 wrong (accepted) + 3 correct (accepted) -> FAR is 1/1, not 1/4
    s = score_judge("mixed", _items([(False, True), (True, True),
                                     (True, True), (True, True)]))
    assert s.false_acceptance_rate == 1.0
    assert s.n_wrong == 1


def test_no_wrong_answers_does_not_divide_by_zero():
    s = score_judge("all_correct", _items([(True, True), (True, False)]))
    assert s.false_acceptance_rate == 0.0
    assert s.catch_rate == 1.0
    assert s.false_rejection_rate == 0.5   # but it wrongly rejected a correct one


def test_no_correct_answers_does_not_divide_by_zero():
    s = score_judge("all_wrong", _items([(False, True), (False, False)]))
    assert s.false_rejection_rate == 0.0
    assert s.false_acceptance_rate == 0.5


def test_empty_raises():
    import pytest
    with pytest.raises(ValueError):
        score_judge("empty", [])
