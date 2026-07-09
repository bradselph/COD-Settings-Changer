"""Shared pytest setup: run Qt headless and expose the editor package on sys.path.
Only `pytest` is required (no pytest-qt) -- a single offscreen QApplication is created."""
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication  # noqa: E402

_app = QApplication.instance() or QApplication([])
