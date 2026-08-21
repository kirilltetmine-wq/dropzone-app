from gui.templates.wheel._navigation import WheelMixinNavigation
from gui.templates.wheel._cards import WheelMixinCards
from gui.templates.wheel._values import WheelMixinValues
from gui.templates.wheel._colors import WheelMixinColors
from gui.templates.wheel._items import WheelMixinItems
from gui.templates.wheel._spin_logs_io import WheelMixinSpinLogsIO


class WheelMixin(
    WheelMixinNavigation,
    WheelMixinCards,
    WheelMixinValues,
    WheelMixinColors,
    WheelMixinItems,
    WheelMixinSpinLogsIO,
):
    _skip_value_batch_warning = False