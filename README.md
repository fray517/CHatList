# CHatList

Минимальная программа с графическим интерфейсом на PyQt5.

## Установка

1. Активируйте виртуальное окружение:
```powershell
.\venv\Scripts\Activate.ps1
```

2. Установите зависимости:
```powershell
pip install -r requirements.txt
```

## Запуск

Запустите программу:
```powershell
python main.py
```

## Сборка исполняемого файла

Для создания исполняемого файла используйте скрипт сборки:
```powershell
.\build.ps1
```

Или вручную:
```powershell
pyinstaller --onefile --windowed --name "CHatList" main.py
```

Исполняемый файл будет находиться в папке `dist\CHatList.exe`.
