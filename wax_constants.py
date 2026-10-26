"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

RULES = {
    "plurality": "Mehrheitswahl",
    "borda": "Borda-Zählung",
    "copeland": "Copeland (paarweise Siege)",
    "irv": "Sofortstichwahl (IRV)",
}
DEFAULT_RULE = "plurality"
AXIOMS = {
    "condorcet": "Condorcet-Konsistenz",
    "pareto": "Pareto-Effizienz",
    "monotonie": "Monotonie",
    "teilnahme": "Teilnahme",
    "konsistenz": "Konsistenz",
    "iia": "Unabhängigkeit vom Ausscheiden eines Verlierers",
}
DEFAULT_AXIOM = "condorcet"
AXIOM_TEXT = {
    "condorcet": "Gibt es einen Kandidaten, der jeden anderen Kandidaten im Paarvergleich mit Mehrheit schlägt (Condorcet-Sieger), wird er gewählt.",
    "pareto": "Reihen alle Wähler den Kandidaten a vor dem Kandidaten b, wird b nicht gewählt.",
    "monotonie": "Rückt ein Wähler den Sieger in seiner Rangfolge nach oben (alles andere bleibt), bleibt er Sieger.",
    "teilnahme": "Wer mitwählt, steht nicht schlechter da als jemand, der zu Hause bleibt: kommt ein Wähler dazu, gewinnt kein Kandidat, den er schlechter findet als den bisherigen Sieger.",
    "konsistenz": "Wählen zwei Wählergruppen je für sich denselben Sieger, wählt die Gesamtheit ihn auch.",
    "iia": "Scheidet ein Verlierer aus der Wahl aus (er wird aus allen Rangfolgen gestrichen), bleibt der Sieger derselbe.",
}

M_MIN, M_MAX, DEFAULT_M = 2, 4, 3             # bei zwei Kandidaten gelten alle Eigenschaften; drei und vier Kandidaten zeigen die Unterschiede
N_MIN, N_MAX, DEFAULT_N = 2, 9, 8             # größte Wählerzahl der Suche
N_LIMIT = {2: 9, 3: 9, 4: 4}                  # Bei vier Kandidaten gibt es 24 Rangfolgen: die Aufzählung aller Profile endet bei 4 Wählern

# Feste Messreihen (unabhängig von den Reglern): nie ein einzelner Seed als Befund
SERIES_SEED = 100000
SERIES_RUNS = 150
SERIES_MS = (3, 4)
SERIES_N = 21
TABLE_M, TABLE_N = 3, 8

MODELS = {
    "random": "Zufall (jeder Wähler ordnet beliebig)",
    "single": "einspitzig (Kandidaten auf einer Achse)",
    "camps": "zwei Lager (55 : 45, gegenläufig, mit Streuung)",
}
SERIES_MODEL_M = 4

COLOR_PLURALITY = "#4c78a8"
COLOR_BORDA = "#e8a838"
COLOR_COPELAND = "#2F6B65"
COLOR_IRV = "#b04a3a"
COLOR_ALERT = "#c0392b"
RULE_COLORS = {"plurality": COLOR_PLURALITY, "borda": COLOR_BORDA, "copeland": COLOR_COPELAND, "irv": COLOR_IRV}
CANDIDATE_LABELS = "ABCD"

PRESETS = {
    "Condorcet: wer scheitert?": {"axiom": "condorcet", "rule": "plurality", "m": 3, "max_n": 8, "tie_free": False},
    "Copeland: nie ein Verstoß": {"axiom": "condorcet", "rule": "copeland", "m": 3, "max_n": 6, "tie_free": False},
    "Sofortstichwahl: Monotonie": {"axiom": "monotonie", "rule": "irv", "m": 3, "max_n": 7, "tie_free": False},
    "Teilnahme: Copeland": {"axiom": "teilnahme", "rule": "copeland", "m": 3, "max_n": 6, "tie_free": False},
    "Ohne Gleichstand: Borda": {"axiom": "iia", "rule": "borda", "m": 3, "max_n": 6, "tie_free": True},
}
PRESET_HELP = {
    "Condorcet: wer scheitert?": "Voreinstellung: Mehrheitswahl und Condorcet-Konsistenz, drei Kandidaten, Suche bis 8 Wähler. Schon drei Wähler genügen: ein Kandidat gewinnt die Erststimmen, obwohl ein anderer jeden Paarvergleich gewinnt.",
    "Copeland: nie ein Verstoß": "Copeland wählt jeden vorhandenen Condorcet-Sieger (das ist seine Definition); bei drei Kandidaten und bis zu 6 Wählern findet die Aufzählung deshalb nichts.",
    "Sofortstichwahl: Monotonie": "Das Lehrbuchbeispiel der Sofortstichwahl: ein Wähler rückt den Sieger nach oben, und er verliert. Mit dem Los genügen 7 Wähler; ohne Hilfe eines Gleichstands fand die Aufzählung bis 15 Wähler keines.",
    "Teilnahme: Copeland": "Ein Wähler kommt dazu und der Sieger wird einer, den er schlechter findet (das „No-Show-Paradox“). Mit dem Los genügen bei Copeland 4 Wähler.",
    "Ohne Gleichstand: Borda": "Dieselbe Frage wie die Unabhängigkeit vom Ausscheiden eines Verlierers, aber nur Gegenbeispiele, die in keinem Lauf einen Gleichstand brauchen; bei Borda sind es 5 Wähler.",
}
