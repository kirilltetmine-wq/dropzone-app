"""
ui_kit — модульная система UI-компонентов проекта Dropzone
Все компоненты импортируются из оригинальных gui-файлов.
"""

from .ui_kit_buttons import (
    GlowButton, HoverIconButton, RoundedButton, TabButton, SplitSendButton,
    U001, U002, U003, U004, U005, U006, U007, U008, U009, U010,
)
from .ui_kit_inputs import (
    ToggleSwitch, ModernSlider, RoundedLineEdit, WheelDropdown, WheelPopup,
    PlatformDropdown,
    U011, U012, U013, U014, U015, U016, U017, U036,
)
from .ui_kit_containers import (
    RoundedFrame, RoundedListView,
    U018, U019,
)
from .ui_kit_primitives import (
    PlatformIcon, BadgeLabel, MessageRow, SystemMessage,
    DragHandle, DropContainer, _DragHandle,
    U020, U021, U022, U023, U037, U042, U043,
)
from .ui_kit_dialogs import (
    ModernDialog, ModernColorPicker, ModernItemPicker,
    DeleteConfirmDialog, BatchValueDialog, SegmentInfoPopup,
    ImageEditorDialog, _ImageEditorPreview,
    show_info, ask_string,
    U024, U025, U026, U027, U028, U029, U030,
)
from .ui_kit_widgets import (
    WheelWidget, DiceCubeWidget, DicePanel, WheelTabPage,
    ChatWidget,
    U031, U032, U033, U034, U035,
)
from .ui_kit_windows import (
    TitleBar, SplashScreen, DetachedWindow,
    DetachableSection, DetachablePanel, DetachedConfigWindow,
    U038, U039, U040, U041, U041B, U040B,
)
from .ui_kit_pages import (
    TabBarTemplate, WheelTabTemplate, LotteryTabTemplate,
    ConfigTabTemplate, LogsTabTemplate,
    T001, T002, T003, T004, T005,
)
from .ui_kit_index import UI_KIT_REGISTRY