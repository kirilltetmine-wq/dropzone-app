import math

import random

import time

from PyQt6.QtCore import Qt, QTimer, QVariantAnimation, QEasingCurve

from PyQt6.QtGui import QIcon

from gui.widgets.case_strip import _CaseStripWidget


class CaseAnimationMixin:

    def _resize_case_image(self):

        if not hasattr(self, '_case_overlay'):

            return

        ow = self._case_overlay.width()

        oh = self._case_overlay.height()

        if ow < 50 or oh < 50:

            return

        tw = int(ow * 1.0)

        th = int(oh * 1.0)

        closed_orig = getattr(self, '_case_closed_pix_orig', None)

        open_orig = getattr(self, '_case_open_pix_orig', None)

        if closed_orig and not closed_orig.isNull():

            self._case_closed_pix = closed_orig.scaled(tw, th, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        if open_orig and not open_orig.isNull():

            self._case_open_pix = open_orig.scaled(tw, th, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        if self._case_opened and open_orig and not open_orig.isNull():

            self._case_img.setIcon(QIcon(self._case_open_pix))

            self._case_img.setIconSize(self._case_open_pix.size())

        elif not self._case_opened and closed_orig and not closed_orig.isNull():

            self._case_img.setIcon(QIcon(self._case_closed_pix))

            self._case_img.setIconSize(self._case_closed_pix.size())

        if hasattr(self, '_case_strip_wrapper'):

            margin = 40

            self._case_strip_wrapper.setGeometry(-margin, oh - 110, ow + 2 * margin, 110)

        if hasattr(self, '_case_glow'):

            glow_size = int(min(ow, oh) * 0.55)

            gx = (ow - glow_size) // 2

            gy = (oh - glow_size) // 2

            self._case_glow.setGeometry(gx, gy, glow_size, glow_size)

    def _case_toggle(self):

        self._case_opened = not self._case_opened

        if self._case_opened:

            if not self._case_open_pix.isNull():

                self._case_img.setIcon(QIcon(self._case_open_pix))

                self._case_img.setIconSize(self._case_open_pix.size())

            self._case_strip_wrapper.show()

            self._case_strip.set_prizes(self._case_prizes)

            self._case_result.show()

            self._case_btn_spacer.setFixedHeight(4)

            self._resize_case_image()

            self._case_update_glow()

        else:

            if not self._case_closed_pix.isNull():

                self._case_img.setIcon(QIcon(self._case_closed_pix))

                self._case_img.setIconSize(self._case_closed_pix.size())

            self._case_strip_wrapper.hide()

            self._case_glow.hide()

            self._case_result.hide()

            self._case_btn_spacer.setFixedHeight(0)

    def _case_update_glow(self):

        if not self._case_opened:

            self._case_glow.hide()

            return

        win = self._case_strip.get_winner(self._case_strip_wrapper.width())

        if win:

            c = win['color']

            self._case_result.setText(win['name'])

            self._case_result.setStyleSheet(

                f"font-size: 24px; font-weight: 800; letter-spacing: 2px; color: {c};"

            )

            self._case_result.show()

            r, g, b = int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)

            self._case_glow.setStyleSheet(

                f"QFrame {{  background-color: rgba({r},{g},{b},120); border-radius: 500px; border: none; }} "

            )

            self._case_glow.show()

    def _case_spin(self):

        if self._case_is_spinning:

            return

        prizes = self._case_prizes if hasattr(self, '_case_prizes') else []

        if not prizes:

            return

        if not self._case_opened:

            self._case_spin_btn.setEnabled(False)

            self._case_is_spinning = True

            orig_pos = self._case_img.pos()

            shake_anim = QVariantAnimation(self)

            shake_anim.setDuration(600)

            shake_anim.setStartValue(0.0)

            shake_anim.setEndValue(1.0)

            def on_shake(val):

                t = val * 8 * math.pi

                amplitude = 15 * (1 - val)

                dx = int(math.sin(t) * amplitude)

                self._case_img.move(orig_pos.x() + dx, orig_pos.y())

            def after_shake():

                self._case_img.move(orig_pos)

                self._case_opened = True

                if not self._case_open_pix.isNull():

                    self._case_img.setIcon(QIcon(self._case_open_pix))

                    self._case_img.setIconSize(self._case_open_pix.size())

                self._case_btn_spacer.setFixedHeight(4)

                self._resize_case_image()

                self._case_glow.hide()

                self._case_strip_wrapper.hide()

                self._case_result.hide()

                QTimer.singleShot(1000, _fade_in_glow)

            def _fade_in_glow():

                self._case_strip.set_prizes(self._case_prizes)

                win = self._case_strip.get_winner(self._case_strip_wrapper.width())

                if win:

                    c = win['color']

                    self._case_result.setText(win['name'])

                    self._case_result.setStyleSheet(

                        f"font-size: 24px; font-weight: 800; letter-spacing: 2px; color: {c};"

                    )

                    self._case_result.show()

                    r, g, b = int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)

                    self._case_glow.show()

                    glow_anim = QVariantAnimation(self)

                    glow_anim.setDuration(500)

                    glow_anim.setStartValue(0)

                    glow_anim.setEndValue(120)

                    glow_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

                    def on_glow_alpha(alpha):

                        self._case_glow.setStyleSheet(

                            f"QFrame {{  background-color: rgba({r},{g},{b},{alpha}); border-radius: 500px; border: none; }} "

                        )

                    glow_anim.valueChanged.connect(on_glow_alpha)

                    glow_anim.finished.connect(_after_glow_fade)

                    glow_anim.start(QVariantAnimation.DeletionPolicy.DeleteWhenStopped)

                else:

                    self._case_glow.show()

                    self._case_update_glow()

                    _after_glow_fade()

            def _after_glow_fade():

                self._resize_case_image()

                self._case_strip_wrapper.show()

                self._case_strip_wrapper.setFixedHeight(0)

                slide_anim = QVariantAnimation(self)

                slide_anim.setDuration(400)

                slide_anim.setStartValue(0.0)

                slide_anim.setEndValue(1.0)

                slide_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

                def on_slide(val):

                    self._case_strip_wrapper.setFixedHeight(int(110 * val))

                def after_slide():

                    self._case_strip_wrapper.setFixedHeight(110)

                    QTimer.singleShot(0, self._start_case_spin_animation)

                slide_anim.valueChanged.connect(on_slide)

                slide_anim.finished.connect(after_slide)

                slide_anim.start(QVariantAnimation.DeletionPolicy.DeleteWhenStopped)

            shake_anim.valueChanged.connect(on_shake)

            shake_anim.finished.connect(after_shake)

            shake_anim.start(QVariantAnimation.DeletionPolicy.DeleteWhenStopped)

            return

        self._start_case_spin_animation()

    def _start_case_spin_animation(self):

        prizes = self._case_prizes if hasattr(self, '_case_prizes') else []

        if not prizes:

            return

        self._case_is_spinning = True

        self._case_spin_btn.setEnabled(False)

        slot_w = _CaseStripWidget.SLOT_W

        n = len(prizes)

        wrapper_w = self._case_strip_wrapper.width()

        total_chance = sum(p.get('chance', 10) for p in prizes)

        r = random.uniform(0, total_chance)

        cum = 0

        target_idx = 0

        for i, p in enumerate(prizes):

            cum += p.get('chance', 10)

            if r <= cum:

                target_idx = i

                break

        cycles_offset = random.randint(10, 18) * n

        target_idx += cycles_offset

        target_offset = target_idx * slot_w - wrapper_w / 2 + slot_w / 2

        start_offset = self._case_strip._offset

        min_cells = 30

        min_scroll = min_cells * slot_w

        scroll_distance = target_offset - start_offset

        if scroll_distance < min_scroll:

            extra_cycles = int(math.ceil((min_scroll - scroll_distance) / (n * slot_w))) + 2

            target_idx += extra_cycles * n

            target_offset = target_idx * slot_w - wrapper_w / 2 + slot_w / 2

        duration_ms = 5500

        t0 = time.time()

        self._case_anim_timer = QTimer(self)

        self._case_anim_timer.setInterval(16)

        def anim_step():

            elapsed = time.time() - t0

            t = min(elapsed / (duration_ms / 1000.0), 1.0)

            if t < 0.2:

                eased = t * 5.0 * 0.4

            else:

                eased = 0.4 + 0.6 * (1.0 - pow(1.0 - (t - 0.2) / 0.8, 5.0))

            self._case_strip.scroll_to(int(start_offset + (target_offset - start_offset) * eased))

            self._case_update_glow()

            if t >= 1.0:

                self._case_anim_timer.stop()

                self._case_strip.scroll_to(int(target_offset))

                actual_idx = target_idx % n

                self._case_last_prize = prizes[actual_idx].get('name', 'Prize')

                winner_name = self._case_winner_entry.text().strip() if hasattr(self, '_case_winner_entry') else ""

                if winner_name:

                    self._case_confirm_btn.setVisible(True)

                self._case_is_spinning = False

                self._case_spin_btn.setEnabled(True)

                self._case_update_glow()

        self._case_anim_timer.timeout.connect(anim_step)

        self._case_anim_timer.start()