"""
ui_kit_windows — окна и заголовки
  U038: TitleBar(parent) — заголовок окна (встроенная реализация)
  U039-U041B: Импортируются из оригинальных gui-файлов (восстановлены из бэкапа)
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QFont
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton,
)

from core.theme import (
    BG_COLOR, CARD_COLOR, CARD_LIGHT,
    TEXT_MAIN, BORDER_COLOR, DANGER_COLOR, FONT_FAMILY,
)

# ============================================================================
#                    U038: TitleBar (встроенная реализация)
# ============================================================================

class TitleBar(QWidget):
    def __init__(self, parent=None, title_text="", show_minimize=True, show_maximize=True, show_close=True):
        super().__init__(parent)
        self._parent_window = parent
        self._dragging = False
        self._drag_start = None
        self._title = title_text
        self.setFixedHeight(38)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.ArrowCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 0, 0)
        layout.setSpacing(0)

        self._title_label = QLabel(title_text)
        self._title_label.setStyleSheet(f"""
            color: {TEXT_MAIN};
            font-size: 12px;
            font-weight: 600;
            font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;
            background: transparent;
            padding: 0;
        """)
        self._title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        layout.addWidget(self._title_label)
        layout.addStretch(1)

        btn_size = 46
        self._min_btn = None
        self._max_btn = None
        self._close_btn = None

        if show_minimize:
            self._min_btn = QPushButton("—")
            self._min_btn.setFixedSize(btn_size, 38)
            self._min_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._min_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; border: none;
                    color: {TEXT_MAIN}; font-size: 16px; font-weight: bold;
                    font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;
                }}
                QPushButton:hover {{ background: {CARD_LIGHT}; }}
            """)
            self._min_btn.clicked.connect(self._on_minimize)
            layout.addWidget(self._min_btn)

        if show_maximize:
            self._max_btn = QPushButton("□")
            self._max_btn.setFixedSize(btn_size, 38)
            self._max_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._max_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; border: none;
                    color: {TEXT_MAIN}; font-size: 14px; font-weight: bold;
                    font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;
                }}
                QPushButton:hover {{ background: {CARD_LIGHT}; }}
            """)
            self._max_btn.clicked.connect(self._on_maximize)
            layout.addWidget(self._max_btn)

        if show_close:
            self._close_btn = QPushButton("✕")
            self._close_btn.setFixedSize(btn_size, 38)
            self._close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._close_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; border: none;
                    color: {TEXT_MAIN}; font-size: 16px; font-weight: bold;
                    font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;
                }}
                QPushButton:hover {{ background: {DANGER_COLOR}; }}
            """)
            self._close_btn.clicked.connect(self._on_close)
            layout.addWidget(self._close_btn)

    def set_title(self, text):
        self._title = text
        self._title_label.setText(text)

    def _on_minimize(self):
        if self._parent_window:
            self._parent_window.showMinimized()

    def _on_maximize(self):
        if self._parent_window:
            if self._parent_window.isMaximized():
                self._parent_window.showNormal()
                if self._max_btn:
                    self._max_btn.setText("□")
            else:
                self._parent_window.showMaximized()
                if self._max_btn:
                    self._max_btn.setText("❐")

    def _on_close(self):
        if self._parent_window:
            self._parent_window.close()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_start = event.globalPosition().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        if self._dragging and self._drag_start and self._parent_window:
            if self._parent_window.isMaximized():
                self._parent_window.showNormal()
            delta = event.globalPosition().toPoint() - self._drag_start
            self._drag_start = event.globalPosition().toPoint()
            pos = self._parent_window.pos()
            self._parent_window.move(pos.x() + delta.x(), pos.y() + delta.y())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._dragging:
            self._dragging = False
            self._drag_start = None
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def mouseDoubleClickEvent(self, event):
        if self._max_btn and self._parent_window:
            self._on_maximize()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#0A0A0B"))
        painter.end()

# ============================================================================
#  U039-U041B: SplashScreen, DetachableSection, DetachablePanel,
#              DetachedWindow, DetachedConfigWindow
#  Импортируются из оригинальных gui-файлов (восстановлены из бэкапа)
# ============================================================================

from gui.splash import SplashScreen
from gui.detach import (
    DetachableSection,
    DetachablePanel,
    DetachedWindow,
    DetachedConfigWindow,
    _PanelDragHandle,
)

# ============================================================================
#                           АЛИАСЫ
# ============================================================================

U038 = TitleBar
U039 = SplashScreen
U040 = DetachedWindow
U041 = DetachableSection
U041B = DetachablePanel
U040B = DetachedConfigWindow