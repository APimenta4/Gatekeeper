from gatekeeper.policy.verdict import Verdict, worst


def test_worst_block_beats_warn():
    assert worst(Verdict.BLOCK, Verdict.WARN) == Verdict.BLOCK


def test_worst_warn_beats_allow():
    assert worst(Verdict.WARN, Verdict.ALLOW) == Verdict.WARN


def test_worst_block_beats_allow():
    assert worst(Verdict.BLOCK, Verdict.ALLOW) == Verdict.BLOCK


def test_worst_equal_returns_same():
    assert worst(Verdict.WARN, Verdict.WARN) == Verdict.WARN


def test_worst_commutative():
    assert worst(Verdict.WARN, Verdict.BLOCK) == worst(Verdict.BLOCK, Verdict.WARN)
