"""ui_kit_dialogs — импорт из оригиналов gui/dialogs/"""
from gui.dialogs.primitives import DragHandle, DropContainer
from gui.dialogs.modern_dialog import ModernDialog, show_info, ask_string
from gui.dialogs.color_picker import ModernColorPicker
from gui.dialogs.item_picker import ModernItemPicker
from gui.dialogs.confirm_dialogs import DeleteConfirmDialog, BatchValueDialog, SegmentInfoPopup
from gui.dialogs.image_editor import ImageEditorDialog, _ImageEditorPreview

U024 = ModernDialog
U025 = ModernColorPicker
U026 = ModernItemPicker
U027 = DeleteConfirmDialog
U028 = BatchValueDialog
U029 = SegmentInfoPopup
U030 = ImageEditorDialog