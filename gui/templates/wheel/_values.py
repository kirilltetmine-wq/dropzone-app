from PyQt6.QtWidgets import QDialog

from core.storage import Storage
from ui_kit import BatchValueDialog


class WheelMixinValues:
    """Value/slider/chance management and silent save."""

    def _sync_val_from_entry(self, index, text):
        try:
            val = float(text)
            if 0 <= val <= 100:
                self._apply_batch_value(index, val)
        except:
            pass

    def _on_slider_change(self, index, value, entry):
        entry.blockSignals(True)
        entry.setText(f"{value:.1f}")
        entry.blockSignals(False)
        self._apply_batch_value(index, value)

    def _on_slider_drag_start(self, idx):
        self.wheel_widget.set_show_labels(False)
        self._batch_mode_active = False
        selected = self.wheel_widget.selected_indices()
        if len(selected) > 1 and idx in selected:
            if not self._batch_value_warned and not ChatLotteryApp._skip_value_batch_warning:
                self._batch_value_warned = True
                dialog = BatchValueDialog(self)
                if dialog.exec() != QDialog.DialogCode.Accepted:
                    return
                if dialog.dont_show_again:
                    ChatLotteryApp._skip_value_batch_warning = True
            self._batch_mode_active = True

    def _on_slider_drag_finish(self):
        self._batch_mode_active = False
        self.wheel_widget.set_show_labels(True)

    def _apply_batch_value(self, index, value):
        selected = self.wheel_widget.selected_indices()
        is_multi = len(selected) > 1 and index in selected
        if is_multi and not self._batch_mode_active:
            if not self._batch_value_warned and not ChatLotteryApp._skip_value_batch_warning:
                self._batch_value_warned = True
                dialog = BatchValueDialog(self)
                if dialog.exec() != QDialog.DialogCode.Accepted:
                    return
                if dialog.dont_show_again:
                    ChatLotteryApp._skip_value_batch_warning = True
            self._batch_mode_active = True
        if self._batch_mode_active and is_multi:
            for si in selected:
                if si < len(self.current_wheel_data):
                    self.current_wheel_data[si]['chance'] = value
        else:
            self.current_wheel_data[index]['chance'] = value
        if self.auto_color_var:
            self.apply_auto_colors_logic()
        self.save_silently()
        self.wheel_widget.set_segments(self.current_wheel_data)

    def update_and_sync(self, index, key, value):
        if index < len(self.current_wheel_data):
            try:
                if key == 'chance':
                    value = float(value)
                self.current_wheel_data[index][key] = value
                if self.auto_color_var:
                    self.apply_auto_colors_logic()
                self.save_silently()
                self.wheel_widget.set_segments(self.current_wheel_data)
            except:
                pass

    def save_silently(self):
        name = self._get_current_wheel_name()
        if name:
            wheels = Storage.get_wheels()
            wheels[name] = self.current_wheel_data
            Storage.save_wheels(wheels)