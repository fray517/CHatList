"""Минимальная программа с графическим интерфейсом на PyQt."""

import sys

from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton,
                              QVBoxLayout, QWidget, QLabel)


class MainWindow(QMainWindow):
    """Главное окно приложения."""

    def __init__(self):
        """Инициализация главного окна."""
        super().__init__()
        self.setWindowTitle('Минимальное PyQt приложение')
        self.setGeometry(100, 100, 400, 200)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Вертикальный layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Метка с приветствием
        label = QLabel('Добро пожаловать в PyQt!')
        layout.addWidget(label)

        # Кнопка
        button = QPushButton('Нажми меня')
        button.clicked.connect(self.on_button_clicked)
        layout.addWidget(button)

    def on_button_clicked(self):
        """Обработчик нажатия на кнопку."""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            'Сообщение',
            'Кнопка была нажата!'
        )


def main():
    """Точка входа в приложение."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
