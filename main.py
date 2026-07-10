import html
import json
import os
import re
import stat
import sys
from qt_material import apply_stylesheet
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
							 QPushButton, QLabel, QFileDialog, QMessageBox, QTabWidget,
							 QScrollArea, QCheckBox, QComboBox, QLineEdit,
							 QGridLayout, QDialog, QTextEdit, QAction, QDockWidget,
							 QHBoxLayout, QMenu, QActionGroup, QListWidget, QListWidgetItem)
from help_texts import get_help_texts
from setting_row import SettingRow, SettingSpec, CHANGED_COLOR


class GameSelector(QDialog):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowTitle("Select Game")
		self.setFixedSize(320, 260)

		if parent and hasattr(parent, 'app'):
			self.app = parent.app
		else:
			self.app = QApplication.instance()

		settings = QSettings("Lif3Snatcher's", "CODOptionsEditor")
		theme = settings.value("theme", "dark_blue", type=str)
		try:
			apply_stylesheet(self.app, theme=theme)
		except Exception as e:
			print(f"Error applying theme to GameSelector: {str(e)}")


		layout = QVBoxLayout()
		label = QLabel("Choose the game you want to modify settings for:")
		layout.addWidget(label)

		self.mw2_button = QPushButton("MW2 2022")
		self.mw2_button.clicked.connect(lambda: self.select_game("MW2 2022"))
		layout.addWidget(self.mw2_button)

		self.mw3_button = QPushButton("MW3 2023")
		self.mw3_button.clicked.connect(lambda: self.select_game("MW3 2023"))
		layout.addWidget(self.mw3_button)

		self.bo6_button = QPushButton("BO6 2024/Warzone 2024")
		self.bo6_button.clicked.connect(lambda: self.select_game("BO6 2024"))
		layout.addWidget(self.bo6_button)

		self.bo7_button = QPushButton("BO7 2025/Warzone 2025")
		self.bo7_button.clicked.connect(lambda: self.select_game("BO7 2025"))
		layout.addWidget(self.bo7_button)

		self.selected_game = None
		self.setLayout(layout)

		self.setup_window_flags()

	def show_first_time_warning(self):
		warning_text = (
				"<h3 style='color: #FF4444; text-align: center;'>WARNING: Advanced Application</h3>"
				"<p style='text-align: center;'>This is an advanced application for editing Call of Duty game settings.</p>"
				"<p style='text-align: center;'>Caution should be taken when making changes, as incorrect modifications "
				"may affect your game performance or stability.</p>"
				"<p style='text-align: center;'>It is recommended to backup your settings files before making any changes.</p>"
				"<p style='text-align: center;'><b>Use this application at your own risk.</b></p>"
		)

		warning_dialog = QMessageBox(self)
		warning_dialog.setWindowTitle("First-Time User Warning")
		warning_dialog.setText(warning_text)
		warning_dialog.setTextFormat(Qt.RichText)
		warning_dialog.setIcon(QMessageBox.Warning)
		warning_dialog.setStandardButtons(QMessageBox.Ok)
		warning_dialog.exec_()

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


class ImportPreviewDialog(QDialog):
	def __init__(self, rows, source_game, target_game, missing_count, parent=None):
		super().__init__(parent)
		self.setWindowTitle('Import Preview')
		self.resize(760, 540)
		self.rows = rows
		self.checks = []
		layout = QVBoxLayout(self)
		header = QLabel(f'Transfer from {source_game}  ->  {target_game}     ({len(rows)} matched, {missing_count} not in target)')
		layout.addWidget(header)
		top = QHBoxLayout()
		select_all = QPushButton('Select all changeable')
		select_none = QPushButton('Deselect all')
		select_all.clicked.connect(lambda: self.set_all(True))
		select_none.clicked.connect(lambda: self.set_all(False))
		top.addWidget(select_all)
		top.addWidget(select_none)
		top.addStretch()
		layout.addLayout(top)
		scroll = QScrollArea()
		scroll.setWidgetResizable(True)
		content = QWidget()
		grid = QGridLayout(content)
		for col, title in enumerate(('Apply', 'Setting', 'Current', 'New', 'Status')):
			grid.addWidget(QLabel(f'<b>{title}</b>'), 0, col)
		for i, row in enumerate(rows, start=1):
			name, current, new, status, reason, wd = row
			cb = QCheckBox()
			if status == 'changed':
				cb.setChecked(True)
			else:
				cb.setChecked(False)
				cb.setEnabled(False)
			self.checks.append(cb)
			grid.addWidget(cb, i, 0)
			grid.addWidget(QLabel(str(name)), i, 1)
			grid.addWidget(QLabel(str(current)), i, 2)
			grid.addWidget(QLabel(str(new)), i, 3)
			status_label = QLabel('invalid: ' + reason if status == 'invalid' else status)
			if status == 'invalid':
				status_label.setStyleSheet('color: #d9534f;')
			elif status == 'unchanged':
				status_label.setStyleSheet('color: gray;')
			elif status == 'changed':
				status_label.setStyleSheet('color: #5cb85c;')
			grid.addWidget(status_label, i, 4)
		content.setLayout(grid)
		scroll.setWidget(content)
		layout.addWidget(scroll)
		buttons = QHBoxLayout()
		apply_btn = QPushButton('Apply Selected')
		cancel_btn = QPushButton('Cancel')
		apply_btn.clicked.connect(self.accept)
		cancel_btn.clicked.connect(self.reject)
		buttons.addStretch()
		buttons.addWidget(apply_btn)
		buttons.addWidget(cancel_btn)
		layout.addLayout(buttons)

	def set_all(self, state):
		for cb, row in zip(self.checks, self.rows):
			if row[3] == 'changed':
				cb.setChecked(state)

	def selected_indices(self):
		return [i for i, cb in enumerate(self.checks) if cb.isChecked() and self.rows[i][3] == 'changed']


class PresetMetaDialog(QDialog):
	'Collects title/author/description when exporting or saving a shareable preset.'
	def __init__(self, default_title, default_author='', parent=None):
		super().__init__(parent)
		self.setWindowTitle('Preset Details')
		self.resize(460, 320)
		layout = QVBoxLayout(self)
		layout.addWidget(QLabel('Name this preset so others know what it is. Author and description are optional.'))
		form = QGridLayout()
		form.addWidget(QLabel('Title:'), 0, 0)
		self.title_edit = QLineEdit(default_title)
		self.title_edit.setMaxLength(80)
		form.addWidget(self.title_edit, 0, 1)
		form.addWidget(QLabel('Author:'), 1, 0)
		self.author_edit = QLineEdit(default_author)
		form.addWidget(self.author_edit, 1, 1)
		form.addWidget(QLabel('Description:'), 2, 0)
		self.desc_edit = QTextEdit()
		self.desc_edit.setPlaceholderText('e.g. Competitive low-latency, high-visibility, controller aim tuning...')
		form.addWidget(self.desc_edit, 2, 1)
		layout.addLayout(form)
		btns = QHBoxLayout()
		ok = QPushButton('OK')
		cancel = QPushButton('Cancel')
		ok.clicked.connect(self.accept)
		cancel.clicked.connect(self.reject)
		btns.addStretch()
		btns.addWidget(ok)
		btns.addWidget(cancel)
		layout.addLayout(btns)
	def values(self):
		return {'title': self.title_edit.text().strip(), 'author': self.author_edit.text().strip(), 'description': self.desc_edit.toPlainText().strip()}


class OptionsEditor(QMainWindow):
	def __init__(self):
		super().__init__()
		self.app = QApplication.instance()
		self.setWindowTitle("Call of Duty Options Editor")
		self.setGeometry(100, 100, 1000, 600)
		self.show_log_action = QAction("Show Log", self, checkable=True)
		self.read_only_action = QAction("Save as Read-only", self, checkable=True)
		self.tab_widget = QTabWidget()

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

		self.file_mapping = {
				"MW2 2022": {
						"game_specific":    "options.3.cod22.cst",
						"profile_specific": "settings.3.local.cod22.cst"
				},
				"MW3 2023": {
						"game_specific":    "options.4.cod23.cst",
						"profile_specific": "gamerprofile.0.BASE.cst"
				},
				"BO6 2024": {
						"game_specific":    "s.1.0.cod24.txt",
						"profile_specific": "g.1.0.l.txt"
				},
				"BO7 2025": {
						"game_specific":    "s.1.0.cod25.txt",
						"profile_specific": "g.p.cod25.1.0.l.txt"
				}
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

		self.show_welcome()

	def setup_theme(self):
		settings = QSettings("Lif3Snatcher's", "CODOptionsEditor")
		theme = settings.value("theme", "dark_blue.xml", type=str)
		self.apply_theme(theme)

	def apply_theme(self, theme_name):
		try:
			apply_stylesheet(self.app, theme=theme_name)
			for r in list(self.widgets.values()):
				if hasattr(r, 'refresh_theme'):
					r.refresh_theme()
			settings = QSettings("Lif3Snatcher's", "CODOptionsEditor")
			settings.setValue("theme", theme_name)

			status_bar = self.statusBar()
			status_bar.showMessage(f"Theme: {theme_name.replace('_', ' ').title()}")
		except Exception as e:
			self.log(f"Error applying theme: {str(e)}")

	def create_theme_menu(self):
		theme_menu = QMenu("Theme", self)
		themes = [
			"dark_blue.xml",
			"dark_cyan.xml",
			"dark_lightgreen.xml",
			"dark_pink.xml",
			"dark_purple.xml",
			"dark_red.xml",
			"dark_teal.xml",
			"dark_yellow.xml",
			"light_blue.xml",
			"light_amber.xml",
			"light_cyan.xml",
			"light_cyan_500.xml",
			"light_lightgreen.xml",
			"light_pink.xml",
			"light_purple.xml",
			"light_red.xml",
			"light_teal.xml",
			"light_yellow.xml"
		]

		theme_group = QActionGroup(self)
		theme_group.setExclusive(True)

		settings = QSettings("Lif3Snatcher's", "CODOptionsEditor")
		current_theme = settings.value("theme", "dark_blue.xml", type=str)

		for theme in themes:
			display_name = theme.replace(".xml", "").replace("_", " ").title()
			action = QAction(display_name, self, checkable=True)
			action.setChecked(theme == current_theme)
			action.triggered.connect(lambda checked, t=theme: self.apply_theme(t))
			theme_group.addAction(action)
			theme_menu.addAction(action)

		return theme_menu

	def setup_message_box(self, msg_box):
		msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowStaysOnTopHint)
		return msg_box

	def show_welcome(self):
		'Idle landing state so the app opens without forcing game/file selection.'
		settings = QSettings("Lif3Snatcher's", 'CODOptionsEditor')
		if not settings.value('app_launched', False, type=bool):
			self.show_first_time_warning()
			settings.setValue('app_launched', True)
		self.tab_widget.clear()
		placeholder = QWidget()
		lay = QVBoxLayout(placeholder)
		lbl = QLabel('<h2>Call of Duty Options Editor</h2>'
					 '<p>Use <b>File &gt; Change Game</b> to load and edit your settings.</p>')
		lbl.setAlignment(Qt.AlignCenter)
		lay.addWidget(lbl)
		self.tab_widget.addTab(placeholder, 'Welcome')
		self.statusBar().showMessage('No game loaded - use File > Change Game to begin')

	def is_txt_game(self):
		"""BO6/BO7 store settings as plaintext .txt (double-buffered); earlier titles use .cst."""
		return self.game in ("BO6 2024", "BO7 2025")

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
		file_menu.addSeparator()
		file_menu.addAction(QAction("Export Settings...", self, triggered=self.export_settings))
		file_menu.addAction(QAction("Import Settings...", self, triggered=self.import_settings))
		file_menu.addAction(QAction("Settings Library...", self, triggered=self.show_settings_library))
		file_menu.addAction(QAction("Reload", self, triggered=self.reload_file))
		file_menu.addAction(QAction("Change Game", self, triggered=self.change_game))
		file_menu.addSeparator()
		file_menu.addAction(QAction("Exit", self, triggered=self.close))

		view_menu = menu_bar.addMenu("View")
		self.show_log_action.triggered.connect(self.toggle_log_window)
		view_menu.addAction(self.show_log_action)

		options_menu = menu_bar.addMenu("Options")
		options_menu.addAction(self.read_only_action)
		options_menu.addAction(QAction("Revert All Changes", self, triggered=self.revert_all_changes))
		options_menu.addMenu(self.create_theme_menu())
		clear_settings_action = QAction("Clear All Settings", self)
		clear_settings_action.triggered.connect(self.clear_all_settings)
		options_menu.addAction(clear_settings_action)

		advanced_menu = menu_bar.addMenu("Advanced")
		advanced_menu.addAction(QAction("Controller Settings...", self, triggered=self.show_binary_settings))
		advanced_menu.addAction(QAction("Advanced Console Settings...", self, triggered=self.show_cfg_dvars))

		help_menu = menu_bar.addMenu("Help")
		help_menu.addAction(QAction("About", self, triggered=self.show_about_dialog))
		help_menu.addAction(QAction("Show Warning", self, triggered=self.show_first_time_warning))
		corner = QWidget()
		clay = QHBoxLayout(corner)
		clay.setContentsMargins(0, 0, 8, 0)
		clay.setSpacing(10)
		self.read_only_toggle = QCheckBox("Save as read-only")
		self.read_only_toggle.setToolTip("Save the config files read-only so the game can't overwrite your changes.")
		self.read_only_toggle.toggled.connect(self.read_only_action.setChecked)
		self.read_only_action.toggled.connect(self.read_only_toggle.setChecked)
		clay.addWidget(self.read_only_toggle)
		revert_chip = QPushButton("Revert all")
		revert_chip.setToolTip("Revert every value to what's currently on disk")
		revert_chip.clicked.connect(self.revert_all_changes)
		clay.addWidget(revert_chip)
		menu_bar.setCornerWidget(corner, Qt.TopRightCorner)
	def show_first_time_warning(self):
		warning_text = (
				"<h3 style='color: #FF4444; text-align: center;'>WARNING: Advanced Application</h3>"
				"<p style='text-align: center;'>This is an advanced application for editing Call of Duty game settings.</p>"
				"<p style='text-align: center;'>Caution should be taken when making changes, as incorrect modifications "
				"may affect your game performance or stability.</p>"
				"<p style='text-align: center;'>It is recommended to backup your settings files before making any changes.</p>"
				"<p style='text-align: center;'><b>Use this application at your own risk.</b></p>"
		)

		warning_dialog = QMessageBox(self)
		warning_dialog.setWindowTitle("First-Time User Warning")
		warning_dialog.setText(warning_text)
		warning_dialog.setTextFormat(Qt.RichText)
		warning_dialog.setIcon(QMessageBox.Warning)
		warning_dialog.setStandardButtons(QMessageBox.Ok)
		warning_dialog.exec_()

	def show_binary_settings(self):
		'View/edit the binary controller/advanced settings for the CURRENTLY LOADED game only.'
		if not self.game:
			self.show_error_message('Controller Settings', 'Select a game first (File > Change Game).')
			return
		try:
			import csb_binary
		except Exception as e:
			self.show_error_message('Controller Settings', 'Could not open the controller settings reader: ' + str(e))
			return
		engine = csb_binary.engine_for(self.game)
		if engine is None:
			self.show_error_message('Controller Settings', 'No controller settings available for ' + self.game + '.')
			return
		path, _ = csb_binary.find_binary_settings(self.game)
		if not path:
			path, _ = QFileDialog.getOpenFileName(self, 'Select ' + csb_binary.expected_file_hint(self.game) + ' for ' + self.game, '', 'All Files (*)')
		if not path:
			return
		try:
			info = csb_binary.decode_binary(path, engine)
		except Exception as e:
			self.show_error_message('Controller Settings', 'Could not read the settings file: ' + str(e))
			return
		rows = info['rows']
		# Only surface settings we can name and explain; hide anonymous values.
		rows = [r for r in rows if not str(r['name']).startswith('Profile value')]
		editable = info['editable']

		dlg = QDialog(self)
		dlg.setWindowTitle('Controller / Advanced Settings -- ' + self.game)
		dlg.resize(660, 560)
		lay = QVBoxLayout(dlg)
		if engine == 'iw':
			intro = '<p><b>' + self.game + '</b> controller settings: deadzones, stick sensitivity, aim response, and movement and interaction behaviors. Hover a setting to see what it does. Edited settings turn <b>amber</b> &mdash; use the revert arrow to undo one.</p>'
		else:
			intro = '<p><b>' + self.game + '</b> controller settings: deadzones, stick sensitivity, ADS multipliers, Tac-Stance, and button and stick layout. Hover a setting to see what it does. Change these in the game&#39;s Controller settings.</p>'
		header = QLabel(intro)
		header.setWordWrap(True)
		lay.addWidget(header)
		scroll = QScrollArea()
		scroll.setWidgetResizable(True)
		content = QWidget()
		vbox = QVBoxLayout(content)
		vbox.setContentsMargins(0, 0, 0, 0)
		vbox.setSpacing(0)
		editors = {}
		for r in rows:
			if editable and r.get('kind') == 'float':
				lo, hi, dec, step = csb_binary.float_range(r['name'])
				spec = SettingSpec(name=r['name'], value=str(r['value']), comment=str(lo) + ' to ' + str(hi), editable=True, help_text=self.help_texts.get(r['name'], ''))
				row = SettingRow(spec, non_editable_fields=[])
				editors[r['hash']] = row
			else:
				spec = SettingSpec(name=r['name'], value=str(r['value']), comment='', editable=False, help_text=self.help_texts.get(r['name'], ''))
				row = SettingRow(spec, non_editable_fields=[])
			vbox.addWidget(row)
		vbox.addStretch(1)
		scroll.setWidget(content)
		lay.addWidget(scroll)

		if editable:
			note = QLabel('<i>Editable settings save straight to the game (a backup is made automatically first). Settings shown for reference can&#39;t be changed here. Close the game before saving.</i>')
		else:
			note = QLabel('<i>These settings are shown for reference &mdash; change them in the game&#39;s Controller settings.</i>')
		note.setWordWrap(True)
		lay.addWidget(note)

		def name_of(h):
			for r in rows:
				if r.get('hash') == h:
					return r['name']
			return '%#010x' % h

		def do_save():
			changes = {}
			for h, row in editors.items():
				if row.is_changed():
					try:
						changes[h] = float(row.value())
					except ValueError:
						continue
			if not changes:
				QMessageBox.information(dlg, 'No changes', 'No settings were changed.')
				return
			summary = '\n'.join('  - ' + name_of(h) + ' -> ' + str(v) for h, v in changes.items())
			resp = QMessageBox.question(dlg, 'Write to game file?', 'This edits the saved settings for ' + self.game + '. Make sure the game is CLOSED.\n\nA backup is made automatically first.\n\nChanges:\n' + summary + '\n\nProceed?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
			if resp != QMessageBox.Yes:
				return
			try:
				bpath = csb_binary.backup(path)
				applied = csb_binary.write_floats(path, changes)
			except Exception as e:
				self.show_error_message('Controller Settings', 'Write failed: ' + str(e))
				return
			self.log('Binary settings [' + self.game + ']: wrote %d change(s), backup at %s' % (len(applied), os.path.basename(bpath)))
			for h, old, new in applied:
				self.log('  ' + name_of(h) + ': ' + str(old) + ' -> ' + str(new))
				if h in editors:
					editors[h].reset_baseline()
			for r in rows:
				if r.get('hash') in changes:
					r['value'] = changes[r['hash']]
			QMessageBox.information(dlg, 'Saved', 'Wrote %d change(s).\nBackup:\n%s' % (len(applied), bpath))

		def do_restore():
			backups = csb_binary.list_backups(path)
			start = backups[0] if backups else os.path.dirname(path)
			bpath, _ = QFileDialog.getOpenFileName(dlg, 'Choose a backup to restore', start, 'Backups (*.bak);;All Files (*)')
			if not bpath:
				return
			if QMessageBox.question(dlg, 'Restore backup?', 'Overwrite the live save with:\n' + bpath + ' ?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes:
				return
			try:
				csb_binary.restore(path, bpath)
			except Exception as e:
				self.show_error_message('Controller Settings', 'Restore failed: ' + str(e))
				return
			self.log('Binary settings [' + self.game + ']: restored from %s' % os.path.basename(bpath))
			try:
				new_info = csb_binary.decode_binary(path, engine)
				vals = {rr.get('hash'): rr['value'] for rr in new_info['rows']}
				for h, row in editors.items():
					if h in vals:
						row.set_value(str(vals[h]))
						row.reset_baseline()
			except Exception:
				pass
			QMessageBox.information(dlg, 'Restored', 'Restored from backup.')

		btn_row = QHBoxLayout()
		if editable:
			save_btn = QPushButton('Save Changes to Game File')
			save_btn.clicked.connect(do_save)
			restore_btn = QPushButton('Restore from Backup...')
			restore_btn.clicked.connect(do_restore)
			btn_row.addWidget(save_btn)
			btn_row.addWidget(restore_btn)
		btn_row.addStretch(1)
		close_btn = QPushButton('Close')
		close_btn.clicked.connect(dlg.accept)
		btn_row.addWidget(close_btn)
		lay.addLayout(btn_row)

		self.log('Viewed binary settings [' + self.game + ']: %d row(s) (editable=%s)' % (len(rows), editable))
		dlg.exec_()

	def show_cfg_dvars(self):
		"View advanced console settings stored in the game's config files."
		if not self.game:
			self.show_error_message('Advanced Console Settings', 'Select a game first (File > Change Game).')
			return
		try:
			import cfg_decoder
		except Exception as e:
			self.show_error_message('Advanced Console Settings', 'Could not open the reader: ' + str(e))
			return
		paths = cfg_decoder.find_cfgs(self.game)
		if not paths:
			if self.game in ('BO6 2024', 'BO7 2025'):
				QMessageBox.information(self, 'Advanced Console Settings', self.game + ' does not use these config files, so there is nothing to show here.')
				return
			p, _ = QFileDialog.getOpenFileName(self, 'Select a config .cfg file for ' + self.game, '', 'Config (*.cfg);;All Files (*)')
			if not p:
				return
			paths = [p]
		best = None
		for p in paths:
			try:
				rows, st = cfg_decoder.decode_cfg(p)
			except Exception:
				continue
			if best is None or st['named'] > best[2]['named']:
				best = (p, rows, st)
		if not best:
			self.show_error_message('Advanced Console Settings', 'No config file found.')
			return
		p, rows, st = best
		rows = [r for r in rows if r['named']]
		dlg = QDialog(self)
		dlg.setWindowTitle('Advanced Console Settings -- ' + self.game)
		dlg.resize(640, 560)
		lay = QVBoxLayout(dlg)
		lay.addWidget(QLabel('<p>Advanced console settings for <b>' + self.game + '</b>. These are separate from the settings tabs.</p>'))
		scroll = QScrollArea()
		scroll.setWidgetResizable(True)
		content = QWidget()
		grid = QGridLayout(content)
		grid.addWidget(QLabel('<b>Setting</b>'), 0, 0)
		grid.addWidget(QLabel('<b>Value</b>'), 0, 1)
		for i, r in enumerate(rows, 1):
			lbl = QLabel(r['key'])
			if not r['named']:
				lbl.setStyleSheet('color: gray;')
			grid.addWidget(lbl, i, 0)
			grid.addWidget(QLabel(str(r['value'])), i, 1)
		content.setLayout(grid)
		scroll.setWidget(content)
		lay.addWidget(scroll)
		lay.addWidget(QLabel('<i>Read-only here &mdash; change these in-game.</i>'))
		btn = QPushButton('Close')
		btn.clicked.connect(dlg.accept)
		lay.addWidget(btn)
		self.log('Viewed config dvars: %d/%d named from %s' % (st['named'], st['total'], os.path.basename(p)))
		dlg.exec_()

	def show_about_dialog(self):
		about_text = """
		<div style='text-align: center;'>
			<h2>Call of Duty Options Editor</h2>
			<p><b>Version: 1.5</b></p>
			<p style='color: #FF4444;'><b>This application is FREE and costs $0.<br>
			If you paid for this app, you got scammed.</b></p>
			<p>This application is designed to edit options for Call of Duty games:</p>
			<ul style='list-style-type: none;'>
				<li>- Modern Warfare 2 2022</li>
				<li>- Modern Warfare 3 2023</li>
				<li>- Black Ops 6/Warzone 2024</li>
				<li>- Black Ops 7/Warzone 2025</li>
			</ul>
			<p style='color: #666;'><i>DISCLAIMER: This application and its developer are not in any way,<br>
			shape, or form tied to or related with Activision, the publisher of Call of Duty games.</i></p>
			<p><b>Third-party software used:</b></p>
			<ul style='list-style-type: none;'>
				<li>- PyQt5 (GPL v3)</li>
				<li>- Python (PSF License)</li>
				<li>- Qt-Material (BSD-2-Clause License)</li>
			</ul>
		</div>
		"""
		about_dialog = QMessageBox(self)
		about_dialog.setWindowTitle("About")
		about_dialog.setText(about_text)
		about_dialog.setTextFormat(Qt.RichText)
		about_dialog.setIcon(QMessageBox.Information)

		settings = QSettings("Lif3Snatcher's", "CODOptionsEditor")
		theme = settings.value("theme", "dark_blue.xml", type=str)
		try:
			apply_stylesheet(self.app, theme=theme)
		except Exception as e:
			print(f"Error applying theme to GameSelector: {str(e)}")

		self.setup_message_box(about_dialog).exec_()

	def clear_all_settings(self):
		reply = QMessageBox.question(self, 'Clear Settings',
									"Are you sure you want to clear all settings? "
									"This will reset the application to its initial state.",
									QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

		if reply == QMessageBox.Yes:
			settings = QSettings("Lif3Snatcher's", "CODOptionsEditor")
			current_theme = settings.value("theme", "dark_blue", type=str)
			settings.clear()
			settings.setValue("theme", current_theme)
			settings.sync()

			QMessageBox.information(self, "Settings Cleared",
								  "All settings have been cleared. "
								  "The application will now close. "
								  "The next launch will be like a fresh install.")
			self.close()

	def create_widgets(self):
		central_widget = QWidget()
		self.setCentralWidget(central_widget)
		main_layout = QVBoxLayout()

		search_widget = QWidget()
		search_layout = QHBoxLayout(search_widget)
		search_layout.setContentsMargins(0, 0, 10, 0)

		self.search_bar = QLineEdit()
		self.search_bar.setPlaceholderText("Search settings...")
		self.search_bar.setClearButtonEnabled(True)
		self.search_bar.setFixedWidth(200)
		self.search_bar.textChanged.connect(self.filter_settings)

		self.category_filter = QComboBox()
		self.category_filter.addItem("All Categories")

		categories = set()
		for section_name in self.options.keys():
			categories.add(section_name)

		sorted_categories = sorted(list(categories))
		self.category_filter.addItems(sorted_categories)

		self.category_filter.setFixedWidth(150)
		self.category_filter.currentTextChanged.connect(self.filter_settings)

		search_layout.addWidget(QLabel("Search:"))
		search_layout.addWidget(self.search_bar)
		self.search_results_label = QLabel("")
		search_layout.addWidget(self.search_results_label)
		search_layout.addWidget(QLabel("Category:"))
		search_layout.addWidget(self.category_filter)

		self.tab_widget.setCornerWidget(search_widget, Qt.TopRightCorner)
		main_layout.addWidget(self.tab_widget)
		central_widget.setLayout(main_layout)

		self.populate_category_filter()

		self.setup_theme()
		self.show()
		self.activateWindow()

	def populate_category_filter(self):
		self.category_filter.clear()
		self.category_filter.addItem("All Categories")

		categories = set()
		for section_name in self.options.keys():
			if section_name:
				categories.add(section_name)

		sorted_categories = sorted(list(categories))
		self.category_filter.addItems(sorted_categories)

	def filter_settings(self):
		try:
			text = self.search_bar.text().lower()
			selected_category = self.category_filter.currentText()
			current_tab = self.tab_widget.currentIndex()
			total = 0
			first = None
			for ti in range(self.tab_widget.count()):
				tab = self.tab_widget.widget(ti)
				tab_name = self.tab_widget.tabText(ti)
				if selected_category != 'All Categories' and selected_category != tab_name:
					self.tab_widget.setTabEnabled(ti, False)
					continue
				tab_matches = 0
				for r in self._rows_in_tab(tab):
					m = r.matches(text) if text else False
					r.set_highlight(bool(text) and m)
					if text and m:
						tab_matches += 1
						total += 1
						if first is None:
							first = (ti, r)
				self.tab_widget.setTabEnabled(ti, (tab_matches > 0) or not text)
			if not text:
				self.search_results_label.setText('')
			elif total == 0:
				self.search_results_label.setText('No results')
			else:
				self.search_results_label.setText(str(total) + (' result' if total == 1 else ' results'))
			if text and 0 < total <= 3 and first:
				ti, r = first
				self.tab_widget.setCurrentIndex(ti)
				sa = self.tab_widget.widget(ti)
				if isinstance(sa, QScrollArea):
					sa.ensureWidgetVisible(r)
			elif text and total == 0:
				tab_name_cur = self.tab_widget.tabText(current_tab)
				if selected_category == 'All Categories' or selected_category == tab_name_cur:
					self.tab_widget.setTabEnabled(current_tab, True)
					self.tab_widget.setCurrentIndex(current_tab)
				else:
					for i in range(self.tab_widget.count()):
						if self.tab_widget.isTabEnabled(i):
							self.tab_widget.setCurrentIndex(i)
							break
			elif self.tab_widget.isTabEnabled(current_tab):
				self.tab_widget.setCurrentIndex(current_tab)
			else:
				for i in range(self.tab_widget.count()):
					if self.tab_widget.isTabEnabled(i):
						self.tab_widget.setCurrentIndex(i)
						break
		except Exception as e:
			self.log('Error in filter_settings: ' + str(e))

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

	def load_file(self, auto=False):
		if not self.game:
			self.log("No game selected, cannot load file")
			return
		try:
			self.log("Starting load_file method")
			default_path = os.path.expanduser("~\\Documents\\Call of Duty\\players")
			game_files = self.file_mapping.get(self.game)
			if not game_files:
				self.log(f"No file mapping found for {self.game}")
				return

			search_roots = self.get_search_roots()

			game_specific_path = self.find_config_file(game_files["game_specific"], search_roots)
			if not auto or not game_specific_path:
				game_specific_path = game_specific_path or self.get_file_path("game_specific",
														game_files["game_specific"],
														default_path)

			profile_path = self.find_config_file(game_files["profile_specific"], search_roots)
			if not auto or not profile_path:
				profile_path = profile_path or self.get_file_path("profile_specific",
														game_files["profile_specific"],
														default_path)

			if game_specific_path and profile_path:
				self.file_path = game_specific_path
				self.profile_path = profile_path
				self.game_agnostic_file_path = profile_path

				self.log(f"Loading files: {self.file_path} and {self.profile_path}")
				self.read_only = not os.access(self.file_path, os.W_OK) or \
								 not os.access(self.profile_path, os.W_OK)

				if self.read_only:
					self.show_read_only_message()
				self.parse_options_file()
				self.display_options()
				self.unsaved_changes = False
			else:
				self.log("File selection incomplete")
				self.show_error_message("File Selection",
										"Both files are required to proceed. Please select both files.")

		except Exception as e:
			self.log(f"Error in load_file: {str(e)}")
			self.show_error_message("File Loading Error",
									f"An error occurred while loading files: {str(e)}")

	def get_file_path(self, file_type, file_name, default_path):
		message = f"""
			<div style='text-align: center;'>
			<h3>Select {file_type} File</h3>
			<p>Please select the file:<br>
			<b>{file_name}</b></p>
			<p>This file is typically located in:<br>
			<i>{default_path}</i></p>
			</div>
			"""

		msg_box = QMessageBox(QMessageBox.Information, "Select File", message)
		msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
		msg_box.setDefaultButton(QMessageBox.Ok)
		msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowStaysOnTopHint)

		result = msg_box.exec_()
		if result == QMessageBox.Ok:
			if self.is_txt_game():
				file_filter = "Text Files (*.txt);;All Files (*)"
			else:
				file_filter = "CST Files (*.cst);;All Files (*)"

			file_path, _ = QFileDialog.getOpenFileName(
					self,
					f"Select {file_name}",
					default_path,
					file_filter
			)
			if file_path:
				return file_path
			self.log(f"No file selected for {file_type}")
			return None
		self.log(f"File selection cancelled for {file_type}")
		return None

	def find_player_folders(self, base_path):
		player_folders = []
		try:
			if os.path.exists(os.path.join(base_path, "players")):
				player_folders.append(os.path.join(base_path, "players"))

			steam_pattern = re.compile(r"765\d{11,13}")

			bnet_pattern = re.compile(r"253\d{11,13}")

			for item in os.listdir(base_path):
				if steam_pattern.match(item) or bnet_pattern.match(item):
					full_path = os.path.join(base_path, item)
					if os.path.isdir(full_path):
						player_folders.append(full_path)
			player_folders.sort(key=lambda x: os.path.getmtime(x), reverse=True)
			return player_folders
		except Exception as e:
			self.log(f"Error scanning for player folders: {str(e)}")
			return [os.path.join(base_path, "players")]

	def get_search_roots(self):
		"""Ordered dirs that may hold CoD config, across launchers/platforms:
		Steam, Battle.net, and Microsoft Store / Game Pass (%LOCALAPPDATA%\\Activision)."""
		home = os.path.expanduser("~")
		docs = os.path.join(home, "Documents")
		lad = os.environ.get("LOCALAPPDATA", os.path.join(home, "AppData", "Local"))
		bases = [
			os.path.join(docs, "Call of Duty"),
			os.path.join(docs, "Call of Duty MWII"),
			os.path.join(docs, "Call of Duty MWIII"),
			os.path.join(docs, "Call of Duty Modern Warfare"),
			os.path.join(lad, "Activision", "Call of Duty"),
			os.path.join(lad, "Activision", "Call of Duty MWII"),
			os.path.join(lad, "Activision", "Call of Duty MWIII"),
		]
		roots = []
		for base in bases:
			players = os.path.join(base, "players")
			if os.path.isdir(players):
				xuid_dirs = self.find_player_folders(players)
				if xuid_dirs:
					roots.extend(xuid_dirs)   # mtime-sorted accounts first (most-recent wins)
				roots.append(players)       # bare players/ as fallback
			elif os.path.isdir(base):
				roots.append(base)
		seen, ordered = set(), []
		for r in roots:
			if r not in seen:
				seen.add(r)
				ordered.append(r)
		self.log(f"Config search roots: {len(ordered)} location(s)")
		return ordered

	def find_config_file(self, filename, roots):
		"""Locate a config file across roots and their immediate sub-folders.
		Handles the .txt0/.txt1 double-buffer of BO6/BO7 (prefers the .txt0 buffer)."""
		if filename.endswith(".txt"):
			candidates = [filename + "0", filename + "1", filename]
		else:
			candidates = [filename]
		# Some launchers/platforms insert a ".pc" segment, and its position varies per title
		# (gamerprofile.pc.0.BASE.cst vs settings.3.local.pc.cod22.cst) -- try each dot boundary.
		variants = []
		for c in candidates:
			variants.append(c)
			parts = c.split(".")
			if "pc" not in parts:
				for i in range(1, len(parts) - 1):
					variants.append(".".join(parts[:i] + ["pc"] + parts[i:]))
		candidates = variants
		for root in roots:
			search_dirs = [root]
			try:
				search_dirs += [os.path.join(root, d) for d in os.listdir(root)
								if os.path.isdir(os.path.join(root, d))]
			except OSError:
				pass
			for directory in search_dirs:
				for name in candidates:
					path = os.path.join(directory, name)
					if os.path.exists(path):
						self.log(f"Found {filename} at {path}")
						return path
		return None

	def show_read_only_message(self):
		msg_box = QMessageBox(QMessageBox.Information, "Read-only File",
							  "One or both of the selected files are read-only. "
							  "You can make changes, but you'll need to save them as new files "
							  "or remove the read-only attribute.")
		msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowStaysOnTopHint)
		msg_box.exec_()

	def show_error_message(self, title, message):
		formatted_message = f"""
		<div style='text-align: center;'>
			<h3 style='color: #FF4444;'>Error Occurred</h3>
			<p>{message}</p>
		</div>
		"""
		msg_box = QMessageBox(self)
		msg_box.setWindowTitle(title)
		msg_box.setText(formatted_message)
		msg_box.setTextFormat(Qt.RichText)
		msg_box.setIcon(QMessageBox.Critical)
		self.setup_message_box(msg_box).exec_()

	def validate_file_format(self, file_path):
		if self.is_txt_game() and not file_path.lower().endswith('.txt'):
			return False
		elif not self.is_txt_game() and not file_path.lower().endswith('.cst'):
			return False
		return True

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
					if self.is_txt_game():
						sections = re.split(r'//\n// [A-Za-z][A-Za-z0-9 ]*\n', content)[1:]
						section_names = re.findall(r'//\n// ([A-Za-z][A-Za-z0-9 ]*)\n', content)
					else:
						sections = re.split(r'//\n// [A-Za-z][A-Za-z0-9 ]*\n//', content)[1:]
						section_names = re.findall(r'//\n// ([A-Za-z][A-Za-z0-9 ]*)\n//', content)
				else:  # GameAgnostic
					sections = [content]
					section_names = ["GameAgnostic"]

				for name, section in zip(section_names, sections):
					name = name.strip()
					if name not in self.options:
						self.options[name] = {"settings": []}
					lines = section.strip().split('\n')
					for line in lines:
						if '=' in line and not line.strip().startswith('//'):
							key, value = line.split('=', 1)
							if file_type == "GameSpecific":
								if self.is_txt_game():
									key = key.split('@')[0].strip()
								else:
									key = key.split(':')[0].strip()
							else:
								key = key.split('@')[0].split(':')[0].strip()
							value = value.strip()
							comment = ""
							if '//' in value:
								value, comment = value.split('//', 1)
								comment = comment.strip()
							value = value.strip().strip('"')
							self.options[name]["settings"].append({
								"name": key,
								"value": value,
								"comment": comment,
								"editable": not line.strip().startswith("// DO NOT MODIFY"),
								"file_type": file_type
							})
		except Exception as e:
			self.show_error_message("Error", f"Failed to parse options file {file_path}: {str(e)}")
			self.log(f"Error parsing options file {file_path}: {str(e)}")

	def display_options(self):
		self.tab_widget.clear()
		self.widgets.clear()
		for section, data in self.options.items():
			scroll_area = QScrollArea()
			scroll_area.setWidgetResizable(True)
			content = QWidget()
			vbox = QVBoxLayout(content)
			vbox.setContentsMargins(0, 0, 0, 0)
			vbox.setSpacing(0)
			for i, setting in enumerate(data["settings"]):
				wkey = f"{section}_{setting['name']}_{i}"
				setting['_wkey'] = wkey
				spec = SettingSpec(name=setting['name'], value=setting['value'], comment=setting['comment'], editable=setting['editable'], file_type=setting['file_type'], help_text=self.help_texts.get(setting['name'], ''), wkey=wkey)
				row = SettingRow(spec, non_editable_fields=self.non_editable_fields)
				row.valueChanged.connect(self.on_row_value_changed)
				self.widgets[wkey] = row
				vbox.addWidget(row)
			vbox.addStretch(1)
			scroll_area.setWidget(content)
			self.tab_widget.addTab(scroll_area, section)
		self.populate_category_filter()
		self.update_dirty_state()
	def on_row_value_changed(self, name, old, new):
		self.log(name + ': ' + str(old) + ' \u2192 ' + str(new))
		self.update_dirty_state()
	def update_dirty_state(self):
		changed = [r for r in self.widgets.values() if hasattr(r, 'is_changed') and r.is_changed()]
		n = len(changed)
		self.unsaved_changes = (n > 0)
		title = 'Call of Duty Options Editor'
		if self.game:
			title += ' - ' + self.game
		if n:
			title += '  \u2022'
		self.setWindowTitle(title)
		sb = self.statusBar()
		if n:
			sb.setStyleSheet('color: ' + CHANGED_COLOR + ';')
			sb.showMessage(str(n) + (' unsaved change' if n == 1 else ' unsaved changes'))
		else:
			sb.setStyleSheet('')
			sb.showMessage('No unsaved changes' if self.game else 'No game loaded - use File > Change Game to begin')
	def revert_all_changes(self):
		reverted = 0
		for r in list(self.widgets.values()):
			if hasattr(r, 'is_changed') and r.is_changed():
				r.revert()
				reverted += 1
		if reverted:
			self.log('Reverted ' + str(reverted) + ' change(s) to on-disk values')
		self.update_dirty_state()
	def _rows_in_tab(self, tab):
		if not isinstance(tab, QScrollArea):
			return []
		content = tab.widget()
		if not content or not content.layout():
			return []
		rows = []
		lay = content.layout()
		for i in range(lay.count()):
			item = lay.itemAt(i)
			w = item.widget() if item else None
			if isinstance(w, SettingRow):
				rows.append(w)
		return rows

	def save_options(self):
		self.log(f"Starting save_options method for {self.game}")
		if not self.file_path or not self.game_agnostic_file_path:
			self.show_error_message("Error", "One or both files are not loaded")
			return
		try:
			skipped = self.save_file_with_permissions(self.file_path, "GameSpecific") or []
			skipped += self.save_file_with_permissions(self.game_agnostic_file_path, "GameAgnostic") or []

			# Mirror double-buffered .txt files so the game cannot reload a stale buffer
			self.mirror_double_buffer(self.file_path)
			self.mirror_double_buffer(self.game_agnostic_file_path)

			# Set files as read-only if checkbox is checked
			if self.read_only_action.isChecked():
				os.chmod(self.file_path, 0o444)  # Read-only for user, group, and others
				os.chmod(self.game_agnostic_file_path, 0o444)
				self.show_read_only_message()

			self.log(f"Options saved to {self.file_path} and {self.game_agnostic_file_path}")
			self.unsaved_changes = False
			self.reload_file()
			if skipped:
				QMessageBox.warning(self, "Saved with skipped settings", f"Options for {self.game} were saved, but {len(skipped)} value(s) were out of range and were NOT written:\n- " + "\n- ".join(skipped[:25]))
			else:
				QMessageBox.information(self, "Success", f"Options for {self.game} saved successfully")
		except Exception as e:
			error_msg = f"Failed to save options for {self.game}: {str(e)}\n"
			error_msg += f"Error type: {type(e).__name__}\n"
			error_msg += f"Error args: {e.args}\n"
			self.show_error_message("Error", error_msg)
			self.log(error_msg)

	def export_settings(self):
		'Export current settings to a shareable .codsettings file (others can import it).'
		if not self.options:
			self.show_error_message('Export', 'Load a game first, then export.')
			return
		store = QSettings("Lif3Snatcher's", 'CODOptionsEditor')
		meta_dlg = PresetMetaDialog(f'{self.game} settings', store.value('preset_author', '', type=str), self)
		if not meta_dlg.exec_():
			return
		meta = meta_dlg.values()
		store.setValue('preset_author', meta['author'])
		records = self._collect_records()
		payload = self._build_payload(records, meta)
		safe = (re.sub(r'[^A-Za-z0-9_-]+', '_', meta['title'] or self.game).strip('_') or 'settings')[:80]
		path, _ = QFileDialog.getSaveFileName(self, 'Export / Share Settings', f'{safe}.codsettings', 'COD Settings (*.codsettings *.json);;All Files (*)')
		if not path:
			return
		try:
			with open(path, 'w', encoding='utf-8') as f:
				json.dump(payload, f, indent=2)
			self.log(f'Exported {len(records)} settings from {self.game} to {path}')
			QMessageBox.information(self, 'Export Complete', 'Saved ' + str(len(records)) + ' settings as "' + meta['title'] + '".\n\nShare this .codsettings file with others -- they can load it via File > Import Settings or add it to their Settings Library.')
		except Exception as e:
			self.show_error_message('Export Failed', str(e))

	def import_settings(self):
		"Apply a shared .codsettings file to the loaded game (matched by setting name)."
		if not self.options:
			self.show_error_message('Import', 'Load the target game first, then import.')
			return
		path, _ = QFileDialog.getOpenFileName(self, 'Import / Apply Settings', '', 'COD Settings (*.codsettings *.json);;All Files (*)')
		if not path:
			return
		payload = self._read_preset(path)
		if payload is None:
			return
		meta = payload.get('meta') or {}
		self._apply_records(payload.get('settings', []), meta.get('game', 'unknown'), meta.get('title') or os.path.basename(path))

	def _read_preset(self, path):
		'Load and lightly validate a .codsettings payload; None on failure.'
		try:
			with open(path, 'r', encoding='utf-8') as f:
				payload = json.load(f)
			if not isinstance(payload, dict) or not isinstance(payload.get('settings'), list):
				raise ValueError('not a valid .codsettings file')
			return payload
		except Exception as e:
			self.show_error_message('Preset', 'Could not read ' + os.path.basename(path) + ': ' + str(e))
			return None

	def _collect_records(self):
		'Snapshot the current (edited) widget values as portable records.'
		records = []
		for section, data in self.options.items():
			for setting in data['settings']:
				wd = self.widgets.get(setting.get('_wkey', ''))
				value = self.get_widget_value(wd) if wd else setting['value']
				records.append({'name': setting['name'], 'value': value, 'file_type': setting['file_type'], 'comment': setting['comment']})
		return records

	def _build_payload(self, records, meta):
		'Assemble a .codsettings payload with sharing metadata.'
		return {'meta': {'title': (meta.get('title') or (self.game + ' settings')), 'author': meta.get('author', ''), 'description': meta.get('description', ''), 'game': self.game, 'app': 'CODOptionsEditor', 'version': '1.5', 'count': len(records)}, 'settings': records}

	def _apply_records(self, records, source_game, source_label=''):
		'Match records to the loaded game by name, preview, and apply the selected ones.'
		if not self.options:
			self.show_error_message('Apply', 'Load the target game first.')
			return
		index = {}
		for section, data in self.options.items():
			for setting in data['settings']:
				index.setdefault(setting['name'], []).append((section, setting))
		rows, missing = [], []
		for rec in records:
			if not isinstance(rec, dict):
				continue
			name = rec.get('name', '')
			value = str(rec.get('value', ''))
			if name not in index:
				missing.append(name)
				continue
			matched = False
			for section, setting in index[name]:
				wd = self.widgets.get(setting.get('_wkey', ''))
				if not wd:
					continue
				matched = True
				current = self.get_widget_value(wd)
				if not setting['editable'] or name in self.non_editable_fields:
					rows.append([name, current, value, 'invalid', 'read-only in target', wd])
				elif not self.is_value_valid_for_target(setting, value):
					rows.append([name, current, value, 'invalid', 'out of range / not a valid option', wd])
				elif self.values_equal(current, value):
					rows.append([name, current, value, 'unchanged', '', wd])
				else:
					rows.append([name, current, value, 'changed', '', wd])
			if not matched:
				missing.append(name)
		if not rows:
			self.show_error_message('Apply', 'None of the ' + str(len(missing)) + ' settings exist in ' + self.game + '.')
			return
		label = source_label or source_game or 'preset'
		dialog = ImportPreviewDialog(rows, label, self.game, len(missing), self)
		if not dialog.exec_():
			self.log('Apply cancelled')
			return
		applied = []
		for i in dialog.selected_indices():
			name, current, value, status, reason, wd = rows[i]
			self.set_widget_value(wd, value)
			applied.append(name)
		if applied:
			self.update_dirty_state()
		self.log('Applied ' + str(len(applied)) + ' of ' + str(len(rows)) + ' matched (' + str(len(missing)) + ' not in ' + self.game + ') from ' + label)
		QMessageBox.information(self, 'Apply Complete', 'Applied ' + str(len(applied)) + ' setting(s) to ' + self.game + '.\n' + str(len(missing)) + ' setting(s) were not present in this game.\n\nUse File > Save Options to write them to the game.')

	def _preset_dirs(self):
		'Return (recommended_dir, user_dir); user_dir is created if missing.'
		if getattr(sys, 'frozen', False):
			app_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
		else:
			app_dir = os.path.dirname(os.path.abspath(__file__))
		recommended = os.path.join(app_dir, 'presets')
		lad = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
		user = os.path.join(lad, 'CODOptionsEditor', 'presets')
		try:
			os.makedirs(user, exist_ok=True)
		except OSError:
			pass
		return recommended, user

	def save_current_as_preset(self):
		'Save the current settings into the local Settings Library as a reusable preset.'
		if not self.options:
			self.show_error_message('Save Preset', 'Load a game first.')
			return None
		store = QSettings("Lif3Snatcher's", 'CODOptionsEditor')
		meta_dlg = PresetMetaDialog(f'{self.game} settings', store.value('preset_author', '', type=str), self)
		if not meta_dlg.exec_():
			return None
		meta = meta_dlg.values()
		store.setValue('preset_author', meta['author'])
		_, user_dir = self._preset_dirs()
		payload = self._build_payload(self._collect_records(), meta)
		safe = (re.sub(r'[^A-Za-z0-9_-]+', '_', (meta['title'] or self.game)).strip('_') or 'preset')[:80]
		path = os.path.join(user_dir, safe + '.codsettings')
		n = 1
		while os.path.exists(path):
			path = os.path.join(user_dir, safe + '_' + str(n) + '.codsettings')
			n += 1
		try:
			with open(path, 'w', encoding='utf-8') as f:
				json.dump(payload, f, indent=2)
			self.log('Saved preset "' + meta['title'] + '" to library (' + path + ')')
			return path
		except Exception as e:
			self.show_error_message('Save Preset', str(e))
			return None

	def _load_library(self):
		'Scan recommended + user preset folders; return a list of preset dicts.'
		recommended, user = self._preset_dirs()
		items = []
		for src, d in (('Recommended', recommended), ('My Presets', user)):
			if not os.path.isdir(d):
				continue
			for fn in sorted(os.listdir(d)):
				if not fn.lower().endswith(('.codsettings', '.json')):
					continue
				p = os.path.join(d, fn)
				try:
					with open(p, 'r', encoding='utf-8') as f:
						payload = json.load(f)
					meta = payload.get('meta') or {}
					items.append({'title': meta.get('title') or os.path.splitext(fn)[0], 'game': meta.get('game', 'unknown'), 'author': meta.get('author', ''), 'description': meta.get('description', ''), 'count': meta.get('count', len(payload.get('settings', []))), 'source': src, 'path': p, 'payload': payload})
				except Exception:
					continue
		return items

	def show_settings_library(self):
		'Browse recommended and personal presets; preview & apply, import, save, or delete.'
		dlg = QDialog(self)
		dlg.setWindowTitle('Settings Library')
		dlg.resize(720, 540)
		lay = QVBoxLayout(dlg)
		intro = QLabel('<p>Apply <b>recommended</b> presets or ones <b>shared with you</b>, save your own, and manage your collection. Applying only stages the changes -- review them in the preview, then <b>File &gt; Save Options</b> to write them to the game.</p>')
		intro.setWordWrap(True)
		lay.addWidget(intro)
		only_game = QCheckBox('Show only presets for the loaded game')
		only_game.setChecked(bool(self.game))
		lay.addWidget(only_game)
		listw = QListWidget()
		lay.addWidget(listw, 1)
		details = QLabel('Select a preset to see its details.')
		details.setWordWrap(True)
		details.setStyleSheet('color: gray;')
		lay.addWidget(details)

		def selected():
			it = listw.currentItem()
			return it.data(Qt.UserRole) if it else None

		def refresh():
			listw.clear()
			for it in self._load_library():
				if only_game.isChecked() and self.game and it['game'] != self.game:
					continue
				label = it['title'] + '  |  ' + str(it['game']) + '  |  ' + str(it['count']) + ' settings  |  ' + it['source']
				item = QListWidgetItem(label)
				item.setData(Qt.UserRole, it)
				listw.addItem(item)
			if listw.count() == 0:
				details.setStyleSheet('color: gray;')
				details.setText('No presets to show. Use "Save current as preset" or "Import file to library" to add some.')

		def on_select():
			d = selected()
			b_delete.setEnabled(bool(d and d['source'] == 'My Presets'))
			if not d:
				details.setStyleSheet('color: gray;')
				details.setText('Select a preset to see its details.')
				return
			parts = ['<b>' + html.escape(d['title']) + '</b> -- for <b>' + html.escape(str(d['game'])) + '</b>']
			if d['author']:
				parts.append(' by ' + html.escape(d['author']))
			if d['description']:
				parts.append('<br>' + html.escape(d['description']))
			parts.append('<br><i>' + d['source'] + ' - ' + str(d['count']) + ' settings - ' + html.escape(os.path.basename(d['path'])) + '</i>')
			details.setStyleSheet('')
			details.setText(''.join(parts))

		def do_apply():
			d = selected()
			if not d:
				return
			if not self.options:
				self.show_error_message('Apply', 'Load a game first (File > Change Game).')
				return
			meta = d['payload'].get('meta') or {}
			self._apply_records(d['payload'].get('settings', []), meta.get('game', d['game']), d['title'])

		def do_import():
			path, _ = QFileDialog.getOpenFileName(dlg, 'Add a preset file to your library', '', 'COD Settings (*.codsettings *.json);;All Files (*)')
			if not path:
				return
			payload = self._read_preset(path)
			if payload is None:
				return
			_, user_dir = self._preset_dirs()
			dst = os.path.join(user_dir, os.path.basename(path))
			base, ext = os.path.splitext(dst)
			n = 1
			while os.path.exists(dst):
				dst = base + '_' + str(n) + ext
				n += 1
			try:
				import shutil
				shutil.copy2(path, dst)
				self.log('Added preset to library: ' + dst)
				refresh()
			except Exception as e:
				self.show_error_message('Import', str(e))

		def do_save():
			if self.save_current_as_preset():
				refresh()

		def do_delete():
			d = selected()
			if not d:
				return
			if d['source'] != 'My Presets':
				self.show_error_message('Delete', 'Only presets in "My Presets" can be deleted.')
				return
			if QMessageBox.question(dlg, 'Delete preset', 'Delete "' + d['title'] + '" from your library?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes:
				return
			try:
				os.remove(d['path'])
				self.log('Deleted preset ' + d['path'])
				refresh()
			except Exception as e:
				self.show_error_message('Delete', str(e))

		def do_folder():
			_, user_dir = self._preset_dirs()
			try:
				os.startfile(user_dir)
			except Exception:
				QMessageBox.information(dlg, 'Preset folder', user_dir)

		listw.currentItemChanged.connect(lambda *_: on_select())
		listw.itemDoubleClicked.connect(lambda *_: do_apply())
		only_game.stateChanged.connect(lambda *_: refresh())

		btns = QHBoxLayout()
		b_apply = QPushButton('Preview && Apply')
		b_import = QPushButton('Import file to library...')
		b_save = QPushButton('Save current as preset...')
		b_delete = QPushButton('Delete')
		b_delete.setEnabled(False)
		b_folder = QPushButton('Open folder')
		b_close = QPushButton('Close')
		b_apply.clicked.connect(do_apply)
		b_import.clicked.connect(do_import)
		b_save.clicked.connect(do_save)
		b_delete.clicked.connect(do_delete)
		b_folder.clicked.connect(do_folder)
		b_close.clicked.connect(dlg.accept)
		for b in (b_apply, b_import, b_save, b_delete, b_folder):
			btns.addWidget(b)
		btns.addStretch()
		btns.addWidget(b_close)
		lay.addLayout(btns)
		refresh()
		dlg.exec_()

	def set_widget_value(self, widget_data, value):
		widget_data.set_value(str(value))

	def is_value_valid_for_target(self, setting, value):
		comment = setting.get('comment', '') or ''
		current = str(setting.get('value', '')).strip()
		value = str(value).strip()
		if current.lower() in ('true', 'false'):
			return value.lower() in ('true', 'false')
		if 'one of' in comment:
			opts = [o.strip() for o in comment.split('one of', 1)[1].strip().strip('[]').split(',')]
			return value in opts
		if 'to' in comment and re.search(r'-?\d', comment):
			return self.is_value_in_range(setting, value)
		return True

	def values_equal(self, a, b):
		a, b = str(a).strip(), str(b).strip()
		try:
			return abs(float(a) - float(b)) < 1e-9
		except ValueError:
			return a.lower() == b.lower()

	def save_file_with_permissions(self, file_path, file_type):
		original_permissions = os.stat(file_path).st_mode
		try:
			os.chmod(file_path, stat.S_IWRITE | stat.S_IREAD)
			return self.save_file(file_path, file_type)
		finally:
			os.chmod(file_path, original_permissions)

	def mirror_double_buffer(self, path):
		"""BO6/BO7 keep two copies (.txt0/.txt1); write the sibling so the game
		cannot reload a stale buffer after we edit one."""
		if not path:
			return
		m = re.search(r"\.txt([01])$", path)
		if not m:
			return
		sibling = path[:-1] + ("1" if m.group(1) == "0" else "0")
		try:
			if os.path.exists(sibling) and not os.access(sibling, os.W_OK):
				os.chmod(sibling, stat.S_IWRITE | stat.S_IREAD)
			with open(path, "rb") as src:
				data = src.read()
			with open(sibling, "wb") as dst:
				dst.write(data)
			if self.read_only_action.isChecked():
				os.chmod(sibling, 0o444)
			self.log(f"Mirrored double-buffer to {sibling}")
		except Exception as e:
			self.log(f"Could not mirror double-buffer {sibling}: {e}")

	def save_file(self, file_path, file_type):
		skipped = []
		try:
			with open(file_path, 'rb') as _f:
				_newline = '\r\n' if b'\r\n' in _f.read() else '\n'
			with open(file_path, 'r') as file:
				lines = file.readlines()
			used = set()
			for i, line in enumerate(lines):
				if '=' in line and not line.strip().startswith('//'):
					key = line.split('=', 1)[0].strip()
					if file_type == "GameSpecific":
						if self.is_txt_game():
							key = key.split('@')[0].strip()
						else:
							key = key.split(':')[0].strip()
					else:
						key = key.split('@')[0].split(':')[0].strip()
					matched = False
					for section, data in self.options.items():
						for setting in data["settings"]:
							sid = id(setting)
							if key == setting["name"] and setting["editable"] and setting["file_type"] == file_type and sid not in used:
								widget_key = setting.get('_wkey', '')
								if widget_key in self.widgets:
									widget_data = self.widgets[widget_key]
									value = self.get_widget_value(widget_data)
									if self.is_value_in_range(setting, value):
										lines[i] = self.format_line(file_type, line, setting, value)
									else:
										skipped.append(setting['name'])
										self.log(f"Value {value} for {setting['name']} is out of range. Skipping.")
								used.add(sid)
								matched = True
								break
						if matched:
							break
			with open(file_path, 'w', newline=_newline) as file:
				file.writelines(lines)
		except Exception as e:
			error_msg = f"Failed to save options to {file_path}: {str(e)}\n"
			error_msg += f"Error type: {type(e).__name__}\n"
			error_msg += f"Error args: {e.args}\n"
			raise Exception(error_msg)
		return skipped

	def get_widget_value(self, widget_data):
		return widget_data.value()

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
		# Preserve the original key and ALL its decoration (@instance;hashes, :version)
		# by keeping everything up to the first '='; only the value and its trailing
		# comment are replaced. Re-quote the value iff the original line quoted it.
		head, _sep, rest = line.partition('=')
		out_val = f'"{value}"' if rest.lstrip().startswith('"') else f'{value}'
		comment = f" // {setting['comment']}" if setting['comment'] else ''
		return f"{head.rstrip()} = {out_val}{comment}\n"

	def reload_file(self):
		if self.file_path and self.game_agnostic_file_path:
			self.parse_options_file()
			self.display_options()
			self.unsaved_changes = False
			self.log(f"Files reloaded for {self.game}")

	def check_unsaved_changes(self):
		if self.unsaved_changes:
			msg_box = QMessageBox.question(
					self,
					'Unsaved Changes',
					"""
					<div style='text-align: center;'>
						<h3>Unsaved Changes</h3>
						<p>You have unsaved changes.<br>
						Would you like to save them?</p>
					</div>
					""",
					QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
					QMessageBox.Save
			)
			reply = msg_box
			if reply == QMessageBox.Save:
				self.save_options()
				return True
			elif reply == QMessageBox.Cancel:
				return False
		return True

	def closeEvent(self, event):
		if self.check_unsaved_changes():
			QSettings("Lif3Snatcher's", "CODOptionsEditor").sync()
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
		QMessageBox.critical(
			None,
			"Critical Error",
			f"""
			<div style='text-align: center;'>
				<h3 style='color: #FF4444;'>Critical Error</h3>
				<p>An unhandled error occurred:</p>
				<p><b>{str(e)}</b></p>
			</div>
			""",
			QMessageBox.Ok
		)
		sys.exit(1)

if __name__ == "__main__":
	main()
