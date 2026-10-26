"""Randfälle: kleinste und größte Reglerwerte für jede Eigenschaft und Regel, ungültige Eingaben, Determinismus, Struktur der Tabelle und der Messreihen bei kleinen Zahlen."""

import time

import numpy as np
import pytest

import wax_algorithm as A
import wax_constants as C
import wax_evaluation as ev
from wax_scenario import make_profile


def test_every_axiom_and_rule_at_the_extreme_settings():
    for axiom in C.AXIOMS:
        for rule in C.RULES:
            for m, n, free in ((C.M_MIN, C.N_MAX, False), (3, C.N_MIN, True), (3, C.N_MAX, True), (C.M_MAX, C.N_MAX, False)):
                a = ev.analyse(ev.Settings(axiom, rule, m, n, free))
                assert a.searched_to == min(n, C.N_LIMIT[m]) and ev.verdict_state(a)[0] in ("success", "warning")
                if a.violation is not None:
                    assert 1 <= a.violation.n <= a.searched_to and len(ev.describe(a.violation)) >= 2


def test_with_two_candidates_every_property_holds():
    tb = np.array([0, 1])
    for axiom in C.AXIOMS:
        for rule in C.RULES:
            assert A.smallest_violation(axiom, rule, 2, tb, 6) is None, (axiom, rule)


def test_the_largest_search_runs_fast_enough_for_the_app():
    t = time.perf_counter()
    ev.analyse(ev.Settings("konsistenz", "irv", 3, C.N_MAX, True))
    ev.analyse(ev.Settings("konsistenz", "copeland", 4, C.N_MAX, True))
    assert time.perf_counter() - t < 20


def test_a_search_limit_below_the_smallest_example_finds_nothing():
    assert ev.analyse(ev.Settings("condorcet", "plurality", 3, 2, False)).violation is None and ev.analyse(ev.Settings("condorcet", "plurality", 3, 3, False)).violation.n == 3


def test_invalid_inputs_raise():
    with pytest.raises(ValueError):
        make_profile("x", 3, 5, 1)
    with pytest.raises(ValueError):
        make_profile("random", 1, 5, 1)
    with pytest.raises(ValueError):
        make_profile("random", 3, 0, 1)
    with pytest.raises(ValueError):
        A.check_profile("x", "plurality", np.zeros(6, dtype=int), 3, np.arange(3))


def test_the_same_settings_give_the_same_analysis():
    a, b = ev.analyse(ev.Settings("teilnahme", "irv", 3, 6, False)), ev.analyse(ev.Settings("teilnahme", "irv", 3, 6, False))
    assert a.violation == b.violation and a.violation.n == 3


def test_table_structure_with_small_numbers():
    cells = ev.table_cells(m=3, max_n=3)
    assert [(c["axiom"], c["rule"]) for c in cells] == [(a, r) for a in C.AXIOMS for r in C.RULES] and all(set(c) == {"axiom", "rule", "m", "max_n", "with_tie", "tie_free"} for c in cells)
    assert all(c["with_tie"] is None or c["with_tie"] <= 3 for c in cells) and next(c for c in cells if (c["axiom"], c["rule"]) == ("condorcet", "plurality"))["with_tie"] == 3


def test_series_structure_with_small_numbers():
    rows = ev.series_frequency(ms=(3,), n=7, runs=10)
    assert [(r["axiom"], r["rule"]) for r in rows] == [(a, r) for a in C.AXIOMS for r in C.RULES]
    assert all(0 <= r["share_free"] <= r["share"] <= 1 for r in rows)
    models = ev.series_models(m=3, n=7, runs=10)
    assert len(models) == 3 * 5 * 4 and {r["model"] for r in models} == set(C.MODELS)


def test_the_stichproben_use_a_fixed_split_for_the_consistency_check():
    p, tb = make_profile("random", 3, 20, 5)
    a = ev.violates("konsistenz", "irv", p, tb, np.random.default_rng(1), False)
    b = ev.violates("konsistenz", "irv", p, tb, np.random.default_rng(1), False)
    assert a == b
