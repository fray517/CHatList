"""Диалог настроек приложения."""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QSpinBox, QFormLayout, QDialogButtonBox,
    QMessageBox
)

from src import db


class SettingsDialog(QDialog):
    """Диалог настроек приложения."""

    def __init__(self, parent=None):
        """Инициализация диалога."""
        super().__init__(parent)
        self.setWindowTitle('Настройки')
        self.setMinimumWidth(400)
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        """Инициализация интерфейса."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        form = QFormLayout()

        # Выбор темы
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(['Светлая', 'Тёмная'])
        form.addRow('Тема:', self.theme_combo)

        # Размер шрифта
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setMinimum(8)
        self.font_size_spin.setMaximum(24)
        self.font_size_spin.setValue(10)
        self.font_size_spin.setSuffix(' pt')
        form.addRow('Размер шрифта:', self.font_size_spin)

        layout.addLayout(form)

        # Кнопки
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.save_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def load_settings(self):
        """Загрузить настройки из базы данных."""
        theme = db.get_setting('theme', 'light')
        font_size = db.get_setting('font_size', '10')

        # Установка темы
        if theme == 'dark':
            self.theme_combo.setCurrentIndex(1)
        else:
            self.theme_combo.setCurrentIndex(0)

        # Установка размера шрифта
        try:
            self.font_size_spin.setValue(int(font_size))
        except (ValueError, TypeError):
            self.font_size_spin.setValue(10)

    def save_and_accept(self):
        """Сохранить настройки и закрыть диалог."""
        # Сохранение темы
        theme = 'dark' if self.theme_combo.currentIndex() == 1 else 'light'
        db.set_setting('theme', theme)

        # Сохранение размера шрифта
        font_size = str(self.font_size_spin.value())
        db.set_setting('font_size', font_size)

        self.accept()
