"""Einmalige Messung der README-Zahlen (nicht Teil der App): feste Pläne, Ausgabe auf stdout."""

import sys
import time

sys.path.insert(0, ".")
import wax_constants as C
import wax_evaluation as ev

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

t0 = time.time()
print("PRESETS")
for name, p in C.PRESETS.items():
    a = ev.analyse(ev.Settings(**p))
    print(name, "->", None if a.violation is None else (a.violation.n, ev.describe(a.violation)))

print("TABELLE (3 Kandidaten, bis 8 Wähler): kleinste Wählerzahl mit Los / ohne Gleichstand")
cells = ev.table_cells()
for key in ("with_tie", "tie_free"):
    for r in ev.table_rows(cells, key):
        print(key, r)
print(ev.verdict_table(cells)[1])

print("REIHE 1 (Zufallsprofile, 21 Wähler, je Zelle", C.SERIES_RUNS, "Profile): Anteil mit Los (ohne Gleichstand)")
rows = ev.series_frequency()
for m in C.SERIES_MS:
    for r in ev.frequency_rows(rows, m):
        print("m =", m, r)

print("REIHE 2 (4 Kandidaten, 21 Wähler): Anteil mit Los / ohne Gleichstand, nur Anteile über 0")
for r in ev.series_models():
    if r["share"] > 0:
        print(r["model"], r["axiom"], r["rule"], round(100 * r["share"], 1), round(100 * r["share_free"], 1))
print("sec", round(time.time() - t0, 1))
