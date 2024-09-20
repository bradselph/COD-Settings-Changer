#!/usr/bin/env python
_X='-?\\d+(?:\\.\\d+)?'
_W='RefreshRate'
_V='Resolution'
_U='TargetRefreshRate'
_T='VoiceChatEffect'
_S='Save Log'
_R='value_label'
_Q='Error'
_P='// DO NOT MODIFY'
_O='file_type'
_N='GameAgnostic'
_M='MW3/Warzone 2024'
_L='slider'
_K='editable'
_J='//'
_I=None
_H='GameSpecific'
_G='='
_F='settings'
_E='widget'
_D=True
_C='comment'
_B=False
_A='name'
from PyQt5.QtWidgets import QApplication,QMainWindow,QWidget,QVBoxLayout,QPushButton,QLabel,QFileDialog,QMessageBox,QTabWidget,QScrollArea,QCheckBox,QSlider,QComboBox,QLineEdit,QGridLayout,QDialog,QTextEdit,QAction,QDockWidget,QHBoxLayout
from PyQt5.QtCore import Qt,QRegExp
from PyQt5.QtGui import QRegExpValidator
from help_texts import get_help_texts
import sys,os,re,stat
class GameSelector(QDialog):
	def __init__(A,parent=_I):C='MW2/Warzone 2023';super().__init__(parent);A.setWindowTitle('Select Game');A.setFixedSize(300,150);B=QVBoxLayout();D=QLabel('Choose the game you want to modify settings for:');B.addWidget(D);A.mw2_button=QPushButton(C);A.mw2_button.clicked.connect(lambda:A.select_game(C));B.addWidget(A.mw2_button);A.mw3_button=QPushButton(_M);A.mw3_button.clicked.connect(lambda:A.select_game(_M));B.addWidget(A.mw3_button);A.selected_game=_I;A.setLayout(B);A.setup_window_flags()
	def setup_window_flags(A):A.setWindowFlags(A.windowFlags()|Qt.Window|Qt.WindowStaysOnTopHint)
	def showEvent(A,event):super().showEvent(event);A.raise_();A.activateWindow()
	def select_game(A,game):A.selected_game=game;A.accept()
class LogWindow(QDockWidget):
	def __init__(A,parent=_I):super().__init__(parent);A.setWindowTitle('Log');A.setAllowedAreas(Qt.AllDockWidgetAreas);B=QWidget();C=QVBoxLayout(B);A.text_edit=QTextEdit();A.text_edit.setReadOnly(_D);C.addWidget(A.text_edit);D=QPushButton(_S);D.clicked.connect(A.save_log);C.addWidget(D);A.setWidget(B)
	def log(A,message):A.text_edit.append(message)
	def save_log(A):
		B,D=QFileDialog.getSaveFileName(A,_S,'','Log Files (*.log);;All Files (*)')
		if B:
			with open(B,'w')as C:C.write(A.text_edit.toPlainText())
			A.log(f"Log saved to {B}")
	def closeEvent(A,event):
		if isinstance(A.parent(),OptionsEditor):A.parent().show_log_action.setChecked(_B);A.parent().log_window_detached=A.isFloating()
		super().closeEvent(event)
class NoScrollSlider(QSlider):
	def wheelEvent(A,event):event.ignore()
class NoScrollComboBox(QComboBox):
	def wheelEvent(A,event):event.ignore()
class OptionsEditor(QMainWindow):
	def __init__(A):super().__init__();A.setWindowTitle('Call of Duty Options Editor');A.setGeometry(100,100,1000,600);A.options={};A.widgets={};A.file_path='';A.game_agnostic_file_path='';A.read_only=_B;A.game='';A.selected_game='';A.non_editable_fields=['SoundOutputDevice','SoundInputDevice','VoiceOutputDevice','VoiceInputDevice','Monitor','GPUName','DetectedFrequencyGHz','DetectedMemoryAmountMB','LastUsedGPU','GPUDriverVersion','DisplayDriverVersion','DisplayDriverVersionRecommended','ESSDI'];A.unsaved_changes=_B;A.log_window=LogWindow(A);A.addDockWidget(Qt.BottomDockWidgetArea,A.log_window);A.log_window.hide();A.log_window_detached=_B;A.log_window.topLevelChanged.connect(A.on_log_window_detached);A.create_menu();A.create_widgets();A.help_texts=get_help_texts();A.setStyleSheet('\n\t\t\tQToolTip {\n\t\t\t\tbackground-color: #2a82da;\n\t\t\t\tcolor: white;\n\t\t\t\tborder: 1px solid white;\n\t\t\t\tpadding: 5px;\n\t\t\t}\n\t\t');A.select_game()
	def log(A,message):
		B=message
		if hasattr(A,'log_window'):A.log_window.log(B)
		else:print(B)
	def create_menu(A):C=A.menuBar();B=C.addMenu('File');B.addAction(QAction('Load Options',A,triggered=A.load_file));B.addAction(QAction('Save Options',A,triggered=A.save_options));B.addAction(QAction('Reload',A,triggered=A.reload_file));B.addAction(QAction('Change Game',A,triggered=A.change_game));B.addSeparator();B.addAction(QAction('Exit',A,triggered=A.close));D=C.addMenu('View');A.show_log_action=QAction('Show Log',A,checkable=_D);A.show_log_action.triggered.connect(A.toggle_log_window);D.addAction(A.show_log_action);E=C.addMenu('Options');A.read_only_action=QAction('Save as Read-only',A,checkable=_D);E.addAction(A.read_only_action)
	def create_widgets(A):B=QWidget();A.setCentralWidget(B);C=QVBoxLayout();A.tab_widget=QTabWidget();C.addWidget(A.tab_widget);B.setLayout(C)
	def select_game(A):
		try:
			B=GameSelector(A)
			if B.exec_():A.game=B.selected_game;A.selected_game=A.game;A.log(f"Selected game: {A.game}");A.load_file(auto=_D)
			else:A.log('Game selection cancelled');A.close()
		except Exception as C:A.log(f"Error in select_game: {str(C)}");QMessageBox.critical(A,'Game Selection Error',f"An error occurred during game selection: {str(C)}")
	def change_game(A):
		if A.check_unsaved_changes():A.select_game();A.load_file(auto=_D);A.log(f"Changed game to: {A.game}")
	def on_log_window_detached(A,floating):A.log_window_detached=floating
	def toggle_log_window(A,checked):
		if checked:
			if not A.log_window.isVisible():
				if A.log_window_detached:A.log_window=LogWindow(A);A.addDockWidget(Qt.BottomDockWidgetArea,A.log_window);A.log_window.topLevelChanged.connect(A.on_log_window_detached);A.log_window_detached=_B
				A.log_window.show()
			elif A.log_window_detached:A.log_window.setFloating(_B);A.addDockWidget(Qt.BottomDockWidgetArea,A.log_window);A.log_window_detached=_B
		else:A.log_window.close()
	def show_log_window(A):
		if not A.log_window.isVisible():
			if A.log_window_detached:A.log_window=LogWindow(A);A.addDockWidget(Qt.BottomDockWidgetArea,A.log_window);A.log_window.topLevelChanged.connect(A.on_log_window_detached);A.log_window_detached=_B
			A.log_window.show()
		elif A.log_window_detached:A.log_window.setFloating(_B);A.addDockWidget(Qt.BottomDockWidgetArea,A.log_window);A.log_window_detached=_B
	def hide_log_window(A):A.log_window.close()
	def load_file(A,auto=_B):
		I='game_agnostic';H='game_specific'
		try:
			A.log('Starting load_file method');E=os.path.expanduser('~\\Documents\\Call of Duty\\players');J={H:'options.4.cod23.cst'if A.game==_M else'options.3.cod22.cst',I:'gamerprofile.0.BASE.cst'};B={}
			for(D,F)in J.items():
				C=os.path.join(E,F)
				if not auto or not os.path.exists(C):C=A.get_file_path(D,F,E)
				if C:B[D]=C
				else:A.log(f"File selection cancelled for {D}");return
			if len(B)==2:
				A.file_path=B[H];A.game_agnostic_file_path=B[I];A.log(f"Loading files: {A.file_path} and {A.game_agnostic_file_path}");A.read_only=not os.access(A.file_path,os.W_OK)or not os.access(A.game_agnostic_file_path,os.W_OK)
				if A.read_only:A.show_read_only_message()
				A.parse_options_file();A.display_options();A.unsaved_changes=_B
			else:A.log('File selection incomplete');A.show_error_message('File Selection','Both files are required to proceed. Please select both files.')
		except Exception as G:A.log(f"Error in load_file: {str(G)}");A.show_error_message('File Loading Error',f"An error occurred while loading files: {str(G)}")
	def get_file_path(B,file_type,file_name,default_path):
		E=default_path;D=file_name;C=file_type;G=f"Please select the {C} file:\n{D}\n\nThis file is typically located in:\n{E}";A=QMessageBox(QMessageBox.Information,'Select File',G);A.setStandardButtons(QMessageBox.Ok|QMessageBox.Cancel);A.setDefaultButton(QMessageBox.Ok);A.setWindowFlags(A.windowFlags()|Qt.WindowStaysOnTopHint);H=A.exec_()
		if H==QMessageBox.Ok:
			F,I=QFileDialog.getOpenFileName(B,f"Select {D}",E,'CST Files (*.cst);;All Files (*)')
			if F:return F
			else:B.log(f"No file selected for {C}");return
		else:B.log(f"File selection cancelled for {C}");return
	def show_read_only_message(B):A=QMessageBox(QMessageBox.Information,'Read-only File',"One or both of the selected files are read-only. You can make changes, but you'll need to save them as new files or remove the read-only attribute.");A.setWindowFlags(A.windowFlags()|Qt.WindowStaysOnTopHint);A.exec_()
	def show_error_message(B,title,message):A=QMessageBox(QMessageBox.Critical,title,message);A.setWindowFlags(A.windowFlags()|Qt.WindowStaysOnTopHint);A.exec_()
	def parse_options_file(A):A.options.clear();A.parse_file(A.file_path,_H);A.parse_file(A.game_agnostic_file_path,_N);A.log(f"Loaded {sum(len(A[_F])for A in A.options.values())} options from both files")
	def parse_file(B,file_path,file_type):
		G=file_type;C=file_path
		try:
			with open(C,'r')as M:
				H=M.read()
				if G==_H:J=re.split('//\\n// [A-Za-z]+\\n//',H)[1:];K=re.findall('//\\n// ([A-Za-z]+)\\n//',H)
				else:J=[H];K=[_N]
				for(I,N)in zip(K,J):
					if I not in B.options:B.options[I]={_F:[]}
					O=N.strip().split('\n')
					for D in O:
						if _G in D and not D.strip().startswith(_J):
							E,A=D.split(_G,1);E=E.split(':')[0].strip()if G==_H else E.split('@')[0].strip();A=A.strip().strip('"');F=''
							if _J in A:A,F=A.split(_J,1);A=A.strip();F=F.strip()
							B.options[I][_F].append({_A:E,'value':A,_C:F,_K:not D.strip().startswith(_P),_O:G})
			B.log(f"Loaded {sum(len(A[_F])for A in B.options.values())} options from {C}")
		except Exception as L:B.show_error_message(_Q,f"Failed to parse options file {C}: {str(L)}");B.log(f"Error parsing options file {C}: {str(L)}")
	def display_options(B):
		B.tab_widget.clear();B.widgets.clear()
		for(I,N)in B.options.items():
			J=QScrollArea();M=QWidget();D=QGridLayout()
			for(E,A)in enumerate(N[_F]):
				O=QLabel(f"{A[_A]}:");D.addWidget(O,E,0);P=A['value'].strip('"');C=B.create_widget(A,P)
				if isinstance(C,tuple):F,G=C;K=QHBoxLayout();K.addWidget(F);K.addWidget(G);D.addLayout(K,E,1);B.widgets[f"{I}_{A[_A]}"]={_L:F,_R:G}
				else:D.addWidget(C,E,1);B.widgets[f"{I}_{A[_A]}"]={_E:C}
				L=A[_K]and not A[_A].startswith(_P)and A[_A]not in B.non_editable_fields
				if isinstance(C,tuple):F.setEnabled(L);G.setEnabled(L)
				else:C.setEnabled(L)
				H=B.help_texts.get(A[_A],'No help text available for this setting.');H+=f"\n\nValid range: {A[_C]}"if A[_C]else''
				if isinstance(C,tuple):F.setToolTip(H);G.setToolTip(H)
				else:C.setToolTip(H)
				Q=QLabel(A[_C]);D.addWidget(Q,E,3);R=QLabel(f"({A[_O]})");D.addWidget(R,E,4)
			M.setLayout(D);J.setWidget(M);J.setWidgetResizable(_D);B.tab_widget.addTab(J,I)
		B.update_widget_states()
	def create_widget(B,setting,value):
		F='true';D=setting;C=value
		if D[_A]in B.non_editable_fields:A=QLineEdit(C);A.setReadOnly(_D)
		elif D[_A]in[_T,_U,_V,_W]:A=NoScrollComboBox();E=B.get_options_for_combobox(D);A.addItems(E);A.setCurrentText(C);A.currentTextChanged.connect(B.set_unsaved_changes)
		elif C.lower()in(F,'false'):A=QCheckBox();A.setChecked(C.lower()==F);A.stateChanged.connect(B.set_unsaved_changes)
		elif re.match('^-?\\d+(\\.\\d+)?$',C):
			return B.create_slider_widget(D,C)
			if isinstance(A,QSlider):A.valueChanged.connect(B.set_unsaved_changes)
			else:A.textChanged.connect(B.set_unsaved_changes)
		elif'one of'in D[_C]:
			A=NoScrollComboBox();E=re.findall('\\[(.*?)\\]',D[_C])
			if E:A.addItems(E[0].split(', '));A.setCurrentText(C);A.currentTextChanged.connect(B.set_unsaved_changes)
			else:A=QLineEdit(C);A.textChanged.connect(B.set_unsaved_changes)
		else:A=QLineEdit(C);A.textChanged.connect(B.set_unsaved_changes)
		return A
	def get_options_for_combobox(D,setting):
		C='120 Hz';B='60 Hz';A=setting
		if A[_A]==_T:return A[_C].split('one of ')[1].strip('[]').split(', ')
		elif A[_A]==_U:return[B,C]
		elif A[_A]==_V:return['1920x1080','2560x1440','3840x2160']
		elif A[_A]==_W:return[B,C]
	def create_slider_widget(F,setting,value):
		H=setting;E=value
		if'to'in H[_C]:
			B=re.findall(_X,H[_C])
			if len(B)>=2:
				try:
					C,D=float(B[0]),float(B[1]);G='.'not in B[0]and'.'not in B[1];A=NoScrollSlider(Qt.Horizontal)
					if G:A.setRange(int(C),int(D));A.setValue(int(float(E)))
					else:A.setRange(int(C*1000),int(D*1000));A.setValue(int(float(E)*1000))
					A.setTickPosition(QSlider.TicksBelow);A.setTickInterval((int(D*1000)-int(C*1000))//10 if not G else max(1,int((D-C)/10)));I=QLabel(E);A.valueChanged.connect(lambda v,label=I,min_v=C,max_v=D,whole=G:F.update_slider_value(v,label,min_v,max_v,whole));A.valueChanged.connect(F.set_unsaved_changes);return A,I
				except ValueError:pass
		A=QLineEdit(E);A.textChanged.connect(F.set_unsaved_changes);return A
	def update_slider_value(D,value,label,min_val,max_val,whole_number):
		C=whole_number;B=value
		if C:A=B
		else:A=B/1000
		label.setText(f"{A:.6f}"if not C else f"{A}")
	def update_widget_states(A):
		for(F,G)in A.options.items():
			for B in G[_F]:
				E=f"{F}_{B[_A]}"
				if E in A.widgets:
					C=A.widgets[E];D=B[_K]and not B[_A].startswith(_P)and B[_A]not in A.non_editable_fields
					if _L in C:C[_L].setEnabled(D);C[_R].setEnabled(D)
					else:C[_E].setEnabled(D)
	def set_unsaved_changes(A):A.unsaved_changes=_D
	def save_options(A):
		A.log(f"Starting save_options method for {A.game}")
		if not A.file_path or not A.game_agnostic_file_path:A.show_error_message(_Q,'One or both files are not loaded');return
		try:A.save_file_with_permissions(A.file_path,_H);A.save_file_with_permissions(A.game_agnostic_file_path,_N);A.update_file_permissions();A.log(f"Options saved to {A.file_path} and {A.game_agnostic_file_path}");QMessageBox.information(A,'Success',f"Options for {A.game} saved successfully");A.unsaved_changes=_B;A.reload_file()
		except Exception as C:B=f"Failed to save options for {A.game}: {str(C)}\n";B+=f"Error type: {type(C).__name__}\n";B+=f"Error args: {C.args}\n";A.show_error_message(_Q,B);A.log(B)
	def update_file_permissions(A):
		if A.read_only_action.isChecked():os.chmod(A.file_path,stat.S_IREAD);os.chmod(A.game_agnostic_file_path,stat.S_IREAD);A.read_only=_D
		else:os.chmod(A.file_path,stat.S_IWRITE|stat.S_IREAD);os.chmod(A.game_agnostic_file_path,stat.S_IWRITE|stat.S_IREAD);A.read_only=_B
	def save_file_with_permissions(B,file_path,file_type):
		A=file_path;C=os.stat(A).st_mode
		try:os.chmod(A,stat.S_IWRITE|stat.S_IREAD);B.save_file(A,file_type)
		finally:os.chmod(A,C)
	def save_file(A,file_path,file_type):
		E=file_type;D=file_path
		try:
			with open(D,'r')as F:G=F.readlines()
			for(L,C)in enumerate(G):
				if _G in C and not C.strip().startswith(_J):
					M=C.split(_G,1)[0].strip().split(':')[0]if E==_H else C.split(_G,1)[0].strip().split('@')[0]
					for(N,O)in A.options.items():
						for B in O[_F]:
							if M==B[_A]and B[_K]and B[_O]==E:
								K=f"{N}_{B[_A]}"
								if K in A.widgets:
									P=A.widgets[K];H=A.get_widget_value(P)
									if A.is_value_in_range(B,H):G[L]=A.format_line(E,C,B,H)
									else:A.log(f"Value {H} for {B[_A]} is out of range. Skipping.")
			with open(D,'w')as F:F.writelines(G)
		except Exception as I:J=f"Failed to save options to {D}: {str(I)}\n";J+=f"Error type: {type(I).__name__}\n";J+=f"Error args: {I.args}\n";raise Exception(J)
	def get_widget_value(B,widget_data):
		A=widget_data
		if _L in A:return A[_R].text()
		elif isinstance(A[_E],QCheckBox):return str(A[_E].isChecked()).lower()
		elif isinstance(A[_E],QComboBox):return A[_E].currentText()
		elif isinstance(A[_E],QLineEdit):return A[_E].text()
		return''
	def is_value_in_range(F,setting,value):
		B=setting
		if'to'in B[_C]:
			A=re.findall(_X,B[_C])
			if len(A)>=2:
				try:C,D=float(A[0]),float(A[1]);E=float(value);return C<=E<=D
				except ValueError:pass
		return _D
	def format_line(D,file_type,line,setting,value):
		C=' // ';B=value;A=setting
		if file_type==_H:return f'{line.split(_G)[0]}= "{B}"{C+A[_C]if A[_C]else""}\n'
		else:return f"{line.split(_G)[0]}= {B}{C+A[_C]if A[_C]else''}\n"
	def reload_file(A):
		if A.file_path and A.game_agnostic_file_path:A.parse_options_file();A.display_options();A.unsaved_changes=_B;A.log(f"Files reloaded for {A.game}")
	def check_unsaved_changes(A):
		if A.unsaved_changes:
			B=QMessageBox.question(A,'Unsaved Changes','You have unsaved changes. Do you want to save them?',QMessageBox.Save|QMessageBox.Discard|QMessageBox.Cancel,QMessageBox.Save)
			if B==QMessageBox.Save:A.save_options();return _D
			elif B==QMessageBox.Cancel:return _B
		return _D
	def closeEvent(B,event):
		A=event
		if B.check_unsaved_changes():A.accept()
		else:A.ignore()
def main():
	B=QApplication(sys.argv)
	try:C=OptionsEditor();C.show();sys.exit(B.exec_())
	except Exception as A:print(f"Unhandled exception in main: {str(A)}");QMessageBox.critical(_I,'Critical Error',f"An unhandled error occurred: {str(A)}");sys.exit(1)
if __name__=='__main__':main()