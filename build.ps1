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

# Получение версии из version.py
$version = "1.0.0"
$versionLines = Get-Content "version.py"
foreach ($line in $versionLines) {
    if ($line.Contains("__version__")) {
        $parts = $line.Split("=")
        if ($parts.Length -gt 1) {
            $versionPart = $parts[1].Trim()
            $version = $versionPart.Trim("'").Trim('"').Trim()
            break
        }
    }
}
Write-Host "Версия приложения: $version" -ForegroundColor Cyan

# Сборка исполняемого файла
Write-Host "Запуск PyInstaller..." -ForegroundColor Yellow
if (Test-Path "CHatList.spec") {
    pyinstaller CHatList.spec
} else {
    if (Test-Path "app.ico") {
        pyinstaller --onefile --windowed --name "CHatList-$version" --icon=app.ico main.py
    } else {
        pyinstaller --onefile --windowed --name "CHatList-$version" main.py
    }
}

Write-Host ""
Write-Host "Сборка завершена!" -ForegroundColor Green
$exePath = "dist\CHatList-$version.exe"
Write-Host "Исполняемый файл находится в папке: $exePath" -ForegroundColor Cyan
