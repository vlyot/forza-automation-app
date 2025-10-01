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
                    key = action.get('value', '')
                    if key:
                        keyboard.press_and_release(key)
                        time.sleep(0.3)
                elif action['type'] == 'mouse':
                    btn = action.get('value', '')
                    if btn:
                        pyautogui.click(button=btn)
                        time.sleep(0.3)
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
        scale = 1.35
        from PySide6.QtGui import QFont
        font = self.font()
        preferred_fonts = ["SF Pro Display", "San Francisco", "Segoe UI", "Arial"]
        for fam in preferred_fonts:
            font.setFamily(fam)
            test_font = QFont(fam)
            if test_font.family() == fam:
                break
        font.setPointSizeF(font.pointSizeF() * scale)
        self.setFont(font)
        self.resize(int(800 * scale), int(600 * scale))

    from PySide6.QtWidgets import QTabWidget
    central = QWidget()
    main_layout = QVBoxLayout()
    self._main_layout = main_layout
    self._padding_percent = 0.03

    # --- Macro Tab ---
    macro_tab = QWidget()
    macro_layout = QVBoxLayout()

    self.table = QTableWidget(0, 3)
    self.table.setHorizontalHeaderLabels(["Type", "Value", "Wait (s)"])
    self.table.setFont(font)
    macro_layout.addWidget(self.table)

    add_row_btn = QPushButton("Add Action")
    add_row_btn.setFont(font)
    add_row_btn.clicked.connect(self.add_action_row)
    macro_layout.addWidget(add_row_btn)

    duplicate_row_btn = QPushButton("Duplicate Action")
    duplicate_row_btn.setFont(font)
    duplicate_row_btn.clicked.connect(self.duplicate_action_row)
    macro_layout.addWidget(duplicate_row_btn)

    controls = QHBoxLayout()
    self.loop_spin = QSpinBox()
    self.loop_spin.setMinimum(1)
    self.loop_spin.setMaximum(999)
    self.loop_spin.setValue(1)
    self.loop_spin.setFont(font)
    controls.addWidget(QLabel("Loops:", font=font))
    controls.addWidget(self.loop_spin)

    self.start_btn = QPushButton("Start Macro")
    self.start_btn.setFont(font)
    self.start_btn.clicked.connect(self.start_macro)
    controls.addWidget(self.start_btn)

    self.stop_btn = QPushButton("Stop Macro")
    self.stop_btn.setFont(font)
    self.stop_btn.clicked.connect(self.stop_macro)
    self.stop_btn.setEnabled(False)
    controls.addWidget(self.stop_btn)

    macro_layout.addLayout(controls)

    self.runtime_label = QLabel("Loop Runtime: 0.00s")
    self.runtime_label.setFont(font)
    macro_layout.addWidget(self.runtime_label)

    self.countdown_label = QLabel("")
    self.countdown_label.setFont(font)
    macro_layout.addWidget(self.countdown_label)

    macro_tab.setLayout(macro_layout)

    # --- Config Tab ---
    config_tab = QWidget()
    config_layout = QVBoxLayout()

    macro_controls = QHBoxLayout()
    self.macro_name_edit = QLineEdit()
    self.macro_name_edit.setPlaceholderText("Macro name")
    self.macro_name_edit.setFont(font)
    macro_controls.addWidget(self.macro_name_edit)

    self.save_btn = QPushButton("Save Macro")
    self.save_btn.setFont(font)
    self.save_btn.clicked.connect(self.save_macro)
    macro_controls.addWidget(self.save_btn)

    self.load_combo = QComboBox()
    self.load_combo.setFont(font)
    self.refresh_macro_list()
    macro_controls.addWidget(self.load_combo)

    self.load_btn = QPushButton("Load Macro")
    self.load_btn.setFont(font)
    self.load_btn.clicked.connect(self.load_macro)
    macro_controls.addWidget(self.load_btn)

    config_layout.addLayout(macro_controls)

    hotkey_controls = QHBoxLayout()
    self.hotkey_edit = QLineEdit(self.hotkey)
    self.hotkey_edit.setFont(font)
    hotkey_controls.addWidget(QLabel("Global Hotkey:", font=font))
    hotkey_controls.addWidget(self.hotkey_edit)
    self.hotkey_toggle_btn = QPushButton("Enable Hotkey")
    self.hotkey_toggle_btn.setFont(font)
    self.hotkey_toggle_btn.setCheckable(True)
    self.hotkey_toggle_btn.clicked.connect(self.toggle_hotkey)
    hotkey_controls.addWidget(self.hotkey_toggle_btn)
    config_layout.addLayout(hotkey_controls)

    config_tab.setLayout(config_layout)

    # --- Tabs Widget ---
    tabs = QTabWidget()
    tabs.addTab(macro_tab, "Macro")
    tabs.addTab(config_tab, "Config")
    main_layout.addWidget(tabs)

    central.setLayout(main_layout)
    self.setCentralWidget(central)
    self._container = central
    self._update_padding()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_padding()

    def _update_padding(self):
        # Add 3% padding around the main layout
        if hasattr(self, '_container') and hasattr(self, '_main_layout'):
            w = self._container.width()
            h = self._container.height()
            pad_w = int(w * self._padding_percent)
            pad_h = int(h * self._padding_percent)
            self._main_layout.setContentsMargins(pad_w, pad_h, pad_w, pad_h)

    def duplicate_action_row(self):
        row = self.table.currentRow()
        if row < 0:
            return
        type_widget = self.table.cellWidget(row, 0)
        value_widget = self.table.cellWidget(row, 1)
        wait_item = self.table.item(row, 2)
        if not (type_widget and value_widget and wait_item):
            return
        type_ = type_widget.currentText()
        value = value_widget.currentText() if value_widget.isEnabled() else ""
        wait = wait_item.text() if wait_item else "0"
        # Insert new row below
        insert_row = row + 1
        self.table.insertRow(insert_row)
        new_type_combo = QComboBox()
        new_type_combo.addItems(["key", "mouse", "wait"])
        new_type_combo.setCurrentText(type_)
        self.table.setCellWidget(insert_row, 0, new_type_combo)
        key_options = [
            "up", "down", "left", "right", "enter", "space", "tab", "esc", "backspace", "delete", "home", "end", "pageup", "pagedown"
        ]
        key_options += [chr(i) for i in range(97, 123)]  # a-z
        key_options += [str(i) for i in range(0, 10)]   # 0-9
        mouse_options = ["left", "right", "middle"]
        new_value_combo = QComboBox()
        new_value_combo.setEditable(False)
        if type_ == "key":
            new_value_combo.addItems(key_options)
            new_value_combo.setCurrentText(value)
            new_value_combo.setEnabled(True)
        elif type_ == "mouse":
            new_value_combo.addItems(mouse_options)
            new_value_combo.setCurrentText(value)
            new_value_combo.setEnabled(True)
        else:
            new_value_combo.setEnabled(False)
        self.table.setCellWidget(insert_row, 1, new_value_combo)
        new_wait_item = QTableWidgetItem(str(wait))
        self.table.setItem(insert_row, 2, new_wait_item)
        self.table.setCurrentCell(insert_row, 0)

        controls = QHBoxLayout()
        self.loop_spin = QSpinBox()
        self.loop_spin.setMinimum(1)
        self.loop_spin.setMaximum(999)
        self.loop_spin.setValue(1)
        self.loop_spin.setFont(font)
        controls.addWidget(QLabel("Loops:", font=font))
        controls.addWidget(self.loop_spin)

        self.start_btn = QPushButton("Start Macro")
        self.start_btn.setFont(font)
        self.start_btn.clicked.connect(self.start_macro)
        controls.addWidget(self.start_btn)

        self.stop_btn = QPushButton("Stop Macro")
        self.stop_btn.setFont(font)
        self.stop_btn.clicked.connect(self.stop_macro)
        self.stop_btn.setEnabled(False)
        controls.addWidget(self.stop_btn)

        layout.addLayout(controls)

        macro_controls = QHBoxLayout()
        self.macro_name_edit = QLineEdit()
        self.macro_name_edit.setPlaceholderText("Macro name")
        self.macro_name_edit.setFont(font)
        macro_controls.addWidget(self.macro_name_edit)

        self.save_btn = QPushButton("Save Macro")
        self.save_btn.setFont(font)
        self.save_btn.clicked.connect(self.save_macro)
        macro_controls.addWidget(self.save_btn)

        self.load_combo = QComboBox()
        self.load_combo.setFont(font)
        self.refresh_macro_list()
        macro_controls.addWidget(self.load_combo)

        self.load_btn = QPushButton("Load Macro")
        self.load_btn.setFont(font)
        self.load_btn.clicked.connect(self.load_macro)
        macro_controls.addWidget(self.load_btn)

        layout.addLayout(macro_controls)

        hotkey_controls = QHBoxLayout()
        self.hotkey_edit = QLineEdit(self.hotkey)
        self.hotkey_edit.setFont(font)
        hotkey_controls.addWidget(QLabel("Global Hotkey:", font=font))
        hotkey_controls.addWidget(self.hotkey_edit)
        self.hotkey_toggle_btn = QPushButton("Enable Hotkey")
        self.hotkey_toggle_btn.setFont(font)
        self.hotkey_toggle_btn.setCheckable(True)
        self.hotkey_toggle_btn.clicked.connect(self.toggle_hotkey)
        hotkey_controls.addWidget(self.hotkey_toggle_btn)
        layout.addLayout(hotkey_controls)

        self.runtime_label = QLabel("Loop Runtime: 0.00s")
        self.runtime_label.setFont(font)
        layout.addWidget(self.runtime_label)

        self.countdown_label = QLabel("")
        self.countdown_label.setFont(font)
        layout.addWidget(self.countdown_label)

        central.setLayout(layout)
        self.setCentralWidget(central)

    def add_action_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        type_combo = QComboBox()
        type_combo.addItems(["key", "mouse", "wait"])
        self.table.setCellWidget(row, 0, type_combo)

        key_options = [
            "up", "down", "left", "right", "enter", "space", "tab", "esc", "backspace", "delete", "home", "end", "pageup", "pagedown"
        ]
        key_options += [chr(i) for i in range(97, 123)]  # a-z
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
            value_widget = self.table.cellWidget(row, 1)
            value = value_widget.currentText() if value_widget and value_widget.isEnabled() else ""
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
        # Always use current table actions, not saved/loaded macros
        self.sequence = self.get_sequence()
        if not self.sequence:
            QMessageBox.warning(self, "No Actions", "Add actions to the macro before starting.")
            return
        self.stop_event.clear()
        loop_count = self.loop_spin.value()

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)

        self.countdown_label.setText("Switch to your target window! Macro will start in 3 seconds...")
        QApplication.processEvents()

        def do_countdown():
            for i in range(3, 0, -1):
                self.countdown_label.setText(f"Switch to your target window! Macro will start in {i} seconds...")
                QApplication.processEvents()
                time.sleep(1)
            self.countdown_label.setText("")
            QApplication.processEvents()
            self.runner = MacroRunner(self.sequence, loop_count, self.stop_event, self.update_runtime)
            self.runner.start()
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)

        threading.Thread(target=do_countdown, daemon=True).start()

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
        # Save table format: type, value (selected), wait
        actions = []
        for row in range(self.table.rowCount()):
            type_widget = self.table.cellWidget(row, 0)
            type_ = type_widget.currentText() if type_widget else "key"
            value_widget = self.table.cellWidget(row, 1)
            value = value_widget.currentText() if value_widget and value_widget.isEnabled() else ""
            wait_item = self.table.item(row, 2)
            wait = float(wait_item.text()) if wait_item and wait_item.text() else 0.0
            actions.append({"type": type_, "value": value, "wait": wait})
        path = os.path.join(MACROS_DIR, name + '.json')
        with open(path, 'w') as f:
            json.dump(actions, f, indent=2)
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
            actions = json.load(f)
        self.table.setRowCount(0)
        key_options = [
            "up", "down", "left", "right", "enter", "space", "tab", "esc", "backspace", "delete", "home", "end", "pageup", "pagedown"
        ]
        key_options += [chr(i) for i in range(97, 123)]  # a-z
        key_options += [str(i) for i in range(0, 10)]   # 0-9
        mouse_options = ["left", "right", "middle"]
        for action in actions:
            row = self.table.rowCount()
            self.table.insertRow(row)
            type_combo = QComboBox()
            type_combo.addItems(["key", "mouse", "wait"])
            type_combo.setCurrentText(action['type'])
            self.table.setCellWidget(row, 0, type_combo)
            value_combo = QComboBox()
            value_combo.setEditable(False)
            if action['type'] == 'key':
                value_combo.addItems(key_options)
                value_combo.setCurrentText(action['value'])
                value_combo.setEnabled(True)
            elif action['type'] == 'mouse':
                value_combo.addItems(mouse_options)
                value_combo.setCurrentText(action['value'])
                value_combo.setEnabled(True)
            else:
                value_combo.setEnabled(False)
            self.table.setCellWidget(row, 1, value_combo)
            wait_item = QTableWidgetItem(str(action.get('wait', 0)))
            self.table.setItem(row, 2, wait_item)

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
