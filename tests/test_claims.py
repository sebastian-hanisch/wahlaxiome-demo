"""Befunde der README als feste Werte und Bänder: jede Zahl, die dort steht, ist hier an den festen Plänen der App geprüft.

Die Tabelle der kleinsten Gegenbeispiele ist eine Aufzählung und deshalb **exakt** (kein Band). Die Häufigkeiten in Zufallsprofilen sind Stichproben mit je 150 Profilen
(Standardabweichung eines Anteils höchstens 4 Prozentpunkte): dort stehen Bänder von ±10 Punkten, Nullen und Sätze ohne Band.
"""

import numpy as np
import pytest

import wax_algorithm as A
import wax_constants as C
import wax_evaluation as ev

BAND = 0.10


@pytest.fixture(scope="module")
def table():
    return {(c["axiom"], c["rule"]): c for c in ev.table_cells()}


@pytest.fixture(scope="module")
def frequency():
    return {(r["axiom"], r["rule"], r["m"]): r for r in ev.series_frequency()}


@pytest.fixture(scope="module")
def models():
    return {(r["model"], r["axiom"], r["rule"]): r for r in ev.series_models()}


def test_the_table_of_smallest_counterexamples_with_the_tie_break(table):
    want = {("condorcet", "plurality"): 3, ("condorcet", "borda"): 3, ("condorcet", "irv"): 3, ("monotonie", "irv"): 7, ("teilnahme", "copeland"): 4, ("teilnahme", "irv"): 3,
            ("konsistenz", "copeland"): 5, ("konsistenz", "irv"): 5, ("iia", "plurality"): 2, ("iia", "borda"): 2, ("iia", "copeland"): 2, ("iia", "irv"): 2}
    got = {k: c["with_tie"] for k, c in table.items() if c["with_tie"] is not None}
    assert got == want and len(table) == 24


def test_the_table_without_the_help_of_a_tie(table):
    want = {("condorcet", "plurality"): 7, ("condorcet", "borda"): 5, ("condorcet", "irv"): 5, ("iia", "plurality"): 7, ("iia", "borda"): 5, ("iia", "irv"): 5}
    got = {k: c["tie_free"] for k, c in table.items() if c["tie_free"] is not None}
    assert got == want


def test_what_always_holds_in_the_searched_range(table):
    for rule in C.RULES:
        assert table[("pareto", rule)]["with_tie"] is None
    for axiom in ("monotonie", "teilnahme", "konsistenz"):
        for rule in ("plurality", "borda"):
            assert table[(axiom, rule)]["with_tie"] is None, (axiom, rule)
    assert table[("condorcet", "copeland")]["with_tie"] is None and table[("monotonie", "copeland")]["with_tie"] is None


def test_without_a_tie_irv_monotonicity_and_participation_need_more_than_fifteen_voters():
    tb = np.arange(3)
    assert A.smallest_violation("monotonie", "irv", 3, tb, 15, tie_free=True) is None
    assert A.smallest_violation("teilnahme", "irv", 3, tb, 15, tie_free=True) is None


def test_with_four_candidates_up_to_four_voters():
    tb = np.arange(4)
    assert A.smallest_violation("condorcet", "copeland", 4, tb, 4) is None
    assert A.smallest_violation("teilnahme", "copeland", 4, tb, 4).n == 3 and A.smallest_violation("teilnahme", "irv", 4, tb, 4).n == 3
    assert A.smallest_violation("iia", "borda", 4, tb, 4, tie_free=True).n == 4 and A.smallest_violation("iia", "copeland", 4, tb, 4, tie_free=True).n == 4
    assert A.smallest_violation("iia", "irv", 4, tb, 4, tie_free=True) is None


def test_frequency_in_random_profiles_with_four_candidates(frequency):
    f = lambda a, r: frequency[(a, r, 4)]  # noqa: E731
    assert f("condorcet", "plurality")["share"] == pytest.approx(0.23, abs=BAND) and f("condorcet", "plurality")["share_free"] == pytest.approx(0.13, abs=BAND)
    assert f("condorcet", "borda")["share"] == pytest.approx(0.11, abs=BAND) and f("condorcet", "irv")["share"] == pytest.approx(0.05, abs=0.08)
    assert f("condorcet", "copeland")["share"] == 0.0
    assert f("monotonie", "irv")["share"] == pytest.approx(0.08, abs=0.08) and f("teilnahme", "irv")["share"] == pytest.approx(0.09, abs=0.08) and f("teilnahme", "copeland")["share"] == pytest.approx(0.07, abs=0.08)
    assert f("iia", "plurality")["share"] == pytest.approx(0.29, abs=BAND) and f("iia", "borda")["share"] == pytest.approx(0.25, abs=BAND)
    assert f("iia", "copeland")["share"] == pytest.approx(0.16, abs=BAND) and f("iia", "irv")["share"] == pytest.approx(0.21, abs=BAND)


def test_properties_that_are_never_violated_in_the_samples(frequency):
    for rule in C.RULES:
        for m in C.SERIES_MS:
            assert frequency[("pareto", rule, m)]["share"] == 0.0
    for rule in ("plurality", "borda"):
        for axiom in ("monotonie", "teilnahme", "konsistenz"):
            for m in C.SERIES_MS:
                assert frequency[(axiom, rule, m)]["share"] == 0.0, (axiom, rule, m)
    assert frequency[("monotonie", "copeland", 4)]["share"] == 0.0


def test_without_a_tie_only_condorcet_and_iia_remain_in_random_profiles(frequency):
    for (axiom, rule, m), r in frequency.items():
        if axiom in ("monotonie", "teilnahme", "konsistenz", "pareto"):
            assert r["share_free"] == 0.0, (axiom, rule, m)
    assert all(frequency[("iia", "copeland", m)]["share_free"] == 0.0 for m in C.SERIES_MS) and all(frequency[("condorcet", "copeland", m)]["share_free"] == 0.0 for m in C.SERIES_MS)
    assert frequency[("iia", "plurality", 3)]["share_free"] == pytest.approx(0.20, abs=BAND) and frequency[("iia", "borda", 4)]["share_free"] == pytest.approx(0.11, abs=BAND)


def test_iia_is_the_most_frequent_violation(frequency):
    for m in C.SERIES_MS:
        for rule in C.RULES:
            iia = frequency[("iia", rule, m)]["share"]
            assert iia > 0.05 and all(iia >= frequency[(a, rule, m)]["share"] - 0.02 for a in ("monotonie", "teilnahme", "konsistenz", "pareto"))


def test_profile_models_with_four_candidates(models):
    assert models[("single", "iia", "plurality")]["share"] == pytest.approx(0.81, abs=BAND) and models[("single", "condorcet", "plurality")]["share"] == pytest.approx(0.57, abs=BAND)
    assert models[("single", "condorcet", "irv")]["share"] == pytest.approx(0.42, abs=BAND) and models[("single", "condorcet", "borda")]["share"] == pytest.approx(0.09, abs=0.08)
    assert models[("single", "monotonie", "irv")]["share"] == pytest.approx(0.01, abs=0.06)
    assert models[("camps", "iia", "plurality")]["share"] == pytest.approx(0.42, abs=BAND) and models[("camps", "condorcet", "plurality")]["share"] == pytest.approx(0.31, abs=BAND)
    assert models[("random", "iia", "plurality")]["share"] == pytest.approx(0.29, abs=BAND)
    assert all(models[(mo, "condorcet", "copeland")]["share"] == 0.0 for mo in C.MODELS)


def test_the_presets_tell_the_stories_in_their_help_texts():
    for name, p in C.PRESETS.items():
        a = ev.analyse(ev.Settings(**p))
        if name in ("Copeland: nie ein Verstoß",):
            assert a.violation is None
        else:
            assert a.violation is not None, name
    assert ev.analyse(ev.Settings(**C.PRESETS["Condorcet: wer scheitert?"])).violation.n == 3
    assert ev.analyse(ev.Settings(**C.PRESETS["Sofortstichwahl: Monotonie"])).violation.n == 7
    assert ev.analyse(ev.Settings(**C.PRESETS["Teilnahme: Copeland"])).violation.n == 4
    assert ev.analyse(ev.Settings(**C.PRESETS["Ohne Gleichstand: Borda"])).violation.n == 5
