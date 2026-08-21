import json

from pathlib import Path

from PyQt6.QtCore import Qt

from PyQt6.QtWidgets import (
    QDialog, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QMessageBox,
)

from core.theme import CARD_COLOR, BORDER_COLOR, ACCENT_CYAN, TEXT_SEC

from ui_kit import GlowButton, ModernDialog, show_info, ask_string

from core.storage import Storage


class CaseStorageMixin:

    def _case_save(self):

        name = self._get_current_case_name()

        if name and hasattr(self, '_case_prizes'):

            cases = Storage.get_cases()

            cases[name] = self._case_prizes

            Storage.save_cases(cases)

    def _case_add_case(self):

        name = ask_string(self, "NEW CASE", "Enter case name:", placeholder="E.g. Daily Case")

        if name:

            cases = Storage.get_cases()

            cases[name] = [{"name": "PRIZE 1", "chance": 100, "color": "#00F5FF"}]

            Storage.save_cases(cases)

            self.refresh_cases_list()

            keys = list(self._case_data.keys())

            if name in keys:

                idx = keys.index(name)

                self.case_combo.setCurrentIndex(idx)

                self._on_case_selected(idx)

    def _case_delete_case(self):

        name = self._get_current_case_name()

        if name:

            dialog = ModernDialog(self, "DELETE", f"Permanently delete case '{name}'?")

            if dialog.exec() == QDialog.DialogCode.Accepted:

                cases = Storage.get_cases()

                if name in cases:

                    del cases[name]

                    Storage.save_cases(cases)

                    self.refresh_cases_list()

    def _case_rename_case(self):

        old_name = self._get_current_case_name()

        if not old_name:

            return

        new_name = ask_string(self, "RENAME CASE", "Enter new name:", placeholder=old_name)

        if new_name and new_name != old_name:

            cases = Storage.get_cases()

            if new_name in cases:

                QMessageBox.warning(self, "ERROR", f"Case '{new_name}' already exists!")

                return

            if old_name in cases:

                cases[new_name] = cases.pop(old_name)

                Storage.save_cases(cases)

                self.refresh_cases_list()

                keys = list(self._case_data.keys())

                if new_name in keys:

                    idx = keys.index(new_name)

                    self.case_combo.setCurrentIndex(idx)

                    self._on_case_selected(idx)

    def _prev_case(self):

        self.case_combo.setCurrentIndex(max(0, self.case_combo.currentIndex() - 1))

    def _next_case(self):

        self.case_combo.setCurrentIndex(min(self.case_combo.count() - 1, self.case_combo.currentIndex() + 1))

    def _case_confirm_prize(self):

        winner = self._case_winner_entry.text().strip() if hasattr(self, '_case_winner_entry') else ""

        if not winner:

            return

        prize = getattr(self, '_case_last_prize', '')

        if not prize:

            show_info(self, "Error", "No prize landed")

            return

        case_name = self._get_current_case_name()

        Storage.add_log(winner, prize, case_name)

        show_info(self, "LOGGED", f"{winner.upper()} won {prize} from {case_name}")

        self._case_confirm_btn.setVisible(False)

        self._case_winner_entry.clear()

        self._case_last_prize = None

        self.refresh_history()

    def refresh_cases_list(self):

        cases = Storage.get_cases()

        self._case_data = cases

        self.case_combo.clear()

        items = list(cases.keys())

        if items:

            display_items = [f"{n} ({len(cases[n])})" for n in items]

            self.case_combo.addItems(display_items)

            self.case_combo.setCurrentIndex(0)

            self._case_prizes = cases[items[0]]

            self.case_combo.setPopupData(cases)

        else:

            self._case_prizes = []

        self._case_strip.set_prizes(self._case_prizes)

        self._case_render_cards()

    def _get_current_case_name(self):

        if not hasattr(self, '_case_data') or not self._case_data:

            return ""

        keys = list(self._case_data.keys())

        idx = self.case_combo.currentIndex()

        if 0 <= idx < len(keys):

            return keys[idx]

        return ""

    def _export_current_case(self):

        name = self._get_current_case_name()

        if not name:

            show_info(self, "Info", "No case selected")

            return

        prizes = self._case_data.get(name, [])

        data = {

            "export_type": "single_case",

            "name": name,

            "prizes": prizes

        }

        path, _ = QFileDialog.getSaveFileName(

            self, "Export Case", f"{name}.json", "JSON (*.json)"

        )

        if path:

            try:

                with open(path, 'w', encoding='utf-8') as f:

                    json.dump(data, f, ensure_ascii=False, indent=4)

                show_info(self, "Success", f"Case '{name}' exported to {path}")

            except Exception as e:

                show_info(self, "Error", str(e))

    def _import_case(self):

        path, _ = QFileDialog.getOpenFileName(

            self, "Import Case", "", "JSON (*.json)"

        )

        if not path:

            return

        try:

            with open(path, 'r', encoding='utf-8') as f:

                data = json.load(f)

            if not isinstance(data, dict):

                show_info(self, "Error", "Invalid file format")

                return

            case_name = data.get("name", "")

            prizes = data.get("prizes", [])

            if not isinstance(prizes, list):

                show_info(self, "Error", "Invalid prizes data")

                return

            if not case_name:

                case_name = Path(path).stem

            cases = Storage.get_cases()

            cases[case_name] = prizes

            Storage.save_cases(cases)

            self.refresh_cases_list()

            show_info(self, "Success", f"Case '{case_name}' imported ({len(prizes)} prizes)")

        except Exception as e:

            show_info(self, "Error", str(e))

    def _manage_case(self):

        dialog = QDialog(self, Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)

        dialog.setWindowTitle("Manage Case")

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

        title = QLabel("MANAGE CASE")

        title.setStyleSheet(f"color: {ACCENT_CYAN}; font-size: 16px; font-weight: bold; border: none;")

        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_layout.addWidget(title)

        name = self._get_current_case_name() or "—"

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

        export_btn.clicked.connect(lambda: (dialog.accept(), self._export_current_case()))

        btn_layout.addWidget(export_btn)

        import_btn = GlowButton("IMPORT", "outline", dialog)

        import_btn.setFixedSize(120, 42)

        import_btn.clicked.connect(lambda: (dialog.accept(), self._import_case()))

        btn_layout.addWidget(import_btn)

        dialog.exec()