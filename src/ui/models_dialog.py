"""Диалог управления моделями."""

from typing import Optional, List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QCheckBox, QLineEdit, QLabel, QMessageBox, QHeaderView,
    QDialogButtonBox, QFormLayout, QComboBox
)

from src import db
from src.models import Model, load_models


class ModelsDialog(QDialog):
    """Диалог для управления моделями."""

    def __init__(self, parent=None):
        """Инициализация диалога."""
        super().__init__(parent)
        self.setWindowTitle('Управление моделями')
        self.setMinimumSize(800, 600)
        self.models: List[Model] = []
        self.init_ui()
        self.load_models_list()

    def init_ui(self):
        """Инициализация интерфейса."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Таблица моделей
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            'Активна', 'Название', 'API URL', 'Тип', 'Имя модели'
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

        # Кнопки управления
        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton('Добавить')
        self.add_button.clicked.connect(self.on_add_clicked)
        buttons_layout.addWidget(self.add_button)

        self.edit_button = QPushButton('Редактировать')
        self.edit_button.clicked.connect(self.on_edit_clicked)
        buttons_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton('Удалить')
        self.delete_button.clicked.connect(self.on_delete_clicked)
        buttons_layout.addWidget(self.delete_button)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        # Кнопки диалога
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def load_models_list(self):
        """Загрузить список моделей в таблицу."""
        self.models = load_models()
        self.table.setRowCount(len(self.models))

        for row, model in enumerate(self.models):
            # Чекбокс активности
            checkbox = QCheckBox()
            checkbox.setChecked(bool(model.is_active))
            checkbox.stateChanged.connect(
                lambda state, m=model: self.toggle_model_active(m, state)
            )
            self.table.setCellWidget(row, 0, checkbox)

            # Название
            name_item = QTableWidgetItem(model.name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 1, name_item)

            # API URL
            url_item = QTableWidgetItem(model.api_url)
            url_item.setFlags(url_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 2, url_item)

            # Тип
            type_item = QTableWidgetItem(model.model_type)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 3, type_item)

            # Имя модели
            model_name_item = QTableWidgetItem(
                model.model_name or model.name
            )
            model_name_item.setFlags(
                model_name_item.flags() & ~Qt.ItemIsEditable
            )
            self.table.setItem(row, 4, model_name_item)

    def toggle_model_active(self, model: Model, state: int):
        """Переключить активность модели."""
        is_active = 1 if state == Qt.Checked else 0
        db.update_model(model.id, is_active=is_active)
        model.is_active = is_active

    def on_add_clicked(self):
        """Обработчик добавления модели."""
        dialog = ModelEditDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_models_list()

    def on_edit_clicked(self):
        """Обработчик редактирования модели."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'Предупреждение', 'Выберите модель!')
            return

        model = self.models[current_row]
        dialog = ModelEditDialog(self, model)
        if dialog.exec_() == QDialog.Accepted:
            self.load_models_list()

    def on_delete_clicked(self):
        """Обработчик удаления модели."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'Предупреждение', 'Выберите модель!')
            return

        model = self.models[current_row]
        reply = QMessageBox.question(
            self,
            'Подтверждение',
            f'Удалить модель "{model.name}"?',
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Удаление через обновление is_active или прямое удаление
            # В данном случае просто деактивируем
            db.update_model(model.id, is_active=0)
            self.load_models_list()


class ModelEditDialog(QDialog):
    """Диалог редактирования модели."""

    def __init__(self, parent=None, model: Optional[Model] = None):
        """Инициализация диалога."""
        super().__init__(parent)
        self.model = model
        self.setWindowTitle(
            'Редактировать модель' if model else 'Добавить модель'
        )
        self.setMinimumWidth(500)
        self.init_ui()

        if model:
            self.load_model_data()

    def init_ui(self):
        """Инициализация интерфейса."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        form = QFormLayout()

        # Название
        self.name_input = QLineEdit()
        form.addRow('Название:', self.name_input)

        # API URL
        self.api_url_input = QLineEdit()
        self.api_url_input.setText(
            'https://openrouter.ai/api/v1/chat/completions'
        )
        form.addRow('API URL:', self.api_url_input)

        # Переменная окружения для ключа
        self.api_key_env_input = QLineEdit()
        self.api_key_env_input.setText('OPENROUTER_API_KEY')
        form.addRow('Переменная окружения для API-ключа:', self.api_key_env_input)

        # Тип модели
        self.model_type_input = QComboBox()
        self.model_type_input.addItems([
            'openrouter', 'openai', 'deepseek', 'groq', 'qwen', 'llama', 'mistral'
        ])
        form.addRow('Тип модели:', self.model_type_input)

        # Имя модели в API
        self.model_name_input = QLineEdit()
        form.addRow('Имя модели в API:', self.model_name_input)

        # Активна
        self.is_active_checkbox = QCheckBox()
        self.is_active_checkbox.setChecked(True)
        form.addRow('Активна:', self.is_active_checkbox)

        layout.addLayout(form)

        # Кнопки
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def load_model_data(self):
        """Загрузить данные модели в форму."""
        if not self.model:
            return

        self.name_input.setText(self.model.name)
        self.api_url_input.setText(self.model.api_url)
        self.api_key_env_input.setText(self.model.api_key_env)
        index = self.model_type_input.findText(self.model.model_type)
        if index >= 0:
            self.model_type_input.setCurrentIndex(index)
        self.model_name_input.setText(self.model.model_name or '')
        self.is_active_checkbox.setChecked(bool(self.model.is_active))

    def validate_and_accept(self):
        """Валидация и принятие диалога."""
        name = self.name_input.text().strip()
        api_url = self.api_url_input.text().strip()
        api_key_env = self.api_key_env_input.text().strip()
        model_type = self.model_type_input.currentText()
        model_name = self.model_name_input.text().strip()

        if not name:
            QMessageBox.warning(self, 'Ошибка', 'Введите название модели!')
            return

        if not api_url:
            QMessageBox.warning(self, 'Ошибка', 'Введите API URL!')
            return

        if not api_key_env:
            QMessageBox.warning(
                self,
                'Ошибка',
                'Введите имя переменной окружения для API-ключа!'
            )
            return

        if not model_name:
            model_name = name

        if self.model:
            # Обновление существующей модели
            db.update_model(
                self.model.id,
                name=name,
                api_url=api_url,
                api_key_env=api_key_env,
                model_type=model_type,
                model_name=model_name,
                is_active=1 if self.is_active_checkbox.isChecked() else 0
            )
        else:
            # Создание новой модели
            db.create_model(
                name=name,
                api_url=api_url,
                api_key_env=api_key_env,
                model_type=model_type,
                model_name=model_name,
                is_active=1 if self.is_active_checkbox.isChecked() else 0
            )

        self.accept()
