"""Диалог "О программе"."""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QDialogButtonBox
)
from PyQt5.QtCore import Qt


class AboutDialog(QDialog):
    """Диалог с информацией о программе."""

    def __init__(self, parent=None):
        """Инициализация диалога."""
        super().__init__(parent)
        self.setWindowTitle('О программе')
        self.setMinimumSize(500, 400)
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Название программы
        title_label = QLabel('ChatList')
        title_label.setStyleSheet(
            'font-size: 24px; font-weight: bold; color: #2980b9;'
        )
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Версия
        version_label = QLabel('Версия 1.0.0')
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)

        layout.addSpacing(20)

        # Описание
        description_label = QLabel(
            'Приложение для сравнения ответов различных нейросетей '
            'на один и тот же промт.\n\n'
            'Возможности:\n'
            '• Отправка промта в несколько нейросетей одновременно\n'
            '• Сравнение ответов в удобной таблице\n'
            '• Сохранение промтов и результатов\n'
            '• Управление моделями нейросетей\n'
            '• Просмотр истории промтов и результатов\n'
            '• Экспорт результатов в Markdown и JSON\n'
            '• AI-ассистент для улучшения промтов\n'
            '• Настройка темы и размера шрифта'
        )
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(description_label)

        layout.addSpacing(20)

        # Технологии
        tech_label = QLabel(
            '<b>Технологии:</b><br>'
            '• Python 3.11+<br>'
            '• PyQt5<br>'
            '• SQLite<br>'
            '• OpenRouter API'
        )
        tech_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(tech_label)

        layout.addSpacing(20)

        # Автор и лицензия
        author_label = QLabel(
            '<b>Лицензия:</b> См. файл LICENSE'
        )
        author_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(author_label)

        layout.addStretch()

        # Кнопка закрытия
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
