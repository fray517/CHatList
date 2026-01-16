"""Диалог для улучшения промтов с помощью AI."""

from typing import Optional, Dict, Any

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLabel, QComboBox, QMessageBox, QProgressBar, QTabWidget,
    QWidget, QDialogButtonBox
)

from src.models import Model, get_active_models
from src.prompt_enhancer import (
    enhance_prompt_full, enhance_prompt, generate_alternatives,
    adapt_prompt_for_type
)


class EnhancementWorker(QThread):
    """Поток для выполнения улучшения промта."""

    finished = pyqtSignal(dict)
    progress = pyqtSignal(str)

    def __init__(
        self,
        prompt: str,
        model: Model,
        include_alternatives: bool = True,
        include_adaptations: bool = True
    ):
        """Инициализация потока."""
        super().__init__()
        self.prompt = prompt
        self.model = model
        self.include_alternatives = include_alternatives
        self.include_adaptations = include_adaptations

    def run(self):
        """Выполнение улучшения."""
        try:
            self.progress.emit('Улучшение основного промта...')
            results = enhance_prompt_full(
                self.prompt,
                self.model,
                self.include_alternatives,
                self.include_adaptations
            )
            self.finished.emit(results)
        except Exception as e:
            self.finished.emit({
                'error': str(e),
                'original_prompt': self.prompt
            })


class PromptEnhancerDialog(QDialog):
    """Диалог для отображения результатов улучшения промта."""

    def __init__(self, parent=None, initial_prompt: str = ''):
        """Инициализация диалога."""
        super().__init__(parent)
        self.setWindowTitle('Улучшение промта')
        self.setMinimumSize(900, 700)
        self.initial_prompt = initial_prompt
        self.selected_prompt: Optional[str] = None
        self.results: Optional[Dict[str, Any]] = None
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Выбор модели
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel('Модель для улучшения:'))
        self.model_combo = QComboBox()
        self.load_models()
        model_layout.addWidget(self.model_combo)
        layout.addLayout(model_layout)

        # Исходный промт
        layout.addWidget(QLabel('<b>Исходный промт:</b>'))
        self.original_text = QTextEdit()
        self.original_text.setPlainText(self.initial_prompt)
        self.original_text.setReadOnly(True)
        self.original_text.setMaximumHeight(100)
        layout.addWidget(self.original_text)

        # Индикатор загрузки
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_label = QLabel()
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar)

        # Вкладки для результатов
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Вкладка "Улучшенный"
        self.enhanced_tab = self.create_enhanced_tab()
        self.tabs.addTab(self.enhanced_tab, 'Улучшенный')

        # Вкладка "Альтернативы"
        self.alternatives_tab = self.create_alternatives_tab()
        self.tabs.addTab(self.alternatives_tab, 'Альтернативы')

        # Вкладка "Адаптации"
        self.adaptations_tab = self.create_adaptations_tab()
        self.tabs.addTab(self.adaptations_tab, 'Адаптации')

        # Кнопки
        buttons_layout = QHBoxLayout()
        self.enhance_button = QPushButton('Улучшить промт')
        self.enhance_button.clicked.connect(self.on_enhance_clicked)
        buttons_layout.addWidget(self.enhance_button)

        buttons_layout.addStretch()

        self.use_button = QPushButton('Использовать выбранный')
        self.use_button.clicked.connect(self.on_use_clicked)
        self.use_button.setEnabled(False)
        buttons_layout.addWidget(self.use_button)

        layout.addLayout(buttons_layout)

        # Кнопки диалога
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def load_models(self):
        """Загрузить список активных моделей."""
        models = get_active_models()
        for model in models:
            self.model_combo.addItem(model.name, model)

    def create_enhanced_tab(self) -> QWidget:
        """Создать вкладку с улучшенным промтом."""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        self.enhanced_text = QTextEdit()
        self.enhanced_text.setReadOnly(True)
        layout.addWidget(self.enhanced_text)

        use_button = QPushButton('Использовать этот вариант')
        use_button.clicked.connect(
            lambda: self.select_prompt(self.enhanced_text.toPlainText())
        )
        layout.addWidget(use_button)

        return widget

    def create_alternatives_tab(self) -> QWidget:
        """Создать вкладку с альтернативными вариантами."""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        self.alternatives_texts = []
        for i in range(3):
            layout.addWidget(QLabel(f'<b>Вариант {i + 1}:</b>'))
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setMaximumHeight(150)
            self.alternatives_texts.append(text_edit)
            layout.addWidget(text_edit)

            use_button = QPushButton(f'Использовать вариант {i + 1}')
            use_button.clicked.connect(
                lambda checked, idx=i: self.select_prompt(
                    self.alternatives_texts[idx].toPlainText()
                )
            )
            layout.addWidget(use_button)

        return widget

    def create_adaptations_tab(self) -> QWidget:
        """Создать вкладку с адаптированными версиями."""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Адаптация для кода
        layout.addWidget(QLabel('<b>Для программирования:</b>'))
        self.code_text = QTextEdit()
        self.code_text.setReadOnly(True)
        self.code_text.setMaximumHeight(120)
        layout.addWidget(self.code_text)
        code_button = QPushButton('Использовать для программирования')
        code_button.clicked.connect(
            lambda: self.select_prompt(self.code_text.toPlainText())
        )
        layout.addWidget(code_button)

        # Адаптация для анализа
        layout.addWidget(QLabel('<b>Для аналитических задач:</b>'))
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        self.analysis_text.setMaximumHeight(120)
        layout.addWidget(self.analysis_text)
        analysis_button = QPushButton('Использовать для анализа')
        analysis_button.clicked.connect(
            lambda: self.select_prompt(self.analysis_text.toPlainText())
        )
        layout.addWidget(analysis_button)

        # Адаптация для креатива
        layout.addWidget(QLabel('<b>Для креативных задач:</b>'))
        self.creative_text = QTextEdit()
        self.creative_text.setReadOnly(True)
        self.creative_text.setMaximumHeight(120)
        layout.addWidget(self.creative_text)
        creative_button = QPushButton('Использовать для креатива')
        creative_button.clicked.connect(
            lambda: self.select_prompt(self.creative_text.toPlainText())
        )
        layout.addWidget(creative_button)

        return widget

    def on_enhance_clicked(self):
        """Обработчик нажатия кнопки улучшения."""
        prompt = self.original_text.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(
                self,
                'Предупреждение',
                'Введите промт для улучшения!'
            )
            return

        model = self.model_combo.currentData()
        if not model:
            QMessageBox.warning(
                self,
                'Предупреждение',
                'Выберите модель!'
            )
            return

        # Показ индикатора загрузки
        self.progress_bar.setVisible(True)
        self.progress_label.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.enhance_button.setEnabled(False)

        # Запуск потока улучшения
        self.worker = EnhancementWorker(prompt, model)
        self.worker.progress.connect(self.on_progress_update)
        self.worker.finished.connect(self.on_enhancement_finished)
        self.worker.start()

    def on_progress_update(self, message: str):
        """Обновление сообщения о прогрессе."""
        self.progress_label.setText(message)

    def on_enhancement_finished(self, results: Dict[str, Any]):
        """Обработчик завершения улучшения."""
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        self.enhance_button.setEnabled(True)
        self.results = results

        if 'error' in results:
            QMessageBox.critical(
                self,
                'Ошибка',
                f'Ошибка при улучшении промта:\n{results["error"]}'
            )
            return

        # Отображение улучшенного промта
        if results.get('enhanced_prompt'):
            self.enhanced_text.setPlainText(results['enhanced_prompt'])

        # Отображение альтернатив
        alternatives = results.get('alternatives', [])
        for i, alt in enumerate(alternatives):
            if i < len(self.alternatives_texts) and alt:
                self.alternatives_texts[i].setPlainText(alt)

        # Отображение адаптаций
        adaptations = results.get('adaptations', {})
        if adaptations.get('code'):
            self.code_text.setPlainText(adaptations['code'])
        if adaptations.get('analysis'):
            self.analysis_text.setPlainText(adaptations['analysis'])
        if adaptations.get('creative'):
            self.creative_text.setPlainText(adaptations['creative'])

        self.use_button.setEnabled(True)
        QMessageBox.information(
            self,
            'Успех',
            'Промт успешно улучшен!'
        )

    def select_prompt(self, prompt_text: str):
        """Выбрать промт для использования."""
        if prompt_text.strip():
            self.selected_prompt = prompt_text.strip()
            self.use_button.setEnabled(True)

    def on_use_clicked(self):
        """Обработчик использования выбранного промта."""
        # Определяем, какой промт выбран
        current_tab = self.tabs.currentIndex()

        if current_tab == 0:  # Улучшенный
            selected = self.enhanced_text.toPlainText().strip()
        elif current_tab == 1:  # Альтернативы
            # Находим первый непустой вариант
            selected = None
            for text_edit in self.alternatives_texts:
                text = text_edit.toPlainText().strip()
                if text:
                    selected = text
                    break
        elif current_tab == 2:  # Адаптации
            # Используем выбранный ранее или первый доступный
            if self.selected_prompt:
                selected = self.selected_prompt
            else:
                # Пробуем найти первый непустой
                for text_edit in [
                    self.code_text, self.analysis_text, self.creative_text
                ]:
                    text = text_edit.toPlainText().strip()
                    if text:
                        selected = text
                        break
        else:
            selected = self.selected_prompt

        if selected and selected.strip():
            self.selected_prompt = selected.strip()
            self.accept()
        else:
            QMessageBox.warning(
                self,
                'Предупреждение',
                'Выберите вариант промта для использования!'
            )
