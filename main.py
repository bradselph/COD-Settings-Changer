#!/usr/bin/env python
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
							 QPushButton, QLabel, QFileDialog, QMessageBox, QTabWidget,
							 QScrollArea, QCheckBox, QSlider, QComboBox, QLineEdit,
							 QGridLayout, QDialog, QTextEdit, QAction, QDockWidget)
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator
from help_texts import get_help_texts
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
		self.unsaved_changes = False

		self.log_window = LogWindow(self)
		self.addDockWidget(Qt.BottomDockWidgetArea, self.log_window)
		self.log_window.show()

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
		file_menu.addSeparator()
		file_menu.addAction(QAction("Exit", self, triggered=self.close))

		view_menu = menu_bar.addMenu("View")
		self.show_log_action = QAction("Show Log", self, checkable=True)
		self.show_log_action.triggered.connect(self.toggle_log_window)
		view_menu.addAction(self.show_log_action)

		options_menu = menu_bar.addMenu("Options")
		self.read_only_action = QAction("Save as Read-only", self, checkable=True)
		options_menu.addAction(self.read_only_action)

	def create_widgets(self):
		central_widget = QWidget()
		self.setCentralWidget(central_widget)

		layout = QVBoxLayout()
		self.tab_widget = QTabWidget()
		layout.addWidget(self.tab_widget)
		central_widget.setLayout(layout)

	def select_game(self):
		try:
			dialog = GameSelector(self)
			if dialog.exec_():
				self.game = "MW3/Warzone 2024"
				self.selected_game = self.game
				self.log(f"Selected game: {self.game}")
				self.load_file(auto=True)
			else:
				self.log("Game selection cancelled")
				self.close()
		except Exception as e:
			self.log(f"Error in select_game: {str(e)}")
			QMessageBox.critical(self, "Game Selection Error", f"An error occurred during game selection: {str(e)}")

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

	def load_file(self, auto=False):
		try:
			self.log("Starting load_file method")
			default_path = os.path.expanduser("~\\Documents\\Call of Duty\\players")
			file_names = {
					"game_specific": "options.4.cod23.cst",
					"game_agnostic": "gamerprofile.0.BASE.cst"
			}

			for file_type, file_name in file_names.items():
				file_path = os.path.join(default_path, file_name)
				if not auto or not os.path.exists(file_path):
					file_path = self.get_file_path(file_type, file_name, default_path)

				if file_type == "game_specific":
					self.file_path = file_path
				else:
					self.game_agnostic_file_path = file_path

			if self.file_path and self.game_agnostic_file_path:
				self.log(f"Loading files: {self.file_path} and {self.game_agnostic_file_path}")
				self.read_only = not os.access(self.file_path, os.W_OK) or not os.access(self.game_agnostic_file_path, os.W_OK)
				if self.read_only:
					self.show_read_only_message()
				self.parse_options_file()
				self.display_options()
				self.unsaved_changes = False
			else:
				self.log("File selection cancelled")
				self.close()
		except Exception as e:
			self.log(f"Error in load_file: {str(e)}")
			self.show_error_message("File Loading Error", f"An error occurred while loading files: {str(e)}")

	def get_file_path(self, file_type, file_name, default_path):
		self.log(f"File not found: {file_name}")
		msg_box = QMessageBox(QMessageBox.Warning, "File Not Found", f"Could not find {file_name}. Please select it manually.")
		msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowStaysOnTopHint)
		msg_box.exec_()
		return QFileDialog.getOpenFileName(self, f"Select {file_name}", default_path, "CST Files (*.cst);;All Files (*)")[0]

	def show_read_only_message(self):
		msg_box = QMessageBox(QMessageBox.Information, "Read-only File",
							  "One or both of the selected files are read-only. You can make changes, but you'll need to save them as new files or remove the read-only attribute.")
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
							key = key.split(':')[0].strip() if file_type == "GameSpecific" else key.split('@')[0].strip()
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
									"editable": not line.strip().startswith("// DO NOT MODIFY"),
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
			for i, setting in enumerate(data["settings"]):
				label = QLabel(f"{setting['name']}:")
				scroll_layout.addWidget(label, i, 0)
				value = setting['value'].strip('"')
				widget = self.create_widget(setting, value)
				scroll_layout.addWidget(widget, i, 1)
				widget.setEnabled(setting['editable'] and not setting['name'].startswith("// DO NOT MODIFY") and setting['name'] not in self.non_editable_fields)
				self.widgets[f"{section}_{setting['name']}"] = widget
				tooltip_text = self.help_texts.get(setting['name'], "No help text available for this setting.")
				tooltip_text += f"\n\nValid range: {setting['comment']}" if setting['comment'] else ""
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
			widget = self.create_slider_widget(setting, value)
			widget.valueChanged.connect(self.set_unsaved_changes)
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
					widget = NoScrollSlider(Qt.Horizontal)
					if is_whole_number:
						widget.setRange(int(min_val), int(max_val))
						widget.setValue(int(float(value)))
					else:
						widget.setRange(int(min_val * 1000), int(max_val * 1000))
						widget.setValue(int(float(value) * 1000))
						widget.setTickPosition(QSlider.TicksBelow)
						widget.setTickInterval((int(max_val * 1000) - int(min_val * 1000)) // 10 if not is_whole_number else max(1, int((max_val - min_val) / 10)))
						value_label = QLabel(value)
						widget.valueChanged.connect(lambda v, label=value_label, min_v=min_val, max_v=max_val, whole=is_whole_number:
													self.update_slider_value(v, label, min_v, max_v, whole))
					return widget
				except ValueError:
					pass
		return QLineEdit(value)

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
					widget.setEnabled(setting["editable"])

	def set_unsaved_changes(self):
		self.unsaved_changes = True

	def save_options(self):
		self.log("Starting save_options method")
		if not self.file_path or not self.game_agnostic_file_path:
			self.show_error_message("Error", "One or both files are not loaded")
			return
		try:
			self.save_file_with_permissions(self.file_path, "GameSpecific")
			self.save_file_with_permissions(self.game_agnostic_file_path, "GameAgnostic")
			self.update_file_permissions()
			self.log(f"Options saved to {self.file_path} and {self.game_agnostic_file_path}")
			QMessageBox.information(self, "Success", "Options saved successfully")
			self.unsaved_changes = False
			self.reload_file()
		except Exception as e:
			error_msg = f"Failed to save options: {str(e)}\n"
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
					key = line.split('=', 1)[0].strip().split(':')[0] if file_type == "GameSpecific" else line.split('=', 1)[0].strip().split('@')[0]
					for section, data in self.options.items():
						for setting in data["settings"]:
							if key == setting["name"] and setting["editable"] and setting["file_type"] == file_type:
								widget_key = f"{section}_{setting['name']}"
								if widget_key in self.widgets:
									widget = self.widgets[widget_key]
									value = self.get_widget_value(widget)
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

	def get_widget_value(self, widget):
		if isinstance(widget, QCheckBox):
			return str(widget.isChecked()).lower()
		elif isinstance(widget, QSlider):
			return str(widget.value() / 1000) if widget.maximum() > 1000 else str(widget.value())
		elif isinstance(widget, QComboBox):
			return widget.currentText()
		elif isinstance(widget, QLineEdit):
			return widget.text()
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
			return f"{line.split('=')[0]}= \"{value}\"{' // ' + setting['comment'] if setting['comment'] else ''}\n"
		else:  # GameAgnostic
			return f"{line.split('=')[0]}= {value}{' // ' + setting['comment'] if setting['comment'] else ''}\n"

	def reload_file(self):
		if self.file_path and self.game_agnostic_file_path:
			self.parse_options_file()
			self.display_options()
			self.unsaved_changes = False
			self.log("Files reloaded")

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
