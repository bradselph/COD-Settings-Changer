"""Unit tests for setting_row.py -- the reusable settings-row template.

Run with `pytest` (only pytest needed; a headless QApplication is created in conftest),
or directly with `python tests/test_setting_row.py` for a quick standalone check.
"""
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PyQt5.QtWidgets import QApplication  # noqa: E402
_app = QApplication.instance() or QApplication([])

import setting_row as sr  # noqa: E402


def _spec(**kw):
    d = dict(name="X", value="0", comment="", editable=True, file_type="GameSpecific", help_text="")
    d.update(kw)
    return sr.SettingSpec(**d)


# ---- pure parsers ----
def test_parse_numeric_range_float():
    assert sr.parse_numeric_range("0.500000 to 1.000000") == (0.5, 1.0, False)


def test_parse_numeric_range_int():
    assert sr.parse_numeric_range("-1 to 16") == (-1.0, 16.0, True)


def test_parse_numeric_range_none():
    assert sr.parse_numeric_range("no range here") is None
    assert sr.parse_numeric_range("") is None


def test_parse_numeric_range_scientific_overflow():
    rng = sr.parse_numeric_range("-3.4028e38 to 3.4028e38")
    assert rng is not None and abs(rng[1] - rng[0]) > 1e9   # caller rejects as a slider


def test_parse_enum_bracket_and_bare():
    assert sr.parse_enum_options("one of [SMAA, XeSS, FSR AA]") == ["SMAA", "XeSS", "FSR AA"]
    assert sr.parse_enum_options("one of unknown, hdd, ssdorbetter, count") == \
        ["unknown", "hdd", "ssdorbetter", "count"]
    assert sr.parse_enum_options("plain text") is None


def test_special_combo_refreshrate_not_forced():
    # RefreshRate / Resolution must NOT be forced into a fixed combo (would clobber values)
    assert sr.special_combo_options("RefreshRate", "60 to 300") is None
    assert sr.special_combo_options("Resolution", "") is None
    assert sr.special_combo_options("TargetRefreshRate", "") == ["60 Hz", "120 Hz"]


# ---- SettingRow behavior ----
def test_bool_value_and_signal_semantics():
    r = sr.SettingRow(_spec(name="DepthOfField", value="true"))
    assert r.value() == "true" and r._kind == "bool" and not r.is_changed()
    seen = []
    r.valueChanged.connect(lambda n, v: seen.append((n, v)))
    r.set_value("false")                 # programmatic set must NOT emit
    assert r.value() == "false" and r.is_changed() and seen == []
    r._on_committed()                    # a real user commit emits exactly once
    assert seen == [("DepthOfField", "false")]


def test_revert_restores_baseline():
    r = sr.SettingRow(_spec(name="DepthOfField", value="true"))
    r.set_value("false")
    assert r.is_changed()
    r.revert()
    assert r.value() == "true" and not r.is_changed()


def test_slider_float_tolerance_no_false_dirty():
    r = sr.SettingRow(_spec(name="Fov", value="0.600000", comment="0.500000 to 1.000000"))
    assert r._kind == "slider"
    r.set_value("0.60")                  # numerically equal to 0.600000
    assert not r.is_changed()
    r.set_value("0.800000")
    assert r.is_changed()


def test_enum_inserts_current_value():
    r = sr.SettingRow(_spec(name="AATechniquePreferred", value="ZZZ",
                            comment="one of [SMAA, XeSS, FSR AA]"))
    assert r._kind == "enum" and r.value() == "ZZZ"   # unknown current value still selectable


def test_readonly_excluded_from_dirty():
    r = sr.SettingRow(_spec(name="GPUName", value="TEST GPU", comment="DO NOT MODIFY"),
                      non_editable_fields=["GPUName"])
    assert r._readonly
    r.set_value("HACKED")
    assert not r.is_changed()


def test_matches_name_help_value():
    r = sr.SettingRow(_spec(name="BulletImpacts", value="Off",
                            comment="", help_text="Toggles bullet impact effects"))
    assert r.matches("bullet")           # name
    assert r.matches("impact effects")   # help text
    assert r.matches("off")              # current value
    assert not r.matches("nonexistent")
    assert r.matches("")                 # empty query matches everything


def test_unusable_range_falls_back_to_text():
    r = sr.SettingRow(_spec(name="Weird", value="0", comment="-3.4028e38 to 3.4028e38"))
    assert r._kind == "text"             # overflow range -> plain field, not a broken slider


if __name__ == "__main__":
    import types
    mod = sys.modules[__name__]
    passed = failed = 0
    for name in sorted(vars(mod)):
        fn = getattr(mod, name)
        if name.startswith("test_") and isinstance(fn, types.FunctionType):
            try:
                fn()
                passed += 1
                print(f"PASS {name}")
            except Exception as e:
                failed += 1
                print(f"FAIL {name}: {type(e).__name__}: {e}")
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
