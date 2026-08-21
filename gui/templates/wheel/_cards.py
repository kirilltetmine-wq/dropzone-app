from pathlib import Path

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QWidget

from core.theme import ACCENT_CYAN, ACCENT_LIME, BORDER_COLOR, CARD_LIGHT, DANGER_COLOR
from core.utils import _get_cached_pixmap
from ui_kit import RoundedLineEdit, ModernSlider, RoundedButton, DragHandle


class WheelMixinCards:
    """Prize card rendering and card border updates."""

    def render_prize_cards(self):
        for i in reversed(range(self.cards_layout.count())):
            item = self.cards_layout.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()
        self._prize_cards.clear()
        for i, item in enumerate(self.current_wheel_data):
            self.create_prize_card(i, item)

    def _update_card_borders(self):
        selected = self.wheel_widget.selected_indices()
        for idx, card in self._prize_cards.items():
            if idx in selected:
                card.setStyleSheet(
                    f"QFrame#cardDark {{  background-color: #0A0A0B; border: 2px solid {ACCENT_LIME}; border-radius: 30px; }} "
                )
            else:
                card.setStyleSheet(
                    "QFrame#cardDark { background-color: #0A0A0B; border: 1px solid #232326; border-radius: 30px; }"
                )

    def _on_wheel_selection_changed(self):
        self._update_card_borders()
        self._batch_value_warned = False
        self._batch_mode_active = False

    def create_prize_card(self, index, item):
        card = QFrame()
        card.setObjectName("cardDark")
        card.setStyleSheet(
            "QFrame#cardDark { background-color: #0A0A0B; border: 1px solid #232326; border-radius: 30px; }"
        )
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(8, 20, 20, 20)
        card_layout.setSpacing(6)
        self.cards_layout.addWidget(card)
        self._prize_cards[index] = card

        _prev_mp = card.mousePressEvent
        card.mousePressEvent = lambda event, idx=index, orig=_prev_mp: self._on_card_click(event, idx, orig)

        handle = DragHandle(index)
        handle.drag_started.connect(lambda idx: self.wheel_widget.set_drag_idx(idx))
        handle.drag_finished.connect(lambda idx: self.wheel_widget.set_drag_idx(-1))
        card_layout.addWidget(handle)

        content = QWidget()
        content.setStyleSheet("background-color: transparent;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.addWidget(content, 1)

        top_row = QHBoxLayout()
        content_layout.addLayout(top_row)

        name_entry = RoundedLineEdit()
        name_entry.setText(item['prize'])
        name_entry.set_colors(bg="transparent", border="transparent")
        name_entry.setMaxLength(16)
        if hasattr(self, '_config_max_name_length'):
            name_entry.setMaxLength(self._config_max_name_length)
        name_entry.textChanged.connect(lambda text, idx=index: self.update_and_sync(idx, 'prize', text))
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
        color_btn.clicked.connect(lambda checked, idx=index, btn=color_btn: self._on_color_btn(idx, btn))
        top_row.addWidget(color_btn)

        bot_row = QHBoxLayout()
        content_layout.addLayout(bot_row)

        val_entry = RoundedLineEdit()
        val_entry.setText(str(round(item['chance'], 1)))
        val_entry.setMaximumWidth(80)
        val_entry.set_colors(bg="transparent", border="transparent")
        val_entry.textChanged.connect(lambda text, idx=index: self._sync_val_from_entry(idx, text))
        bot_row.addWidget(val_entry)

        slider = ModernSlider()
        slider.setValue(item['chance'])
        slider.valueChanged.connect(lambda v, idx=index, entry=val_entry: self._on_slider_change(idx, v, entry))
        slider.dragStarted.connect(lambda idx=index: self._on_slider_drag_start(idx))
        slider.dragFinished.connect(lambda: self._on_slider_drag_finish())
        bot_row.addWidget(slider, 1)

        del_btn = RoundedButton("X")
        del_btn.setFixedSize(40, 40)
        del_btn.set_colors(bg="transparent", text=DANGER_COLOR, border="transparent", hover_bg=CARD_LIGHT)
        del_btn.clicked.connect(lambda checked, idx=index: self._on_delete_btn(idx))
        bot_row.addWidget(del_btn)

        self._update_card_borders()