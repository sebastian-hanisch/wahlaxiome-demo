# Wahlregeln und ihre Axiome: welche Regel verletzt was? – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-wahlaxiome-demo.streamlit.app/)** -->

Stück der Linie **Abstimmen und Fair Teilen** (Konzepte-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“). Vorgänger: [wahlregeln-demo](https://github.com/sebastian-hanisch/wahlregeln-demo) (vier Regeln auf denselben Profilen) und [taktisch-waehlen-demo](https://github.com/sebastian-hanisch/taktisch-waehlen-demo) (Manipulation durch einen einzelnen Wähler).
Die Demo fragt: **Welche Eigenschaften, die man von einer fairen Wahlregel erwartet, erfüllen Mehrheitswahl, Borda, Copeland und Sofortstichwahl, und wie klein kann ein Gegenbeispiel sein?** Sechs Eigenschaften: Condorcet-Konsistenz, Pareto-Effizienz, Monotonie, Teilnahme (kein „No-Show-Paradox“), Konsistenz und Unabhängigkeit vom Ausscheiden eines Verlierers.
Für jede Regel und jede Eigenschaft sucht die Demo das **kleinste Gegenbeispiel durch Aufzählung aller Profile**, gibt es in Worten wieder und trennt dabei **Gegenbeispiele, die vom Gleichstand leben, von denen, die ohne ihn auskommen**.

Der Kern ist eigener Code (`numpy`): vier Regeln auf Zählvektoren, sechs Eigenschaftsprüfungen, die Suche. Ein unabhängiges naives Orakel in den Tests prüft jede Eigenschaft auf Listen von Wählern.

## Warum dieses Problem

Jede der sechs Eigenschaften klingt selbstverständlich. Die Demo zeigt, dass **keine der vier gängigen Regeln alle erfüllt**, und macht sichtbar, **wie früh** die Verletzung beginnt: bei zwei Wählern (Ausscheiden eines Verlierers), bei drei (Condorcet-Konsistenz, Teilnahme; gezählt ohne den hinzukommenden Wähler), bei sieben (Monotonie der Sofortstichwahl).
Dazu kommt ein Befund, der in der Lehrbuchdarstellung meist fehlt: **viele Gegenbeispiele hängen am Gleichstand**. Lässt man nur Gegenbeispiele zu, in denen kein Lauf einen Gleichstand braucht, bleiben von zwölf Gegenbeispielen in der Tabelle nur sechs.

## Modell

**Regeln.** Mehrheitswahl, Borda-Zählung, Copeland (je gewonnenem Paarvergleich 1 Punkt, je Gleichstand 0,5), Sofortstichwahl (der Kandidat mit den wenigsten Erststimmen scheidet aus, bis einer bleibt). **Gleichstand:** feste Rangfolge A vor B vor C vor D; bei der Sofortstichwahl scheidet unter mehreren Letzten der am wenigsten bevorzugte aus.
**Eigenschaften.** *Condorcet-Konsistenz:* gibt es einen Kandidaten, der jeden anderen mit Mehrheit schlägt, wird er gewählt. *Pareto:* reihen alle Wähler a vor b, wird b nicht gewählt. *Monotonie:* rückt ein Wähler den Sieger einen Platz nach oben, bleibt er Sieger. *Teilnahme:* kommt ein Wähler dazu, gewinnt kein Kandidat, den er schlechter findet als den bisherigen Sieger.
*Konsistenz:* wählen zwei Gruppen je denselben Sieger, wählt die Gesamtheit ihn auch. *Ausscheiden eines Verlierers:* wird ein Nicht-Sieger aus allen Rangfolgen gestrichen, bleibt der Sieger derselbe.
**Ohne Hilfe eines Gleichstands.** Ein Gegenbeispiel zählt so, wenn in **keinem** der beteiligten Läufe ein Gleichstand an der Spitze (bei der Sofortstichwahl: in irgendeiner Runde) vorkommt. Die Definition ist **streng**: sie zählt jeden Gleichstand, auch einen folgenlosen.
**Suche.** Profile sind Zählvektoren über alle m! Rangfolgen. Für n = 1, 2, … werden **alle** Zerlegungen aufgezählt (bei drei Kandidaten und 8 Wählern 1 287 + 792 + … Profile); das erste Profil mit einem Verstoß ist das kleinste Gegenbeispiel. Bei der Konsistenz werden alle Paare von Gruppen geprüft. Bei vier Kandidaten (24 Rangfolgen) endet die Aufzählung bei 4 Wählern.
Formeln und Lesehilfe stehen im 📐-Expander der App.

## Methodik

- **Kern** (`wax_algorithm.py`): Rangfolgen als Index, die vier Regeln samt Gleichstandsmarke, die sechs Prüfungen (`check_profile`, `check_consistency`), die Aufzählung (`smallest_violation`), Profilmodelle für die Stichproben.
- **Szenario und Auswertung** (`wax_scenario.py`, `wax_evaluation.py`): Suche je Einstellung, das Gegenbeispiel in Worten, die Tabelle aller 24 Zellen, zwei Messreihen mit festem Programm, alle Verdikte als reine Funktionen.
- **Oberfläche** (`app.py`): fünf Schnellstart-Szenarien, Regler für Eigenschaft, Regel, Kandidaten, Suchgrenze und „nur ohne Gleichstand“, das kleinste Gegenbeispiel in Worten, drei Reiter (Tabelle, Häufigkeit in Zufallsprofilen, Profilmodelle), Annahmen und Formeln.
- **Messreihen:** Reihe 1: Zufallsprofile, 21 Wähler, 3 und 4 Kandidaten; Reihe 2: alle drei Profilmodelle bei 4 Kandidaten und 21 Wählern; je Zelle 150 Profile mit den Zufalls-Seeds 100000 bis 100149.

## Befunde (gemessen, keine Behauptungen)

Die Tabelle der kleinsten Gegenbeispiele ist eine **Aufzählung** und deshalb exakt. Die Häufigkeiten sind Stichproben mit je 150 Profilen (die Standardabweichung eines Anteils liegt bei höchstens 4 Prozentpunkten). **Die Zufallszahlen eines `numpy`-Generators sind nicht über Versionen stabil**: die Tests prüfen für die Stichproben deshalb Bänder um diese Zahlen.

| Frage | Befund | Test |
|---|---|---|
| Stimmt der Kern? | Die vier Regeln samt Gleichstandsmarke gleich einer naiven Auswertung auf Listen von Wählern (320 Profile); jede der fünf Profileigenschaften gleich der naiven Prüfung (80 Profile je Eigenschaft und Regel, mit und ohne Gleichstand); die Konsistenz gleich der naiven Prüfung auf 300 Gruppenpaaren; das kleinste Gegenbeispiel gleich einer naiven Aufzählung aller Multimengen von Rangfolgen bis 5 Wähler; jedes gefundene Gegenbeispiel wird nachgespielt. | `tests/test_oracle_wahlaxiome.py` |
| Wie klein sind die Gegenbeispiele (3 Kandidaten, mit dem Los)? | **Ausscheiden eines Verlierers: 2 Wähler** bei allen vier Regeln. **Condorcet-Konsistenz: 3 Wähler** bei Mehrheitswahl, Borda und Sofortstichwahl, bei Copeland nie. **Teilnahme: 3 Wähler** bei der Sofortstichwahl, 4 bei Copeland (ohne den hinzukommenden Wähler gezählt). **Konsistenz: 5 Wähler** bei Copeland und Sofortstichwahl. **Monotonie: 7 Wähler** bei der Sofortstichwahl. **Pareto: nie** (bei keiner Regel). | `test_claims.py::test_the_table_of_smallest_counterexamples_with_the_tie_break` |
| Was bleibt ohne Hilfe eines Gleichstands? | Nur noch **Condorcet-Konsistenz** (Mehrheitswahl 7 Wähler, Borda 5, Sofortstichwahl 5) und **Ausscheiden eines Verlierers** (7, 5, –, 5): **6 von 24 Zellen** statt 12. Monotonie, Teilnahme und Konsistenz haben bis 8 Wähler kein gleichstandsfreies Gegenbeispiel; bei der Sofortstichwahl auch bis **15 Wähler** keines für Monotonie und Teilnahme. Das ist kein Zufall der Suchgrenze: bei einem einzelnen Wähler hängt jede solche Verletzung an einem Gleichstand (ein Wähler ändert nur die Erststimmenzahlen zweier Kandidaten um 1; die Ausscheidereihenfolge kann sich erst ändern, wenn eine Zahl die kleinste einholt; Beweisskizze der Prüfung, hier nicht getestet). | `test_claims.py::test_the_table_without_the_help_of_a_tie`, `::test_without_a_tie_irv_monotonicity_and_participation_have_no_counterexample_up_to_fifteen_voters` |
| Was ändert sich bei vier Kandidaten (bis 4 Wähler)? | Copeland bleibt Condorcet-konsistent (kein Gegenbeispiel). Teilnahme: schon **3 Wähler** bei Copeland und Sofortstichwahl. **Ohne Gleichstand** gibt es jetzt bei **Borda und Copeland** ein Gegenbeispiel zum Ausscheiden eines Verlierers (je 4 Wähler), bei der Sofortstichwahl keines. | `test_claims.py::test_with_four_candidates_up_to_four_voters` |
| Wie oft kommt es in Zufallsprofilen vor (21 Wähler, 4 Kandidaten)? | **Ausscheiden eines Verlierers: 29 %** (Mehrheitswahl), 25 % (Borda), 16 % (Copeland), 21 % (Sofortstichwahl), ohne Gleichstand 8 / 11 / **0** / 8 %. **Condorcet-Konsistenz:** 23 % (Mehrheitswahl), 11 % (Borda), 5 % (Sofortstichwahl), Copeland 0 %. **Monotonie:** 8 % (Sofortstichwahl, sonst 0 %). **Teilnahme:** 9 % (Sofortstichwahl), 7 % (Copeland). **Konsistenz:** rund 1 % oder weniger (Sofortstichwahl 1,3 %). Pareto nie. | `test_claims.py::test_frequency_in_random_profiles_with_four_candidates`, `::test_properties_that_are_never_violated_in_the_samples` |
| Lebt das vom Gleichstand? | In den Zufallsprofilen kommen **Monotonie, Teilnahme und Konsistenz ohne Hilfe eines Gleichstands in keinem einzigen Profil** vor (0 von 150 Profilen je Zelle, das heißt: höchstens etwa 2 %); bei Monotonie und Teilnahme der Sofortstichwahl ist es bei einem einzelnen Wähler grundsätzlich unmöglich. Copeland verletzt Condorcet und das Ausscheiden eines Verlierers ohne Gleichstand in diesen Profilen nie; die verbleibenden Verletzungen sind Condorcet und das Ausscheiden bei Mehrheitswahl, Borda und Sofortstichwahl. | `test_claims.py::test_without_a_tie_only_condorcet_and_iia_remain_in_random_profiles` |
| Hängt es vom Profilmodell ab? | Bei **einspitzigen** Profilen ist das Ausscheiden eines Verlierers bei der Mehrheitswahl in **81 %** der Profile verletzt (Zufall: 29 %), die Condorcet-Konsistenz in 57 % (Zufall: 23 %) und bei der Sofortstichwahl in 42 % (Zufall: 5 %); Monotonie der Sofortstichwahl dagegen nur 1 % (Zufall: 8 %). Copeland verletzt Condorcet in keinem Modell. | `test_claims.py::test_profile_models_with_four_candidates` |
| Schnellstart-Szenarien | Condorcet: Mehrheitswahl, 3 Wähler (1 × A > B > C, 1 × B > A > C, 1 × C > B > A: bei Gleichstand der Erststimmen entscheidet das Los für A, obwohl B jeden Paarvergleich gewinnt). Copeland: bis 6 Wähler keines. Monotonie: Sofortstichwahl, 7 Wähler. Teilnahme: Copeland, 4 Wähler (ohne den hinzukommenden). Ohne Gleichstand: Borda, Ausscheiden eines Verlierers, 5 Wähler (3 × A > B > C, 2 × B > C > A). | `test_claims.py::test_the_presets_tell_the_stories_in_their_help_texts`, `tests/test_algorithm.py` |

## Ehrliche Grenzen

- **„Keines gefunden“ ist kein Beweis.** Die Aufzählung endet bei 8 oder 9 Wählern (drei Kandidaten) beziehungsweise 4 (vier Kandidaten). Dass Mehrheitswahl und Borda monoton, teilnahmefreundlich und konsistent sind und dass Pareto nie verletzt wird, sind bekannte Eigenschaften (aus dem Gedächtnis); hier sind sie **in diesem Bereich bestätigt**, nicht bewiesen.
- **Ohne Gleichstand ist streng.** Jeder Gleichstand an der Spitze, in irgendeiner Runde der Sofortstichwahl, in einem beteiligten Lauf, macht ein Gegenbeispiel zu einem „mit Los“. Ein Gegenbeispiel, das einen folgenlosen Gleichstand enthält, wird so dem Los zugeschlagen: Anzahl und Anteile gleichstandsfreier Gegenbeispiele sind eher zu klein, die kleinsten Wählerzahlen eher zu groß. Dass bei der Sofortstichwahl Monotonie und Teilnahme ohne Gleichstand bis 15 Wähler **kein** Gegenbeispiel haben, gilt für die Definition dieser Demo (ein einzelner Wähler rückt den Sieger hoch oder kommt dazu); gleichstandsfreie Beispiele der Lehrbücher ändern mehrere Wähler zugleich, und das kleinste mit drei Kandidaten braucht nach unabhängiger Aufzählung der Prüfung 17 Wähler.
- **Die Eigenschaft „Ausscheiden eines Verlierers“ ist nicht Arrows Unabhängigkeit irrelevanter Alternativen.** Sie fragt, ob der Sieger bleibt, wenn ein Nicht-Sieger gestrichen wird (eine schwache Form); Arrows Fassung betrifft die Rangfolge zweier Kandidaten und ist hier nicht geprüft.
- **Zufallsprofile sind eine Annahme.** Die Anteile hängen stark vom Profilmodell ab (siehe oben); echte Präferenzen liegen dazwischen. Die Zahlen sind kein Maß dafür, wie oft ein Paradox in einer echten Wahl vorkommt.
- **Ein Verstoß ist ein Verstoß, wie schwer er wiegt, sagt die Zahl nicht.** Ein Gegenbeispiel mit 7 Wählern ist ein Beleg, dass die Eigenschaft nicht gilt; in einer großen Wahl kann es sehr selten sein.
- **Die Preset-Beispiele sind Aufzählungsergebnisse, keine Stichproben** (das kleinste Gegenbeispiel einer festen Reihenfolge der Profile): sie sind eindeutig, aber nicht „typisch“.
- **Literatur** (Arrow 1951; Moulin 1988 zum No-Show-Paradox; Fishburn und Brams 1983; *Handbook of Computational Social Choice*, 2016) aus dem Gedächtnis, nicht im Original geprüft.

## Befunde und Korrekturen gegenüber dem Plan

- **Port:** 9191 (9170 bis 9190 sind vergeben).
- **Sechs Eigenschaften statt fünf:** der Plan nannte Condorcet-Konsistenz, Monotonie, Pareto, Unabhängigkeit irrelevanter Alternativen und Teilnahme; die App prüft zusätzlich die **Konsistenz** (Verstärkung) und ersetzt Arrows Unabhängigkeit irrelevanter Alternativen durch die schwächere Form „Ausscheiden eines Verlierers“ (siehe Grenzen).
- **Suchgrenzen:** der Plan sprach von „m = 3 bis 4, n bis 7“; die Aufzählung läuft bei 3 Kandidaten bis 8 oder 9 Wähler und bei 4 Kandidaten bis 4 (bei 24 Rangfolgen wächst die Zahl der Profile zu schnell).
- **Folge aus Stück 3 umgesetzt:** das Los bestimmt, was bei der Manipulation gelingt, und deshalb zeigt jede Tabelle und jedes Beispiel hier **mit und ohne Hilfe eines Gleichstands**; der Plan verlangte das als Lehre aus `taktisch-waehlen-demo`.
- **Hypothese des Plans** („Gegenbeispiele existieren für jede Regel und jede Eigenschaftenkombination“): **teilweise bestätigt**: jede Regel hat mindestens ein Gegenbeispiel (jede der vier verletzt „Ausscheiden eines Verlierers“ schon mit 2 Wählern), aber nicht jede Eigenschaft hat für jede Regel eines (Pareto bei keiner, Monotonie nur bei der Sofortstichwahl).
- **Reglerspanne:** Kandidaten 2 bis 4, Suchgrenze 2 bis 9 Wähler; bei vier Kandidaten gilt höchstens 4.

## Verifikation

- **Kern:** jede Einheit an Mini-Profilen von Hand (die vier Regeln mit Zyklus und Gleichstand, jedes Gegenbeispiel mit Rechnung im Kommentar: Mehrheitswahl und Borda bei Condorcet, Monotonie der Sofortstichwahl mit 7 Wählern, No-Show bei Copeland mit 4, Konsistenz der Sofortstichwahl mit 5, Ausscheiden bei Mehrheitswahl), Randfälle (zwei Kandidaten, kleinste und größte Reglerwerte für jede Eigenschaft und Regel, ungültige Eingaben, Suchgrenze unter dem kleinsten Beispiel).
- **Orakel:** naive Auswertung der Regeln samt Gleichstandsmarke, naive Prüfung jeder Eigenschaft (mit und ohne Gleichstand) auf zufälligen Profilen, naive Konsistenzprüfung, naive Aufzählung des kleinsten Gegenbeispiels, Nachspielen jedes gefundenen Gegenbeispiels, Copeland nie gegen Condorcet.
- **Verdikte:** reine Funktionen, jeder Zweig (Gegenbeispiel mit und ohne Gleichstand, keines, Grenze bei vier Kandidaten, zwei Kandidaten, Tabelle, Häufigkeit, Profilmodelle) und jede Zahl im Text an handgesetzten Werten (`tests/test_verdicts.py`).
- **Presets, Layout, Oberfläche:** wie in allen Demos (Presets vollständig und im Regelbereich, keines auf einem Reglerrand, kein Preset entsteht durch Änderung eines einzigen Reglers, Schnellstart oben, aktives Preset hervorgehoben, AppTest jeder Button und jeder Regler an den Rändern, Wahrheitswert in der Adresszeile).
- **Mutationsprüfung** (`tools/mutate_demo.py`): 138 Stellen im Kern `wax_algorithm.py`, **128 gefangen** (46 davon über wortgleiche Zeilen in Nachbar-Demos), **10 als äquivalent festgehalten**, keine Zeitüberschreitung. Der erste Lauf ließ 17 überleben; sieben davon waren **echte Lücken** und haben Tests bekommen: die Pareto-Prüfung selbst (keine der vier Regeln verletzt Pareto, deshalb setzt `test_pareto_check_detects_a_rule_that_chooses_a_dominated_candidate` eine Regel ein, die den Borda-Letzten wählt) und die Obergrenze der Konsistenz-Suche (`test_the_consistency_search_respects_its_bounds`: kleinstes Gegenbeispiel bei genau 5 Wählern, mit Grenze 4 keines). Die zehn Äquivalenten: Borda- und Copeland-Punkte werden nur um eine Konstante verschoben (`- -> +`, `1 -> 0/2` in `outcome`, Rangfolge und Gleichstände bleiben), `<` statt `<=` in `drop_candidate` trifft nur den gestrichenen Kandidaten selbst, `m < 3` statt `m < 2` bei der Streichprobe ändert nichts (mit zwei Kandidaten zeigt `test_iia_needs_at_least_three_candidates` trotzdem das richtige Ergebnis), und zwei `or -> and` in der Vorfilterung der Konsistenz-Suche, die nur weniger Paare überspringen, die `check_consistency` danach selbst verwirft.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `wax_algorithm.py` | Kern: Regeln, Eigenschaften, Aufzählung |
| `wax_constants.py` | Regler-Grenzen, feste Pläne, Farben, Presets |
| `wax_evaluation.py` | Suche, Gegenbeispiel in Worten, Tabelle, Messreihen, Verdikte |
| `wax_layout.py` | Fester Kopf (Stylesheet) |
| `wax_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben) |
| `wax_scenario.py` | Profil und Gleichstandslos für die Stichproben |
| `wax_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `messen.py` | Einmalige Messung der Zahlen in dieser README (nicht Teil der App) |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Mini-Profile, Kern, Orakel, Verdikte, Randfälle, Presets, Abbildungen, Layout, AppTest, Footer, Laufzeit-Importe, Claims |

## Bewusst nicht umgesetzt

- **Arrows Unabhängigkeit irrelevanter Alternativen und der Satz von Arrow:** die Aufzählung zeigt Einzelfälle; ein SAT-Beweis der Unmöglichkeit ist ein eigenes, größeres Vorhaben.
- **Weitere Eigenschaften** (Anonymität, Neutralität, Klonunabhängigkeit, Schwach- und Starkform von Pareto, Ordnungsfolgerichtigkeit): nicht geprüft.
- **Andere Gleichstandsregeln** (neuer Zufall je Lauf, Vorsitzender): die feste Rangfolge ist die einfachste Wahl; „ohne Gleichstand“ umgeht sie.
- **Mehr als vier Kandidaten und größere Suchgrenzen:** die Zahl der Profile wächst zu schnell für eine Aufzählung im Browser.
- **Echte Wahldaten:** nur synthetische Profile (Datenschutz, Positionierung).

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und NumPy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
