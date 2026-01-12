"""Тестовая программа для просмотра и редактирования базы данных SQLite."""

import sys
import sqlite3
from typing import List, Dict, Any, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QLabel,
    QMessageBox, QFileDialog, QDialog, QDialogButtonBox, QFormLayout,
    QLineEdit, QTextEdit, QSpinBox, QHeaderView
)


class DatabaseViewer(QMainWindow):
    """Главное окно для просмотра базы данных."""

    def __init__(self):
        """Инициализация главного окна."""
        super().__init__()
        self.setWindowTitle('Просмотр базы данных SQLite')
        self.setGeometry(100, 100, 1200, 800)

        self.db_path: Optional[str] = None
        self.connection: Optional[sqlite3.Connection] = None
        self.current_table: Optional[str] = None
        self.current_page = 1
        self.rows_per_page = 50

        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Панель выбора файла
        file_panel = self.create_file_panel()
        layout.addWidget(file_panel)

        # Панель выбора таблицы
        table_panel = self.create_table_panel()
        layout.addWidget(table_panel)

        # Панель управления
        control_panel = self.create_control_panel()
        layout.addWidget(control_panel)

        # Таблица данных
        self.data_table = self.create_data_table()
        layout.addWidget(self.data_table)

        # Панель пагинации
        pagination_panel = self.create_pagination_panel()
        layout.addWidget(pagination_panel)

    def create_file_panel(self) -> QWidget:
        """Создать панель выбора файла."""
        panel = QWidget()
        layout = QHBoxLayout()
        panel.setLayout(layout)

        layout.addWidget(QLabel('Файл базы данных:'))
        self.file_label = QLabel('Не выбран')
        layout.addWidget(self.file_label)

        self.open_file_button = QPushButton('Выбрать файл')
        self.open_file_button.clicked.connect(self.on_open_file)
        layout.addWidget(self.open_file_button)

        layout.addStretch()
        return panel

    def create_table_panel(self) -> QWidget:
        """Создать панель выбора таблицы."""
        panel = QWidget()
        layout = QHBoxLayout()
        panel.setLayout(layout)

        layout.addWidget(QLabel('Таблица:'))
        self.tables_combo = QComboBox()
        self.tables_combo.currentTextChanged.connect(self.on_table_selected)
        layout.addWidget(self.tables_combo)

        self.open_table_button = QPushButton('Открыть')
        self.open_table_button.clicked.connect(self.on_open_table)
        self.open_table_button.setEnabled(False)
        layout.addWidget(self.open_table_button)

        layout.addStretch()
        return panel

    def create_control_panel(self) -> QWidget:
        """Создать панель управления."""
        panel = QWidget()
        layout = QHBoxLayout()
        panel.setLayout(layout)

        self.add_button = QPushButton('Добавить')
        self.add_button.clicked.connect(self.on_add_clicked)
        self.add_button.setEnabled(False)
        layout.addWidget(self.add_button)

        self.edit_button = QPushButton('Редактировать')
        self.edit_button.clicked.connect(self.on_edit_clicked)
        self.edit_button.setEnabled(False)
        layout.addWidget(self.edit_button)

        self.delete_button = QPushButton('Удалить')
        self.delete_button.clicked.connect(self.on_delete_clicked)
        self.delete_button.setEnabled(False)
        layout.addWidget(self.delete_button)

        layout.addStretch()

        layout.addWidget(QLabel('Строк на странице:'))
        self.rows_per_page_spin = QSpinBox()
        self.rows_per_page_spin.setMinimum(10)
        self.rows_per_page_spin.setMaximum(500)
        self.rows_per_page_spin.setValue(50)
        self.rows_per_page_spin.valueChanged.connect(self.on_rows_per_page_changed)
        layout.addWidget(self.rows_per_page_spin)

        return panel

    def create_data_table(self) -> QTableWidget:
        """Создать таблицу данных."""
        table = QTableWidget()
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        return table

    def create_pagination_panel(self) -> QWidget:
        """Создать панель пагинации."""
        panel = QWidget()
        layout = QHBoxLayout()
        panel.setLayout(layout)

        self.page_info_label = QLabel('Страница: 0 / 0')
        layout.addWidget(self.page_info_label)

        self.prev_button = QPushButton('◄ Предыдущая')
        self.prev_button.clicked.connect(self.on_prev_page)
        self.prev_button.setEnabled(False)
        layout.addWidget(self.prev_button)

        self.next_button = QPushButton('Следующая ►')
        self.next_button.clicked.connect(self.on_next_page)
        self.next_button.setEnabled(False)
        layout.addWidget(self.next_button)

        layout.addStretch()
        return panel

    def on_open_file(self):
        """Обработчик открытия файла."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            'Выбрать файл базы данных',
            '',
            'SQLite Database (*.db *.sqlite *.sqlite3);;All Files (*)'
        )

        if filename:
            try:
                self.db_path = filename
                self.file_label.setText(filename.split('/')[-1])

                # Подключение к базе данных
                self.connection = sqlite3.connect(filename)
                self.connection.row_factory = sqlite3.Row

                # Загрузка списка таблиц
                self.load_tables()

                QMessageBox.information(
                    self,
                    'Успех',
                    f'База данных открыта: {filename}'
                )

            except Exception as e:
                QMessageBox.critical(
                    self,
                    'Ошибка',
                    f'Не удалось открыть базу данных:\n{str(e)}'
                )
                self.db_path = None
                self.connection = None

    def load_tables(self):
        """Загрузить список таблиц."""
        if not self.connection:
            return

        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND name NOT LIKE 'sqlite_%' "
                "ORDER BY name"
            )
            tables = [row[0] for row in cursor.fetchall()]

            self.tables_combo.clear()
            self.tables_combo.addItems(tables)

            if tables:
                self.open_table_button.setEnabled(True)
            else:
                self.open_table_button.setEnabled(False)

        except Exception as e:
            QMessageBox.critical(
                self,
                'Ошибка',
                f'Ошибка при загрузке таблиц:\n{str(e)}'
            )

    def on_table_selected(self, table_name: str):
        """Обработчик выбора таблицы."""
        self.current_table = table_name if table_name else None
        self.current_page = 1

    def on_open_table(self):
        """Обработчик открытия таблицы."""
        if not self.current_table or not self.connection:
            return

        self.load_table_data()
        self.add_button.setEnabled(True)
        self.edit_button.setEnabled(True)
        self.delete_button.setEnabled(True)

    def get_total_rows(self) -> int:
        """Получить общее количество строк в таблице."""
        if not self.current_table or not self.connection:
            return 0

        try:
            cursor = self.connection.cursor()
            cursor.execute(f'SELECT COUNT(*) FROM "{self.current_table}"')
            return cursor.fetchone()[0]
        except Exception as e:
            QMessageBox.critical(
                self,
                'Ошибка',
                f'Ошибка при подсчёте строк:\n{str(e)}'
            )
            return 0

    def load_table_data(self):
        """Загрузить данные таблицы с пагинацией."""
        if not self.current_table or not self.connection:
            return

        try:
            # Получаем структуру таблицы
            cursor = self.connection.cursor()
            cursor.execute(f'PRAGMA table_info("{self.current_table}")')
            columns_info = cursor.fetchall()

            column_names = [col[1] for col in columns_info]
            column_types = {col[1]: col[2] for col in columns_info}

            # Настройка таблицы
            self.data_table.setColumnCount(len(column_names))
            self.data_table.setHorizontalHeaderLabels(column_names)

            # Получаем общее количество строк
            total_rows = self.get_total_rows()
            total_pages = (total_rows + self.rows_per_page - 1) // self.rows_per_page

            # Обновление информации о странице
            self.page_info_label.setText(
                f'Страница: {self.current_page} / {max(total_pages, 1)} '
                f'(Всего строк: {total_rows})'
            )

            # Кнопки пагинации
            self.prev_button.setEnabled(self.current_page > 1)
            self.next_button.setEnabled(self.current_page < total_pages)

            # Загрузка данных с пагинацией
            offset = (self.current_page - 1) * self.rows_per_page
            cursor.execute(
                f'SELECT * FROM "{self.current_table}" '
                f'LIMIT {self.rows_per_page} OFFSET {offset}'
            )
            rows = cursor.fetchall()

            self.data_table.setRowCount(len(rows))

            for row_idx, row in enumerate(rows):
                for col_idx, col_name in enumerate(column_names):
                    value = row[col_name]
                    if value is None:
                        display_value = 'NULL'
                    else:
                        display_value = str(value)

                    item = QTableWidgetItem(display_value)
                    item.setData(Qt.UserRole, value)  # Сохраняем исходное значение
                    self.data_table.setItem(row_idx, col_idx, item)

            # Автоподбор ширины колонок
            self.data_table.resizeColumnsToContents()

        except Exception as e:
            QMessageBox.critical(
                self,
                'Ошибка',
                f'Ошибка при загрузке данных:\n{str(e)}'
            )

    def on_rows_per_page_changed(self, value: int):
        """Обработчик изменения количества строк на странице."""
        self.rows_per_page = value
        self.current_page = 1
        if self.current_table:
            self.load_table_data()

    def on_prev_page(self):
        """Переход на предыдущую страницу."""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_table_data()

    def on_next_page(self):
        """Переход на следующую страницу."""
        total_rows = self.get_total_rows()
        total_pages = (total_rows + self.rows_per_page - 1) // self.rows_per_page
        if self.current_page < total_pages:
            self.current_page += 1
            self.load_table_data()

    def get_table_structure(self) -> List[Dict[str, Any]]:
        """Получить структуру таблицы."""
        if not self.current_table or not self.connection:
            return []

        cursor = self.connection.cursor()
        cursor.execute(f'PRAGMA table_info("{self.current_table}")')
        columns = cursor.fetchall()

        return [
            {
                'cid': col[0],
                'name': col[1],
                'type': col[2],
                'notnull': col[3],
                'dflt_value': col[4],
                'pk': col[5]
            }
            for col in columns
        ]

    def on_add_clicked(self):
        """Обработчик добавления записи."""
        if not self.current_table or not self.connection:
            return

        structure = self.get_table_structure()
        dialog = RecordEditDialog(self, structure, self.current_table, None)
        if dialog.exec_() == QDialog.Accepted:
            self.load_table_data()

    def on_edit_clicked(self):
        """Обработчик редактирования записи."""
        current_row = self.data_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'Предупреждение', 'Выберите строку!')
            return

        if not self.current_table or not self.connection:
            return

        # Получаем значения текущей строки
        structure = self.get_table_structure()
        primary_keys = [col for col in structure if col['pk']]

        if not primary_keys:
            QMessageBox.warning(
                self,
                'Предупреждение',
                'Таблица не имеет первичного ключа. Редактирование невозможно.'
            )
            return

        # Получаем значения первичного ключа
        pk_values = {}
        for pk_col in primary_keys:
            col_idx = next(
                (i for i, col in enumerate(structure) if col['name'] == pk_col['name']),
                None
            )
            if col_idx is not None:
                item = self.data_table.item(current_row, col_idx)
                if item:
                    pk_values[pk_col['name']] = item.data(Qt.UserRole)

        # Получаем все значения строки
        row_values = {}
        for col_idx, col in enumerate(structure):
            item = self.data_table.item(current_row, col_idx)
            if item:
                row_values[col['name']] = item.data(Qt.UserRole)

        dialog = RecordEditDialog(
            self,
            structure,
            self.current_table,
            row_values
        )
        if dialog.exec_() == QDialog.Accepted:
            self.load_table_data()

    def on_delete_clicked(self):
        """Обработчик удаления записи."""
        current_row = self.data_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'Предупреждение', 'Выберите строку!')
            return

        if not self.current_table or not self.connection:
            return

        structure = self.get_table_structure()
        primary_keys = [col for col in structure if col['pk']]

        if not primary_keys:
            QMessageBox.warning(
                self,
                'Предупреждение',
                'Таблица не имеет первичного ключа. Удаление невозможно.'
            )
            return

        # Получаем значения первичного ключа
        pk_conditions = []
        for pk_col in primary_keys:
            col_idx = next(
                (i for i, col in enumerate(structure) if col['name'] == pk_col['name']),
                None
            )
            if col_idx is not None:
                item = self.data_table.item(current_row, col_idx)
                if item:
                    value = item.data(Qt.UserRole)
                    pk_conditions.append(f'"{pk_col["name"]}" = ?')

        if not pk_conditions:
            QMessageBox.warning(
                self,
                'Предупреждение',
                'Не удалось определить первичный ключ.'
            )
            return

        reply = QMessageBox.question(
            self,
            'Подтверждение',
            'Вы уверены, что хотите удалить эту запись?',
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                cursor = self.connection.cursor()
                where_clause = ' AND '.join(pk_conditions)
                query = f'DELETE FROM "{self.current_table}" WHERE {where_clause}'

                # Получаем значения для подстановки
                values = []
                for pk_col in primary_keys:
                    col_idx = next(
                        (i for i, col in enumerate(structure)
                         if col['name'] == pk_col['name']),
                        None
                    )
                    if col_idx is not None:
                        item = self.data_table.item(current_row, col_idx)
                        if item:
                            values.append(item.data(Qt.UserRole))

                cursor.execute(query, values)
                self.connection.commit()

                QMessageBox.information(self, 'Успех', 'Запись удалена!')
                self.load_table_data()

            except Exception as e:
                QMessageBox.critical(
                    self,
                    'Ошибка',
                    f'Ошибка при удалении:\n{str(e)}'
                )
                self.connection.rollback()

    def closeEvent(self, event):
        """Обработчик закрытия окна."""
        if self.connection:
            self.connection.close()
        event.accept()


class RecordEditDialog(QDialog):
    """Диалог для добавления/редактирования записи."""

    def __init__(
        self,
        parent,
        structure: List[Dict[str, Any]],
        table_name: str,
        row_values: Optional[Dict[str, Any]]
    ):
        """Инициализация диалога."""
        super().__init__(parent)
        self.structure = structure
        self.table_name = table_name
        self.row_values = row_values
        self.inputs = {}

        is_edit = row_values is not None
        self.setWindowTitle(
            f'Редактировать запись' if is_edit else 'Добавить запись'
        )
        self.setMinimumWidth(500)

        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        form = QFormLayout()

        for col in self.structure:
            col_name = col['name']
            col_type = col['type'].upper()
            is_pk = col['pk']
            is_notnull = col['notnull']
            default_value = col['dflt_value']

            # Пропускаем AUTOINCREMENT поля при добавлении
            if not self.row_values and 'INTEGER' in col_type and is_pk:
                # Проверяем, есть ли AUTOINCREMENT
                continue

            label_text = col_name
            if is_pk:
                label_text += ' (PK)'
            if is_notnull:
                label_text += ' *'

            # Создаём поле ввода в зависимости от типа
            if 'TEXT' in col_type or 'VARCHAR' in col_type:
                if col_name in ['prompt', 'response_text'] or len(col_name) > 20:
                    # Для длинных текстовых полей используем QTextEdit
                    input_widget = QTextEdit()
                    input_widget.setMaximumHeight(100)
                else:
                    input_widget = QLineEdit()
            elif 'INTEGER' in col_type:
                input_widget = QSpinBox()
                input_widget.setMinimum(-2147483648)
                input_widget.setMaximum(2147483647)
            elif 'REAL' in col_type:
                input_widget = QLineEdit()
                input_widget.setPlaceholderText('0.0')
            else:
                input_widget = QLineEdit()

            # Устанавливаем значение
            if self.row_values and col_name in self.row_values:
                value = self.row_values[col_name]
                if value is not None:
                    if isinstance(input_widget, QTextEdit):
                        input_widget.setPlainText(str(value))
                    elif isinstance(input_widget, QSpinBox):
                        try:
                            input_widget.setValue(int(value))
                        except (ValueError, TypeError):
                            pass
                    else:
                        input_widget.setText(str(value))
            elif default_value is not None:
                if isinstance(input_widget, QTextEdit):
                    input_widget.setPlainText(str(default_value))
                elif isinstance(input_widget, QSpinBox):
                    try:
                        input_widget.setValue(int(default_value))
                    except (ValueError, TypeError):
                        pass
                else:
                    input_widget.setText(str(default_value))

            # Если это PK и режим редактирования, делаем поле только для чтения
            if is_pk and self.row_values:
                if isinstance(input_widget, QTextEdit):
                    input_widget.setReadOnly(True)
                elif isinstance(input_widget, QSpinBox):
                    input_widget.setReadOnly(True)
                else:
                    input_widget.setReadOnly(True)

            form.addRow(label_text, input_widget)
            self.inputs[col_name] = input_widget

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
        try:
            parent = self.parent()
            if not parent or not parent.connection:
                return

            cursor = parent.connection.cursor()

            if self.row_values:
                # Редактирование
                primary_keys = [col for col in self.structure if col['pk']]
                set_clauses = []
                values = []

                for col in self.structure:
                    col_name = col['name']
                    if col_name in self.inputs:
                        input_widget = self.inputs[col_name]

                        if isinstance(input_widget, QTextEdit):
                            value = input_widget.toPlainText()
                        elif isinstance(input_widget, QSpinBox):
                            value = input_widget.value()
                        else:
                            value = input_widget.text()

                        # Проверка на NULL
                        if col['notnull'] and not value and value != 0:
                            QMessageBox.warning(
                                self,
                                'Ошибка',
                                f'Поле "{col_name}" обязательно для заполнения!'
                            )
                            return

                        if col_name not in [pk['name'] for pk in primary_keys]:
                            set_clauses.append(f'"{col_name}" = ?')
                            values.append(value if value else None)

                where_clauses = []
                for pk_col in primary_keys:
                    pk_name = pk_col['name']
                    if pk_name in self.row_values:
                        where_clauses.append(f'"{pk_name}" = ?')
                        values.append(self.row_values[pk_name])

                query = (
                    f'UPDATE "{self.table_name}" '
                    f'SET {", ".join(set_clauses)} '
                    f'WHERE {" AND ".join(where_clauses)}'
                )

            else:
                # Добавление
                columns = []
                placeholders = []
                values = []

                for col in self.structure:
                    col_name = col['name']
                    if col_name in self.inputs:
                        input_widget = self.inputs[col_name]

                        if isinstance(input_widget, QTextEdit):
                            value = input_widget.toPlainText()
                        elif isinstance(input_widget, QSpinBox):
                            value = input_widget.value()
                        else:
                            value = input_widget.text()

                        # Проверка на NULL
                        if col['notnull'] and not value and value != 0:
                            QMessageBox.warning(
                                self,
                                'Ошибка',
                                f'Поле "{col_name}" обязательно для заполнения!'
                            )
                            return

                        columns.append(f'"{col_name}"')
                        placeholders.append('?')
                        values.append(value if value else None)

                query = (
                    f'INSERT INTO "{self.table_name}" '
                    f'({", ".join(columns)}) '
                    f'VALUES ({", ".join(placeholders)})'
                )

            cursor.execute(query, values)
            parent.connection.commit()

            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self,
                'Ошибка',
                f'Ошибка при сохранении:\n{str(e)}'
            )
            if parent and parent.connection:
                parent.connection.rollback()


def main():
    """Точка входа в приложение."""
    app = QApplication(sys.argv)
    window = DatabaseViewer()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
