import random

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QDialog

from core.theme import ACCENT_CYAN
from ui_kit import ModernItemPicker, DeleteConfirmDialog


class WheelMixinItems:
    """Prize item CRUD: add, delete (single/batch), reorder, balance chances."""

    def add_prize_item(self):
        if self._random_color_mode:
            new_color = f'#{random.randint(0,255):02X}{random.randint(0,255):02X}{random.randint(0,255):02X}'
        elif self._general_color_mode:
            new_color = self._general_color_value
        else:
            new_color = ACCENT_CYAN
        new_item = {"prize": f"PRIZE {len(self.current_wheel_data)+1}", "chance": 10, "color": new_color}
        self.current_wheel_data.append(new_item)
        self.balance_chances_equally()
        self.save_silently()

    def _on_card_click(self, event, idx, orig):
        ctrl = event.modifiers() & Qt.KeyboardModifier.ControlModifier
        if ctrl:
            selected = self.wheel_widget.selected_indices()
            if idx in selected:
                selected.discard(idx)
            else:
                selected.add(idx)
            self.wheel_widget.set_selected_indices(selected)
        else:
            orig(event)

    def _on_color_btn(self, idx, btn):
        selected = self.wheel_widget.selected_indices()
        if len(selected) > 1 and idx in selected:
            item = self.current_wheel_data[idx]
            initial = item.get('color', ACCENT_CYAN)
            initial_image = item.get('image', None)
            picker = ModernItemPicker(self, initial, initial_image, cell_type="wheel")
            if picker.exec() == QDialog.DialogCode.Accepted:
                ptype, pval = picker.result
                self.auto_toggle.set_checked(False)
                self.auto_color_var = False
                ep = picker.editor_params
                for si in selected:
                    if si < len(self.current_wheel_data):
                        if ptype == 'color':
                            self.current_wheel_data[si]['color'] = pval
                            self.current_wheel_data[si].pop('image', None)
                            self.current_wheel_data[si].pop('img_ox', None)
                            self.current_wheel_data[si].pop('img_oy', None)
                            self.current_wheel_data[si].pop('img_sx', None)
                            self.current_wheel_data[si].pop('img_sy', None)
                        else:
                            self.current_wheel_data[si]['image'] = pval
                            self.current_wheel_data[si]['color'] = initial
                            self.current_wheel_data[si]['img_ox'] = ep['ox']
                            self.current_wheel_data[si]['img_oy'] = ep['oy']
                            self.current_wheel_data[si]['img_sx'] = ep['sx']
                            self.current_wheel_data[si]['img_sy'] = ep['sy']
                self.render_prize_cards()
                self.wheel_widget.set_segments(self.current_wheel_data)
                self.save_silently()
        else:
            self.pick_item_color(idx, self.current_wheel_data[idx].get('color', ACCENT_CYAN), btn)

    def _on_delete_btn(self, idx):
        selected = self.wheel_widget.selected_indices()
        if len(selected) > 1 and idx in selected:
            self._batch_delete(selected)
        else:
            self._batch_delete({idx})

    def _batch_delete(self, indices):
        if not indices:
            return
        if len(self.current_wheel_data) - len(indices) < 1:
            return
        if DeleteConfirmDialog._skip_confirm:
            self._execute_delete(indices)
            return
        dialog = DeleteConfirmDialog(self, len(indices))
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._execute_delete(indices)

    def _execute_delete(self, indices):
        for idx in sorted(indices, reverse=True):
            if idx < len(self.current_wheel_data):
                self.current_wheel_data.pop(idx)
        self.balance_chances_equally()
        self.wheel_widget.set_selected_indices(set())
        self.save_silently()

    def remove_prize_item(self, index):
        self._batch_delete({index})

    def balance_chances_equally(self):
        if not self.current_wheel_data: return
        eq = 100.0 / len(self.current_wheel_data)
        for item in self.current_wheel_data:
            item['chance'] = round(eq, 2)
        if self.auto_color_var: self.apply_auto_colors_logic()
        self.render_prize_cards()
        self.wheel_widget.set_segments(self.current_wheel_data)
        self.save_silently()

    def _on_reorder_drop(self, from_idx, to_idx):
        if from_idx < 0 or to_idx < 0 or from_idx >= len(self.current_wheel_data) or to_idx >= len(self.current_wheel_data):
            return
        item = self.current_wheel_data.pop(from_idx)
        self.current_wheel_data.insert(to_idx, item)
        if self.auto_color_var:
            self.apply_auto_colors_logic()
        self.save_silently()
        self.wheel_widget.set_segments(self.current_wheel_data)
        QTimer.singleShot(0, self.render_prize_cards)