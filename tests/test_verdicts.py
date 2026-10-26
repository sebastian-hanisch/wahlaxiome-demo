"""Verdikte und Texte (reine Funktionen): Art und jede Zahl im Text an handgesetzten Werten, jeder Zweig."""

import numpy as np

import wax_algorithm as A
import wax_constants as C
import wax_evaluation as ev
from conftest import counts
from wax_evaluation import Settings


def test_num_pct_label_and_texts():
    assert ev.num(3.14159, 2) == "3,14" and ev.pct(0.456) == "46 %" and ev.pct(0.0456, 1) == "4,6 %" and ev.label(0) == "A" and ev.label(3) == "D"
    assert ev.ranking_text((2, 1, 0)) == "C > B > A" and ev.short_rule("irv") == "Sofortstichwahl" and ev.short_rule("copeland") == "Copeland"
    assert ev.profile_text(counts(3, (1, "BAC"), (2, "CAB")), 3) == "1 × B > A > C, 2 × C > A > B"
    assert ev.effective_max_n(3, 9) == 9 and ev.effective_max_n(4, 9) == 4 and ev.effective_max_n(4, 3) == 3 and ev.effective_max_n(2, 9) == 9


def test_verdict_when_a_counterexample_exists():
    a = ev.analyse(Settings("condorcet", "plurality", 3, 8, False))
    assert a.searched_to == 8 and a.violation.n == 3
    kind, text = ev.verdict_state(a)
    assert kind == "warning"
    assert text == "Bei Mehrheitswahl verletzt schon ein Profil mit **3 Wählern** die Eigenschaft „Condorcet-Konsistenz“ (Aufzählung aller Profile, A vor B vor C bei Gleichstand)."
    kind, text = ev.verdict_state(ev.analyse(Settings("condorcet", "plurality", 3, 8, True)))
    assert text == "Bei Mehrheitswahl verletzt schon ein Profil mit **7 Wählern** ohne Hilfe eines Gleichstands die Eigenschaft „Condorcet-Konsistenz“ (Aufzählung aller Profile, A vor B vor C bei Gleichstand)."


def test_verdict_without_a_counterexample():
    kind, text = ev.verdict_state(ev.analyse(Settings("condorcet", "copeland", 3, 6, False)))
    assert kind == "success"
    assert text == ("Bei Copeland fand die Aufzählung aller Profile mit bis zu 6 Wählern **kein Gegenbeispiel** zu „Condorcet-Konsistenz“. "
                    "Das ist kein Zufall: Copeland wählt per Definition den Kandidaten mit den meisten Paarsiegen, und ein Condorcet-Sieger hat alle. Das ist kein Beweis für größere Profile.")
    kind, text = ev.verdict_state(ev.analyse(Settings("pareto", "plurality", 4, 9, False)))
    assert kind == "success"
    assert text == ("Bei Mehrheitswahl fand die Aufzählung aller Profile mit bis zu 4 Wählern **kein Gegenbeispiel** zu „Pareto-Effizienz“ (bei 4 Kandidaten endet die Aufzählung bei 4 Wählern)."
                    " Das ist kein Beweis für größere Profile.")


def test_verdict_for_two_candidates():
    kind, text = ev.verdict_state(ev.analyse(Settings("iia", "borda", 2, 6, False)))
    assert kind == "success" and "Bei zwei Kandidaten gelten alle diese Eigenschaften für jede der vier Regeln." in text and "bis zu 6 Wählern" in text


def test_descriptions_for_every_property():
    d = ev.describe(ev.analyse(Settings("condorcet", "plurality", 3, 8, False)).violation)
    assert d == ["Profil mit 3 Wählern: 1 × A > B > C, 1 × B > A > C, 1 × C > B > A.", "Gewählt wird **A**, aber **B** schlägt jeden anderen Kandidaten im Paarvergleich mit Mehrheit."]
    d = ev.describe(ev.analyse(Settings("monotonie", "irv", 3, 7, False)).violation)
    assert d == ["Profil mit 7 Wählern: 2 × A > B > C, 2 × B > A > C, 1 × C > A > B, 2 × C > B > A. Sieger: **A**.",
                 "Ein Wähler mit der Rangfolge C > A > B rückt A einen Platz nach oben: 2 × A > B > C, 1 × A > C > B, 2 × B > A > C, 2 × C > B > A.", "Jetzt gewinnt **B**, obwohl A Zuspruch gewonnen hat."]
    d = ev.describe(ev.analyse(Settings("teilnahme", "copeland", 3, 6, False)).violation)
    assert d == ["Profil mit 4 Wählern: 1 × A > B > C, 1 × B > C > A, 2 × C > A > B. Sieger: **C**.",
                 "Kommt ein Wähler mit der Rangfolge B > C > A dazu: 1 × A > B > C, 2 × B > C > A, 2 × C > A > B.", "Jetzt gewinnt **A**, und den findet er schlechter als C: zu Hause bleiben wäre besser gewesen."]
    d = ev.describe(ev.analyse(Settings("konsistenz", "irv", 3, 8, False)).violation)
    assert d == ["Gruppe 1: 1 × A > B > C, 1 × C > A > B: Sieger **A**.", "Gruppe 2: 1 × A > B > C, 1 × B > C > A, 1 × C > A > B: Sieger ebenfalls **A**.", "Beide zusammen (5 Wähler): Sieger **C**."]
    d = ev.describe(ev.analyse(Settings("iia", "borda", 3, 6, True)).violation)
    assert d == ["Profil mit 5 Wählern: 3 × A > B > C, 2 × B > C > A. Sieger: **B**.",
                 "Scheidet der Verlierer C aus (er wird aus allen Rangfolgen gestrichen), bleiben: 3 × A > B, 2 × B > A.", "Jetzt gewinnt **A** statt B."]
    d = ev.describe(A.Violation("pareto", "plurality", 3, 3, tuple(counts(3, (3, "ABC"))), 2, detail=(0, 2)))
    assert d == ["Profil mit 3 Wählern: 3 × A > B > C.", "Alle Wähler reihen A vor C, trotzdem gewinnt **C**."]


def test_iia_description_relabels_the_remaining_candidates():
    # Gestrichen wird B: aus A,C,D werden 0,1,2; in der Anzeige tragen sie wieder ihre alten Buchstaben.
    c = counts(4, (1, "ABCD"), (1, "CDAB"))
    v = A.Violation("iia", "plurality", 4, 2, tuple(c), 0, tuple(A.drop_candidate(c, 4, 1)), 2, detail=(1,))
    assert ev.describe(v)[1] == "Scheidet der Verlierer B aus (er wird aus allen Rangfolgen gestrichen), bleiben: 1 × A > C > D, 1 × C > D > A."


def make_cells(with_tie, tie_free, m=3, max_n=8):
    cells = []
    for axiom in C.AXIOMS:
        for rule in C.RULES:
            cells.append({"axiom": axiom, "rule": rule, "m": m, "max_n": max_n, "with_tie": with_tie.get((axiom, rule)), "tie_free": tie_free.get((axiom, rule))})
    return cells


def test_table_rows_and_verdict_by_hand():
    cells = make_cells({("condorcet", "plurality"): 3, ("condorcet", "borda"): 3, ("monotonie", "irv"): 7, ("iia", "plurality"): 2, ("iia", "borda"): 2, ("iia", "irv"): 2},
                       {("condorcet", "plurality"): 7, ("iia", "irv"): 5})
    rows = ev.table_rows(cells, "with_tie")
    assert [r["Eigenschaft"] for r in rows] == list(C.AXIOMS.values())
    assert rows[0] == {"Eigenschaft": "Condorcet-Konsistenz", "Mehrheitswahl": "3 Wähler", "Borda-Zählung": "3 Wähler", "Copeland": "–", "Sofortstichwahl": "–"}
    assert rows[2]["Sofortstichwahl"] == "7 Wähler" and rows[1]["Mehrheitswahl"] == "–"
    assert ev.table_rows(cells, "tie_free")[5]["Sofortstichwahl"] == "5 Wähler"
    kind, text = ev.verdict_table(cells)
    assert kind == "info"
    assert text == "Bei 3 Kandidaten und bis zu 8 Wählern gibt es in 6 von 24 Zellen ein Gegenbeispiel mit dem Los, in 2 von 24 auch ohne Hilfe eines Gleichstands. Keine Verletzung bei Copeland."
    kind, text = ev.verdict_table(make_cells({(a, r): 3 for a in C.AXIOMS for r in C.RULES}, {}))
    assert text.endswith("in 0 von 24 auch ohne Hilfe eines Gleichstands. Jede Regel verletzt mindestens eine der Eigenschaften.")


def frequency_rows():
    rows = []
    for m in (3, 4):
        for axiom in C.AXIOMS:
            for rule in C.RULES:
                share = share_free = 0.0
                if m == 4 and axiom == "iia" and rule == "plurality":
                    share, share_free = 0.29, 0.08
                if m == 4 and axiom == "condorcet" and rule == "plurality":
                    share, share_free = 0.23, 0.13
                rows.append({"axiom": axiom, "rule": rule, "m": m, "n": 21, "runs": 150, "share": share, "share_free": share_free})
    return rows


def test_frequency_rows_and_verdict_by_hand():
    rows = ev.frequency_rows(frequency_rows(), 4)
    assert rows[0] == {"Eigenschaft": "Condorcet-Konsistenz", "Mehrheitswahl": "23 % (13 %)", "Borda-Zählung": "0 % (0 %)", "Copeland": "0 % (0 %)", "Sofortstichwahl": "0 % (0 %)"}
    assert rows[5]["Mehrheitswahl"] == "29 % (8 %)"
    kind, text = ev.verdict_frequency(frequency_rows())
    assert kind == "info"
    assert text == ("Bei 4 Kandidaten und 21 Wählern ist die Eigenschaft „Unabhängigkeit vom Ausscheiden eines Verlierers“ bei Mehrheitswahl am häufigsten verletzt: in 29 % der Zufallsprofile, "
                    "in 8 % auch ohne Hilfe eines Gleichstands. Nie verletzt (bei allen vier Regeln): Konsistenz, Monotonie, Pareto-Effizienz, Teilnahme.")


def test_models_verdict_by_hand():
    rows = []
    tops = {"random": ("iia", "plurality", 0.287), "single": ("iia", "plurality", 0.813), "camps": ("condorcet", "plurality", 0.307)}
    for model in C.MODELS:
        for axiom in ("condorcet", "monotonie", "teilnahme", "konsistenz", "iia"):
            for rule in C.RULES:
                share = tops[model][2] if (axiom, rule) == tops[model][:2] else 0.0
                rows.append({"model": model, "axiom": axiom, "rule": rule, "m": 4, "n": 21, "runs": 150, "share": share, "share_free": 0.0})
    kind, text = ev.verdict_models(rows)
    assert kind == "info"
    assert text == ("Die häufigste Verletzung je Profilmodell (4 Kandidaten, 21 Wähler): Zufall: Unabhängigkeit vom Ausscheiden eines Verlierers bei Mehrheitswahl (29 %); "
                    "einspitzig: Unabhängigkeit vom Ausscheiden eines Verlierers bei Mehrheitswahl (81 %); zwei Lager: Condorcet-Konsistenz bei Mehrheitswahl (31 %).")
