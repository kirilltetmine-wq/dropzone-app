import json

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QFileDialog,
)

from core.theme import (
    ACCENT_CYAN, ACCENT_LIME, CARD_COLOR, BG_COLOR,
    TEXT_SEC, BORDER_COLOR,
)
from core.storage import Storage
from ui_kit import GlowButton, ModernDialog, SegmentInfoPopup, show_info
from ui_kit.ui_kit_pages import LogsTabTemplate


class WheelMixinSpinLogsIO:
    """Spin animation, prize confirmation, logs, and wheel import/export."""

    def start_spin(self):
        self.wheel_widget.start_spin()
        name = self.winner_entry.text().strip()
        if name:
            self.wheel_widget._callback = lambda: self._show_confirm_prize_btn(True)

    def _show_confirm_prize_btn(self, visible):
        if hasattr(self, 'confirm_prize_btn'):
            self.confirm_prize_btn.setVisible(visible)

    def _confirm_prize(self):
        name = self.winner_entry.text().strip()
        if not name:
            show_info(self, "Info", "No winner name — nothing logged")
            self._show_confirm_prize_btn(False)
            return
        prize = self.wheel_widget.get_winner()
        if not prize:
            show_info(self, "Error", "No prize landed")
            return
        wheel_name = self._get_current_wheel_name()
        Storage.add_log(name, prize, wheel_name)
        show_info(self, "LOGGED", f"{name.upper()} won {prize} from {wheel_name}")
        self._current_winner = None
        self.winner_entry.clear()
        self._show_confirm_prize_btn(False)

    def on_segment_clicked(self, index, prize, chance):
        popup = SegmentInfoPopup(self, prize, chance)
        popup.show()

    def _setup_logs_tab(self):
        page = self.logs_page
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        template = LogsTabTemplate()
        layout.addWidget(template)
        template.export_btn.clicked.connect(self._export_logs_from_tab)
        clear_btn = GlowButton("CLEAR LOGS", "danger")
        clear_btn.clicked.connect(self.clear_history)
        template.btn_row.addWidget(clear_btn)
        self.logs_layout = template.logs_layout
        self.refresh_history()

    def refresh_history(self):
        for i in reversed(range(self.logs_layout.count())):
            item = self.logs_layout.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()
        for log in reversed(Storage.get_logs()):
            row = QFrame()
            row.setStyleSheet(f"""
                QFrame {{
                    background-color: {BG_COLOR};
                    border: none;
                    border-radius: 0;
                }}
            """)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(15, 8, 15, 8)
            for key in ['user', 'prize', 'wheel', 'date']:
                lbl = QLabel(log[key])
                if key == 'prize':
                    lbl.setStyleSheet(f"color: {ACCENT_CYAN};")
                elif key == 'date':
                    lbl.setStyleSheet(f"color: {TEXT_SEC};")
                row_layout.addWidget(lbl)
            self.logs_layout.addWidget(row)

    def _export_logs_from_tab(self):
        from core.storage import Storage
        logs = Storage.get_logs()
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Logs", "logs_export.json", "JSON (*.json)"
        )
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(logs, f, ensure_ascii=False, indent=4)
                show_info(self, "Success", f"Exported {len(logs)} log entries to {path}")
            except Exception as e:
                show_info(self, "Error", str(e))

    def clear_history(self):
        dialog = ModernDialog(self, "CLEAR", "Permanently clear history?")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            Storage.clear_logs()
            self.refresh_history()

    def _export_current_wheel(self):
        name = self._get_current_wheel_name()
        if not name:
            show_info(self, "Info", "No wheel selected")
            return
        wheels = Storage.get_wheels()
        segments = wheels.get(name, [])
        data = {
            "export_type": "single_wheel",
            "name": name,
            "segments": segments
        }
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Wheel", f"{name}.json", "JSON (*.json)"
        )
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                show_info(self, "Success", f"Wheel '{name}' exported to {path}")
            except Exception as e:
                show_info(self, "Error", str(e))

    def _import_wheel(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Wheel", "", "JSON (*.json)"
        )
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if not isinstance(data, dict):
                show_info(self, "Error", "Invalid file format")
                return
            wheel_name = data.get("name", "")
            segments = data.get("segments", [])
            if not isinstance(segments, list):
                show_info(self, "Error", "Invalid segments data")
                return
            if not wheel_name:
                wheel_name = Path(path).stem
            wheels = Storage.get_wheels()
            wheels[wheel_name] = segments
            Storage.save_wheels(wheels)
            self.refresh_wheels_list()
            wheels = Storage.get_wheels()
            names = list(wheels.keys())
            if wheel_name in names:
                self.wheel_combo.setCurrentIndex(names.index(wheel_name))
            show_info(self, "Success", f"Wheel '{wheel_name}' imported ({len(segments)} sectors)")
        except Exception as e:
            show_info(self, "Error", str(e))

    def _manage_wheel(self):
        dialog = QDialog(self, Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        dialog.setWindowTitle("Manage Wheel")
        dialog.setFixedSize(320, 200)
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        dialog.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        dialog.setStyleSheet(f"background: transparent;")
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(0, 0, 0, 0)
        card = QFrame(dialog)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 30px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(16)
        layout.addWidget(card)
        title = QLabel("MANAGE WHEEL")
        title.setStyleSheet(f"color: {ACCENT_CYAN}; font-size: 16px; font-weight: bold; border: none;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)
        name = self._get_current_wheel_name() or "—"
        info = QLabel(f"Current: {name}")
        info.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px; border: none;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(info)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addLayout(btn_layout)
        export_btn = GlowButton("EXPORT", "lime", dialog)
        export_btn.setFixedSize(120, 42)
        export_btn.clicked.connect(lambda: (dialog.accept(), self._export_current_wheel()))
        btn_layout.addWidget(export_btn)
        import_btn = GlowButton("IMPORT", "outline", dialog)
        import_btn.setFixedSize(120, 42)
        import_btn.clicked.connect(lambda: (dialog.accept(), self._import_wheel()))
        btn_layout.addWidget(import_btn)
        dialog.exec()