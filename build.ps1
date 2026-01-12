# Скрипт для сборки исполняемого файла

Write-Host "Сборка исполняемого файла..." -ForegroundColor Green

# Проверка активации виртуального окружения
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Активация виртуального окружения..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
}

# Установка PyInstaller, если не установлен
Write-Host "Проверка PyInstaller..." -ForegroundColor Yellow
pip install pyinstaller --quiet

# Сборка исполняемого файла
Write-Host "Запуск PyInstaller..." -ForegroundColor Yellow
if (Test-Path "CHatList.spec") {
    pyinstaller CHatList.spec
} else {
    pyinstaller --onefile --windowed --name "CHatList" main.py
}

Write-Host "`nСборка завершена!" -ForegroundColor Green
Write-Host "Исполняемый файл находится в папке: dist\CHatList.exe" -ForegroundColor Cyan
