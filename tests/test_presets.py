"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, keiner auf einem Reglerrand und keiner, der durch eine einzelne Regleränderung vom Standard entsteht."""

import wax_constants as C
import wax_evaluation as ev
import wax_presets as P

FIRST = "Condorcet: wer scheitert?"


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_regler_bounds():
    for name, p in C.PRESETS.items():
        assert p["axiom"] in C.AXIOMS and p["rule"] in C.RULES and C.M_MIN <= p["m"] <= C.M_MAX and C.N_MIN <= p["max_n"] <= C.N_MAX and isinstance(p["tie_free"], bool), name


def test_default_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS[FIRST]) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_no_preset_sits_on_a_slider_bound():
    bounds = {"m": (C.M_MIN, C.M_MAX), "max_n": (C.N_MIN, C.N_MAX)}
    for name, preset in C.PRESETS.items():
        for key, (lo, hi) in bounds.items():
            assert preset[key] not in (lo, hi), (name, key)


def test_no_single_change_of_the_default_produces_another_preset():
    default = C.PRESETS[FIRST]
    for name, p in C.PRESETS.items():
        if name != FIRST:
            assert sum(1 for k in p if p[k] != default[k]) >= 2, name


def test_presets_are_pairwise_different_and_cover_the_rules_and_axioms():
    values = [tuple(sorted(p.items())) for p in C.PRESETS.values()]
    assert len(set(values)) == len(values)
    assert {p["rule"] for p in C.PRESETS.values()} == {"plurality", "copeland", "irv", "borda"} and {p["tie_free"] for p in C.PRESETS.values()} == {False, True}


def test_the_bool_parser_for_the_address_line():
    assert P._bool("True") is True and P._bool("1") is True and P._bool("False") is False and P._bool("0") is False
    for bad in ("", "ja", "2"):
        try:
            P._bool(bad)
            assert False, bad
        except ValueError:
            pass
