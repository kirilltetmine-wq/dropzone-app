from core.theme import SUCCESS_COLOR
from core.storage import Storage
from ui_kit import ModernDialog, ask_string
from PyQt6.QtWidgets import QMessageBox, QDialog


class WheelMixinNavigation:
    """Wheel navigation, selection, CRUD (add/delete/rename), and list refresh."""

    def _prev_wheel(self):
        idx = self.wheel_combo.currentIndex()
        if idx < 0:
            idx = self.wheel_combo.count()
        idx = (idx - 1) % max(self.wheel_combo.count(), 1)
        self.wheel_combo.setCurrentIndex(idx)

    def _next_wheel(self):
        idx = self.wheel_combo.currentIndex()
        idx = (idx + 1) % max(self.wheel_combo.count(), 1)
        self.wheel_combo.setCurrentIndex(idx)

    def on_wheel_selected(self):
        idx = self.wheel_combo.currentIndex()
        if idx < 0: return
        wheels = Storage.get_wheels()
        names = list(wheels.keys())
        if idx >= len(names): return
        name = names[idx]
        self.current_wheel_data = wheels.get(name, [])
        self.render_prize_cards()
        self.wheel_widget.set_segments(self.current_wheel_data)

    def _get_current_wheel_name(self):
        idx = self.wheel_combo.currentIndex()
        if idx < 0: return ""
        wheels = Storage.get_wheels()
        names = list(wheels.keys())
        if idx >= len(names): return ""
        return names[idx]

    def add_wheel(self):
        name = ask_string(self, "NEW WHEEL", "Enter wheel name:", placeholder="E.g. Daily Bonus")
        if name:
            wheels = Storage.get_wheels()
            wheels[name] = [{"prize": "PRIZE 1", "chance": 100, "color": SUCCESS_COLOR}]
            Storage.save_wheels(wheels)
            self.refresh_wheels_list()
            wheels = Storage.get_wheels()
            names = list(wheels.keys())
            if name in names:
                self.wheel_combo.setCurrentIndex(names.index(name))
            self.on_wheel_selected()

    def delete_wheel(self):
        name = self._get_current_wheel_name()
        if name:
            dialog = ModernDialog(self, "DELETE", f"Permanently delete wheel '{name}'?")
            if dialog.exec() == QDialog.DialogCode.Accepted:
                wheels = Storage.get_wheels()
                if name in wheels:
                    del wheels[name]
                    Storage.save_wheels(wheels)
                    self.refresh_wheels_list()

    def rename_wheel(self):
        old_name = self._get_current_wheel_name()
        if not old_name:
            return
        new_name = ask_string(self, "RENAME WHEEL", "Enter new name:", placeholder=old_name)
        if new_name and new_name != old_name:
            wheels = Storage.get_wheels()
            if new_name in wheels:
                QMessageBox.warning(self, "ERROR", f"Wheel '{new_name}' already exists!")
                return
            if old_name in wheels:
                wheels[new_name] = wheels.pop(old_name)
                Storage.save_wheels(wheels)
                self.refresh_wheels_list()
                wheels = Storage.get_wheels()
                names = list(wheels.keys())
                if new_name in names:
                    self.wheel_combo.setCurrentIndex(names.index(new_name))
                self.on_wheel_selected()

    def refresh_wheels_list(self):
        wheels = Storage.get_wheels()
        names = list(wheels.keys())
        self.wheel_combo.blockSignals(True)
        self.wheel_combo.clear()
        if names:
            display_items = [f"{n} ({len(wheels[n])})" for n in names]
            self.wheel_combo.addItems(display_items)
            self.wheel_combo.setPopupData(wheels)
            self.wheel_combo.setCurrentIndex(0)
            self.on_wheel_selected()
        self.wheel_combo.blockSignals(False)
        if not names:
            self.current_wheel_data = []
            self.render_prize_cards()
            self.wheel_widget.set_segments([])