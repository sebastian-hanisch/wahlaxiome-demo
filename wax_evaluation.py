"""Auswertung: die Suche nach dem kleinsten Gegenbeispiel, Tabelle aller Regeln und Eigenschaften, zwei Messreihen mit festem Programm, alle Verdikte als reine Funktionen."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

import wax_algorithm as A
import wax_constants as C
from wax_scenario import make_profile


def num(x: float, digits: int = 1) -> str:
    return f"{x:.{digits}f}".replace(".", ",")


def pct(x: float, digits: int = 0) -> str:
    return f"{100 * x:.{digits}f} %".replace(".", ",")


def label(c) -> str:
    return C.CANDIDATE_LABELS[int(c)]


def ranking_text(r) -> str:
    return " > ".join(label(c) for c in r)


def short_rule(rule: str) -> str:
    """Regelname ohne den Zusatz in Klammern: „Sofortstichwahl“, „Copeland“."""
    return C.RULES[rule].split(" (")[0]


def profile_text(c, m: int) -> str:
    """Zählvektor als Text: „2 × A > B > C, 1 × B > A > C“."""
    rk = A.all_rankings(m)
    return ", ".join(f"{int(c[i])} × {ranking_text(rk[i])}" for i in range(len(c)) if c[i] > 0)


def effective_max_n(m: int, max_n: int) -> int:
    """Größte Wählerzahl der Suche: bei vier Kandidaten (24 Rangfolgen) endet die Aufzählung bei 4 Wählern."""
    return min(max_n, C.N_LIMIT[m])


@dataclass(frozen=True)
class Settings:
    axiom: str = C.DEFAULT_AXIOM
    rule: str = C.DEFAULT_RULE
    m: int = C.DEFAULT_M
    max_n: int = C.DEFAULT_N
    tie_free: bool = False


@dataclass(frozen=True)
class Analysis:
    settings: Settings
    searched_to: int
    violation: A.Violation | None


def tiebreak_of(m: int) -> np.ndarray:
    """Gleichstand: A vor B vor C vor D (festgelegt, damit das Gegenbeispiel nicht vom Zufall abhängt)."""
    return np.arange(m)


def analyse(settings: Settings) -> Analysis:
    up_to = effective_max_n(settings.m, settings.max_n)
    v = A.smallest_violation(settings.axiom, settings.rule, settings.m, tiebreak_of(settings.m), up_to, settings.tie_free)
    return Analysis(settings, up_to, v)


def describe(v: A.Violation) -> list[str]:
    """Das Gegenbeispiel in Worten, eine Zeile je Schritt (Profile und Sieger aus dem Verstoß, ohne weitere Rechnung)."""
    m = v.m
    c1 = np.array(v.counts)
    prof = profile_text(c1, m)
    if v.axiom == "condorcet":
        return [f"Profil mit {v.n} Wählern: {prof}.", f"Gewählt wird **{label(v.winner)}**, aber **{label(v.detail[0])}** schlägt jeden anderen Kandidaten im Paarvergleich mit Mehrheit."]
    if v.axiom == "pareto":
        return [f"Profil mit {v.n} Wählern: {prof}.", f"Alle Wähler reihen {label(v.detail[0])} vor {label(v.detail[1])}, trotzdem gewinnt **{label(v.winner)}**."]
    c2 = np.array(v.counts2)
    prof2 = profile_text(c2, m - 1 if v.axiom == "iia" else m)
    if v.axiom == "monotonie":
        return [f"Profil mit {v.n} Wählern: {prof}. Sieger: **{label(v.winner)}**.",
                f"Ein Wähler mit der Rangfolge {ranking_text(v.detail[0])} rückt {label(v.winner)} einen Platz nach oben: {prof2}.", f"Jetzt gewinnt **{label(v.winner2)}**, obwohl {label(v.winner)} Zuspruch gewonnen hat."]
    if v.axiom == "teilnahme":
        return [f"Profil mit {v.n} Wählern: {prof}. Sieger: **{label(v.winner)}**.",
                f"Kommt ein Wähler mit der Rangfolge {ranking_text(v.detail[0])} dazu: {prof2}.", f"Jetzt gewinnt **{label(v.winner2)}**, und den findet er schlechter als {label(v.winner)}: zu Hause bleiben wäre besser gewesen."]
    if v.axiom == "konsistenz":
        return [f"Gruppe 1: {prof}: Sieger **{label(v.winner)}**.", f"Gruppe 2: {prof2}: Sieger ebenfalls **{label(v.winner)}**.", f"Beide zusammen ({v.n} Wähler): Sieger **{label(v.winner2)}**."]
    if v.axiom == "iia":
        x = label(v.detail[0])
        return [f"Profil mit {v.n} Wählern: {prof}. Sieger: **{label(v.winner)}**.",
                f"Scheidet der Verlierer {x} aus (er wird aus allen Rangfolgen gestrichen), bleiben: {prof2.translate(_relabel_table(v.detail[0], m))}.", f"Jetzt gewinnt **{label(v.winner2)}** statt {label(v.winner)}."]
    raise ValueError(f"unbekannte Eigenschaft: {v.axiom}")


def _relabel_table(x: int, m: int):
    """Das gestrichene Profil trägt die Kandidaten von 0 an neu nummeriert; für die Anzeige zurück auf die alten Buchstaben (ohne den gestrichenen)."""
    old = [c for c in range(m) if c != x]
    return {ord(C.CANDIDATE_LABELS[i]): C.CANDIDATE_LABELS[o] for i, o in enumerate(old)}


def check_description(v: A.Violation) -> str:
    """Kurzfassung für die Tabellen: Wählerzahl und Eigenschaft in einem Satz."""
    return f"{v.n} Wähler: {C.AXIOMS[v.axiom]} bei {short_rule(v.rule)} verletzt"


def verdict_state(a: Analysis) -> tuple[str, str]:
    """Verdikt der Kernfrage als (Art, Text), rein: die App ruft st.<Art>(Text), der Test prüft jede Zahl im Text."""
    s = a.settings
    name, axiom = short_rule(s.rule), C.AXIOMS[s.axiom]
    mode = " ohne Hilfe eines Gleichstands" if s.tie_free else ""
    if a.violation is None:
        capped = f" (bei {s.m} Kandidaten endet die Aufzählung bei {C.N_LIMIT[s.m]} Wählern)" if a.searched_to < s.max_n else ""
        extra = ""
        if s.axiom == "condorcet" and s.rule == "copeland":
            extra = " Das ist kein Zufall: Copeland wählt per Definition den Kandidaten mit den meisten Paarsiegen, und ein Condorcet-Sieger hat alle."
        if s.m == 2:
            extra = " Bei zwei Kandidaten gelten alle diese Eigenschaften für jede der vier Regeln."
        return "success", f"Bei {name} fand die Aufzählung aller Profile mit bis zu {a.searched_to} Wählern{mode} **kein Gegenbeispiel** zu „{axiom}“{capped}.{extra} Das ist kein Beweis für größere Profile."
    v = a.violation
    return "warning", f"Bei {name} verletzt schon ein Profil mit **{v.n} Wählern**{mode} die Eigenschaft „{axiom}“ (Aufzählung aller Profile, A vor B vor C bei Gleichstand)."


# --- Tabelle aller Regeln und Eigenschaften ---------------------------------------------------------------------------------------------

def table_cells(m: int = C.TABLE_M, max_n: int = C.TABLE_N) -> list[dict]:
    """Je Eigenschaft und Regel die kleinste Wählerzahl eines Gegenbeispiels, mit und ohne Gleichstand (None: bis max_n keines)."""
    tb = tiebreak_of(m)
    cells = []
    for axiom in C.AXIOMS:
        for rule in C.RULES:
            cell = {"axiom": axiom, "rule": rule, "m": m, "max_n": max_n}
            for key, free in (("with_tie", False), ("tie_free", True)):
                v = A.smallest_violation(axiom, rule, m, tb, max_n, free)
                cell[key] = None if v is None else v.n
            cells.append(cell)
    return cells


def table_rows(cells: list[dict], key: str) -> list[dict]:
    """Zeilen für st.table: je Eigenschaft eine Zeile, je Regel eine Spalte „n Wähler“ oder „–“ (key: with_tie oder tie_free)."""
    rows = []
    for axiom in C.AXIOMS:
        row = {"Eigenschaft": C.AXIOMS[axiom]}
        for rule in C.RULES:
            n = next(c for c in cells if c["axiom"] == axiom and c["rule"] == rule)[key]
            row[short_rule(rule)] = "–" if n is None else f"{n} Wähler"
        rows.append(row)
    return rows


def verdict_table(cells: list[dict]) -> tuple[str, str]:
    """Verdikt der Tabelle: wie viele der 24 Zellen haben ein Gegenbeispiel (mit Los, ohne Gleichstand), und welche Regeln bleiben in beiden Fällen sauber."""
    total = len(cells)
    with_tie = sum(c["with_tie"] is not None for c in cells)
    free = sum(c["tie_free"] is not None for c in cells)
    clean = [short_rule(r) for r in C.RULES if all(c["with_tie"] is None for c in cells if c["rule"] == r)]
    m, max_n = cells[0]["m"], cells[0]["max_n"]
    tail = f" Keine Verletzung bei {', '.join(clean)}." if clean else " Jede Regel verletzt mindestens eine der Eigenschaften."
    return "info", (f"Bei {m} Kandidaten und bis zu {max_n} Wählern gibt es in {with_tie} von {total} Zellen ein Gegenbeispiel mit dem Los, in {free} von {total} auch ohne Hilfe eines Gleichstands.{tail}")


# --- Häufigkeit in Zufallsprofilen --------------------------------------------------------------------------------------------------------

def violates(axiom: str, rule: str, profile: np.ndarray, tiebreak: np.ndarray, rng: np.random.Generator, tie_free: bool) -> bool:
    m = profile.shape[1]
    c = A.counts_of(profile)
    if axiom == "konsistenz":
        order = rng.permutation(len(profile))
        half = len(profile) // 2
        c1, c2 = A.counts_of(profile[order[:half]]), A.counts_of(profile[order[half:]])
        return A.check_consistency(rule, c1, c2, m, tiebreak, tie_free) is not None
    return A.check_profile(axiom, rule, c, m, tiebreak, tie_free) is not None


def violation_share(axiom: str, rule: str, model: str, m: int, n: int, runs: int, seed: int) -> dict:
    """Anteil der Profile (je `runs` feste Seeds), in denen die Eigenschaft verletzt ist: mit dem Los und ohne Hilfe eines Gleichstands."""
    out = {"share": 0, "share_free": 0}
    for j in range(runs):
        profile, tiebreak = make_profile(model, m, n, seed + j)
        rng = np.random.default_rng(seed + j + 10_000)
        out["share"] += violates(axiom, rule, profile, tiebreak, rng, False)
        out["share_free"] += violates(axiom, rule, profile, tiebreak, np.random.default_rng(seed + j + 10_000), True)
    return {k: v / runs for k, v in out.items()}


def series_frequency(ms=C.SERIES_MS, n: int = C.SERIES_N, runs: int = C.SERIES_RUNS, seed: int = C.SERIES_SEED) -> list[dict]:
    """Zufallsprofile: je Eigenschaft, Regel und Kandidatenzahl der Anteil der Profile mit einer Verletzung (mit Los und ohne Hilfe eines Gleichstands)."""
    rows = []
    for m in ms:
        for axiom in C.AXIOMS:
            for rule in C.RULES:
                rows.append({"axiom": axiom, "rule": rule, "m": m, "n": n, "runs": runs, **violation_share(axiom, rule, "random", m, n, runs, seed)})
    return rows


def series_models(m: int = C.SERIES_MODEL_M, n: int = C.SERIES_N, runs: int = C.SERIES_RUNS, seed: int = C.SERIES_SEED) -> list[dict]:
    """Dieselbe Frage für die drei Profilmodelle bei fester Kandidaten- und Wählerzahl (nur Eigenschaften, die in Zufallsprofilen vorkommen können)."""
    rows = []
    for model in C.MODELS:
        for axiom in ("condorcet", "monotonie", "teilnahme", "konsistenz", "iia"):
            for rule in C.RULES:
                rows.append({"model": model, "axiom": axiom, "rule": rule, "m": m, "n": n, "runs": runs, **violation_share(axiom, rule, model, m, n, runs, seed)})
    return rows


def frequency_rows(rows: list[dict], m: int) -> list[dict]:
    """Zeilen für st.table: je Eigenschaft eine Zeile, je Regel eine Spalte „Anteil (davon ohne Gleichstand)“."""
    out = []
    for axiom in C.AXIOMS:
        row = {"Eigenschaft": C.AXIOMS[axiom]}
        for rule in C.RULES:
            r = next(x for x in rows if x["axiom"] == axiom and x["rule"] == rule and x["m"] == m)
            row[short_rule(rule)] = f"{pct(r['share'])} ({pct(r['share_free'])})"
        out.append(row)
    return out


def verdict_frequency(rows: list[dict]) -> tuple[str, str]:
    """Verdikt der Reihe 1: die häufigste Verletzung bei der größten Kandidatenzahl und was ohne Gleichstand davon bleibt."""
    m = max(r["m"] for r in rows)
    cell = [r for r in rows if r["m"] == m]
    top = max(cell, key=lambda r: r["share"])
    zero = sorted({C.AXIOMS[r["axiom"]] for r in cell if r["share"] == 0.0 and all(x["share"] == 0.0 for x in cell if x["axiom"] == r["axiom"])})
    text = (f"Bei {m} Kandidaten und {top['n']} Wählern ist die Eigenschaft „{C.AXIOMS[top['axiom']]}“ bei {short_rule(top['rule'])} am häufigsten verletzt: in {pct(top['share'])} der Zufallsprofile, "
            f"in {pct(top['share_free'])} auch ohne Hilfe eines Gleichstands.")
    if zero:
        text += f" Nie verletzt (bei allen vier Regeln): {', '.join(zero)}."
    return "info", text


def verdict_models(rows: list[dict]) -> tuple[str, str]:
    """Verdikt der Reihe 2: je Profilmodell die häufigste Verletzung (Eigenschaft und Regel) mit dem Anteil der Profile."""
    parts = []
    for model in C.MODELS:
        cell = [r for r in rows if r["model"] == model]
        top = max(cell, key=lambda r: r["share"])
        parts.append(f"{C.MODELS[model].split(' (')[0]}: {C.AXIOMS[top['axiom']]} bei {short_rule(top['rule'])} ({pct(top['share'])})")
    r0 = rows[0]
    return "info", f"Die häufigste Verletzung je Profilmodell ({r0['m']} Kandidaten, {r0['n']} Wähler): " + "; ".join(parts) + "."
