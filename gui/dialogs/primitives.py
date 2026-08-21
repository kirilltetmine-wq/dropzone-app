from PyQt6.QtCore import Qt, QMimeData, pyqtSignal, QEvent, QObject
from PyQt6.QtGui import QDrag
from PyQt6.QtWidgets import QLabel, QWidget

class DragHandle(QLabel):
    drag_started = pyqtSignal(int)
    drag_finished = pyqtSignal(int)
    def __init__(self, index, parent=None):
        super().__init__("≡", parent)
        self._index = index
        self._drag_start = None
        self.setFixedWidth(24)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("""
            color: #8E8E93;
            font-size: 18px;
            font-weight: 700;
            background-color: transparent;
        """)
    def set_index(self, idx):
        self._index = idx
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self._drag_start:
            if (event.position().toPoint() - self._drag_start).manhattanLength() > 8:
                self.drag_started.emit(self._index)
                drag = QDrag(self)
                mime = QMimeData()
                mime.setText(str(self._index))
                drag.setMimeData(mime)
                drag.exec(Qt.DropAction.MoveAction)
                self.drag_finished.emit(self._index)
                self.setCursor(Qt.CursorShape.OpenHandCursor)
                self._drag_start = None
        super().mouseMoveEvent(event)
    def mouseReleaseEvent(self, event):
        self._drag_start = None
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        super().mouseReleaseEvent(event)

class DropContainer(QWidget):
    item_dropped = pyqtSignal(int, int)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._drag_over_idx = -1
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
    def dragMoveEvent(self, event):
        event.acceptProposedAction()
        pos_y = event.position().toPoint().y()
        self._drag_over_idx = self._pos_to_index(pos_y)
        self.update()
    def dragLeaveEvent(self, event):
        self._drag_over_idx = -1
        self.update()
    def dropEvent(self, event):
        if event.mimeData().hasText():
            from_idx = int(event.mimeData().text())
            pos_y = event.position().toPoint().y()
            to_idx = self._pos_to_index(pos_y)
            child_count = self._child_count()
            if to_idx > child_count - 1:
                to_idx = child_count - 1
            if to_idx < 0:
                to_idx = 0
            if from_idx != to_idx:
                self.item_dropped.emit(from_idx, to_idx)
            event.acceptProposedAction()
        self._drag_over_idx = -1
        self.update()
    def _pos_to_index(self, y):
        if self.layout() is None:
            return 0
        count = self.layout().count()
        if count == 0:
            return 0
        cumulative = 0
        child_heights = []
        for i in range(count):
            item = self.layout().itemAt(i)
            if item and item.widget():
                h = item.widget().height()
                child_heights.append(h)
        if not child_heights:
            return 0
        total_h = sum(child_heights) + (count - 1) * self.layout().spacing()
        if y <= 0:
            return 0
        if y >= total_h:
            return count - 1
        cumulative = 0
        for i, h in enumerate(child_heights):
            mid = cumulative + h // 2
            if y < mid:
                return i
            cumulative += h + self.layout().spacing()
        return count - 1
    def _child_count(self):
        if self.layout() is None:
            return 0
        return self.layout().count()

def _add_card_mask(card):
    card._update_shadow_mask = lambda: _update_card_mask(card)
    card._update_shadow_mask()
    card.installEventFilter(_ShadowMaskFilter(card))

class _ShadowMaskFilter(QObject):
    def __init__(self, card):
        super().__init__(card)
        self._card = card
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Resize:
            _update_card_mask(self._card)
        return super().eventFilter(obj, event)

def _update_card_mask(card):
    # Mask is intentionally not used – setMask() with QRegion creates
    # pixelated stair-stepping on rounded corners.
    # Stylesheet border-radius handles anti-aliased visual clipping,
    # and layout margins keep children inside the rounded area.
    pass