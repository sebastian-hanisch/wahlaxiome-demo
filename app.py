"""Wahlregeln und ihre Axiome: welche Regel verletzt was? - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück der Linie „Abstimmen und Fair Teilen“: sechs Eigenschaften, die man von einer Wahlregel erwartet (Condorcet-Konsistenz, Pareto, Monotonie, Teilnahme,
Konsistenz, Unabhängigkeit vom Ausscheiden eines Verlierers), vier Regeln und die Suche nach dem KLEINSTEN Gegenbeispiel durch Aufzählung aller Profile. Der Kern liegt in wax_algorithm.py.

Lauffähig mit: streamlit run app.py
"""

import time

import streamlit as st

import wax_constants as C
import wax_evaluation as ev
from wax_evaluation import Settings, analyse, describe, frequency_rows, num, short_rule, table_rows, verdict_frequency, verdict_models, verdict_state, verdict_table
from wax_layout import dunkles_design, kopf_css
from wax_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    sidebar_presets,
    sync_query_params,
)
from wax_visualization import build_frequency, build_models, build_table

st.set_page_config(page_title="Wahlaxiome – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _table():
    return ev.table_cells()


@st.cache_data(show_spinner=False)
def _series_frequency():
    return ev.series_frequency()


@st.cache_data(show_spinner=False)
def _series_models():
    return ev.series_models()


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in wax_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("📏 Wahlregeln und ihre Axiome: welche Regel verletzt was?")
st.markdown(
    """
Was erwartet man von einer **fairen Wahlregel**? Zum Beispiel: wer jeden anderen im Paarvergleich schlägt, soll gewinnen (**Condorcet-Konsistenz**); wer mehr Zuspruch bekommt, soll nicht verlieren (**Monotonie**); wer mitwählt, soll nicht schlechter dastehen als wer zu Hause bleibt (**Teilnahme**).
Jede dieser Eigenschaften klingt selbstverständlich, und **keine der vier gängigen Regeln erfüllt alle**. Die Demo sucht für jede Regel und jede Eigenschaft das **kleinste Gegenbeispiel** durch Aufzählung **aller** Profile bis zu einer Wählerzahl und prüft jedes gefundene Beispiel nach.
Sie zeigt außerdem, **wie oft** die Verletzung in Zufallsprofilen vorkommt und **wie viele Gegenbeispiele nur vom Gleichstand leben**: bei einem Gleichstand entscheidet ein festes Los, und mancher „Verstoß“ verschwindet, wenn man nur Beispiele ohne Gleichstand zulässt.
Vorgänger: `wahlregeln-demo` (die Regeln auf denselben Profilen) und `taktisch-waehlen-demo` (Manipulation durch einen Wähler).

Weiter unten: der Abschnitt **🔬 Tabelle und Messreihen**, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So wird gesucht", expanded=True):
    st.markdown(
        """
1. **Profile** werden als Zählvektoren über alle Rangfolgen geführt (Wähler mit derselben Rangfolge sind austauschbar). Die Suche geht Wählerzahl für Wählerzahl vor und zählt **alle** Zerlegungen auf; das erste Profil, das die Eigenschaft verletzt, ist das kleinste Gegenbeispiel.
2. **Eigenschaften** werden an einem Profil (Condorcet, Pareto, Monotonie, Teilnahme, Ausscheiden eines Verlierers) oder an zwei Gruppen (Konsistenz) geprüft; jede Regel liefert dazu einen Sieger.
3. **Ohne Hilfe eines Gleichstands:** nur Gegenbeispiele, in denen weder in einem der beteiligten Läufe ein Gleichstand an der Spitze (bei der Sofortstichwahl: in irgendeiner Runde) vorkommt. Das Ergebnis hängt dann nicht am Los.
4. **Gleichstand:** A vor B vor C vor D, festgelegt, damit das Gegenbeispiel nicht vom Zufall abhängt. Bei vier Kandidaten (24 Rangfolgen) endet die Aufzählung bei 4 Wählern.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    axiom = st.selectbox("Eigenschaft", list(C.AXIOMS), format_func=C.AXIOMS.get, key="axiom_select", help="Welche Eigenschaft geprüft wird; ihre Bedeutung steht unter dem Ergebnis.")
    rule = st.selectbox("Regel", list(C.RULES), format_func=C.RULES.get, key="rule_select", help="Die Regel, die gezählt wird.")
    m = st.slider("Kandidaten", *bounds("m_slider"), key="m_slider", help="Bei zwei Kandidaten gelten alle Eigenschaften; vier Kandidaten haben 24 Rangfolgen, dann endet die Aufzählung bei 4 Wählern.")
    max_n = st.slider("Suche bis zu … Wählern", *bounds("maxn_slider"), key="maxn_slider", help="Die Aufzählung prüft alle Profile mit 1 bis zu dieser Zahl von Wählern (bei vier Kandidaten höchstens 4).")
    tie_free = st.checkbox("nur Gegenbeispiele ohne Hilfe eines Gleichstands", key="tiefree_check", help="Gegenbeispiele, in denen in keinem Lauf ein Gleichstand vorkommt: das Ergebnis hängt dann nicht am Los.")

sync_query_params({"axiom_select": axiom, "rule_select": rule, "m_slider": int(m), "maxn_slider": int(max_n), "tiefree_check": bool(tie_free)})

settings = Settings(axiom=axiom, rule=rule, m=int(m), max_n=int(max_n), tie_free=bool(tie_free))
with st.spinner("Zähle alle Profile auf …"):
    a = _analysis(settings)
v = a.violation

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
st.markdown(f"**{C.AXIOMS[settings.axiom]}:** {C.AXIOM_TEXT[settings.axiom]}")
m1, m2, m3 = st.columns(3)
m1.metric("Regel", short_rule(settings.rule), delta=f"{settings.m} Kandidaten", delta_color="off")
m2.metric("Kleinstes Gegenbeispiel", "keines" if v is None else f"{v.n} Wähler", delta=f"Suche bis {a.searched_to} Wähler" + (" ohne Gleichstand" if settings.tie_free else ""), delta_color="off")
m3.metric("Verletzt", "nein" if v is None else "ja", delta="im untersuchten Bereich" if v is None else C.AXIOMS[settings.axiom], delta_color="off")
if v is not None:
    for line in describe(v):
        st.markdown("- " + line)

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Hält die Regel, was man von ihr erwartet?")
kind, text = verdict_state(a)
getattr(st, kind)(text)

st.markdown("---")

# --- Tabelle und Messreihen ----------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Tabelle und Messreihen")
st.caption(f"Feste Programme, unabhängig von den Reglern. Jede Reihe rechnet auf Klick in einigen Sekunden; die Messreihen nutzen je Zelle {C.SERIES_RUNS} Profile mit den Zufalls-Seeds {C.SERIES_SEED} bis {C.SERIES_SEED + C.SERIES_RUNS - 1}.")
tab0, tab1, tab2 = st.tabs(["Alle Regeln, alle Eigenschaften", "Wie oft in Zufallsprofilen?", "Profilmodelle"])
with tab0:
    st.markdown(f"**Das kleinste Gegenbeispiel je Regel und Eigenschaft** ({C.TABLE_M} Kandidaten, Suche bis {C.TABLE_N} Wähler). „–“: bis dahin keines gefunden.")
    if st.button("Tabelle rechnen", key="table_button"):
        t0 = time.perf_counter()
        with st.spinner("Zähle alle Profile auf (einige Sekunden) …"):
            _table()
        st.session_state["table_done"] = time.perf_counter() - t0
    if "table_done" in st.session_state:
        cells = _table()
        c1, c2 = st.columns(2)
        c1.markdown("**mit dem Los**")
        c1.plotly_chart(build_table(cells, "with_tie"), width="stretch", key="table_with")
        c2.markdown("**ohne Hilfe eines Gleichstands**")
        c2.plotly_chart(build_table(cells, "tie_free"), width="stretch", key="table_free")
        st.table(table_rows(cells, "with_tie"))
        st.table(table_rows(cells, "tie_free"))
        kind, text = verdict_table(cells)
        getattr(st, kind)(text)
        st.caption(f"Rechenzeit dieser Sitzung: {num(st.session_state['table_done'], 1)} s (beim ersten Mal; danach liegt das Ergebnis im Zwischenspeicher).")
with tab1:
    st.markdown(f"**Wie oft ist eine Eigenschaft in Zufallsprofilen verletzt?** {C.SERIES_N} Wähler, Anteil der Profile; in Klammern der Anteil ohne Hilfe eines Gleichstands.")
    if st.button("Reihe rechnen", key="frequency_button"):
        t0 = time.perf_counter()
        with st.spinner("Rechne die Reihe (einige Sekunden) …"):
            _series_frequency()
        st.session_state["frequency_done"] = time.perf_counter() - t0
    if "frequency_done" in st.session_state:
        rows = _series_frequency()
        for mm in C.SERIES_MS:
            st.markdown(f"**{mm} Kandidaten**")
            st.plotly_chart(build_frequency(rows, mm), width="stretch", key=f"frequency_chart_{mm}")
            st.table(frequency_rows(rows, mm))
        kind, text = verdict_frequency(rows)
        getattr(st, kind)(text)
        st.caption(f"Rechenzeit dieser Sitzung: {num(st.session_state['frequency_done'], 1)} s (beim ersten Mal; danach liegt das Ergebnis im Zwischenspeicher).")
with tab2:
    st.markdown(f"**Wie hängt es vom Profilmodell ab?** {C.SERIES_MODEL_M} Kandidaten, {C.SERIES_N} Wähler; die zehn häufigsten Verletzungen.")
    if st.button("Reihe rechnen", key="models_button"):
        t0 = time.perf_counter()
        with st.spinner("Rechne die Reihe (einige Sekunden) …"):
            _series_models()
        st.session_state["models_done"] = time.perf_counter() - t0
    if "models_done" in st.session_state:
        rows = _series_models()
        st.plotly_chart(build_models(rows), width="stretch", key="models_chart")
        kind, text = verdict_models(rows)
        getattr(st, kind)(text)

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Die Aufzählung endet bei wenigen Wählern** | „Keines gefunden“ heißt nur: bis zu dieser Wählerzahl keines. Ein größeres Profil kann eines enthalten; gleichstandsfreie Lehrbuchbeispiele der Sofortstichwahl ändern mehrere Wähler zugleich und brauchen mehr Wähler, als hier durchsucht werden (das kleinste mit drei Kandidaten 17 nach einer unabhängigen Aufzählung); mit einem einzelnen Wähler gibt es ohne Gleichstand keines. | diese Demo (Grenze im Verdikt) |
| **Das Los entscheidet jeden Gleichstand gleich** | Viele Gegenbeispiele leben vom Gleichstand und verschwinden, wenn man nur gleichstandsfreie zulässt. „Ohne Gleichstand“ ist dabei streng: jeder Gleichstand zählt, auch ein folgenloser. | diese Demo (zweite Tabelle) |
| **Ein Verstoß ist ein Verstoß** | Wie schwer er wiegt, sagt die Zahl der Wähler nicht. Die Messreihen zeigen, wie oft er in Zufallsprofilen vorkommt. | diese Demo (Messreihen) |
| **Die Profile sind Modelle** | Die Anteile hängen vom Profilmodell ab (drei Modelle). Echte Präferenzen liegen dazwischen. | diese Demo |
| **Genau diese sechs Eigenschaften** | Andere Eigenschaften (Anonymität, Neutralität, Unabhängigkeit irrelevanter Alternativen im Sinne von Arrow, Klonunabhängigkeit) sind nicht geprüft. Nach Arrow ist keine Regel, die aus den Rangfolgen eine Gesamtrangfolge bildet und mindestens 3 Kandidaten zulässt, zugleich Pareto-effizient, unabhängig von irrelevanten Alternativen und nicht diktatorisch. | – |
| **Ehrliche Wähler** | Die Eigenschaften gelten für ehrlich abgegebene Rangfolgen; taktisches Wählen ist ein eigenes Thema. | `taktisch-waehlen-demo` |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Profil.** Ein Zählvektor $c \in \mathbb{N}^{m!}$ über die Rangfolgen; $f(c)$ ist der Sieger einer Regel $f$ (Gleichstand: feste Rangfolge der Kandidaten).

**Eigenschaften.** Condorcet-Konsistenz: Gibt es $a$ mit $W(a, b) > W(b, a)$ für alle $b \ne a$ ($W(a,b)$ = Zahl der Wähler, die $a$ vor $b$ reihen), gilt $f(c) = a$.
Pareto: reihen alle Wähler $a$ vor $b$, gilt $f(c) \ne b$. Monotonie: wird $c' = c - e_R + e_{R'}$ gebildet, wobei $R'$ aus $R$ entsteht, indem der Sieger $f(c)$ einen Platz nach oben rückt, gilt $f(c') = f(c)$.
Teilnahme: für jede Rangfolge $R$ ist $f(c + e_R)$ in $R$ nicht schlechter als $f(c)$. Konsistenz: aus $f(c_1) = f(c_2) = a$ folgt $f(c_1 + c_2) = a$. Ausscheiden eines Verlierers: für jedes $x \ne f(c)$ gilt $f(c \setminus x) = f(c)$.

**Suche.** Für $n = 1, 2, \dots$ werden alle Zerlegungen $c$ mit $\sum c = n$ aufgezählt (bei $m = 3$ sind das $\binom{n+5}{5}$ Profile) und der Reihe nach geprüft; das erste Profil mit einem Verstoß ist das kleinste Gegenbeispiel. Bei der Konsistenz werden alle Paare von Gruppen mit zusammen $n$ Wählern geprüft.

**Gleichstandsfrei.** Ein Gegenbeispiel zählt als gleichstandsfrei, wenn in keinem der beteiligten Läufe ein Gleichstand an der Spitze (Sofortstichwahl: in irgendeiner Runde) vorkommt.

**Literatur** (aus dem Gedächtnis, nicht im Original geprüft): Arrow (1951); Moulin (1988) zum No-Show-Paradox; Fishburn und Brams (1983) zu Nichtmonotonie und No-Show bei der Sofortstichwahl; Überblick: Brandt, Conitzer, Endriss, Lang, Procaccia (Hrsg.), *Handbook of Computational Social Choice*, Cambridge University Press 2016.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
