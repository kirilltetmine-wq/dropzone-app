from pathlib import Path

from PyQt6.QtCore import Qt, QSize

from PyQt6.QtGui import QIcon, QPixmap

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QWidget

from core.theme import BORDER_COLOR, ACCENT_CYAN, CARD_LIGHT, DANGER_COLOR

from ui_kit import RoundedLineEdit, ModernSlider, RoundedButton

from ui_kit import DragHandle

from core.utils import _get_cached_pixmap


class CaseUIMixin:

    def _on_case_selected(self, idx):

        if hasattr(self, '_case_data') and self._case_data:

            keys = list(self._case_data.keys())

            if 0 <= idx < len(keys):

                self._case_prizes = self._case_data[keys[idx]]

            else:

                self._case_prizes = []

        else:

            self._case_prizes = []

        if self._case_opened:

            self._case_strip.set_prizes(self._case_prizes)

            self._case_update_glow()

        self._case_render_cards()

    def _case_render_cards(self):

        if not hasattr(self, '_case_cards_layout'):

            return

        for i in reversed(range(self._case_cards_layout.count())):

            item = self._case_cards_layout.itemAt(i)

            if item and item.widget():

                item.widget().deleteLater()

        prizes = self._case_prizes if hasattr(self, '_case_prizes') else []

        for i, p in enumerate(prizes):

            self._case_create_card(i, p)

    def _case_create_card(self, index, item):

        card = QFrame()

        card.setObjectName("cardDark")

        card.setStyleSheet(

            "QFrame#cardDark { background-color: #0A0A0B; border: 1px solid #232326; border-radius: 30px; }"

        )

        card_layout = QHBoxLayout(card)

        card_layout.setContentsMargins(8, 20, 20, 20)

        card_layout.setSpacing(6)

        self._case_cards_layout.addWidget(card)

        handle = DragHandle(index)

        card_layout.addWidget(handle)

        content = QWidget()

        content.setStyleSheet("background-color: transparent;")

        content_layout = QVBoxLayout(content)

        content_layout.setContentsMargins(0, 0, 0, 0)

        card_layout.addWidget(content, 1)

        top_row = QHBoxLayout()

        content_layout.addLayout(top_row)

        name_entry = RoundedLineEdit()

        name_entry.setText(item.get('name', 'PRIZE'))

        name_entry.set_colors(bg="transparent", border="transparent")

        name_entry.setMaxLength(16)

        if hasattr(self, '_config_max_name_length'):

            name_entry.setMaxLength(self._config_max_name_length)

        name_entry.textChanged.connect(lambda text, idx=index: self._case_update_and_sync(idx, 'name', text))

        top_row.addWidget(name_entry, 1)

        color_btn = RoundedButton("", card)

        color_btn.setFixedSize(40, 30)

        img_path = item.get('image', None)

        if img_path and Path(img_path).exists():

            pix = _get_cached_pixmap(img_path)

            if pix:

                icon = QIcon(pix.scaled(36, 26, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

                color_btn.setIcon(icon)

                color_btn.setIconSize(QSize(36, 26))

                color_btn.set_colors(bg="transparent", border=BORDER_COLOR, hover_border="#FFFFFF")

            else:

                color_btn.set_colors(bg=item.get('color', ACCENT_CYAN), border=BORDER_COLOR, hover_border="#FFFFFF")

        else:

            color_btn.set_colors(bg=item.get('color', ACCENT_CYAN), border=BORDER_COLOR, hover_border="#FFFFFF")

        color_btn.clicked.connect(lambda checked, idx=index, btn=color_btn: self._case_on_color_btn(idx, btn))

        top_row.addWidget(color_btn)

        bot_row = QHBoxLayout()

        content_layout.addLayout(bot_row)

        val_entry = RoundedLineEdit()

        val_entry.setText(str(round(item.get('chance', 10), 1)))

        val_entry.setMaximumWidth(80)

        val_entry.set_colors(bg="transparent", border="transparent")

        val_entry.textChanged.connect(lambda text, idx=index: self._case_sync_val_from_entry(idx, text))

        bot_row.addWidget(val_entry)

        slider = ModernSlider()

        slider.setValue(item.get('chance', 10))

        slider.valueChanged.connect(lambda v, idx=index, entry=val_entry: self._case_on_slider_change(idx, v, entry))

        bot_row.addWidget(slider, 1)

        del_btn = RoundedButton("X")

        del_btn.setFixedSize(40, 40)

        del_btn.set_colors(bg="transparent", text=DANGER_COLOR, border="transparent", hover_bg=CARD_LIGHT)

        del_btn.clicked.connect(lambda checked, idx=index: self._case_on_delete_btn(idx))

        bot_row.addWidget(del_btn)