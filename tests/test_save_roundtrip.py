"""Save round-trip through the SettingRow-based editor on the handoff's fixture:
edit a value -> save -> the line is rewritten with key decoration + quotes + comment
preserved -> reload -> dirty count is 0. Read-only rows stay out of the dirty set.

Run with `pytest`, or `python tests/test_save_roundtrip.py`.
"""
import os
import sys
import tempfile

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PyQt5.QtWidgets import QApplication, QMessageBox  # noqa: E402
_app = QApplication.instance() or QApplication([])
QMessageBox.information = QMessageBox.warning = QMessageBox.critical = QMessageBox.question = \
    staticmethod(lambda *a, **k: 0)

import main  # noqa: E402
import setting_row  # noqa: E402

FIXTURE_GS = (
    "0\n"
    "//\n// Graphics\n//\n"
    'Fov:1.0 = "80" // 60 to 120\n'
    'DepthOfField:1.0 = "true"\n'
    'AATechniquePreferred:1.0 = "SMAA" // one of [SMAA, XeSS, FSR AA]\n'
    'GPUName:1.0 = "TEST GPU" // DO NOT MODIFY\n'
)
FIXTURE_GA = "0\nMicrophoneVolume:0.0 = \"4\"\n"


def _load_editor(tmp):
    gs = os.path.join(tmp, "options.4.cod23.cst")
    ga = os.path.join(tmp, "gamerprofile.0.BASE.cst")
    open(gs, "w").write(FIXTURE_GS)
    open(ga, "w").write(FIXTURE_GA)
    ed = main.OptionsEditor()
    ed.game = "MW3 2023"          # .cst, is_txt_game() == False
    ed.file_path = gs
    ed.game_agnostic_file_path = ga
    ed.options = {}
    ed.parse_options_file()
    ed.display_options()
    return ed, gs


def _row(ed, name):
    for r in ed.widgets.values():
        if r.spec.name == name:
            return r
    return None


def test_edit_preserves_key_decoration_and_resets_dirty():
    with tempfile.TemporaryDirectory() as tmp:
        ed, gs = _load_editor(tmp)

        # GPUName is DO NOT MODIFY -> read-only, excluded from dirty
        assert _row(ed, "GPUName")._readonly

        # edit Fov 80 -> 100 through the row, then save
        fov = _row(ed, "Fov")
        assert fov._kind == "slider"
        fov.set_value("100")
        assert fov.is_changed()
        ed.save_file(gs, "GameSpecific")

        saved = open(gs).read()
        assert 'Fov:1.0 = "100" // 60 to 120' in saved, saved   # decoration + quotes + comment kept
        assert 'DepthOfField:1.0 = "true"' in saved             # untouched line intact
        assert 'GPUName:1.0 = "TEST GPU" // DO NOT MODIFY' in saved

        # reload -> baselines reset -> nothing dirty
        ed.options = {}
        ed.parse_options_file()
        ed.display_options()
        assert sum(r.is_changed() for r in ed.widgets.values()) == 0
        assert _row(ed, "Fov").value() == "100"


def test_enum_edit_roundtrips():
    with tempfile.TemporaryDirectory() as tmp:
        ed, gs = _load_editor(tmp)
        aa = _row(ed, "AATechniquePreferred")
        assert aa._kind == "enum"
        aa.set_value("XeSS")
        ed.save_file(gs, "GameSpecific")
        assert 'AATechniquePreferred:1.0 = "XeSS" // one of [SMAA, XeSS, FSR AA]' in open(gs).read()


if __name__ == "__main__":
    import types
    passed = failed = 0
    for name in sorted(vars(sys.modules[__name__])):
        fn = getattr(sys.modules[__name__], name)
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
