"""Kern: vier Wahlregeln auf Zählvektoren und die Prüfung von sechs Eigenschaften (Axiomen) mit der Suche nach dem kleinsten Gegenbeispiel.

Ein Profil wird als Zählvektor `c` über alle m! Rangfolgen geführt (Wähler mit derselben Rangfolge sind austauschbar; alle vier Regeln sind anonym).
Gleichstände entscheidet eine feste Rangfolge der Kandidaten (`tiebreak`, kleinerer Wert = bevorzugt); bei der Sofortstichwahl scheidet unter mehreren Letzten
der am wenigsten bevorzugte aus. Zu jedem Sieger gehört die Marke „Gleichstand“ (an der Spitze bei den Punkteregeln, in irgendeiner Runde bei der Sofortstichwahl):
Ein Gegenbeispiel **ohne Gleichstand** kommt in keinem beteiligten Lauf mit einem Gleichstand aus und hängt deshalb nicht am Los.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from functools import lru_cache

import numpy as np

RULE_NAMES = {"plurality": "Mehrheitswahl", "borda": "Borda-Zählung", "copeland": "Copeland (paarweise Siege)", "irv": "Sofortstichwahl (IRV)"}
RULES = tuple(RULE_NAMES)
AXIOMS = {
    "condorcet": "Condorcet-Konsistenz",
    "pareto": "Pareto-Effizienz",
    "monotonie": "Monotonie",
    "teilnahme": "Teilnahme",
    "konsistenz": "Konsistenz",
    "iia": "Unabhängigkeit vom Ausscheiden eines Verlierers",
}
MALLOWS_PHI = 0.7
CAMP_SHARE = 0.55


# --- Profile (für die Stichproben) ---------------------------------------------------------------------------------------------------------

def profile_random(n: int, m: int, rng: np.random.Generator) -> np.ndarray:
    return np.argsort(rng.random((n, m)), axis=1)


def profile_single_peaked(n: int, m: int, rng: np.random.Generator) -> np.ndarray:
    ideal = rng.random(n) * m - 0.5
    dist = np.abs(ideal[:, None] - np.arange(m)[None, :]) + 1e-9 * rng.random((n, m))
    return np.argsort(dist, axis=1)


def mallows_profile(n: int, base: list[int], phi: float, rng: np.random.Generator) -> np.ndarray:
    """n Ziehungen aus dem Mallows-Modell um `base` durch wiederholtes Einfügen: Wahrscheinlichkeit einer Rangfolge ∝ phi^(Fehlstände gegenüber `base`)."""
    m = len(base)
    pos = np.zeros((n, m), dtype=int)
    for i in range(1, m):
        weights = phi ** (i - np.arange(i + 1))
        cum = np.cumsum(weights / weights.sum())
        j = np.minimum(np.searchsorted(cum, rng.random(n), side="right"), i)
        pos[:, :i] += (pos[:, :i] >= j[:, None])
        pos[:, i] = j
    out = np.empty((n, m), dtype=int)
    out[np.arange(n)[:, None], pos] = np.array(base)[None, :]
    return out


def profile_camps(n: int, m: int, rng: np.random.Generator, phi: float = MALLOWS_PHI, share: float = CAMP_SHARE) -> np.ndarray:
    n_a = int(round(share * n))
    arr = np.vstack([mallows_profile(n_a, list(range(m)), phi, rng), mallows_profile(n - n_a, list(range(m - 1, -1, -1)), phi, rng)])
    return arr[rng.permutation(n)]


PROFILE_MODELS = {"random": profile_random, "single": profile_single_peaked, "camps": profile_camps}


# --- Rangfolgen als Index -------------------------------------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def all_rankings(m: int) -> np.ndarray:
    return np.array(list(itertools.permutations(range(m))), dtype=int)


@lru_cache(maxsize=None)
def ranking_tables(m: int):
    """(Rangplatz je Kandidat (m!, m), before[i, a, b] = a steht in Rangfolge i vor b (m!, m, m), Index je Rangfolge)."""
    rk = all_rankings(m)
    pos = np.empty_like(rk)
    pos[np.arange(len(rk))[:, None], rk] = np.arange(m)[None, :]
    before = pos[:, :, None] < pos[:, None, :]
    index = {tuple(r): i for i, r in enumerate(rk.tolist())}
    return pos, before, index


def counts_of(profile: np.ndarray) -> np.ndarray:
    m = profile.shape[1]
    _, _, index = ranking_tables(m)
    c = np.zeros(len(index), dtype=int)
    for row in profile.tolist():
        c[index[tuple(row)]] += 1
    return c


def compositions(total: int, parts: int):
    """Alle Zerlegungen von `total` in `parts` nichtnegative ganze Zahlen (lexikographisch absteigend im ersten Teil)."""
    if parts == 1:
        yield (total,)
        return
    for first in range(total, -1, -1):
        for rest in compositions(total - first, parts - 1):
            yield (first,) + rest


# --- Regeln ----------------------------------------------------------------------------------------------------------------------------------

def outcome(rule: str, c: np.ndarray, m: int, tiebreak: np.ndarray) -> tuple[int, bool]:
    """(Sieger, Gleichstand-Marke) einer Regel für den Zählvektor `c` über die m! Rangfolgen."""
    pos, before, _ = ranking_tables(m)
    rk = all_rankings(m)
    if rule in ("plurality", "borda", "copeland"):
        if rule == "plurality":
            scores = np.bincount(rk[:, 0], weights=c, minlength=m)
        elif rule == "borda":
            scores = c @ (m - 1 - pos)
        else:
            w = np.tensordot(c, before, axes=1).astype(int)
            np.fill_diagonal(w, 0)
            scores = (w > w.T).sum(axis=1) + ((w == w.T).sum(axis=1) - 1) * 0.5
        top = np.rint(2 * scores).astype(int)
        cand = np.flatnonzero(top == top.max())
        return int(cand[np.argmin(tiebreak[cand])]), len(cand) > 1
    if rule == "irv":
        alive = np.ones(m, dtype=bool)
        tied = False
        while alive.sum() > 1:
            first = np.argmin(np.where(alive[None, :], pos, m + 1), axis=1)
            counts = np.bincount(first, weights=c, minlength=m)
            cand = np.flatnonzero(alive)
            low = cand[counts[cand] == counts[cand].min()]
            tied |= len(low) > 1
            alive[int(low[np.argmax(tiebreak[low])])] = False
        return int(np.flatnonzero(alive)[0]), tied
    raise ValueError(f"unbekannte Regel: {rule}")


def pairwise(c: np.ndarray, m: int) -> np.ndarray:
    _, before, _ = ranking_tables(m)
    w = np.tensordot(c, before, axes=1).astype(int)
    np.fill_diagonal(w, 0)
    return w


def condorcet_winner(w: np.ndarray):
    m = len(w)
    for a in range(m):
        if all(w[a, b] > w[b, a] for b in range(m) if b != a):
            return a
    return None


def drop_candidate(c: np.ndarray, m: int, x: int) -> np.ndarray:
    """Zählvektor nach Streichen des Kandidaten x (die übrigen werden von 0 an neu nummeriert): über die Rangfolgen von m - 1 Kandidaten."""
    _, _, index_small = ranking_tables(m - 1)
    rk = all_rankings(m)
    out = np.zeros(len(index_small), dtype=int)
    for i in np.flatnonzero(c > 0):
        row = tuple(cc if cc < x else cc - 1 for cc in rk[i].tolist() if cc != x)
        out[index_small[row]] += c[i]
    return out


def raise_index(i: int, cand: int, m: int):
    """Index der Rangfolge, die entsteht, wenn `cand` in Rangfolge i einen Platz nach oben rückt (None, wenn er schon vorn steht)."""
    _, _, index = ranking_tables(m)
    row = all_rankings(m)[i].tolist()
    p = row.index(cand)
    if p == 0:
        return None
    row[p - 1], row[p] = row[p], row[p - 1]
    return index[tuple(row)]


# --- Eigenschaften --------------------------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Violation:
    axiom: str
    rule: str
    m: int
    n: int
    counts: tuple                 # Zählvektor des (ersten) Profils
    winner: int                   # Sieger dieses Profils
    counts2: tuple | None = None  # zweites Profil (Monotonie, Teilnahme, Konsistenz: das Vergleichsprofil; Konsistenz: die zweite Gruppe)
    winner2: int | None = None    # Sieger des zweiten Profils bzw. der Gesamtheit (Konsistenz)
    detail: tuple = ()            # je Eigenschaft: Condorcet: (Condorcet-Sieger,), Pareto: (a, b), Monotonie/Teilnahme: (Rangfolge des Wählers,), IIA: (gestrichener Kandidat,)


def check_profile(axiom: str, rule: str, c: np.ndarray, m: int, tiebreak: np.ndarray, tie_free: bool = False):
    """Prüft eine Eigenschaft an EINEM Profil (nicht Konsistenz, die braucht zwei Gruppen). Rückgabe: Verletzung oder None."""
    n = int(c.sum())
    w, t = outcome(rule, c, m, tiebreak)
    if tie_free and t:
        return None
    pos, before, _ = ranking_tables(m)
    rk = all_rankings(m)
    base = dict(axiom=axiom, rule=rule, m=m, n=n, counts=tuple(int(x) for x in c), winner=w)
    if axiom == "condorcet":
        cw = condorcet_winner(pairwise(c, m))
        if cw is not None and cw != w:
            return Violation(**base, detail=(cw,))
    elif axiom == "pareto":
        for a in range(m):
            if a != w and int((c * before[:, a, w]).sum()) == n and n > 0:      # alle Wähler reihen a vor dem Sieger w
                return Violation(**base, detail=(a, w))
    elif axiom == "monotonie":
        for i in np.flatnonzero(c > 0):
            j = raise_index(int(i), w, m)
            if j is None:
                continue
            c2 = c.copy()
            c2[i] -= 1
            c2[j] += 1
            w2, t2 = outcome(rule, c2, m, tiebreak)
            if w2 != w and not (tie_free and t2):
                return Violation(**base, counts2=tuple(int(x) for x in c2), winner2=w2, detail=(tuple(rk[i].tolist()),))
    elif axiom == "teilnahme":
        for i in range(len(c)):
            c2 = c.copy()
            c2[i] += 1
            w2, t2 = outcome(rule, c2, m, tiebreak)
            if pos[i, w2] > pos[i, w] and not (tie_free and t2):                  # mit der Stimme des neuen Wählers steht er schlechter da als ohne
                return Violation(**base, counts2=tuple(int(x) for x in c2), winner2=w2, detail=(tuple(rk[i].tolist()),))
    elif axiom == "iia":
        if m < 3:
            return None
        for x in range(m):
            if x == w:
                continue
            c2 = drop_candidate(c, m, x)
            w2, t2 = outcome(rule, c2, m - 1, np.delete(tiebreak, x))
            w2_old = w2 if w2 < x else w2 + 1                                    # zurück auf die ursprüngliche Nummerierung
            if w2_old != w and not (tie_free and t2):
                return Violation(**base, counts2=tuple(int(v) for v in c2), winner2=w2_old, detail=(x,))
    else:
        raise ValueError(f"unbekannte Eigenschaft: {axiom}")
    return None


def check_consistency(rule: str, c1: np.ndarray, c2: np.ndarray, m: int, tiebreak: np.ndarray, tie_free: bool = False):
    """Konsistenz: wählen beide Gruppen denselben Sieger, muss die Gesamtheit ihn wählen."""
    w1, t1 = outcome(rule, c1, m, tiebreak)
    w2, t2 = outcome(rule, c2, m, tiebreak)
    if w1 != w2 or (tie_free and (t1 or t2)):
        return None
    w3, t3 = outcome(rule, c1 + c2, m, tiebreak)
    if w3 != w1 and not (tie_free and t3):
        return Violation("konsistenz", rule, m, int((c1 + c2).sum()), tuple(int(x) for x in c1), w1, tuple(int(x) for x in c2), w3)
    return None


def smallest_violation(axiom: str, rule: str, m: int, tiebreak: np.ndarray, max_n: int, tie_free: bool = False):
    """Kleinstes Gegenbeispiel (nach der Zahl der Wähler, dann lexikographisch) durch Aufzählung ALLER Profile bis max_n Wähler; None, wenn bis dahin keines existiert."""
    k = len(all_rankings(m))
    if axiom == "konsistenz":
        by_n = {}
        for n in range(1, max_n):
            by_n[n] = [(np.array(comp), *outcome(rule, np.array(comp), m, tiebreak)) for comp in compositions(n, k)]
        for total in range(2, max_n + 1):
            for n1 in range(1, total // 2 + 1):
                for c1, w1, t1 in by_n[n1]:
                    for c2, w2, t2 in by_n[total - n1]:
                        if w1 != w2 or (tie_free and (t1 or t2)):
                            continue
                        v = check_consistency(rule, c1, c2, m, tiebreak, tie_free)
                        if v is not None:
                            return v
        return None
    for n in range(1, max_n + 1):
        for comp in compositions(n, k):
            v = check_profile(axiom, rule, np.array(comp), m, tiebreak, tie_free)
            if v is not None:
                return v
    return None
