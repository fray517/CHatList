"""Главный модуль приложения ChatList с графическим интерфейсом."""

import sys
from datetime import datetime
from typing import List, Dict, Any, Optional

import markdown

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
    QLabel, QLineEdit, QMessageBox, QCheckBox, QHeaderView, QProgressBar,
    QMenuBar, QMenu, QAction, QPlainTextEdit, QDialog, QDialogButtonBox
)
from PyQt5.QtGui import QKeySequence, QIcon
import os

from src import db
from src.models import Model, get_active_models, add_default_models
from src.network import send_prompt_to_model
from src.ui.models_dialog import ModelsDialog
from src.ui.history_dialogs import PromptsHistoryDialog, ResultsHistoryDialog
from src.ui.prompt_enhancer_dialog import PromptEnhancerDialog
from src.export import export_to_markdown, export_to_json


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
        
        # Установка иконки приложения
        icon_path = os.path.join(os.path.dirname(__file__), 'app.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Временная таблица результатов (в памяти)
        self.temp_results: List[Dict[str, Any]] = []
        self.current_prompt_id: Optional[int] = None

        # Инициализация БД
        db.init_database()
        add_default_models()

        self.init_ui()
        self.create_menu()

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

    def create_menu(self):
        """Создать меню приложения."""
        menubar = self.menuBar()

        # Меню "Настройки"
        settings_menu = menubar.addMenu('Настройки')
        models_action = QAction('Управление моделями', self)
        models_action.setShortcut(QKeySequence('Ctrl+M'))
        models_action.triggered.connect(self.on_manage_models)
        settings_menu.addAction(models_action)

        # Меню "История"
        history_menu = menubar.addMenu('История')
        prompts_action = QAction('История промтов', self)
        prompts_action.setShortcut(QKeySequence('Ctrl+P'))
        prompts_action.triggered.connect(self.on_prompts_history)
        history_menu.addAction(prompts_action)

        results_action = QAction('История результатов', self)
        results_action.setShortcut(QKeySequence('Ctrl+R'))
        results_action.triggered.connect(self.on_results_history)
        history_menu.addAction(results_action)

        # Меню "Улучшение"
        enhance_menu = menubar.addMenu('Улучшение')
        enhance_action = QAction('Улучшить промт', self)
        enhance_action.setShortcut(QKeySequence('Ctrl+I'))
        enhance_action.triggered.connect(self.on_enhance_prompt_clicked)
        enhance_menu.addAction(enhance_action)

        # Меню "Экспорт"
        export_menu = menubar.addMenu('Экспорт')
        export_md_action = QAction('Экспорт в Markdown', self)
        export_md_action.setShortcut(QKeySequence('Ctrl+E'))
        export_md_action.triggered.connect(self.on_export_markdown)
        export_menu.addAction(export_md_action)

        export_json_action = QAction('Экспорт в JSON', self)
        export_json_action.setShortcut(QKeySequence('Ctrl+J'))
        export_json_action.triggered.connect(self.on_export_json)
        export_menu.addAction(export_json_action)

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

        self.enhance_button = QPushButton('Улучшить промт')
        self.enhance_button.clicked.connect(self.on_enhance_prompt_clicked)
        buttons_layout.addWidget(self.enhance_button)

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
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(['Выбрать', 'Модель', 'Ответ', 'Действия'])

        # Настройка колонок
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Установка минимальной высоты строк
        table.verticalHeader().setDefaultSectionSize(150)
        table.verticalHeader().setMinimumSectionSize(100)

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
        try:
            models = get_active_models()
            if not models:
                QMessageBox.warning(
                    self,
                    'Предупреждение',
                    'Нет активных моделей! Добавьте модели в настройках '
                    '(Настройки -> Управление моделями).'
                )
                return
        except Exception as e:
            QMessageBox.critical(
                self,
                'Ошибка',
                f'Ошибка при загрузке моделей:\n{str(e)}'
            )
            return

        # Показ индикатора загрузки
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Неопределённый прогресс
        self.send_button.setEnabled(False)
        self.save_results_button.setEnabled(False)

        # Запуск потока для запросов
        try:
            self.worker = RequestWorker(prompt_text, models)
            self.worker.finished.connect(self.on_requests_finished)
            self.worker.start()
        except Exception as e:
            self.progress_bar.setVisible(False)
            self.send_button.setEnabled(True)
            QMessageBox.critical(
                self,
                'Ошибка',
                f'Ошибка при запуске запросов:\n{str(e)}'
            )

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

            # Ответ (многострочное поле)
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

            # Используем QPlainTextEdit для многострочного отображения
            text_widget = QPlainTextEdit()
            text_widget.setPlainText(response_text)
            text_widget.setReadOnly(True)
            text_widget.setFrameStyle(0)  # Убираем рамку
            text_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            text_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            # Устанавливаем минимальную высоту
            text_widget.setMinimumHeight(100)
            text_widget.setMaximumHeight(300)
            
            self.results_table.setCellWidget(row, 2, text_widget)

            # Кнопка "Открыть" для просмотра в markdown
            open_button = QPushButton('Открыть')
            open_button.clicked.connect(
                lambda checked, r=row: self.open_response_markdown(r)
            )
            self.results_table.setCellWidget(row, 3, open_button)

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

    def open_response_markdown(self, row: int):
        """Открыть ответ нейросети в форматированном markdown."""
        if row >= len(self.temp_results):
            QMessageBox.warning(
                self,
                'Предупреждение',
                'Не удалось получить ответ для отображения.'
            )
            return

        result = self.temp_results[row]
        response_text = result.get('response_text', '')

        # Получаем название модели
        from src.models import load_models
        models = load_models()
        model = next(
            (m for m in models if m.id == result['model_id']),
            None
        )
        model_name = model.name if model else 'Неизвестная модель'

        # Создаём диалог для отображения markdown
        dialog = QDialog(self)
        dialog.setWindowTitle(f'Ответ: {model_name}')
        dialog.setMinimumSize(800, 600)

        layout = QVBoxLayout()
        dialog.setLayout(layout)

        # Информация о модели
        info_label = QLabel(
            f'<b>Модель:</b> {model_name}<br>'
            f'<b>Дата:</b> {result.get("created_at", "Неизвестно")}'
        )
        layout.addWidget(info_label)

        # Текстовое поле для отображения markdown
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)

        # Конвертируем markdown в HTML
        try:
            html_content = markdown.markdown(
                response_text,
                extensions=['fenced_code', 'tables', 'nl2br']
            )
            # Добавляем базовые стили для улучшения отображения
            styled_html = f'''
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        padding: 10px;
                    }}
                    code {{
                        background-color: #f4f4f4;
                        padding: 2px 4px;
                        border-radius: 3px;
                        font-family: "Courier New", monospace;
                    }}
                    pre {{
                        background-color: #f4f4f4;
                        padding: 10px;
                        border-radius: 5px;
                        overflow-x: auto;
                    }}
                    pre code {{
                        background-color: transparent;
                        padding: 0;
                    }}
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                        margin: 10px 0;
                    }}
                    th, td {{
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: left;
                    }}
                    th {{
                        background-color: #f2f2f2;
                        font-weight: bold;
                    }}
                    h1, h2, h3, h4, h5, h6 {{
                        margin-top: 20px;
                        margin-bottom: 10px;
                    }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            '''
            text_edit.setHtml(styled_html)
        except Exception as e:
            # Если ошибка при конвертации, показываем как обычный текст
            text_edit.setPlainText(response_text)
            QMessageBox.warning(
                dialog,
                'Предупреждение',
                f'Ошибка при форматировании markdown: {str(e)}\n'
                'Текст отображается без форматирования.'
            )

        layout.addWidget(text_edit)

        # Кнопки
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.exec_()

    def on_manage_models(self):
        """Обработчик открытия диалога управления моделями."""
        dialog = ModelsDialog(self)
        if dialog.exec_() == ModelsDialog.Accepted:
            # Обновление списка активных моделей не требуется,
            # так как они загружаются при каждом запросе
            QMessageBox.information(
                self,
                'Информация',
                'Изменения сохранены. Они вступят в силу при следующем запросе.'
            )

    def on_prompts_history(self):
        """Обработчик открытия истории промтов."""
        dialog = PromptsHistoryDialog(self)
        if dialog.exec_() == PromptsHistoryDialog.Accepted:
            if dialog.selected_prompt_id:
                prompt = db.get_prompt_by_id(dialog.selected_prompt_id)
                if prompt:
                    self.prompt_input.setPlainText(prompt['prompt'])
                    if prompt.get('tags'):
                        self.tags_input.setText(prompt['tags'])
                    self.update_prompts_combo()

    def on_results_history(self):
        """Обработчик открытия истории результатов."""
        dialog = ResultsHistoryDialog(self)
        dialog.exec_()

    def on_export_markdown(self):
        """Экспорт результатов в Markdown."""
        if not self.temp_results or not self.current_prompt_id:
            QMessageBox.warning(
                self,
                'Предупреждение',
                'Нет результатов для экспорта!'
            )
            return

        prompt = db.get_prompt_by_id(self.current_prompt_id)
        prompt_text = prompt['prompt'] if prompt else 'Неизвестный промт'

        # Получаем названия моделей
        from src.models import load_models
        models = load_models()
        model_dict = {m.id: m.name for m in models}

        export_results = []
        for result in self.temp_results:
            export_results.append({
                'model_name': model_dict.get(result['model_id'], 'Неизвестно'),
                'response_text': result['response_text'],
                'created_at': result.get('created_at', ''),
                'tokens_used': result.get('tokens_used'),
                'response_time': result.get('response_time')
            })

        export_to_markdown(export_results, prompt_text, self)

    def on_export_json(self):
        """Экспорт результатов в JSON."""
        if not self.temp_results or not self.current_prompt_id:
            QMessageBox.warning(
                self,
                'Предупреждение',
                'Нет результатов для экспорта!'
            )
            return

        prompt = db.get_prompt_by_id(self.current_prompt_id)
        prompt_text = prompt['prompt'] if prompt else 'Неизвестный промт'

        # Получаем названия моделей
        from src.models import load_models
        models = load_models()
        model_dict = {m.id: m.name for m in models}

        export_results = []
        for result in self.temp_results:
            export_results.append({
                'model_name': model_dict.get(result['model_id'], 'Неизвестно'),
                'response_text': result['response_text'],
                'created_at': result.get('created_at', ''),
                'tokens_used': result.get('tokens_used'),
                'response_time': result.get('response_time')
            })

        export_to_json(export_results, prompt_text, self)

    def on_enhance_prompt_clicked(self):
        """Обработчик нажатия кнопки 'Улучшить промт'."""
        prompt_text = self.prompt_input.toPlainText().strip()
        if not prompt_text:
            QMessageBox.warning(
                self,
                'Предупреждение',
                'Введите промт для улучшения!'
            )
            return

        # Открытие диалога улучшения промтов
        dialog = PromptEnhancerDialog(self, prompt_text)
        if dialog.exec_() == PromptEnhancerDialog.Accepted:
            if dialog.selected_prompt:
                # Подстановка выбранного варианта в поле ввода
                self.prompt_input.setPlainText(dialog.selected_prompt)
                QMessageBox.information(
                    self,
                    'Успех',
                    'Улучшенный промт подставлен в поле ввода!'
                )


def main():
    """Точка входа в приложение."""
    app = QApplication(sys.argv)
    
    # Установка иконки приложения
    icon_path = os.path.join(os.path.dirname(__file__), 'app.ico')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
