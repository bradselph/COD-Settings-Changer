from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QPushButton, QLabel, QFileDialog, QMessageBox, QTabWidget,
                             QScrollArea, QCheckBox, QSlider, QComboBox, QLineEdit,
                             QGridLayout, QDialog, QTextEdit, QAction, QDockWidget)
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator

import sys
import os
import re
import stat

class GameSelector(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Game")
        self.setFixedSize(300, 150)

        layout = QVBoxLayout()
        label = QLabel("Choose the game you want to modify settings for:")
        layout.addWidget(label)

        mw2_button = QPushButton("MW2/Warzone 2023")
        mw2_button.setEnabled(False)
        layout.addWidget(mw2_button)

        mw3_button = QPushButton("MW3/Warzone 2024")
        mw3_button.clicked.connect(self.accept)
        layout.addWidget(mw3_button)

        self.setLayout(layout)

class LogWindow(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Log", parent)
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
        self.text_edit.append(message)

    def save_log(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Log", "", "Log Files (*.log);;All Files (*)")
        if file_name:
            with open(file_name, 'w') as f:
                f.write(self.text_edit.toPlainText())
            self.log(f"Log saved to {file_name}")

class OptionsEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Call of Duty Options Editor")
        self.setGeometry(100, 100, 1000, 600)

        self.options = {}
        self.widgets = {}
        self.file_path = ""
        self.read_only = False
        self.game = ""

        self.log_window = LogWindow(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.log_window)
        self.log_window.hide()

        self.create_menu()
        self.create_widgets()

        self.select_game()

    def create_menu(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        file_menu.addAction(QAction("Load Options", self, triggered=self.load_file))
        file_menu.addAction(QAction("Save Options", self, triggered=self.save_options))
        file_menu.addAction(QAction("Reload", self, triggered=self.reload_file))
        file_menu.addSeparator()
        file_menu.addAction(QAction("Exit", self, triggered=self.close))

        view_menu = menu_bar.addMenu("View")
        self.show_log_action = QAction("Show Log", self, checkable=True)
        self.show_log_action.triggered.connect(self.toggle_log_window)
        view_menu.addAction(self.show_log_action)

        options_menu = menu_bar.addMenu("Options")
        self.read_only_action = QAction("Save as Read-only", self, checkable=True)
        options_menu.addAction(self.read_only_action)
        self.edit_all_action = QAction("Enable Editing of All Values", self, checkable=True)
        self.edit_all_action.triggered.connect(self.toggle_edit_all)
        options_menu.addAction(self.edit_all_action)

    def create_widgets(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        central_widget.setLayout(layout)

    def select_game(self):
        dialog = GameSelector(self)
        if dialog.exec_():
            self.game = "MW3/Warzone 2024"
            self.load_file(auto=True)

    def toggle_log_window(self, checked):
        if checked:
            self.log_window.show()
        else:
            self.log_window.hide()

    def log(self, message):
        self.log_window.log(message)

    def load_file(self, auto=False):
        if auto:
            default_path = os.path.expanduser("~\\Documents\\Call of Duty\\players")
            file_name = "options.4.cod23.cst"
            self.file_path = os.path.join(default_path, file_name)

            if not os.path.exists(self.file_path):
                QMessageBox.warning(self, "File Not Found", f"Could not find {file_name}. Please select it manually.")
                self.file_path = QFileDialog.getOpenFileName(self, f"Select {file_name}", default_path,
                                                             "CST Files (*.cst);;All Files (*)")[0]
        else:
            default_path = os.path.expanduser("~\\Documents\\Call of Duty\\players")
            self.file_path = QFileDialog.getOpenFileName(self, "Select options.4.cod23.cst file", default_path,
                                                         "CST Files (*.cst);;All Files (*)")[0]

        if self.file_path:
            self.read_only = not os.access(self.file_path, os.W_OK)
            if self.read_only:
                QMessageBox.information(self, "Read-only File",
                                        "The selected file is read-only. You can make changes, but you'll need to save it as a new file or remove the read-only attribute.")
            self.parse_options_file()
            self.display_options()

    def parse_options_file(self):
        self.options.clear()
        current_section = ""

        try:
            with open(self.file_path, 'r') as file:
                content = file.read()
                sections = re.split(r'//\n// [A-Za-z]+\n//', content)[1:]
                section_names = re.findall(r'//\n// ([A-Za-z]+)\n//', content)

                for name, section in zip(section_names, sections):
                    self.options[name] = {"settings": []}
                    lines = section.strip().split('\n')
                    for line in lines:
                        if '=' in line and not line.strip().startswith('//'):
                            key, value = line.split('=', 1)
                            key = key.split(':')[0].strip()  # Remove version number
                            value = value.strip().strip('"')
                            comment = ""
                            if '//' in value:
                                value, comment = value.split('//', 1)
                                value = value.strip()
                                comment = comment.strip()
                            self.options[name]["settings"].append({
                                "name": key,
                                "value": value,
                                "comment": comment,
                                "editable": not line.strip().startswith("// DO NOT MODIFY")
                            })

            self.log(
                f"Loaded {sum(len(section['settings']) for section in self.options.values())} options from {self.file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to parse options file: {str(e)}")
            self.log(f"Error parsing options file: {str(e)}")

    def display_options(self):
        self.tab_widget.clear()
        self.widgets.clear()  # Clear existing widgets
        for section, data in self.options.items():
            scroll_area = QScrollArea()
            scroll_widget = QWidget()
            scroll_layout = QGridLayout()

            for i, setting in enumerate(data["settings"]):
                label = QLabel(f"{setting['name']}:")
                scroll_layout.addWidget(label, i, 0)

                value = setting['value'].strip('"')  # Remove any surrounding quotes
                if value.lower() in ('true', 'false'):
                    widget = QCheckBox()
                    widget.setChecked(value.lower() == 'true')
                elif re.match(r'^-?\d+(\.\d+)?$', value):
                    if "to" in setting['comment']:
                        numbers = re.findall(r"-?\d+(?:\.\d+)?", setting['comment'])
                        if len(numbers) >= 2:
                            try:
                                min_val, max_val = float(numbers[0]), float(numbers[1])
                                is_whole_number = '.' not in numbers[0] and '.' not in numbers[1]
                                if is_whole_number:
                                    widget = QSlider(Qt.Horizontal)
                                    widget.setRange(int(min_val), int(max_val))
                                    widget.setValue(int(float(value)))
                                    widget.setTickPosition(QSlider.TicksBelow)
                                    widget.setTickInterval(max(1, int((max_val - min_val) / 10)))
                                else:
                                    widget = QSlider(Qt.Horizontal)
                                    widget.setRange(int(min_val * 1000), int(max_val * 1000))
                                    widget.setValue(int(float(value) * 1000))
                                    widget.setTickPosition(QSlider.TicksBelow)
                                    widget.setTickInterval((int(max_val * 1000) - int(min_val * 1000)) // 10)

                                # Add a label to display the current value
                                value_label = QLabel(value)
                                scroll_layout.addWidget(value_label, i, 2)

                                # Connect the slider's valueChanged signal to update the label
                                widget.valueChanged.connect(lambda v, label=value_label, min_v=min_val, max_v=max_val, whole=is_whole_number:
                                                            self.update_slider_value(v, label, min_v, max_v, whole))
                            except ValueError:
                                widget = QLineEdit(value)
                                validator = QRegExpValidator(QRegExp(r'^-?\d+(\.\d+)?$'))
                                widget.setValidator(validator)
                        else:
                            widget = QLineEdit(value)
                            validator = QRegExpValidator(QRegExp(r'^-?\d+(\.\d+)?$'))
                            widget.setValidator(validator)
                    else:
                        widget = QLineEdit(value)
                        validator = QRegExpValidator(QRegExp(r'^-?\d+(\.\d+)?$'))
                        widget.setValidator(validator)
                elif "one of" in setting['comment']:
                    options = re.findall(r'\[(.*?)\]', setting['comment'])[0].split(', ')
                    widget = QComboBox()
                    widget.addItems(options)
                    widget.setCurrentText(value)
                else:
                    widget = QLineEdit(value)
                scroll_layout.addWidget(widget, i, 1)
                widget.setEnabled(setting['editable'])
                self.widgets[f"{section}_{setting['name']}"] = widget
                comment = QLabel(setting['comment'])
                scroll_layout.addWidget(comment, i, 3)
            scroll_widget.setLayout(scroll_layout)
            scroll_area.setWidget(scroll_widget)
            scroll_area.setWidgetResizable(True)
            self.tab_widget.addTab(scroll_area, section)
        self.update_widget_states()

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
                    widget = self.widgets[widget_key]
                    widget.setEnabled(self.edit_all_action.isChecked() or setting["editable"])

    def toggle_edit_all(self, checked):
        self.update_widget_states()

    def save_options(self):
        self.log("Starting save_options method")
        if not self.file_path:
            QMessageBox.critical(self, "Error", "No file loaded")
            return

        if self.read_only:
            new_file_path, _ = QFileDialog.getSaveFileName(self, "Save As", os.path.dirname(self.file_path),
                                                           "CST Files (*.cst);;All Files (*)")
            if not new_file_path:
                return
            self.file_path = new_file_path
            self.read_only = False

        try:
            with open(self.file_path, 'r') as file:
                lines = file.readlines()

            for i, line in enumerate(lines):
                if "=" in line and not line.strip().startswith('//'):
                    key = line.split('=', 1)[0].strip().split(':')[0]
                    for section, data in self.options.items():
                        for setting in data["settings"]:
                            if key == setting["name"] and setting["editable"]:
                                widget_key = f"{section}_{setting['name']}"
                                if widget_key in self.widgets:
                                    widget = self.widgets[widget_key]
                                    if isinstance(widget, QCheckBox):
                                        value = str(widget.isChecked()).lower()
                                    elif isinstance(widget, QSlider):
                                        is_whole_number = '.' not in setting['comment']
                                        if is_whole_number:
                                            value = str(widget.value())
                                        else:
                                            value = f"{widget.value() / 1000:.6f}"
                                    elif isinstance(widget, QComboBox):
                                        value = widget.currentText()
                                    elif isinstance(widget, QLineEdit):
                                        value = widget.text()
                                        if '.' not in setting['comment'] and value.replace('.', '').isdigit():
                                            value = str(int(float(value)))
                                    else:
                                        continue  # Skip if we can't determine the widget type
                                    # Check if the value is within the recommended range
                                    if "to" in setting['comment']:
                                        numbers = re.findall(r"-?\d+(?:\.\d+)?", setting['comment'])
                                        if len(numbers) >= 2:
                                            try:
                                                min_val, max_val = float(numbers[0]), float(numbers[1])
                                                float_value = float(value)
                                                if float_value < min_val or float_value > max_val:
                                                    user_choice = QMessageBox.warning(
                                                    self,
                                                    "Value out of range",
                                                    f"The value {value} for {setting['name']} is outside the recommended range ({min_val} to {max_val}). Do you want to proceed?",
                                                    QMessageBox.Yes | QMessageBox.No,
                                                    QMessageBox.No
                                                )
                                                    if user_choice == QMessageBox.No:
                                                        continue
                                            except ValueError:
                                                pass

                                    lines[i] = f"{line.split('=')[0]}= \"{value}\"{' // ' + setting['comment'] if setting['comment'] else ''}\n"

            with open(self.file_path, 'w') as file:
                file.writelines(lines)

            if self.read_only_action.isChecked():
                os.chmod(self.file_path, stat.S_IREAD)
                self.read_only = True
            else:
                os.chmod(self.file_path, stat.S_IWRITE | stat.S_IREAD)
                self.read_only = False

            self.log(f"Options saved to {self.file_path}")
            QMessageBox.information(self, "Success", "Options saved successfully")
            self.reload_file()
        except Exception as e:
            error_msg = f"Failed to save options: {str(e)}\n"
            error_msg += f"Error type: {type(e).__name__}\n"
            error_msg += f"Error args: {e.args}\n"
            QMessageBox.critical(self, "Error", error_msg)
            self.log(error_msg)

    def reload_file(self):
        if self.file_path:
            self.parse_options_file()
            self.display_options()
            self.log("File reloaded")

def main():
    app = QApplication(sys.argv)
    editor = OptionsEditor()
    editor.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()