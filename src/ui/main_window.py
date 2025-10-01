import sys
import os
import json
import time
import threading
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QLabel, QMessageBox, QComboBox, QSpinBox,
    QTabWidget
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
        loop_counter = 0
        
        # Handle infinite loops vs fixed count
        while True:
            if self.stop_event.is_set():
                break
                
            # Check if we've reached the fixed loop count (if not infinite)
            if self.loop_count != float('inf') and loop_counter >= self.loop_count:
                break
                
            for action in self.sequence:
                if self.stop_event.is_set():
                    break
                    
                if action['type'] == 'key':
                    key = action.get('value', '')
                    hold_duration = action.get('hold', 0.1)
                    if key:
                        keyboard.press(key)
                        time.sleep(hold_duration)
                        keyboard.release(key)
                elif action['type'] == 'mouse':
                    btn = action.get('value', '')
                    hold_duration = action.get('hold', 0.1)
                    if btn:
                        pyautogui.mouseDown(button=btn)
                        time.sleep(hold_duration)
                        pyautogui.mouseUp(button=btn)
                elif action['type'] == 'wait':
                    time.sleep(action['value'])
                    
            loop_counter += 1
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
        
        # Define options once to avoid duplication
        self.key_options = [
            "up", "down", "left", "right", "enter", "space", "tab", "esc", 
            "backspace", "delete", "home", "end", "pageup", "pagedown"
        ]
        self.key_options += [chr(i) for i in range(97, 123)]  # a-z
        self.key_options += [str(i) for i in range(0, 10)]   # 0-9
        self.mouse_options = ["left", "right", "middle"]
        
        self.init_ui()

    def init_ui(self):
        scale = 1.62  # Increased by 1.2x (was 1.35)
        from PySide6.QtGui import QFont
        font = self.font()
        preferred_fonts = ["SF Pro Display", "San Francisco", "Segoe UI", "Arial"]
        for fam in preferred_fonts:
            font.setFamily(fam)
            test_font = QFont(fam)
            if test_font.family() == fam:
                break
        font.setPointSizeF(font.pointSizeF() * scale)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Create macro tab
        self.create_macro_tab(font)
        
        # Create config tab
        self.create_config_tab(font)

    def create_macro_tab(self, font):
        """Create the main macro editing and execution tab."""
        macro_widget = QWidget()
        layout = QVBoxLayout()
        macro_widget.setLayout(layout)

        # Macro table setup
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Type", "Value", "Hold (s)", "Wait (s)"])
        self.table.setFont(font)
        layout.addWidget(self.table)

        # Table controls
        table_controls = QHBoxLayout()
        add_btn = QPushButton("Add Action")
        add_btn.setFont(font)
        add_btn.clicked.connect(self.add_action_row)
        table_controls.addWidget(add_btn)

        duplicate_btn = QPushButton("Duplicate Action")
        duplicate_btn.setFont(font)
        duplicate_btn.clicked.connect(self.duplicate_action_row)
        table_controls.addWidget(duplicate_btn)

        remove_btn = QPushButton("Remove Selected")
        remove_btn.setFont(font)
        remove_btn.clicked.connect(self.remove_selected_row)
        table_controls.addWidget(remove_btn)
        
        layout.addLayout(table_controls)

        # Macro controls
        macro_controls = QHBoxLayout()
        
        self.start_btn = QPushButton("Start Macro")
        self.start_btn.setFont(font)
        self.start_btn.clicked.connect(self.start_macro)
        macro_controls.addWidget(self.start_btn)

        self.stop_btn = QPushButton("Stop Macro")
        self.stop_btn.setFont(font)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_macro)
        macro_controls.addWidget(self.stop_btn)

        # Loop controls with radio buttons
        from PySide6.QtWidgets import QRadioButton, QButtonGroup
        loop_controls = QVBoxLayout()
        
        self.loop_group = QButtonGroup()
        self.loop_until_stop = QRadioButton("Loop until stop")
        self.loop_until_stop.setFont(font)
        self.loop_until_stop.setChecked(True)  # Default option
        self.loop_group.addButton(self.loop_until_stop)
        loop_controls.addWidget(self.loop_until_stop)
        
        fixed_loop_layout = QHBoxLayout()
        self.loop_fixed_count = QRadioButton("Fixed loops:")
        self.loop_fixed_count.setFont(font)
        self.loop_group.addButton(self.loop_fixed_count)
        fixed_loop_layout.addWidget(self.loop_fixed_count)
        
        self.loop_spin = QSpinBox()
        self.loop_spin.setMinimum(1)
        self.loop_spin.setMaximum(1000)
        self.loop_spin.setValue(1)
        self.loop_spin.setFont(font)
        self.loop_spin.setEnabled(False)
        fixed_loop_layout.addWidget(self.loop_spin)
        
        # Connect radio button to enable/disable spin box
        self.loop_fixed_count.toggled.connect(self.loop_spin.setEnabled)
        
        loop_controls.addLayout(fixed_loop_layout)
        macro_controls.addLayout(loop_controls)

        layout.addLayout(macro_controls)

        # Status labels
        self.runtime_label = QLabel("Runtime: 0.0s")
        self.runtime_label.setFont(font)
        layout.addWidget(self.runtime_label)
        
        self.countdown_label = QLabel("")
        self.countdown_label.setFont(font)
        layout.addWidget(self.countdown_label)

        self.tab_widget.addTab(macro_widget, "Macro")

    def create_config_tab(self, font):
        """Create the configuration tab with save/load and hotkey settings."""
        config_widget = QWidget()
        layout = QVBoxLayout()
        config_widget.setLayout(layout)

        # Save/Load controls
        save_load_group = QVBoxLayout()
        save_load_group.addWidget(QLabel("Macro Management", font=font))
        
        save_load_controls = QHBoxLayout()
        save_load_controls.addWidget(QLabel("Name:", font=font))
        self.macro_name_edit = QLineEdit()
        self.macro_name_edit.setFont(font)
        save_load_controls.addWidget(self.macro_name_edit)

        save_btn = QPushButton("Save Macro")
        save_btn.setFont(font)
        save_btn.clicked.connect(self.save_macro)
        save_load_controls.addWidget(save_btn)

        save_load_group.addLayout(save_load_controls)

        # Load controls
        load_controls = QHBoxLayout()
        load_controls.addWidget(QLabel("Load:", font=font))
        self.load_combo = QComboBox()
        self.load_combo.setFont(font)
        load_controls.addWidget(self.load_combo)

        load_btn = QPushButton("Load Macro")
        load_btn.setFont(font)
        load_btn.clicked.connect(self.load_macro)
        load_controls.addWidget(load_btn)

        save_load_group.addLayout(load_controls)
        layout.addLayout(save_load_group)

        # Add separator
        layout.addWidget(QLabel(""))

        # Hotkey controls
        hotkey_group = QVBoxLayout()
        hotkey_group.addWidget(QLabel("Global Hotkey Settings", font=font))
        
        hotkey_controls = QHBoxLayout()
        hotkey_controls.addWidget(QLabel("Hotkey:", font=font))
        
        self.hotkey_edit = QLineEdit("ctrl+alt+m")
        self.hotkey_edit.setFont(font)
        hotkey_controls.addWidget(self.hotkey_edit)
        
        self.hotkey_toggle_btn = QPushButton("Enable Hotkey")
        self.hotkey_toggle_btn.setFont(font)
        self.hotkey_toggle_btn.setCheckable(True)
        self.hotkey_toggle_btn.clicked.connect(self.toggle_hotkey)
        hotkey_controls.addWidget(self.hotkey_toggle_btn)

        hotkey_group.addLayout(hotkey_controls)
        
        # Add hotkey help text
        help_label = QLabel("Use this hotkey to start/stop macros from anywhere.")
        help_label.setFont(font)
        help_label.setStyleSheet("color: gray;")
        hotkey_group.addWidget(help_label)
        
        layout.addLayout(hotkey_group)

        # Add stretch to push everything to the top
        layout.addStretch()

        self.tab_widget.addTab(config_widget, "Config")
        
        # Initialize macro list
        self.refresh_macro_list()



    def add_action_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Type combo box
        type_combo = QComboBox()
        type_combo.addItems(["key", "mouse", "wait"])
        type_combo.currentTextChanged.connect(lambda: self.update_value_combo(row))
        self.table.setCellWidget(row, 0, type_combo)

        # Value combo box
        value_combo = QComboBox()
        value_combo.setEditable(False)
        self.table.setCellWidget(row, 1, value_combo)

        # Hold time (for key/mouse actions)
        hold_item = QTableWidgetItem("0.1")
        self.table.setItem(row, 2, hold_item)
        
        # Wait time
        wait_item = QTableWidgetItem("0.1")
        self.table.setItem(row, 3, wait_item)
        
        # Update value combo options based on initial type
        self.update_value_combo(row)

    def duplicate_action_row(self):
        """Duplicate the currently selected action row."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select an action to duplicate.")
            return
            
        # Get data from selected row
        type_widget = self.table.cellWidget(current_row, 0)
        value_widget = self.table.cellWidget(current_row, 1)
        hold_item = self.table.item(current_row, 2)
        wait_item = self.table.item(current_row, 3)
        
        if not type_widget:
            return
            
        # Create new row
        new_row = current_row + 1
        self.table.insertRow(new_row)
        
        # Duplicate type combo
        new_type_combo = QComboBox()
        new_type_combo.addItems(["key", "mouse", "wait"])
        new_type_combo.setCurrentText(type_widget.currentText())
        new_type_combo.currentTextChanged.connect(lambda: self.update_value_combo(new_row))
        self.table.setCellWidget(new_row, 0, new_type_combo)
        
        # Duplicate value combo
        new_value_combo = QComboBox()
        new_value_combo.setEditable(False)
        self.table.setCellWidget(new_row, 1, new_value_combo)
        
        # Update value combo options and set current value
        self.update_value_combo(new_row)
        if value_widget and value_widget.isEnabled():
            new_value_combo.setCurrentText(value_widget.currentText())
        
        # Duplicate hold and wait times
        new_hold_item = QTableWidgetItem(hold_item.text() if hold_item else "0.1")
        self.table.setItem(new_row, 2, new_hold_item)
        
        new_wait_item = QTableWidgetItem(wait_item.text() if wait_item else "0.1")
        self.table.setItem(new_row, 3, new_wait_item)
        
        # Select the new row
        self.table.selectRow(new_row)

    def remove_selected_row(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)

    def update_value_combo(self, row):
        """Update the value combo box options based on the selected type."""
        type_widget = self.table.cellWidget(row, 0)
        value_widget = self.table.cellWidget(row, 1)
        hold_item = self.table.item(row, 2)
        wait_item = self.table.item(row, 3)

        if not type_widget or not value_widget or not hold_item or not wait_item:
            return

        action_type = type_widget.currentText()
        value_widget.clear()

        # Default: enable everything
        value_widget.setEnabled(True)
        hold_item.setFlags(hold_item.flags() | Qt.ItemIsEditable)
        wait_item.setFlags(wait_item.flags() | Qt.ItemIsEditable)

        if action_type == "key" or action_type == "mouse":
            # Enable value and hold, disable wait
            if action_type == "key":
                value_widget.addItems(self.key_options)
            else:
                value_widget.addItems(self.mouse_options)
            value_widget.setEnabled(True)
            hold_item.setFlags(hold_item.flags() | Qt.ItemIsEditable)
            wait_item.setFlags(wait_item.flags() & ~Qt.ItemIsEditable)
        elif action_type == "wait":
            # Enable wait, disable value and hold
            value_widget.setEnabled(False)
            hold_item.setFlags(hold_item.flags() & ~Qt.ItemIsEditable)
            wait_item.setFlags(wait_item.flags() | Qt.ItemIsEditable)

        # Update the table to reflect changes
        self.table.setItem(row, 2, hold_item)
        self.table.setItem(row, 3, wait_item)

    def get_sequence(self):
        sequence = []
        for row in range(self.table.rowCount()):
            type_widget = self.table.cellWidget(row, 0)
            type_ = type_widget.currentText() if type_widget else "key"
            
            value_widget = self.table.cellWidget(row, 1)
            value = value_widget.currentText() if value_widget and value_widget.isEnabled() else ""
            
            hold_item = self.table.item(row, 2)
            hold = float(hold_item.text()) if hold_item and hold_item.text() else 0.1
            
            wait_item = self.table.item(row, 3)
            wait = float(wait_item.text()) if wait_item and wait_item.text() else 0.1
            
            if type_ == "wait":
                # For wait actions, use the wait value as the delay time
                sequence.append({"type": "wait", "value": wait})
            else:
                # For key/mouse actions, include hold duration
                sequence.append({"type": type_, "value": value, "hold": hold})
                if wait > 0:
                    sequence.append({"type": "wait", "value": wait})
        
        return sequence

    def start_macro(self):
        # Always use current table actions, not saved/loaded macros
        self.sequence = self.get_sequence()
        if not self.sequence:
            QMessageBox.warning(self, "No Actions", "Add actions to the macro before starting.")
            return
        
        self.stop_event.clear()
        
        # Determine loop count based on radio button selection
        if self.loop_until_stop.isChecked():
            loop_count = float('inf')  # Infinite loops until stopped
        else:
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
        # Save table format: type, value, hold, wait
        actions = []
        for row in range(self.table.rowCount()):
            type_widget = self.table.cellWidget(row, 0)
            type_ = type_widget.currentText() if type_widget else "key"
            value_widget = self.table.cellWidget(row, 1)
            value = value_widget.currentText() if value_widget and value_widget.isEnabled() else ""
            hold_item = self.table.item(row, 2)
            hold = float(hold_item.text()) if hold_item and hold_item.text() else 0.1
            wait_item = self.table.item(row, 3)
            wait = float(wait_item.text()) if wait_item and wait_item.text() else 0.1
            actions.append({"type": type_, "value": value, "hold": hold, "wait": wait})
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
        for action in actions:
            row = self.table.rowCount()
            self.table.insertRow(row)
            type_combo = QComboBox()
            type_combo.addItems(["key", "mouse", "wait"])
            type_combo.setCurrentText(action['type'])
            type_combo.currentTextChanged.connect(lambda: self.update_value_combo(row))
            self.table.setCellWidget(row, 0, type_combo)
            value_combo = QComboBox()
            value_combo.setEditable(False)
            if action['type'] == 'key':
                value_combo.addItems(self.key_options)
                value_combo.setCurrentText(action['value'])
                value_combo.setEnabled(True)
            elif action['type'] == 'mouse':
                value_combo.addItems(self.mouse_options)
                value_combo.setCurrentText(action['value'])
                value_combo.setEnabled(True)
            else:
                value_combo.setEnabled(False)
            self.table.setCellWidget(row, 1, value_combo)
            
            # Handle hold column (backward compatibility for old saves)
            hold_item = QTableWidgetItem(str(action.get('hold', 0.1)))
            self.table.setItem(row, 2, hold_item)
            
            # Handle wait column (backward compatibility for old saves)
            wait_item = QTableWidgetItem(str(action.get('wait', 0.1)))
            self.table.setItem(row, 3, wait_item)

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
