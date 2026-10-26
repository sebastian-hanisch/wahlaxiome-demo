"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import wax_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def _short(rule):
    return C.RULES[rule].split(" (")[0]


def build_table(cells, key="with_tie"):
    """Karte aller Regeln und Eigenschaften: in der Zelle die kleinste Wählerzahl eines Gegenbeispiels („–“: bis zur Grenze keines); je kleiner die Zahl, desto kräftiger die Farbe."""
    axioms, rules = list(C.AXIOMS), list(C.RULES)
    z, text = [], []
    for axiom in axioms:
        zr, tr = [], []
        for rule in rules:
            n = next(c for c in cells if c["axiom"] == axiom and c["rule"] == rule)[key]
            zr.append(None if n is None else n)
            tr.append("–" if n is None else str(n))
        z.append(zr)
        text.append(tr)
    fig = go.Figure(go.Heatmap(z=z, x=[_short(r) for r in rules], y=[C.AXIOMS[a] for a in axioms], text=text, texttemplate="%{text}", colorscale="Reds", reversescale=True, showscale=False,
                               zmin=1, zmax=cells[0]["max_n"] + 2, xgap=3, ygap=3, hovertemplate="%{y}, %{x}: kleinstes Gegenbeispiel mit %{text} Wählern<extra></extra>"))
    fig.update_xaxes(side="top")
    fig.update_yaxes(autorange="reversed")
    return _base(fig, height=330)


def build_frequency(rows, m, key="share"):
    """Anteil der Zufallsprofile mit einer Verletzung, je Eigenschaft eine Gruppe, je Regel ein Balken (key: share mit Los, share_free ohne Hilfe eines Gleichstands)."""
    fig = go.Figure()
    axioms = list(C.AXIOMS)
    for rule in C.RULES:
        vals = [next(r[key] for r in rows if r["axiom"] == a and r["rule"] == rule and r["m"] == m) for a in axioms]
        fig.add_trace(go.Bar(x=[C.AXIOMS[a] for a in axioms], y=vals, name=_short(rule), marker_color=C.RULE_COLORS[rule],
                             text=[f"{100 * v:.0f} %" if v > 0 else "" for v in vals], textposition="outside", hovertemplate="%{x}: %{y:.3f}<extra>" + _short(rule) + "</extra>"))
    fig.update_layout(barmode="group")
    fig.update_xaxes(tickangle=-20)
    fig.update_yaxes(title_text="Anteil der Profile mit einer Verletzung", range=[0, 0.5], tickformat=".0%")
    return _base(fig, height=380)


def build_models(rows, top=10):
    """Die häufigsten Verletzungen (Eigenschaft und Regel) je Profilmodell als gruppierte Balken."""
    combos = {}
    for r in rows:
        combos[(r["axiom"], r["rule"])] = max(combos.get((r["axiom"], r["rule"]), 0.0), r["share"])
    best = sorted(combos, key=lambda k: -combos[k])[:top]
    palette = {"random": "#4c78a8", "single": "#e8a838", "camps": "#2F6B65"}
    fig = go.Figure()
    for model in C.MODELS:
        vals = [next(r["share"] for r in rows if r["model"] == model and r["axiom"] == a and r["rule"] == rule) for a, rule in best]
        fig.add_trace(go.Bar(x=[f"{C.AXIOMS[a].split(' ')[0]}, {_short(rule)}" for a, rule in best], y=vals, name=C.MODELS[model].split(" (")[0], marker_color=palette[model],
                             text=[f"{100 * v:.0f} %" if v > 0 else "" for v in vals], textposition="outside", hovertemplate="%{x}: %{y:.3f}<extra>" + C.MODELS[model].split(" (")[0] + "</extra>"))
    fig.update_layout(barmode="group")
    fig.update_xaxes(tickangle=-25)
    fig.update_yaxes(title_text="Anteil der Profile mit einer Verletzung", range=[0, 1.0], tickformat=".0%")
    return _base(fig, height=400)
