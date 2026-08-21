"""ui_kit_index — реестр всех UI-компонентов. Словарь UI_KIT_REGISTRY: код → (класс, описание)"""
from .ui_kit_buttons import (
    GlowButton, HoverIconButton, RoundedButton, TabButton, SplitSendButton,
)
from .ui_kit_inputs import (
    ToggleSwitch, ModernSlider, RoundedLineEdit, WheelDropdown, PlatformDropdown,
)
from .ui_kit_containers import RoundedFrame, RoundedListView
from .ui_kit_primitives import (
    PlatformIcon, BadgeLabel, MessageRow, SystemMessage,
    DragHandle, DropContainer, _DragHandle,
)
from .ui_kit_dialogs import (
    ModernDialog, ModernColorPicker, ModernItemPicker,
    DeleteConfirmDialog, BatchValueDialog, SegmentInfoPopup,
    ImageEditorDialog,
)
from .ui_kit_widgets import (
    WheelWidget, DiceCubeWidget, DicePanel, WheelTabPage, ChatWidget,
)
from .ui_kit_windows import (
    TitleBar, SplashScreen, DetachedWindow,
    DetachableSection, DetachablePanel, DetachedConfigWindow,
)
from .ui_kit_pages import (
    TabBarTemplate, WheelTabTemplate, LotteryTabTemplate,
    ConfigTabTemplate, LogsTabTemplate,
)

UI_KIT_REGISTRY = {
    "U001": (GlowButton, "GlowButton(style='lime') — кнопка с зелёным свечением"),
    "U002": (GlowButton, "GlowButton(style='ghost') — прозрачная кнопка с рамкой"),
    "U003": (GlowButton, "GlowButton(style='danger') — красная кнопка удаления"),
    "U004": (GlowButton, "GlowButton(style='outline') — кнопка с обводкой"),
    "U005": (GlowButton, "GlowButton(style='cyan') — кнопка с голубым свечением"),
    "U006": (HoverIconButton, "HoverIconButton — иконка с заменой при наведении"),
    "U007": (RoundedButton, "RoundedButton(text) — скруглённая кнопка"),
    "U008": (TabButton, "TabButton(text) — кнопка вкладки"),
    "U009": (None, "TitleBarButton — в titlebar.py"),
    "U010": (SplitSendButton, "SplitSendButton — кнопка отправки с разделителем"),
    "U011": (ToggleSwitch, "ToggleSwitch(True) — переключатель ВКЛ"),
    "U012": (ToggleSwitch, "ToggleSwitch(False) — переключатель ВЫКЛ"),
    "U013": (ModernSlider, "ModernSlider() — ползунок (0-100)"),
    "U014": (ModernSlider, "ModernSlider(0, 255) — ползунок (0-255)"),
    "U015": (RoundedLineEdit, "RoundedLineEdit() — поле ввода"),
    "U016": (WheelDropdown, "WheelDropdown() — выпадающий список колёс"),
    "U017": (None, "ChatInput — в chat_widget.py"),
    "U018": (RoundedFrame, "RoundedFrame() — скруглённый фрейм"),
    "U019": (RoundedListView, "RoundedListView() — скруглённый список"),
    "U020": (DropContainer, "DropContainer() — контейнер с drag-and-drop"),
    "U021": (DragHandle, "DragHandle(index) — ручка перетаскивания"),
    "U022": (MessageRow, "MessageRow(author, text) — строка сообщения"),
    "U023": (SystemMessage, "SystemMessage(tag, text) — системное сообщение"),
    "U024": (ModernDialog, "ModernDialog(parent, title, msg) — модальное окно"),
    "U025": (ModernColorPicker, "ModernColorPicker(parent, color) — выбор цвета"),
    "U026": (ModernItemPicker, "ModernItemPicker(parent, color, img) — выбор предмета"),
    "U027": (DeleteConfirmDialog, "DeleteConfirmDialog(parent, count) — подтверждение удаления"),
    "U028": (BatchValueDialog, "BatchValueDialog(parent) — batch-изменение"),
    "U029": (SegmentInfoPopup, "SegmentInfoPopup(parent, prize, chance) — попап приза"),
    "U030": (ImageEditorDialog, "ImageEditorDialog(parent, path) — редактор изображений"),
    "U031": (WheelWidget, "WheelWidget() — колесо фортуны"),
    "U032": (DiceCubeWidget, "DiceCubeWidget() — кубик дайса"),
    "U033": (DicePanel, "DicePanel(parent) — панель дайсов"),
    "U034": (ChatWidget, "ChatWidget(parent) — чат стрима"),
    "U035": (WheelTabPage, "WheelTabPage() — страница кейсов"),
    "U036": (PlatformDropdown, "PlatformDropdown() — выпадающий список платформ"),
    "U037": (BadgeLabel, "BadgeLabel('MOD') — бейдж пользователя"),
    "U038": (TitleBar, "TitleBar(parent) — заголовок окна"),
    "U039": (SplashScreen, "SplashScreen(parent) — заставка"),
    "U040": (DetachedWindow, "DetachedWindow(content, title) — оторванное окно"),
    "U040B": (DetachedConfigWindow, "DetachedConfigWindow(content, title) — оторванный конфиг"),
    "U041": (DetachableSection, "DetachableSection(content, title) — отделяемая секция"),
    "U041B": (DetachablePanel, "DetachablePanel(content, title) — отделяемая панель"),
    "U042": (_DragHandle, "_DragHandle(dialog) — drag handle окна"),
    "U043": (PlatformIcon, "PlatformIcon(icon_path) — иконка платформы"),
    "T001": (TabBarTemplate, "TabBarTemplate() — панель вкладок"),
    "T002": (WheelTabTemplate, "WheelTabTemplate() — вкладка колеса"),
    "T003": (LotteryTabTemplate, "LotteryTabTemplate() — вкладка лотереи"),
    "T004": (ConfigTabTemplate, "ConfigTabTemplate() — вкладка настроек"),
    "T005": (LogsTabTemplate, "LogsTabTemplate() — вкладка логов"),
}