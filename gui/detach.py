from PyQt6.QtCore import Qt, QEvent, pyqtSignal, QPoint, QSize, QRect, QPointF
from PyQt6.QtGui import QIcon, QColor, QPainter, QPen, QBrush
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QApplication, QMainWindow,
)

from core.theme import (
    BG_COLOR, CARD_COLOR, CARD_LIGHT, TEXT_MAIN, TEXT_SEC,
    BORDER_COLOR,
    MINUS_PATH, KVADRAT_PATH, KRESTIK_PATH, KRESTIK_WHITE_PATH,
)
from core.config import ConfigManager


class DetachablePanel(QWidget):
    """Wraps any widget and makes it detachable into a floating window.

    Usage:
        panel = DetachablePanel(sidebar_widget, "WHEEL CONFIGURATOR", parent)
        splitter.addWidget(panel)
    """

    panel_detached = pyqtSignal(object, bool)

    def __init__(self, content, title="Panel", parent=None):
        super().__init__(parent)
        self._content = content
        self._title = title
        self._detached = False
        self._detached_window = None

        self.setStyleSheet("background: transparent;")

        # Stack: content + drag handle overlay
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._slot = QWidget()
        self._slot.setStyleSheet("background: transparent;")
        slot_layout = QVBoxLayout(self._slot)
        slot_layout.setContentsMargins(0, 0, 0, 0)
        slot_layout.setSpacing(0)
        slot_layout.addWidget(content)
        layout.addWidget(self._slot, 1)

        # Drag handle with 3 dots — overlaid in top-left
        self._grip = _PanelDragHandle(self)
        self._grip.drag_detach.connect(self.detach)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._grip.move(8, 8)

    def detach(self):
        if self._detached:
            return
        self._detached = True

        content_size = self._content.size()

        self._slot.layout().removeWidget(self._content)
        self._content.setParent(None)
        self._content.hide()

        cursor_pos = self.cursor().pos()
        global_pos = self.mapToGlobal(cursor_pos)

        self._detached_window = DetachedConfigWindow(
            self._content, self._title, position=global_pos, content_size=content_size
        )
        self._detached_window.reattach_requested.connect(self._on_reattach)
        self._detached_window.show()

        self._slot.hide()
        self._grip.hide()
        self.panel_detached.emit(self, True)

    def _on_reattach(self, content):
        if not self._detached:
            return
        self._detached = False
        self._detached_window = None

        self._slot.show()
        self._grip.show()
        content.setParent(self._slot)
        self._slot.layout().addWidget(content)
        content.show()
        self.panel_detached.emit(self, False)

    @property
    def is_detached(self):
        return self._detached


class _PanelDragHandle(QWidget):
    """Three-dot drag handle that detaches the panel when dragged."""

    drag_detach = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._drag_start = None
        self.setFixedSize(36, 20)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setToolTip("Drag to detach")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#8E8E93"))
        dot_r = 3
        y = self.height() / 2
        spacing = 9
        total_w = spacing * 2
        start_x = (self.width() - total_w) / 2
        for i in range(3):
            cx = start_x + i * spacing
            painter.drawEllipse(QPointF(cx, y), dot_r, dot_r)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = event.globalPosition().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self._drag_start:
            delta = event.globalPosition().toPoint() - self._drag_start
            if delta.manhattanLength() > 8:
                self._drag_start = None
                self.setCursor(Qt.CursorShape.OpenHandCursor)
                self.drag_detach.emit()

    def mouseReleaseEvent(self, event):
        self._drag_start = None
        self.setCursor(Qt.CursorShape.OpenHandCursor)


class DetachedWindow(QWidget):
    """Floating window for main sections (e.g. LOTTERY, CHAT, WHEEL)."""

    reattach_requested = pyqtSignal(object)
    hovering_over_main = pyqtSignal(bool)

    def __init__(self, content, title="Section", parent=None, position=None):
        super().__init__(parent)

        self._content = content
        self._title = title
        self._drag_pos = None
        self._main_window = None
        self._resize_margin = 6
        self._resizing = False
        self._resize_edge = None
        self._resize_last_global = None

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setMinimumSize(500, 400)
        self.resize(800, 600)

        if position is not None:
            self.move(self._clamp_position(position - QPoint(400, 300)))

        self._target_opacity = 0.9
        try:
            cfg = ConfigManager()
            raw = str(cfg.get("general", "transparency", 90)).strip("\\ '")
            self._target_opacity = int(raw) / 100.0
        except Exception:
            pass

        self.setWindowOpacity(self._target_opacity)

        outer = QFrame(self)
        outer.setObjectName("detachedWindowOuter")
        outer.setStyleSheet(f"""
            QFrame#detachedWindowOuter {{
                background-color: {BG_COLOR};
                border: 1px solid {BORDER_COLOR};
            }}
        """)

        outer_layout = QVBoxLayout(outer)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        title_bar = QFrame()
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_COLOR};
                border: none;
                border-bottom: 1px solid {BORDER_COLOR};
            }}
        """)

        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(16, 0, 0, 0)
        title_layout.setSpacing(0)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            f"color: {TEXT_MAIN}; font-size: 13px; font-weight: 700;"
            f" background: transparent;"
        )
        title_layout.addWidget(title_lbl)
        title_layout.addStretch()

        btn_base = f"""
            #dtMinBtn, #dtMaxBtn, #dtCloseBtn {{
                background: transparent;
                border: none;
                border-radius: 0;
                padding: 0;
            }}
            #dtMinBtn:hover, #dtMaxBtn:hover {{
                background: {CARD_COLOR};
            }}
        """

        min_btn = QPushButton()
        min_btn.setObjectName("dtMinBtn")
        min_btn.setIcon(QIcon(str(MINUS_PATH)))
        min_btn.setIconSize(QSize(16, 16))
        min_btn.setFixedSize(46, 40)
        min_btn.setStyleSheet(btn_base)
        min_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        title_layout.addWidget(min_btn)

        max_btn = QPushButton()
        max_btn.setObjectName("dtMaxBtn")
        max_btn.setIcon(QIcon(str(KVADRAT_PATH)))
        max_btn.setIconSize(QSize(16, 16))
        max_btn.setFixedSize(46, 40)
        max_btn.setStyleSheet(btn_base)
        max_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        title_layout.addWidget(max_btn)

        close_btn = QPushButton()
        close_btn.setObjectName("dtCloseBtn")
        close_btn.setIcon(QIcon(str(KRESTIK_PATH)))
        close_btn.setIconSize(QSize(16, 16))
        close_btn.setFixedSize(46, 40)
        close_btn.setStyleSheet(f"""
            #dtCloseBtn {{
                background: transparent;
                border: none;
                border-radius: 0;
                padding: 0;
            }}
            #dtCloseBtn:hover {{
                background: #E81123;
            }}
        """)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self._reattach)

        self._close_btn = close_btn
        close_btn.installEventFilter(self)
        title_layout.addWidget(close_btn)

        min_btn.clicked.connect(self.showMinimized)
        max_btn.clicked.connect(self._toggle_maximize)

        outer_layout.addWidget(title_bar)
        outer_layout.addWidget(content, 1)

        content.show()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(outer)

        title_bar.mousePressEvent = self._on_drag_press
        title_bar.mouseMoveEvent = self._on_drag_move
        title_bar.mouseReleaseEvent = self._on_drag_release

        self._outer = outer

        QApplication.instance().installEventFilter(self)

    def _get_resize_edge(self, pos):
        m = self._resize_margin
        r = self.rect()
        edges = set()
        if pos.x() <= m:
            edges.add('left')
        if pos.x() >= r.width() - m:
            edges.add('right')
        if pos.y() <= m:
            edges.add('top')
        if pos.y() >= r.height() - m:
            edges.add('bottom')
        return edges

    def _set_resize_cursor(self, edges):
        if not edges:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        elif 'left' in edges and 'top' in edges:
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif 'right' in edges and 'bottom' in edges:
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif 'left' in edges and 'bottom' in edges:
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif 'right' in edges and 'top' in edges:
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif 'left' in edges or 'right' in edges:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif 'top' in edges or 'bottom' in edges:
            self.setCursor(Qt.CursorShape.SizeVerCursor)

    def _find_main_window(self):
        if self._main_window is not None:
            try:
                if self._main_window.isVisible():
                    return self._main_window
            except RuntimeError:
                pass

        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, QMainWindow):
                self._main_window = widget
                return widget

        self._main_window = None
        return None

    def _is_over_main_tab_bar(self, cursor_global_pos):
        main_win = self._find_main_window()
        if not main_win or main_win.isMinimized():
            return False

        tab_bar = main_win.findChild(QFrame, "tabBar")
        if not tab_bar:
            return False

        tab_bar_rect = QRect(tab_bar.mapToGlobal(QPoint(0, 0)), tab_bar.size())
        tab_bar_rect.adjust(-20, -30, 20, 30)
        return tab_bar_rect.contains(cursor_global_pos)

    def eventFilter(self, obj, event):
        close_btn = getattr(self, '_close_btn', None)
        if close_btn is not None and obj is close_btn:
            if event.type() == QEvent.Type.Enter:
                close_btn.setIcon(QIcon(str(KRESTIK_WHITE_PATH)))
            elif event.type() == QEvent.Type.Leave:
                close_btn.setIcon(QIcon(str(KRESTIK_PATH)))
            return super().eventFilter(obj, event)

        if obj is not self and obj is not self._outer:
            try:
                p = obj.parent()
            except TypeError:
                return super().eventFilter(obj, event)
            is_child = False
            while p:
                if p is self or p is self._outer:
                    is_child = True
                    break
                p = p.parent()
            if not is_child:
                return super().eventFilter(obj, event)

        t = event.type()
        if t == QEvent.Type.MouseMove:
            global_pos = event.globalPosition().toPoint()
            if self._resizing and self._resize_edge is not None:
                delta = global_pos - self._resize_last_global
                self._resize_last_global = global_pos
                geom = self.geometry()
                x, y, w, h = geom.x(), geom.y(), geom.width(), geom.height()

                if 'left' in self._resize_edge:
                    new_x = x + delta.x()
                    new_w = w - delta.x()
                    if new_w >= self.minimumWidth():
                        x = new_x
                        w = new_w

                if 'right' in self._resize_edge:
                    new_w = w + delta.x()
                    if new_w >= self.minimumWidth():
                        w = new_w

                if 'top' in self._resize_edge:
                    new_y = y + delta.y()
                    new_h = h - delta.y()
                    if new_h >= self.minimumHeight():
                        y = new_y
                        h = new_h

                if 'bottom' in self._resize_edge:
                    new_h = h + delta.y()
                    if new_h >= self.minimumHeight():
                        h = new_h

                self.setGeometry(x, y, w, h)
                return True

            local_pos = self.mapFromGlobal(global_pos)
            if self.rect().contains(local_pos):
                edges = self._get_resize_edge(local_pos)
                self._set_resize_cursor(edges)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
            return super().eventFilter(obj, event)

        elif t == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                local_pos = self.mapFromGlobal(event.globalPosition().toPoint())
                edges = self._get_resize_edge(local_pos)
                if edges:
                    self._resizing = True
                    self._resize_edge = edges
                    self._resize_last_global = event.globalPosition().toPoint()
                    return True
            return super().eventFilter(obj, event)

        elif t == QEvent.Type.MouseButtonRelease:
            if event.button() == Qt.MouseButton.LeftButton and self._resizing:
                self._resizing = False
                self._resize_edge = None
                self._resize_last_global = None
                self.setCursor(Qt.CursorShape.ArrowCursor)
                return True
            return super().eventFilter(obj, event)

        return super().eventFilter(obj, event)

    def _toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def _clamp_position(self, pos):
        screen = self.screen()
        if screen:
            sg = screen.availableGeometry()
            pos.setX(max(sg.x() - self.width() + 40, min(pos.x(), sg.right() - 40)))
            pos.setY(max(sg.y(), min(pos.y(), sg.bottom() - 40)))
        return pos

    def _on_drag_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
            event.accept()

    def _on_drag_move(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            delta = event.globalPosition().toPoint() - self._drag_pos
            new_pos = self._clamp_position(self.pos() + delta)
            self.move(new_pos)
            self._drag_pos = event.globalPosition().toPoint()

            cursor_pos = event.globalPosition().toPoint()
            is_over = self._is_over_main_tab_bar(cursor_pos)
            self.hovering_over_main.emit(is_over)
            event.accept()

    def _on_drag_release(self, event):
        if self._drag_pos is not None:
            cursor_pos = event.globalPosition().toPoint()
            if self._is_over_main_tab_bar(cursor_pos):
                self.hovering_over_main.emit(False)
                self._reattach()
                event.accept()
                return
        self._drag_pos = None
        event.accept()

    def _reattach(self):
        self.reattach_requested.emit(self._content)
        self.close()

    def closeEvent(self, event):
        self._reattach()
        event.accept()


class DetachedConfigWindow(QWidget):
    """Floating window for configurator panels — rounded, matches sidebar look 1:1."""

    reattach_requested = pyqtSignal(object)

    def __init__(self, content, title="Config", parent=None, position=None, content_size=None):
        super().__init__(parent)
        self._content = content
        self._title = title
        self._drag_pos = None

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        if content_size and content_size.width() > 0:
            w = content_size.width()
            h = content_size.height()
        else:
            hint = content.sizeHint()
            w = max(hint.width(), 280)
            h = max(hint.height(), 300)
        self.setMinimumSize(280, 200)
        self.resize(w + 20, h + 20)

        if position is not None:
            self.move(self._clamp_position(position - QPoint(self.width() // 2, self.height() // 2)))

        self._target_opacity = 0.9
        try:
            cfg = ConfigManager()
            raw = str(cfg.get("general", "transparency", 90)).strip("\\ '")
            self._target_opacity = int(raw) / 100.0
        except Exception:
            pass
        self.setWindowOpacity(self._target_opacity)

        # Single rounded card — exact match for sidebar card (black background, gray buttons)
        card = QFrame(self)
        card.setObjectName("detachedConfigCard")
        card.setStyleSheet(f"""
            QFrame#detachedConfigCard {{
                background-color: {BG_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 20px;
            }}
            QFrame#detachedConfigCard QPushButton {{
                background-color: {CARD_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
                color: {TEXT_MAIN};
            }}
            QFrame#detachedConfigCard QPushButton:hover {{
                background-color: {CARD_LIGHT};
            }}
            QFrame#detachedConfigCard QPushButton#dtConfigCloseBtn {{
                background: transparent;
                border: none;
            }}
            QFrame#detachedConfigCard QPushButton#dtConfigCloseBtn:hover {{
                background: #E81123;
            }}
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        # Top bar with 3-dot grip + close button
        top_bar = QFrame()
        top_bar.setFixedHeight(34)
        top_bar.setStyleSheet("background: transparent; border: none;")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(12, 0, 8, 0)
        top_layout.setSpacing(0)

        grip = _PanelDragHandle()
        grip.setToolTip("Drag to move")
        top_layout.addWidget(grip)
        top_layout.addStretch()

        close_btn = QPushButton()
        close_btn.setObjectName("dtConfigCloseBtn")
        close_btn.setIcon(QIcon(str(KRESTIK_PATH)))
        close_btn.setIconSize(QSize(14, 14))
        close_btn.setFixedSize(28, 28)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton#dtConfigCloseBtn {{
                background: transparent; border: none; color: {TEXT_SEC};
                font-size: 12px;
            }}
            QPushButton#dtConfigCloseBtn:hover {{ color: #FFFFFF; background: #E81123; border-radius: 6px; }}
        """)
        close_btn.clicked.connect(self._reattach)
        top_layout.addWidget(close_btn)

        card_layout.addWidget(top_bar)
        card_layout.addWidget(content, 1)

        content.show()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(card)

        # Draggable via grip & top_bar
        top_bar.mousePressEvent = self._on_drag_press
        top_bar.mouseMoveEvent = self._on_drag_move
        top_bar.mouseReleaseEvent = self._on_drag_release
        grip.mousePressEvent = self._on_drag_press
        grip.mouseMoveEvent = self._on_drag_move
        grip.mouseReleaseEvent = self._on_drag_release

    def _clamp_position(self, pos):
        screen = self.screen()
        if screen:
            sg = screen.availableGeometry()
            pos.setX(max(sg.x() - self.width() + 40, min(pos.x(), sg.right() - 40)))
            pos.setY(max(sg.y(), min(pos.y(), sg.bottom() - 40)))
        return pos

    def _on_drag_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
            event.accept()

    def _on_drag_move(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self._clamp_position(self.pos() + delta))
            self._drag_pos = event.globalPosition().toPoint()
            event.accept()

    def _on_drag_release(self, event):
        self._drag_pos = None
        event.accept()

    def _reattach(self):
        self.reattach_requested.emit(self._content)
        self.close()

    def closeEvent(self, event):
        self._reattach()
        event.accept()


class DetachableSection(QWidget):

    section_detached = pyqtSignal(object, bool)

    def __init__(self, content, title="Section", parent=None):
        super().__init__(parent)

        self._content = content
        self._title = title
        self._detached = False
        self._detached_window = None

        self.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._slot = QWidget()
        self._slot.setStyleSheet("background: transparent;")

        slot_layout = QVBoxLayout(self._slot)
        slot_layout.setContentsMargins(0, 0, 0, 0)
        slot_layout.setSpacing(0)
        slot_layout.addWidget(content)

        layout.addWidget(self._slot, 1)

    def _detach(self, pos=None):
        if self._detached:
            return

        self._detached = True
        self._drag_start = None

        self._slot.layout().removeWidget(self._content)
        self._content.setParent(None)
        self._content.hide()

        self._detached_window = DetachedWindow(self._content, self._title, position=pos)
        self._detached_window.reattach_requested.connect(self._on_reattach)
        self._detached_window.hovering_over_main.connect(self._on_hover_over_main)
        self._detached_window.show()

        self._slot.hide()
        self.section_detached.emit(self, True)

    def _on_reattach(self, content):
        if not self._detached:
            return

        self._detached = False
        self._detached_window = None

        self._slot.show()
        content.setParent(self._slot)
        self._slot.layout().addWidget(content)
        content.show()

        self.section_detached.emit(self, False)

    def _on_hover_over_main(self, hovering):
        main_win = self.window()
        if main_win and hasattr(main_win, '_highlight_tab_bar'):
            if hovering:
                main_win._highlight_tab_bar()
            else:
                main_win._unhighlight_tab_bar()

    @property
    def is_detached(self):
        return self._detached
