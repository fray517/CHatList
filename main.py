"""Главный модуль приложения ChatList с графическим интерфейсом."""

import sys
from datetime import datetime
from typing import List, Dict, Any, Optional

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
    QLabel, QLineEdit, QMessageBox, QCheckBox, QHeaderView, QProgressBar
)

from src import db
from src.models import Model, get_active_models, add_default_models
from src.network import send_prompt_to_model


class RequestWorker(QThread):
    """Поток для выполнения запросов к API."""

    finished = pyqtSignal(list)

    def __init__(self, prompt: str, models: List[Model]):
        """Инициализация потока."""
        super().__init__()
        self.prompt = prompt
        self.models = models

    def run(self):
        """Выполнение запросов."""
        results = []
        for model in self.models:
            result = send_prompt_to_model(self.prompt, model)
            results.append({
                'model': model,
                'result': result
            })
        self.finished.emit(results)


class MainWindow(QMainWindow):
    """Главное окно приложения."""

    def __init__(self):
        """Инициализация главного окна."""
        super().__init__()
        self.setWindowTitle('ChatList - Сравнение ответов нейросетей')
        self.setGeometry(100, 100, 1200, 800)

        # Временная таблица результатов (в памяти)
        self.temp_results: List[Dict[str, Any]] = []
        self.current_prompt_id: Optional[int] = None

        # Инициализация БД
        db.init_database()
        add_default_models()

        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Панель ввода промта
        prompt_panel = self.create_prompt_panel()
        main_layout.addWidget(prompt_panel)

        # Таблица результатов
        self.results_table = self.create_results_table()
        main_layout.addWidget(self.results_table)

        # Панель управления
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)

        # Обновление списка промтов
        self.update_prompts_combo()

    def create_prompt_panel(self) -> QWidget:
        """Создать панель ввода промта."""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)

        # Выбор сохранённого промта
        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel('Выбрать сохранённый промт:'))
        self.prompts_combo = QComboBox()
        self.prompts_combo.currentTextChanged.connect(self.on_prompt_selected)
        h_layout.addWidget(self.prompts_combo)
        layout.addLayout(h_layout)

        # Поле ввода нового промта
        layout.addWidget(QLabel('Или введите новый промт:'))
        self.prompt_input = QTextEdit()
        self.prompt_input.setMaximumHeight(100)
        self.prompt_input.setPlaceholderText('Введите ваш запрос здесь...')
        layout.addWidget(self.prompt_input)

        # Кнопки
        buttons_layout = QHBoxLayout()
        self.send_button = QPushButton('Отправить')
        self.send_button.clicked.connect(self.on_send_clicked)
        buttons_layout.addWidget(self.send_button)

        self.save_prompt_button = QPushButton('Сохранить промт')
        self.save_prompt_button.clicked.connect(self.on_save_prompt_clicked)
        buttons_layout.addWidget(self.save_prompt_button)

        # Поле для тегов
        buttons_layout.addWidget(QLabel('Теги:'))
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText('тег1, тег2, тег3')
        buttons_layout.addWidget(self.tags_input)

        layout.addLayout(buttons_layout)

        return panel

    def create_results_table(self) -> QTableWidget:
        """Создать таблицу результатов."""
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(['Выбрать', 'Модель', 'Ответ'])

        # Настройка колонок
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)

        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)

        return table

    def create_control_panel(self) -> QWidget:
        """Создать панель управления."""
        panel = QWidget()
        layout = QHBoxLayout()
        panel.setLayout(layout)

        # Индикатор загрузки
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Кнопки
        self.save_results_button = QPushButton('Сохранить выбранные')
        self.save_results_button.clicked.connect(self.on_save_results_clicked)
        self.save_results_button.setEnabled(False)
        layout.addWidget(self.save_results_button)

        self.clear_button = QPushButton('Очистить результаты')
        self.clear_button.clicked.connect(self.on_clear_clicked)
        layout.addWidget(self.clear_button)

        layout.addStretch()

        return panel

    def update_prompts_combo(self):
        """Обновить список промтов в выпадающем списке."""
        self.prompts_combo.clear()
        self.prompts_combo.addItem('-- Новый промт --', None)

        prompts = db.get_prompts(limit=50)
        for prompt in prompts:
            preview = prompt['prompt'][:50] + '...' if len(
                prompt['prompt']
            ) > 50 else prompt['prompt']
            self.prompts_combo.addItem(
                f"{prompt['date']} - {preview}",
                prompt['id']
            )

    def on_prompt_selected(self, text: str):
        """Обработчик выбора промта из списка."""
        prompt_id = self.prompts_combo.currentData()
        if prompt_id:
            prompt = db.get_prompt_by_id(prompt_id)
            if prompt:
                self.prompt_input.setPlainText(prompt['prompt'])
                if prompt['tags']:
                    self.tags_input.setText(prompt['tags'])

    def on_send_clicked(self):
        """Обработчик нажатия кнопки 'Отправить'."""
        prompt_text = self.prompt_input.toPlainText().strip()
        if not prompt_text:
            QMessageBox.warning(self, 'Предупреждение', 'Введите промт!')
            return

        # Очистка предыдущих результатов
        self.temp_results = []
        self.results_table.setRowCount(0)
        self.current_prompt_id = None

        # Получение активных моделей
        models = get_active_models()
        if not models:
            QMessageBox.warning(
                self,
                'Предупреждение',
                'Нет активных моделей! Добавьте модели в настройках.'
            )
            return

        # Показ индикатора загрузки
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Неопределённый прогресс
        self.send_button.setEnabled(False)
        self.save_results_button.setEnabled(False)

        # Запуск потока для запросов
        self.worker = RequestWorker(prompt_text, models)
        self.worker.finished.connect(self.on_requests_finished)
        self.worker.start()

    def on_requests_finished(self, results: List[Dict[str, Any]]):
        """Обработчик завершения запросов."""
        self.progress_bar.setVisible(False)
        self.send_button.setEnabled(True)

        # Сохранение промта в БД
        tags = self.tags_input.text().strip()
        self.current_prompt_id = db.create_prompt(
            self.prompt_input.toPlainText(),
            tags if tags else None
        )

        # Обновление таблицы результатов
        self.results_table.setRowCount(len(results))

        for row, item in enumerate(results):
            model = item['model']
            result = item['result']

            # Чекбокс
            checkbox = QCheckBox()
            checkbox.setChecked(False)
            self.results_table.setCellWidget(row, 0, checkbox)

            # Название модели
            model_item = QTableWidgetItem(model.name)
            model_item.setFlags(model_item.flags() & ~Qt.ItemIsEditable)
            self.results_table.setItem(row, 1, model_item)

            # Ответ
            if result['success']:
                response_text = result.get('response_text', 'Ошибка парсинга')
                self.temp_results.append({
                    'model_id': model.id,
                    'response_text': response_text,
                    'tokens_used': result.get('tokens_used'),
                    'response_time': result.get('response_time')
                })
            else:
                response_text = f"Ошибка: {result.get('error', 'Неизвестная ошибка')}"

            response_item = QTableWidgetItem(response_text)
            response_item.setFlags(response_item.flags() & ~Qt.ItemIsEditable)
            self.results_table.setItem(row, 2, response_item)

        # Включение кнопки сохранения
        if self.temp_results:
            self.save_results_button.setEnabled(True)

        # Обновление списка промтов
        self.update_prompts_combo()

    def on_save_prompt_clicked(self):
        """Обработчик нажатия кнопки 'Сохранить промт'."""
        prompt_text = self.prompt_input.toPlainText().strip()
        if not prompt_text:
            QMessageBox.warning(self, 'Предупреждение', 'Введите промт!')
            return

        tags = self.tags_input.text().strip()
        db.create_prompt(prompt_text, tags if tags else None)
        self.update_prompts_combo()

        QMessageBox.information(
            self,
            'Успех',
            'Промт сохранён!'
        )

    def on_save_results_clicked(self):
        """Обработчик нажатия кнопки 'Сохранить выбранные'."""
        if not self.current_prompt_id:
            QMessageBox.warning(
                self,
                'Предупреждение',
                'Сначала отправьте запрос!'
            )
            return

        selected_results = []
        for row in range(self.results_table.rowCount()):
            checkbox = self.results_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                if row < len(self.temp_results):
                    result = self.temp_results[row].copy()
                    result['prompt_id'] = self.current_prompt_id
                    result['created_at'] = datetime.now().strftime(
                        '%Y-%m-%d %H:%M:%S'
                    )
                    selected_results.append(result)

        if not selected_results:
            QMessageBox.warning(
                self,
                'Предупреждение',
                'Выберите хотя бы один результат для сохранения!'
            )
            return

        db.save_results(selected_results)
        QMessageBox.information(
            self,
            'Успех',
            f'Сохранено результатов: {len(selected_results)}'
        )

        # Очистка временной таблицы
        self.temp_results = []
        self.results_table.setRowCount(0)
        self.save_results_button.setEnabled(False)

    def on_clear_clicked(self):
        """Обработчик нажатия кнопки 'Очистить результаты'."""
        self.temp_results = []
        self.results_table.setRowCount(0)
        self.current_prompt_id = None
        self.save_results_button.setEnabled(False)


def main():
    """Точка входа в приложение."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
