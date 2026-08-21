import random

from pathlib import Path

from PyQt6.QtCore import Qt, QSize

from PyQt6.QtGui import QIcon, QPixmap

from PyQt6.QtWidgets import QDialog

from core.theme import ACCENT_CYAN, BORDER_COLOR, CARD_LIGHT, DANGER_COLOR

from ui_kit import RoundedLineEdit, ModernSlider, RoundedButton

from ui_kit import DragHandle, ModernColorPicker, ModernItemPicker

from core.utils import _get_cached_pixmap


class CaseItemsMixin:

    def _case_add_prize(self):

        if not hasattr(self, '_case_prizes'):

            self._case_prizes = []

        if self._case_random_toggle.is_checked() if hasattr(self, '_case_random_toggle') else False:

            new_color = f'#{random.randint(0,255):02X}{random.randint(0,255):02X}{random.randint(0,255):02X}'

        elif self._case_general_color_mode if hasattr(self, '_case_general_color_mode') else False:

            new_color = self._case_general_color_value if hasattr(self, '_case_general_color_value') else '#00F5FF'

        else:

            new_color = '#00F5FF'

        self._case_prizes.append({'name': f'PRIZE {len(self._case_prizes) + 1}', 'chance': 10, 'color': new_color})

        self._case_balance_chances()

        self._case_save()

        self._case_strip.set_prizes(self._case_prizes)

        self._case_render_cards()

    def _case_on_random_toggle(self, checked):

        if checked:

            self._case_random_color_mode = True

            self._case_general_color_mode = False

            self._case_auto_color_var = False

            if hasattr(self, '_case_general_toggle'):

                self._case_general_toggle.set_checked(False)

            if hasattr(self, '_case_auto_toggle'):

                self._case_auto_toggle.set_checked(False)

            for item in self._case_prizes:

                item['color'] = f'#{random.randint(0,255):02X}{random.randint(0,255):02X}{random.randint(0,255):02X}'

            self._case_save()

            self._case_strip.set_prizes(self._case_prizes)

            self._case_render_cards()

        else:

            self._case_random_color_mode = False

    def _case_on_general_toggle(self, checked):

        if checked:

            initial = self._case_prizes[0]['color'] if self._case_prizes else '#00F5FF'

            picker = ModernColorPicker(self, initial)

            if picker.exec() == QDialog.DialogCode.Accepted and picker.result:

                self._case_general_color_mode = True

                self._case_general_color_value = picker.result

                self._case_random_color_mode = False

                self._case_auto_color_var = False

                if hasattr(self, '_case_random_toggle'):

                    self._case_random_toggle.set_checked(False)

                if hasattr(self, '_case_auto_toggle'):

                    self._case_auto_toggle.set_checked(False)

                for item in self._case_prizes:

                    item['color'] = picker.result

                self._case_save()

                self._case_strip.set_prizes(self._case_prizes)

                self._case_render_cards()

            else:

                self._case_general_toggle.set_checked(False)

        else:

            self._case_general_color_mode = False

    def _case_remove_prize(self, idx):

        if not hasattr(self, '_case_prizes') or len(self._case_prizes) <= 1:

            return

        self._case_prizes.pop(idx)

        self._case_balance_chances()

        self._case_save()

        self._case_strip.set_prizes(self._case_prizes)

        self._case_render_cards()

    def _case_equalize(self):

        self._case_balance_chances()

        self._case_save()

        self._case_strip.set_prizes(self._case_prizes)

        self._case_render_cards()

    def _case_balance_chances(self):

        prizes = self._case_prizes if hasattr(self, '_case_prizes') else []

        if not prizes:

            return

        equal = 100.0 / len(prizes)

        for p in prizes:

            p['chance'] = equal

        self._case_apply_auto_colors()

    def _case_apply_auto_colors(self):

        prizes = self._case_prizes if hasattr(self, '_case_prizes') else []

        if not prizes:

            return

        max_ch = max(p['chance'] for p in prizes) if prizes else 1

        for p in prizes:

            ratio = p['chance'] / max_ch if max_ch > 0 else 0.5

            r = int(0 + ratio * 204)

            g = int(245 * ratio + (1-ratio)*50)

            b = int(255 * (1-ratio))

            p['color'] = f'#{r:02x}{g:02x}{b:02x}'

    def _case_on_auto_color_toggle(self, checked):

        self._case_auto_color_var = checked

        if checked:

            self._case_apply_auto_colors()

            self._case_save()

            self._case_strip.set_prizes(self._case_prizes)

            self._case_render_cards()

    def _case_update_and_sync(self, index, key, value):

        if hasattr(self, '_case_prizes') and index < len(self._case_prizes):

            self._case_prizes[index][key] = value

            self._case_save()

            self._case_strip.set_prizes(self._case_prizes)

    def _case_on_color_btn(self, idx, btn):

        if not hasattr(self, '_case_prizes') or idx >= len(self._case_prizes):

            return

        item = self._case_prizes[idx]

        initial = item.get('color', ACCENT_CYAN)

        initial_image = item.get('image', None)

        picker = ModernItemPicker(self, initial, initial_image, cell_type="case")

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

            self._case_auto_toggle.set_checked(False)

            self._case_save()

            self._case_strip.set_prizes(self._case_prizes)

            self._case_render_cards()

    def _case_on_delete_btn(self, idx):

        self._case_remove_prize(idx)

    def _case_on_slider_change(self, index, value, entry):

        entry.blockSignals(True)

        entry.setText(f"{value:.1f}")

        entry.blockSignals(False)

        if hasattr(self, '_case_prizes') and index < len(self._case_prizes):

            self._case_prizes[index]['chance'] = value

            if self._case_auto_color_var if hasattr(self, '_case_auto_color_var') else False:

                self._case_apply_auto_colors()

            self._case_save()

            self._case_strip.set_prizes(self._case_prizes)

    def _case_sync_val_from_entry(self, index, text):

        try:

            val = float(text)

            if 0 <= val <= 100 and hasattr(self, '_case_prizes') and index < len(self._case_prizes):

                self._case_prizes[index]['chance'] = val

                if self._case_auto_color_var if hasattr(self, '_case_auto_color_var') else False:

                    self._case_apply_auto_colors()

                self._case_save()

                self._case_strip.set_prizes(self._case_prizes)

        except:

            pass