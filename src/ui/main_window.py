import sys
import os
import json
import time
import threading
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QLabel, QMessageBox, QComboBox, QSpinBox
)
from PySide6.QtCore import Qt
import pyautogui
import keyboard

MACROS_DIR = os.path.join(os.path.dirname(__file__), '../../macros')
os.makedirs(MACROS_DIR, exist_ok=True)
MAX_MACROS = 5

class MacroRunner(threading.Thread):
    def __init__(self, sequence, loop_count, stop_event, update_runtime):
        super().__init__()
        self.sequence = sequence
        self.loop_count = loop_count
        self.stop_event = stop_event
        self.update_runtime = update_runtime

    def run(self):
        start_time = time.time()
        for i in range(self.loop_count):
            if self.stop_event.is_set():
                break
            for action in self.sequence:
                if self.stop_event.is_set():
                    break
                if action['type'] == 'key':
                    keyboard.press_and_release(action['value'])
                elif action['type'] == 'mouse':
                    pyautogui.click(button=action['value'])
                elif action['type'] == 'wait':
                    time.sleep(action['value'])
            self.update_runtime(time.time() - start_time)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Forza KB/M Macro Automation")
        self.sequence = []
        self.runner = None
        self.stop_event = threading.Event()
        self.global_hotkey_enabled = False
        self.hotkey = 'ctrl+alt+m'
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        layout = QVBoxLayout()

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Type", "Value", "Wait (s)"])
        layout.addWidget(self.table)

        add_row_btn = QPushButton("Add Action")
        add_row_btn.clicked.connect(self.add_action_row)
        layout.addWidget(add_row_btn)

        controls = QHBoxLayout()
        self.loop_spin = QSpinBox()
        self.loop_spin.setMinimum(1)
        self.loop_spin.setMaximum(999)
        self.loop_spin.setValue(1)
        controls.addWidget(QLabel("Loops:"))
        controls.addWidget(self.loop_spin)

        self.start_btn = QPushButton("Start Macro")
        self.start_btn.clicked.connect(self.start_macro)
        controls.addWidget(self.start_btn)

        self.stop_btn = QPushButton("Stop Macro")
        self.stop_btn.clicked.connect(self.stop_macro)
        self.stop_btn.setEnabled(False)
        controls.addWidget(self.stop_btn)

        layout.addLayout(controls)

        macro_controls = QHBoxLayout()
        self.macro_name_edit = QLineEdit()
        self.macro_name_edit.setPlaceholderText("Macro name")
        macro_controls.addWidget(self.macro_name_edit)

        self.save_btn = QPushButton("Save Macro")
        self.save_btn.clicked.connect(self.save_macro)
        macro_controls.addWidget(self.save_btn)

        self.load_combo = QComboBox()
        self.refresh_macro_list()
        macro_controls.addWidget(self.load_combo)

        self.load_btn = QPushButton("Load Macro")
        self.load_btn.clicked.connect(self.load_macro)
        macro_controls.addWidget(self.load_btn)

        layout.addLayout(macro_controls)

        hotkey_controls = QHBoxLayout()
        self.hotkey_edit = QLineEdit(self.hotkey)
        hotkey_controls.addWidget(QLabel("Global Hotkey:"))
        hotkey_controls.addWidget(self.hotkey_edit)
        self.hotkey_toggle_btn = QPushButton("Enable Hotkey")
        self.hotkey_toggle_btn.setCheckable(True)
        self.hotkey_toggle_btn.clicked.connect(self.toggle_hotkey)
        hotkey_controls.addWidget(self.hotkey_toggle_btn)
        layout.addLayout(hotkey_controls)

        self.runtime_label = QLabel("Loop Runtime: 0.00s")
        layout.addWidget(self.runtime_label)

        central.setLayout(layout)
        self.setCentralWidget(central)

    def add_action_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        type_combo = QComboBox()
        type_combo.addItems(["key", "mouse", "wait"])
        self.table.setCellWidget(row, 0, type_combo)

        key_options = ["up", "down", "left", "right", "enter", "space", "tab", "esc", "backspace", "delete", "home", "end", "pageup", "pagedown"]
        key_options += [chr(i) for i in range(65, 91)]  # A-Z
        key_options += [str(i) for i in range(0, 10)]   # 0-9
        mouse_options = ["left", "right", "middle"]

        value_combo = QComboBox()
        value_combo.setEditable(False)
        self.table.setCellWidget(row, 1, value_combo)

        wait_item = QTableWidgetItem("0")
        self.table.setItem(row, 2, wait_item)

        def update_row_fields():
            type_ = type_combo.currentText()
            if type_ == "wait":
                value_combo.clear()
                value_combo.setEnabled(False)
                wait_item.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled)
            elif type_ == "key":
                value_combo.clear()
                value_combo.addItems(key_options)
                value_combo.setEnabled(True)
                wait_item.setFlags(Qt.ItemIsEnabled)  # Disable editing
            elif type_ == "mouse":
                value_combo.clear()
                value_combo.addItems(mouse_options)
                value_combo.setEnabled(True)
                wait_item.setFlags(Qt.ItemIsEnabled)  # Disable editing
        type_combo.currentIndexChanged.connect(update_row_fields)
        update_row_fields()

    def get_sequence(self):
        sequence = []
        for row in range(self.table.rowCount()):
            type_widget = self.table.cellWidget(row, 0)
            type_ = type_widget.currentText() if type_widget else "key"
            value_item = self.table.item(row, 1)
            value = value_item.text() if value_item else ""
            wait_item = self.table.item(row, 2)
            wait = float(wait_item.text()) if wait_item and wait_item.text() else 0.0
            if type_ == "wait":
                sequence.append({"type": "wait", "value": wait})
            else:
                sequence.append({"type": type_, "value": value})
                if wait > 0:
                    sequence.append({"type": "wait", "value": wait})
        return sequence

    def start_macro(self):
        if self.runner and self.runner.is_alive():
            QMessageBox.warning(self, "Macro Running", "Macro is already running.")
            return
        self.sequence = self.get_sequence()
        if not self.sequence:
            QMessageBox.warning(self, "No Actions", "Add actions to the macro before starting.")
            return
        self.stop_event.clear()
        loop_count = self.loop_spin.value()
        self.runner = MacroRunner(self.sequence, loop_count, self.stop_event, self.update_runtime)
        self.runner.start()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def stop_macro(self):
        self.stop_event.set()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def update_runtime(self, runtime):
        self.runtime_label.setText(f"Loop Runtime: {runtime:.2f}s")

    def save_macro(self):
        name = self.macro_name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Name Required", "Enter a name for the macro.")
            return
        macro_files = [f for f in os.listdir(MACROS_DIR) if f.endswith('.json')]
        if len(macro_files) >= MAX_MACROS and name + '.json' not in macro_files:
            QMessageBox.warning(self, "Limit Reached", f"Maximum {MAX_MACROS} macros allowed.")
            return
        sequence = self.get_sequence()
        if not sequence:
            QMessageBox.warning(self, "No Actions", "Add actions before saving.")
            return
        path = os.path.join(MACROS_DIR, name + '.json')
        with open(path, 'w') as f:
            json.dump(sequence, f, indent=2)
        self.refresh_macro_list()
        QMessageBox.information(self, "Saved", f"Macro '{name}' saved.")

    def refresh_macro_list(self):
        self.load_combo.clear()
        macro_files = [f for f in os.listdir(MACROS_DIR) if f.endswith('.json')]
        for f in macro_files:
            self.load_combo.addItem(f[:-5])

    def load_macro(self):
        name = self.load_combo.currentText()
        if not name:
            QMessageBox.warning(self, "Select Macro", "Choose a macro to load.")
            return
        path = os.path.join(MACROS_DIR, name + '.json')
        if not os.path.exists(path):
            QMessageBox.warning(self, "Not Found", f"Macro '{name}' not found.")
            return
        with open(path, 'r') as f:
            sequence = json.load(f)
        self.table.setRowCount(0)
        for action in sequence:
            row = self.table.rowCount()
            self.table.insertRow(row)
            type_combo = QComboBox()
            type_combo.addItems(["key", "mouse", "wait"])
            type_combo.setCurrentText(action['type'])
            self.table.setCellWidget(row, 0, type_combo)
            if action['type'] == 'wait':
                self.table.setItem(row, 1, QTableWidgetItem(""))
                self.table.setItem(row, 2, QTableWidgetItem(str(action['value'])))
            else:
                self.table.setItem(row, 1, QTableWidgetItem(action['value']))
                self.table.setItem(row, 2, QTableWidgetItem("0"))

    def toggle_hotkey(self):
        if self.hotkey_toggle_btn.isChecked():
            self.hotkey = self.hotkey_edit.text().strip()
            if not self.hotkey:
                QMessageBox.warning(self, "Hotkey Required", "Enter a hotkey.")
                self.hotkey_toggle_btn.setChecked(False)
                return
            try:
                keyboard.add_hotkey(self.hotkey, self.hotkey_action)
                self.global_hotkey_enabled = True
                self.hotkey_toggle_btn.setText("Disable Hotkey")
            except Exception as e:
                QMessageBox.warning(self, "Hotkey Error", str(e))
                self.hotkey_toggle_btn.setChecked(False)
        else:
            keyboard.remove_hotkey(self.hotkey)
            self.global_hotkey_enabled = False
            self.hotkey_toggle_btn.setText("Enable Hotkey")

    def hotkey_action(self):
        if self.runner and self.runner.is_alive():
            self.stop_macro()
        else:
            self.start_macro()


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
