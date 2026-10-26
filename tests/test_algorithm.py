"""Kern von Hand: jede Regel und jede Eigenschaft an Mini-Profilen, mit der Rechnung im Kommentar."""

import numpy as np
import pytest

import wax_algorithm as A
from conftest import counts

TB = np.array([0, 1, 2])


def test_rankings_tables_and_counts():
    rk = A.all_rankings(3)
    assert rk.shape == (6, 3) and rk.tolist()[0] == [0, 1, 2]
    pos, before, index = A.ranking_tables(3)
    assert pos[index[(1, 2, 0)]].tolist() == [2, 0, 1] and before[index[(1, 2, 0)], 1, 0]
    c = counts(3, (2, "ABC"), (1, "CBA"))
    assert c.sum() == 3 and c[index[(0, 1, 2)]] == 2 and c[index[(2, 1, 0)]] == 1
    assert A.counts_of(np.array([[0, 1, 2], [0, 1, 2], [2, 1, 0]])).tolist() == c.tolist()


def test_compositions():
    assert len(list(A.compositions(3, 6))) == 56 and all(sum(c) == 4 for c in A.compositions(4, 5))


def test_the_four_rules_by_hand():
    # 3 x A>B>C, 2 x B>C>A, 2 x C>B>A: Erststimmen A 3, B 2, C 2; Borda A 6, B 9, C 6; Copeland A 0, B 2, C 1; Sofortstichwahl: C scheidet aus (Gleichstand mit B, A vor B vor C), B gewinnt.
    c = counts(3, (3, "ABC"), (2, "BCA"), (2, "CBA"))
    assert A.outcome("plurality", c, 3, TB) == (0, False)
    assert A.outcome("borda", c, 3, TB) == (1, False)
    assert A.outcome("copeland", c, 3, TB) == (1, False)
    assert A.outcome("irv", c, 3, TB) == (1, True)                      # in der ersten Runde liegen B und C gleich hinten
    assert A.outcome("plurality", c, 3, np.array([2, 1, 0])) == (0, False)
    with pytest.raises(ValueError):
        A.outcome("x", c, 3, TB)


def test_tie_marks_and_tie_break():
    c = counts(3, (1, "ABC"), (1, "BCA"), (1, "CAB"))                      # Zyklus: alle gleich
    rev = np.array([2, 1, 0])
    for rule in ("plurality", "borda", "copeland", "irv"):
        assert A.outcome(rule, c, 3, TB) == (0, True)
    for rule in ("plurality", "borda", "copeland"):
        assert A.outcome(rule, c, 3, rev) == (2, True)                    # alle drei gleich: der Kandidat mit dem kleinsten Wert (C)
    # Sofortstichwahl mit C vor B vor A: alle drei gleich, A scheidet aus (größter Wert); seine Stimme geht an B (A>B>C): B 2, C 1 -> C scheidet aus, B gewinnt.
    assert A.outcome("irv", c, 3, rev) == (1, True)


def test_condorcet_winner_and_pairwise():
    c = counts(3, (1, "ABC"), (1, "BAC"), (1, "CBA"))
    w = A.pairwise(c, 3)
    assert w.tolist() == [[0, 2, 2], [1, 0, 2], [1, 1, 0]] or w.tolist() == [[0, 1, 2], [2, 0, 2], [1, 1, 0]]
    assert A.condorcet_winner(w) == 1 and A.condorcet_winner(A.pairwise(counts(3, (1, "ABC"), (1, "BCA"), (1, "CAB")), 3)) is None


def test_condorcet_violation_of_plurality_by_hand():
    # A>B>C, B>A>C, C>B>A: Erststimmen 1 : 1 : 1, Gleichstand A vor B vor C -> A. B schlägt A (2:1) und C (2:1).
    c = counts(3, (1, "ABC"), (1, "BAC"), (1, "CBA"))
    v = A.check_profile("condorcet", "plurality", c, 3, TB)
    assert v is not None and v.winner == 0 and v.detail == (1,) and v.n == 3
    assert A.check_profile("condorcet", "plurality", c, 3, TB, tie_free=True) is None                 # der Sieger hängt am Gleichstand


def test_copeland_never_violates_condorcet():
    for n in range(1, 6):
        for comp in A.compositions(n, 6):
            assert A.check_profile("condorcet", "copeland", np.array(comp), 3, TB) is None


def test_borda_condorcet_violation_without_a_tie_by_hand():
    # 3 x A>B>C, 2 x B>C>A: Borda A 6, B 3 + 4 = 7?? A: 3*2 = 6; B: 3*1 + 2*2 = 7; C: 2*1 = 2 -> B gewinnt. Condorcet: A schlägt B (3:2)
    c = counts(3, (3, "ABC"), (2, "BCA"))
    v = A.check_profile("condorcet", "borda", c, 3, TB, tie_free=True)
    assert v is not None and v.winner == 1 and v.detail == (0,) and v.n == 5


def test_irv_monotonicity_violation_by_hand():
    # 2 ABC, 2 BAC, 1 CAB, 2 CBA (7 Wähler): erste Runde A 2, B 2, C 3 -> A scheidet aus (Gleichstand A/B, B vor A? tiebreak A vor B: unter den Letzten scheidet der am wenigsten bevorzugte aus = B).
    c = counts(3, (2, "ABC"), (2, "BAC"), (1, "CAB"), (2, "CBA"))
    w, t = A.outcome("irv", c, 3, TB)
    assert (w, t) == (0, True)
    v = A.check_profile("monotonie", "irv", c, 3, TB)
    assert v is not None and v.winner == 0 and v.winner2 == 1 and v.detail == ((2, 0, 1),) and v.n == 7
    assert A.check_profile("monotonie", "irv", c, 3, TB, tie_free=True) is None


def test_no_show_violation_by_hand():
    # Copeland, 1 x ABC, 1 x BCA, 2 x CAB: C schlägt A (3:1)? A>B: 2 (ABC, CAB), B>A: 1... C bekommt 2 Siege. Mit B>C>A dazu gewinnt A.
    c = counts(3, (1, "ABC"), (1, "BCA"), (2, "CAB"))
    assert A.outcome("copeland", c, 3, TB)[0] == 2
    v = A.check_profile("teilnahme", "copeland", c, 3, TB)
    assert v is not None and v.winner == 2 and v.winner2 == 0 and v.detail == ((1, 2, 0),)


def test_consistency_violation_by_hand():
    # Copeland: Gruppe 1 = ABC + BAC (Gleichstand A/B -> A), Gruppe 2 = ACB + BAC + CBA (Sieger B). Hier die in der Aufzählung gefundene Form.
    c1 = counts(3, (1, "ABC"), (1, "BAC"))
    c2 = counts(3, (1, "ACB"), (1, "BAC"), (1, "CBA"))
    assert A.outcome("copeland", c1, 3, TB)[0] == 0
    v = A.check_consistency("copeland", c1, c2, 3, TB)
    assert v is None or v.winner2 != v.winner                           # beide Gruppen haben verschiedene Sieger oder die Verletzung liegt vor
    c3 = counts(3, (1, "ABC"), (1, "CAB"))
    c4 = counts(3, (1, "ABC"), (1, "BCA"), (1, "CAB"))
    assert A.outcome("irv", c3, 3, TB)[0] == 0 and A.outcome("irv", c4, 3, TB)[0] == 0
    v = A.check_consistency("irv", c3, c4, 3, TB)
    assert v is not None and v.winner == 0 and v.winner2 == 2 and v.n == 5


def test_ausscheiden_eines_verlierers_by_hand():
    # Plurality: 1 x BAC, 1 x CAB: Gleichstand B/C -> B. C ausgeschieden: 1 x BA, 1 x AB -> Gleichstand -> A (A vor B).
    c = counts(3, (1, "BAC"), (1, "CAB"))
    v = A.check_profile("iia", "plurality", c, 3, TB)
    assert v is not None and v.winner == 1 and v.winner2 == 0 and v.detail == (2,)


def test_drop_candidate_and_raise_index():
    c = counts(3, (2, "BCA"), (1, "CAB"))
    d = A.drop_candidate(c, 3, 2)                                      # C streichen: BCA -> BA, CAB -> AB; neu nummeriert: A=0, B=1
    assert d.sum() == 3 and d[A.ranking_tables(2)[2][(1, 0)]] == 2 and d[A.ranking_tables(2)[2][(0, 1)]] == 1
    _, _, index = A.ranking_tables(3)
    assert A.raise_index(index[(0, 1, 2)], 1, 3) == index[(1, 0, 2)] and A.raise_index(index[(0, 1, 2)], 0, 3) is None


def test_pareto_is_never_violated():
    for n in range(1, 6):
        for comp in A.compositions(n, 6):
            for rule in A.RULES:
                assert A.check_profile("pareto", rule, np.array(comp), 3, TB) is None


def test_smallest_violations_found_by_search_match_the_hand_cases():
    assert A.smallest_violation("condorcet", "plurality", 3, TB, 8).n == 3
    assert A.smallest_violation("condorcet", "plurality", 3, TB, 6, tie_free=True) is None and A.smallest_violation("condorcet", "plurality", 3, TB, 7, tie_free=True).n == 7
    assert A.smallest_violation("monotonie", "irv", 3, TB, 8).n == 7 and A.smallest_violation("monotonie", "irv", 3, TB, 6) is None
    assert A.smallest_violation("teilnahme", "copeland", 3, TB, 8).n == 4 and A.smallest_violation("teilnahme", "irv", 3, TB, 8).n == 3
    assert A.smallest_violation("konsistenz", "irv", 3, TB, 8).n == 5 and A.smallest_violation("konsistenz", "plurality", 3, TB, 6) is None
    assert A.smallest_violation("iia", "borda", 3, TB, 8).n == 2 and A.smallest_violation("iia", "borda", 3, TB, 8, tie_free=True).n == 5


def test_unknown_axiom_raises():
    with pytest.raises(ValueError):
        A.check_profile("x", "plurality", counts(3, (1, "ABC")), 3, TB)


def test_profile_models_shapes():
    rng = np.random.default_rng(1)
    for gen in A.PROFILE_MODELS.values():
        p = gen(30, 4, rng)
        assert p.shape == (30, 4) and all(sorted(r) == [0, 1, 2, 3] for r in p.tolist())


def test_pareto_check_detects_a_rule_that_chooses_a_dominated_candidate(monkeypatch):
    """Keine der vier Regeln verletzt Pareto; damit die Prüfung selbst getestet ist, wird eine Regel eingesetzt, die den Borda-Letzten wählt."""
    def worst(rule, c, m, tb):
        pos, _, _ = A.ranking_tables(m)
        return int(np.argmin(c @ (m - 1 - pos))), False

    monkeypatch.setattr(A, "outcome", worst)
    v = A.check_profile("pareto", "plurality", counts(3, (3, "ABC")), 3, TB)
    assert v is not None and v.winner == 2 and v.detail == (0, 2) and v.n == 3                  # alle drei reihen A vor C, C gewinnt
    assert A.check_profile("pareto", "plurality", counts(3, (1, "ABC")), 3, TB) is not None       # ein einzelner Wähler genügt
    assert A.check_profile("pareto", "plurality", np.zeros(6, dtype=int), 3, TB) is None          # ohne Wähler gibt es nichts zu verletzen


def test_the_consistency_search_respects_its_bounds():
    assert A.smallest_violation("konsistenz", "irv", 3, TB, 5).n == 5
    assert A.smallest_violation("konsistenz", "irv", 3, TB, 4) is None
    assert A.smallest_violation("konsistenz", "copeland", 3, TB, 6).n == 5 and A.smallest_violation("konsistenz", "copeland", 3, TB, 5).n == 5


def test_iia_needs_at_least_three_candidates():
    for rule in A.RULES:
        assert A.check_profile("iia", rule, counts(2, (1, "AB"), (1, "BA")), 2, np.array([0, 1])) is None
