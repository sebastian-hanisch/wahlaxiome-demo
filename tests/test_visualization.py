"""Abbildungen: Spuren je Figur, Werte, Achsen gesperrt."""

import wax_constants as C
import wax_visualization as V


def _locked(fig):
    return fig.layout.xaxis.fixedrange is True and fig.layout.yaxis.fixedrange is True


def cells():
    out = []
    for axiom in C.AXIOMS:
        for rule in C.RULES:
            out.append({"axiom": axiom, "rule": rule, "m": 3, "max_n": 8, "with_tie": 3 if (axiom, rule) == ("condorcet", "plurality") else None, "tie_free": None})
    return out


def test_table_figure_by_hand():
    fig = V.build_table(cells(), "with_tie")
    assert _locked(fig) and list(fig.data[0].x) == ["Mehrheitswahl", "Borda-Zählung", "Copeland", "Sofortstichwahl"] and list(fig.data[0].y) == list(C.AXIOMS.values())
    assert fig.data[0].z[0][0] == 3 and fig.data[0].z[0][1] is None and fig.data[0].text[0][0] == "3" and fig.data[0].text[0][1] == "–"
    free = V.build_table(cells(), "tie_free")
    assert all(v is None for row in free.data[0].z for v in row)


def frequency_rows():
    return [{"axiom": a, "rule": r, "m": m, "n": 21, "runs": 10, "share": 0.1, "share_free": 0.05} for m in (3, 4) for a in C.AXIOMS for r in C.RULES]


def test_frequency_figure_has_a_bar_per_rule():
    fig = V.build_frequency(frequency_rows(), 4)
    assert [t.name for t in fig.data] == ["Mehrheitswahl", "Borda-Zählung", "Copeland", "Sofortstichwahl"] and _locked(fig) and list(fig.data[0].y) == [0.1] * 6
    assert list(V.build_frequency(frequency_rows(), 3, "share_free").data[1].y) == [0.05] * 6


def test_models_figure_picks_the_most_frequent_combinations():
    rows = []
    for model in C.MODELS:
        for axiom in ("condorcet", "monotonie", "teilnahme", "konsistenz", "iia"):
            for rule in C.RULES:
                rows.append({"model": model, "axiom": axiom, "rule": rule, "m": 4, "n": 21, "share": 0.5 if (axiom, rule) == ("iia", "plurality") else 0.01})
    fig = V.build_models(rows, top=3)
    assert [t.name for t in fig.data] == ["Zufall", "einspitzig", "zwei Lager"] and _locked(fig) and len(fig.data[0].x) == 3 and fig.data[0].x[0].startswith("Unabhängigkeit")
    assert fig.data[0].y[0] == 0.5
