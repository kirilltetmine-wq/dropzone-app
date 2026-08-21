"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      DROPZONE — UI KIT v2.0                                  ║
║  Полный каталог всех визуальных компонентов проекта                          ║
║                                                                              ║
║  Кодовая система:                                                            ║
║    U001-U010  →  Кнопки (Buttons)                                            ║
║    U011-U012  →  Переключатели (Toggles)                                     ║
║    U013-U014  →  Ползунки (Sliders)                                          ║
║    U015-U017  →  Поля ввода (Inputs)                                         ║
║    U018-U023  →  Фреймы / Карточки (Frames / Cards)                          ║
║    U024-U030  →  Диалоги (Dialogs)                                           ║
║    U031-U037  →  Кастомные виджеты (Custom Widgets)                          ║
║    U038-U041  →  Окна / Заголовки (Windows / Titlebar)                       ║
║    U042-U043  →  Утилиты (Utilities)                                         ║
║    T001-T005  →  Темплейты страниц (Template Pages)                          ║
║                                                                              ║
║  ПРАВИЛО:                                                                    ║
║  Контейнеры (SectionCard, ComponentCard) НЕ имеют border.                    ║
║  Только сами интерактивные виджеты рисуют свои границы через paintEvent.     ║
╚══════════════════════════════════════════════════════════════════════════════╝

Запуск: python ui_kit_demo.py
"""

import sys
import os
from PyQt6.QtCore import Qt, QSize, QRectF
from PyQt6.QtGui import QColor, QPixmap, QPainter, QFont, QFontDatabase
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QScrollArea, QFrame, QPushButton, QLineEdit, QSizePolicy,
    QStackedWidget, QGridLayout, QSplitter,
)

# ============================================================================
#                           ИМПОРТ КОМПОНЕНТОВ (из ui_kit)
# ============================================================================
from ui_kit.ui_kit_buttons import (
    RoundedButton, GlowButton, HoverIconButton, TabButton,
    SplitSendButton,
)
from ui_kit.ui_kit_inputs import (
    RoundedLineEdit, WheelDropdown, ToggleSwitch, ModernSlider,
    PlatformDropdown,
)
from ui_kit.ui_kit_containers import (
    RoundedFrame, RoundedListView,
)
from ui_kit.ui_kit_primitives import (
    PlatformIcon, BadgeLabel, MessageRow, SystemMessage,
    DragHandle, DropContainer, _DragHandle,
)
from ui_kit.ui_kit_dialogs import (
    ModernDialog, ModernColorPicker, DeleteConfirmDialog,
    BatchValueDialog, SegmentInfoPopup, ModernItemPicker,
    ImageEditorDialog,
)
from ui_kit.ui_kit_widgets import (
    WheelWidget, DiceCubeWidget, DicePanel, _CaseStripWidget, ChatWidget,
)
from ui_kit.ui_kit_windows import (
    TitleBar, SplashScreen, DetachedWindow,
    DetachableSection, DetachablePanel,
)
from ui_kit.ui_kit_pages import (
    TabBarTemplate, WheelTabTemplate, LotteryTabTemplate,
    ConfigTabTemplate, LogsTabTemplate,
)

from core.theme import (
    BG_COLOR, CARD_COLOR, CARD_LIGHT, BORDER_COLOR,
    ACCENT_CYAN, ACCENT_LIME, TEXT_MAIN, TEXT_SEC, DANGER_COLOR,
    FONT_FAMILY, APP_DIR,
    PLUS_PATH, KRESTIK_PATH,
)


# ============================================================================
#                       СТИЛИ ДЛЯ UI KIT ДЕМО
# ============================================================================
KIT_BG = "#0D0D0E"
KIT_CARD = "#141416"
KIT_BORDER = "#232326"
KIT_ACCENT = "#CCFF00"
KIT_TEXT = "#FFFFFF"
KIT_TEXT_SEC = "#8E8E93"

SECTION_STYLE = f"""
    background-color: {KIT_CARD};
    border: 1px solid {KIT_BORDER};
    border-radius: 20px;
"""
CODE_LABEL_STYLE = f"""
    color: {KIT_ACCENT};
    font-size: 11px;
    font-weight: 700;
    font-family: 'Consolas', 'Courier New', monospace;
    background-color: rgba(204, 255, 0, 0.1);
    border-radius: 6px;
    padding: 2px 8px;
"""
NAME_LABEL_STYLE = f"""
    color: {TEXT_MAIN};
    font-size: 12px;
    font-weight: 600;
"""
DESC_LABEL_STYLE = f"""
    color: {TEXT_SEC};
    font-size: 10px;
"""


class CodeLabel(QLabel):
    """Метка с кодовым номером компонента (U001, U002, ...)"""
    def __init__(self, code, name, description=""):
        super().__init__()
        self.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        code_lbl = QLabel(f"  {code}  ")
        code_lbl.setStyleSheet(CODE_LABEL_STYLE)
        code_lbl.setFixedHeight(22)
        layout.addWidget(code_lbl)

        name_lbl = QLabel(name)
        name_lbl.setStyleSheet(NAME_LABEL_STYLE)
        layout.addWidget(name_lbl)

        if description:
            desc_lbl = QLabel(description)
            desc_lbl.setStyleSheet(DESC_LABEL_STYLE)
            layout.addWidget(desc_lbl)

        layout.addStretch(1)


class ComponentCard(QFrame):
    """Карточка-контейнер для одного компонента + его код"""
    def __init__(self, code, name, description="", widget=None):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {KIT_CARD};
                border-radius: 16px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 16)
        layout.setSpacing(10)

        # Кодовая метка
        self.code_label = CodeLabel(code, name, description)
        layout.addWidget(self.code_label)

        # Разделитель
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {KIT_BORDER};")
        layout.addWidget(sep)

        # Виджет компонента
        if widget is not None:
            widget.setParent(self)
            layout.addWidget(widget, alignment=Qt.AlignmentFlag.AlignLeft)


class SectionCard(QFrame):
    """Секция с заголовком и списком компонентов"""
    def __init__(self, title, code_range):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {KIT_BG};
                border-radius: 24px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(16)

        # Заголовок секции
        header = QFrame()
        header.setStyleSheet("background: transparent;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"""
            color: {KIT_ACCENT};
            font-size: 18px;
            font-weight: 900;
            letter-spacing: 1px;
            text-transform: uppercase;
        """)
        header_layout.addWidget(title_lbl)

        range_lbl = QLabel(code_range)
        range_lbl.setStyleSheet(f"""
            color: {TEXT_SEC};
            font-size: 11px;
            font-weight: 600;
            font-family: 'Consolas', monospace;
            background-color: rgba(255,255,255,0.05);
            border-radius: 8px;
            padding: 2px 10px;
        """)
        header_layout.addStretch(1)
        header_layout.addWidget(range_lbl)

        layout.addWidget(header)

        # Контейнер для карточек компонентов
        self.grid = QVBoxLayout()
        self.grid.setSpacing(12)
        layout.addLayout(self.grid)

    def add_component(self, code, name, description="", widget=None):
        """Добавить компонент в секцию"""
        card = ComponentCard(code, name, description, widget)
        self.grid.addWidget(card)


class UiKitDemo(QMainWindow):
    """Главное окно UI Kit демонстрации"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dropzone UI Kit v2.0")
        self.setMinimumSize(1100, 800)
        self.resize(1300, 900)
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {KIT_BG};
            }}
        """)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ================================================================
        # ВЕРХНИЙ ХЕДЕР
        # ================================================================
        header = QFrame()
        header.setStyleSheet(f"""
            background-color: {KIT_CARD};
            border-bottom: 1px solid {KIT_BORDER};
        """)
        header.setFixedHeight(60)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(30, 0, 30, 0)

        title = QLabel("DROPZONE  UI  KIT  v2.0")
        title.setStyleSheet(f"""
            color: {KIT_ACCENT};
            font-size: 22px;
            font-weight: 900;
            letter-spacing: 2px;
        """)
        header_layout.addWidget(title)

        header_layout.addStretch(1)

        subtitle = QLabel("Всего компонентов: 43  •  U001–U043  •  Темплейты: T001–T005")
        subtitle.setStyleSheet(f"""
            color: {TEXT_SEC};
            font-size: 11px;
            font-weight: 600;
            font-family: 'Consolas', monospace;
        """)
        header_layout.addWidget(subtitle)

        main_layout.addWidget(header)

        # ================================================================
        # СКРОЛЛЯЩАЯСЯ ОБЛАСТЬ
        # ================================================================
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                width: 4px;
                margin: 4px 0;
                background: transparent;
            }
            QScrollBar::handle:vertical {
                background: #232326;
                border-radius: 2px;
                min-height: 30px;
            }
            QScrollBar::add-line, QScrollBar::sub-line { height: 0; background: none; }
            QScrollBar::add-page, QScrollBar::sub-page { background: none; }
        """)

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(30, 24, 30, 40)
        content_layout.setSpacing(20)

        # ================================================================
        # СЕКЦИЯ 1: КНОПКИ (U001-U010)
        # ================================================================
        sec1 = SectionCard("Buttons — Кнопки", "U001 – U010")

        # U001: GlowButton lime
        btn_lime = GlowButton("PRIMARY (LIME)", "lime")
        btn_lime.setFixedSize(200, 45)
        sec1.add_component("U001", "GlowButton(style='lime')",
                           "Основная зеленая кнопка", btn_lime)

        # U002: GlowButton ghost
        btn_ghost = GlowButton("SECONDARY (GHOST)", "ghost")
        btn_ghost.setFixedSize(200, 45)
        sec1.add_component("U002", "GlowButton(style='ghost')",
                           "Вторичная серая кнопка", btn_ghost)

        # U003: GlowButton danger
        btn_danger = GlowButton("DANGER", "danger")
        btn_danger.setFixedSize(200, 45)
        sec1.add_component("U003", "GlowButton(style='danger')",
                           "Красная кнопка опасности", btn_danger)

        # U004: GlowButton outline
        btn_outline = GlowButton("OUTLINE", "outline")
        btn_outline.setFixedSize(200, 45)
        sec1.add_component("U004", "GlowButton(style='outline')",
                           "Контурная кнопка", btn_outline)

        # U005: GlowButton cyan
        btn_cyan = GlowButton("CYAN", "cyan")
        btn_cyan.setFixedSize(200, 45)
        sec1.add_component("U005", "GlowButton(style='cyan')",
                           "Бирюзовая кнопка", btn_cyan)

        # U006: HoverIconButton
        icon_btn = HoverIconButton(PLUS_PATH, PLUS_PATH)
        icon_btn.setFixedSize(40, 40)
        icon_btn.setIconSize(QSize(24, 24))
        sec1.add_component("U006", "HoverIconButton(normal, hover)",
                           "Иконка-кнопка с ховером", icon_btn)

        # U007: RoundedButton
        rnd_btn = RoundedButton("ROUNDED")
        rnd_btn.setFixedSize(180, 45)
        rnd_btn.set_colors(bg=CARD_LIGHT, text=TEXT_MAIN, border=BORDER_COLOR,
                           hover_bg="transparent", hover_text=ACCENT_LIME, hover_border=ACCENT_LIME)
        sec1.add_component("U007", "RoundedButton(text)",
                           "Базовая скругленная кнопка", rnd_btn)

        # U008: TabButton
        tab_btn = TabButton("TAB")
        tab_btn.setFixedSize(120, 40)
        sec1.add_component("U008", "TabButton(text)",
                           "Кнопка-вкладка (checkable)", tab_btn)

        # U009: TitleBar buttons (QPushButton)
        titlebar_btns = QWidget()
        titlebar_btns.setStyleSheet("background: transparent;")
        tb_layout = QHBoxLayout(titlebar_btns)
        tb_layout.setContentsMargins(0, 0, 0, 0)
        tb_layout.setSpacing(4)

        min_btn = QPushButton()
        min_btn.setFixedSize(46, 38)
        min_btn.setStyleSheet("""
            QPushButton { background: transparent; border: none; border-radius: 0; }
            QPushButton:hover { background: #141416; }
        """)
        min_btn.setText("—")
        min_btn.setStyleSheet(min_btn.styleSheet() + "color: #FFFFFF; font-size: 16px; font-weight: bold;")
        tb_layout.addWidget(min_btn)

        max_btn = QPushButton()
        max_btn.setFixedSize(46, 38)
        max_btn.setText("□")
        max_btn.setStyleSheet(max_btn.styleSheet() + "color: #FFFFFF; font-size: 16px; font-weight: bold;")
        tb_layout.addWidget(max_btn)

        close_btn = QPushButton()
        close_btn.setFixedSize(46, 38)
        close_btn.setText("✕")
        close_btn.setStyleSheet("""
            QPushButton { background: transparent; border: none; color: #FFFFFF; font-size: 16px; font-weight: bold; }
            QPushButton:hover { background: #E81123; }
        """)
        tb_layout.addWidget(close_btn)

        sec1.add_component("U009", "TitleBar Buttons",
                           "Кнопки свернуть/развернуть/закрыть", titlebar_btns)

        # U010: SplitSendButton
        split_btn = SplitSendButton()
        split_btn.setFixedWidth(200)
        sec1.add_component("U010", "SplitSendButton()",
                           "Раздельная кнопка отправки (платформа + send)", split_btn)

        content_layout.addWidget(sec1)

        # ================================================================
        # СЕКЦИЯ 2: ПЕРЕКЛЮЧАТЕЛИ (U011-U012)
        # ================================================================
        sec2 = SectionCard("Toggles — Переключатели", "U011 – U012")

        toggle_on = ToggleSwitch(initial=True)
        sec2.add_component("U011", "ToggleSwitch(initial=True)",
                           "Включенный переключатель", toggle_on)

        toggle_off = ToggleSwitch(initial=False)
        sec2.add_component("U012", "ToggleSwitch(initial=False)",
                           "Выключенный переключатель", toggle_off)

        content_layout.addWidget(sec2)

        # ================================================================
        # СЕКЦИЯ 3: ПОЛЗУНКИ (U013-U014)
        # ================================================================
        sec3 = SectionCard("Sliders — Ползунки", "U013 – U014")

        slider1 = ModernSlider()
        slider1.setFixedWidth(300)
        slider1.setValue(50)
        sec3.add_component("U013", "ModernSlider()",
                           "Ползунок со значением 50", slider1)

        slider2 = ModernSlider()
        slider2.setFixedWidth(300)
        slider2.setRange(0, 255)
        slider2.setValue(180)
        sec3.add_component("U014", "ModernSlider(range=0..255)",
                           "Ползунок с кастомным диапазоном", slider2)

        content_layout.addWidget(sec3)

        # ================================================================
        # СЕКЦИЯ 4: ПОЛЯ ВВОДА (U015-U017)
        # ================================================================
        sec4 = SectionCard("Inputs — Поля ввода", "U015 – U017")

        line_edit = RoundedLineEdit()
        line_edit.setPlaceholderText("Введите текст...")
        line_edit.setFixedWidth(300)
        line_edit.setFixedHeight(48)
        sec4.add_component("U015", "RoundedLineEdit()",
                           "Скругленное поле ввода", line_edit)

        dropdown = WheelDropdown()
        dropdown.setFixedWidth(300)
        dropdown.addItems(["Wheel 1", "Wheel 2", "Wheel 3"])
        sec4.add_component("U016", "WheelDropdown()",
                           "Выпадающий список колес", dropdown)

        chat_input = QLineEdit()
        chat_input.setPlaceholderText("Message...")
        chat_input.setFixedWidth(300)
        chat_input.setFixedHeight(40)
        chat_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {BG_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 20px;
                padding: 8px 14px;
                color: #FFFFFF;
                font-size: 13px;
            }}
            QLineEdit::placeholder {{ color: #555; }}
        """)
        sec4.add_component("U017", "QLineEdit (Chat Input)",
                           "Поле ввода сообщений чата", chat_input)

        content_layout.addWidget(sec4)

        # ================================================================
        # СЕКЦИЯ 5: ФРЕЙМЫ / КАРТОЧКИ (U018-U023)
        # ================================================================
        sec5 = SectionCard("Frames & Cards — Фреймы и карточки", "U018 – U023")

        # U018: RoundedFrame
        rnd_frame = RoundedFrame(bg_color=CARD_COLOR, border_color=BORDER_COLOR, radius=30)
        rnd_frame.setFixedSize(200, 80)
        frame_layout = QVBoxLayout(rnd_frame)
        frame_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl = QLabel("RoundedFrame")
        lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px; background: transparent;")
        frame_layout.addWidget(lbl)
        sec5.add_component("U018", "RoundedFrame(bg, border, radius)",
                           "Скругленный фрейм-карточка", rnd_frame)

        # U019: RoundedListView
        list_view = RoundedListView(radius=20)
        list_view.setFixedSize(200, 80)
        sec5.add_component("U019", "RoundedListView(radius)",
                           "Скругленный список", list_view)

        # U020: DropContainer
        drop = DropContainer()
        drop.setFixedSize(200, 60)
        drop.setStyleSheet(f"background-color: {CARD_COLOR}; border: 1px dashed {BORDER_COLOR}; border-radius: 16px;")
        sec5.add_component("U020", "DropContainer()",
                           "Контейнер drag-and-drop", drop)

        # U021: DragHandle
        drag_handle = DragHandle(0)
        sec5.add_component("U021", "DragHandle(index)",
                           "Ручка перетаскивания", drag_handle)

        # U022: MessageRow (заглушка)
        msg_row = MessageRow(
            author="User", text="!join", color=ACCENT_CYAN,
            platform_icon_path=os.path.join(str(APP_DIR), "resources", "twitch.svg"),
            timestamp="12:34", badges=["MOD"], is_entry=False, is_mod=True
        )
        msg_row.setFixedWidth(500)
        sec5.add_component("U022", "MessageRow(author, text, ...)",
                           "Строка сообщения чата", msg_row)

        # U023: SystemMessage
        sys_msg = SystemMessage("SYSTEM", "Системное сообщение чата", ACCENT_LIME)
        sys_msg.setFixedWidth(500)
        sec5.add_component("U023", "SystemMessage(tag, text, color)",
                           "Системное сообщение чата", sys_msg)

        content_layout.addWidget(sec5)

        # ================================================================
        # СЕКЦИЯ 6: ДИАЛОГИ (U024-U030)
        # ================================================================
        sec6 = SectionCard("Dialogs — Диалоговые окна", "U024 – U030")

        # U024: ModernDialog (запускается по кнопке)
        modern_dialog_btn = GlowButton("OPEN MODERN DIALOG", "lime")
        modern_dialog_btn.setFixedSize(240, 45)
        modern_dialog_btn.clicked.connect(self._show_modern_dialog)
        sec6.add_component("U024", "ModernDialog(parent, title, msg)",
                           "Базовый современный диалог", modern_dialog_btn)

        # U025: ModernColorPicker (запускается по кнопке)
        color_picker_btn = GlowButton("OPEN COLOR PICKER", "cyan")
        color_picker_btn.setFixedSize(240, 45)
        color_picker_btn.clicked.connect(self._show_color_picker)
        sec6.add_component("U025", "ModernColorPicker(parent, color)",
                           "Выбор цвета с RGB-слайдерами", color_picker_btn)

        # U026: ModernItemPicker (запускается по кнопке)
        item_picker_btn = GlowButton("OPEN ITEM PICKER", "outline")
        item_picker_btn.setFixedSize(240, 45)
        item_picker_btn.clicked.connect(self._show_item_picker)
        sec6.add_component("U026", "ModernItemPicker(parent, color, img)",
                           "Выбор цвета/изображения", item_picker_btn)

        # U027: DeleteConfirmDialog (запускается по кнопке)
        delete_btn = GlowButton("OPEN DELETE CONFIRM", "danger")
        delete_btn.setFixedSize(240, 45)
        delete_btn.clicked.connect(self._show_delete_confirm)
        sec6.add_component("U027", "DeleteConfirmDialog(parent, count)",
                           "Диалог подтверждения удаления", delete_btn)

        # U028: BatchValueDialog (запускается по кнопке)
        batch_btn = GlowButton("OPEN BATCH DIALOG", "ghost")
        batch_btn.setFixedSize(240, 45)
        batch_btn.clicked.connect(self._show_batch_dialog)
        sec6.add_component("U028", "BatchValueDialog(parent)",
                           "Диалог массового изменения", batch_btn)

        # U029: SegmentInfoPopup (запускается по кнопке)
        segment_btn = GlowButton("OPEN SEGMENT INFO", "outline")
        segment_btn.setFixedSize(240, 45)
        segment_btn.clicked.connect(self._show_segment_popup)
        sec6.add_component("U029", "SegmentInfoPopup(parent, prize, chance)",
                           "Информация о сегменте колеса", segment_btn)

        # U030: ImageEditorDialog (запускается по кнопке)
        img_editor_btn = GlowButton("OPEN IMAGE EDITOR", "lime")
        img_editor_btn.setFixedSize(240, 45)
        img_editor_btn.clicked.connect(self._show_image_editor)
        sec6.add_component("U030", "ImageEditorDialog(parent, path, ...)",
                           "Редактор изображений", img_editor_btn)

        content_layout.addWidget(sec6)

        # ================================================================
        # СЕКЦИЯ 7: КАСТОМНЫЕ ВИДЖЕТЫ (U031-U037)
        # ================================================================
        sec7 = SectionCard("Custom Widgets — Кастомные виджеты", "U031 – U037")

        # U031: WheelWidget
        wheel = WheelWidget()
        wheel.setFixedSize(300, 300)
        wheel.set_segments([
            {"prize": "Prize 1", "chance": 25, "color": "#FF3B30"},
            {"prize": "Prize 2", "chance": 25, "color": "#FF9500"},
            {"prize": "Prize 3", "chance": 25, "color": "#CCFF00"},
            {"prize": "Prize 4", "chance": 25, "color": "#00F5FF"},
        ])
        sec7.add_component("U031", "WheelWidget()",
                           "Колесо фортуны (сегменты + вращение)", wheel)

        # U032: DiceCubeWidget
        dice = DiceCubeWidget()
        dice.setFixedSize(200, 200)
        sec7.add_component("U032", "DiceCubeWidget()",
                           "3D-кубик с анимацией броска", dice)

        # U033: DicePanel (запускается по кнопке)
        dice_panel_btn = GlowButton("OPEN DICE PANEL", "lime")
        dice_panel_btn.setFixedSize(240, 45)
        dice_panel_btn.clicked.connect(self._show_dice_panel)
        sec7.add_component("U033", "DicePanel(parent)",
                           "Панель управления кубиком", dice_panel_btn)

        # U034: _CaseStripWidget
        case_strip = _CaseStripWidget([
            {"name": "Prize 1", "color": "#FF3B30", "chance": 25},
            {"name": "Prize 2", "color": "#FF9500", "chance": 25},
            {"name": "Prize 3", "color": "#CCFF00", "chance": 25},
            {"name": "Prize 4", "color": "#00F5FF", "chance": 25},
        ])
        case_strip.setFixedWidth(500)
        sec7.add_component("U034", "_CaseStripWidget(prizes)",
                           "Полоска кейса с призами", case_strip)

        # U035: ChatWidget (запускается по кнопке)
        chat_btn = GlowButton("OPEN CHAT WIDGET", "cyan")
        chat_btn.setFixedSize(240, 45)
        chat_btn.clicked.connect(self._show_chat_widget)
        sec7.add_component("U035", "ChatWidget(parent)",
                           "Виджет чата с сообщениями", chat_btn)

        # U036: PlatformDropdown
        platform_drop = PlatformDropdown("twitch")
        sec7.add_component("U036", "PlatformDropdown(current_id)",
                           "Выпадающий список платформ", platform_drop)

        # U037: BadgeLabel
        badge = BadgeLabel("MOD")
        badge.setFixedWidth(40)
        sec7.add_component("U037", "BadgeLabel(text='MOD'/'VIP'/'SUB')",
                           "Бейдж модератора/VIP/подписчика", badge)

        content_layout.addWidget(sec7)

        # ================================================================
        # СЕКЦИЯ 8: ОКНА / ЗАГОЛОВКИ (U038-U041)
        # ================================================================
        sec8 = SectionCard("Windows & Titlebar — Окна и заголовки", "U038 – U041")

        # U038: TitleBar
        titlebar = QFrame()
        titlebar.setFixedSize(500, 38)
        titlebar.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 0;
            }}
        """)
        # Создаем мини-TitleBar вручную
        tb_layout_inner = QHBoxLayout(titlebar)
        tb_layout_inner.setContentsMargins(16, 0, 0, 0)
        tb_lbl = QLabel("Dropzone")
        tb_lbl.setStyleSheet(f"color: {TEXT_MAIN}; font-size: 13px; font-weight: 700; background: transparent;")
        tb_layout_inner.addWidget(tb_lbl)
        tb_layout_inner.addStretch()
        for _ in range(3):
            dot_btn = QPushButton()
            dot_btn.setFixedSize(46, 38)
            dot_btn.setStyleSheet("""
                QPushButton {
                    background: transparent; border: none; border-radius: 0;
                    color: #FFFFFF; font-size: 14px;
                }
                QPushButton:hover { background: #141416; }
            """)
            tb_layout_inner.addWidget(dot_btn)
        sec8.add_component("U038", "TitleBar(parent)",
                           "Кастомный заголовок окна", titlebar)

        # U039: SplashScreen (запускается по кнопке)
        splash_btn = GlowButton("OPEN SPLASH SCREEN", "lime")
        splash_btn.setFixedSize(240, 45)
        splash_btn.clicked.connect(self._show_splash)
        sec8.add_component("U039", "SplashScreen(parent)",
                           "Экран-заставка при запуске", splash_btn)

        # U040: DetachedWindow (запускается по кнопке)
        detach_btn = GlowButton("OPEN DETACHED WINDOW", "ghost")
        detach_btn.setFixedSize(240, 45)
        detach_btn.clicked.connect(self._show_detached)
        sec8.add_component("U040", "DetachedWindow(content, title, ...)",
                           "Открепленное окно", detach_btn)

        # U041: DetachableSection (запускается по кнопке)
        detach_sec_btn = GlowButton("OPEN DETACHABLE SECTION", "outline")
        detach_sec_btn.setFixedSize(240, 45)
        detach_sec_btn.clicked.connect(self._show_detachable_section)
        sec8.add_component("U041", "DetachableSection(content, title)",
                           "Открепляемая секция", detach_sec_btn)

        content_layout.addWidget(sec8)

        # ================================================================
        # СЕКЦИЯ 9: УТИЛИТЫ (U042-U043)
        # ================================================================
        sec9 = SectionCard("Utilities — Утилиты", "U042 – U043")

        # U042: _DragHandle (из utils.py)
        util_drag = _DragHandle(self)
        sec9.add_component("U042", "_DragHandle(parent_dialog, dot_color)",
                           "Ручка перетаскивания для диалогов", util_drag)

        # U043: PlatformIcon
        icon_path = os.path.join(str(APP_DIR), "resources", "twitch.svg")
        if os.path.exists(icon_path):
            plat_icon = PlatformIcon(icon_path)
        else:
            plat_icon = PlatformIcon.__new__(PlatformIcon)
            plat_icon = QLabel("TW")
            plat_icon.setFixedSize(14, 14)
            plat_icon.setStyleSheet(f"color: {ACCENT_CYAN}; font-size: 10px; font-weight: bold;")
        sec9.add_component("U043", "PlatformIcon(icon_path)",
                           "Иконка платформы (YouTube/Twitch/Kick)", plat_icon)

        content_layout.addWidget(sec9)

        # ================================================================
        # СЕКЦИЯ 10: ТЕМПЛЕЙТЫ СТРАНИЦ
        # ================================================================
        sec10 = SectionCard("Template Pages — Готовые страницы", "T001 – T005")

        # T001: TabBarTemplate
        tab_bar_btn = GlowButton("OPEN TAB BAR", "lime")
        tab_bar_btn.setFixedSize(240, 45)
        tab_bar_btn.clicked.connect(self._show_tab_bar)
        sec10.add_component("T001", "TabBarTemplate()",
                           "Панель вкладок MAIN/WHEEL/LOGS/CONFIG", tab_bar_btn)

        # T002: WheelTabTemplate
        wheel_tab_btn = GlowButton("OPEN WHEEL TAB", "cyan")
        wheel_tab_btn.setFixedSize(240, 45)
        wheel_tab_btn.clicked.connect(self._show_wheel_tab)
        sec10.add_component("T002", "WheelTabTemplate()",
                           "Вкладка колеса: WheelWidget + конфигуратор", wheel_tab_btn)

        # T003: LotteryTabTemplate
        lottery_btn = GlowButton("OPEN LOTTERY TAB", "outline")
        lottery_btn.setFixedSize(240, 45)
        lottery_btn.clicked.connect(self._show_lottery_tab)
        sec10.add_component("T003", "LotteryTabTemplate()",
                           "Вкладка лотереи: стрим + управление", lottery_btn)

        # T004: ConfigTabTemplate
        config_btn = GlowButton("OPEN CONFIG TAB", "ghost")
        config_btn.setFixedSize(240, 45)
        config_btn.clicked.connect(self._show_config_tab)
        sec10.add_component("T004", "ConfigTabTemplate()",
                           "Вкладка настроек: sidebar + контент", config_btn)

        # T005: LogsTabTemplate
        logs_btn = GlowButton("OPEN LOGS TAB", "danger")
        logs_btn.setFixedSize(240, 45)
        logs_btn.clicked.connect(self._show_logs_tab)
        sec10.add_component("T005", "LogsTabTemplate()",
                           "Вкладка логов: таблица + экспорт", logs_btn)

        content_layout.addWidget(sec10)

        # ================================================================
        # ФУТЕР
        # ================================================================
        footer = QFrame()
        footer.setStyleSheet(f"""
            background-color: {KIT_CARD};
            border-radius: 16px;
        """)
        footer.setFixedHeight(50)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 0, 20, 0)

        footer_text = QLabel("© Dropzone  •  PyQt6  •  Цветовая схема: accent=#CCFF00  •  danger=#FF3B30  •  bg=#0A0A0B")
        footer_text.setStyleSheet(f"color: {TEXT_SEC}; font-size: 10px;")
        footer_layout.addWidget(footer_text)

        content_layout.addWidget(footer)

        # ================================================================
        # ФИНАЛ
        # ================================================================
        scroll.setWidget(content)
        main_layout.addWidget(scroll, 1)

    # ====================================================================
    #                     МЕТОДЫ ДЛЯ ЗАПУСКА ДИАЛОГОВ
    # ====================================================================
    def _show_modern_dialog(self):
        dlg = ModernDialog(self, "DIALOG TITLE", "Сообщение диалога")
        dlg.exec()

    def _show_color_picker(self):
        dlg = ModernColorPicker(self, "#CCFF00")
        dlg.exec()

    def _show_item_picker(self):
        dlg = ModernItemPicker(self, "#CCFF00")
        dlg.exec()

    def _show_delete_confirm(self):
        dlg = DeleteConfirmDialog(self, 3)
        dlg.exec()

    def _show_batch_dialog(self):
        dlg = BatchValueDialog(self)
        dlg.exec()

    def _show_segment_popup(self):
        popup = SegmentInfoPopup(self, "Prize Name", 25.0)
        popup.show()

    def _show_image_editor(self):
        img_path = os.path.join(str(APP_DIR), "resources", "logo.png")
        if os.path.exists(img_path):
            dlg = ImageEditorDialog(self, img_path)
            dlg.exec()

    def _show_dice_panel(self):
        panel = DicePanel(self)
        dlg = ModernDialog(self, "DICE PANEL", "")
        dlg.exec()

    def _show_chat_widget(self):
        chat = ChatWidget(self)
        chat.setFixedSize(400, 500)
        chat.add_system_message("SYSTEM", "Чат запущен", ACCENT_LIME)
        chat.add_message("Streamer", "!join", ACCENT_CYAN,
                         os.path.join(str(APP_DIR), "resources", "twitch.svg"),
                         "12:34", ["MOD"], is_mod=True)
        chat.add_message("User1", "Hello!", "#FF9500",
                         os.path.join(str(APP_DIR), "resources", "youtube.svg"),
                         "12:35", is_entry=True)
        dlg = QFrame(self)
        dlg.setStyleSheet(f"background: {BG_COLOR}; border-radius: 20px;")
        layout = QVBoxLayout(dlg)
        layout.addWidget(chat)
        dlg.show()

    def _show_splash(self):
        splash = SplashScreen(self)
        splash.exec()

    def _show_detached(self):
        content = QLabel("Detached Window Content")
        content.setStyleSheet(f"color: {TEXT_MAIN}; font-size: 14px; background: {BG_COLOR};")
        det = DetachedWindow(content, "Detached Section")
        det.show()

    def _show_detachable_section(self):
        content = QLabel("Detachable Section Content")
        content.setStyleSheet(f"color: {TEXT_MAIN}; font-size: 14px;")
        sec = DetachableSection(content, "Detachable Section")
        sec.show()

    # ================================================================
    # МЕТОДЫ ДЛЯ ЗАПУСКА ТЕМПЛЕЙТОВ СТРАНИЦ
    # ================================================================
    def _show_tab_bar(self):
        """T001: TabBarTemplate + простой QStackedWidget"""
        dlg = QFrame(self)
        dlg.setWindowFlags(Qt.WindowType.Window)
        dlg.setMinimumSize(800, 400)
        dlg.setStyleSheet(f"background-color: {BG_COLOR};")
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        tab_bar = TabBarTemplate()
        stack = QStackedWidget()
        stack.setStyleSheet("background: transparent;")

        # 4 страницы-заглушки
        for name in ["MAIN CONTENT", "WHEEL CONTENT", "LOGS CONTENT", "CONFIG CONTENT"]:
            page = QWidget()
            page.setStyleSheet("background: transparent;")
            pl = QVBoxLayout(page)
            lbl = QLabel(name)
            lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 24px; font-weight: 800;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            pl.addWidget(lbl)
            stack.addWidget(page)

        tab_bar.connect_to_stack(stack)
        layout.addWidget(tab_bar)
        layout.addWidget(stack, 1)

        dlg.show()
        dlg.raise_()

    def _show_wheel_tab(self):
        """T002: WheelTabTemplate"""
        page = WheelTabTemplate()
        page.setWindowFlags(Qt.WindowType.Window)
        page.setMinimumSize(900, 600)
        page.show()
        page.raise_()

    def _show_lottery_tab(self):
        """T003: LotteryTabTemplate"""
        page = LotteryTabTemplate()
        page.setWindowFlags(Qt.WindowType.Window)
        page.setMinimumSize(700, 400)
        page.show()
        page.raise_()

    def _show_config_tab(self):
        """T004: ConfigTabTemplate"""
        page = ConfigTabTemplate()
        page.setWindowFlags(Qt.WindowType.Window)
        page.setMinimumSize(800, 500)
        page.show()
        page.raise_()

    def _show_logs_tab(self):
        """T005: LogsTabTemplate"""
        page = LogsTabTemplate()
        page.setWindowFlags(Qt.WindowType.Window)
        page.setMinimumSize(700, 500)
        page.show()
        page.raise_()


# ============================================================================
#               ТЕМПЛЕЙТЫ СТРАНИЦ — ГОТОВЫЕ БЛОКИ ИНТЕРФЕЙСА
# ============================================================================
# Эти классы повторяют структуру реального app.py.
# Основной код может наследовать их или использовать как вложенные виджеты.
# ============================================================================


class TabBarTemplate(QFrame):
    """
    [T001]  Панель вкладок (MAIN / WHEEL / LOGS / CONFIG)
    ───────
    Как в app.py: QFrame + QPushButton + glow_line + QStackedWidget
    Использование:
        tab_bar = TabBarTemplate()
        tab_bar.tab_names = ["MAIN", "WHEEL", "LOGS", "CONFIG"]
        tab_bar.setup(stack_widget)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("tabBar")
        self.setStyleSheet(f"""
            QFrame#tabBar {{
                background-color: {BG_COLOR};
                border-bottom: 1px solid {BORDER_COLOR};
            }}
        """)
        self.setFixedHeight(38)

        self.tab_btns = []
        self.glow_line = None
        self.tab_names = ["MAIN", "WHEEL", "LOGS", "CONFIG"]
        self._stack = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        for name in self.tab_names:
            btn = QPushButton(name, self)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; border: none;
                    color: {TEXT_SEC}; font-size: 12px; font-weight: 800;
                    letter-spacing: 0.8px; text-transform: uppercase;
                    padding: 0 24px;
                    font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;
                }}
                QPushButton:hover {{ color: {TEXT_MAIN}; }}
            """)
            btn.setMinimumHeight(38)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            layout.addWidget(btn, 1)
            self.tab_btns.append(btn)

        self.glow_line = QFrame(self)
        self.glow_line.setFixedHeight(2)
        self.glow_line.setStyleSheet(f"""
            background-color: {ACCENT_LIME}; border-radius: 1px;
        """)
        self.glow_line.setGeometry(0, 36, self.width(), 2)
        self.glow_line.lower()

    def connect_to_stack(self, stack: QStackedWidget):
        """Привязать кнопки к QStackedWidget"""
        self._stack = stack
        for i, btn in enumerate(self.tab_btns):
            btn.clicked.connect(lambda checked, idx=i: self._switch(idx))

    def _switch(self, idx):
        if self._stack:
            self._stack.setCurrentIndex(idx)
        # Подсветка активной вкладки
        for i, btn in enumerate(self.tab_btns):
            active = (i == idx)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; border: none;
                    color: {ACCENT_LIME if active else TEXT_SEC};
                    font-size: 12px; font-weight: 800;
                    letter-spacing: 0.8px; text-transform: uppercase;
                    padding: 0 24px;
                    font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;
                }}
                QPushButton:hover {{ color: {ACCENT_LIME if active else TEXT_MAIN}; }}
            """)
        # Двигаем glow_line
        if self._stack:
            tab_btn = self.tab_btns[idx]
            self.glow_line.setGeometry(tab_btn.x(), 36, tab_btn.width(), 2)
            self.glow_line.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.glow_line and self.tab_btns:
            idx = self._stack.currentIndex() if self._stack else 0
            if idx < len(self.tab_btns):
                tab_btn = self.tab_btns[idx]
                self.glow_line.setGeometry(tab_btn.x(), 36, tab_btn.width(), 2)


class WheelTabTemplate(QWidget):
    """
    [T002]  Вкладка колеса: QSplitter(wheel_area + sidebar_configurator)
    ───────
    Как в app.py._setup_wheel_tab():
      слева — WheelWidget + WheelDropdown + GlowButton("SPIN WHEEL")
      справа — конфигуратор (ToggleSwitch, GlowButton, cards)
    Использование:
        wheel_page = WheelTabTemplate()
        stack.addWidget(wheel_page)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(5)
        splitter.setChildrenCollapsible(False)
        layout.addWidget(splitter)

        # -- Левая часть: колесо --
        wheel_area = QWidget()
        wheel_area.setMinimumWidth(400)
        wheel_layout = QVBoxLayout(wheel_area)
        wheel_layout.setContentsMargins(30, 20, 20, 20)

        header = QHBoxLayout()
        wheel_layout.addLayout(header)

        self.wheel_combo = WheelDropdown()
        self.wheel_combo.setPlaceholderText("Select wheel...")
        header.addWidget(self.wheel_combo, 1)

        self.btn_frame = QHBoxLayout()
        self.btn_frame.setSpacing(4)
        header.addLayout(self.btn_frame)

        self.add_btn = HoverIconButton(PLUS_PATH, PLUS_PATH)
        self.add_btn.setFixedSize(36, 36)
        self.add_btn.setIconSize(self.add_btn.size())
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.setStyleSheet("""
            QPushButton { background: transparent; border: none; padding: 0; }
            QPushButton:hover { background: rgba(255,255,255,12); border-radius: 18px; }
        """)
        self.btn_frame.addWidget(self.add_btn)

        self.del_btn = GlowButton("DELETE", "ghost")
        self.btn_frame.addWidget(self.del_btn)
        self.rename_btn = GlowButton("RENAME", "ghost")
        self.btn_frame.addWidget(self.rename_btn)
        self.manage_btn = GlowButton("MANAGE", "ghost")
        self.btn_frame.addWidget(self.manage_btn)

        self.wheel_widget = WheelWidget()
        self.wheel_widget.set_segments([
            {"prize": "Prize 1", "chance": 25, "color": "#FF3B30"},
            {"prize": "Prize 2", "chance": 25, "color": "#FF9500"},
            {"prize": "Prize 3", "chance": 25, "color": "#CCFF00"},
            {"prize": "Prize 4", "chance": 25, "color": "#00F5FF"},
        ])
        self.wheel_layout = wheel_layout
        self.wheel_layout.addWidget(self.wheel_widget, 1)

        self.spin_btn = GlowButton("SPIN WHEEL", "lime")
        self.wheel_layout.addWidget(self.spin_btn, 0, Qt.AlignmentFlag.AlignCenter)

        splitter.addWidget(wheel_area)

        # -- Правая часть: конфигуратор --
        sidebar = QFrame()
        sidebar.setMinimumWidth(280)
        sidebar.setObjectName("sidebarFrame")
        sidebar.setStyleSheet("QFrame#sidebarFrame { background-color: transparent; border: 1px solid #232326; border-radius: 20px; }")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)

        side_scroll = QScrollArea()
        side_scroll.setWidgetResizable(True)
        side_scroll.setStyleSheet("""
            QScrollArea { background-color: transparent; border: none; }
        """)

        side_content = QWidget()
        side_content.setStyleSheet("background-color: transparent;")
        self.side_layout = QVBoxLayout(side_content)
        self.side_layout.setContentsMargins(30, 40, 30, 40)

        side_scroll.setWidget(side_content)
        sidebar_layout.addWidget(side_scroll)

        config_title = QLabel("WHEEL CONFIGURATOR")
        config_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        config_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.side_layout.addWidget(config_title)

        # Auto Color
        self.auto_color_row = QWidget()
        self.auto_color_row.setStyleSheet("background: transparent;")
        toggle_row = QHBoxLayout(self.auto_color_row)
        toggle_row.setContentsMargins(0, 0, 0, 0)
        self.side_layout.addWidget(self.auto_color_row)
        toggle_label = QLabel("Auto Color Gradient")
        toggle_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 13px;")
        toggle_row.addWidget(toggle_label)
        toggle_row.addStretch()
        self.auto_toggle = ToggleSwitch(initial=True)
        toggle_row.addWidget(self.auto_toggle)

        # Random Colors
        self.random_color_row = QWidget()
        self.random_color_row.setStyleSheet("background: transparent;")
        random_layout = QHBoxLayout(self.random_color_row)
        random_layout.setContentsMargins(0, 0, 0, 0)
        self.side_layout.addWidget(self.random_color_row)
        random_label = QLabel("Random Colors")
        random_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 13px;")
        random_layout.addWidget(random_label)
        random_layout.addStretch()
        self.random_toggle = ToggleSwitch(initial=False)
        random_layout.addWidget(self.random_toggle)

        # General Color
        self.general_color_row = QWidget()
        self.general_color_row.setStyleSheet("background: transparent;")
        general_layout = QHBoxLayout(self.general_color_row)
        general_layout.setContentsMargins(0, 0, 0, 0)
        self.side_layout.addWidget(self.general_color_row)
        general_label = QLabel("General Color")
        general_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 13px;")
        general_layout.addWidget(general_label)
        general_layout.addStretch()
        self.general_toggle = ToggleSwitch(initial=False)
        general_layout.addWidget(self.general_toggle)

        # Buttons
        btn_row = QHBoxLayout()
        self.side_layout.addLayout(btn_row)
        self.add_sector_btn = GlowButton("ADD SECTOR", "outline")
        btn_row.addWidget(self.add_sector_btn)
        self.equalize_btn = GlowButton("EQUALIZE", "outline")
        btn_row.addWidget(self.equalize_btn)

        self.side_layout.addSpacing(10)

        detachable_sidebar = DetachablePanel(sidebar, "WHEEL CONFIGURATOR")
        splitter.addWidget(detachable_sidebar)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([700, 400])


class LotteryTabTemplate(QWidget):
    """
    [T003]  Вкладка лотереи: стрим-коннекшн + управление
    ───────
    Как в app_lottery_mixin.py._setup_lottery_tab():
      card → RoundedLineEdit + GlowButton + ToggleSwitch + QScrollArea
    Все виджеты доступны как self.xxx для подключения сигналов.
    Использование:
        lottery_page = LotteryTabTemplate()
        lottery_page.start_btn.clicked.connect(self.toggle_collection)
        stack.addWidget(lottery_page)
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)

        conn_card = QFrame()
        conn_card.setObjectName("cardLight")
        conn_layout = QVBoxLayout(conn_card)
        conn_layout.setContentsMargins(30, 20, 30, 20)
        layout.addWidget(conn_card)

        conn_title = QLabel("LIVE STREAM CONNECTION")
        conn_title.setStyleSheet(f"color: {ACCENT_LIME}; font-size: 14px; font-weight: bold;")
        conn_layout.addWidget(conn_title)

        inputs_row = QHBoxLayout()
        conn_layout.addLayout(inputs_row)

        self.video_url_entry = RoundedLineEdit()
        self.video_url_entry.setPlaceholderText("Enter YouTube Video URL or ID...")
        inputs_row.addWidget(self.video_url_entry, 1)

        self.keyword_entry = RoundedLineEdit()
        self.keyword_entry.setPlaceholderText("Keyword...")
        self.keyword_entry.setText("!join")
        self.keyword_entry.setMaximumWidth(200)
        inputs_row.addWidget(self.keyword_entry)

        controls_row = QHBoxLayout()
        conn_layout.addLayout(controls_row)

        self.start_btn = GlowButton("START TRACKING", "ghost")
        controls_row.addWidget(self.start_btn)

        self.collect_btn = GlowButton("START COLLECTING", "outline")
        self.collect_btn.setEnabled(False)
        controls_row.addWidget(self.collect_btn)

        self.pick_winner_btn = GlowButton("PICK WINNER", "lime")
        controls_row.addWidget(self.pick_winner_btn)

        self.clear_btn = GlowButton("CLEAR LIST", "ghost")
        controls_row.addWidget(self.clear_btn)

        self.manual_add_row = QWidget()
        self.manual_add_row.setStyleSheet("background: transparent;")
        add_row = QHBoxLayout(self.manual_add_row)
        add_row.setContentsMargins(0, 0, 0, 0)
        conn_layout.addWidget(self.manual_add_row)

        add_label = QLabel("Manual add:")
        add_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px;")
        add_row.addWidget(add_label)

        self.manual_add_entry = RoundedLineEdit()
        self.manual_add_entry.setPlaceholderText("@username")
        self.manual_add_entry.setMaximumWidth(200)
        add_row.addWidget(self.manual_add_entry)

        self.add_user_btn = GlowButton("ADD", "outline")
        add_row.addWidget(self.add_user_btn)

        add_row.addStretch()

        toggle_row = QHBoxLayout()
        conn_layout.addLayout(toggle_row)

        gray_label = QLabel("Delete winners")
        gray_label.setFixedWidth(120)
        gray_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px;")
        toggle_row.addWidget(gray_label)

        self.auto_gray_toggle = ToggleSwitch(initial=True)
        toggle_row.addWidget(self.auto_gray_toggle)
        toggle_row.addStretch()

        wheel_toggle_row = QHBoxLayout()
        conn_layout.addLayout(wheel_toggle_row)

        wheel_label = QLabel("Auto wheel")
        wheel_label.setFixedWidth(120)
        wheel_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px;")
        wheel_toggle_row.addWidget(wheel_label)

        self.auto_wheel_toggle = ToggleSwitch(initial=False)
        wheel_toggle_row.addWidget(self.auto_wheel_toggle)
        wheel_toggle_row.addStretch()

        self.status_label = QLabel("STANDBY")
        self.status_label.setStyleSheet(f"color: {TEXT_SEC}; font-weight: bold;")
        toggle_row.addWidget(self.status_label)

        self.participants_label = QLabel("PARTICIPANTS")
        self.participants_label.setStyleSheet("font-size: 15px; font-weight: bold; margin-top: 24px; margin-left: 6px;")
        layout.addWidget(self.participants_label)

        scroll = QScrollArea()
        scroll.setObjectName("cardScroll")
        scroll.setWidgetResizable(True)

        self.participants_container = QWidget()
        self.participants_container.setStyleSheet("background-color: transparent; border-radius: 30px;")

        scroll.setWidget(self.participants_container)
        layout.addWidget(scroll, 1)


class ConfigTabTemplate(QWidget):
    """
    [T004]  Вкладка настроек: sidebar + контент
    ───────
    Как в app_config_mixin.py._setup_config_tab():
      слева — QFrame(240px) с QPushButton навигацией
      справа — QStackedWidget с секциями настроек
    Использование:
        config_page = ConfigTabTemplate()
        stack.addWidget(config_page)
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_COLOR};
                border-right: 1px solid {BORDER_COLOR};
            }}
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 16, 0, 16)
        sidebar_layout.setSpacing(0)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(sidebar)

        # Секции и кнопки
        sections = [
            ("GENERAL", ["General", "Appearance"]),
            ("WHEEL", ["Wheel", "Segments", "Animation"]),
            ("CASE", ["Case", "Prize"]),
            ("LOTTERY", ["Lottery", "Participants"]),
            ("CHAT", ["Chat", "Commands"]),
        ]

        self._nav_btns = []
        self._content_stack = QStackedWidget()

        for section_name, items in sections:
            # Заголовок секции
            lbl = QLabel(section_name)
            lbl.setStyleSheet(f"""
                color: {TEXT_MAIN}; font-size: 10px; font-weight: 700;
                letter-spacing: 1.2px; padding: 10px 20px 4px;
                font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;
            """)
            sidebar_layout.addWidget(lbl)

            for item_name in items:
                btn = QPushButton(item_name)
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent; border: none;
                        border-left: 2px solid transparent;
                        color: {TEXT_SEC}; font-size: 12px; font-weight: 600;
                        letter-spacing: 0.3px; padding: 8px 0 8px 20px;
                        text-align: left;
                        font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;
                    }}
                    QPushButton:hover {{ color: {TEXT_MAIN}; }}
                """)
                sidebar_layout.addWidget(btn)
                self._nav_btns.append(btn)

                # Контент для каждой секции (заглушка)
                content_page = QWidget()
                content_page.setStyleSheet("background: transparent;")
                content_layout = QVBoxLayout(content_page)
                content_layout.setContentsMargins(40, 30, 40, 30)
                placeholder = QLabel(f"[{item_name}] Settings content here")
                placeholder.setStyleSheet(f"color: {TEXT_SEC}; font-size: 14px;")
                content_layout.addWidget(placeholder)
                content_layout.addStretch(1)
                self._content_stack.addWidget(content_page)

        sidebar_layout.addStretch(1)

        layout.addWidget(self._content_stack, 1)

        # Связываем кнопки с контентом
        for i, btn in enumerate(self._nav_btns):
            btn.clicked.connect(lambda checked, idx=i: self._content_stack.setCurrentIndex(idx))


class LogsTabTemplate(QWidget):
    """
    [T005]  Вкладка логов: таблица + экспорт
    ───────
    Как в wheel_mixin.py._setup_logs_tab():
      header → QScrollArea с логами → GlowButton("EXPORT LOGS")
    Использование:
        logs_page = LogsTabTemplate()
        stack.addWidget(logs_page)
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 30, 50, 30)

        # Заголовок таблицы
        header = QFrame()
        header.setObjectName("cardLight")
        header_layout = QHBoxLayout(header)
        for text in ["WINNER", "PRIZE", "WHEEL", "TIMESTAMP"]:
            lbl = QLabel(text)
            lbl.setStyleSheet("font-weight: bold;")
            header_layout.addWidget(lbl)
        layout.addWidget(header)

        # Список логов
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { background-color: transparent; border: none; }
        """)
        self.logs_container = QWidget()
        self.logs_container.setStyleSheet("background-color: transparent;")
        self.logs_layout = QVBoxLayout(self.logs_container)
        self.logs_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll.setWidget(self.logs_container)
        layout.addWidget(scroll, 1)

        # Кнопка экспорта
        self.btn_row = QHBoxLayout()
        self.btn_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btn_row.setSpacing(12)
        layout.addLayout(self.btn_row)

        self.export_btn = GlowButton("EXPORT LOGS", "outline")
        self.btn_row.addWidget(self.export_btn)


# ============================================================================
#                               ЗАПУСК
# ============================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Глобальный шрифт
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = UiKitDemo()
    window.show()

    sys.exit(app.exec())