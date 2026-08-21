import sys

import ctypes

from pathlib import Path

from PyQt6.QtGui import QFont, QFontDatabase, QColor

from PyQt6.QtWidgets import QApplication

APP_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = APP_DIR / "data"

# Unified persistent data root (next to the executable / script)
_EXE_DIR = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent.parent
APP_DATA_ROOT = _EXE_DIR / "Dropzone"

TOKEN_PATH = APP_DATA_ROOT / "auth" / "token.pickle"

CLIENT_SECRET_PATH = DATA_DIR / "client_secret.json"

FONT_PATH = APP_DIR / "resources" / "ofont.ru_FindSans Pro.ttf"

CIRCLE_ACTIVE_PATH = APP_DIR / "resources" / "circle_active.svg"

CIRCLE_DISABLED_PATH = APP_DIR / "resources" / "circle_disabled.svg"

RECYCLE_BIN_PATH = APP_DIR / "resources" / "recycle_bin.svg"

RECYCLE_BIN_ACTIVE_PATH = APP_DIR / "resources" / "recycle_bin_active.svg"

LEFT_ARROW_PATH = APP_DIR / "resources" / "left.svg"

RIGHT_ARROW_PATH = APP_DIR / "resources" / "right.svg"

PLUS_PATH = APP_DIR / "resources" / "plus.svg"

MINUS_PATH = APP_DIR / "resources" / "minus.svg"

KVADRAT_PATH = APP_DIR / "resources" / "kvadrat.svg"

KRESTIK_PATH = APP_DIR / "resources" / "krestik.svg"

KRESTIK_WHITE_PATH = APP_DIR / "resources" / "krestik_white.svg"

QUESTION_PATH = APP_DIR / "resources" / "question.svg"

SEARCH_PATH = APP_DIR / "resources" / "search.svg"

if FONT_PATH.exists():

    FR_PRIVATE = 0x10

    ctypes.windll.gdi32.AddFontResourceExW(str(FONT_PATH), FR_PRIVATE, 0)

FONT_GLOBAL = None

class _FontFamily:

    _value = "Segoe UI"

    def __str__(self):

        return self._value

    def __repr__(self):

        return self._value

    def set(self, value):

        self._value = value

FONT_FAMILY = _FontFamily()

def load_font_global(app):

    global FONT_GLOBAL

    if FONT_PATH.exists():

        try:

            fid = QFontDatabase.addApplicationFont(str(FONT_PATH))

            if fid >= 0:

                families = QFontDatabase.applicationFontFamilies(fid)

                if families:

                    FONT_FAMILY.set(families[0])

                    FONT_GLOBAL = QFont(str(FONT_FAMILY), 13)

                    app.setFont(FONT_GLOBAL)

                    return

        except Exception:

            pass

    FONT_GLOBAL = QFont("Segoe UI", 13)

    app.setFont(FONT_GLOBAL)

BG_COLOR = "#0A0A0B"

CARD_COLOR = "#141416"

CARD_LIGHT = "#1C1C1E"

ACCENT_CYAN = "#00F5FF"

ACCENT_LIME = "#CCFF00"

TEXT_MAIN = "#FFFFFF"

TEXT_SEC = "#8E8E93"

BORDER_COLOR = "#232326"

DANGER_COLOR = "#FF3B30"

TWITCH_CLIENT_ID = "dqlafmhyptfklyp90nmc7axqqdpjf3"

SUCCESS_COLOR = "#34C759"

GLOBAL_RADIUS = "30px"

GLOBAL_FONT_SIZE = 13

def get_stylesheet(font_size=None):

    fs = font_size if font_size else GLOBAL_FONT_SIZE

    return f"""

QMainWindow {{

    background-color: {BG_COLOR};

}}



QWidget {{

    background-color: transparent;

    color: {TEXT_MAIN};

    font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;

    font-size: {fs}px;

}}



/* === КАРТОЧКИ === */

QFrame#card {{

    background-color: {CARD_COLOR};

    border: 1px solid {BORDER_COLOR};

    border-radius: 30px;

}}



QFrame#cardLight {{

    background-color: {CARD_LIGHT};

    border: 1px solid {BORDER_COLOR};

    border-radius: 30px;

}}



QFrame#cardDark {{

    background-color: {BG_COLOR};

    border: 1px solid {BORDER_COLOR};

    border-radius: 30px;

}}



/* === ВСЕ ВНУТРЕННИЕ ВИДЖЕТЫ КАРТОЧЕК — ПРОЗРАЧНЫЕ === */

QFrame#card QWidget,

QFrame#cardLight QWidget,

QFrame#cardDark QWidget,

QFrame#card QLabel,

QFrame#cardLight QLabel,

QFrame#cardDark QLabel,

QScrollArea QWidget {{

    background-color: transparent;

}}



/* === КНОПКИ — ИДЕАЛЬНЫЙ ОВАЛ === */

QPushButton {{

    font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;

    font-weight: bold;

    text-transform: uppercase;

    letter-spacing: 0.5px;

    border: 2px solid transparent;

    border-radius: 9999px; /* Максимальное скругление */

    padding: 12px 24px;

    font-size: 13px;

    background-color: transparent;

    border-style: solid;

}}



QPushButton#btnLime {{

    background-color: {ACCENT_LIME};

    color: {BG_COLOR};

    border-color: {ACCENT_LIME};

}}

QPushButton#btnLime:hover {{

    background-color: transparent;

    color: {ACCENT_LIME};

}}



QPushButton#btnCyan {{

    background-color: {ACCENT_CYAN};

    color: {BG_COLOR};

    border-color: {ACCENT_CYAN};

}}

QPushButton#btnCyan:hover {{

    background-color: transparent;

    color: {ACCENT_CYAN};

}}



QPushButton#btnDanger {{

    background-color: {DANGER_COLOR};

    color: white;

    border-color: {DANGER_COLOR};

}}

QPushButton#btnDanger:hover {{

    background-color: transparent;

    color: {DANGER_COLOR};

}}



QPushButton#btnGhost {{

    background-color: {CARD_LIGHT};

    color: {TEXT_MAIN};

    border-color: {BORDER_COLOR};

}}

QPushButton#btnGhost:hover {{

    background-color: transparent;

    border-color: {TEXT_SEC};

}}



QPushButton#btnOutline {{

    background-color: transparent;

    color: {TEXT_MAIN};

    border-color: {BORDER_COLOR};

}}

QPushButton#btnOutline:hover {{

    border-color: {ACCENT_LIME};

    color: {ACCENT_LIME};

}}



QPushButton:disabled {{

    opacity: 0.35;

}}



/* === ТАБ-КНОПКИ === */

QPushButton#tabBtn {{

    background-color: transparent;

    color: {TEXT_SEC};

    border: 2px solid transparent;

    border-radius: 9999px;

    padding: 12px 24px;

    font-size: 12px;

    font-weight: bold;

    text-transform: uppercase;

    font-family: '{FONT_FAMILY}';

    border-style: solid;

}}

QPushButton#tabBtn:hover {{

    color: {TEXT_MAIN};

    background-color: rgba(255,255,255,0.05);

}}

QPushButton#tabBtn:checked {{

    background-color: {ACCENT_LIME};

    color: {BG_COLOR};

}}



/* === ПОЛЯ ВВОДА === */

QLineEdit {{

    background-color: {BG_COLOR};

    border: 1px solid {BORDER_COLOR};

    color: {TEXT_MAIN};

    padding: 14px 18px;

    border-radius: 9999px;

    font-size: 14px;

    font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;

    border-style: solid;

}}

QLineEdit:focus {{

    border-color: {ACCENT_CYAN};

}}

QLineEdit::placeholder {{

    color: #555;

}}



/* === ТЕКСТОВЫЕ ПОЛЯ === */

QTextEdit {{

    background-color: {BG_COLOR};

    border: 1px solid {BORDER_COLOR};

    color: {TEXT_MAIN};

    padding: 14px 18px;

    border-radius: 30px;

    font-size: 14px;

    font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;

}}

QTextEdit:focus {{

    border-color: {ACCENT_CYAN};

}}



/* === ВЫПАДАЮЩИЕ СПИСКИ === */

QComboBox {{

    background-color: {CARD_LIGHT};

    border: 1px solid {BORDER_COLOR};

    color: {TEXT_MAIN};

    padding: 0 18px;

    border-radius: 9999px;

    font-size: 13px;

    font-family: '{FONT_FAMILY}';

    min-width: 200px;

}}

QComboBox:hover {{

    border-color: {ACCENT_CYAN};

}}

QComboBox::drop-down {{

    border: none;

    width: 30px;

    border-top-right-radius: 9999px;

    border-bottom-right-radius: 9999px;

    background-color: transparent;

}}

QComboBox::down-arrow {{

    image: none;

    border: none;

}}

QComboBox QAbstractItemView {{

    background-color: {CARD_COLOR};

    border: 1px solid {BORDER_COLOR};

    border-radius: 20px;

    color: {TEXT_MAIN};

    selection-background-color: {CARD_LIGHT};

    selection-color: {ACCENT_LIME};

    padding: 4px;

    outline: none;

}}

QComboBox QAbstractItemView::item {{

    padding: 8px 16px;

    border-radius: 15px;

    margin: 2px 4px;

    background-color: transparent;

}}

QComboBox QAbstractItemView::item:hover {{

    background-color: {CARD_LIGHT};

    color: {ACCENT_LIME};

    border-radius: 15px;

}}



/* === RoundedListView (кастомный выпадающий список) === */

RoundedListView {{

    background-color: transparent;

    border: none;

    padding: 4px;

}}

RoundedListView::item {{

    padding: 8px 16px;

    border-radius: 15px;

    margin: 2px 4px;

    background-color: transparent;

    color: {TEXT_MAIN};

}}

RoundedListView::item:hover {{

    background-color: {CARD_LIGHT};

    color: {ACCENT_LIME};

    border-radius: 15px;

}}



/* === QScrollArea === */

QScrollArea {{

    background-color: transparent;

    border: none;

}}

QScrollArea > QWidget > QWidget {{

    background-color: transparent;

}}

QScrollArea#cardScroll > QWidget {{

    background-color: {CARD_LIGHT};

    border-radius: 30px;

}}



/* === СКРОЛЛБАРЫ === */

QScrollBar:vertical {{

    background: transparent;

    width: 6px;

    margin: 4px 0;

}}

QScrollBar::handle:vertical {{

    background: {BORDER_COLOR};

    border-radius: 3px;

    min-height: 30px;

}}

QScrollBar::handle:vertical:hover {{

    background: {TEXT_SEC};

}}

QScrollBar::add-line:vertical,

QScrollBar::sub-line:vertical {{

    height: 0;

    background: none;

}}

QScrollBar::add-page:vertical,

QScrollBar::sub-page:vertical {{

    background: none;

}}



QScrollBar:horizontal {{

    background: transparent;

    height: 6px;

    margin: 0 4px;

}}

QScrollBar::handle:horizontal {{

    background: {BORDER_COLOR};

    border-radius: 3px;

    min-width: 30px;

}}

QScrollBar::handle:horizontal:hover {{

    background: {TEXT_SEC};

}}

QScrollBar::add-line:horizontal,

QScrollBar::sub-line:horizontal {{

    width: 0;

    background: none;

}}

QScrollBar::add-page:horizontal,

QScrollBar::sub-page:horizontal {{

    background: none;

}}



/* === ТЕГИ === */

QLabel#tag {{

    padding: 6px 14px;

    border-radius: 9999px;

    font-size: 12px;

    font-weight: 600;

    background-color: {CARD_COLOR};

    border: 1px solid {BORDER_COLOR};

}}

QLabel#tagCyan {{

    border-color: {ACCENT_CYAN};

    color: {ACCENT_CYAN};

}}

QLabel#tagLime {{

    border-color: {ACCENT_LIME};

    color: {ACCENT_LIME};

}}

QLabel#tagDanger {{

    border-color: {DANGER_COLOR};

    color: {DANGER_COLOR};

}}

QLabel#tagSuccess {{

    border-color: {SUCCESS_COLOR};

    color: {SUCCESS_COLOR};

}}



/* === УБИРАЕМ ФОН У ВСЕХ QLabel В КАРТОЧКАХ === */

QLabel {{

    background-color: transparent;

    border: none;

}}



/* === ПРОГРЕСС-БАРЫ === */

QFrame#progressBar {{

    background-color: {BORDER_COLOR};

    border-radius: 9999px;

}}

QFrame#progressFill {{

    border-radius: 9999px;

}}



/* === ДИАЛОГИ === */

QDialog {{

    background-color: transparent;

}}



/* === QStackedWidget === */

QStackedWidget {{

    background-color: transparent;

}}



/* === QButtonGroup — невидимый === */

QButtonGroup {{

    background-color: transparent;

    border: none;

}}



/* === СПИСКИ (list widget) === */

QListWidget {{

    background-color: {CARD_LIGHT};

    border: 1px solid {BORDER_COLOR};

    border-radius: 30px;

    color: {TEXT_MAIN};

    outline: none;

}}

QListWidget::item {{

    background-color: transparent;

    padding: 10px 16px;

    border-radius: 15px;

    margin: 2px 4px;

}}

QListWidget::item:hover {{

    background-color: {CARD_COLOR};

    color: {ACCENT_LIME};

    border-radius: 15px;

}}



/* === SPINBOX === */

QSpinBox {{

    background-color: {BG_COLOR};

    border: 1px solid {BORDER_COLOR};

    color: {TEXT_MAIN};

    padding: 10px 14px;

    border-radius: 9999px;

    font-size: 14px;

    font-family: '{FONT_FAMILY}';

}}

QSpinBox:focus {{

    border-color: {ACCENT_CYAN};

}}

"""
