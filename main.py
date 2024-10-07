#!/usr/bin/env python
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QPushButton, QLabel, QFileDialog, QMessageBox, QTabWidget,
                             QScrollArea, QCheckBox, QSlider, QComboBox, QLineEdit,
                             QGridLayout, QDialog, QTextEdit, QAction, QDockWidget, QHBoxLayout, QSizePolicy)
from PyQt5.QtCore import QSettings
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator
from help_texts import get_help_texts
from PyQt5.QtGui import QIcon

import sys
import os
import re
import stat

class GameSelector(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Game")
        self.setFixedSize(300, 200)

        settings = QSettings("Lif3Snatcher's", "CODOptionsEditor")
        if not settings.value("app_launched", False, type=bool):
            self.show_first_time_warning()
            settings.setValue("app_launched", True)

        layout = QVBoxLayout()
        label = QLabel("Choose the game you want to modify settings for:")
        layout.addWidget(label)

        self.mw2_button = QPushButton("MW2/Warzone 2023")
        self.mw2_button.clicked.connect(lambda: self.select_game("MW2/Warzone 2023"))
        layout.addWidget(self.mw2_button)

        self.mw3_button = QPushButton("MW3/Warzone 2024")
        self.mw3_button.clicked.connect(lambda: self.select_game("MW3/Warzone 2024"))
        layout.addWidget(self.mw3_button)

        self.bo6_button = QPushButton("BO6")
        self.bo6_button.clicked.connect(lambda: self.select_game("BO6"))
        self.bo6_button.setEnabled(False)
        layout.addWidget(self.bo6_button)

        self.selected_game = None
        self.setLayout(layout)

        self.setup_window_flags()

    def show_first_time_warning(self):
        warning_text = """
        WARNING: Advanced Application
    
        This is an advanced application for editing Call of Duty game settings. 
        Caution should be taken when making changes, as incorrect modifications 
        may affect your game performance or stability.
    
        It is recommended to backup your settings files before making any changes.
    
        Use this application at your own risk.
        """

        warning_dialog = QMessageBox(self)
        warning_dialog.setWindowTitle("First-Time User Warning")
        warning_dialog.setText(warning_text)
        warning_dialog.setIcon(QMessageBox.Warning)
        warning_dialog.setStandardButtons(QMessageBox.Ok)
        warning_dialog.exec_()

    def show_read_only_message(self):
        message = (
                "The settings files have been saved as read-only. This prevents the game from overwriting your settings.\n\n"
                "If you encounter any problems or want to allow the game to modify these files again, you can undo this by:\n"
                "1. Locating the changed files\n"
                "2. Right-clicking on each file\n"
                "3. Selecting 'Properties'\n"
                "4. Unchecking the 'Read-only' attribute\n"
                "5. Clicking 'Apply' and then 'OK'\n\n"
                "This will allow the game to modify and overwrite these files again."
        )
        QMessageBox.information(self, "Read-only Settings", message)

    def setup_window_flags(self):
        self.setWindowFlags(self.windowFlags() | Qt.Window | Qt.WindowStaysOnTopHint)

    def showEvent(self, event):
        super().showEvent(event)
        self.raise_()
        self.activateWindow()

    def select_game(self, game):
        self.selected_game = game
        self.accept()

class LogWindow(QDockWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Log")
        self.setAllowedAreas(Qt.AllDockWidgetAreas)

        content = QWidget()
        layout = QVBoxLayout(content)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)

        save_button = QPushButton("Save Log")
        save_button.clicked.connect(self.save_log)
        layout.addWidget(save_button)

        self.setWidget(content)

    def log(self, message):
        with open("application_log.txt", 'a') as log_file:
            log_file.write(message + "\n")
        self.text_edit.append(message)

    def save_log(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Log", "", "Log Files (*.log);;All Files (*)")
        if file_name:
            with open(file_name, 'w') as f:
                f.write(self.text_edit.toPlainText())
            self.log(f"Log saved to {file_name}")

    def closeEvent(self, event):
        if isinstance(self.parent(), OptionsEditor):
            self.parent().show_log_action.setChecked(False)
            self.parent().log_window_detached = self.isFloating()
        super().closeEvent(event)

class NoScrollSlider(QSlider):
    def wheelEvent(self, event):
        event.ignore()

class NoScrollComboBox(QComboBox):
    def wheelEvent(self, event):
        event.ignore()

class OptionsEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Call of Duty Options Editor")
        self.setGeometry(100, 100, 1000, 600)
        self.show_log_action = QAction("Show Log", self, checkable=True)
        self.read_only_action = QAction("Save as Read-only", self, checkable=True)
        self.read_only_checkbox = QCheckBox("Save as Read-only")
        self.read_only_checkbox.setToolTip("Check this to save the file as read-only and prevent the game from overwriting your settings.")
        self.layout().addWidget(self.read_only_checkbox)
        self.tab_widget = QTabWidget()

        self.widget_mappings = {
                "boolean": QCheckBox,
                "numeric": NoScrollSlider,
                "string": QLineEdit,
                "dropdown": NoScrollComboBox
        }
        if getattr(sys, 'frozen', False):
            application_path = sys._MEIPASS
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(application_path, 'gear_icon.ico')
        self.setWindowIcon(QIcon(icon_path))
        self.options = {}
        self.widgets = {}
        self.file_path = ""
        self.game_agnostic_file_path = ""
        self.read_only = False
        self.game = ""
        self.selected_game = ""
        self.non_editable_fields = [
                "SoundOutputDevice", "SoundInputDevice", "VoiceOutputDevice", "VoiceInputDevice",
                "Monitor", "GPUName", "DetectedFrequencyGHz", "DetectedMemoryAmountMB", "LastUsedGPU",
                "GPUDriverVersion", "DisplayDriverVersion", "DisplayDriverVersionRecommended", "ESSDI"
        ]
        self.setting_options = {
                "VoiceChatEffect": ["mw_default", "mw", "mw_classic"],
                "TargetRefreshRate": ["60", "120"],
                "Resolution": ["1920x1080", "2560x1440", "3840x2160"],
                # add more here as needed
        }
        self.unsaved_changes = False

        self.log_window = LogWindow(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.log_window)
        self.log_window.hide()

        self.log_window_detached = False
        self.log_window.topLevelChanged.connect(self.on_log_window_detached)

        self.create_menu()
        self.create_widgets()
        self.help_texts = get_help_texts()

        self.setStyleSheet("""
            QToolTip {
                background-color: #2a82da;
                color: white;
                border: 1px solid white;
                padding: 5px;
            }
        """)

        self.select_game()

    def select_game(self):
        try:
            dialog = GameSelector(self)
            if dialog.exec_():
                self.game = dialog.selected_game
                self.selected_game = self.game
                self.log(f"Selected game: {self.game}")
                self.load_file(auto=True)
                self.raise_()
                self.activateWindow()
            else:
                self.log("Game selection cancelled")
                self.close()
        except Exception as e:
            self.log(f"Error in select_game: {str(e)}")
            QMessageBox.critical(self, "Game Selection Error", f"An error occurred during game selection: {str(e)}")

    def get_combobox_options(self, setting):
        return self.setting_options.get(setting["name"], [])

    def create_widget(self, setting, value):
        setting_type = self.get_setting_type(setting)
        widget_class = self.widget_mappings.get(setting_type, QLineEdit)
        widget = widget_class()

        if isinstance(widget, QSlider):
            widget.setValue(int(value))
            widget.valueChanged.connect(self.set_unsaved_changes)
        elif isinstance(widget, QComboBox):
            widget.addItems(self.get_combobox_options(setting))
            widget.setCurrentText(value)
            widget.currentTextChanged.connect(self.set_unsaved_changes)
        else:
            widget.setText(value)
            widget.textChanged.connect(self.set_unsaved_changes)

        return widget

    def get_setting_type(self, setting):
        if setting["name"].endswith("Volume") or "Sensitivity" in setting["name"]:
            return "numeric"
        elif setting["name"].startswith("Enable") or setting["value"].lower() in ("true", "false"):
            return "boolean"
        elif "one of" in setting["comment"]:
            return "dropdown"
        return "string"

    def log(self, message):
        if hasattr(self, 'log_window'):
            self.log_window.log(message)
        else:
            print(message)

    def create_menu(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        file_menu.addAction(QAction("Load Options", self, triggered=self.load_file))
        file_menu.addAction(QAction("Save Options", self, triggered=self.save_options))
        file_menu.addAction(QAction("Reload", self, triggered=self.reload_file))
        file_menu.addAction(QAction("Change Game", self, triggered=self.change_game))
        file_menu.addSeparator()
        file_menu.addAction(QAction("Exit", self, triggered=self.close))

        view_menu = menu_bar.addMenu("View")
        self.show_log_action.triggered.connect(self.toggle_log_window)
        view_menu.addAction(self.show_log_action)

        options_menu = menu_bar.addMenu("Options")
        options_menu.addAction(self.read_only_action)

        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction(QAction("About", self, triggered=self.show_about_dialog))
        help_menu.addAction(QAction("Show Warning", self, triggered=self.show_first_time_warning))

        options_menu = self.menuBar().addMenu("Options")
        clear_settings_action = QAction("Clear All Settings", self)
        clear_settings_action.triggered.connect(self.clear_all_settings)
        options_menu.addAction(clear_settings_action)

    def show_first_time_warning(self):
        warning_text = """
        WARNING: Advanced Application
    
        This is an advanced application for editing Call of Duty game settings. 
        Caution should be taken when making changes, as incorrect modifications 
        may affect your game performance or stability.
    
        It is recommended to backup your settings files before making any changes.
    
        Use this application at your own risk.
        """

        warning_dialog = QMessageBox(self)
        warning_dialog.setWindowTitle("First-Time User Warning")
        warning_dialog.setText(warning_text)
        warning_dialog.setIcon(QMessageBox.Warning)
        warning_dialog.setStandardButtons(QMessageBox.Ok)
        warning_dialog.exec_()

    def show_about_dialog(self):
        about_text = """
        Call of Duty Options Editor

        Version: 1.0

        This application is FREE and costs $0. If you paid for this app, you got scammed.
        
        This application is designed to edit options for Call of Duty games.

        DISCLAIMER: This application and its developer are not in any way, shape, or form 
        tied to or related with Activision, the publisher of Call of Duty games.


        Third-party software used:
        - PyQt5 (GPL v3)
        - Python (PSF License)

        """

        about_dialog = QMessageBox(self)
        about_dialog.setWindowTitle("About")
        about_dialog.setText(about_text)
        about_dialog.setIcon(QMessageBox.Information)
        about_dialog.exec_()

    def clear_all_settings(self):
        reply = QMessageBox.question(self, 'Clear Settings',
                                     "Are you sure you want to clear all settings? "
                                     "This will reset the application to its initial state.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            settings = QSettings("Lif3Snatcher's", "CODOptionsEditor")
            settings.clear()
            settings.sync()

            QMessageBox.information(self, "Settings Cleared",
                                    "All settings have been cleared. "
                                    "The application will now close. "
                                    "The next launch will be like a fresh install.")

            self.close()

    def closeEvent(self, event):
        if self.check_unsaved_changes():
            settings = QSettings("Lif3Snatcher's", "CODOptionsEditor")
            if not settings.contains("app_launched"):
                event.accept()
            else:
                event.accept()
        else:
            event.ignore()

    def create_widgets(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        central_widget.setLayout(layout)

    def change_game(self):
        if self.check_unsaved_changes():
            try:
                dialog = GameSelector(self)
                if dialog.exec_():
                    self.game = dialog.selected_game
                    self.selected_game = self.game
                    self.log(f"Changed game to: {self.game}")
                    self.load_file(auto=True)
                    self.raise_()
                    self.activateWindow()
            except Exception as e:
                self.log(f"Error in change_game: {str(e)}")
                QMessageBox.critical(self, "Game Change Error", f"An error occurred while changing game: {str(e)}")

    def on_log_window_detached(self, floating):
        self.log_window_detached = floating

    def toggle_log_window(self, checked):
        if checked:
            if not self.log_window.isVisible():
                if self.log_window_detached:
                    self.log_window = LogWindow(self)
                    self.addDockWidget(Qt.BottomDockWidgetArea, self.log_window)
                    self.log_window.topLevelChanged.connect(self.on_log_window_detached)
                    self.log_window_detached = False
                self.log_window.show()
            elif self.log_window_detached:
                self.log_window.setFloating(False)
                self.addDockWidget(Qt.BottomDockWidgetArea, self.log_window)
                self.log_window_detached = False
        else:
            self.log_window.close()

    def show_log_window(self):
        if not self.log_window.isVisible():
            if self.log_window_detached:
                self.log_window = LogWindow(self)
                self.addDockWidget(Qt.BottomDockWidgetArea, self.log_window)
                self.log_window.topLevelChanged.connect(self.on_log_window_detached)
                self.log_window_detached = False
            self.log_window.show()
        elif self.log_window_detached:
            self.log_window.setFloating(False)
            self.addDockWidget(Qt.BottomDockWidgetArea, self.log_window)
            self.log_window_detached = False

    def hide_log_window(self):
        self.log_window.close()

    def load_file(self, auto=False):
        if not self.game:
            self.log("No game selected, cannot load file")
            return
        try:
            self.log("Starting load_file method")
            default_path = os.path.expanduser("~\\Documents\\Call of Duty\\players")
            file_names = {
                    "game_specific": "s.1.0.cod24.txt" if self.game == "BO6" else ("options.4.cod23.cst" if self.game == "MW3/Warzone 2024" else "options.3.cod22.cst"),
                    "game_agnostic": "gamerprofile.pc.0.BASE.cst" if self.game == "BO6" else "gamerprofile.0.BASE.cst"
            }

            files_to_load = {}
            for file_type, file_name in file_names.items():
                file_path = os.path.join(default_path, file_name)
                if not auto or not os.path.exists(file_path):
                    file_path = self.get_file_path(file_type, file_name, default_path)

                if file_path:
                    files_to_load[file_type] = file_path
                else:
                    self.log(f"File selection cancelled for {file_type}")
                    return

            if len(files_to_load) == 2:
                self.file_path = files_to_load["game_specific"]
                self.game_agnostic_file_path = files_to_load["game_agnostic"]

                self.log(f"Loading files: {self.file_path} and {self.game_agnostic_file_path}")
                self.read_only = not os.access(self.file_path, os.W_OK) or not os.access(self.game_agnostic_file_path, os.W_OK)
                if self.read_only:
                    self.show_read_only_message()
                self.parse_options_file()
                self.display_options()
                self.unsaved_changes = False
            else:
                self.log("File selection incomplete")
                self.show_error_message("File Selection", "Both files are required to proceed. Please select both files.")
        except Exception as e:
            self.log(f"Error in load_file: {str(e)}")
            self.show_error_message("File Loading Error", f"An error occurred while loading files: {str(e)}")

    def get_file_path(self, file_type, file_name, default_path):
        message = (f"Please select the {file_type} file:\n"
                   f"{file_name}\n\n"
                   f"This file is typically located in:\n"
                   f"{default_path}")

        msg_box = QMessageBox(QMessageBox.Information, "Select File", message)
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg_box.setDefaultButton(QMessageBox.Ok)
        msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowStaysOnTopHint)

        result = msg_box.exec_()
        if result == QMessageBox.Ok:
            file_path, _ = QFileDialog.getOpenFileName(self, f"Select {file_name}", default_path,
                                                       "CST Files (*.cst);;TXT Files (*.txt);;All Files (*)")
            if file_path:
                return file_path
            else:
                self.log(f"No file selected for {file_type}")
                return None
        else:
            self.log(f"File selection cancelled for {file_type}")
            return None

    def show_read_only_message(self):
        msg_box = QMessageBox(QMessageBox.Information, "Read-only File",
                              "One or both of the selected files are read-only. "
                              "You can make changes, but you'll need to save them as new files "
                              "or remove the read-only attribute.")
        msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowStaysOnTopHint)
        msg_box.exec_()

    def show_error_message(self, title, message):
        msg_box = QMessageBox(QMessageBox.Critical, title, message)
        msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowStaysOnTopHint)
        msg_box.exec_()

    def parse_options_file(self):
        self.options.clear()
        self.parse_file(self.file_path, "GameSpecific")
        self.parse_file(self.game_agnostic_file_path, "GameAgnostic")
        self.log(f"Loaded {sum(len(section['settings']) for section in self.options.values())} options from both files")

    def parse_file(self, file_path, file_type):
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                if file_type == "GameSpecific":
                    if self.game == "BO6":
                        sections = re.split(r'//\n// [A-Za-z ]+\n//', content)[1:]
                        section_names = re.findall(r'//\n// ([A-Za-z ]+)\n//', content)
                    else:
                        sections = re.split(r'//\n// [A-Za-z]+\n//', content)[1:]
                        section_names = re.findall(r'//\n// ([A-Za-z]+)\n//', content)
                else:  # GameAgnostic
                    sections = [content]
                    section_names = ["GameAgnostic"]
                for name, section in zip(section_names, sections):
                    if name not in self.options:
                        self.options[name] = {"settings": []}
                    lines = section.strip().split('\n')
                    for line in lines:
                        if '=' in line and not line.strip().startswith('//'):
                            key, value = line.split('=', 1)
                            if file_type == "GameSpecific":
                                if self.game == "BO6":
                                    key = key.split('@')[0].strip()
                                else:
                                    key = key.split(':')[0].strip()
                            else:
                                key = key.split('@')[0].strip()
                            value = value.strip().strip('"')
                            comment = ""
                            if '//' in value:
                                value, comment = value.split('//', 1)
                                value = value.strip()
                                comment = comment.strip()
                            self.options[name]["settings"].append({
                                    "name":      key,
                                    "value":     value,
                                    "comment":   comment,
                                    "editable":  not line.strip().startswith("// DO NOT MODIFY"),
                                    "file_type": file_type
                            })
            self.log(f"Loaded {sum(len(section['settings']) for section in self.options.values())} options from {file_path}")
        except Exception as e:
            self.show_error_message("Error", f"Failed to parse options file {file_path}: {str(e)}")
            self.log(f"Error parsing options file {file_path}: {str(e)}")

    def display_options(self):
        self.tab_widget.clear()
        self.widgets.clear()
        for section, data in self.options.items():
            scroll_area = QScrollArea()
            scroll_widget = QWidget()
            scroll_layout = QGridLayout()
            scroll_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            for i, setting in enumerate(data["settings"]):
                label = QLabel(f"{setting['name']}:")
                scroll_layout.addWidget(label, i, 0)
                value = setting['value'].strip('"')
                widget = self.create_widget(setting, value)
                if isinstance(widget, tuple):  # For sliders with value labels
                    slider, value_label = widget
                    slider_layout = QHBoxLayout()
                    slider_layout.addWidget(slider)
                    slider_layout.addWidget(value_label)
                    scroll_layout.addLayout(slider_layout, i, 1)
                    self.widgets[f"{section}_{setting['name']}"] = {"slider": slider, "value_label": value_label}
                else:
                    scroll_layout.addWidget(widget, i, 1)
                    self.widgets[f"{section}_{setting['name']}"] = {"widget": widget}

                is_editable = setting['editable'] and not setting['name'].startswith("// DO NOT MODIFY") and setting[
                    'name'] not in self.non_editable_fields
                if isinstance(widget, tuple):
                    slider.setEnabled(is_editable)
                    value_label.setEnabled(is_editable)
                else:
                    widget.setEnabled(is_editable)

                tooltip_text = self.help_texts.get(setting['name'], "No help text available for this setting.")
                tooltip_text += f"\n\nValid range: {setting['comment']}" if setting['comment'] else ""
                if isinstance(widget, tuple):
                    slider.setToolTip(tooltip_text)
                    value_label.setToolTip(tooltip_text)
                else:
                    widget.setToolTip(tooltip_text)
                comment = QLabel(setting['comment'])
                scroll_layout.addWidget(comment, i, 3)
                file_type_label = QLabel(f"({setting['file_type']})")
                scroll_layout.addWidget(file_type_label, i, 4)
            scroll_widget.setLayout(scroll_layout)
            scroll_area.setWidget(scroll_widget)
            scroll_area.setWidgetResizable(True)
            self.tab_widget.addTab(scroll_area, section)
        self.update_widget_states()

    def create_widget(self, setting, value):
        if setting['name'] in self.non_editable_fields:
            widget = QLineEdit(value)
            widget.setReadOnly(True)
        elif setting['name'] in ["VoiceChatEffect", "TargetRefreshRate", "Resolution", "RefreshRate"]:
            widget = NoScrollComboBox()
            options = self.get_options_for_combobox(setting)
            widget.addItems(options)
            widget.setCurrentText(value)
            widget.currentTextChanged.connect(self.set_unsaved_changes)
        elif value.lower() in ('true', 'false'):
            widget = QCheckBox()
            widget.setChecked(value.lower() == 'true')
            widget.stateChanged.connect(self.set_unsaved_changes)
        elif re.match(r'^-?\d+(\.\d+)?$', value):
            return self.create_slider_widget(setting, value)
            if isinstance(widget, QSlider):
                widget.valueChanged.connect(self.set_unsaved_changes)
            else:
                widget.textChanged.connect(self.set_unsaved_changes)
        elif "one of" in setting['comment']:
            widget = NoScrollComboBox()
            options = re.findall(r'\[(.*?)\]', setting['comment'])
            if options:
                widget.addItems(options[0].split(', '))
                widget.setCurrentText(value)
                widget.currentTextChanged.connect(self.set_unsaved_changes)
            else:
                widget = QLineEdit(value)
                widget.textChanged.connect(self.set_unsaved_changes)
        else:
            widget = QLineEdit(value)
            widget.textChanged.connect(self.set_unsaved_changes)
        return widget

    def get_options_for_combobox(self, setting):
        if setting['name'] == "VoiceChatEffect":
            return setting['comment'].split("one of ")[1].strip("[]").split(", ")
        elif setting['name'] == "TargetRefreshRate":
            return ["60 Hz", "120 Hz"]
        elif setting['name'] == "Resolution":
            return ["1920x1080", "2560x1440", "3840x2160"]
        elif setting['name'] == "RefreshRate":
            return ["60 Hz", "120 Hz"]

    def create_slider_widget(self, setting, value):
        if "to" in setting['comment']:
            numbers = re.findall(r"-?\d+(?:\.\d+)?", setting['comment'])
            if len(numbers) >= 2:
                try:
                    min_val, max_val = float(numbers[0]), float(numbers[1])
                    is_whole_number = '.' not in numbers[0] and '.' not in numbers[1]
                    slider = NoScrollSlider(Qt.Horizontal)
                    line_edit = QLineEdit(f"{float(value):.6f}" if not is_whole_number else f"{int(value)}")

                    if is_whole_number:
                        slider.setRange(int(min_val), int(max_val))
                        slider.setValue(int(float(value)))
                    else:
                        slider.setRange(int(min_val * 1000), int(max_val * 1000))
                        slider.setValue(int(float(value) * 1000))

                    def update_slider_value(slider_value):
                        real_value = slider_value if is_whole_number else slider_value / 1000
                        line_edit.setText(f"{real_value:.6f}" if not is_whole_number else f"{int(real_value)}")

                    def update_line_value(text):
                        if text:
                            real_value = float(text)
                            if is_whole_number:
                                slider.setValue(int(real_value))
                            else:
                                slider.setValue(int(real_value * 1000))

                    slider.valueChanged.connect(update_slider_value)
                    line_edit.textChanged.connect(update_line_value)
                    slider.valueChanged.connect(self.set_unsaved_changes)
                    return slider, line_edit
                except ValueError:
                    pass
        widget = QLineEdit(value)
        widget.textChanged.connect(self.set_unsaved_changes)
        return widget

    def update_slider_value(self, value, label, min_val, max_val, whole_number):
        if whole_number:
            real_value = value
        else:
            real_value = value / 1000
        label.setText(f"{real_value:.6f}" if not whole_number else f"{real_value}")

    def update_widget_states(self):
        for section, data in self.options.items():
            for setting in data["settings"]:
                widget_key = f"{section}_{setting['name']}"
                if widget_key in self.widgets:
                    widget_data = self.widgets[widget_key]
                    is_editable = setting['editable'] and not setting['name'].startswith("// DO NOT MODIFY") and setting[
                        'name'] not in self.non_editable_fields
                    if "slider" in widget_data:
                        widget_data["slider"].setEnabled(is_editable)
                        widget_data["value_label"].setEnabled(is_editable)
                    else:
                        widget_data["widget"].setEnabled(is_editable)
    def set_unsaved_changes(self):
        self.unsaved_changes = True

    def save_options(self):
        self.log(f"Starting save_options method for {self.game}")
        if not self.file_path or not self.game_agnostic_file_path:
            self.show_error_message("Error", "One or both files are not loaded")
            return
        try:
            self.save_file_with_permissions(self.file_path, "GameSpecific")
            self.save_file_with_permissions(self.game_agnostic_file_path, "GameAgnostic")

            # Set files as read-only if checkbox is checked
            if self.read_only_checkbox.isChecked():
                os.chmod(self.file_path, 0o444)  # Read-only for user, group, and others
                os.chmod(self.game_agnostic_file_path, 0o444)
                self.show_read_only_message()

            self.log(f"Options saved to {self.file_path} and {self.game_agnostic_file_path}")
            QMessageBox.information(self, "Success", f"Options for {self.game} saved successfully")
            self.unsaved_changes = False
            self.reload_file()
        except Exception as e:
            error_msg = f"Failed to save options for {self.game}: {str(e)}\n"
            error_msg += f"Error type: {type(e).__name__}\n"
            error_msg += f"Error args: {e.args}\n"
            self.show_error_message("Error", error_msg)
            self.log(error_msg)

    def update_file_permissions(self):
        if self.read_only_action.isChecked():
            os.chmod(self.file_path, stat.S_IREAD)
            os.chmod(self.game_agnostic_file_path, stat.S_IREAD)
            self.read_only = True
        else:
            os.chmod(self.file_path, stat.S_IWRITE | stat.S_IREAD)
            os.chmod(self.game_agnostic_file_path, stat.S_IWRITE | stat.S_IREAD)
            self.read_only = False

    def save_file_with_permissions(self, file_path, file_type):
        original_permissions = os.stat(file_path).st_mode
        try:
            os.chmod(file_path, stat.S_IWRITE | stat.S_IREAD)
            self.save_file(file_path, file_type)
        finally:
            os.chmod(file_path, original_permissions)

    def save_file(self, file_path, file_type):
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
            for i, line in enumerate(lines):
                if '=' in line and not line.strip().startswith('//'):
                    key = line.split('=', 1)[0].strip()
                    if file_type == "GameSpecific":
                        if self.game == "BO6":
                            key = key.split('@')[0]
                        else:
                            key = key.split(':')[0]
                    else:
                        key = key.split('@')[0]
                    for section, data in self.options.items():
                        for setting in data["settings"]:
                            if key == setting["name"] and setting["editable"] and setting["file_type"] == file_type:
                                widget_key = f"{section}_{setting['name']}"
                                if widget_key in self.widgets:
                                    widget_data = self.widgets[widget_key]
                                    value = self.get_widget_value(widget_data)
                                    if self.is_value_in_range(setting, value):
                                        lines[i] = self.format_line(file_type, line, setting, value)
                                    else:
                                        self.log(f"Value {value} for {setting['name']} is out of range. Skipping.")
            with open(file_path, 'w') as file:
                file.writelines(lines)
        except Exception as e:
            error_msg = f"Failed to save options to {file_path}: {str(e)}\n"
            error_msg += f"Error type: {type(e).__name__}\n"
            error_msg += f"Error args: {e.args}\n"
            raise Exception(error_msg)

    def get_widget_value(self, widget_data):
        if "slider" in widget_data:
            return widget_data["value_label"].text()
        elif isinstance(widget_data["widget"], QCheckBox):
            return str(widget_data["widget"].isChecked()).lower()
        elif isinstance(widget_data["widget"], QComboBox):
            value = widget_data["widget"].currentText()
            if widget_data["widget"].objectName() == "TargetRefreshRate":
                return value.split()[0]
            return value
        elif isinstance(widget_data["widget"], QLineEdit):
            return widget_data["widget"].text()
        return ""

    def is_value_in_range(self, setting, value):
        if "to" in setting['comment']:
            numbers = re.findall(r"-?\d+(?:\.\d+)?", setting['comment'])
            if len(numbers) >= 2:
                try:
                    min_val, max_val = float(numbers[0]), float(numbers[1])
                    float_value = float(value)
                    return min_val <= float_value <= max_val
                except ValueError:
                    pass
        return True

    def format_line(self, file_type, line, setting, value):
        if file_type == "GameSpecific":
            if self.game == "BO6":
                return f"{line.split('=')[0]}= {value}{' // ' + setting['comment'] if setting['comment'] else ''}\n"
            else:
                return f"{line.split('=')[0]}= \"{value}\"{' // ' + setting['comment'] if setting['comment'] else ''}\n"
        else:  # GameAgnostic
            return f"{line.split('=')[0]}= {value}{' // ' + setting['comment'] if setting['comment'] else ''}\n"

    def reload_file(self):
        if self.file_path and self.game_agnostic_file_path:
            self.parse_options_file()
            self.display_options()
            self.unsaved_changes = False
            self.log(f"Files reloaded for {self.game}")

    def check_unsaved_changes(self):
        if self.unsaved_changes:
            reply = QMessageBox.question(self, 'Unsaved Changes',
                                         "You have unsaved changes. Do you want to save them?",
                                         QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                                         QMessageBox.Save)
            if reply == QMessageBox.Save:
                self.save_options()
                return True
            elif reply == QMessageBox.Cancel:
                return False
        return True

    def closeEvent(self, event):
        if self.check_unsaved_changes():
            event.accept()
        else:
            event.ignore()

def main():
    app = QApplication(sys.argv)
    try:
        editor = OptionsEditor()
        editor.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Unhandled exception in main: {str(e)}")
        QMessageBox.critical(None, "Critical Error", f"An unhandled error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
