"""Reusable settings-row template for the COD Options Editor ("Refined Classic" GUI).

One control language for every value editor (toggle / dropdown / slider+number / read-only),
per-row "changed since load" state (amber dot + amber-tinted control + revert), all derived
from the active qt-material theme accent so every theme keeps working.

Import direction is one-way: main.py -> setting_row.py (never the reverse), so there is no
import cycle. This module owns no file I/O; it only renders/edits a value and reports changes.
"""
import math
import os
import re

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QComboBox, QSlider, QCheckBox,
                             QHBoxLayout, QToolButton, QSizePolicy)

# The one theme-independent constant: the "changed since load" accent.
CHANGED_COLOR = "#f2a93b"


def theme_colors():
    """Colors for the current qt-material theme, read from the env vars it exports, with
    dark-theme fallbacks so the very first paint (before apply_stylesheet) still works."""
    def env(key, default):
        v = os.environ.get(key, "").strip()
        return v if v else default
    return {
        "accent":         env("QTMATERIAL_PRIMARYCOLOR", "#2f6fed"),
        "bg":             env("QTMATERIAL_SECONDARYDARKCOLOR", "#1b212c"),
        "surface":        env("QTMATERIAL_SECONDARYCOLOR", "#1f2531"),
        "surface_light":  env("QTMATERIAL_SECONDARYLIGHTCOLOR", "#303848"),
        "text":           env("QTMATERIAL_PRIMARYTEXTCOLOR", "#e8ecf4"),
        "text_secondary": env("QTMATERIAL_SECONDARYTEXTCOLOR", "#8a93a6"),
        "changed":        CHANGED_COLOR,
    }


# ---------------------------------------------------------------------------
# Pure comment parsers (extracted verbatim from the old create_slider_widget /
# create_widget regexes; unit-testable, no Qt).
# ---------------------------------------------------------------------------
def parse_numeric_range(comment):
    """(min, max, is_int) for a `... N to M ...` range comment, else None.
    Scientific-notation bounds (e.g. -3.4028e38) are parsed so the caller can reject
    unusable ranges instead of silently mis-reading them as small integers."""
    if not comment or "to" not in comment:
        return None
    nums = re.findall(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", comment)
    if len(nums) < 2:
        return None
    try:
        mn, mx = float(nums[0]), float(nums[1])
    except ValueError:
        return None
    if not (math.isfinite(mn) and math.isfinite(mx)):
        return None
    is_int = bool(re.fullmatch(r"-?\d+", nums[0])) and bool(re.fullmatch(r"-?\d+", nums[1]))
    return mn, mx, is_int


def parse_enum_options(comment):
    """List of options for a `... one of a, b, c` (or `one of [a, b, c]`) comment, else None."""
    if not comment or "one of" not in comment:
        return None
    m = re.findall(r"\[(.*?)\]", comment)
    if m:
        opts = [o.strip() for o in m[0].split(",") if o.strip()]
    else:
        opts = [o.strip() for o in comment.split("one of", 1)[1].split(",") if o.strip()]
    return opts or None


def special_combo_options(name, comment):
    """Forced dropdown options for the two settings that need them regardless of comment.
    (RefreshRate / Resolution deliberately NOT forced -- they store raw values a fixed list
    would clobber; they fall through to numeric/text. This matches the audited save path.)"""
    if name == "VoiceChatEffect" and "one of" in (comment or ""):
        return parse_enum_options(comment)
    if name == "TargetRefreshRate":
        return ["60 Hz", "120 Hz"]
    return None


def values_equal(a, b):
    """Numeric-tolerant equality so '0.60' vs '0.600000' is not a false 'changed'."""
    a, b = str(a).strip(), str(b).strip()
    try:
        return abs(float(a) - float(b)) < 1e-9
    except ValueError:
        return a.lower() == b.lower()


# ---------------------------------------------------------------------------
# Widgets moved here unchanged from main.py.
# ---------------------------------------------------------------------------
class NoScrollSlider(QSlider):
    def wheelEvent(self, event):
        event.ignore()


class NoScrollComboBox(QComboBox):
    def wheelEvent(self, event):
        event.ignore()


class ToggleSwitch(QCheckBox):
    """On/Off pill toggle, theme-accent when on (amber when changed). Keeps the old
    stateChanged->text swap so value semantics stay identical to the plain checkbox."""
    def __init__(self, checked=False, parent=None):
        super().__init__("On" if checked else "Off", parent)
        self.setChecked(checked)
        self.setCursor(Qt.PointingHandCursor)
        self.stateChanged.connect(lambda st: self.setText("On" if st else "Off"))
        self._changed = False
        self.refresh_theme()

    def set_changed(self, changed):
        if changed != self._changed:
            self._changed = changed
            self.refresh_theme()

    def refresh_theme(self):
        c = theme_colors()
        on = c["changed"] if self._changed else c["accent"]
        off_border = c["changed"] if self._changed else c["surface_light"]
        track = c["surface_light"]
        self.setStyleSheet(
            "QCheckBox { spacing: 8px; }"
            "QCheckBox::indicator { width: 40px; height: 20px; }"
            "QCheckBox::indicator:unchecked {"
            f"  image: none; border: 1px solid {off_border}; border-radius: 10px;"
            f"  background: qlineargradient(x1:0, y1:0, x2:1, y2:0,"
            f"    stop:0 #f5f5f5, stop:0.5 #f5f5f5, stop:0.5 {track}, stop:1 {track}); }}"
            "QCheckBox::indicator:checked {"
            f"  image: none; border: 1px solid {on}; border-radius: 10px;"
            f"  background: qlineargradient(x1:0, y1:0, x2:1, y2:0,"
            f"    stop:0 {on}, stop:0.55 {on}, stop:0.55 #ffffff, stop:1 #ffffff); }}"
        )


class SettingSpec:
    """Everything a row needs to render/edit one setting. `value` is the on-disk baseline."""
    __slots__ = ("name", "value", "comment", "editable", "file_type", "help_text", "wkey")

    def __init__(self, name, value, comment="", editable=True, file_type="",
                 help_text="", wkey=""):
        self.name = name
        self.value = value
        self.comment = comment
        self.editable = editable
        self.file_type = file_type
        self.help_text = help_text
        self.wkey = wkey


class SettingRow(QWidget):
    """One unified row: [dot] [name] [control] [revert] [range]. The control is a toggle,
    dropdown, slider+number, or read-only field chosen by the same rules as the old
    create_widget(). Reports edits via valueChanged(name, new_value)."""

    valueChanged = pyqtSignal(str, str)   # (setting name, new value)
    SLIDER_SCALE = 1000                   # float sliders are integer-scaled by this

    def __init__(self, spec, non_editable_fields=None, parent=None):
        super().__init__(parent)
        self.spec = spec
        self.baseline = "" if spec.value is None else str(spec.value)
        self._non_editable = set(non_editable_fields or [])
        self._kind = "text"               # bool | enum | slider | text
        self._is_int = True
        self._slider = None
        self._numbox = None
        self._control = None
        self._highlight = False
        self._readonly = self._compute_readonly()
        self._build()
        self._sync_changed()

    # -- read-only decision (matches display_options / update_widget_states) --
    def _compute_readonly(self):
        s = self.spec
        if not s.editable:
            return True
        if s.name.startswith("// DO NOT MODIFY"):
            return True
        if s.name in self._non_editable_fields():
            return True
        return False

    def _non_editable_fields(self):
        return self._non_editable

    # ---- layout / control factory ----
    def _build(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 3, 10, 3)
        lay.setSpacing(8)
        self.setMinimumHeight(40)

        self.dot = QLabel()
        self.dot.setFixedSize(8, 8)
        lay.addWidget(self.dot)

        self.name_label = QLabel(self.spec.name)
        self.name_label.setMinimumWidth(190)
        self.name_label.setMaximumWidth(190)
        tip = self.spec.help_text or "No help text available for this setting."
        if self.spec.comment:
            tip += "\n\nValid range: " + self.spec.comment
        self.name_label.setToolTip(tip)
        lay.addWidget(self.name_label)

        holder = QWidget()
        holder.setFixedWidth(220)
        hlay = QHBoxLayout(holder)
        hlay.setContentsMargins(0, 0, 0, 0)
        hlay.setSpacing(6)
        self._control_holder = hlay
        self._build_control(hlay)
        lay.addWidget(holder)

        self.revert_btn = QToolButton()
        self.revert_btn.setText("↺")   # loop reload glyph
        self.revert_btn.setCursor(Qt.PointingHandCursor)
        self.revert_btn.setToolTip("Revert to loaded value")
        self.revert_btn.setAutoRaise(True)
        self.revert_btn.setFixedWidth(20)
        self.revert_btn.clicked.connect(self.revert)
        lay.addWidget(self.revert_btn)

        self.range_label = QLabel(self.spec.comment or "")
        self.range_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.range_label.setToolTip(self.spec.comment or "")
        lay.addWidget(self.range_label, 1)

        for w in (self.name_label, self.range_label):
            w.setTextInteractionFlags(Qt.NoTextInteraction)
        self.refresh_theme()

    def _build_control(self, hlay):
        s = self.spec
        value = self.baseline.strip('"')

        if self._readonly:
            self._kind = "text"
            le = QLineEdit(value)
            le.setReadOnly(True)
            self._control = le
            le.setToolTip(self.name_label.toolTip())
            hlay.addWidget(le)
            return

        forced = special_combo_options(s.name, s.comment)
        if forced is not None:
            self._make_combo(hlay, forced, value)
            return
        if value.lower() in ("true", "false"):
            self._kind = "bool"
            self._control = ToggleSwitch(value.lower() == "true")
            self._control.stateChanged.connect(self._on_committed)
            hlay.addWidget(self._control)
            return
        if re.match(r"^-?\d+(\.\d+)?$", value):
            rng = parse_numeric_range(s.comment)
            if rng and abs(rng[1] - rng[0]) <= 1e9:
                self._make_slider(hlay, rng, value)
                return
            # unusable / no range -> plain numeric text field
            self._make_text(hlay, value)
            return
        opts = parse_enum_options(s.comment)
        if opts:
            self._make_combo(hlay, opts, value)
            return
        self._make_text(hlay, value)

    def _make_combo(self, hlay, options, value):
        self._kind = "enum"
        cb = NoScrollComboBox()
        cb.addItems(options)
        if cb.findText(value) < 0:
            cb.insertItem(0, value)
        cb.setCurrentText(value)
        cb.currentTextChanged.connect(self._on_committed)
        self._control = cb
        cb.setToolTip(self.name_label.toolTip())
        hlay.addWidget(cb)

    def _make_text(self, hlay, value):
        self._kind = "text"
        le = QLineEdit(value)
        le.editingFinished.connect(self._on_committed)
        self._control = le
        le.setToolTip(self.name_label.toolTip())
        hlay.addWidget(le)

    def _make_slider(self, hlay, rng, value):
        self._kind = "slider"
        mn, mx, is_int = rng
        self._is_int = is_int
        slider = NoScrollSlider(Qt.Horizontal)
        numbox = QLineEdit(f"{int(float(value))}" if is_int else f"{float(value):.6f}")
        numbox.setFixedWidth(56)
        numbox.setAlignment(Qt.AlignCenter)
        if is_int:
            slider.setRange(int(mn), int(mx))
            slider.setValue(int(float(value)))
        else:
            slider.setRange(int(mn * self.SLIDER_SCALE), int(mx * self.SLIDER_SCALE))
            slider.setValue(int(float(value) * self.SLIDER_SCALE))

        def on_slider(v):
            real = v if is_int else v / self.SLIDER_SCALE
            numbox.blockSignals(True)
            numbox.setText(f"{int(real)}" if is_int else f"{real:.6f}")
            numbox.blockSignals(False)

        def on_numbox(text):
            if not text:
                return
            try:
                real = float(text)
            except ValueError:
                return
            slider.blockSignals(True)
            slider.setValue(int(real) if is_int else int(real * self.SLIDER_SCALE))
            slider.blockSignals(False)

        slider.valueChanged.connect(on_slider)
        numbox.textChanged.connect(on_numbox)
        # commit (log + dirty) only on release / edit-finished, not every tick
        slider.sliderReleased.connect(self._on_committed)
        numbox.editingFinished.connect(self._on_committed)
        self._slider, self._numbox = slider, numbox
        self._control = numbox   # value() reads the number box, like the old value_label
        slider.setToolTip(self.name_label.toolTip())
        numbox.setToolTip(self.name_label.toolTip())
        hlay.addWidget(slider, 1)
        hlay.addWidget(numbox)

    # ---- value API (same string semantics as the old get/set_widget_value) ----
    def value(self):
        if self._kind == "slider":
            return self._numbox.text()
        if self._kind == "bool":
            return str(self._control.isChecked()).lower()
        if self._kind == "enum":
            return self._control.currentText()
        return self._control.text()

    def set_value(self, value):
        value = str(value)
        self._block(True)
        if self._kind == "slider":
            self._numbox.setText(value)          # textChanged (blocked) won't fire; sync slider
            try:
                real = float(value)
                self._slider.setValue(int(real) if self._is_int else int(real * self.SLIDER_SCALE))
            except ValueError:
                pass
        elif self._kind == "bool":
            self._control.setChecked(value.strip().lower() == "true")
        elif self._kind == "enum":
            if self._control.findText(value) < 0:
                self._control.insertItem(0, value)
            self._control.setCurrentText(value)
        else:
            self._control.setText(value)
        self._block(False)
        self._sync_changed()

    def is_changed(self):
        if self._readonly:
            return False
        return not values_equal(self.value(), self.baseline)

    def revert(self):
        self.set_value(self.baseline)
        self.valueChanged.emit(self.spec.name, self.value())

    def reset_baseline(self, new_value=None):
        """After a save/reload, the on-disk value becomes the new baseline."""
        self.baseline = self.value() if new_value is None else str(new_value)
        self._sync_changed()

    def set_editable(self, editable):
        self._readonly = not editable or self._compute_readonly()
        for w in (self._slider, self._numbox, self._control):
            if w is not None:
                w.setEnabled(editable and not self._compute_readonly())
        self._sync_changed()

    # ---- search ----
    def matches(self, text):
        if not text:
            return True
        text = text.lower()
        if text in self.spec.name.lower():
            return True
        if self.spec.help_text and text in self.spec.help_text.lower():
            return True
        return text in self.value().lower()

    def set_highlight(self, on):
        self._highlight = bool(on)
        self._apply_row_style()

    # ---- theming / changed-state visuals ----
    def refresh_theme(self):
        if self._kind == "bool" and isinstance(self._control, ToggleSwitch):
            self._control.refresh_theme()
        self._sync_changed()

    def _sync_changed(self):
        changed = self.is_changed()
        c = theme_colors()
        self.dot.setVisible(changed)
        self.dot.setStyleSheet(
            f"background:{c['changed']}; border-radius:4px;" if changed else "background:transparent;")
        self.revert_btn.setVisible(changed)
        self.name_label.setStyleSheet(f"color:{c['changed'] if changed else c['text']};")
        self.range_label.setStyleSheet(f"color:{c['text_secondary']};")
        self.revert_btn.setStyleSheet(f"QToolButton {{ border:none; color:{c['text_secondary']}; }}")
        accent = c["changed"] if changed else c["accent"]
        if self._kind == "bool":
            self._control.set_changed(changed)
        elif self._kind == "slider":
            self._slider.setStyleSheet(
                f"QSlider::groove:horizontal {{ height:4px; background:{c['surface_light']}; border-radius:2px; }}"
                f"QSlider::sub-page:horizontal {{ background:{accent}; border-radius:2px; }}"
                f"QSlider::handle:horizontal {{ width:12px; height:12px; margin:-4px 0; border-radius:6px; background:{accent}; }}")
            self._numbox.setStyleSheet(
                f"QLineEdit {{ height:24px; border:1px solid {accent if changed else c['surface_light']};"
                f" border-radius:5px; background:{c['surface']}; color:{c['changed'] if changed else c['text']}; }}")
        elif self._kind == "enum":
            self._control.setStyleSheet(
                f"QComboBox {{ height:27px; border:1px solid {accent if changed else c['surface_light']};"
                f" border-radius:6px; padding:0 8px; background:{c['surface']}; color:{c['text']}; }}")
        else:
            if self._readonly:
                self._control.setStyleSheet(
                    f"QLineEdit {{ height:27px; border:1px dashed {c['surface_light']}; border-radius:6px;"
                    f" padding:0 10px; background:transparent; color:{c['text_secondary']}; }}")
            else:
                self._control.setStyleSheet(
                    f"QLineEdit {{ height:27px; border:1px solid {accent if changed else c['surface_light']};"
                    f" border-radius:6px; padding:0 10px; background:{c['surface']};"
                    f" color:{c['changed'] if changed else c['text']}; }}")
        self._apply_row_style()

    def _apply_row_style(self):
        c = theme_colors()
        if self._highlight:
            r, g, b = _hex_rgb(c["accent"])
            self.setStyleSheet(f"SettingRow {{ background: rgba({r},{g},{b},0.20); border-radius:4px; }}")
        else:
            self.setStyleSheet("SettingRow { background: transparent; }")

    # ---- internals ----
    def _on_committed(self, *args):
        self._sync_changed()
        self.valueChanged.emit(self.spec.name, self.value())

    def _block(self, on):
        for w in (self._slider, self._numbox, self._control):
            if w is not None:
                w.blockSignals(on)


def _hex_rgb(color):
    """(r, g, b) for a #rrggbb string, with a safe fallback."""
    color = (color or "").lstrip("#")
    if len(color) == 6:
        try:
            return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        except ValueError:
            pass
    return 45, 140, 255
