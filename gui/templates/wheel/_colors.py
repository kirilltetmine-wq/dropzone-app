import random

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QDialog

from core.theme import ACCENT_CYAN, BORDER_COLOR
from core.utils import _get_cached_pixmap
from ui_kit import ModernColorPicker, ModernItemPicker


class WheelMixinColors:
    """Color management: auto, random, general, and per-item color picking."""

    def on_auto_color_toggle(self, checked):
        self.auto_color_var = checked
        if checked:
            self.apply_auto_colors_logic()
            self.render_prize_cards()
            self.wheel_widget.set_segments(self.current_wheel_data)

    def apply_auto_colors_logic(self):
        if not self.current_wheel_data: return
        max_ch = max(item['chance'] for item in self.current_wheel_data) if self.current_wheel_data else 1
        for item in self.current_wheel_data:
            ratio = item['chance'] / max_ch if max_ch > 0 else 0.5
            r = int(0 + ratio * 204)
            g = int(245 * ratio + (1-ratio)*50)
            b = int(255 * (1-ratio))
            item['color'] = f'#{r:02x}{g:02x}{b:02x}'

    def on_random_toggle(self, checked):
        if checked:
            self._random_color_mode = True
            self._general_color_mode = False
            self.general_toggle.set_checked(False)
            self.auto_toggle.set_checked(False)
            self.auto_color_var = False
            for item in self.current_wheel_data:
                item['color'] = f'#{random.randint(0,255):02X}{random.randint(0,255):02X}{random.randint(0,255):02X}'
            self.render_prize_cards()
            self.wheel_widget.set_segments(self.current_wheel_data)
            self.save_silently()
        else:
            self._random_color_mode = False

    def on_general_toggle(self, checked):
        if checked:
            initial = self.current_wheel_data[0]['color'] if self.current_wheel_data else ACCENT_CYAN
            picker = ModernColorPicker(self, initial)
            if picker.exec() == QDialog.DialogCode.Accepted and picker.result:
                self._general_color_mode = True
                self._general_color_value = picker.result
                self._random_color_mode = False
                self.random_toggle.set_checked(False)
                self.auto_toggle.set_checked(False)
                self.auto_color_var = False
                for item in self.current_wheel_data:
                    item['color'] = picker.result
                self.render_prize_cards()
                self.wheel_widget.set_segments(self.current_wheel_data)
                self.save_silently()
            else:
                self.general_toggle.set_checked(False)
        else:
            self._general_color_mode = False

    def pick_item_color(self, index, initial, btn):
        item = self.current_wheel_data[index]
        initial_image = item.get('image', None)
        picker = ModernItemPicker(self, initial, initial_image, cell_type="wheel")
        if picker.exec() == QDialog.DialogCode.Accepted:
            ptype, pval = picker.result
            if ptype == 'color':
                item['color'] = pval
                item.pop('image', None)
                item.pop('img_ox', None)
                item.pop('img_oy', None)
                item.pop('img_sx', None)
                item.pop('img_sy', None)
                btn.set_colors(bg=pval, border=BORDER_COLOR, hover_border="#FFFFFF")
                btn.setIcon(QIcon())
            else:
                item['image'] = pval
                item['color'] = initial
                ep = picker.editor_params
                item['img_ox'] = ep['ox']
                item['img_oy'] = ep['oy']
                item['img_sx'] = ep['sx']
                item['img_sy'] = ep['sy']
                pix = _get_cached_pixmap(pval)
                if pix:
                    icon = QIcon(pix.scaled(36, 26, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                    btn.setIcon(icon)
                    btn.setIconSize(QSize(36, 26))
                    btn.set_colors(bg="transparent", border=BORDER_COLOR, hover_border="#FFFFFF")
            self.auto_toggle.set_checked(False)
            self.auto_color_var = False
            self.render_prize_cards()
            self.wheel_widget.set_segments(self.current_wheel_data)
            self.save_silently()