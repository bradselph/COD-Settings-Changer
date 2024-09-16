from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QPushButton, QLabel, QFileDialog, QMessageBox, QTabWidget,
                             QScrollArea, QCheckBox, QSlider, QComboBox, QLineEdit,
                             QGridLayout, QDialog, QTextEdit, QAction, QDockWidget, QToolTip)
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

class NoScrollSlider(QSlider):
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

        self.log_window = LogWindow(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.log_window)
        self.log_window.hide()

        self.create_menu()
        self.create_widgets()
        self.create_help_texts()

        # Set tooltip style
        self.setStyleSheet("""
            QToolTip {
                background-color: #2a82da;
                color: white;
                border: 1px solid white;
                padding: 5px;
            }
        """)

        self.select_game()

    def create_menu(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        file_menu.addAction(QAction("Load Options", self, triggered=self.load_file))
        file_menu.addAction(QAction("Save Options", self, triggered=self.save_options))
        file_menu.addAction(QAction("Reload", self, triggered=self.load_file))
        file_menu.addSeparator()
        file_menu.addAction(QAction("Exit", self, triggered=self.close))

        view_menu = menu_bar.addMenu("View")
        self.show_log_action = QAction("Show Log", self, checkable=True)
        self.show_log_action.triggered.connect(self.toggle_log_window)
        view_menu.addAction(self.show_log_action)

        options_menu = menu_bar.addMenu("Options")
        self.read_only_action = QAction("Save as Read-only", self, checkable=True)
        options_menu.addAction(self.read_only_action)

    def create_help_texts(self):
        self.help_texts = {
            
            "VideoMemoryScale":                "Adjusts the fraction of your GPU's memory used by the game. Higher values may improve texture quality but could cause instability.",
            "RendererWorkerCount":             "Sets the number of CPU threads for handling rendering tasks. Higher values may improve performance on multi-core CPUs.",
            "VoicePushToTalk":                 "When enabled, you need to press a key to activate your microphone in voice chat.",
            "AudioMix":                        "Selects from predefined audio mix presets for different listening environments.",
            "Volume":                          "Adjusts the overall game volume.",
            "VoiceVolume":                     "Adjusts the volume of character dialogues and announcer voices.",
            "MusicVolume":                     "Adjusts the volume of background music.",
            "EffectsVolume":                   "Adjusts the volume of sound effects.",
            "HitMarkersVolume":                "Adjusts the volume of hit marker sounds.",
            "CapFps":                          "Enables or disables the custom frame rate limit.",
            "MaxFpsInGame":                    "Sets the maximum frame rate during gameplay. Higher values provide smoother gameplay but require more powerful hardware.",
            "MaxFpsInMenu":                    "Sets the maximum frame rate in menus. Lower values can reduce power consumption when not in gameplay.",
            "MaxFpsOutOfFocus":                "Sets the maximum frame rate when the game window is not in focus. Lower values can reduce resource usage when tabbed out.",
            "DepthOfField":                    "Adds a blur effect to out-of-focus areas when aiming down sights. May impact performance.",
            "DisplayMode":                     "Chooses between fullscreen, windowed, and borderless window modes.",
            "NvidiaReflex":                    "Reduces system latency on NVIDIA GPUs. 'Enabled + boost' mode may provide the lowest latency but could increase power consumption.",
            "ParticleQuality":                 "Adjusts the detail level of particle effects. Higher quality may impact performance in busy scenes.",
            "DLSSMode":                        "Enables NVIDIA DLSS (Deep Learning Super Sampling) for improved performance at higher resolutions on supported GPUs.",
            "AMDFidelityFX":                   "Enables AMD FidelityFX features for improved image quality or performance on supported GPUs.",
            "HDR":                             "Enables High Dynamic Range for improved color and brightness on supported displays.",
            "RecommendedSet":                  "Indicates whether recommended settings have been applied. If set to false, the game will reset settings to recommended values.",
            "ShowBlood":                       "Toggles the display of blood effects in the game.",
            "ShowBrass":                       "Toggles whether weapons eject brass (shell casings) when fired.",
            "VSyncInMenu":                     "Enables vertical sync in menus to prevent screen tearing.",
            "ResolutionMultiplier":            "Adjusts the rendering resolution relative to the display resolution. Values below 100 can improve performance at the cost of image quality.",
            "AspectRatio":                     "Forces a specific aspect ratio for the game, independent of the window's aspect ratio.",
            "FocusedMode":                     "Enables a mode that reduces on-screen distractions for better focus during gameplay.",
            "TextureFilter":                   "Sets the quality of texture filtering. Higher values provide sharper textures at oblique angles but may impact performance.",
            "Tessellation":                    "Controls the level of geometric detail. Higher values provide more detailed surfaces but impact performance.",
            "VolumetricQuality":               "Adjusts the quality of volumetric lighting effects. Higher quality provides more realistic fog and smoke but impacts performance.",
            "SSAOTechnique":                   "Sets the method used for Screen Space Ambient Occlusion, which adds depth and realism to shadows in corners and crevices.",
            "DLSSFrameGeneration":             "Enables NVIDIA DLSS Frame Generation, which can significantly boost FPS on supported hardware.",
            "FSRFrameInterpolation":           "Enables AMD FSR Frame Interpolation, which can boost FPS on supported hardware.",
            "ShaderQuality":                   "Adjusts the complexity and detail of shader effects. Lower settings can improve performance on older hardware.",
            "DeferredPhysics":                 "Controls the quality of physics simulations. Higher quality provides more realistic physics but impacts CPU performance.",
            "GPUUploadHeaps":                  "Enables optimizations for systems that support resizable BAR, allowing more efficient data transfer to the GPU.",
            "MicrophoneVolume":                "Adjusts the volume of your microphone input.",
            "MicThreshold":                    "Sets the minimum volume threshold for your microphone to activate.",
            "Brightness":                      "Adjusts the overall brightness of the game. Higher values make the game brighter but may wash out some details.",
            "Fov":                             "Adjusts the Field of View in first-person perspective. Higher values show more of the game world but may cause distortion at the edges.",
            "ThirdPersonFov":                  "Adjusts the Field of View in third-person perspective.",
            "ADSFovScaling":                   "When enabled, maintains your set FOV when aiming down sights.",
            "MouseInvertPitch":                "Inverts the vertical mouse movement. Enable if you prefer pushing the mouse forward to look down.",
            "MouseHorizontalSensibility":      "Adjusts the horizontal sensitivity of the mouse. Higher values make camera movement more responsive.",
            "MouseVerticalSensibility":        "Adjusts the vertical sensitivity of the mouse. Higher values make camera movement more responsive.",
            "ADSSensitivity":                  "Adjusts mouse sensitivity when aiming down sights. Lower values can help with precision aiming.",
            "ConfigCloudStorageEnabled":       "Enables cloud storage for your configuration settings.",
            "ConfigCloudSavegameEnabled":      "Enables cloud storage for your savegames.",
            "EnableHUD":                       "Toggles the visibility of the Heads-Up Display (HUD) during gameplay.",
            "FreeLook":                        "Enables the ability to look around freely without changing your character's direction of movement.",
            "MonoSound":                       "Enables mono audio output, which can be useful for players with hearing impairments or using a single earphone.",
            "VoiceChat":                       "Enables or disables voice chat functionality in the game.",
            "MouseAcceleration":               "Applies acceleration to mouse movement. Higher values make the cursor move faster as you move the mouse quicker.",
            "MouseFilter":                     "Applies smoothing to mouse movement. Higher values can reduce jitter but may introduce input lag.",
            "MouseSmoothing":                  "Enables additional smoothing of mouse movement, which can reduce jitter but may introduce input lag.",
            "ConstrainMouse":                  "When enabled, locks the mouse cursor to the game window.",
            "HDRGamma":                        "Adjusts the gamma curve for HDR displays. Only applies when HDR is enabled.",
            "HDRMaxLum":                       "Sets the maximum luminance for HDR content. Only applies when HDR is enabled.",
            "HDRMinLum":                       "Sets the minimum luminance for HDR content. Only applies when HDR is enabled.",
            "TextureQuality":                  "Adjusts the resolution of textures. Lower numbers indicate higher quality. Higher quality requires more VRAM and may impact performance.",
            "SoundOutputDevice":               "Displays the current sound output device. This setting is for information only and cannot be edited here.",
            "SoundInputDevice":                "Displays the current sound input device. This setting is for information only and cannot be edited here.",
            "VoiceOutputDevice":               "Displays the current voice output device. This setting is for information only and cannot be edited here.",
            "VoiceInputDevice":                "Displays the current voice input device. This setting is for information only and cannot be edited here.",
            "Monitor":                         "Displays the current monitor being used. This setting is for information only and cannot be edited here.",
            "GPUName":                         "Displays the name of the GPU being used. This setting is for information only and cannot be edited here.",
            "DetectedFrequencyGHz":            "Displays the detected CPU frequency. This setting is for information only and cannot be edited here.",
            "DetectedMemoryAmountMB":          "Displays the detected amount of system memory. This setting is for information only and cannot be edited here.",
            "LastUsedGPU":                     "Displays the last GPU used to run the game. This setting is for information only and cannot be edited here.",
            "GPUDriverVersion":                "Displays the current GPU driver version. This setting is for information only and cannot be edited here.",
            "DisplayDriverVersion":            "Displays the current display driver version. This setting is for information only and cannot be edited here.",
            "DisplayDriverVersionRecommended": "Displays the recommended display driver version. This setting is for information only and cannot be edited here.",
            "ESSDI":                           "ESSDI information. This setting is for information only and cannot be edited here.",
            "VoiceChatEffect":                 "Selects the voice chat effect to apply.",
            "TargetRefreshRate":               "Sets the target refresh rate for the game.",
            "Resolution":                      "Sets the display resolution for the game.",
            "RefreshRate":                     "Sets the refresh rate for the game display.",
        }

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
            self.selected_game = self.game
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
            self.game_agnostic_file_path = os.path.join(default_path, "gamerprofile.0.BASE.cst")

            if not os.path.exists(self.file_path):
                QMessageBox.warning(self, "File Not Found", f"Could not find {file_name}. Please select it manually.")
                self.file_path = QFileDialog.getOpenFileName(self, f"Select {file_name}", default_path,
                                                             "CST Files (*.cst);;All Files (*)")[0]

            if not os.path.exists(self.game_agnostic_file_path):
                QMessageBox.warning(self, "File Not Found", f"Could not find gamerprofile.0.BASE.cst. Please select it manually.")
                self.game_agnostic_file_path = QFileDialog.getOpenFileName(self, "Select gamerprofile.0.BASE.cst", default_path,
                                                                           "CST Files (*.cst);;All Files (*)")[0]
        else:
            default_path = os.path.expanduser("~\\Documents\\Call of Duty\\players")
            self.file_path = QFileDialog.getOpenFileName(self, "Select options.4.cod23.cst file", default_path,
                                                         "CST Files (*.cst);;All Files (*)")[0]
            self.game_agnostic_file_path = QFileDialog.getOpenFileName(self, "Select gamerprofile.0.BASE.cst file", default_path,
                                                                       "CST Files (*.cst);;All Files (*)")[0]

        if self.file_path and self.game_agnostic_file_path:
            self.read_only = not os.access(self.file_path, os.W_OK) or not os.access(self.game_agnostic_file_path, os.W_OK)
            if self.read_only:
                QMessageBox.information(self, "Read-only File",
                                        "One or both of the selected files are read-only. You can make changes, but you'll need to save them as new files or remove the read-only attribute.")
            self.parse_options_file()
            self.display_options()

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
            self.log(
                    f"Loaded {sum(len(section['settings']) for section in self.options.values())} options from {self.file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to parse options file {file_path}: {str(e)}")
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
                if setting['name'] in self.non_editable_fields:
                    widget = QLineEdit(value)
                    widget.setReadOnly(True)
                elif setting['name'] in ["VoiceChatEffect", "TargetRefreshRate"]:
                    widget = QComboBox()
                    options = setting['comment'].split("one of ")[1].strip("[]").split(", ")
                    widget.addItems(options)
                    widget.setCurrentText(value)
                elif setting['name'] == "Resolution":
                    widget = QComboBox()
                    options = ["1920x1080", "2560x1440", "3840x2160"]
                    widget.addItems(options)
                    widget.setCurrentText(value)
                elif setting['name'] == "RefreshRate":
                    widget = QComboBox()
                    options = ["60 Hz", "120 Hz"]
                    widget.addItems(options)
                    widget.setCurrentText(value)
                elif value.lower() in ('true', 'false'):
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
                                    widget = NoScrollSlider(Qt.Horizontal)
                                    widget.setRange(int(min_val), int(max_val))
                                    widget.setValue(int(float(value)))
                                    widget.setTickPosition(QSlider.TicksBelow)
                                    widget.setTickInterval(max(1, int((max_val - min_val) / 10)))
                                else:
                                    widget = NoScrollSlider(Qt.Horizontal)
                                    widget.setRange(int(min_val * 1000), int(max_val * 1000))
                                    widget.setValue(int(float(value) * 1000))
                                    widget.setTickPosition(QSlider.TicksBelow)
                                    widget.setTickInterval((int(max_val * 1000) - int(min_val * 1000)) // 10)
                                value_label = QLabel(value)
                                scroll_layout.addWidget(value_label, i, 2)
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
                    matches = re.findall(r'\[(.*?)\]', setting['comment'])
                    if matches:
                        options = matches[0].split(', ')
                        widget = QComboBox()
                        widget.addItems(options)
                        widget.setCurrentText(value)
                    else:
                        widget = QLineEdit(value)
                else:
                    widget = QLineEdit(value)
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
                
    def save_options(self):
        self.log("Starting save_options method")
        if not self.file_path or not self.game_agnostic_file_path:
            QMessageBox.critical(self, "Error", "One or both files are not loaded")
            return
        if self.read_only:
            new_file_path, _ = QFileDialog.getSaveFileName (self, "Save Game-Specific File As", os.path.dirname (self.file_path),                                                           "CST Files (*.cst);;All Files (*)")
            new_game_agnostic_file_path, _ = QFileDialog.getSaveFileName (self, "Save Game-Agnostic File As", os.path.dirname (self.game_agnostic_file_path),
                                                                         "CST Files (*.cst);;All Files (*)")
            if not new_file_path or not new_game_agnostic_file_path:
                return
            self.file_path = new_file_path
            self.game_agnostic_file_path = new_game_agnostic_file_path
            self.read_only = False
        try:
            self.save_file(self.file_path, "GameSpecific")
            self.save_file(self.game_agnostic_file_path, "GameAgnostic")
            if self.read_only_action.isChecked():
                os.chmod(self.file_path, stat.S_IREAD)
                os.chmod(self.game_agnostic_file_path, stat.S_IREAD)
                self.read_only = True
            else:
                os.chmod(self.file_path, stat.S_IWRITE | stat.S_IREAD)
                os.chmod(self.game_agnostic_file_path, stat.S_IWRITE | stat.S_IREAD)
                self.read_only = False
            self.log(f"Options saved to {self.file_path} and {self.game_agnostic_file_path}")
            QMessageBox.information(self, "Success", "Options saved successfully")
            self.reload_file()
        except Exception as e:
            error_msg = f"Failed to save options: {str(e)}\n"
            error_msg += f"Error type: {type(e).__name__}\n"
            error_msg += f"Error args: {e.args}\n"
            QMessageBox.critical(self, "Error", error_msg)
            self.log(error_msg)

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
                                        continue
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
                                    if file_type == "GameSpecific":
                                        lines[i] = f"{line.split('=')[0]}= \"{value}\"{' // ' + setting['comment'] if setting['comment'] else ''}\n"
                                    else:  # GameAgnostic
                                        lines[i] = f"{line.split('=')[0]}= {value}{' // ' + setting['comment'] if setting['comment'] else ''}\n"
            with open(file_path, 'w') as file:
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
            error_msg = f"Failed to save options to {file_path}: {str(e)}\n"
            error_msg += f"Error type: {type(e).__name__}\n"
            error_msg += f"Error args: {e.args}\n"
            QMessageBox.critical(self, "Error", error_msg)
        self.log(error_msg)
        raise

def reload_file(self):
    if self.file_path and self.game_agnostic_file_path:
        self.parse_options_file()
        self.display_options()
        self.log("Files reloaded")

def main():
    app = QApplication(sys.argv)
    editor = OptionsEditor()
    editor.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()