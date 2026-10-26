"""Orakel (DEMO-PLAYBOOK §12): unabhängige Rechenwege für Regeln, Eigenschaften und die Suche.

Die naive Fassung arbeitet mit Listen von Rangfolgen (ein Eintrag je Wähler) und einfachen Schleifen, nicht mit Zählvektoren.
(1) Regeln samt Gleichstandsmarke gegen die Zählvektor-Fassung, (2) jede Eigenschaft (mit und ohne Gleichstand) gegen die naive Prüfung auf zufälligen Profilen,
(3) das kleinste Gegenbeispiel gegen eine naive Aufzählung aller Multimengen von Rangfolgen, (4) jedes gefundene Gegenbeispiel wird nachgespielt.
"""

import itertools

import numpy as np
import pytest

import wax_algorithm as A
from conftest import counts  # noqa: F401  (gemeinsame Hilfe)


def naive_outcome(rule, voters, m, tb):
    """(Sieger, Gleichstand-Marke); voters = Liste von Rangfolgen (Tupel)."""
    if rule in ("plurality", "borda", "copeland"):
        if rule == "plurality":
            scores = [float(sum(1 for r in voters if r[0] == c)) for c in range(m)]
        elif rule == "borda":
            scores = [float(sum(m - 1 - r.index(c) for r in voters)) for c in range(m)]
        else:
            w = [[sum(1 for r in voters if r.index(a) < r.index(b)) for b in range(m)] for a in range(m)]
            scores = [sum(1.0 if w[a][b] > w[b][a] else (0.5 if w[a][b] == w[b][a] else 0.0) for b in range(m) if b != a) for a in range(m)]
        best = max(scores)
        top = [c for c in range(m) if scores[c] == best]
        return min(top, key=lambda c: tb[c]), len(top) > 1
    alive = set(range(m))
    tied = False
    while len(alive) > 1:
        cnt = {c: 0 for c in alive}
        for r in voters:
            for c in r:
                if c in alive:
                    cnt[c] += 1
                    break
        low = min(cnt.values())
        losers = [c for c in alive if cnt[c] == low]
        tied |= len(losers) > 1
        alive.discard(max(losers, key=lambda c: tb[c]))
    return next(iter(alive)), tied


def naive_violation(axiom, rule, voters, m, tb, tie_free):
    """True, wenn die Eigenschaft am Profil `voters` verletzt ist (Konsistenz: nicht hier)."""
    w, t = naive_outcome(rule, voters, m, tb)
    if tie_free and t:
        return False
    rankings = list(itertools.permutations(range(m)))
    n = len(voters)
    if axiom == "condorcet":
        pw = [[sum(1 for r in voters if r.index(a) < r.index(b)) for b in range(m)] for a in range(m)]
        cw = next((a for a in range(m) if all(pw[a][b] > pw[b][a] for b in range(m) if b != a)), None)
        return cw is not None and cw != w
    if axiom == "pareto":
        return any(a != w and all(r.index(a) < r.index(w) for r in voters) for a in range(m)) and n > 0
    if axiom == "monotonie":
        for k, r in enumerate(voters):
            p = r.index(w)
            if p == 0:
                continue
            lst = list(r)
            lst[p - 1], lst[p] = lst[p], lst[p - 1]
            changed = voters[:k] + [tuple(lst)] + voters[k + 1:]
            w2, t2 = naive_outcome(rule, changed, m, tb)
            if w2 != w and not (tie_free and t2):
                return True
        return False
    if axiom == "teilnahme":
        for r in rankings:
            w2, t2 = naive_outcome(rule, voters + [r], m, tb)
            if r.index(w2) > r.index(w) and not (tie_free and t2):
                return True
        return False
    if axiom == "iia":
        if m < 3:
            return False
        for x in range(m):
            if x == w:
                continue
            keep = [c for c in range(m) if c != x]
            small = [tuple(keep.index(c) for c in r if c != x) for r in voters]
            w2, t2 = naive_outcome(rule, small, m - 1, tb[keep])
            if keep[w2] != w and not (tie_free and t2):
                return True
        return False
    raise ValueError(axiom)


def voters_of(c, m):
    rk = A.all_rankings(m)
    return [tuple(rk[i].tolist()) for i in range(len(c)) for _ in range(int(c[i]))]


@pytest.mark.parametrize("rule", A.RULES)
def test_rules_match_the_naive_evaluation(rule):
    rng = np.random.default_rng(10)
    for t in range(80):
        m = int(rng.integers(2, 5))
        n = int(rng.integers(1, 25))
        model = list(A.PROFILE_MODELS)[t % 3]
        profile = A.PROFILE_MODELS[model](n, m, rng)
        tb = rng.permutation(m)
        got = A.outcome(rule, A.counts_of(profile), m, tb)
        assert got == naive_outcome(rule, [tuple(r) for r in profile.tolist()], m, tb), (rule, t)


@pytest.mark.parametrize("axiom", ["condorcet", "pareto", "monotonie", "teilnahme", "iia"])
@pytest.mark.parametrize("rule", A.RULES)
def test_each_property_matches_the_naive_check_on_random_profiles(axiom, rule):
    rng = np.random.default_rng(20)
    hits = 0
    for t in range(80):
        m = 3 + t % 2
        n = int(rng.integers(2, 12))
        profile = A.PROFILE_MODELS[list(A.PROFILE_MODELS)[t % 3]](n, m, rng)
        tb = rng.permutation(m)
        c = A.counts_of(profile)
        voters = [tuple(r) for r in profile.tolist()]
        for free in (False, True):
            fast = A.check_profile(axiom, rule, c, m, tb, free) is not None
            slow = naive_violation(axiom, rule, voters, m, tb, free)
            assert fast == slow, (axiom, rule, t, free)
            hits += fast


def test_consistency_matches_the_naive_check():
    rng = np.random.default_rng(30)
    found = 0
    for t in range(300):
        m = 3
        n1, n2 = int(rng.integers(1, 5)), int(rng.integers(1, 5))
        p1 = A.profile_random(n1, m, rng)
        p2 = A.profile_random(n2, m, rng)
        tb = rng.permutation(m)
        for rule in ("copeland", "irv", "borda"):
            for free in (False, True):
                v1, v2 = [tuple(r) for r in p1.tolist()], [tuple(r) for r in p2.tolist()]
                w1, t1 = naive_outcome(rule, v1, m, tb)
                w2, t2 = naive_outcome(rule, v2, m, tb)
                slow = False
                if w1 == w2 and not (free and (t1 or t2)):
                    w3, t3 = naive_outcome(rule, v1 + v2, m, tb)
                    slow = w3 != w1 and not (free and t3)
                fast = A.check_consistency(rule, A.counts_of(p1), A.counts_of(p2), m, tb, free) is not None
                assert fast == slow, (rule, t, free)
                found += fast
    assert found > 0


@pytest.mark.parametrize("axiom", ["condorcet", "monotonie", "teilnahme", "iia"])
@pytest.mark.parametrize("rule", A.RULES)
def test_smallest_counterexample_matches_a_naive_enumeration(axiom, rule):
    m, tb = 3, np.array([0, 1, 2])
    rankings = list(itertools.permutations(range(m)))
    for free in (False, True):
        want = None
        for n in range(1, 6):
            for combo in itertools.combinations_with_replacement(rankings, n):
                if naive_violation(axiom, rule, list(combo), m, tb, free):
                    want = n
                    break
            if want:
                break
        got = A.smallest_violation(axiom, rule, m, tb, 5, free)
        assert (None if got is None else got.n) == want, (axiom, rule, free)


def test_every_found_counterexample_replays():
    m, tb = 3, np.array([0, 1, 2])
    for axiom in ("condorcet", "monotonie", "teilnahme", "iia", "konsistenz"):
        for rule in A.RULES:
            for free in (False, True):
                v = A.smallest_violation(axiom, rule, m, tb, 8, free)
                if v is None:
                    continue
                if axiom == "konsistenz":
                    c1, c2 = np.array(v.counts), np.array(v.counts2)
                    w1, t1 = naive_outcome(rule, voters_of(c1, m), m, tb)
                    w2, t2 = naive_outcome(rule, voters_of(c2, m), m, tb)
                    w3, t3 = naive_outcome(rule, voters_of(c1 + c2, m), m, tb)
                    assert w1 == w2 == v.winner and w3 == v.winner2 != w1 and v.n == int((c1 + c2).sum())
                    if free:
                        assert not (t1 or t2 or t3)
                else:
                    assert naive_violation(axiom, rule, voters_of(np.array(v.counts), m), m, tb, free), (axiom, rule, free)
                    assert v.n == sum(v.counts)


def test_copeland_never_violates_condorcet_in_random_profiles():
    rng = np.random.default_rng(40)
    for t in range(200):
        m = 3 + t % 3
        if m > 4:
            m = 4
        profile = A.profile_random(int(rng.integers(1, 30)), m, rng)
        assert A.check_profile("condorcet", "copeland", A.counts_of(profile), m, rng.permutation(m)) is None
