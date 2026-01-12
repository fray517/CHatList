"""Диалоги для просмотра истории промтов и результатов."""

from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QMessageBox, QHeaderView,
    QDialogButtonBox, QTextEdit, QComboBox, QFormLayout
)

from src import db


class PromptsHistoryDialog(QDialog):
    """Диалог просмотра истории промтов."""

    def __init__(self, parent=None):
        """Инициализация диалога."""
        super().__init__(parent)
        self.setWindowTitle('История промтов')
        self.setMinimumSize(900, 600)
        self.selected_prompt_id: Optional[int] = None
        self.init_ui()
        self.load_prompts()

    def init_ui(self):
        """Инициализация интерфейса."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Поиск
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel('Поиск:'))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Поиск по тексту или тегам...')
        self.search_input.textChanged.connect(self.on_search_changed)
        search_layout.addWidget(self.search_input)

        # Сортировка
        search_layout.addWidget(QLabel('Сортировка:'))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            'По дате (новые сначала)',
            'По дате (старые сначала)',
            'По тексту (А-Я)',
            'По тексту (Я-А)'
        ])
        self.sort_combo.currentIndexChanged.connect(self.load_prompts)
        search_layout.addWidget(self.sort_combo)

        layout.addLayout(search_layout)

        # Таблица промтов
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            'Дата', 'Промт', 'Теги', 'Действия'
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

        # Кнопки
        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton('Добавить')
        self.add_button.clicked.connect(self.on_add_clicked)
        buttons_layout.addWidget(self.add_button)

        self.edit_button = QPushButton('Редактировать')
        self.edit_button.clicked.connect(self.on_edit_clicked)
        buttons_layout.addWidget(self.edit_button)

        self.use_button = QPushButton('Использовать выбранный')
        self.use_button.clicked.connect(self.on_use_clicked)
        buttons_layout.addWidget(self.use_button)

        self.delete_button = QPushButton('Удалить')
        self.delete_button.clicked.connect(self.on_delete_clicked)
        buttons_layout.addWidget(self.delete_button)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        # Кнопки диалога
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def load_prompts(self):
        """Загрузить список промтов."""
        search_text = self.search_input.text().strip()
        sort_index = self.sort_combo.currentIndex()

        if search_text:
            prompts = db.search_prompts(search_text)
        else:
            order_by = {
                0: 'date DESC',
                1: 'date ASC',
                2: 'prompt ASC',
                3: 'prompt DESC'
            }.get(sort_index, 'date DESC')
            prompts = db.get_prompts(order_by=order_by)

        self.table.setRowCount(len(prompts))

        for row, prompt in enumerate(prompts):
            # Дата
            date_item = QTableWidgetItem(prompt['date'])
            date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, date_item)

            # Промт
            prompt_text = prompt['prompt']
            preview = prompt_text[:100] + '...' if len(prompt_text) > 100 else prompt_text
            prompt_item = QTableWidgetItem(preview)
            prompt_item.setFlags(prompt_item.flags() & ~Qt.ItemIsEditable)
            prompt_item.setData(Qt.UserRole, prompt['id'])
            self.table.setItem(row, 1, prompt_item)

            # Теги
            tags = prompt.get('tags', '') or ''
            tags_item = QTableWidgetItem(tags)
            tags_item.setFlags(tags_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 2, tags_item)

            # Кнопки действий
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(2, 2, 2, 2)
            actions_widget.setLayout(actions_layout)

            view_button = QPushButton('Просмотр')
            view_button.clicked.connect(
                lambda checked, p=prompt: self.view_prompt(p)
            )
            actions_layout.addWidget(view_button)

            edit_button = QPushButton('Редактировать')
            edit_button.clicked.connect(
                lambda checked, p=prompt: self.edit_prompt(p)
            )
            actions_layout.addWidget(edit_button)

            self.table.setCellWidget(row, 3, actions_widget)

    def on_search_changed(self):
        """Обработчик изменения поискового запроса."""
        self.load_prompts()

    def view_prompt(self, prompt: dict):
        """Просмотр полного текста промта."""
        dialog = QDialog(self)
        dialog.setWindowTitle('Просмотр промта')
        dialog.setMinimumSize(600, 400)

        layout = QVBoxLayout()
        dialog.setLayout(layout)

        # Текст промта
        text_edit = QTextEdit()
        text_edit.setPlainText(prompt['prompt'])
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)

        # Теги
        if prompt.get('tags'):
            tags_label = QLabel(f'Теги: {prompt["tags"]}')
            layout.addWidget(tags_label)

        # Кнопка закрытия
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.exec_()

    def on_use_clicked(self):
        """Использовать выбранный промт."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'Предупреждение', 'Выберите промт!')
            return

        prompt_item = self.table.item(current_row, 1)
        if prompt_item:
            self.selected_prompt_id = prompt_item.data(Qt.UserRole)
            self.accept()

    def on_delete_clicked(self):
        """Удалить выбранный промт."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'Предупреждение', 'Выберите промт!')
            return

        prompt_item = self.table.item(current_row, 1)
        if prompt_item:
            prompt_id = prompt_item.data(Qt.UserRole)
            prompt = db.get_prompt_by_id(prompt_id)

            if prompt:
                reply = QMessageBox.question(
                    self,
                    'Подтверждение',
                    f'Удалить промт "{prompt["prompt"][:50]}..."?',
                    QMessageBox.Yes | QMessageBox.No
                )

                if reply == QMessageBox.Yes:
                    db.delete_prompt(prompt_id)
                    self.load_prompts()

    def on_add_clicked(self):
        """Обработчик добавления промта."""
        dialog = PromptEditDialog(self, None)
        if dialog.exec_() == QDialog.Accepted:
            self.load_prompts()

    def on_edit_clicked(self):
        """Обработчик редактирования промта."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'Предупреждение', 'Выберите промт!')
            return

        prompt_item = self.table.item(current_row, 1)
        if prompt_item:
            prompt_id = prompt_item.data(Qt.UserRole)
            prompt = db.get_prompt_by_id(prompt_id)
            if prompt:
                dialog = PromptEditDialog(self, prompt)
                if dialog.exec_() == QDialog.Accepted:
                    self.load_prompts()

    def edit_prompt(self, prompt: dict):
        """Редактировать промт из кнопки в таблице."""
        dialog = PromptEditDialog(self, prompt)
        if dialog.exec_() == QDialog.Accepted:
            self.load_prompts()


class ResultsHistoryDialog(QDialog):
    """Диалог просмотра истории результатов."""

    def __init__(self, parent=None):
        """Инициализация диалога."""
        super().__init__(parent)
        self.setWindowTitle('История результатов')
        self.setMinimumSize(1000, 700)
        self.init_ui()
        self.load_results()

    def init_ui(self):
        """Инициализация интерфейса."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Фильтры
        filters_layout = QHBoxLayout()
        filters_layout.addWidget(QLabel('Поиск:'))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Поиск по тексту ответа...')
        self.search_input.textChanged.connect(self.load_results)
        filters_layout.addWidget(self.search_input)

        filters_layout.addWidget(QLabel('Промт:'))
        self.prompt_combo = QComboBox()
        self.prompt_combo.addItem('Все промты', None)
        self.load_prompts_combo()
        self.prompt_combo.currentIndexChanged.connect(self.load_results)
        filters_layout.addWidget(self.prompt_combo)

        filters_layout.addWidget(QLabel('Модель:'))
        self.model_combo = QComboBox()
        self.model_combo.addItem('Все модели', None)
        self.load_models_combo()
        self.model_combo.currentIndexChanged.connect(self.load_results)
        filters_layout.addWidget(self.model_combo)

        layout.addLayout(filters_layout)

        # Таблица результатов
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            'Дата', 'Промт', 'Модель', 'Ответ', 'Действия'
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

        # Кнопки
        buttons_layout = QHBoxLayout()
        self.export_button = QPushButton('Экспорт выбранных')
        self.export_button.clicked.connect(self.on_export_clicked)
        buttons_layout.addWidget(self.export_button)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        # Кнопки диалога
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def load_prompts_combo(self):
        """Загрузить список промтов в комбобокс."""
        prompts = db.get_prompts(limit=100)
        for prompt in prompts:
            preview = prompt['prompt'][:50] + '...' if len(
                prompt['prompt']
            ) > 50 else prompt['prompt']
            self.prompt_combo.addItem(
                f"{prompt['date']} - {preview}",
                prompt['id']
            )

    def load_models_combo(self):
        """Загрузить список моделей в комбобокс."""
        from src.models import load_models
        models = load_models()
        for model in models:
            self.model_combo.addItem(model.name, model.id)

    def load_results(self):
        """Загрузить список результатов."""
        prompt_id = self.prompt_combo.currentData()
        model_id = self.model_combo.currentData()
        search_text = self.search_input.text().strip()

        if search_text:
            results = db.search_results(search_text)
            # Фильтрация по промту и модели
            if prompt_id:
                results = [r for r in results if r['prompt_id'] == prompt_id]
            if model_id:
                results = [r for r in results if r['model_id'] == model_id]
        else:
            results = db.get_results(prompt_id=prompt_id, model_id=model_id)

        self.table.setRowCount(len(results))

        for row, result in enumerate(results):
            # Дата
            date_item = QTableWidgetItem(result['created_at'])
            date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, date_item)

            # Промт
            prompt = db.get_prompt_by_id(result['prompt_id'])
            prompt_text = prompt['prompt'] if prompt else 'Неизвестно'
            preview = prompt_text[:50] + '...' if len(
                prompt_text
            ) > 50 else prompt_text
            prompt_item = QTableWidgetItem(preview)
            prompt_item.setFlags(prompt_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 1, prompt_item)

            # Модель
            from src.models import load_models
            models = load_models()
            model = next((m for m in models if m.id == result['model_id']), None)
            model_name = model.name if model else 'Неизвестно'
            model_item = QTableWidgetItem(model_name)
            model_item.setFlags(model_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 2, model_item)

            # Ответ
            response_text = result['response_text']
            preview = response_text[:100] + '...' if len(
                response_text
            ) > 100 else response_text
            response_item = QTableWidgetItem(preview)
            response_item.setFlags(response_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 3, response_item)

            # Кнопка просмотра
            view_button = QPushButton('Просмотр')
            view_button.clicked.connect(
                lambda checked, r=result: self.view_result(r)
            )
            self.table.setCellWidget(row, 4, view_button)

    def view_result(self, result: dict):
        """Просмотр полного результата."""
        dialog = QDialog(self)
        dialog.setWindowTitle('Просмотр результата')
        dialog.setMinimumSize(700, 500)

        layout = QVBoxLayout()
        dialog.setLayout(layout)

        # Информация о результате
        info_label = QLabel(
            f"Дата: {result['created_at']}\n"
            f"Модель: {self.get_model_name(result['model_id'])}\n"
            f"Промт: {self.get_prompt_text(result['prompt_id'])}"
        )
        layout.addWidget(info_label)

        # Текст ответа
        text_edit = QTextEdit()
        text_edit.setPlainText(result['response_text'])
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)

        # Кнопка закрытия
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.exec_()

    def get_model_name(self, model_id: int) -> str:
        """Получить название модели по ID."""
        from src.models import load_models
        models = load_models()
        model = next((m for m in models if m.id == model_id), None)
        return model.name if model else 'Неизвестно'

    def get_prompt_text(self, prompt_id: int) -> str:
        """Получить текст промта по ID."""
        prompt = db.get_prompt_by_id(prompt_id)
        return prompt['prompt'] if prompt else 'Неизвестно'

    def on_export_clicked(self):
        """Экспорт выбранных результатов."""
        selected_rows = set(
            index.row() for index in self.table.selectedIndexes()
        )
        if not selected_rows:
            QMessageBox.warning(
                self,
                'Предупреждение',
                'Выберите результаты для экспорта!'
            )
            return

        # Экспорт будет реализован в основном модуле
        QMessageBox.information(
            self,
            'Информация',
            f'Выбрано результатов: {len(selected_rows)}. '
            'Экспорт будет реализован в следующей версии.'
        )


class PromptEditDialog(QDialog):
    """Диалог для добавления/редактирования промта."""

    def __init__(self, parent=None, prompt: Optional[dict] = None):
        """Инициализация диалога."""
        super().__init__(parent)
        self.prompt = prompt
        is_edit = prompt is not None
        self.setWindowTitle(
            'Редактировать промт' if is_edit else 'Добавить промт'
        )
        self.setMinimumSize(600, 400)
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        form = QFormLayout()

        # Поле для текста промта
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText('Введите текст промта...')
        self.prompt_input.setMinimumHeight(200)
        form.addRow('Промт *:', self.prompt_input)

        # Поле для тегов
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText('тег1, тег2, тег3')
        form.addRow('Теги:', self.tags_input)

        # Заполнение полей, если редактируем
        if self.prompt:
            self.prompt_input.setPlainText(self.prompt.get('prompt', ''))
            self.tags_input.setText(self.prompt.get('tags', '') or '')

        layout.addLayout(form)

        # Кнопки
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def validate_and_accept(self):
        """Валидация и принятие диалога."""
        prompt_text = self.prompt_input.toPlainText().strip()
        tags = self.tags_input.text().strip()

        if not prompt_text:
            QMessageBox.warning(
                self,
                'Ошибка',
                'Поле "Промт" обязательно для заполнения!'
            )
            return

        try:
            if self.prompt:
                # Редактирование существующего промта
                db.update_prompt(
                    self.prompt['id'],
                    prompt=prompt_text,
                    tags=tags if tags else None
                )
            else:
                # Добавление нового промта
                db.create_prompt(prompt_text, tags if tags else None)

            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self,
                'Ошибка',
                f'Ошибка при сохранении промта:\n{str(e)}'
            )
